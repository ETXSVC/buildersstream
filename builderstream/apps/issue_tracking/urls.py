"""Issue Tracking URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "issue_tracking"

router = DefaultRouter()
router.register("issue-types", views.IssueTypeViewSet, basename="issuetype")
router.register("issues", views.IssueViewSet, basename="issue")
router.register("comments", views.IssueCommentViewSet, basename="issuecomment")
router.register("canned-responses", views.CannedResponseViewSet, basename="cannedresponse")
router.register("escalation-rules", views.EscalationRuleViewSet, basename="escalationrule")

urlpatterns = [
    path("", include(router.urls)),
    path("reports/sla-compliance/", views.SLAComplianceView.as_view(), name="sla_compliance"),
]
