# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Family

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Familie & Rolle', {
            'fields': ('family', 'role', 'avatar')
        }),
    )
    list_display = ('username', 'email', 'family', 'role', 'is_staff')
    list_filter = ('role', 'family', 'is_staff')
    search_fields = ('username', 'email')
