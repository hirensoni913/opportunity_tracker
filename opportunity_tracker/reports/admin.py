from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldBooleanSwitchWidget
from django.contrib import admin, messages
from django import forms
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from .models import ReportConfig
from .registry import REPORTS
import copy
import logging

logger = logging.getLogger(__name__)

CFG_PREFIX = "cfg__"


class LabeledSwitchWidget(UnfoldBooleanSwitchWidget):
    """Custom widget that renders label on left and switch on right"""

    def __init__(self, label_text='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_text = label_text

    def render(self, name, value, attrs=None, renderer=None):
        # Get the switch HTML from parent
        switch_html = super().render(name, value, attrs, renderer)

        # Wrap in a flex container with label on left and switch on right
        # Using negative margin to reduce space between rows added by form field wrappers
        html = f'''
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 0.5rem 1rem; background-color: rgba(0, 0, 0, 0.02); border-radius: 0.375rem; margin: -0.5rem 0 -0.5rem 0;">
            <span style="font-weight: 500; flex: 1;">{self.label_text}</span>
            <div style="flex: 0 0 auto;">{switch_html}</div>
        </div>
        '''
        return mark_safe(html)


class ReportConfigAdminForm(forms.ModelForm):
    class Meta:
        model = ReportConfig
        # leave fields as default except updated_by (we exclude explicitly)
        exclude = ("updated_by",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide the raw config JSON field from the UI
        if "config" in self.fields:
            self.fields["config"].widget = forms.HiddenInput()

        # Determine instance / slug
        instance = kwargs.get("instance")
        report_slug = getattr(
            instance, "slug", None) if instance else self.initial.get("slug")

        if not report_slug:
            return

        entry = REPORTS.get(report_slug)
        if not entry or not entry.get("form_class"):
            return

        # import the report's form class
        try:
            FormClass = import_string(entry["form_class"])
        except Exception:
            # failing to import should silently skip injecting fields
            return

        # instantiate the report form to inspect fields
        try:
            report_form = FormClass()
        except Exception:
            return

        # load existing config (guard with isinstance)
        existing_config = {}
        if instance and getattr(instance, "config", None) and isinstance(instance.config, dict):
            existing_config = copy.deepcopy(instance.config)

        # Inject switch fields for visibility with custom widget
        for name, field in report_form.fields.items():
            checkbox_name = f"{CFG_PREFIX}{name}"
            label = getattr(field, "label", None) or name.replace(
                "_", " ").capitalize()

            self.fields[checkbox_name] = forms.BooleanField(
                required=False,
                label='',  # Empty label since we're rendering it in the widget
                initial=bool(existing_config.get(name, True)),
                widget=LabeledSwitchWidget(label_text=label),
            )

    def clean(self):
        cleaned = super().clean()

        # Collect injected config values into a dict and store on cleaned_data["config"]
        config_data = {}
        for fname, form_field in list(self.fields.items()):
            if fname.startswith(CFG_PREFIX):
                real_name = fname[len(CFG_PREFIX):]
                # Use cleaned.get(..., False) fallback, but respect field.initial if not present
                value = cleaned.get(fname, form_field.initial)
                config_data[real_name] = bool(value)

        cleaned["config"] = config_data
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.config = self.cleaned_data.get("config", {}) or {}

        if commit:
            instance.save()
        return instance


@admin.register(ReportConfig)
class ReportConfigAdmin(ModelAdmin):
    form = ReportConfigAdminForm

    list_display = ("name", "slug", "hidden_summary",
                    "updated_by", "updated_at")
    search_fields = ("name", "slug")

    def has_add_permission(self, request):
        """Disable the ability to add new records"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable the ability to delete records"""
        return False

    def get_form(self, request, obj=None, **kwargs):
        """
        Override get_form to prevent validation of dynamic cfg__ fields
        """
        # Don't pass fields to the parent get_form to avoid validation
        # The form itself will handle adding the dynamic fields
        kwargs['fields'] = None
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically generate fieldsets including cfg__ prefixed fields
        Using fieldsets for better layout control in Unfold
        """
        # Base fields
        base_fieldset = (None, {
            'fields': ['name', 'slug']
        })

        # Collect dynamic cfg__ fields if we have an object
        cfg_fields = []
        if obj and obj.slug:
            entry = REPORTS.get(obj.slug)
            if entry and entry.get("form_class"):
                try:
                    FormClass = import_string(entry["form_class"])
                    report_form = FormClass()
                    # Add all cfg__ prefixed field names
                    cfg_fields = [
                        f"{CFG_PREFIX}{name}" for name in report_form.fields.keys()]
                except Exception as e:
                    logger.warning(
                        f"Could not load form class for {obj.slug}: {e}")

        # Build fieldsets
        fieldsets = [base_fieldset]

        if cfg_fields:
            # Use Unfold's classes parameter for better styling
            fieldsets.append(
                ('Field Visibility Configuration', {
                    'fields': cfg_fields,
                    'classes': ('tab',),
                    'description': 'Toggle switches to show/hide fields in the report.'
                })
            )

        return fieldsets

    def changelist_view(self, request, extra_context=None):
        # Create report configs if they don't exist
        created_slugs = []
        for slug, meta in REPORTS.items():
            rc, created = ReportConfig.objects.get_or_create(
                slug=slug,
                defaults={"name": meta.get("name", slug), "config": {}}
            )
            if created:
                created_slugs.append(slug)

        if created_slugs:
            messages.info(
                request, f"Created report config for: {', '.join(created_slugs)}"
            )

        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        # set the modifier and save
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        """Redirect after add - removes 'Save and add another' option"""
        return super().response_change(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Customize the change view to remove 'Save and add another' button"""
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)
