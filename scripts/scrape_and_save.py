import os
import django
import requests
import re
from bs4 import BeautifulSoup
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Django環境をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keiba_predictor.settings')
django.setup()

from race.models import RaceResult

def scrape_race_result(race_id):
    url = f"https://db.netkeiba.com/race/{race_id}/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        if response.status_code != 200:
            print(f"[ERROR] レースページの取得に失敗しました: status={response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] URL取得失敗: {e}")
        return False

    soup = BeautifulSoup(response.text, "html.parser")

    distance = None
    try:
        race_data_dl = soup.find('dl', class_='racedata')
        if race_data_dl:
            race_text = race_data_dl.find('span').text.strip()
            match = re.search(r"(\d{3,4})m", race_text)
            if match:
                distance = int(match.group(1))
    except Exception as e:
        print(f"[WARN] 距離の取得に失敗しました: {e}")

    result_table = soup.find("table", class_="race_table_01")
    if not result_table:
        print("[ERROR] レース結果テーブルが見つかりません")
        return False

    header_row = result_table.find("tr")
    headers = [th.text.strip() for th in header_row.find_all("th")]

    try:
        horse_number_idx = headers.index("馬番")
        horse_name_idx = headers.index("馬名")
        odds_idx = headers.index("単勝")
        pop_idx = headers.index("人気")
    except ValueError as e:
        print(f"[ERROR] ヘッダーから必要な列を特定できません: {e}")
        return False

    rows = result_table.find_all("tr")[1:]  # ヘッダー行を除く

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 14:
            continue

        try:
            rank = cols[0].text.strip()
            if not rank.isdigit():
                continue  # "除外"などはスキップ

            horse_number = cols[horse_number_idx].text.strip()
            horse_name = cols[horse_name_idx].text.strip()
            odds = cols[odds_idx].text.strip()
            popularity = cols[pop_idx].text.strip()

            print(f"{horse_number}番 {horse_name} - オッズ: {odds}, 人気: {popularity}")

            RaceResult.objects.update_or_create(
                race_id=race_id,
                horse_number=horse_number,
                defaults={
                    'horse_name': horse_name,
                    'odds': odds,
                    'popularity': popularity,
                    'distance': distance,
                    'rank': int(rank),
                }
            )

        except Exception as e:
            print(f"[ERROR] 馬データ処理中に例外: {e}")

    return True

if __name__ == "__main__":
    test_race_id = "202305030811"
    scrape_race_result(test_race_id)