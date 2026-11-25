"""Общие данные для шаблонов."""

from django.http import HttpRequest


def site_info(request: HttpRequest) -> dict[str, str]:
    """Передать общее название сайта."""
    return {"site_name": "Столовая"}
