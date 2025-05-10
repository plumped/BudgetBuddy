# savings/admin.py - Erweiterte Admin-Registrierungen
from django.contrib import admin
from .models import (SavingGoal, SavingTransaction, SavingCategory,
                     SavingMilestone, SavingChallenge, ChallengeParticipant)


@admin.register(SavingCategory)
class SavingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name', 'description')


@admin.register(SavingGoal)
class SavingGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'family', 'creator', 'target_amount', 'current_amount',
                    'progress_percentage', 'target_date', 'priority')
    list_filter = ('family', 'creator', 'priority', 'auto_save_enabled')
    search_fields = ('title', 'description')
    readonly_fields = ('progress_percentage',)

    fieldsets = (
        ('Allgemeine Informationen', {
            'fields': ('family', 'creator', 'title', 'description', 'category', 'priority')
        }),
        ('Spar-Ziele', {
            'fields': ('target_amount', 'current_amount', 'target_date', 'image')
        }),
        ('Automatisches Sparen', {
            'fields': ('auto_save_enabled', 'auto_save_percentage', 'auto_save_fixed_amount', 'linked_budget'),
            'classes': ('collapse',)
        }),
    )

    actions = ['enable_auto_save', 'disable_auto_save', 'add_milestone']

    def enable_auto_save(self, request, queryset):
        queryset.update(auto_save_enabled=True)
        self.message_user(request, f"Automatisches Sparen für {queryset.count()} Ziele aktiviert.")

    enable_auto_save.short_description = "Automatisches Sparen aktivieren"

    def disable_auto_save(self, request, queryset):
        queryset.update(auto_save_enabled=False)
        self.message_user(request, f"Automatisches Sparen für {queryset.count()} Ziele deaktiviert.")

    disable_auto_save.short_description = "Automatisches Sparen deaktivieren"


@admin.register(SavingMilestone)
class SavingMilestoneAdmin(admin.ModelAdmin):
    list_display = ('goal', 'title', 'target_percentage', 'target_amount', 'achieved', 'achieved_at')
    list_filter = ('achieved', 'goal')
    search_fields = ('title', 'goal__title')
    readonly_fields = ('achieved_at',)


@admin.register(SavingChallenge)
class SavingChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'family', 'start_date', 'end_date', 'target_amount', 'current_amount')
    list_filter = ('family', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('participants',)


@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'user', 'personal_target', 'amount_saved', 'joined_at')
    list_filter = ('challenge', 'user')