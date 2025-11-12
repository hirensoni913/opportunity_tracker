from django.db import models
from django.conf import settings


class ReportConfig(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    config = models.JSONField(default=dict, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="updated_report_configs")

    class Meta:
        ordering = ("name", )
        verbose_name = "Report configuration"
        verbose_name_plural = "Report configurations"

    def __str__(self):
        return f"{self.name}"

    def hidden_summary(self):
        cfg = self.config or {}
        total = len(cfg) if isinstance(cfg, dict) else 0
        hidden = sum(1 for v in cfg.values() if v is False)
        return f"{hidden} hidden / {total}"
