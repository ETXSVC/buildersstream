from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Team, TeamMember

User = get_user_model()


class TeamMemberSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "user", "user_full_name", "user_email", "role", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "description", "member_count", "members", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.members.count()


class TeamListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "description", "member_count", "created_at"]
        read_only_fields = ["id", "name", "description", "member_count", "created_at"]

    def get_member_count(self, obj):
        return obj.members.count()


class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=TeamMember.Role.choices, default=TeamMember.Role.MEMBER)
