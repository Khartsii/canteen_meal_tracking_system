"""Модели меню и исключений доступности."""

from django.db import models


class Dish(models.Model):
    """Блюдо с ценой и базовой доступностью."""

    name = models.CharField(max_length=200, unique=True)
    price = models.FloatField()
    available = models.BooleanField(default=True)

    class Meta:
        """Ограничения справочника блюд."""

        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="menu_dish_nonnegative_price",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть название блюда."""
        return self.name


class DishUnavailability(models.Model):
    """Ограничение доступности блюда на конкретную дату."""

    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name="unavailability",
    )
    unavailable_date = models.DateField()

    class Meta:
        """Одно исключение на блюдо и дату."""

        constraints = [
            models.UniqueConstraint(
                fields=["dish", "unavailable_date"],
                name="menu_unique_unavailability_date",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть блюдо и дату исключения."""
        return f"{self.dish} — {self.unavailable_date}"
