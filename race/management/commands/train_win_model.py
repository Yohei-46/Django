import pandas as pd
import os
import joblib
from django.core.management.base import BaseCommand
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DATA_PATH = "data/training_race_data.csv"
MODEL_PATH = "models/win_model.pkl"

class Command(BaseCommand):
    help = "単勝予測モデルの学習"

    def handle(self, *args, **kwargs):
        if not os.path.exists(DATA_PATH):
            self.stderr.write(f"❌ データが存在しません: {DATA_PATH}")
            return

        df = pd.read_csv(DATA_PATH)

        # 特徴量とラベル
        df = df.dropna()
        X = df[["popularity", "odds", "distance"]]
        y = (df["rank"] == 1).astype(int)  # 1着なら1、それ以外は0

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LogisticRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        print("📊 評価レポート:\n", classification_report(y_test, y_pred))

        # モデル保存
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print(f"✅ モデルを保存しました: {MODEL_PATH}")
