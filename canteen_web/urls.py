"""Корневые маршруты сайта столовой."""

from django.urls import include, path

urlpatterns = [
    path("", include("homepage.urls")),
    path("menu/", include("menu.urls")),
    path("orders/", include("orders.urls")),
]

handler404 = "homepage.views.page_not_found"
handler500 = "homepage.views.server_error"
