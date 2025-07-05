from django.core.management.base import BaseCommand
from race.models import RaceResult
import pandas as pd
from pathlib import Path

class Command(BaseCommand):
    help = "RaceResultモデルからCSVファイルに学習データをエクスポート"

    def handle(self, *args, **options):
        # クエリセットを取得
        results = RaceResult.objects.all().values(
            'race_id', 'horse_number', 'horse_name', 'popularity', 'odds', 'rank', 'distance'
        )

        if not results.exists():
            self.stdout.write(self.style.WARNING("エクスポート対象のデータが存在しません。"))
            return

        df = pd.DataFrame(results)

        # 型変換（文字列→数値）など必要に応じて追加
        df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
        df['odds'] = pd.to_numeric(df['odds'], errors='coerce')
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')

        df.dropna(subset=['rank'], inplace=True)  # 着順が無い行を除外（出走取消など）

        # ファイル保存
        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "training_race_data.csv"
        df.to_csv(output_file, index=False)

        self.stdout.write(self.style.SUCCESS(f"✅ 学習データを {output_file} に保存しました。"))
