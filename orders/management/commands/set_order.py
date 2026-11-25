"""Создание и изменение действующего заказа через ORM."""

from argparse import ArgumentParser
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import localdate

from menu.models import Dish
from orders.models import Order, Visitor


class Command(BaseCommand):
    """Установить блюдо в действующем заказе посетителя."""

    help = "Создать или изменить действующий заказ."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Принять имя посетителя и название блюда."""
        parser.add_argument("visitor")
        parser.add_argument("dish")
        parser.add_argument("--date", type=date.fromisoformat)

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        """Проверить справочники и сохранить заказ."""
        try:
            visitor = Visitor.objects.get(name=options["visitor"])
            day = options["date"] or localdate()
            active = Order.objects.active()
            previous = active.filter(visitor=visitor).first()
            dishes = Dish.objects.available_on(
                day, exclude_order=previous.pk if previous else None,
            )
            dish = dishes.get(name=options["dish"])
        except Visitor.DoesNotExist as error:
            raise CommandError("Посетитель не найден.") from error
        except Dish.DoesNotExist as error:
            raise CommandError("Блюдо не найдено или недоступно.") from error

        _, created = active.update_or_create(
            visitor=visitor, defaults={"dish": dish, "meal_date": day},
        )
        self.stdout.write("Заказ создан." if created else "Заказ изменён.")
