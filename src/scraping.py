# --- 変数説明 ---
# URL: サイトのトップページURL
# BASE_URL: 詳細ページURL生成用のベースURL（1ページ目）
# CATEGORY_NAME: スクレイピング対象カテゴリー名（例: "romance_8"）
#
# scrape_home_to_df: トップページの本一覧をDataFrameで取得
# scrape_page_to_df: 指定ページ番号の本一覧をDataFrameで取得
# scrape_all_pages_to_df: 全ページの本一覧をDataFrameで取得
# scrape_category_to_df: 指定カテゴリーの全ページの本一覧をDataFrameで取得
# get_category_url: カテゴリー名から1ページ目のURLを生成
# save_csv: DataFrameをCSV保存
# sleep_between_requests: リクエスト間の待機
# main: 実行メイン関数
#
# 変数や関数の詳細は各定義部のdocstringも参照してください

import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
from urllib.parse import urljoin
import os

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))

URL = "http://books.toscrape.com/"
BASE_URL = "http://books.toscrape.com/catalogue/page-1.html"
CATEGORY_NAME = "romance_8"


def scrape_home_to_df():
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")

    books = []
    for card in soup.select("article.product_pod"):
        a = card.select_one("h3 a")
        # タイトル（title属性がフル、無ければテキスト）
        title = (a.get("title") or a.get_text(strip=True)) if a else ""

        # 詳細ページURL（相対→絶対）
        rel = a.get("href", "") if a else ""
        detail_url = urljoin(BASE_URL, rel)

        # 価格（文字列と数値）
        price_el = card.select_one(".price_color")
        price_text = price_el.get_text(strip=True) if price_el else ""

        # 在庫（改行や余白の圧縮）
        avail_el = card.select_one(".availability")
        availability = " ".join(avail_el.get_text().split()) if avail_el else ""

        # 星評価（クラス名から 'One' 'Two' ... を抽出）
        rating_el = card.select_one("p.star-rating")
        rating = ""
        if rating_el:
            classes = rating_el.get("class", [])
            rating = next((c for c in classes if c.lower() != "star-rating"), "")

        books.append({
            "title": title,
            "detail_url": detail_url,
            "price_text": price_text,
            "availability": availability,
            "rating": rating,
            "list_page_url": BASE_URL,
        })
    # DataFrame形式で返す
    return pd.DataFrame(books)


def scrape_page_to_df(page_num):
    """
    指定ページ番号の本データをDataFrameで取得
    """
    page_url = f"http://books.toscrape.com/catalogue/page-{page_num}.html"
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    books = []
    for card in soup.select("article.product_pod"):
        a = card.select_one("h3 a")
        title = (a.get("title") or a.get_text(strip=True)) if a else ""
        rel = a.get("href", "") if a else ""
        detail_url = urljoin(page_url, rel)
        price_el = card.select_one(".price_color")
        price_text = price_el.get_text(strip=True) if price_el else ""
        avail_el = card.select_one(".availability")
        availability = " ".join(avail_el.get_text().split()) if avail_el else ""
        rating_el = card.select_one("p.star-rating")
        rating = ""
        if rating_el:
            classes = rating_el.get("class", [])
            rating = next((c for c in classes if c.lower() != "star-rating"), "")
        books.append({
            "title": title,
            "detail_url": detail_url,
            "price_text": price_text,
            "availability": availability,
            "rating": rating,
            "list_page_url": page_url,
        })
    return pd.DataFrame(books)

def sleep_between_requests():
    import time
    time.sleep(3)  # 1秒待機

# save_csv関数をpandasで実装

def save_csv(data, filename, out_dir=None):
    import os
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, filename)
    else:
        filepath = filename
    data.to_csv(filepath, index=False)

#　ページ遷移

def scrape_all_pages_to_df(sleep_sec=3):
    """
    最後のページまで全ての本データを取得し、1つのDataFrameで返す
    """
    df = pd.DataFrame()
    page_num = 1
    while True:
        df_page = scrape_page_to_df(page_num)
        if df_page.empty:
            break
        df = pd.concat([df, df_page], ignore_index=True)
        page_num += 1
        sleep_between_requests() if sleep_sec else None
    return df

# カテゴリーを選択してスクレイピング

def scrape_category_to_df(category_url, sleep_sec=3):
    """
    指定カテゴリーの全ての本データを取得し、1つのDataFrameで返す
    category_url: カテゴリの1ページ目のURL（例: .../category/books/philosophy_7/index.html）
    """
    df = pd.DataFrame()
    page_num = 1
    while True:
        if page_num == 1:
            page_url = category_url
        else:
            # 2ページ目以降はpage-{n}.htmlに遷移
            base_url = category_url.rsplit('/', 1)[0]
            page_url = f"{base_url}/page-{page_num}.html"
        response = requests.get(page_url)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.content, "html.parser")
        books = []
        for card in soup.select("article.product_pod"):
            a = card.select_one("h3 a")
            title = (a.get("title") or a.get_text(strip=True)) if a else ""
            rel = a.get("href", "") if a else ""
            detail_url = urljoin(page_url, rel)
            price_el = card.select_one(".price_color")
            price_text = price_el.get_text(strip=True) if price_el else ""
            avail_el = card.select_one(".availability")
            availability = " ".join(avail_el.get_text().split()) if avail_el else ""
            rating_el = card.select_one("p.star-rating")
            rating = ""
            if rating_el:
                classes = rating_el.get("class", [])
                rating = next((c for c in classes if c.lower() != "star-rating"), "")
            books.append({
                "title": title,
                "detail_url": detail_url,
                "price_text": price_text,
                "availability": availability,
                "rating": rating,
                "list_page_url": page_url,
            })
        df_page = pd.DataFrame(books)
        if df_page.empty:
            break
        df = pd.concat([df, df_page], ignore_index=True)
        page_num += 1
        sleep_between_requests() if sleep_sec else None
    return df

def get_category_url(CATEGORY_NAME):
    """
    カテゴリー名（例: 'travel_2'）から1ページ目のURLを生成
    """      

    return f"https://books.toscrape.com/catalogue/category/books/{CATEGORY_NAME}/index.html"


def main():
    # トップページの本一覧取得
    df_home = scrape_home_to_df()
    # 全ページ分を取得
    df_all = scrape_all_pages_to_df(sleep_sec=3)
    # 出力先ディレクトリを指定可能に
    save_csv(df_home, "books_home.csv", out_dir=OUT_DIR)
    save_csv(df_all, "books_all.csv", out_dir=OUT_DIR)
    print(f"[OK] home: {len(df_home)} rows -> {OUT_DIR}/books_home.csv")
    print(f"[OK] all: {len(df_all)} rows -> {OUT_DIR}/books_all.csv")
    # カテゴリーを指定してスクレイピング
    category_url = get_category_url(CATEGORY_NAME)
    df_travel = scrape_category_to_df(category_url)
    save_csv(df_travel, f"books_{CATEGORY_NAME}.csv", out_dir=OUT_DIR)


if __name__ == "__main__":
    main()
