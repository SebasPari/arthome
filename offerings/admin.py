from django.contrib import admin
from .models import Offering, Booking


@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'category', 'price_display', 'is_active', 'created_at']
    list_filter = ['category', 'price_type', 'is_active']
    search_fields = ['title', 'artist__full_name', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['offering', 'host', 'status', 'date_wish', 'guests', 'created_at']
    list_filter = ['status']
    search_fields = ['offering__title', 'host__full_name', 'host__email']
    list_editable = ['status']
    ordering = ['-created_at']
