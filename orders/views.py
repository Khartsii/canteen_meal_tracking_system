"""Страница действующих заказов."""

from django.http import HttpRequest, HttpResponse
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
