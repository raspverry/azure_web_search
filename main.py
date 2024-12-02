from src.web_search import bing_web_search
from src.chatgpt import openai_generate_response
from src.crawlers.crawler_factory import CrawlerFactory
import asyncio
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# クローラーの設定
CRAWLER_TYPE = os.getenv("CRAWLER_TYPE", "scrapy")  # デフォルトはscrapy
CRAWLER_CONFIG = {
    "user_agent": "カスタムユーザーエージェント",
    "respect_robots": True,
    "delay": 2
}

async def fetch_webpage_content(url: str) -> str:
    """ウェブページのコンテンツを取得"""
    crawler = CrawlerFactory.create_crawler(CRAWLER_TYPE, CRAWLER_CONFIG)
    try:
        result = await crawler.fetch_content(url)
        return result.content if not result.error else ""
    finally:
        crawler.cleanup()

async def main():
    """メイン関数"""
    user_query = input("質問を入力してください: ")
    print("\nウェブ検索を実行しています...\n")

    try:
        # Azure Web Search APIを呼び出す
        search_results = bing_web_search(user_query)
        web_pages = search_results.get("webPages", {}).get("value", [])
        
        if not web_pages:
            print("検索結果が見つかりませんでした。")
            return

        # 検索結果からURLを抽出し、ウェブページの内容を取得
        detailed_summaries = []
        for i, page in enumerate(web_pages, 1):
            url = page.get("url")
            print(f"\n[{i}/{len(web_pages)}] 取得中: {url}")
            
            content = await fetch_webpage_content(url)
            detailed_summaries.append({
                "title": page.get("name"),
                "url": url,
                "snippet": page.get("snippet"),
                "content": content[:1000] if content else "コンテンツを取得できませんでした"
            })

        # OpenAIのプロンプトを生成
        prompt = (
            f"以下は '{user_query}' に関するウェブ検索の結果です。各ソースの情報を総合的に分析し、"
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

        # OpenAI GPT APIを呼び出す
        ai_response = openai_generate_response(prompt)
        
        # 応答を表示
        answer = ai_response["choices"][0]["message"]["content"]
        print("\n💡 **AI応答**\n")
        print(answer)

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())