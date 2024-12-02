# src/crawlers/base_crawler.py
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class CrawlResult:
    """クロールの結果を格納するデータクラス"""
    content: str
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BaseCrawler(ABC):
    """基本クローラークラス"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    async def fetch_content(self, url: str) -> CrawlResult:
        """ウェブページのコンテンツを取得する抽象メソッド"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """リソースのクリーンアップのための抽象メソッド"""
        pass