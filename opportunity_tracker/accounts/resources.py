from import_export import resources
from django.contrib.auth import get_user_model

User = get_user_model()


class UserResource(resources.ModelResource):
    def before_import_row(self, row, row_number=None, **kwargs):
        if not row.get("username"):
            raise ValueError("Each user must have a unique 'username'")

    class Meta:
        model = User
        import_id_fields = ['username']
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'phone_number', 'is_staff', 'is_superuser'
        )
