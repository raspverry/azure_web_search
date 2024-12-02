# src/crawlers/crawler_factory.py
from typing import Dict, Any, Optional
from .base_crawler import BaseCrawler
from .scrapy_crawler import ScrapyCrawler
from .firecrawl_crawler import FirecrawlCrawler

class CrawlerFactory:
    """クローラー生成のためのファクトリークラス"""
    
    @staticmethod
    def create_crawler(crawler_type: str, config: Optional[Dict[str, Any]] = None) -> BaseCrawler:
        """指定されたタイプのクローラーインスタンスを生成"""
        crawlers = {
            "scrapy": ScrapyCrawler,
            "firecrawl": FirecrawlCrawler
        }
        
        crawler_class = crawlers.get(crawler_type.lower())
        if not crawler_class:
            raise ValueError(f"サポートされていないクローラータイプです: {crawler_type}")
        
        return crawler_class(config)