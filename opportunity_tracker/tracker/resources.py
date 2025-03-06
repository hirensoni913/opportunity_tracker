import uuid
from import_export import resources
from .models import Client, FundingAgency, Institute, Unit


class ClientResource(resources.ModelResource):
    def before_import_row(self, row, row_number=None, **kwargs):
        if not row.get("code"):
            raise ValueError("Each client must have a unique 'code'")

        if not Client.objects.filter(code=row["code"]).exists():
            row["id"] = str(uuid.uuid4())

    class Meta:
        model = Client
        import_id_fields = ("code", )
        fields = ("code", "name", "client_type")


class FundingAgencyResource(resources.ModelResource):
    def before_import_row(self, row, row_number=None, **kwargs):
        if not row.get("code"):
            raise ValueError("Each funding agency must have a unique 'code'")

        if not FundingAgency.objects.filter(code=row["code"]).exists():
            row["id"] = str(uuid.uuid4())

    class Meta:
        model = FundingAgency
        import_id_fields = ("code", )
        fields = ("code", "name")


class InstituteResource(resources.ModelResource):
    def before_import_row(self, row, row_number=None, **kwargs):
        if not row.get("code"):
            raise ValueError("Each institute must have a unique 'code'")

        if not Institute.objects.filter(code=row["code"]).exists():
            row["id"] = str(uuid.uuid4())

    class Meta:
        model = Institute
        import_id_fields = ("code", )
        fields = ("code", "name")


class UnitResource(resources.ModelResource):
    def before_import_row(self, row, row_number=None, **kwargs):
        if not row.get("code"):
            raise ValueError("Each unit must have a unique 'code'")

        if not Unit.objects.filter(code=row["code"]).exists():
            row["id"] = str(uuid.uuid4())

    class Meta:
        model = Unit
        import_id_fields = ("code", )
        fields = ("code", "name")
