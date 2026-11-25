"""Страницы действующих заказов."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import select


def order_list(request: HttpRequest) -> HttpResponse:
    """Показать заказы и их общую стоимость."""
    totals = select("order_totals")[0]
    return render(
        request,
        "orders.html",
        {
            "orders": select("orders"),
            "count": totals["count"],
            "total": totals["total"],
        },
    )


def order_detail(request: HttpRequest, visitor: str) -> HttpResponse:
    """Показать действующий заказ выбранного посетителя."""
    orders = select("order_detail", visitor)
    if not orders:
        raise Http404("Заказ не найден.")
    return render(request, "order_detail.html", {"order": orders[0]})
