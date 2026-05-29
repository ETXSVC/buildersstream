"""Custom DRF exceptions."""
from rest_framework.exceptions import APIException
from rest_framework import status


class PlanLimitExceeded(APIException):
    """Raised when an org has hit a resource limit for its subscription plan.

    Returns HTTP 402 Payment Required with a structured body:
        {
            "detail": "<human message>",
            "upgrade_required": true,
            "limit_type": "projects" | "crm_leads" | ...,
            "current": <int>,
            "limit": <int>
        }
    The frontend `apiClient` interceptor listens for 402 + upgrade_required
    and fires the global UpgradeModal.
    """

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = "Plan limit exceeded. Please upgrade your subscription."
    default_code = "plan_limit_exceeded"

    def __init__(self, detail: str, limit_type: str, current: int, limit: int):
        self.detail = {
            "detail": detail,
            "upgrade_required": True,
            "limit_type": limit_type,
            "current": current,
            "limit": limit,
        }
