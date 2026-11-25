"""Страницы меню столовой."""

from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Dish


def dish_list(request: HttpRequest) -> HttpResponse:
    """Вывести меню с поиском по названию и доступности на дату."""
    selected_date = request.GET.get("date", "").strip()
    search = request.GET.get("q", "").strip()
    error = ""
    dishes = Dish.objects.all()
    if search:
        dishes = dishes.filter(name__icontains=search)
    if selected_date:
        try:
            day = date.fromisoformat(selected_date)
        except ValueError:
            error = "Укажите дату в формате ГГГГ-ММ-ДД."
        else:
            dishes = dishes.available_on(day)

    return render(
        request,
        "dish_list.html",
        {
            "dishes": sorted(dishes, key=lambda dish: dish.name.casefold()),
            "date": selected_date,
            "search": search,
            "date_error": error,
        },
        status=400 if error else 200,
    )


def dish_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Показать цену и доступность выбранного блюда."""
    dish = get_object_or_404(Dish, slug=slug)
    return render(request, "dish_detail.html", {"dish": dish})


def legacy_detail(request: HttpRequest, name: str) -> HttpResponse:
    """Перенаправить старый адрес блюда на карточку по slug."""
    return redirect(get_object_or_404(Dish, name=name))
