from rest_framework import serializers

from .models import Team, TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_trade = serializers.CharField(source="employee.trade", read_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "employee", "employee_name", "employee_trade", "role", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_employee_name(self, obj):
        return obj.employee.full_name


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
    employee_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=TeamMember.Role.choices, default=TeamMember.Role.MEMBER)
