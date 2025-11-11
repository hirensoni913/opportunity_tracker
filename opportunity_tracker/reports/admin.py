from unfold.admin import ModelAdmin
from django.contrib import admin, messages
from .models import ReportConfig
from .registry import REPORTS

# Register your models here.


@admin.register(ReportConfig)
class ReportConfigAdmin(ModelAdmin):
    list_display = ("name", "slug", "hidden_summary", "updated_at")
    search_fields = ("name", "slug")

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
                request, f"Created report config for: {', '.join(created_slugs)}")

        # Use Django's default changelist view with Unfold styling
        return super().changelist_view(request, extra_context)
