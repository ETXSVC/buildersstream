"""Client portal serializers."""
from rest_framework import serializers

from .models import ClientPortalAccess, Selection


class ClientPortalAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPortalAccess
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class SelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Selection
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
