"""Настройки администрирования посетителей и заказов."""

from django.contrib import admin

from .models import Order, Visitor


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    """Справочник посетителей."""

    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Список заказов с данными посетителей и блюд."""

    list_display = ("id", "visitor", "dish", "meal_date", "status")
    list_select_related = ("visitor", "dish")
    list_filter = ("status", "meal_date", "dish")
    search_fields = ("visitor__name", "dish__name")
    ordering = ("-id",)
    autocomplete_fields = ("visitor", "dish")
