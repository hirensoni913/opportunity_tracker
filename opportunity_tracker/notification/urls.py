from django.urls import path
from .views import ToggleSubscriptionView

app_name = 'notification'

urlpatterns = [
    path('toggle-subscription/<uuid:opportunity_id>',
         ToggleSubscriptionView.as_view(), name='toggle_subscription')
]
