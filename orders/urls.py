"""Маршруты списка и карточки заказов."""

from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("", views.order_list, name="list"),
    path("id/<int:pk>/", views.order_history_detail, name="by_id"),
    path("<path:visitor>/", views.order_detail, name="detail"),
]
