from django.urls import path

from .views import page_by_path
from .site_settings_views import site_settings
from .jobs import job_detail, jobs_list
from .preview import preview_revision


urlpatterns = [
    path("pages/by-path/", page_by_path, name="api-v1-page-by-path"),
    path("site-settings/", site_settings, name="api-v1-site-settings"),
    path("jobs/", jobs_list, name="api-v1-jobs"),
    path("jobs/<slug:slug>/", job_detail, name="api-v1-job-detail"),
    path("preview/<str:token>/", preview_revision, name="api-v1-preview"),
]
