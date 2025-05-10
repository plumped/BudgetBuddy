# dashboard/admin.py - Erweiterte Admin-Registrierungen
from django.contrib import admin
from .models import (DashboardPreference, QuickAction, DashboardWidget,
                     FavoriteItem, ShortcutKey)

@admin.register(DashboardPreference)
class DashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'default_period', 'show_budget_widget', 'show_savings_widget')
    list_filter = ('theme', 'default_period')
    search_fields = ('user__username',)
    readonly_fields = ('widget_order',)

@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'icon', 'url', 'order', 'is_active', 'use_count')
    list_filter = ('user', 'is_active')
    search_fields = ('name', 'description', 'user__username')
    list_editable = ('order', 'is_active')

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'widget_type', 'title', 'position', 'size', 'is_visible')
    list_filter = ('widget_type', 'size', 'is_visible')
    search_fields = ('user__username', 'title')
    list_editable = ('position', 'is_visible')
    readonly_fields = ('settings',)

@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_type', 'name', 'access_count', 'added_at')
    list_filter = ('item_type', 'user')
    search_fields = ('user__username', 'name')
    readonly_fields = ('added_at', 'access_count')

@admin.register(ShortcutKey)
class ShortcutKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'key_combination', 'is_active')
    list_filter = ('user', 'is_active')
    search_fields = ('user__username', 'action', 'key_combination')
    list_editable = ('is_active',)