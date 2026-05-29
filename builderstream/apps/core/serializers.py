"""Core serializers."""
from rest_framework import serializers


class TimeStampedSerializer(serializers.ModelSerializer):
    """Base serializer that includes timestamp fields as read-only."""

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
