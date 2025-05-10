# expenses/admin.py - Erweiterte Admin-Registrierungen
from django.contrib import admin
from .models import (Expense, RecurringPattern, ExpenseSplit, ExpenseSplitItem,
                     ExpenseTemplate, ExpenseChangeLog)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'category', 'user', 'family', 'date', 'status', 'expense_type')
    list_filter = ('family', 'user', 'category', 'date', 'status', 'expense_type')
    search_fields = ('description', 'user__username', 'family__name')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Allgemeine Informationen', {
            'fields': ('family', 'user', 'category', 'amount', 'description', 'date')
        }),
        ('Ausgaben-Typ', {
            'fields': ('status', 'expense_type', 'recurring_pattern', 'split_group')
        }),
        ('Beleg', {
            'fields': ('receipt_image',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_expenses', 'categorize_expenses', 'split_expenses']

    def approve_expenses(self, request, queryset):
        count = queryset.update(status='confirmed')
        self.message_user(request, f"{count} Ausgaben wurden genehmigt.")

    approve_expenses.short_description = "Ausgaben genehmigen"

    def categorize_expenses(self, request, queryset):
        # Implementierung für Batch-Kategorisierung
        pass

    categorize_expenses.short_description = "Ausgaben kategorisieren"


@admin.register(RecurringPattern)
class RecurringPatternAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'interval', 'end_date', 'max_occurrences', 'created_at')
    list_filter = ('frequency', 'created_at')


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('description', 'created_by', 'total_amount', 'created_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('description',)


@admin.register(ExpenseSplitItem)
class ExpenseSplitItemAdmin(admin.ModelAdmin):
    list_display = ('split_group', 'user', 'amount', 'paid_by', 'is_paid')
    list_filter = ('is_paid', 'user')


@admin.register(ExpenseTemplate)
class ExpenseTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'user', 'category', 'default_amount', 'use_count')
    list_filter = ('family', 'user', 'category')
    search_fields = ('name', 'description_template')


@admin.register(ExpenseChangeLog)
class ExpenseChangeLogAdmin(admin.ModelAdmin):
    list_display = ('expense', 'user', 'field_name', 'changed_at')
    list_filter = ('user', 'field_name', 'changed_at')
    search_fields = ('expense__description', 'user__username')
    readonly_fields = ('changed_at',)