# savings/admin.py
from django.contrib import admin
from .models import SavingGoal, SavingTransaction

@admin.register(SavingGoal)
class SavingGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'family', 'creator', 'target_amount', 'current_amount', 'target_date', 'created_at')
    list_filter = ('family', 'creator')
    search_fields = ('title', 'description')

@admin.register(SavingTransaction)
class SavingTransactionAdmin(admin.ModelAdmin):
    list_display = ('goal', 'user', 'amount', 'transaction_type', 'date', 'created_at')
    list_filter = ('transaction_type', 'date', 'user')
    search_fields = ('goal__title', 'note')
