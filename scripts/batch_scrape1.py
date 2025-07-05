#多分ファイルごと消してOK
import os
import django
import time
import sys
from datetime import date, timedelta
from .scraper import scrape_race_result

# プロジェクトルート（manage.pyがあるディレクトリ）をパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Django環境の設定
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keiba_predictor.settings")
django.setup()

from scripts.scrape_and_save import scrape_race_result

# スクレイピングする race_id 一覧
# 開催地名とコードの対応表
PLACE_CODE_MAP = {
    "札幌": "01",
    "函館": "02",
    "福島": "03",
    "新潟": "04",
    "東京": "05",
    "中山": "06",
    "中京": "07",
    "京都": "08",
    "阪神": "09",
    "小倉": "10",
}

# レースIDを生成する
def generate_race_ids(year, month, day, place_code):
    date_str = f"{year:04}{month:02}{day:02}"
    race_ids = []
    for kai in range(1, 6):
        for nichi in range(1, 13):
            for race in range(1, 13):
                race_id = f"{date_str}{place_code}{kai:02}{nichi:02}{race:02}"[-12:]
                race_ids.append(race_id)
    return race_ids

def run_batch_scraping(race_ids):
    for race_id in race_ids:
        print(f"スクレイピング中: {race_id}")
        scrape_race_result(race_id)

#期間の日付リストを作る関数

def daterange(start_date: date, end_date: date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)

def generate_race_ids_for_period(start_date, end_date, place_code, start_race=1, end_race=12):
    all_race_ids = []
    for single_date in daterange(start_date, end_date):
        daily_ids = generate_race_ids(
            year=single_date.year,
            month=single_date.month,
            day=single_date.day,
            place_code=place_code,
            start=start_race,
            end=end_race
        )
        all_race_ids.extend(daily_ids)
    return all_race_ids
    
if __name__ == "__main__":
    # 例: 2023年5月1日〜5月3日、京都（place_code=3）
    start_date = date(2023, 5, 1)
    end_date = date(2023, 5, 3)
    place_code = 3

    race_ids = generate_race_ids(2023, 5, 3, place_code=3)
    run_batch_scraping(race_ids)