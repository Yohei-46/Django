import joblib
import pandas as pd
from django.core.management.base import BaseCommand
from race.models import RaceResult
from race.scraper import scrape_race_result

MODEL_PATH = "models/win_model.pkl"

class Command(BaseCommand):
    help = "指定レースIDに対して1着予測を行う（単勝）"

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=str, help="予測対象の race_id")

    def handle(self, *args, **options):
        race_id = options["race_id"]

        # スクレイピングしてデータベースに保存（もし未取得なら）
        scrape_race_result(race_id)

        # race_id に対応する全馬取得
        horses = RaceResult.objects.filter(race_id=race_id)

        if not horses.exists():
            self.stderr.write(f"❌ レースID {race_id} にデータが存在しません。")
            return

        # モデル読み込み
        model = joblib.load(MODEL_PATH)

        # データ整形
        df = pd.DataFrame.from_records(
            horses.values("horse_number", "horse_name", "popularity", "odds", "distance")
        )

        X = df[["popularity", "odds", "distance"]]
        preds = model.predict_proba(X)[:, 1]  # 1着になる確率（クラス1の確率）

        df["勝率予測（%）"] = (preds * 100).round(2)

        # 勝率順に表示
        df = df.sort_values(by="勝率予測（%）", ascending=False)

        print("\n📊 単勝予測（1着になる確率）:")
        print(df[["horse_number", "horse_name", "popularity", "odds", "勝率予測（%）"]].to_string(index=False))
import joblib
import pandas as pd
from django.core.management.base import BaseCommand
from race.models import RaceResult
from race.scraper import scrape_race_result

MODEL_PATH = "models/win_model.pkl"

class Command(BaseCommand):
    help = "指定レースIDに対して1着予測を行う（単勝）"

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=str, help="予測対象の race_id")

    def handle(self, *args, **options):
        race_id = options["race_id"]

        # スクレイピングしてデータベースに保存（もし未取得なら）
        scrape_race_result(race_id)

        # race_id に対応する全馬取得
        horses = RaceResult.objects.filter(race_id=race_id)

        if not horses.exists():
            self.stderr.write(f"❌ レースID {race_id} にデータが存在しません。")
            return

        # モデル読み込み
        model = joblib.load(MODEL_PATH)

        # データ整形
        df = pd.DataFrame.from_records(
            horses.values("horse_number", "horse_name", "popularity", "odds", "distance")
        )

        X = df[["popularity", "odds", "distance"]]
        preds = model.predict_proba(X)[:, 1]  # 1着になる確率（クラス1の確率）

        df["勝率予測（%）"] = (preds * 100).round(2)

        # 勝率順に表示
        df = df.sort_values(by="勝率予測（%）", ascending=False)

        print("\n📊 単勝予測（1着になる確率）:")
        print(df[["horse_number", "horse_name", "popularity", "odds", "勝率予測（%）"]].to_string(index=False))
