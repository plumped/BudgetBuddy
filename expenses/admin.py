# expenses/admin.py
from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'category', 'user', 'family', 'date', 'created_at')
    list_filter = ('family', 'user', 'category', 'date')
    search_fields = ('description',)
