from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as userAdmin


class CustomUserAdmin(userAdmin):
    # Add custom fields to the new user admin page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_superuser', 'groups'),
        }),
    )

    # Add phone_number field to the existing user admin page
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name',
         'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


# admin.site.unregister(CustomUser)
admin.site.register(User, CustomUserAdmin)
