"""Модели посетителей и действующих заказов."""

from django.db import models

from menu.models import Dish


class Visitor(models.Model):
    """Зарегистрированный посетитель."""

    name = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        """Вернуть имя посетителя."""
        return self.name


class Order(models.Model):
    """Один действующий заказ посетителя."""

    visitor = models.OneToOneField(
        Visitor, on_delete=models.PROTECT, related_name="order",
    )
    dish = models.ForeignKey(
        Dish, on_delete=models.PROTECT, related_name="orders",
    )

    def __str__(self) -> str:
        """Вернуть посетителя и блюдо."""
        return f"{self.visitor} — {self.dish}"
