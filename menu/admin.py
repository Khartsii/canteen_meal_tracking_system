"""Настройки администрирования меню."""

from django.contrib import admin

from .models import Dish, DishUnavailability


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    """Справочник блюд в админке."""

    list_display = ("name", "price", "available", "daily_portions", "slug")
    list_filter = ("available",)
    search_fields = ("name", "description")
    ordering = ("name",)
    readonly_fields = ("slug",)


@admin.register(DishUnavailability)
class DishUnavailabilityAdmin(admin.ModelAdmin):
    """Календарные исключения в админке."""

    list_display = ("dish", "unavailable_date")
    list_select_related = ("dish",)
    list_filter = ("unavailable_date",)
    search_fields = ("dish__name",)
    ordering = ("-unavailable_date", "dish__name")
