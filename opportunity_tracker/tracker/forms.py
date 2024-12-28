from typing import Any, Mapping
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Client, Country, FundingAgency, Institute, Opportunity
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
    next = forms.CharField(widget=forms.HiddenInput(), required=False)


class OpportunityForm(forms.ModelForm):
    OPP_STATUS = [
        (2, "Go"),
        (3, "NO-Go"),
        (4, "Consider"),
    ]

    class Meta:
        model = Opportunity
        fields = ['ref_no', 'title', 'funding_agency', 'client', 'opp_type', 'countries',
                  'due_date', 'clarification_date', 'intent_bid_date',  'duration_months', 'notes', 'status']

        widgets = {
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'clarification_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'intent_bid_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'files': forms.ClearableFileInput(),
        }
    status = forms.IntegerField(initial=1, widget=forms.HiddenInput())
    title = forms.CharField(required=True, error_messages={
                            "required": "Title is required"})


class UpdateOpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ['ref_no', 'title', 'funding_agency', 'client', 'opp_type', 'countries',
                  'due_date', 'clarification_date', 'intent_bid_date', 'duration_months', 'notes', 'status']

        widgets = {
            'ref_no': forms.TextInput(attrs={'readonly': 'readonly'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'clarification_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'intent_bid_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'files': forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        is_subscribed = kwargs.pop("is_subscribed", False)
        super().__init__(*args, **kwargs)
        self.fields["is_subscribed"].initial = is_subscribed

    status = forms.IntegerField(initial=1, widget=forms.HiddenInput())
    is_subscribed = forms.BooleanField(
        required=False, label="Subscribe to this Opportunity",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        }))


class UpdateStatusForm(forms.ModelForm):
    OPP_STATUS = [
        (2, "Go"),
        (3, "NO-Go"),
        (4, "Consider"),
        (5, "Submitted"),
        (6, "Lost"),
        (7, "Won"),
    ]

    class Meta:
        model = Opportunity
        fields = ['status', 'lead_unit', 'proposal_lead', 'result_note']

    status = forms.ChoiceField(
        widget=forms.RadioSelect, label="status", choices=OPP_STATUS, required=True, error_messages={'required': 'Select at least one option'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proposal_lead'].queryset = User.objects.all()
        self.fields['proposal_lead'].label_from_instance = lambda obj: f"{obj.first_name} {
            obj.last_name}" if obj.first_name and obj.last_name else obj.username


class SubmitProposalForm(forms.ModelForm):
    submission_date = forms.DateField(required=True,
                                      error_messages={
                                          'required': 'Please provide a submission date'},
                                      widget=forms.DateInput(
                                          attrs={'class': 'form-control', 'type': 'date'})
                                      )
    lead_institute = forms.ModelChoiceField(
        queryset=Institute.objects.all(), required=True, label="Lead Organization", error_messages={'required': 'Select a Lead Organization'})

    partners = forms.ModelMultipleChoiceField(
        queryset=Institute.objects.all(), required=False, label="Partners")

    class Meta:
        model = Opportunity
        fields = ['status', 'lead_institute', 'partners',
                  'submission_date', 'currency', 'proposal_amount', 'net_amount']

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        currency = cleaned_data.get("currency")
        proposal_amount = cleaned_data.get("proposal_amount")
        net_amount = cleaned_data.get("net_amount")

        if (proposal_amount or net_amount) and not currency:
            raise forms.ValidationError({
                'currency': 'Please select a currency.'
            })

        return cleaned_data


class OpportunityDetailForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        exclude = ['updated_at', 'updated_by']


class OpportunitySearchForm(forms.Form):
    ref_no = forms.CharField(required=False, label='Ref#')
    title = forms.CharField(required=False, label='Title')
    funding_agency = forms.ModelChoiceField(
        queryset=FundingAgency.objects.all(), required=False, label="Funding Agency", widget=forms.Select(attrs={'hx-get': '/opportunities/', 'hx-trigger': 'change delay:500ms'}))
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), required=False, label='Client')
    status = forms.ChoiceField(
        choices=[('', '')] + Opportunity.OPP_STATUS, required=False, label="Status")
    opp_type = forms.ChoiceField(
        choices=[('', '')] + Opportunity.OPP_TYPE, required=False, label="Type")

    def __init__(self, *args, **kwargs):
        from django.urls import reverse
        super().__init__(*args, **kwargs)

        # Set the htmx attributes
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'hx-get':  reverse('opportunities'),
                'hx-target': '#opportunity-container',
                'hx-trigger': 'change' if isinstance(self.fields[field_name].widget, forms.Select) else 'keyup changed delay:500ms',
            })
