from django.shortcuts import render
from django.utils import timezone
from .pdf_processor import PDFProcessor
from tracker.models import Opportunity
from .forms import OpportunityFilterForm
from .models import ReportConfig


def reports(request):
    return render(request, "reports/reports.html")


def get_opportunities(request):
    # Load the report config for 'opportunity' to determine field visibility
    try:
        report_config = ReportConfig.objects.get(slug='opportunity')
        field_config = report_config.config or {}
    except ReportConfig.DoesNotExist:
        field_config = {}

    form = OpportunityFilterForm(request.GET or None)

    # Hide fields that are not visible in the config (where value is False)
    from django import forms
    for field_name, is_visible in field_config.items():
        if not is_visible and field_name in form.fields:
            # Use HiddenInput to hide the field instead of deleting it
            form.fields[field_name].widget = forms.HiddenInput()
            form.fields[field_name].required = False

    context = {'form': form, 'field_config': field_config}

    if form.is_valid():
        opp_type = form.cleaned_data.get("opp_type", None)
        status = form.cleaned_data.get("status", None)
        currency = form.cleaned_data.get("currency", None)
        client = form.cleaned_data.get("client", None)
        funding_agency = form.cleaned_data.get("funding_agency", None)
        lead_unit = form.cleaned_data.get("lead_unit", None)
        lead_institute = form.cleaned_data.get("lead_institute", None)
        proposal_lead = form.cleaned_data.get("proposal_lead", None)
        created_by = form.cleaned_data.get("created_by", None)
        due_date_from = form.cleaned_data.get("due_date_from", None)
        due_date_to = form.cleaned_data.get("due_date_to", None)
        clarification_date_from = form.cleaned_data.get(
            "clarification_date_from", None)
        clarification_date_to = form.cleaned_data.get(
            "clarification_date_to", None)
        intent_bid_date_from = form.cleaned_data.get(
            "intent_bid_date_from", None)
        intent_bid_date_to = form.cleaned_data.get("intent_bid_date_to", None)
        submission_date_from = form.cleaned_data.get(
            "submission_date_from", None)
        submission_date_to = form.cleaned_data.get("submission_date_to", None)
        created_from = form.cleaned_data.get("created_at_from", None)
        created_to = form.cleaned_data.get("created_at_to", None)

        opportunities = Opportunity.objects.all().order_by("-created_at")

        if opp_type:
            opportunities = opportunities.filter(opp_type=opp_type)
        if status:
            opportunities = opportunities.filter(status=status)
        if currency:
            opportunities = opportunities.filter(currency=currency)
        if client:
            opportunities = opportunities.filter(client=client)
        if funding_agency:
            opportunities = opportunities.filter(funding_agency=funding_agency)
        if lead_unit:
            opportunities = opportunities.filter(lead_unit=lead_unit)
        if lead_institute:
            opportunities = opportunities.filter(lead_institute=lead_institute)
        if proposal_lead:
            opportunities = opportunities.filter(proposal_lead=proposal_lead)
        if created_by:
            opportunities = opportunities.filter(created_by=created_by)
        if due_date_from:
            opportunities = opportunities.filter(due_date__gte=due_date_from)
        if due_date_to:
            opportunities = opportunities.filter(due_date__lte=due_date_to)
        if clarification_date_from:
            opportunities = opportunities.filter(
                clarification_date__gte=clarification_date_from)
        if clarification_date_to:
            opportunities = opportunities.filter(
                clarification_date__lte=clarification_date_to)
        if intent_bid_date_from:
            opportunities = opportunities.filter(
                intent_bid_date__gte=intent_bid_date_from)
        if intent_bid_date_to:
            opportunities = opportunities.filter(
                intent_bid_date__lte=intent_bid_date_to)
        if submission_date_from:
            opportunities = opportunities.filter(
                submission_date__gte=submission_date_from)
        if submission_date_to:
            opportunities = opportunities.filter(
                submission_date__lte=submission_date_to)
        if created_from:
            opportunities = opportunities.filter(created_at__gte=created_from)
        if created_to:
            opportunities = opportunities.filter(created_at__lte=created_to)

        # return render(request, "reports/report_templates/opportunities.html", {
        #     "data": opportunities
        # })

        template = "reports/report_templates/opportunities.html"
        response = PDFProcessor.process(
            request, template, opportunities, filename="Opportunities.pdf")
        return response

    return render(request, "reports/opportunities.html", context)
