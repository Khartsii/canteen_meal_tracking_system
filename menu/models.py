"""Модели меню и исключений доступности."""

from datetime import date

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class DishQuerySet(models.QuerySet):
    """Выборки блюд по доступности."""

    def available_on(
        self, day: date, exclude_order: int | None = None,
    ) -> "DishQuerySet":
        """Найти блюда с незарезервированными порциями на дату."""
        from orders.models import OrderStatus

        reservations = models.Q(
            orders__status=OrderStatus.ACTIVE, orders__meal_date=day,
        )
        if exclude_order is not None:
            reservations &= ~models.Q(orders__pk=exclude_order)
        return self.filter(available=True).exclude(
            unavailability__unavailable_date=day,
        ).annotate(
            reserved=models.Count("orders", filter=reservations),
        ).filter(
            models.Q(daily_portions__isnull=True)
            | models.Q(daily_portions__gt=models.F("reserved")),
        )


class Dish(models.Model):
    """Блюдо с ценой и базовой доступностью."""

    objects = DishQuerySet.as_manager()

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    price = models.FloatField()
    daily_portions = models.PositiveIntegerField(null=True, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        """Ограничения справочника блюд."""

        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="menu_dish_nonnegative_price",
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        """Заполнить постоянный slug при первом сохранении."""
        if not self.slug:
            base = slugify(self.name) or "dish"
            self.slug = base
            suffix = 2
            dishes = Dish.objects.exclude(pk=self.pk)
            while dishes.filter(slug=self.slug).exists():
                self.slug = f"{base}-{suffix}"
                suffix += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Вернуть адрес карточки блюда."""
        return reverse("menu:detail", kwargs={"slug": self.slug})

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
