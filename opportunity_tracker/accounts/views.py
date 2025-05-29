from django.shortcuts import render
from django.contrib.auth.views import PasswordResetView
from .forms import CustomPasswordResetForm


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view that uses notification module to send emails"""
    form_class = CustomPasswordResetForm
