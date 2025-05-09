# dashboard/admin.py
from django.contrib import admin
from .models import DashboardPreference

@admin.register(DashboardPreference)
class DashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'show_budget_widget', 'show_savings_widget', 'show_expenses_widget', 'default_period')
    list_filter = ('default_period',)
