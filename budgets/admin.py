# budgets/admin.py
from django.contrib import admin
from .models import Category, Budget, BudgetCategory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('family', 'month', 'is_active', 'created_at')
    list_filter = ('family', 'month', 'is_active')
    search_fields = ('family__name',)

@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('budget', 'category', 'amount')
    list_filter = ('budget', 'category')
