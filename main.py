from src.web_search import bing_web_search
from src.chatgpt import openai_generate_response
from src.crawlers.crawler_factory import CrawlerFactory
import asyncio
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# クローラーの設定
CRAWLER_TYPE = os.getenv("CRAWLER_TYPE", "scrapy")
CRAWLER_CONFIG = {
    "user_agent": "カスタムユーザーエージェント",
    "respect_robots": True,
    "delay": 2,
    "api_url": "http://localhost:3002/v1/scrape",  # Firecrawl API URL
    "timeout": 60,
}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


async def fetch_webpage_content(
    url: str, semaphore: asyncio.Semaphore
) -> tuple[str, str, str]:
    """ウェブページのコンテンツを取得"""
    async with semaphore:  # 同時接続数を制限
        crawler = CrawlerFactory.create_crawler(CRAWLER_TYPE, CRAWLER_CONFIG)
        try:
            result = await crawler.fetch_content(url)
            content = result.content if not result.error else ""
            title = result.title if hasattr(result, "title") else ""
            error = result.error if hasattr(result, "error") else ""
            return content, title, error
        finally:
            await crawler.cleanup()  # awaitを追加


async def process_urls(urls: list) -> list:
    """URLリストを並列で処理"""
    semaphore = asyncio.Semaphore(5)  # 同時に処理するURL数を制限
    tasks = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 取得中: {url}")
        task = asyncio.create_task(fetch_webpage_content(url, semaphore))
        tasks.append((url, task))

    results = []
    for url, task in tasks:
        content, title, error = await task
        if error:
            print(f"エラー ({url}): {error}")
        results.append(content)

    return results


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

        # URLリストを作成
        urls = [page.get("url") for page in web_pages]

        # 並列処理でコンテンツを取得
        contents = await process_urls(urls)

        # 検索結果とコンテンツを組み合わせる
        detailed_summaries = [
            {
                "title": page.get("name"),
                "url": page.get("url"),
                "snippet": page.get("snippet"),
                "content": content[:1000]
                if content
                else "コンテンツを取得できませんでした",
            }
            for page, content in zip(web_pages, contents)
        ]

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
        ai_response = openai_generate_response(
            OPENAI_API_KEY=OPENAI_API_KEY, OPENAI_API_URL=OPENAI_API_URL, prompt=prompt
        )

        # 応答を表示
        answer = ai_response["choices"][0]["message"]["content"]
        print("\n💡 **AI応答**\n")
        print(answer)

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
