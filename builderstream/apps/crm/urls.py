"""CRM URL configuration — routers for all 7 models + analytics."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "crm"

router = DefaultRouter()
router.register("contacts", views.ContactViewSet, basename="contact")
router.register("companies", views.CompanyViewSet, basename="company")
router.register("pipeline-stages", views.PipelineStageViewSet, basename="pipelinestage")
router.register("leads", views.LeadViewSet, basename="lead")
router.register("interactions", views.InteractionViewSet, basename="interaction")
router.register("automation-rules", views.AutomationRuleViewSet, basename="automationrule")
router.register("email-templates", views.EmailTemplateViewSet, basename="emailtemplate")

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/", views.LeadAnalyticsView.as_view(), name="analytics"),
]
