"""Главная страница и страницы ошибок."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу столовой."""
    return render(request, "home.html")


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Показать страницу для отсутствующего адреса или блюда."""
    return render(request, "404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    """Показать сообщение об ошибке сервера."""
    return render(request, "500.html", status=500)
