"""Страницы меню столовой."""

from datetime import date

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import select


def dish_list(request: HttpRequest) -> HttpResponse:
    """Вывести меню или доступные на указанную дату блюда."""
    selected_date = request.GET.get("date", "").strip()
    date_error = ""
    dishes = []
    if selected_date:
        try:
            day = date.fromisoformat(selected_date)
        except ValueError:
            date_error = "Укажите дату в формате ГГГГ-ММ-ДД."
        else:
            dishes = select("available_dishes", day.isoformat())
    else:
        dishes = select("dishes")

    dishes.sort(key=lambda dish: dish["name"].casefold())

    return render(
        request,
        "dish_list.html",
        {"dishes": dishes, "date": selected_date, "date_error": date_error},
        status=400 if date_error else 200,
    )


def dish_detail(request: HttpRequest, name: str) -> HttpResponse:
    """Показать цену и доступность выбранного блюда."""
    dishes = select("dish_detail", name)
    if not dishes:
        raise Http404("Блюдо не найдено.")
    return render(request, "dish_detail.html", {"dish": dishes[0]})
