"""Страницы меню столовой."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from storage import DATA_FILE, load_data


def dish_list(request: HttpRequest) -> HttpResponse:
    """Вывести блюда по алфавиту."""
    canteen = load_data(DATA_FILE)
    dishes = sorted(
        canteen.menu.values(), key=lambda dish: dish.name.casefold(),
    )
    return render(request, "dish_list.html", {"dishes": dishes})


def dish_detail(request: HttpRequest, name: str) -> HttpResponse:
    """Показать цену и доступность выбранного блюда."""
    dish = load_data(DATA_FILE).menu.get(name)
    if dish is None:
        raise Http404("Блюдо не найдено.")
    return render(request, "dish_detail.html", {"dish": dish})
