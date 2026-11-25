"""Удаление действующего заказа через ORM."""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from orders.models import Order


class Command(BaseCommand):
    """Отменить действующий заказ посетителя."""

    help = "Удалить действующий заказ посетителя."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Принять имя посетителя."""
        parser.add_argument("visitor")

    def handle(self, *args, **options) -> None:
        """Удалить заказ, сохранив данные посетителя и блюда."""
        deleted, _ = Order.objects.filter(
            visitor__name=options["visitor"],
        ).delete()
        if not deleted:
            raise CommandError("Действующий заказ не найден.")
        self.stdout.write("Заказ отменён.")
