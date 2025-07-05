import requests
from bs4 import BeautifulSoup

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

race_id = "202505020106"
url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}"

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ リクエスト失敗: {e}")
    exit()

# 自動判別されたエンコーディングを使用
response.encoding = response.apparent_encoding
print("📄 Response encoding:", response.encoding)

html = response.text
soup = BeautifulSoup(html, "html.parser")

# デバッグ用に保存
with open("debug.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())

# 結果テーブルのセレクタ候補を複数試す
result_table = (
    soup.select_one("#All_Result_Table") or
    soup.select_one(".RaceResultTable") or
    soup.select_one(".RaceTable01")
)

if result_table:
    print("✅ レース結果テーブルを取得できました。")
else:
    print("❌ レース結果テーブルが見つかりませんでした。debug情報を保存します。")
    with open("error_debug.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())