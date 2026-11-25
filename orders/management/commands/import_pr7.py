"""Перенос исходной SQLite ПР7 в таблицы Django."""

import sqlite3
from argparse import ArgumentParser
from contextlib import closing
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from db.database import DB_PATH
from menu.models import Dish, DishUnavailability
from orders.models import Order, Visitor


class Command(BaseCommand):
    """Перенести данные ПР7 в пустую базу Django."""

    help = "Импорт посетителей, блюд, заказов и дат из базы ПР7."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Принять путь к исходной базе."""
        parser.add_argument("--source", type=Path, default=DB_PATH)

    def handle(self, *args, **options) -> None:
        """Скопировать записи с исходными идентификаторами."""
        source = options["source"].resolve()
        if not source.is_file():
            raise CommandError("Сначала создайте базу ПР7 из JSON.")

        try:
            with closing(sqlite3.connect(
                source.as_uri() + "?mode=ro", uri=True,
            )) as legacy, transaction.atomic():
                legacy.row_factory = sqlite3.Row
                legacy.execute("BEGIN")
                if (
                    Visitor.objects.exists()
                    or Dish.objects.exists()
                    or Order.objects.exists()
                    or DishUnavailability.objects.exists()
                ):
                    raise CommandError(
                        "В базе Django уже есть данные. Импорт пропущен.",
                    )

                visitors = Visitor.objects.bulk_create([
                    Visitor(id=row["id"], name=row["name"])
                    for row in legacy.execute("SELECT id, name FROM visitors")
                ])
                dishes = [
                    Dish.objects.create(
                        id=row["id"],
                        name=row["name"],
                        price=row["price"],
                        available=bool(row["available"]),
                    )
                    for row in legacy.execute("SELECT * FROM dishes")
                ]
                orders = Order.objects.bulk_create([
                    Order(
                        id=row["id"],
                        visitor_id=row["visitor_id"],
                        dish_id=row["dish_id"],
                    )
                    for row in legacy.execute("SELECT * FROM orders")
                ])
                dates = DishUnavailability.objects.bulk_create([
                    DishUnavailability(
                        dish_id=row["dish_id"],
                        unavailable_date=date.fromisoformat(
                            row["unavailable_date"],
                        ),
                    )
                    for row in legacy.execute(
                        "SELECT * FROM dish_unavailability",
                    )
                ])
        except (sqlite3.Error, IntegrityError, ValueError) as error:
            raise CommandError(f"Ошибка переноса данных: {error}") from error

        self.stdout.write(
            f"Перенесено: посетителей {len(visitors)}, блюд {len(dishes)}, "
            f"заказов {len(orders)}, исключений по датам {len(dates)}.",
        )
