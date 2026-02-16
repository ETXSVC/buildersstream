"""Plan configuration constants for BuilderStream subscription tiers.

Plans are defined as constants (not a database model) because they rarely
change and are tightly coupled to Stripe Price IDs configured in the
dashboard.  The Organization model stores which plan a tenant is on via
its ``subscription_plan`` choice field.
"""

PLAN_CONFIG = {
    "TRIAL": {
        "name": "Free Trial",
        "max_users": 5,
        "price_monthly": 0,
        "modules": [
            "PROJECT_CENTER",
            "CRM",
            "ESTIMATING",
            "SCHEDULING",
            "FINANCIALS",
            "CLIENT_PORTAL",
            "DOCUMENTS",
            "FIELD_OPS",
            "QUALITY_SAFETY",
            "ANALYTICS",
        ],
        "trial_days": 14,
    },
    "STARTER": {
        "name": "Starter",
        "max_users": 5,
        "stripe_price_monthly": "price_starter_monthly",
        "stripe_price_annual": "price_starter_annual",
        "price_monthly_per_user": 1500,  # $15.00 in cents
        "price_annual_per_user": 14400,  # $144.00/yr ($12/mo effective)
        "modules": [
            "PROJECT_CENTER",
            "CRM",
            "ESTIMATING",
            "CLIENT_PORTAL",
            "ANALYTICS",
        ],
    },
    "PROFESSIONAL": {
        "name": "Professional",
        "max_users": 25,
        "stripe_price_monthly": "price_pro_monthly",
        "stripe_price_annual": "price_pro_annual",
        "price_monthly_per_user": 5000,  # $50.00
        "price_annual_per_user": 48000,  # $480.00/yr ($40/mo effective)
        "modules": [
            "PROJECT_CENTER",
            "CRM",
            "ESTIMATING",
            "SCHEDULING",
            "FINANCIALS",
            "CLIENT_PORTAL",
            "DOCUMENTS",
            "FIELD_OPS",
            "QUALITY_SAFETY",
            "ANALYTICS",
        ],
    },
    "ENTERPRISE": {
        "name": "Enterprise",
        "max_users": 999,
        "stripe_price_monthly": "price_enterprise_monthly",
        "stripe_price_annual": "price_enterprise_annual",
        "price_monthly_per_user": 12500,  # $125.00
        "price_annual_per_user": 120000,  # $1,200.00/yr ($100/mo effective)
        "modules": [
            "PROJECT_CENTER",
            "CRM",
            "ESTIMATING",
            "SCHEDULING",
            "FINANCIALS",
            "CLIENT_PORTAL",
            "DOCUMENTS",
            "FIELD_OPS",
            "QUALITY_SAFETY",
            "PAYROLL",
            "SERVICE_WARRANTY",
            "ANALYTICS",
        ],
    },
}

# Valid plan keys that can be used for paid subscriptions
PAID_PLAN_KEYS = ("STARTER", "PROFESSIONAL", "ENTERPRISE")

# Map Stripe Price IDs back to plan keys for webhook processing
STRIPE_PRICE_TO_PLAN = {}
for _key, _cfg in PLAN_CONFIG.items():
    if "stripe_price_monthly" in _cfg:
        STRIPE_PRICE_TO_PLAN[_cfg["stripe_price_monthly"]] = _key
    if "stripe_price_annual" in _cfg:
        STRIPE_PRICE_TO_PLAN[_cfg["stripe_price_annual"]] = _key
