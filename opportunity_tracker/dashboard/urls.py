from django.urls import path
from dashboard.views import DashboardDataView

app_name = 'dashboard'

urlpatterns = [
    path("dashboard/chart/data/",
         DashboardDataView.as_view(), name="dashboard_data")
]
