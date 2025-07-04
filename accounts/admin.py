# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'user_type')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('phone_number', 'user_type')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
