import os
import re
import zipfile
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_not_required
from django.utils.decorators import method_decorator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django_htmx.http import HttpResponseClientRefresh
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from notification.models import OpportunitySubscription

from .forms import (OpportunityDetailForm, OpportunityDetailAnonymousForm, OpportunityForm,
                    OpportunitySearchForm, SubmitProposalForm,
                    UpdateOpportunityForm, UpdateStatusForm, FundingAgencyForm, ClientForm)
from .models import Opportunity, OpportunityFile

from .serializers import OpportunitySerializer


User = get_user_model()


class OpportunityViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  # Required JWT token
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer


class IndexView(View):
    template_name = "tracker/home.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class OpportunityListView(ListView):
    model = Opportunity
    template_name = "tracker/list.html"
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
            country = form.cleaned_data.get('country', None)

            if ref_no:
                opportunities = opportunities.filter(ref_no__icontains=ref_no)
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
            if country:
                opportunities = opportunities.filter(countries=country)

        return opportunities or Opportunity.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET or None)
        context['opportunity_count'] = context['page_obj'].paginator.count

        return context

    def get_template_names(self):
        if self.request.htmx:
            return "tracker/partials/opportunity_cards.html"
        else:
            return self.template_name


class FileDeleteView(DeleteView):
    model = OpportunityFile
    login_url = "accounts:login"

    def get_success_url(self) -> str:
        return reverse_lazy("opportunity", kwargs={"pk": self.object.opportunity.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse("", status=200)


class OpportunityCreateView(CreateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = "tracker/new.html"
    success_url = reverse_lazy("opportunities")
    login_url = "accounts:login"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Handle file upload
        files = self.request.FILES.getlist("files")
        for f in files:
            OpportunityFile.objects.create(opportunity=self.object, file=f)

        headers = {"HX-Trigger": "refresh_opp_list"}
        if self.request.htmx:
            return HttpResponse(status=204, headers=headers)
        else:
            return response

    def get_template_names(self):
        if self.request.htmx:
            return "tracker/new_modal.html"
        else:
            return self.template_name


class OpportunityUpdateView(UpdateView):
    model = Opportunity
    template_name = "tracker/update.html"
    form_class = UpdateOpportunityForm
    login_url = "accounts:login"
    # success_url = reverse_lazy("opportunities")

    def get_success_url(self):
        # Use reverse, not reverse_lazy here
        base_url = reverse("opportunities")
        query_params = self.request.GET.copy()
        query_params.pop("page", None)  # Optional: remove page param
        if query_params:
            return f"{base_url}?{query_params.urlencode()}"
        return base_url

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

        if self.request.htmx:
            headers = {"HX-Redirect": str(self.get_success_url())}
            return HttpResponse(status=204, headers=headers)

        return response

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        subscription = OpportunitySubscription.objects.filter(
            user=self.request.user,
            opportunity=self.object,
            is_active=True
        ).first()

        if 'form' not in kwargs:
            context['form'] = UpdateOpportunityForm(
                instance=self.object, is_subscribed=subscription is not None)
        else:
            context['form'] = kwargs['form']  # Preserve form with errors

        context['update_status_form'] = UpdateStatusForm(instance=self.object)
        if not self.submit_proposal_form:
            context['submit_proposal_form'] = SubmitProposalForm(
                instance=self.object)
        else:
            context['submit_proposal_form'] = self.submit_proposal_form

        filters = self.request.GET.copy()
        filters.pop('page', None)  # Remove 'page' if present
        context['back_query'] = filters.urlencode()

        return context

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context, status=400)

    def get_template_names(self):
        if self.request.htmx:
            return "tracker/update.html"
        return super().get_template_names()

    def dispatch(self, request, *args, **kwargs):
        # Extract additional kwargs if provided
        self.submit_proposal_form = kwargs.pop(
            'submit_proposal_form', None)
        return super().dispatch(request, *args, **kwargs)


class OpportunityStatusUpdateView(UpdateView):
    model = Opportunity
    form_class = UpdateStatusForm
    template_name = "tracker/partials/update_status_modal.html"
    # success_url = reverse_lazy("opportunities")

    def get_success_url(self):
        # Use reverse, not reverse_lazy here
        base_url = reverse("opportunities")
        query_params = self.request.GET.copy()
        query_params.pop("page", None)  # Optional: remove page param
        if query_params:
            return f"{base_url}?{query_params.urlencode()}"
        return base_url

    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            # return HttpResponseClientRefresh()
            headers = {"HX-Redirect": str(self.get_success_url())}
            return HttpResponse(status=204, headers=headers)

        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.htmx:
            errors = form.errors.as_json()
            print(errors)
            context = self.get_context_data(
                update_status_form=form)  # Pass the form with errors

            headers = {"HX-Trigger": "form_invalid"}
            return self.render_to_response(context, headers=headers)

        return super().form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if 'update_status_form' in kwargs:
            context['update_status_form'] = kwargs["update_status_form"]
        else:
            context['update_status_form'] = UpdateStatusForm(
                instance=self.object)

        if self.object.status in [1, 2, 3, 4]:
            context['filtered_status'] = [
                (2, "Go"), (3, "NO-Go"), (4, "Consider")]
        elif self.object.status >= 5:
            context['filtered_status'] = [
                (5, "Submitted"), (6, "Lost"), (7, "Won"), (8, "Cancelled"), (9, "Assumed Lost"), (10, "N/A")]

        return context

    def get_template_names(self):
        if self.request.htmx:
            return "tracker/partials/update_status_modal.html"
        return super().get_template_names()


class OpportunitySubmitView(UpdateView):
    model = Opportunity
    form_class = SubmitProposalForm
    template_name = "tracker/partials/submit_proposal_modal.html"
    # success_url = reverse_lazy("opportunities")

    def get_success_url(self):
        # Use reverse, not reverse_lazy here
        base_url = reverse("opportunities")
        query_params = self.request.GET.copy()
        query_params.pop("page", None)  # Optional: remove page param
        if query_params:
            return f"{base_url}?{query_params.urlencode()}"
        return base_url

    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            headers = {"HX-Redirect": str(self.get_success_url())}
            return HttpResponse(status=204, headers=headers)

        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if 'submit_proposal_form' in kwargs:
            context["submit_proposal_form"] = kwargs["submit_proposal_form"]
        else:
            context['submit_proposal_form'] = SubmitProposalForm(
                instance=self.object)

        return context

    def form_invalid(self, form):
        view = OpportunityUpdateView.as_view()
        return view(self.request, pk=self.object.id, submit_proposal_form=form)

    def get_template_names(self):
        if self.request.htmx:
            return "tracker/partials/submit_proposal_modal.html"
        return super().get_template_names()


class OpportunityDetailView(DetailView):
    model = Opportunity
    template_name = "tracker/detail_modal.html"
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
                "tracker/detail_modal.html", {"form": form, "files": files, })
            return JsonResponse({'html': html})

        return super().get(request, *args, **kwargs)


@method_decorator(login_not_required, name='dispatch')
class OpportunityDetailAnonymousView(DeleteView):
    model = Opportunity
    form_class = OpportunityDetailAnonymousForm
    template_name = "tracker/detail_anonymous.html"
    context_object_name = "opportunity"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        opportunity = self.get_object()
        form = OpportunityDetailAnonymousForm(instance=opportunity)
        context['form'] = form
        context['partner_names'] = [
            partner.name for partner in opportunity.partners.all()]

        context['files'] = opportunity.Files.all()

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Handle the AJAX call
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            opportunity = self.get_object()
            form = OpportunityDetailAnonymousForm(instance=opportunity)
            files = opportunity.Files.all()
            html = render_to_string(
                "tracker/detail_modal.html", {"form": form, "files": files, })
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


class NewFundingAgencyView(View):
    template_name = "tracker/new_funding_agency.html"
    form_class = FundingAgencyForm
    success_url = reverse_lazy("new_opportunity")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            agency = form.save()
            if request.htmx:
                return JsonResponse(
                    {
                        "id": agency.id,
                        "name": agency.name
                    },
                    status=201
                )

        return render(request, self.template_name, {"form": form})


class NewClientView(View):
    template_name = "tracker/new_client.html"
    form_class = ClientForm
    success_url = reverse_lazy("new_opportunity")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            client = form.save()
            if request.htmx:
                return JsonResponse(
                    {
                        "id": client.id,
                        "name": client.name
                    },
                    status=201
                )

        return render(request, self.template_name, {"form": form})
