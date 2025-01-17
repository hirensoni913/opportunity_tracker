from django import forms

from accounts.models import User
from tracker.models import Client, FundingAgency, Unit, Institute, Currency


class OpportunityFilterForm(forms.Form):
    OPP_TYPE = [("", "All"), ("EOI", "EOI"),
                ("RFP", "RFP"), ("FC", "Fore-cast")]
    OPP_STATUS = [
        (0, "All"),
        (1, "Entered"),
        (2, "Go"),
        (3, "NO-Go"),
        (4, "Consider"),
        (5, "Submitted"),
        (6, "Lost"),
        (7, "Won"),
        (8, "Cancelled"),
        (9, "Assumed Lost"),
        (10, "N/A"),
    ]
    opp_type = forms.ChoiceField(choices=OPP_TYPE, required=False)
    due_date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    due_date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    clarification_date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    clarification_date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    intent_bid_date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    intent_bid_date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    created_at_from = forms.DateTimeField(
        required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    created_at_to = forms.DateTimeField(
        required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    created_by = forms.ModelChoiceField(
        queryset=User.objects.all(), empty_label="All", required=False)
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), empty_label="All", required=False)
    funding_agency = forms.ModelChoiceField(
        queryset=FundingAgency.objects.all(), empty_label="All", required=False)
    lead_unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(), empty_label="All", required=False)
    lead_institute = forms.ModelChoiceField(
        Institute.objects.all(), empty_label="All", required=False)
    proposal_lead = forms.ModelChoiceField(
        User.objects.all(), empty_label="All", required=False)
    status = forms.ChoiceField(choices=OPP_STATUS, required=False)
    submission_date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    currency = forms.ModelChoiceField(
        Currency.objects.all(), empty_label="All", required=False)

    def __init__(self, *args, **kwargs):
        super(OpportunityFilterForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].queryset = User.objects.all().order_by(
            'first_name', 'last_name')
        self.fields['created_by'].label_from_instance = lambda obj: f"{
            obj.first_name} {obj.last_name}"

        self.fields['proposal_lead'].queryset = User.objects.all().order_by(
            'first_name', 'last_name')
        self.fields['proposal_lead'].label_from_instance = lambda obj: f"{
            obj.first_name} {obj.last_name}"
