from django.urls import path
from .views import scrape_data_view, predict_view

urlpatterns = [
    path('scrape/', scrape_data_view, name='scrape_data'),      # スクレイピング実行用
    path('predict/', predict_view, name='predict'),            # 予測実行用
]