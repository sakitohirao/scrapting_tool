# Books to Scrape – ポートフォリオ用スクレイピングサンプル

このリポジトリは、学習用サイト **Books to Scrape**（<http://books.toscrape.com/>）を対象に、
**カテゴリ横断**・**ページネーション**・**CSV 出力**までをカバーする、実務に近い最小構成のスクレイピングサンプルです。  

> 注意: 本コードは学習用デモサイトのみを対象としています。実サイトへ適用する際は、**利用規約・robots.txt・法令**に必ず従ってください。

---

## できること（サマリ）

- トップページの本一覧を取得（`scrape_home_to_df`）
- 全ページを自動巡回して取得（`scrape_all_pages_to_df`）
- 指定カテゴリの全ページを取得（`scrape_category_to_df`）
- 取得結果を **CSV** へ保存（`save_csv`）
- レート制御（`sleep_between_requests`：デフォルト3秒）
- **再利用しやすい** DataFrameベースの関数群

---

## ディレクトリ構成

```
project-root/
├─ src/
│  └─ scrape_books.py      # ← 本READMEが対象としているスクリプト
├─ output/                 # ← CSVが出力される（自動作成）
└─ README.md               # 
```

> 出力ディレクトリは `OUT_DIR` 定義で `src/../output` に自動作成されます。

---

## 主要変数と関数（コード内定義の要点）

### 変数

- `URL`: サイトのトップページURL  
- `BASE_URL`: 詳細ページURL生成用のベースURL（1ページ目）  
- `CATEGORY_NAME`: スクレイピング対象カテゴリー名（例: `"romance_8"`）  
- `OUT_DIR`: CSV出力先ディレクトリ（`src/../output` を自動解決）

### 関数

- `scrape_home_to_df()`  
  トップページのカード要素（`.product_pod`）から **タイトル / 詳細URL / 価格 / 在庫 / レーティング / リストページURL** を抽出。

- `scrape_page_to_df(page_num)`  
  `page-{n}.html` にアクセスし、同様の情報を抽出。**ページネーション**に対応。

- `scrape_all_pages_to_df(sleep_sec=3)`  
  1ページ目から順に `scrape_page_to_df` を呼び出し、**空ページで停止**。`sleep_between_requests()` により**丁寧な巡回**。

- `scrape_category_to_df(category_url, sleep_sec=3)`  
  カテゴリの **1ページ目URL（`index.html`）** を起点に、2ページ目以降を `page-{n}.html` で辿る。**200以外のHTTPステータスで終了**。

- `get_category_url(CATEGORY_NAME)`  
  `"{CATEGORY_NAME}/index.html"` の形式で **カテゴリ1ページ目URLを生成**。

- `save_csv(df, filename, out_dir=None)`  
  `out_dir` が与えられたら作成・保存。**相対/絶対パスを許容**。

- `sleep_between_requests()`  
  現状は単純な `time.sleep(3)`（必要に応じて指数バックオフやジッターに拡張可能）。

---

## セットアップ

**要件**

- Python 3.9+（動作目安）
- パッケージ: `requests`, `beautifulsoup4`, `pandas`

**インストール**

```bash
pip install -U requests beautifulsoup4 pandas
```

---

## 実行（基本）

`src/` で次を実行：

```bash
python scrape_books.py
```

実行後、以下が出力されます（例）：

- `output/books_home.csv` – トップページ一覧
- `output/books_all.csv` – 全ページ巡回の一覧
- `output/books_{CATEGORY_NAME}.csv` – 指定カテゴリの一覧（例: `books_romance_8.csv`）

> 実行時の標準出力で、行数と保存先パスが表示されます。

---

##  設定の切り替え（今後切り替えの簡易化を検討）

- **カテゴリを切り替える**  
  コード冒頭の `CATEGORY_NAME` を変更：

  ```python
  CATEGORY_NAME = "romance_8"  # 例: "philosophy_7", "travel_2" など
  ```

- **出力先を変える**  
  `OUT_DIR` を任意パスに変更：

  ```python
  OUT_DIR = "/absolute/path/to/output"
  ```

- **待機時間を調整**  
  `scrape_all_pages_to_df(sleep_sec=1)` のように引数で制御（`None` ならスキップ）。

---

##  取得データのスキーマ（CSV列）

| 列名           | 説明                                              |
|----------------|---------------------------------------------------|
| `title`        | 書籍タイトル（`title` 属性があれば優先）         |
| `detail_url`   | 書籍詳細ページの絶対URL                           |
| `price_text`   | 価格（例: `£51.77` の文字列のまま）               |
| `availability` | 在庫表示（改行や余白を圧縮済み）                  |
| `rating`       | 星評価（`One`/`Two`/`Three`/`Four`/`Five`）       |
| `list_page_url`| その行を取得した一覧ページのURL                   |

---

## 実行例（標準出力）

```
[OK] home: 20 rows -> /path/to/output/books_home.csv
[OK] all: 1000 rows -> /path/to/output/books_all.csv
```

---
