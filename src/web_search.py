# src/web_search.py

import os
import requests
from dotenv import load_dotenv

# 環境変数をロードする
load_dotenv()

# Azure Web Search API 設定
BING_SUBSCRIPTION_KEY = os.getenv('BING_SEARCH_V7_SUBSCRIPTION_KEY')
BING_ENDPOINT = os.getenv('BING_SEARCH_V7_ENDPOINT') + "v7.0/search"

def bing_web_search(query, count=5, mkt='en-US'):
    """
    Bing Web Search APIを使用して指定されたクエリに対する検索結果を取得する。
    
    Parameters:
        query (str): 検索クエリ。
        count (int): 取得する検索結果の数。
        mkt (str): マーケットコード（例: 'en-US'）。
    
    Returns:
        dict: APIからのJSONレスポンス。
    """
    headers = {"Ocp-Apim-Subscription-Key": BING_SUBSCRIPTION_KEY}
    params = {
        "q": query,
        "count": count,
        "mkt": mkt,
        "textDecorations": True,
        "textFormat": "HTML"
    }
    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
