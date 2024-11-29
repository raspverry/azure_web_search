# src/scrapy_crawl.py

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.settings import Settings

class ContentSpider(scrapy.Spider):
    name = "content_spider"

    def __init__(self, url, *args, **kwargs):
        """
        スパイダーの初期化。
        
        Parameters:
            url (str): クロールするURL。
        """
        super(ContentSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def parse(self, response):
        """
        ページ内の全ての<p>タグからテキストを抽出し、コンテンツとして返す。
        """
        paragraphs = response.xpath('//p//text()').getall()
        content = '\n'.join(paragraphs)
        yield {'content': content}

def fetch_webpage_content(url):
    """
    指定されたURLからScrapyを使用してコンテンツを取得する。
    
    Parameters:
        url (str): クロールするURL。
    
    Returns:
        str: 取得したコンテンツ（最初のページのみ）。
    """
    # コンテンツを格納するリスト
    contents = []

    # スパイダーからアイテムを収集するためのシグナルハンドラー
    def collect_content(item, response, spider):
        contents.append(item['content'])

    # シグナルを接続する
    dispatcher.connect(collect_content, signal=signals.item_scraped)

    # Scrapyの設定を定義
    settings = Settings()
    settings.set("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                " Chrome/58.0.3029.110 Safari/537.3")
    settings.set("ROBOTSTXT_OBEY", False)  # 必要に応じてTrueに設定

    # CrawlerProcessのインスタンスを作成
    process = CrawlerProcess(settings)

    # スパイダーをクローリングする
    process.crawl(ContentSpider, url=url)
    process.start()  # ブロッキング呼び出し

    # 収集したコンテンツを返す
    if contents:
        return contents[0]
    else:
        return ""
