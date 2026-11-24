"""Проверки маршрутов и страниц Django."""

from pathlib import Path

import django
import pytest
from django.test import Client
from django.urls import reverse

from menu import views as menu_views
from orders import views as order_views
from storage import load_data, save_data


@pytest.fixture
def client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> Client:
    """Запустить Django с отдельным JSON для тестовых запросов."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "canteen_web.settings")
    django.setup()
    path = tmp_path / "canteen.json"
    canteen = load_data(path)
    canteen.add_user("Анна")
    canteen.add_order("Анна", "Soup")
    save_data(path, canteen)
    monkeypatch.setattr(menu_views, "DATA_FILE", path)
    monkeypatch.setattr(order_views, "DATA_FILE", path)
    return Client(HTTP_HOST="localhost")


def test_home_navigation(client: Client) -> None:
    """Главная страница содержит ссылки на меню и заказы."""
    response = client.get("/")
    assert response.status_code == 200
    content = response.content.decode()
    assert 'href="/menu/"' in content
    assert 'href="/orders/"' in content


def test_menu_and_dish(client: Client) -> None:
    """Меню ведёт на динамическую страницу блюда с ценой и доступностью."""
    url = reverse("menu:detail", kwargs={"name": "Pizza"})
    menu = client.get("/menu/")
    assert menu.status_code == 200
    assert f'href="{url}"' in menu.content.decode()

    dish = client.get(url)
    assert dish.status_code == 200
    assert "10,99" in dish.content.decode()
    assert "Доступно для заказа" in dish.content.decode()

    unavailable = client.get("/menu/Salad/")
    assert unavailable.status_code == 200
    assert "Недоступно для заказа" in unavailable.content.decode()


def test_orders_use_saved_data(client: Client) -> None:
    """Страница заказов показывает записи и сумму из JSON."""
    response = client.get("/orders/")
    assert response.status_code == 200
    content = response.content.decode()
    assert "Анна" in content
    assert "Soup" in content
    assert "Всего: 2. Общая стоимость: 15,49 $." in content


@pytest.mark.parametrize("url", ["/unknown/", "/menu/unknown/"])
def test_not_found(client: Client, url: str) -> None:
    """Неизвестный путь и неизвестное блюдо возвращают страницу 404."""
    response = client.get(url)
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()
