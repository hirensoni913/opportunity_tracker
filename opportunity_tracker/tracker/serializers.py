from rest_framework import serializers
from .models import Opportunity


class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"
        read_only_fields = ["id", "created_by",
                            "created_at", "updated_by", "updated_at"]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user

        return super().create(validated_data)
