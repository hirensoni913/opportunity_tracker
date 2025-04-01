from django.forms.widgets import Select
from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.urls import reverse, reverse_lazy
from .models import Client, Country, FundingAgency, Institute, Opportunity, FundingAgency, Client
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class FundingAgencyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.display_label


class ClientChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.display_label


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
    funding_agency = FundingAgencyChoiceField(
        queryset=FundingAgency.objects.all())
    client = ClientChoiceField(
        queryset=Client.objects.all())

    class Meta:
        model = Opportunity
        fields = ['ref_no', 'title', 'funding_agency', 'client', 'opp_type', 'countries',
                  'due_date', 'clarification_date', 'intent_bid_date',  'duration_months', 'notes', 'status', 'currency', 'proposal_amount']

        widgets = {
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'clarification_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'intent_bid_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'files': forms.ClearableFileInput(),
            'funding_agency': forms.Select(attrs={'data-entity': 'funding_agency'}),
            'client': forms.Select(attrs={'data-entity': 'client'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['funding_agency'].widget.attrs.update({
            'data-url': reverse_lazy('new_funding_agency')
        })

        self.fields['client'].widget.attrs.update({
            'data-url': reverse_lazy('new_client')
        })

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        currency = cleaned_data.get("currency")
        proposal_amount = cleaned_data.get("proposal_amount")
        if (proposal_amount) and not currency:
            raise forms.ValidationError({
                'currency': 'Please select a currency.'
            })

        return cleaned_data

    status = forms.IntegerField(initial=1, widget=forms.HiddenInput())
    title = forms.CharField(required=True, error_messages={
                            "required": "Title is required"})


class UpdateOpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ['ref_no', 'title', 'funding_agency', 'client', 'opp_type', 'countries',
                  'due_date', 'clarification_date', 'intent_bid_date', 'duration_months', 'notes', 'status', 'currency', 'proposal_amount']

        widgets = {
            'ref_no': forms.TextInput(attrs={'readonly': 'readonly'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'clarification_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'intent_bid_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'files': forms.ClearableFileInput(),
        }

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        currency = cleaned_data.get("currency")
        proposal_amount = cleaned_data.get("proposal_amount")
        if (proposal_amount) and not currency:
            raise forms.ValidationError({
                'currency': 'Please select a currency.'
            })

        return cleaned_data

    title = forms.CharField(required=True, error_messages={
                            "required": "Title is required"})

    def __init__(self, *args, **kwargs):
        from django.urls import reverse
        is_subscribed = kwargs.pop("is_subscribed", False)
        super().__init__(*args, **kwargs)
        self.fields["is_subscribed"].initial = is_subscribed
        if self.instance.pk:
            toggle_url = reverse('notification:toggle_subscription', kwargs={
                                 'opportunity_id': self.instance.pk})
            self.fields["is_subscribed"].widget.attrs.update({
                'hx-post': toggle_url,
                'hx-trigger': 'change',
                'hx-target': 'this',
                'hx-swap': 'none',
                'data-bs-toast-target': '#successToast',
            })

    status = forms.IntegerField(initial=1, widget=forms.HiddenInput())
    is_subscribed = forms.BooleanField(
        required=False, label="Subscribe to this Opportunity",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch',
        }))


class UpdateStatusForm(forms.ModelForm):
    OPP_STATUS = [
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

    def clean(self):
        cleaned_data = super().clean()
        status = int(cleaned_data.get("status", 0))

        # make proposal_lead and lead_unit mandatory if the status is Go
        if status == 2:
            if not cleaned_data.get("proposal_lead"):
                self.add_error("proposal_lead", "Proposal Lead is required")
            if not cleaned_data.get("lead_unit"):
                self.add_error("lead_unit", "Lead Unit is required")

        return cleaned_data


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
                  'submission_date']


class OpportunityDetailForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        exclude = ['updated_at', 'updated_by']


class OpportunityDetailAnonymousForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        exclude = ['status', 'updated_at', 'updated_by']


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


class FundingAgencyForm(forms.ModelForm):
    class Meta:
        model = FundingAgency
        fields = ["code", "name"]


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["code", "name", "client_type"]
