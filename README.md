# Web Search RAG with Azure

Web検索機能を組み込んだRAG（Retrieval-Augmented Generation）の実装プロトタイプです。Azure Web Search APIを使用してウェブ検索を行い、その結果をOpenAI GPTモデルに入力として提供します。

## 特徴

- Azure Web Search APIによるウェブ検索
- ウェブページコンテンツの取得と前処理
- OpenAI GPTモデルによる回答生成
- 検証用のデータ保存機能

## 前提条件

- Python 3.10以上
- Azure Web Search APIのアクセスキー
- OpenAI APIのアクセスキー
- uvコマンド（パッケージマネージャー）

## インストール

```bash
git clone [repository-url]
cd web-search-rag

# uv (推奨)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## 環境変数の設定

`.env`ファイルをプロジェクトルートに作成し、以下の環境変数を設定してください：

```
BING_SEARCH_V7_SUBSCRIPTION_KEY=your-bing-api-key
BING_SEARCH_V7_ENDPOINT=your-bing-api-endpoint
OPENAI_API_KEY=your-openai-api-key
```

## 使用方法

```bash
uv run main.py
```

プログラムが起動したら、質問を入力してください。システムは以下の手順で処理を行います：

1. Azure Web Search APIで関連するウェブページを検索
2. 検索結果のウェブページからコンテンツを取得
3. 取得したコンテンツを基にGPTモデルが回答を生成

## プロジェクト構造

```
.
├── main.py                  # メインスクリプト
├── src/
│   ├── web_search.py       # Azure Web Search API関連の実装
│   ├── scrapy_crawl.py     # ウェブスクレイピング実装
│   └── chatgpt.py          # OpenAI API関連の実装
├── verification_results/    # 検証結果の保存ディレクトリ
├── pyproject.toml        # 依存パッケージリスト
└── .env                    # 環境変数ファイル
```

## スクレイピング実装について

現在はScrapyを使用してウェブページのコンテンツ取得を実装していますが、モジュール化された設計により他のスクレイピングツール（BeautifulSoup4、Selenium等）への置き換えが容易に行えます。

新しいスクレイピングツールを実装する場合は、以下の手順で対応可能です：

1. `src/` ディレクトリに新しいスクレイピング実装を作成
2. `fetch_webpage_content()` 関数のインターフェースを維持
3. `main.py` でのインポート先を変更

## 検証データ

実行結果は `verification_results/` ディレクトリに保存されます。各実行結果には以下の情報が含まれます：

- 入力されたクエリ
- 検索結果
- 取得したウェブページコンテンツ
- GPTモデルの応答

## 注意事項

- このプロジェクトは検証段階のプロトタイプです
- 大規模な並列処理は実装されていません
- API利用料金が発生する可能性があります
- スクレイピングを行う際は対象サイトのロボット規約を確認してください

## 今後の課題

- [ ] 非同期処理の実装
- [ ] キャッシング機能の追加
- [ ] より洗練されたプロンプトエンジニアリング
- [ ] 検索結果のフィルタリング機能
- [ ] スクレイピング実装の抽象化
- [ ] エラーハンドリングの強化

