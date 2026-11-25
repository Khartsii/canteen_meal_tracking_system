"""Страницы действующих заказов."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from storage import DATA_FILE, load_data


def order_list(request: HttpRequest) -> HttpResponse:
    """Показать заказы и их общую стоимость."""
    canteen = load_data(DATA_FILE)
    count, total = canteen.order_statistics()
    return render(
        request,
        "orders.html",
        {"orders": canteen.orders.values(), "count": count, "total": total},
    )


def order_detail(request: HttpRequest, visitor: str) -> HttpResponse:
    """Показать действующий заказ выбранного посетителя."""
    order = load_data(DATA_FILE).orders.get(visitor)
    if order is None:
        raise Http404("Заказ не найден.")
    return render(request, "order_detail.html", {"order": order})
