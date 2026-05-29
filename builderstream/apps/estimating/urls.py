"""
Estimating URL configuration.

Routes:
  /api/v1/estimating/cost-codes/          -> CostCodeViewSet
  /api/v1/estimating/cost-items/          -> CostItemViewSet
  /api/v1/estimating/assemblies/          -> AssemblyViewSet
  /api/v1/estimating/assembly-items/      -> AssemblyItemViewSet
  /api/v1/estimating/estimates/           -> EstimateViewSet
  /api/v1/estimating/sections/            -> EstimateSectionViewSet
  /api/v1/estimating/line-items/          -> EstimateLineItemViewSet
  /api/v1/estimating/proposals/           -> ProposalViewSet
  /api/v1/estimating/proposal-templates/  -> ProposalTemplateViewSet
  /api/v1/estimating/public/proposals/<token>/ -> PublicProposalView (no auth)
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "estimating"

router = DefaultRouter()
router.register("cost-codes", views.CostCodeViewSet, basename="costcode")
router.register("cost-items", views.CostItemViewSet, basename="costitem")
router.register("assemblies", views.AssemblyViewSet, basename="assembly")
router.register("assembly-items", views.AssemblyItemViewSet, basename="assemblyitem")
router.register("estimates", views.EstimateViewSet, basename="estimate")
router.register("sections", views.EstimateSectionViewSet, basename="estimatesection")
router.register("line-items", views.EstimateLineItemViewSet, basename="estimatelineitem")
router.register("proposals", views.ProposalViewSet, basename="proposal")
router.register("proposal-templates", views.ProposalTemplateViewSet, basename="proposaltemplate")

urlpatterns = [
    path("", include(router.urls)),
    # Public (unauthenticated) proposal view/sign endpoint
    path(
        "public/proposals/<uuid:public_token>/",
        views.PublicProposalView.as_view(),
        name="public-proposal",
    ),
]
