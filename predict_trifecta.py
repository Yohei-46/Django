import os
import django

# Django設定を最初に読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keiba_predictor.settings')
django.setup()

# ↑ django.setup() のあとで model を読み込む
from race.models import RaceResult

import pandas as pd
import joblib
import itertools

def load_race_data(race_id):
    results = RaceResult.objects.filter(race_id=race_id).exclude(rank__isnull=True)
    data = []

    for r in results:
        try:
            data.append({
                "horse_number": int(r.horse_number),
                "odds": float(r.odds),
                "popularity": int(r.popularity),
            })
        except Exception as e:
            print(f"[SKIP] 不正なデータ: {r.horse_number}, {r.odds}, {r.popularity}")
            continue

    return pd.DataFrame(data)

def generate_trifecta_combinations(df):
    horses = df["horse_number"].tolist()
    return list(itertools.permutations(horses, 3))  # 着順順に並んだ組み合わせ

def main():
    race_id = input("予測したいレースIDを入力してください: ").strip()

    df = load_race_data(race_id)
    if len(df) < 3:
        print(f"❌ 馬の数が足りません（{len(df)}頭）")
        return

    combinations = generate_trifecta_combinations(df)

    # モデル読み込み
    model = joblib.load("models/trifecta_model.pkl")

    preds = []
    for comb in combinations:
        horses_df = df.set_index("horse_number")
        h1 = horses_df.loc[comb[0]]
        h2 = horses_df.loc[comb[1]]
        h3 = horses_df.loc[comb[2]]

        row = pd.DataFrame([{
            "odds1": h1["odds"], "pop1": h1["popularity"],
            "odds2": h2["odds"], "pop2": h2["popularity"],
            "odds3": h3["odds"], "pop3": h3["popularity"],
        }])

        prob = model.predict_proba(row)[0][1]  # [1] は「的中する」確率
        preds.append((comb, prob))

    # 上位5件を出力
    preds.sort(key=lambda x: x[1], reverse=True)
    print("\n🎯 上位3連単予測:")
    for i, (trio, prob) in enumerate(preds[:5], 1):
        print(f"{i}: {'-'.join(map(str, trio))}（予測確率: {prob:.4f}）")

if __name__ == "__main__":
    main()