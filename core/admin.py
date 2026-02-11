from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import BikeCategory, Bike, Booking, UserProfile


@admin.register(BikeCategory)
class BikeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_hour', 'price_per_day', 'is_available')
    list_filter = ('is_available', 'category')
    search_fields = ('name',)
    list_editable = ('is_available',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'bike', 'start_date', 'end_date', 'total_cost', 'status')
    list_filter = ('status', 'start_date')
    actions = ['mark_as_completed']

    def mark_as_completed(self, request, queryset):
        queryset.update(status='Completed')
    mark_as_completed.short_description = "Mark selected bookings as completed"


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = UserAdmin.list_display + ('get_phone', 'get_address')
    
    def get_phone(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else ''
    get_phone.short_description = 'Phone'
    
    def get_address(self, obj):
        return obj.profile.address if hasattr(obj, 'profile') else ''
    get_address.short_description = 'Address'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
