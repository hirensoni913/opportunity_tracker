from django.contrib import admin
from unfold.admin import ModelAdmin

from notification.models import (NotificationChannel, NotificationSubscription,
                                 OpportunitySubscription)

from .models import (Client, Country, Currency, FundingAgency, Institute,
                     Staff, Unit)


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
class FundingAgencyAdmin(ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ['code', 'name', 'client_type']
    search_fields = ['code', 'name', 'client_type']
    pass


@admin.register(Institute)
class InstituteAdmin(ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    pass


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    pass


@admin.register(Unit)
class UnitAdmin(ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    pass


@admin.register(Staff)
class StaffAdmin(ModelAdmin):
    pass


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ['code', 'currency', 'symbol']
    search_fields = ['code', 'currency']
    pass


@admin.register(NotificationChannel)
class NotificationChannelAdmin(ModelAdmin):
    pass
