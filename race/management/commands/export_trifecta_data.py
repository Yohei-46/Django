from django.core.management.base import BaseCommand
from race.models import RaceResult
import pandas as pd
import os
from collections import defaultdict

class Command(BaseCommand):
    help = "3連単予測用の学習データをCSVで出力"

    def handle(self, *args, **kwargs):
        grouped = defaultdict(list)

        for result in RaceResult.objects.all():
            grouped[result.race_id].append(result)

        rows = []
        skipped = 0

        for race_id, results in grouped.items():
            if len(results) < 3:
                skipped += 1
                continue

            # 着順がついていない馬を除外（失格や中止など）
            valid_results = [r for r in results if r.rank and isinstance(r.rank, int)]
            if len(valid_results) < 3:
                skipped += 1
                continue

            sorted_results = sorted(valid_results, key=lambda r: r.rank)
            top3 = sorted_results[:3]
            trifecta = "-".join(str(r.horse_number) for r in top3)

            for r in results:
                rows.append({
                    "race_id": r.race_id,
                    "horse_number": r.horse_number,
                    "odds": r.odds,
                    "popularity": r.popularity,
                    "rank": r.rank,
                    "trifecta": trifecta,
                })

        df = pd.DataFrame(rows)

        os.makedirs("data", exist_ok=True)
        df.to_csv("data/trifecta_training_data.csv", index=False)

        self.stdout.write(self.style.SUCCESS(f"✅ trifecta_training_data.csv を出力しました ({len(df)}件, スキップ: {skipped})"))
