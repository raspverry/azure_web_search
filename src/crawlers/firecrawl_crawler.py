# src/crawlers/firecrawl_crawler.py
from typing import Dict, Any, Optional
from .base_crawler import BaseCrawler, CrawlResult
import asyncio
import aiohttp

class FirecrawlCrawler(BaseCrawler):
    """Firecrawlを使用したクローラーの実装"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.session = None
    
    async def _init_session(self):
        """aiohttpセッションの初期化"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def fetch_content(self, url: str) -> CrawlResult:
        """Firecrawlを使用してウェブページのコンテンツを取得"""
        await self._init_session()
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    # Firecrawl専用の処理ロジックを実装
                    return CrawlResult(content=html)
                else:
                    return CrawlResult(
                        content="",
                        error=f"HTTPエラー: {response.status}"
                    )
        except Exception as e:
            return CrawlResult(content="", error=str(e))
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        if self.session:
            asyncio.create_task(self.session.close())
            self.session = None