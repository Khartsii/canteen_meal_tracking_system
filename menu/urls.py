"""Маршруты меню и карточки блюда."""

from django.urls import path

from . import views

app_name = "menu"
urlpatterns = [
    path("", views.dish_list, name="list"),
    path("dish/<slug:slug>/", views.dish_detail, name="detail"),
    path("<path:name>/", views.legacy_detail, name="legacy_detail"),
]
