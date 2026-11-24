"""Проверки сценариев консольной программы."""

import sys
from pathlib import Path

import pytest

import main
from storage import load_data


def test_menu(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Меню выполняет все действия и сохраняет изменения."""
    path = tmp_path / "canteen.json"
    monkeypatch.setattr(main, "DATA_FILE", path)
    monkeypatch.setattr(sys, "argv", ["main.py"])
    answers = iter([
        "?", "1", "Анна", "2", "3", "Alice", "4", "Анна", "Soup",
        "6", "ан", "7", "5", "Анна", "0",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert main.main() == 0
    output = capsys.readouterr().out
    assert "Выберите пункт меню" in output
    assert "Salad недоступно" in output
    assert "Заказ посетителя Alice: Pizza" in output
    assert "Заказ оформлен." in output
    assert "\nАнна\n" in output
    assert "Количество заказов: 2. Стоимость: $15.49." in output
    assert "Заказ отменён." in output
    canteen = load_data(path)
    assert "Анна" in canteen.visitors
    assert list(canteen.orders) == ["Alice"]
    assert canteen.orders["Alice"].dish.name == "Pizza"


def test_demo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Сценарий ПР №1 добавляет посетителя и показывает пиццу и заказ."""
    path = tmp_path / "canteen.json"
    monkeypatch.setattr(main, "DATA_FILE", path)
    monkeypatch.setattr(sys, "argv", ["main.py", "--demo"])
    monkeypatch.setattr("builtins.input", lambda _: "Анна")

    assert main.main() == 0
    output = capsys.readouterr().out
    assert "Pizza доступно для заказа. Цена: $10.99." in output
    assert "Заказ посетителя Alice: Pizza" in output
    assert "Анна" in load_data(path).visitors


def test_failed_save_keeps_current_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ошибка записи не добавляет посетителя в текущее состояние."""
    path = tmp_path / "missing" / "canteen.json"
    canteen = load_data(path)
    monkeypatch.setattr("builtins.input", lambda _: "Анна")

    with pytest.raises(OSError):
        main.run_action("1", canteen, path)

    assert "Анна" not in canteen.visitors
    assert not path.exists()
