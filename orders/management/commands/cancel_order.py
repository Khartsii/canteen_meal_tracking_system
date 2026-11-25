"""Отмена действующего заказа через ORM."""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from orders.models import Order


class Command(BaseCommand):
    """Отменить действующий заказ посетителя."""

    help = "Отменить действующий заказ посетителя."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Принять имя посетителя."""
        parser.add_argument("visitor")

    def handle(self, *args, **options) -> None:
        """Перевести заказ в отменённые, сохранив его историю."""
        updated = Order.objects.active().filter(
            visitor__name=options["visitor"],
        ).update(status=Order.Status.CANCELLED)
        if not updated:
            raise CommandError("Действующий заказ не найден.")
        self.stdout.write("Заказ отменён.")
