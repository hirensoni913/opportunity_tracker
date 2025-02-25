from django.urls import path
from .views import reports, get_opportunities

app_name = "reports"
urlpatterns = [
    path("", reports, name="home"),
    path("opportunities/", get_opportunities, name="opportunities_report"),
]
