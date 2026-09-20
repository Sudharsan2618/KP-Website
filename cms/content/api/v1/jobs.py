from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q
from django.http import JsonResponse
from wagtail.models import Page

from content.pages import JobPage

from .serializers import serialize_page


PAGE_SIZE = 20


def serialize_job(job):
    data = serialize_page(job)
    data["job"] = {
        "status": job.status,
        "is_open": job.status == "open",
        "is_remote": bool(job.remote),
        "application_email": job.application_email or None,
    }
    return data


def _job_facets(queryset):
    return {
        "locations": sorted(value for value in queryset.values_list("location_display", flat=True).distinct() if value),
        "categories": sorted(value for value in queryset.values_list("category", flat=True).distinct() if value),
        "remote": [False, True],
    }


def jobs_list(request):
    remote = request.GET.get("remote", "").strip().lower()
    if remote and remote not in {"true", "false", "1", "0"}:
        return JsonResponse({"error": "remote must be true or false"}, status=400)
    try:
        page_number = int(request.GET.get("page", "1"))
        if page_number < 1:
            raise ValueError
    except ValueError:
        return JsonResponse({"error": "page must be a positive integer"}, status=400)

    queryset = JobPage.objects.live().filter(status="open")
    facets = _job_facets(queryset)

    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(location_display__icontains=query)
            | Q(category__icontains=query)
            | Q(specialization__icontains=query)
        )

    location = request.GET.get("location", "").strip()
    if location:
        queryset = queryset.filter(location_display__iexact=location)

    category = request.GET.get("category", "").strip()
    if category:
        queryset = queryset.filter(category__iexact=category)

    if remote:
        queryset = queryset.filter(remote=remote in {"true", "1"})

    queryset = queryset.order_by("-publication_date", "title", "slug")
    paginator = Paginator(queryset, PAGE_SIZE)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = []

    return JsonResponse({
        "data": [serialize_job(job) for job in page],
        "meta": {
            "page": page_number,
            "page_size": PAGE_SIZE,
            "total": paginator.count,
            "pages": paginator.num_pages,
        },
        "facets": facets,
    })


def job_detail(request, slug):
    job = JobPage.objects.live().filter(slug=slug).first()
    if job is None:
        return JsonResponse({"error": "published job not found"}, status=404)
    return JsonResponse({"data": serialize_job(job)})
