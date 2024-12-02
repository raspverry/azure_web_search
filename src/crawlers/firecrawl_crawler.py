# src/crawlers/firecrawl_crawler.py
from typing import Dict, Any, Optional
from .base_crawler import BaseCrawler, CrawlResult
import aiohttp
import json
from contextlib import AsyncExitStack


class FirecrawlCrawler(BaseCrawler):
    """ローカルにホストされているFirecrawl APIを使用したクローラーの実装"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.exit_stack = AsyncExitStack()
        self.session = None
        self.api_url = config.get("api_url", "http://localhost:3002/v1/scrape")
        self.timeout = aiohttp.ClientTimeout(total=config.get("timeout", 60))

    async def _init_session(self):
        """aiohttpセッションの初期化"""
        if not self.session:
            self.session = await self.exit_stack.enter_async_context(
                aiohttp.ClientSession(timeout=self.timeout)
            )

    async def fetch_content(self, url: str) -> CrawlResult:
        """Firecrawl APIを使用してウェブページのコンテンツを取得"""
        await self._init_session()

        try:
            payload = {"url": url, "formats": ["markdown", "html"]}
            print(f"APIリクエスト: {url}")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": self.config.get(
                    "user_agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ),
            }

            async with self.session.post(
                self.api_url, headers=headers, json=payload
            ) as response:
                if response.status == 200:
                    try:
                        result = await response.json()
                    except json.JSONDecodeError:
                        return CrawlResult(
                            content="", error="JSONパースエラー: 無効なレスポンス形式"
                        )

                    if not result.get("success"):
                        return CrawlResult(content="", error="API成功フラグがFalseです")

                    # データの取得
                    data = result.get("data", {})

                    content = data.get("markdown", "")  # マークダウンを優先
                    if not content:
                        content = data.get("html", "")  # マークダウンがない場合はHTML

                    metadata = data.get("metadata", {})

                    return CrawlResult(
                        content=content,
                        title=metadata.get("title", ""),
                        description=metadata.get("description", ""),
                        metadata={
                            "language": metadata.get("language"),
                            "status_code": metadata.get("statusCode"),
                            "source_url": metadata.get("sourceURL"),
                            "og_title": metadata.get("ogTitle"),
                            "og_description": metadata.get("ogDescription"),
                        },
                    )
                else:
                    error_text = await response.text()
                    return CrawlResult(
                        content="",
                        error=f"Firecrawl APIエラー: {response.status} - {error_text}",
                    )

        except aiohttp.ClientError as e:
            return CrawlResult(content="", error=f"API接続エラー: {str(e)}")
        except Exception as e:
            return CrawlResult(content="", error=f"予期せぬエラー: {str(e)}")

    async def cleanup(self):
        """セッションのクリーンアップ"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.session = None
