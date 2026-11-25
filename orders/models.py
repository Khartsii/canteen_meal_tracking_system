"""Модели посетителей и заказов."""

from datetime import date

from django.db import models

from menu.models import Dish


class OrderStatus(models.TextChoices):
    """Состояния заказа столовой."""

    ACTIVE = "active", "Действующий"
    CANCELLED = "cancelled", "Отменён"
    COMPLETED = "completed", "Выполнен"


class OrderQuerySet(models.QuerySet):
    """Переиспользуемые выборки заказов."""

    def active(self) -> "OrderQuerySet":
        """Вернуть действующие заказы."""
        return self.filter(status=OrderStatus.ACTIVE)

    def for_date(self, day: date) -> "OrderQuerySet":
        """Вернуть заказы с указанной датой."""
        return self.filter(meal_date=day)

    def with_details(self) -> "OrderQuerySet":
        """Загрузить заказ вместе с посетителем и блюдом."""
        return self.select_related("visitor", "dish")

    def search(self, term: str) -> "OrderQuerySet":
        """Найти заказ по посетителю или блюду."""
        return self.filter(
            models.Q(visitor__name__icontains=term)
            | models.Q(dish__name__icontains=term),
        )


class OrderManager(models.Manager.from_queryset(OrderQuerySet)):
    """Менеджер заказов с методами отбора QuerySet."""


class Visitor(models.Model):
    """Зарегистрированный посетитель."""

    name = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        """Вернуть имя посетителя."""
        return self.name


class Order(models.Model):
    """Заказ посетителя с датой и состоянием."""

    Status = OrderStatus
    objects = OrderManager()

    visitor = models.ForeignKey(
        Visitor, on_delete=models.PROTECT, related_name="orders",
    )
    dish = models.ForeignKey(
        Dish, on_delete=models.PROTECT, related_name="orders",
    )
    status = models.CharField(
        max_length=10, choices=OrderStatus.choices, default=OrderStatus.ACTIVE,
    )
    meal_date = models.DateField(null=True, blank=True)

    class Meta:
        """Сохранить правило одного действующего заказа на посетителя."""

        constraints = [
            models.UniqueConstraint(
                fields=["visitor"],
                condition=models.Q(status=OrderStatus.ACTIVE),
                name="orders_one_active_per_visitor",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=OrderStatus.values),
                name="orders_valid_status",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть посетителя и блюдо."""
        return f"{self.visitor} — {self.dish}"
