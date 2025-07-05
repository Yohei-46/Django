import requests
from bs4 import BeautifulSoup
import re
from .models import RaceResult

print("[LOG] scraper.py がインポートされました")

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

    # 距離の取得
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

    # レース結果テーブルの取得
    result_table = soup.find("table", class_="race_table_01")
    if not result_table:
        print("[ERROR] レース結果テーブルが見つかりません")
        return False

    # ヘッダーの列名からインデックス取得
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

    rows = result_table.find_all("tr")[1:]

    saved_count = 0

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < max(horse_number_idx, horse_name_idx, odds_idx, pop_idx) + 1:
            continue

        try:
            rank = cols[0].text.strip()
            if not rank.isdigit():
                continue

            horse_number = cols[horse_number_idx].text.strip()
            horse_name = cols[horse_name_idx].text.strip()
            odds = cols[odds_idx].text.strip()
            popularity = cols[pop_idx].text.strip()

            print(f"🐴 {horse_number}番 {horse_name} - オッズ: {odds}, 人気: {popularity}")

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
            saved_count += 1

        except Exception as e:
            print(f"[ERROR] 馬データ処理中に例外: {e}")

    if saved_count > 0:
        print(f"[SUCCESS] {race_id}：{saved_count}件の馬データを保存")
        return True
    else:
        print(f"[WARN] {race_id}：保存された馬データがありません")
        return False
