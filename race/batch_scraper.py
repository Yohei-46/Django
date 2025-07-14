from .models import RaceResult
from .scraper import scrape_race_result
from datetime import datetime, timedelta

# 地名からplaceコードへ変換
PLACE_CODE_MAP = {
    '札幌': '01',
    '函館': '02',
    '福島': '03',
    '新潟': '04',
    '東京': '05',
    '中山': '06',
    '中京': '07',
    '京都': '08',
    '阪神': '09',
    '小倉': '10',
}

'''
race_idの命名規則
IDは12桁で構成。
例：202505020204

年（YYYY)：「2025」/開催年
場所コード：「05」/東京競馬場（PLACE_CODE_MAPより）
開催回：「02」/開催2回
開催日：「02」/開催2日目
レース番号：「04」/第4レース
'''

print("[LOG] batch_scraper.py がインポートされました")

import time
def run_batch_scraping(race_ids):
    for race_id in race_ids:
        if RaceResult.objects.filter(race_id=race_id).exists():
            print(f"[SKIP] {race_id} は既に保存されています")
            continue

        try:
            print(f"[INFO] スクレイピング中: {race_id}")
            success = scrape_race_result(race_id)
            if not success:
                print(f"[❌] {race_id} テーブル見つからず")
        except Exception as e:
            print(f"[ERROR] {race_id} の処理中に例外: {e}")

        print("[WAIT] 5秒待機中...")
        time.sleep(5)

def generate_race_ids(start_date: str, end_date: str, place_name: str):
    """
    指定した期間と場所に対応する race_id の一覧を生成する（12桁形式）。
    """
    place_code = PLACE_CODE_MAP.get(place_name)
    if not place_code:
        raise ValueError(f"無効な開催地: {place_name}")

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    race_ids = []
    current = start

    while current <= end:
        date_str = current.strftime("%Y%m%d")  # YYYYMMDD
        for day_num in range(1, 13):  # 開催日
            for race_num in range(1, 13):  # レース番号
                # ✅ 正しい12桁形式：日付 + 場所 + 開催日 + レース番号
                race_id = f"{date_str}{place_code}{race_num:02}"
                race_ids.append(race_id)
        current += timedelta(days=1)

    return race_ids
