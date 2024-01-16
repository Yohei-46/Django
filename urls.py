from django.urls import path
from . import ajax, views

app_name = 'othello'

urlpatterns = [
    path("", views.IndexView.as_view(),name='index'),
    path("history/save/",ajax.save_history, name='save_history'),
    path("storage/save/",ajax.save_storage, name='save_storage'),
    path("storage/get/",ajax.get_storage, name='get_storage'),
]
