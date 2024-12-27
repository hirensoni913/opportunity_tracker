import os
import re
from django.conf import settings
from django.utils.timezone import now
from typing import Any
from django.forms import BaseModelForm
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.urls import reverse, reverse_lazy
from django.core. paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.generic import UpdateView, CreateView, DetailView, DeleteView, ListView, TemplateView
from django.contrib.auth.decorators import login_not_required
from django.template.loader import render_to_string
from django.db.models import Count, Sum, Case, When, IntegerField

# from opportunity_tracker.tracker.middleware import is_authenticated
from .serializers import OpportunitySerializer
from .models import Opportunity, OpportunityFile
from .forms import UpdateOpportunityForm, UpdateStatusForm, OpportunityForm, LoginForm, OpportunitySearchForm, SubmitProposalForm, OpportunityDetailForm
from notification.models import OpportunitySubscription
from django.contrib.auth import get_user_model
import zipfile

User = get_user_model()


class OpportunityViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  # Required JWT token
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer


class IndexView(View):
    template_name = "opportunity/home.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class DashboardDataView(TemplateView):
    status_dict = dict(Opportunity.OPP_STATUS)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:

        year_period = now().year

        # Get total opportunities
        totals = self.get_card_numbers(year_period)

        status_overview = self.get_status_overview(year_period)
        status_labels = status_overview["status_labels"]
        status_data = status_overview["status_data"]

        # Opportunities by Funding Agencies
        top_10_agencies = self.get_top_10_funding_agencies(year_period)
        funding_agency_labels = top_10_agencies["funding_agency_labels"]
        agency_dataset = top_10_agencies["agency_dataset"]

        # Opportunities by Lead Unit
        lead_units = self.get_opportunity_by_lead_unit(year_period)
        lead_unit_labels = lead_units["lead_unit_labels"]
        lead_unit_data = lead_units["lead_unit_data"]

        # Opportunities by Lead Institute
        lead_institutes = self.get_opportunity_by_lead_institute(year_period)
        lead_institute_labels = lead_institutes["lead_institute_labels"]
        lead_institute_data = lead_institutes["lead_institute_data"]

        # Opportunities by Proposal Lead
        proposal_lead = self.get_opportunity_by_proposal_lead(year_period)
        proposal_lead_labels = proposal_lead["proposal_lead_labels"]
        proposal_lead_data = proposal_lead["proposal_lead_data"]

        # Top 5 Valued Opportunities
        top5_valued_opportunities = self.get_top5_won_valued_opportunities(
            year_period)
        top5_won_valued_labels = top5_valued_opportunities["top5_won_valued_labels"]
        top5_won_valued_data = top5_valued_opportunities["top5_won_valued_data"]

        # Top 5 Valued Opportunities
        top5_valued_submitted = self.get_top5_valued_submitted(
            year_period)
        top5_valued_submitted_labels = top5_valued_submitted["top5_valued_submitted_labels"]
        top5_valued_submitted_data = top5_valued_submitted["top5_valued_submitted_data"]

        # Top 5 duration Opportunities
        top5_duration_opportunities_won = self.get_top5_duration_opportunities_won(
            year_period)
        top5_duration_won_labels = top5_duration_opportunities_won["top5_duration_won_labels"]
        top5_duration_won_data = top5_duration_opportunities_won["top5_duration_won_data"]

        # Top 5 duration Opportunities
        top5_duration_submitted = self.get_top5_duration_submitted(
            year_period)
        top5_duration_submitted_labels = top5_duration_submitted["top5_duration_submitted_labels"]
        top5_duration_submitted_data = top5_duration_submitted["top5_duration_submitted_data"]

        return JsonResponse({
            "total_opportunities": totals["total_opportunities"],
            "total_submitted_proposal_amount": totals["total_submitted_proposal_amount"],
            "total_won_proposal_amount": totals["total_won_proposal_amount"],
            "status_labels": list(status_labels),
            "status_data": status_data,
            "funding_agency_labels": list(funding_agency_labels),
            "funding_agency_data": agency_dataset,
            "lead_unit_labels": lead_unit_labels,
            "lead_unit_data": lead_unit_data,
            "lead_institute_labels": lead_institute_labels,
            "lead_institute_data": lead_institute_data,
            "proposal_lead_labels": proposal_lead_labels,
            "proposal_lead_data": proposal_lead_data,
            "top5_won_valued_labels": top5_won_valued_labels,
            "top5_won_valued_data": top5_won_valued_data,
            "top5_valued_submitted_labels": top5_valued_submitted_labels,
            "top5_valued_submitted_data": top5_valued_submitted_data,
            "top5_duration_won_labels": top5_duration_won_labels,
            "top5_duration_won_data": top5_duration_won_data,
            "top5_duration_submitted_labels": top5_duration_submitted_labels,
            "top5_duration_submitted_data": top5_duration_submitted_data
        })

    def get_status_overview(self, period):
        # Opportunities by Status
        opportunity_status_count = Opportunity.objects.filter(created_at__year=period).values(
            "status", "opp_type").annotate(count=Count("status")).order_by("status")

        chart_data = {}
        opp_status_labels = set()

        for record in opportunity_status_count:
            opp_type = record["opp_type"]
            status = self.status_dict[record["status"]]
            count = record["count"]

            if status not in chart_data:
                chart_data[status] = {}

            chart_data[status][opp_type] = count
            opp_status_labels.add(opp_type)

        report_labels = list(chart_data.keys())

        # Prepare dataset
        opp_dataset = []
        for opp_type in opp_status_labels:
            dataset = {
                "label": opp_type,
                "data": [
                    chart_data.get(status, {}).get(opp_type, 0)
                    for status in report_labels
                ]
            }
            opp_dataset.append(dataset)

        return {
            "status_labels": report_labels,
            "status_data": opp_dataset
        }

    def get_top_10_funding_agencies(self, period):
        top_10 = Opportunity.objects.filter(created_at__year=period, funding_agency__isnull=False).values(
            "funding_agency").annotate(count=Count("id")).order_by("-count")[:10]

        top_ids = [agency["funding_agency"] for agency in top_10]

        funding_agency_counts = Opportunity.objects.filter(
            created_at__year=period,
            funding_agency__in=top_ids
        ).values("funding_agency__code", "status"
                 ).annotate(
            count=Count("id")
        ).order_by("-count", "status")

        chart_data = {}
        agency_status_labels = set()

        for record in funding_agency_counts:
            agency = record["funding_agency__code"]
            status = self.status_dict[record["status"]]
            count = record["count"]

            if agency not in chart_data:
                chart_data[agency] = {}

            chart_data[agency][status] = count
            agency_status_labels.add(status)

        # Convert to chart.js format
        funding_agency_labels = list(chart_data.keys())

        # Prepare dataset
        agency_dataset = []
        for status in agency_status_labels:
            dataset = {
                "label": status,
                "data": [
                    chart_data.get(agency, {}).get(status, 0)
                    for agency in funding_agency_labels
                ]
            }
            agency_dataset.append(dataset)

        return {
            "funding_agency_labels": funding_agency_labels,
            "agency_dataset": agency_dataset
        }

    def get_opportunity_by_lead_unit(self, period):
        opportunities = Opportunity.objects.filter(created_at__year=period, status__gt=1).values(
            "lead_unit__code").annotate(count=Count("id")).order_by("-count")

        return {
            "lead_unit_labels": [opp["lead_unit__code"] for opp in opportunities],
            "lead_unit_data": [opp["count"] for opp in opportunities]
        }

    def get_opportunity_by_lead_institute(self, period):
        opportunities = Opportunity.objects.filter(created_at__year=period, status__gte=5).values(
            "lead_institute__code").annotate(count=Count("id")).order_by("-count")

        return {
            "lead_institute_labels": [opp["lead_institute__code"] for opp in opportunities],
            "lead_institute_data": [opp["count"] for opp in opportunities]
        }

    def get_opportunity_by_proposal_lead(self, period):
        opportunities = Opportunity.objects.filter(created_at__year=period, status__gte=5).values(
            "proposal_lead__first_name").annotate(count=Count("id")).order_by("-count")

        return {
            "proposal_lead_labels": [opp["proposal_lead__first_name"] for opp in opportunities],
            "proposal_lead_data": [opp["count"] for opp in opportunities]
        }

    def get_top5_won_valued_opportunities(self, period):
        opportunities = Opportunity.objects.filter(
            created_at__year=period, status__exact=7, proposal_amount__gt=0).order_by("-proposal_amount")[:5]

        return {
            "top5_won_valued_labels": [opp.funding_agency.code if opp.funding_agency else "unknown" for opp in opportunities],
            "top5_won_valued_data": [opp.proposal_amount for opp in opportunities]
        }

    def get_top5_valued_submitted(self, period):
        opportunities = Opportunity.objects.filter(
            created_at__year=period, status__exact=5, proposal_amount__gt=0).order_by("-proposal_amount")[:5]

        return {
            "top5_valued_submitted_labels": [opp.funding_agency.code if opp.funding_agency else "unknown" for opp in opportunities],
            "top5_valued_submitted_data": [opp.proposal_amount for opp in opportunities]
        }

    def get_top5_duration_opportunities_won(self, period):
        opportunities = Opportunity.objects.filter(
            created_at__year=period, status__exact=7, duration_months__gt=0).order_by("-duration_months")[:5]

        return {
            "top5_duration_won_labels": [opp.funding_agency.code if opp.funding_agency else "unknown" for opp in opportunities],
            "top5_duration_won_data": [opp.duration_months for opp in opportunities]
        }

    def get_top5_duration_submitted(self, period):
        opportunities = Opportunity.objects.filter(
            created_at__year=period, status__exact=5, duration_months__gt=0).order_by("-duration_months")[:5]

        return {
            "top5_duration_submitted_labels": [opp.funding_agency.code if opp.funding_agency else "unknown" for opp in opportunities],
            "top5_duration_submitted_data": [opp.duration_months for opp in opportunities]
        }

    def get_card_numbers(self, period):
        result = Opportunity.objects.filter(created_at__year=period).aggregate(
            total_opportunities=Count("id"),
            total_submitted_proposal_amount=Sum(
                Case(
                    When(status=5, then="proposal_amount"),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            total_won_proposal_amount=Sum(
                Case(
                    When(status=7, then="proposal_amount"),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )

        return {
            "total_opportunities": result["total_opportunities"],
            "total_submitted_proposal_amount": result["total_submitted_proposal_amount"],
            "total_won_proposal_amount": result["total_won_proposal_amount"]
        }


class OpportunityListView(ListView):
    model = Opportunity
    template_name = "opportunity/list.html"
    paginate_by = 15
    form_class = OpportunitySearchForm

    def get_queryset(self):
        opportunities = Opportunity.objects.all().order_by("-created_at")
        form = OpportunitySearchForm(self.request.GET or None)

        # Apply filter
        if form.is_valid():
            ref_no = form.cleaned_data.get('ref_no', None)
            title = form.cleaned_data.get('title', None)
            funding_agency = form.cleaned_data.get('funding_agency', None)
            client = form.cleaned_data.get('client', None)
            status = form.cleaned_data.get('status', None)
            opp_type = form.cleaned_data.get('opp_type', None)

            if ref_no:
                opportunities = opportunities.filter(ref_no__iexact=ref_no)
            if title:
                opportunities = opportunities.filter(title__icontains=title)
            if funding_agency:
                opportunities = opportunities.filter(
                    funding_agency=funding_agency)
            if client:
                opportunities = opportunities.filter(client=client)
            if status:
                opportunities = opportunities.filter(status=status)
            if opp_type:
                opportunities = opportunities.filter(opp_type=opp_type)

        return opportunities or Opportunity.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET or None)
        context['opportunity_count'] = context['page_obj'].paginator.count

        return context

    def get_template_names(self):
        if self.request.htmx:
            return "opportunity/opportunity_cards.html"
        else:
            return self.template_name


class FileDeleteView(DeleteView):
    model = OpportunityFile
    login_url = "login"

    def get_success_url(self) -> str:
        return reverse_lazy("opportunity", kwargs={"pk": self.object.opportunity.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.get_success_url()


class OpportunityCreateView(CreateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = "opportunity/new.html"
    success_url = reverse_lazy("opportunities")
    login_url = "login"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Handle file upload
        files = self.request.FILES.getlist("files")
        for f in files:
            OpportunityFile.objects.create(opportunity=self.object, file=f)

        return response


class OpportunityUpdateView(UpdateView):
    model = Opportunity
    template_name = "opportunity/update.html"
    form_class = UpdateOpportunityForm
    login_url = "login"
    success_url = reverse_lazy("opportunities")

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        if self.object:
            form.instance.ref_no = self.object.ref_no

        response = super().form_valid(form)

        # handle file upload
        # Handle file upload
        files = self.request.FILES.getlist("files")
        for f in files:
            OpportunityFile.objects.create(opportunity=self.object, file=f)

        return response

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        subscription = OpportunitySubscription.objects.filter(
            user=self.request.user,
            opportunity=self.object,
            is_active=True
        ).first()

        context['form'] = UpdateOpportunityForm(
            instance=self.object, is_subscribed=subscription is not None)
        context['update_status_form'] = UpdateStatusForm(instance=self.object)
        if not self.submit_proposal_form:
            context['submit_proposal_form'] = SubmitProposalForm(
                instance=self.object)
        else:
            context['submit_proposal_form'] = self.submit_proposal_form
        if self.object.status in [1, 3, 4]:
            context['filtered_status'] = [
                (2, "Go"), (3, "NO-Go"), (4, "Consider")]
        elif self.object.status >= 5:
            context['filtered_status'] = [
                (5, "Submitted"), (6, "Lost"), (7, "Won"), (8, "Cancelled"), (9, "Assumed Lost"), (10, "N/A")]

        return context

    def dispatch(self, request, *args, **kwargs):
        # Extract additional kwargs if provided
        self.submit_proposal_form = kwargs.pop(
            'submit_proposal_form', None)
        return super().dispatch(request, *args, **kwargs)


class OpportunityStatusUpdateView(UpdateView):
    model = Opportunity
    form_class = UpdateStatusForm
    template_name = "opportunity/new.html"
    success_url = reverse_lazy("opportunities")

    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors})

        return super().form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = OpportunityForm(instance=self.object)
        context['go_no_go_form'] = UpdateStatusForm(instance=self.object)
        context['submit_proposal_form'] = SubmitProposalForm(
            instance=self.object)

        return context


class OpportunitySubmitView(UpdateView):
    model = Opportunity
    form_class = SubmitProposalForm
    template_name = "opportunity/new.html"
    success_url = reverse_lazy("opportunities")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = OpportunityForm(instance=self.object)
        context['go_no_go_form'] = UpdateStatusForm(instance=self.object)
        context['submit_proposal_form'] = SubmitProposalForm(
            instance=self.object)

        return context

    def form_invalid(self, form):
        # request_copy = HttpRequest()
        # request_copy.__dict__ = self.request.__dict__.copy()
        # request_copy.path = reverse(
        #     "update_opportunity", kwargs={"pk": self.object.id})

        view = OpportunityUpdateView.as_view()
        return view(self.request, pk=self.object.id, submit_proposal_form=form)


class OpportunityDetailView(DetailView):
    model = Opportunity
    template_name = "opportunity/detail.html"
    context_object_name = "opportunity"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        opportunity = self.get_object()
        form = OpportunityDetailForm(instance=opportunity)
        context['form'] = form
        context['partner_names'] = [
            partner.name for partner in opportunity.partners.all()]

        context['files'] = opportunity.Files.all()

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Handle the AJAX call
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            opportunity = self.get_object()
            form = OpportunityDetailForm(instance=opportunity)
            files = opportunity.Files.all()
            html = render_to_string(
                "opportunity/detail.html", {"form": form, "files": files, })
            return JsonResponse({'html': html})

        return super().get(request, *args, **kwargs)


class DownloadFolderView(View):
    def get(self, request, pk):

        # Get the opportunity
        opportunity = Opportunity.objects.filter(id=pk).first()

        if not opportunity:
            return HttpResponse("Opportunity not found", status=404)

        # Get all the files
        files = opportunity.Files.all()

        if not files.exists():
            return HttpResponse("No attachment found", status=404)

        # Create a zip file in memory
        ref_no = foldername = re.sub(r"[^a-zA-Z0-9]", "_", opportunity.ref_no)
        zip_filename = f"{ref_no}.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, "temp", zip_filename)

        # Ensure the temp folder exists
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "temp"), exist_ok=True)

        with zipfile.ZipFile(zip_path, "w") as zip_file:
            for file in files:
                file_path = file.file.path
                # Relative path inside zip
                archname = os.path.relpath(
                    file_path, os.path.join(settings.MEDIA_ROOT, "opportunities", ref_no))
                zip_file.write(file_path, archname)

        # Serve the zip file
        with open(zip_path, "rb") as file:
            response = HttpResponse(
                file.read(), content_type="application/zip")
            response["Content-Disposition"] = f"attachment; filename={
                zip_filename}"

        # Clean up the zip file
        os.remove(zip_path)

        return response
