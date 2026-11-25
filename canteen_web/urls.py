"""Корневые маршруты сайта столовой."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("menu/", include("menu.urls")),
    path("orders/", include("orders.urls")),
]

handler404 = "homepage.views.page_not_found"
handler500 = "homepage.views.server_error"


if settings.TOOLBAR_ENABLED:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
