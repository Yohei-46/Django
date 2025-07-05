from django.shortcuts import render
from .models import RaceResult
from .batch_scraper import run_batch_scraping, generate_race_ids, PLACE_CODE_MAP

import joblib
import pandas as pd
import os

# モデルパス
TRIFECTA_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'trifecta_model.pkl')
WIN_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'win_model.pkl')

# モデルロード
trifecta_model = joblib.load(TRIFECTA_MODEL_PATH) if os.path.exists(TRIFECTA_MODEL_PATH) else None
win_model = joblib.load(WIN_MODEL_PATH) if os.path.exists(WIN_MODEL_PATH) else None


# 1) スクレイピング用ビュー
def scrape_data_view(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        place_name = request.POST.get("place_name")

        try:
            race_ids = generate_race_ids(start_date, end_date, place_name)
            existing_ids = set(RaceResult.objects.filter(race_id__in=race_ids).values_list('race_id', flat=True))
            new_race_ids = [rid for rid in race_ids if rid not in existing_ids]

            # スクレイピング処理
            run_batch_scraping(new_race_ids)

            message = f"{len(new_race_ids)} 件のレースを新たに取得しました。"
            return render(request, "scrape_form.html", {
                "success": True,
                "message": message,
                "places": list(PLACE_CODE_MAP.keys()),
            })
        except Exception as e:
            return render(request, "scrape_form.html", {
                "error": str(e),
                "success": False,
                "places": list(PLACE_CODE_MAP.keys()),
            })

    # GET時はフォーム表示のみ
    return render(request, "scrape_form.html", {
        "places": list(PLACE_CODE_MAP.keys()),
        "success": False,
        "error": None,
    })


# 2) 予測用ビュー
def predict_view(request):
    prediction_error = None
    trifecta_predictions = None
    win_predictions = None
    race_id_for_predict = ""

    if request.method == "POST":
        race_id_for_predict = request.POST.get("predict_race_id")
        if not race_id_for_predict:
            prediction_error = "予測したいレースIDを入力してください。"
        else:
            race_results = RaceResult.objects.filter(race_id=race_id_for_predict).order_by('popularity')[:6]
            if race_results.count() < 3:
                prediction_error = "馬の数が不足しているため予測できません。"
            else:
                # 3連単予測
                trifecta_rows = []
                for i in range(len(race_results)):
                    for j in range(len(race_results)):
                        for k in range(len(race_results)):
                            if len({i,j,k}) < 3:
                                continue
                            h1, h2, h3 = race_results[i], race_results[j], race_results[k]
                            row = {
                                "odds1": float(h1.odds),
                                "pop1": int(h1.popularity),
                                "odds2": float(h2.odds),
                                "pop2": int(h2.popularity),
                                "odds3": float(h3.odds),
                                "pop3": int(h3.popularity),
                            }
                            trifecta_rows.append((f"{h1.horse_number}-{h2.horse_number}-{h3.horse_number}", row))

                df_trifecta = pd.DataFrame([r[1] for r in trifecta_rows])
                trifecta_probs = trifecta_model.predict_proba(df_trifecta)[:, 1] if trifecta_model else []
                top5_trifecta = sorted(zip([r[0] for r in trifecta_rows], trifecta_probs), key=lambda x: x[1], reverse=True)[:5]
                trifecta_predictions = [{"combination": comb, "probability": f"{prob:.4f}"} for comb, prob in top5_trifecta]

                # 単勝予測
                df_win = pd.DataFrame([{
                    "popularity": h.popularity if h.popularity is not None else 0,
                    "odds": h.odds if h.odds is not None else 0.0,
                    "distance": h.distance if h.distance is not None else 0,
                } for h in race_results])
                win_probs = win_model.predict_proba(df_win)[:, 1] if win_model else []
                win_predictions = sorted(
                    [(h.horse_number, h.horse_name, f"{p:.4f}") for h, p in zip(race_results, win_probs)],
                    key=lambda x: x[2], reverse=True
                )

    return render(request, "predict_form.html", {
        "error": prediction_error,
        "trifecta_predictions": trifecta_predictions,
        "win_predictions": win_predictions,
        "predict_race_id": race_id_for_predict,
    })
