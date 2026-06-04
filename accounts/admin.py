from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ArtistProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'full_name']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('ArtHome', {'fields': ('full_name', 'role')}),
    )


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'discipline', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['user__email', 'user__full_name', 'discipline']
