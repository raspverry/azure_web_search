# main.py 
import sys
from src.web_search import bing_web_search
from src.scrapy_crawl import fetch_webpage_content
from src.chatgpt import openai_generate_response
import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# 環境変数をロードする
load_dotenv()

# OpenAI API 設定
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# 検証用の設定
SAVE_RESULTS = True  # 結果を保存するかどうか
RESULTS_DIR = "verification_results"

def save_verification_data(query, search_results, detailed_summaries, ai_response):
    """検証用のデータを保存"""
    if not SAVE_RESULTS:
        return
        
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RESULTS_DIR}/result_{timestamp}.json"
    
    data = {
        "query": query,
        "search_results": search_results,
        "detailed_summaries": detailed_summaries,
        "ai_response": ai_response
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    """
    ユーザーからのクエリを取得し、Bing Web Search APIで検索し、
    各検索結果のウェブページからコンテンツを取得してOpenAI GPTモデルに渡し、回答を生成する。
    """
    user_query = input("質問を入力してください: ")
    print("\nウェブ検索を実行しています...\n")

    try:
        # Azure Web Search API 呼び出し
        search_results = bing_web_search(user_query)
        
        # 検索結果の表示（検証用）
        print(f"\n検索結果数: {len(search_results.get('webPages', {}).get('value', []))}\n")
        
        # ウェブページ検索結果を抽出
        web_pages = search_results.get('webPages', {}).get('value', [])
        if not web_pages:
            print("検索結果がありません。")
            return

        # 検索結果からURLを抽出し、ウェブページの内容を取得
        detailed_summaries = []
        for i, page in enumerate(web_pages, 1):
            title = page.get('name')
            url = page.get('url')
            snippet = page.get('snippet')
            print(f"\n[{i}/{len(web_pages)}] Fetching: {url}")
            
            try:
                content = fetch_webpage_content(url)
                if content:
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"取得成功 - コンテンツ長: {len(content)} 文字")
                    print(f"プレビュー: {content_preview}")
                    detailed_summaries.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "content": content[:1000]  # 最初の1000文字のみ使用
                    })
                else:
                    print("コンテンツを取得できませんでした")
                    detailed_summaries.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "content": "コンテンツを取得できませんでした"
                    })
            except Exception as e:
                print(f"エラー: {str(e)}")
                detailed_summaries.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "content": f"エラー: {str(e)}"
                })

        # OpenAIに伝達するプロンプトを生成
        prompt = (
            f"次の内容は '{user_query}' に関するウェブ検索結果です。各ソースの情報を総合的に分析し、"
            f"矛盾する情報がある場合はそれを指摘し、情報の信頼性も考慮して回答してください:\n\n"
        )
        
        for summary in detailed_summaries:
            prompt += (
                f"ソース: {summary['url']}\n"
                f"タイトル: {summary['title']}\n"
                f"概要: {summary['snippet']}\n"
                f"内容: {summary['content']}\n\n"
            )

        print("\nOpenAI GPTモデルに応答をリクエストしています...\n")

        # OpenAI GPT API 呼び出し
        ai_response = openai_generate_response(OPENAI_API_KEY, OPENAI_API_URL, prompt)

        # 応答を表示
        answer = ai_response['choices'][0]['message']['content']
        print("\n💡 **AI応答**\n")
        print(answer)
        
        # 検証用データを保存
        save_verification_data(user_query, search_results, detailed_summaries, ai_response)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTPエラーが発生しました: {http_err}")
    except Exception as err:
        import traceback
        traceback.print_exc()
        print(f"エラーが発生しました: {err}")

if __name__ == "__main__":
    main()