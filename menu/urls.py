"""Маршруты меню и карточки блюда."""

from django.urls import path

from . import views

app_name = "menu"
urlpatterns = [
    path("", views.dish_list, name="list"),
    path("<path:name>/", views.dish_detail, name="detail"),
]
