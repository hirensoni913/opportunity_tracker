from django.contrib import admin

from .models import Currency, FundingAgency, Client, Institute, Country, Unit, Staff
from notification.models import NotificationChannel, NotificationSubscription, OpportunitySubscription


class NotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel',
                    'preferred_method', 'is_active')
    list_filter = ('user', 'channel', 'is_active')


class OpportunitySubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'opportunity', 'is_active')
    list_filter = ('user', 'is_active')


class FundingAgencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


admin.site.register([Client,
                    Institute, Country, Unit, Staff, Currency, NotificationChannel])

admin.site.register(NotificationSubscription, NotificationSubscriptionAdmin)
admin.site.register(OpportunitySubscription, OpportunitySubscriptionAdmin)

admin.site.register(FundingAgency, FundingAgencyAdmin)
