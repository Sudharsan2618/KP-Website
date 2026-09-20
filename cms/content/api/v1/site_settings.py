from .serializers import serialize_value


PUBLIC_SETTING_FIELDS = (
    "site_name", "full_logo", "compact_logo", "mobile_logo", "favicon", "default_social_image",
    "primary_navigation", "footer_navigation", "legal_navigation", "social_links",
    "default_telephone", "default_email", "offices", "footer_company_text", "copyright_text",
    "employer_cta_label", "candidate_cta_label", "calendly_url", "cookie_heading",
    "cookie_explanation", "cookie_accept_label", "cookie_reject_label", "cookie_customize_label",
    "cookie_privacy_link_label", "cookie_privacy_page", "analytics_enabled", "organization_legal_name",
    "organization_address", "organization_telephone", "organization_email", "organization_logo",
    "organization_social_profiles",
)


def serialize_site_settings(settings):
    return {field: serialize_value(getattr(settings, field, None)) for field in PUBLIC_SETTING_FIELDS}
