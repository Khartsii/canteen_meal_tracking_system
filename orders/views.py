"""Страницы действующих заказов."""

from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
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

    orders = Order.objects.select_related("visitor", "dish")
    if search:
        orders = orders.filter(
            Q(visitor__name__icontains=search)
            | Q(dish__name__icontains=search),
        )
    if dish:
        orders = orders.filter(dish__name=dish)
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
            **totals,
        },
    )


def order_detail(request: HttpRequest, visitor: str) -> HttpResponse:
    """Показать действующий заказ выбранного посетителя."""
    order = get_object_or_404(
        Order.objects.select_related("visitor", "dish"), visitor__name=visitor,
    )
    return render(request, "order_detail.html", {"order": order})
