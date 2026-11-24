"""Точка входа для команд Django."""

import os
import sys

from django.core.management import execute_from_command_line


def main() -> None:
    """Выполнить команду Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canteen_web.settings")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
