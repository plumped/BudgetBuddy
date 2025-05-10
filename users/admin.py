# users/admin.py - Erweiterte Admin-Registrierungen
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, Family, PersonalBudget, ExpenseApproval,
                     Account, Notification, NotificationPreference)


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'require_approval_amount', 'child_spending_limit_daily')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Familie & Rolle', {
            'fields': ('family', 'role', 'avatar')
        }),
        ('Persönliche Einstellungen', {
            'fields': ('personal_budget_enabled', 'personal_budget_amount', 'notification_preferences'),
            'classes': ('collapse',)
        }),
    )
    list_display = ('username', 'email', 'family', 'role', 'is_staff')
    list_filter = ('role', 'family', 'is_staff', 'personal_budget_enabled')
    search_fields = ('username', 'email', 'family__name')


@admin.register(PersonalBudget)
class PersonalBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'family_budget', 'allocated_amount', 'available_amount')
    list_filter = ('user', 'family_budget')
    search_fields = ('user__username', 'description')


@admin.register(ExpenseApproval)
class ExpenseApprovalAdmin(admin.ModelAdmin):
    list_display = ('expense', 'requested_by', 'approver', 'status', 'request_date', 'decision_date')
    list_filter = ('status', 'request_date', 'decision_date')
    search_fields = ('expense__description', 'requested_by__username', 'approver__username')
    readonly_fields = ('request_date', 'decision_date')

    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        for approval in queryset.filter(status='pending'):
            approval.approve(request.user, 'Bulk-Genehmigung vom Admin')
        self.message_user(request, f"{queryset.count()} Genehmigungen wurden erteilt.")

    approve_selected.short_description = "Ausgaben genehmigen"

    def reject_selected(self, request, queryset):
        for approval in queryset.filter(status='pending'):
            approval.reject(request.user, 'Bulk-Ablehnung vom Admin')
        self.message_user(request, f"{queryset.count()} Ausgaben wurden abgelehnt.")

    reject_selected.short_description = "Ausgaben ablehnen"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'account_type', 'balance')
    list_filter = ('family', 'account_type')
    search_fields = ('name', 'family__name')
    filter_horizontal = ('owners',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at',)

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} Benachrichtigungen wurden als gelesen markiert.")

    mark_as_read.short_description = "Als gelesen markieren"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} Benachrichtigungen wurden als ungelesen markiert.")

    mark_as_unread.short_description = "Als ungelesen markieren"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_expense_approval', 'email_budget_warning', 'email_saving_reminder',
                    'email_weekly_summary')
    list_filter = ('email_expense_approval', 'email_budget_warning', 'email_saving_reminder', 'email_weekly_summary')
    search_fields = ('user__username',)