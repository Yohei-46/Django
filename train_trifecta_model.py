# train_trifecta_model.py

import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier

# 学習データ読み込み
df = pd.read_csv("data/trifecta_training_data.csv")

# データ整形：レースごとに3連単パターンごとの特徴量を作成
grouped = df.groupby("race_id")
rows = []

for race_id, group in grouped:
    if len(group) < 3:
        continue

    horses = group.sort_values("popularity")
    horses = horses.head(6)  # 上位6頭を候補にする

    for i in range(len(horses)):
        for j in range(len(horses)):
            for k in range(len(horses)):
                if len(set([i, j, k])) < 3:
                    continue
                h1 = horses.iloc[i]
                h2 = horses.iloc[j]
                h3 = horses.iloc[k]
                trifecta = f"{h1.horse_number}-{h2.horse_number}-{h3.horse_number}"
                label = (trifecta == h1.trifecta)
                rows.append({
                    "odds1": float(h1.odds),
                    "pop1": int(h1.popularity),
                    "odds2": float(h2.odds),
                    "pop2": int(h2.popularity),
                    "odds3": float(h3.odds),
                    "pop3": int(h3.popularity),
                    "label": int(label)
                })

X = pd.DataFrame(rows).drop(columns="label")
y = pd.DataFrame(rows)["label"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/trifecta_model.pkl")
print("✅ 3連単モデルを保存しました")