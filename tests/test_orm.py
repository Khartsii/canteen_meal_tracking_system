"""Проверки переноса данных, связей и операций ORM."""

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from db.import_json import import_data
from menu.models import Dish, DishUnavailability
from orders.models import Order, Visitor
from storage import STARTER_FILE

pytestmark = pytest.mark.django_db


def test_import_preserves_ids_and_relations(tmp_path: Path) -> None:
    """Импорт переносит ключи, обратные связи и исключения по датам."""
    legacy_path = tmp_path / "pr7.sqlite3"
    import_data(STARTER_FILE, legacy_path)
    with closing(sqlite3.connect(legacy_path)) as legacy, legacy:
        legacy.execute("UPDATE orders SET id = 42")
        legacy.execute(
            "INSERT INTO dish_unavailability (dish_id, unavailable_date) "
            "SELECT id, '2026-12-01' FROM dishes WHERE name = 'Pizza'",
        )
    call_command("import_pr7", source=legacy_path)

    assert Visitor.objects.count() == 5
    assert Dish.objects.count() == 3
    order = Order.objects.get(pk=42)
    assert order.visitor.name == "Alice"
    assert order.visitor.order == order
    assert order.dish.orders.get() == order
    exception = order.dish.unavailability.get()
    assert exception.unavailable_date == date(2026, 12, 1)
    with pytest.raises(CommandError, match="уже есть данные"):
        call_command("import_pr7", source=legacy_path)
    assert Order.objects.count() == 1


def test_order_management_commands() -> None:
    """Команды создают, меняют и удаляют заказ через ORM."""
    visitor = Visitor.objects.create(name="Анна")
    pizza = Dish.objects.create(name="Pizza", price=10)
    soup = Dish.objects.create(name="Soup", price=5)
    Dish.objects.create(name="Salad", price=2, available=False)

    call_command("set_order", "Анна", "Pizza")
    order = Order.objects.get(visitor=visitor)
    assert order.dish == pizza
    with pytest.raises(CommandError, match="недоступно"):
        call_command("set_order", "Анна", "Salad")
    call_command("set_order", "Анна", "Soup")
    order.refresh_from_db()
    assert order.dish == soup
    with pytest.raises(ProtectedError):
        soup.delete()

    call_command("cancel_order", "Анна")
    assert not Order.objects.filter(visitor=visitor).exists()
    assert Visitor.objects.filter(pk=visitor.pk).exists()


def test_constraints() -> None:
    """База отклоняет повторный заказ, повтор даты и отрицательную цену."""
    visitor = Visitor.objects.create(name="Анна")
    dish = Dish.objects.create(name="Soup", price=5)
    day = date(2026, 12, 1)
    Order.objects.create(visitor=visitor, dish=dish)
    DishUnavailability.objects.create(dish=dish, unavailable_date=day)

    with pytest.raises(IntegrityError), transaction.atomic():
        Order.objects.create(visitor=visitor, dish=dish)
    with pytest.raises(IntegrityError), transaction.atomic():
        DishUnavailability.objects.create(dish=dish, unavailable_date=day)
    with pytest.raises(IntegrityError), transaction.atomic():
        Dish.objects.create(name="Invalid", price=-1)
