"""Страницы действующих заказов."""

from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from menu.models import Dish

from .models import Order

SORTS = {
    "recent": ("-id",),
    "visitor": ("visitor__name", "id"),
    "price": ("-dish__price", "id"),
}
PAGE_SIZE = 5


def order_list(request: HttpRequest) -> HttpResponse:
    """Вывести заказы с поиском, фильтрами и разбивкой на страницы."""
    search = request.GET.get("q", "").strip()
    dish = request.GET.get("dish", "")
    sort = request.GET.get("sort", "recent")
    if sort not in SORTS:
        sort = "recent"

    status = request.GET.get("status", Order.Status.ACTIVE)
    if status not in (*Order.Status.values, "all"):
        status = Order.Status.ACTIVE

    date_text = request.GET.get("date", "").strip()
    error = ""
    orders = Order.objects.with_details()
    if status == Order.Status.ACTIVE:
        orders = orders.active()
    elif status != "all":
        orders = orders.filter(status=status)
    if search:
        orders = orders.search(search)
    if dish:
        orders = orders.filter(dish__name=dish)
    if date_text:
        try:
            orders = orders.for_date(date.fromisoformat(date_text))
        except ValueError:
            error = "Укажите дату в формате ГГГГ-ММ-ДД."
            orders = orders.none()
    totals = orders.aggregate(
        count=Count("pk"), total=Sum("dish__price", default=0),
    )
    paginated = Paginator(orders.order_by(*SORTS[sort]), PAGE_SIZE)
    page = paginated.get_page(request.GET.get("page"))

    return render(
        request,
        "orders.html",
        {
            "orders": page.object_list,
            "page": page,
            "dishes": Dish.objects.order_by("name").values("name"),
            "selected_dish": dish,
            "search": search,
            "sort": sort,
            "selected_status": status,
            "statuses": Order.Status.choices,
            "date": date_text,
            "date_error": error,
            **totals,
        },
        status=400 if error else 200,
    )


def order_detail(request: HttpRequest, visitor: str) -> HttpResponse:
    """Показать действующий заказ выбранного посетителя."""
    order = get_object_or_404(
        Order.objects.active().with_details(), visitor__name=visitor,
    )
    return render(request, "order_detail.html", {"order": order})


def order_history_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Показать конкретный заказ независимо от состояния."""
    order = get_object_or_404(Order.objects.with_details(), pk=pk)
    return render(request, "order_detail.html", {"order": order})
