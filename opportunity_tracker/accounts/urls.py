# filepath: c:\Projects\Opportunity Tracker\opportunity_tracker\accounts\urls.py
from django.urls import path
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .views import CustomPasswordResetView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path('logout/', LogoutView.as_view(next_page="accounts:login"), name="logout"),
    # Password reset URLs
    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/emails/password_reset_email.html',
        html_email_template_name='accounts/emails/password_reset_email.html',
        success_url='/accounts/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
