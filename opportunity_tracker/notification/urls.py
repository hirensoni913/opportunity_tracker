from django.urls import path
from .views import ToggleSubscriptionView, get_subscribers

app_name = 'notification'

urlpatterns = [
    path('toggle-subscription/<uuid:opportunity_id>',
         ToggleSubscriptionView.as_view(), name='toggle_subscription'),
    path('opportunity/<uuid:opp_id>/subscribers',
         get_subscribers, name='get_opportunity_subscribers'),
]
