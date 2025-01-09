from django.http import HttpResponse
from django.shortcuts import render


def reports(request):
    return render(request, "reports/reports.html")
