# src/crawlers/scrapy_crawler.py
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.settings import Settings
from typing import Dict, Any, Optional
from .base_crawler import BaseCrawler, CrawlResult

SUPPORTED_BROWSERS = ['Chrome', 'Firefox', 'Safari', 'Edge']

def filter_user_agent(ua):
    return any(browser in ua for browser in SUPPORTED_BROWSERS)

class ContentSpider(scrapy.Spider):
    """ウェブページの内容を取得するSpider"""
    name = 'content_spider'
    
    def __init__(self, url, *args, **kwargs):
        super(ContentSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def parse(self, response):
        """ページ内のすべてのテキストを抽出"""
        content = {
            'text': response.xpath("//body//text()").getall(),
            'title': response.css('title::text').get(),
            'meta': response.css('meta[name="description"]::attr(content)').get()
        }
        
        cleaned_text = [text.strip() for text in content['text'] if text.strip()]
        full_content = "\n".join([
            f"タイトル: {content['title']}" if content['title'] else "",
            f"説明: {content['meta']}" if content['meta'] else "",
            "本文:",
            "\n".join(cleaned_text)
        ]).strip()
        
        yield {"content": full_content}

class ScrapyCrawler(BaseCrawler):
    """Scrapyを使用したクローラーの実装"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.contents = []
        
        # Scrapy設定の初期化
        self.settings = Settings()
        self._configure_settings()
    
    def _configure_settings(self):
        """Scrapy設定の構成"""
        self.settings.set("USER_AGENT", self.config.get("user_agent", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/58.0.3029.110 Safari/537.3"))
        self.settings.set("ROBOTSTXT_OBEY", self.config.get("respect_robots", False))
        self.settings.set("DOWNLOAD_DELAY", self.config.get("delay", 2))
        
        # DOWNLOADER_MIDDLEWARESを追加
        self.settings.set('DOWNLOADER_MIDDLEWARES', {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        })
        self.settings.set('USER_AGENT_FILTERS', {'filter_user_agent': filter_user_agent})
        
        self.settings.set('COOKIES_ENABLED', True)
        self.settings.set('DOWNLOAD_TIMEOUT', 180)
        
        self.settings.set('DEFAULT_REQUEST_HEADERS', {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    async def fetch_content(self, url: str) -> CrawlResult:
        """Scrapyを使用してウェブページのコンテンツを取得"""
        self.contents = []
        
        def collect_content(item, response, spider):
            self.contents.append(item["content"])
        
        dispatcher.connect(collect_content, signal=signals.item_scraped)
        
        process = CrawlerProcess(self.settings)
        process.crawl(ContentSpider, url=url)
        process.start()
        
        if self.contents:
            return CrawlResult(content=self.contents[0])
        return CrawlResult(content="", error="コンテンツが見つかりませんでした")
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.contents = []