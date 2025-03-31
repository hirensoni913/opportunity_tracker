from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as userAdmin
from django.contrib.auth.models import Group
from import_export.admin import ExportMixin, ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm)

from accounts.resources import UserResource

from .models import User


class CustomUserAdmin(ModelAdmin, userAdmin, ImportExportModelAdmin):
    resource_class = UserResource
    import_form_class = ImportForm
    export_form_class = ExportForm

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

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
