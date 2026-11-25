"""Главная страница и страницы ошибок."""

from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from menu.models import Dish
from orders.models import Order, Visitor


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу столовой."""
    return render(request, "home.html")


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Показать страницу для отсутствующего адреса или блюда."""
    return render(request, "404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    """Показать сообщение об ошибке сервера."""
    return render(request, "500.html", status=500)


def statistics(request: HttpRequest) -> HttpResponse:
    """Показать статистику меню, посетителей и заказов."""
    return render(
        request,
        "statistics.html",
        {
            "visitor_count": Visitor.objects.count(),
            "orders": Order.objects.active().aggregate(
                count=Count("pk"), total=Sum("dish__price", default=0),
            ),
            "status_totals": Order.objects.aggregate(
                active=Count("pk", filter=Q(status=Order.Status.ACTIVE)),
                cancelled=Count("pk", filter=Q(status=Order.Status.CANCELLED)),
                completed=Count("pk", filter=Q(status=Order.Status.COMPLETED)),
            ),
            "prices": Dish.objects.aggregate(
                minimum=Min("price"), maximum=Max("price"),
                average=Avg("price"),
            ),
            "dish_counts": Dish.objects.values("available").annotate(
                count=Count("pk"),
            ).order_by("-available"),
            "ordered_dishes": Dish.objects.annotate(
                count=Count(
                    "orders", filter=Q(orders__status=Order.Status.ACTIVE),
                ),
            ).filter(count__gt=0).order_by("-count", "name"),
        },
    )
