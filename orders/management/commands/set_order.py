"""Создание и изменение действующего заказа через ORM."""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from menu.models import Dish
from orders.models import Order, Visitor


class Command(BaseCommand):
    """Установить блюдо в действующем заказе посетителя."""

    help = "Создать или изменить действующий заказ."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Принять имя посетителя и название блюда."""
        parser.add_argument("visitor")
        parser.add_argument("dish")

    def handle(self, *args, **options) -> None:
        """Проверить справочники и сохранить заказ."""
        try:
            visitor = Visitor.objects.get(name=options["visitor"])
            dish = Dish.objects.get(name=options["dish"], available=True)
        except Visitor.DoesNotExist as error:
            raise CommandError("Посетитель не найден.") from error
        except Dish.DoesNotExist as error:
            raise CommandError("Блюдо не найдено или недоступно.") from error

        _, created = Order.objects.update_or_create(
            visitor=visitor, defaults={"dish": dish},
        )
        self.stdout.write("Заказ создан." if created else "Заказ изменён.")
