"""Document serializers."""
from rest_framework import serializers

from .models import Document, Folder, RFI, Submittal


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at", "file_size", "file_type"]


class RFISerializer(serializers.ModelSerializer):
    class Meta:
        model = RFI
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class SubmittalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submittal
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
