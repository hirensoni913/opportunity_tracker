from django.http import HttpResponse
from django.shortcuts import render

from tracker.models import Opportunity
from .forms import OpportunityFilterForm


def reports(request):
    return render(request, "reports/reports.html")


def get_opportunities(request):
    form = OpportunityFilterForm(request.GET or None)
    context = {'form': form}

    if form.is_valid():
        opp_type = form.cleaned_data.get("opp_type", None)
        opp_status = form.cleaned_data.get("opp_status", None)
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
        if opp_status:
            opportunities = opportunities.filter(opp_status=opp_status)
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

        # TODO: Create pdf from the filtered opportunities

    return render(request, "reports/opportunities.html", context)
