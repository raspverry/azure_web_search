# src/web_search.py

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# 環境変数をロードする
load_dotenv()

# Azure Web Search API 設定
BING_SUBSCRIPTION_KEY = os.getenv("BING_SEARCH_V7_SUBSCRIPTION_KEY")
BING_ENDPOINT = os.getenv("BING_SEARCH_V7_ENDPOINT") + "v7.0/search"

# キャッシュの設定
CACHE_DIR = Path("cache/bing_search")
CACHE_DURATION = 60 * 60 * 24  # 24時間（秒単位）

class BingSearchCache:
    """Bing検索結果のキャッシュを管理するクラス"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR, cache_duration: int = CACHE_DURATION):
        """
        キャッシュマネージャーの初期化

        Parameters:
            cache_dir (Path): キャッシュファイルを保存するディレクトリ
            cache_duration (int): キャッシュの有効期間（秒）
        """
        self.cache_dir = cache_dir
        self.cache_duration = cache_duration
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, query: str, count: int, mkt: str) -> Path:
        """キャッシュファイルのパスを生成"""
        # クエリパラメータからキャッシュキーを生成
        cache_key = f"{query}_{count}_{mkt}".replace("/", "_")
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, query: str, count: int, mkt: str) -> Optional[Dict[str, Any]]:
        """
        キャッシュからデータを取得

        Returns:
            Optional[Dict[str, Any]]: キャッシュされたデータ、または None
        """
        cache_path = self._get_cache_path(query, count, mkt)
        
        if not cache_path.exists():
            return None
            
        try:
            with cache_path.open("r", encoding="utf-8") as f:
                cached_data = json.load(f)
                
            # キャッシュの有効期限をチェック
            if time.time() - cached_data["timestamp"] > self.cache_duration:
                cache_path.unlink()  # 期限切れのキャッシュを削除
                return None
                
            return cached_data["data"]
            
        except (json.JSONDecodeError, KeyError, OSError):
            # キャッシュファイルが破損している場合は削除
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, query: str, count: int, mkt: str, data: Dict[str, Any]):
        """
        データをキャッシュに保存

        Parameters:
            data (Dict[str, Any]): キャッシュするデータ
        """
        cache_path = self._get_cache_path(query, count, mkt)
        
        try:
            cache_data = {
                "timestamp": time.time(),
                "data": data
            }
            
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except OSError as e:
            print(f"キャッシュの保存中にエラーが発生しました: {e}")

# キャッシュマネージャーのインスタンスを作成
cache_manager = BingSearchCache()

def bing_web_search(query: str, count: int = 10, mkt: str = "en-US") -> Dict[str, Any]:
    """
    Bing Web Search APIを使用して指定されたクエリに対する検索結果を取得する。
    キャッシュがある場合はそれを使用し、なければAPIを呼び出す。

    Parameters:
        query (str): 検索クエリ
        count (int): 取得する検索結果の数
        mkt (str): マーケットコード（例: 'en-US'）

    Returns:
        dict: APIからのJSONレスポンス
    """
    # キャッシュをチェック
    cached_result = cache_manager.get(query, count, mkt)
    if cached_result is not None:
        print(f"キャッシュされた結果を使用: {query}")
        return cached_result
        
    # APIを呼び出し
    headers = {"Ocp-Apim-Subscription-Key": BING_SUBSCRIPTION_KEY}
    params = {
        "q": query,
        "count": count,
        "mkt": mkt,
        "textDecorations": True,
        "textFormat": "HTML",
    }
    
    print(f"APIを呼び出し: {query}")
    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()
    
    # 結果をキャッシュに保存
    result = response.json()
    cache_manager.set(query, count, mkt, result)
    
    return result