from django.contrib import admin
from .models import (Category, Budget, BudgetCategory, BudgetTemplate,
                     BudgetTemplateCategory)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('family', 'month', 'budget_type', 'total_amount', 'status', 'is_active')
    list_filter = ('family', 'budget_type', 'is_active', 'frequency')
    search_fields = ('family__name',)
    readonly_fields = ('carryover_to_next',)

    fieldsets = (
        ('Allgemeine Informationen', {
            'fields': ('family', 'month', 'budget_type', 'end_date', 'frequency', 'is_active')
        }),
        ('Budget-Übertragung', {
            'fields': ('carryover_from_previous', 'carryover_to_next'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'copied_from'),
            'classes': ('collapse',)
        }),
    )

    actions = ['copy_budgets', 'activate_budgets', 'deactivate_budgets']

    def copy_budgets(self, request, queryset):
        for budget in queryset:
            budget.copy_to_next_period()
        self.message_user(request, f"{queryset.count()} Budgets wurden kopiert.")

    copy_budgets.short_description = "Budgets ins nächste Zeitraum kopieren"

    def activate_budgets(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} Budgets wurden aktiviert.")

    activate_budgets.short_description = "Budgets aktivieren"

    def deactivate_budgets(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} Budgets wurden deaktiviert.")

    deactivate_budgets.short_description = "Budgets deaktivieren"


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('budget', 'category', 'amount', 'is_flexible')
    list_filter = ('budget', 'category', 'is_flexible')
    search_fields = ('budget__family__name', 'category__name')


@admin.register(BudgetTemplate)
class BudgetTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'created_at')
    list_filter = ('family', 'created_at')
    search_fields = ('name', 'description', 'family__name')


@admin.register(BudgetTemplateCategory)
class BudgetTemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('template', 'category', 'default_amount')
    list_filter = ('template', 'category')