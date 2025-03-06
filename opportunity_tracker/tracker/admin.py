from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from notification.models import (NotificationChannel, NotificationSubscription,
                                 OpportunitySubscription)
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)

from .models import (Client, Country, Currency, FundingAgency, Institute,
                     Opportunity, Unit)


@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(ModelAdmin):
    list_display = ('user', 'channel',
                    'preferred_method', 'is_active')
    list_filter = ('user', 'channel', 'is_active')


@admin.register(OpportunitySubscription)
class OpportunitySubscriptionAdmin(ModelAdmin):
    list_display = ('user', 'opportunity', 'is_active')
    list_filter = ('user', 'is_active')


@admin.register(FundingAgency)
class FundingAgencyAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    import_form_class = ImportForm
    export_form_class = ExportForm


@admin.register(Client)
class ClientAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['code', 'name', 'client_type']
    search_fields = ['code', 'name', 'client_type']
    import_form_class = ImportForm
    export_form_class = ExportForm
    pass


@admin.register(Institute)
class InstituteAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    import_form_class = ImportForm
    export_form_class = ExportForm
    pass


@admin.register(Country)
class CountryAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    import_form_class = ImportForm
    export_form_class = ExportForm
    pass


@admin.register(Unit)
class UnitAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    import_form_class = ImportForm
    export_form_class = ExportForm
    pass


# @admin.register(Staff)
# class StaffAdmin(ModelAdmin):
#     pass


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['code', 'currency', 'symbol']
    search_fields = ['code', 'currency']
    import_form_class = ImportForm
    export_form_class = ExportForm
    pass


@admin.register(NotificationChannel)
class NotificationChannelAdmin(ModelAdmin):
    pass


@admin.register(Opportunity)
class NotificationSubscriptionAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    search_fields = ['code', 'title']
