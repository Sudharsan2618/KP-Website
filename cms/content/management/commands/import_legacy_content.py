import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Page, Site
from django.core.files import File
from django.core.files.base import ContentFile
from wagtail.images import get_image_model
from wagtail.documents import get_document_model
from django.conf import settings

from content.pages import (
    AboutPage,
    CVPackagesPage,
    CandidatePage,
    ContactPage,
    EmployerPage,
    JobPage,
    JobsIndexPage,
    LegalPage,
    ServicePage,
)
from home.models import HomePage


PAGE_MODELS = {
    "/": HomePage,
    "/arbeitgeber/": EmployerPage,
    "/kandidaten/": CandidatePage,
    "/ueber-uns/": AboutPage,
    "/kontakt/": ContactPage,
    "/projekte/": JobsIndexPage,
    "/leistungen/eignungsdiagnostik/": ServicePage,
    "/leistungen/internationale-rekrutierung/": ServicePage,
    "/leistungen/volumen-projektbesetzung/": ServicePage,
    "/leistungen/employer-branding/": ServicePage,
    "/karriere-services/bewerbungsunterlagen/": CVPackagesPage,
    "/datenschutz/": LegalPage,
    "/nutzungsbedingungen/": LegalPage,
}


class ImportSummary:
    def __init__(self):
        self.created = 0
        self.updated = 0
        self.skipped = 0
        self.failed = 0
        self.media_created = 0

    def line(self):
        return f"created={self.created} updated={self.updated} skipped={self.skipped} failed={self.failed} media_created={self.media_created}"


def _page_title(data):
    title = (data.get("title") or "").strip()
    if title:
        return title
    headings = data.get("headings") or []
    if headings and headings[0].get("text"):
        return headings[0]["text"].strip()
    return data.get("source_slug", "Unbenannte Seite").strip()


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%d.%m.%Y").date()


def rich(value):
    return f"<p>{value}</p>" if value else ""


class Command(BaseCommand):
    help = "Import checked-in KP legacy data into Wagtail pages and jobs."

    def add_arguments(self, parser):
        parser.add_argument("--data", required=True, help="Path to migration-data/content.json")
        parser.add_argument("--structured", help="Path to deterministic structured snippet data")
        parser.add_argument("--structured-only", action="store_true", help="Import structured snippets/settings without re-saving legacy pages and jobs")
        parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without database writes")

    def handle(self, *args, **options):
        data_path = Path(options["data"]).resolve()
        if not data_path.is_file():
            raise CommandError(f"Migration data file does not exist: {data_path}")
        try:
            raw = data_path.read_text(encoding="utf-8")
            if "\ufffd" in raw:
                raise CommandError("Migration data contains a Unicode replacement character")
            payload = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CommandError(f"Unable to read migration data: {exc}") from exc
        structured = {}
        if options.get("structured"):
            structured_path = Path(options["structured"]).resolve()
            try:
                structured = json.loads(structured_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise CommandError(f"Unable to read structured data: {exc}") from exc

        if len(payload.get("jobs", [])) != 17:
            raise CommandError("Migration data must contain exactly 17 jobs")
        for page in payload.get("pages", []):
            if page.get("canonical_path") not in PAGE_MODELS:
                raise CommandError(f"No page model mapping for {page.get('canonical_path')}")

        summary = ImportSummary()
        try:
            with transaction.atomic():
                if options["dry_run"]:
                    self.stdout.write("DRY RUN: no database or media changes will be made")
                else:
                    self._ensure_site_records()
                home = HomePage.objects.first() if not options["dry_run"] else None
                jobs_index = None
                if not options["structured_only"]:
                    for page_data in payload.get("pages", []):
                        model = PAGE_MODELS[page_data["canonical_path"]]
                        if model is JobsIndexPage:
                            jobs_index = self._upsert_page(model, home, page_data, options["dry_run"], summary)
                        elif model is HomePage:
                            home = self._upsert_page(model, None, page_data, options["dry_run"], summary)
                        else:
                            self._upsert_page(model, home, page_data, options["dry_run"], summary)
                    for job_data in payload.get("jobs", []):
                        self._upsert_job(jobs_index, job_data, options["dry_run"], summary)
                if structured:
                    self._upsert_structured(structured, home, options["dry_run"], summary, data_path.parents[1])
        except Exception as exc:
            summary.failed += 1
            raise CommandError(f"Legacy import failed ({summary.line()}): {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Legacy import complete: {summary.line()}"))

    def _media(self, source, repo_root, dry_run, summary):
        if not source:
            return None
        rel = source.replace("\\", "/").lstrip("/")
        if rel.startswith("wp-content/uploads/"):
            path = repo_root / "site" / rel
        else:
            path = repo_root / "site" / rel
        if not path.is_file() or dry_run:
            return None
        title = rel
        Image = get_image_model()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
            obj = Image.objects.filter(title=title).first()
            if obj is None:
                obj = Image(title=title, file=ContentFile(path.read_bytes(), name=path.name))
                obj.save()
                summary.media_created += 1
            return obj
        Document = get_document_model()
        obj = Document.objects.filter(title=title).first()
        if obj is None:
            obj = Document(title=title, file=ContentFile(path.read_bytes(), name=path.name))
            obj.save()
            summary.media_created += 1
        return obj

    def _video_url(self, source, repo_root, dry_run):
        if not source or dry_run or not getattr(settings, "CLOUDINARY_CONFIGURED", False):
            return ""
        path = repo_root / "site" / source.replace("\\", "/").lstrip("/")
        if not path.is_file():
            return ""
        import cloudinary.uploader
        result = cloudinary.uploader.upload(str(path), resource_type="video", use_filename=True, folder="media/videos")
        return result.get("secure_url", "")

    def _upsert_structured(self, data, home, dry_run, summary, repo_root):
        from content.snippets import Service, TeamMember, Testimonial
        from content.site_settings import KPSettings

        team_objects = []
        for item in data.get("team_members", []):
            if dry_run:
                summary.skipped += 1
                continue
            obj, created = TeamMember.objects.get_or_create(source_key=item["source_key"], defaults={"name": item["name"]})
            summary.created += int(created); summary.updated += int(not created)
            obj.name, obj.role, obj.biography = item["name"], item.get("role", ""), item.get("biography", "")
            obj.expertise_tags = [{"type": "tag", "value": tag} for tag in item.get("expertise_tags", [])]
            obj.portrait = self._media(item.get("portrait_src"), repo_root, dry_run, summary)
            obj.active = True
            obj.save(); team_objects.append(obj)

        service_objects = []
        detail_by_key = {"eignungsdiagnostik": "/leistungen/eignungsdiagnostik/", "internationale-rekrutierung": "/leistungen/internationale-rekrutierung/", "volumen-and-projektbesetzung": "/leistungen/volumen-projektbesetzung/", "employer-branding": "/leistungen/employer-branding/"}
        for item in data.get("services", []):
            if dry_run:
                summary.skipped += 1; continue
            obj, created = Service.objects.get_or_create(source_key=item["source_key"], defaults={"title": item["title"], "icon_identifier": "briefcase", "audience": item["audience"]})
            summary.created += int(created); summary.updated += int(not created)
            obj.title, obj.short_description, obj.audience = item["title"], item.get("short_description", ""), item["audience"]
            obj.display_order, obj.icon_identifier = item.get("display_order", 0), item.get("icon_identifier", "briefcase")
            slug = item["title"].lower().replace("&", "and").replace(" ", "-")
            path = detail_by_key.get(slug)
            obj.detail_page = Page.objects.filter(url_path=path).first() if path else None
            obj.active = True; obj.save(); service_objects.append(obj)

        for item in data.get("testimonials", []):
            if dry_run:
                summary.skipped += 1; continue
            obj, created = Testimonial.objects.get_or_create(source_key=item["source_key"], defaults={"quote": item["quote"], "audience": item["audience"]})
            summary.created += int(created); summary.updated += int(not created)
            obj.quote, obj.person_label, obj.organization = item["quote"], item.get("person_label", ""), item.get("organization", "")
            obj.audience, obj.display_order, obj.active = item["audience"], item.get("display_order", 0), True
            obj.save()

        if dry_run or home is None:
            return
        def page(path):
            return Page.objects.filter(url_path=path).specific().first()
        about, employers, candidates = page("/home/ueber-uns/"), page("/home/arbeitgeber/"), page("/home/kandidaten/")
        cv = CVPackagesPage.objects.first()
        # Populate page-specific copy/media directly from the frozen legacy
        # extraction.  This keeps the frontend data-driven and makes every
        # imported value editable in Wagtail instead of falling back to JSX.
        page_payloads = data.get("pages", {})
        for path, payload in page_payloads.items():
            target = page("/home" + path)
            if not target:
                continue
            if hasattr(target, "hero_eyebrow"):
                target.hero_eyebrow = payload.get("hero_eyebrow", "")
                target.hero_heading = payload.get("hero_heading", "") or target.hero_heading
                target.hero_text = payload.get("hero_text", "")
                target.hero_background_image = self._media(payload.get("hero_background_src"), repo_root, dry_run, summary)
            paragraphs = payload.get("paragraphs", [])
            if isinstance(target, EmployerPage):
                headings = payload.get("headings", [])
                target.intro_heading = next(
                    (x for x in headings if x.startswith("Eine Personalberatung")),
                    "",
                )
                intro_copy = next(
                    (x for x in headings if x.startswith("Kastell Personalberatung wei")),
                    "",
                )
                target.intro_body = rich(intro_copy)
                target.services_eyebrow = payload.get("services_eyebrow", "")
                target.services_heading = payload.get("services_heading", "")
                target.why_eyebrow = payload.get("why_eyebrow", "")
                target.why_heading = payload.get("why_heading", "")
                target.why_kastell = [{"type": "section", "value": {
                    "heading": item.get("heading", ""),
                    "body": item.get("body", ""),
                    "image": getattr(self._media(item.get("image_src"), repo_root, dry_run, summary), "pk", None),
                }} for item in payload.get("why_items", [])]
                target.testimonials_eyebrow = payload.get("testimonials_eyebrow", "")
                target.show_testimonial_content = bool(payload.get("show_testimonial_content", False))
                target.testimonials_background_image = self._media(payload.get("testimonials_background_src"), repo_root, dry_run, summary)
                target.recruitment_region_heading = payload.get("recruitment_region_heading", "")
                target.recruitment_region_copy = payload.get("recruitment_region_copy", "")
                target.recruitment_region_image = self._media(payload.get("recruitment_region_image_src"), repo_root, dry_run, summary)
                target.recruitment_regions = [{"type": "region", "value": item} for item in payload.get("recruitment_regions", [])]
                target.closing_eyebrow = payload.get("closing_eyebrow", "")
                target.closing_heading = payload.get("closing_heading", "")
                target.closing_copy = payload.get("closing_copy", "")
                target.closing_background_image = self._media(payload.get("closing_background_src"), repo_root, dry_run, summary)
                target.calendly_cta_label = payload.get("calendly_cta_label", "")
            elif isinstance(target, CandidatePage):
                target.show_hero = payload.get("show_hero", False)
                target.services_eyebrow = payload.get("services_eyebrow", "")
                target.services_heading = payload.get("services_heading", "")
                target.testimonials_eyebrow = payload.get("testimonials_eyebrow", "")
                target.show_testimonial_content = bool(payload.get("show_testimonial_content", False))
                target.testimonials_background_image = self._media(payload.get("testimonials_background_src"), repo_root, dry_run, summary)
                target.career_image = self._media(payload.get("career_image_src"), repo_root, dry_run, summary)
                target.career_heading = payload.get("career_heading", "")
                target.career_copy = payload.get("career_copy", "")
                target.contact_background_image = self._media(payload.get("contact_background_src"), repo_root, dry_run, summary)
                target.contact_heading = payload.get("contact_heading", "")
                target.contact_details = payload.get("contact_details", "") or (rich(paragraphs[-1]) if paragraphs else "")
            elif isinstance(target, AboutPage):
                target.who_we_are_heading = next((x for x in payload.get("headings", []) if "Zugang" in x), "")
                target.who_we_are_sections = [{"type": "section", "value": {"heading": "", "body": rich(x)}} for x in paragraphs[1:4]]
                target.team_eyebrow = "Das Beraterteam"
                target.team_heading = "Köpfe, die den Markt kennen."
                target.team_lead = rich("Drei Berater, ein Anspruch: Executive Search auf Augenhöhe – geprägt von jahrzehntelanger Erfahrung bei den führenden Namen der Branche.")
            elif isinstance(target, ServicePage):
                target.intro = "".join(rich(x) for x in paragraphs[1:])
            elif isinstance(target, CVPackagesPage):
                target.intro = rich(paragraphs[0]) if paragraphs else ""
            elif isinstance(target, ContactPage):
                target.introduction = "".join(rich(x) for x in paragraphs[:3])
            elif isinstance(target, LegalPage):
                target.intro = rich(paragraphs[0]) if paragraphs else ""
                target.body = "".join(rich(x) for x in paragraphs[1:])
            if hasattr(target, "save"):
                target.save(); target.save_revision().publish()
        home_data = data.get("home", {})
        headings = home_data.get("headings", [])
        if headings:
            home.hero_chapters = [{"type": "chapter", "value": {"heading": heading, "paragraph": ""}} for heading in headings]
        cta_values = []
        for item in home_data.get("ctas", []):
            target = employers if "Arbeitgeber" in item.get("label", "") else candidates
            if target:
                cta_values.append({"type": "cta", "value": {"label": item["label"], "is_external": "internal", "page": target.pk}})
        if cta_values:
            home.employer_cta = [cta_values[0]] if employers and "Arbeitgeber" in cta_values[0]["value"]["label"] else []
            home.candidate_cta = [cta_values[0]] if candidates and "Kandidat" in cta_values[0]["value"]["label"] else []
            for cta in cta_values[1:]:
                if "Arbeitgeber" in cta["value"]["label"]: home.employer_cta = [cta]
                if "Kandidat" in cta["value"]["label"]: home.candidate_cta = [cta]
        # Cloudinary video delivery is wired in a later media pass; keep the
        # source reference in structured.json without assigning an invalid
        # image/document object during this page import.
        home.intro_video = None
        if not home.intro_video_url:
            home.intro_video_url = self._video_url(home_data.get("intro_video_src"), repo_root, dry_run)
        home.save(); home.save_revision().publish()
        # The landing pages were updated in the page-content pass above. Reload
        # these references before attaching snippets so a stale in-memory
        # instance cannot overwrite the imported hero/body fields.
        if about:
            about.refresh_from_db()
        if employers:
            employers.refresh_from_db()
        if candidates:
            candidates.refresh_from_db()
        if about:
            about.team_members = [{"type": "member", "value": {"team_member": x.pk}} for x in team_objects]
            about.save(); about.save_revision().publish()
        services = list(Service.objects.order_by("display_order", "source_key"))
        tests = list(Testimonial.objects.order_by("display_order", "source_key"))
        if employers:
            employers.services = [{"type": "service", "value": {"service": x.pk}} for x in services if x.audience in ("employer", "both")]
            employers.testimonials = [{"type": "testimonial", "value": {"testimonial": x.pk}} for x in tests if x.audience == "employer"]
            employers.save(); employers.save_revision().publish()
        if candidates:
            candidates.services = [{"type": "service", "value": {"service": x.pk}} for x in services if x.audience in ("candidate", "both")]
            candidates.testimonials = [{"type": "testimonial", "value": {"testimonial": x.pk}} for x in tests if x.audience == "candidate"]
            candidates.save(); candidates.save_revision().publish()
        if cv:
            cv.packages = [{"type": "package", "value": {"name": x["name"], "price_display": x["price_display"], "experience_range": x.get("experience_range", ""), "audience": "Kandidat:innen", "description": x.get("description", "")}} for x in data.get("cv_packages", [])]
            cv.how_it_works_steps = [{"type": "step", "value": x} for x in data.get("cv_steps", [])]
            cv.save(); cv.save_revision().publish()
        settings = KPSettings.for_site(Site.objects.get(is_default_site=True))
        settings.offices = [{"type": "office", "value": {**x, "map_url": ""}} for x in data.get("office_text", [])]
        settings.default_telephone = data.get("office_text", [{}])[0].get("telephone", "") if data.get("office_text") else ""
        settings.default_email = data.get("office_text", [{}])[0].get("email", "") if data.get("office_text") else ""
        nav = [("Home", "/home/"), ("Für Arbeitgeber", "/home/arbeitgeber/"), ("Für Kandidaten", "/home/kandidaten/"), ("Über uns", "/home/ueber-uns/"), ("Projekte", "/home/projekte/"), ("Kontakt", "/home/kontakt/")]
        settings.primary_navigation = [{"type": "item", "value": {"label": label, "is_external": False, "page": Page.objects.filter(url_path=path).values_list("pk", flat=True).first(), "external_url": ""}} for label, path in nav]
        settings.footer_navigation = [{"type": "item", "value": {"label": label, "is_external": False, "page": Page.objects.filter(url_path=path).values_list("pk", flat=True).first(), "external_url": ""}} for label, path in nav[1:]]
        settings.social_links = [{"type": "item", "value": {"label": "LinkedIn", "url": "https://www.linkedin.com/company/kastell-personalberatung/"}}, {"type": "item", "value": {"label": "Web", "url": "https://www.kastellpersonalberatung.com/"}}, {"type": "item", "value": {"label": "Instagram", "url": "https://www.instagram.com/kastell.personal/"}}, {"type": "item", "value": {"label": "Xing", "url": "https://www.xing.com/"}}]
        settings.copyright_text = "© Kastell Personalberatung. Alle Rechte vorbehalten."
        settings.site_name = "Kastell Personalberatung"
        settings.full_logo = self._media(home_data.get("logo_src"), repo_root, dry_run, summary)
        settings.compact_logo = self._media(home_data.get("compact_logo_src"), repo_root, dry_run, summary)
        settings.mobile_logo = settings.compact_logo
        settings.save()

    def _ensure_site_records(self):
        root = Page.get_first_root_node()
        home = HomePage.objects.first()
        if home is None:
            home = root.add_child(instance=HomePage(title="Home", slug="home"))
            home.save_revision().publish()
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            Site.objects.create(hostname="localhost", port=80, site_name="KP Personalberatung", root_page=home, is_default_site=True)
        elif site.root_page_id != home.id:
            site.root_page = home
            site.save(update_fields=["root_page"])

    def _upsert_page(self, model, parent, data, dry_run, summary):
        path = data["canonical_path"]
        title = _page_title(data)
        slug = "home" if path == "/" else path.strip("/").split("/")[-1]
        existing = None if dry_run else Page.objects.filter(slug=slug, depth__gt=1).specific().first()
        if existing is not None and not isinstance(existing, model):
            raise CommandError(f"Existing page {existing.id} at slug {slug} has type {type(existing).__name__}, expected {model.__name__}")
        if dry_run:
            summary.skipped += 1
            return existing
        if existing is None:
            if model is HomePage:
                existing = HomePage.objects.first()
            else:
                if parent is None:
                    raise CommandError(f"Cannot create {path} without a HomePage parent")
                initial = {"title": title, "slug": slug}
                field_names = {field.name for field in model._meta.concrete_fields}
                if "hero_heading" in field_names:
                    initial["hero_heading"] = title
                if "page_heading" in field_names:
                    initial["page_heading"] = title
                if "service_key" in field_names:
                    initial["service_key"] = slug
                existing = parent.add_child(instance=model(**initial))
            summary.created += 1
        else:
            summary.updated += 1
        existing.title = title
        existing.slug = slug
        existing.search_description = data.get("meta_description", "")
        existing.navigation_label = title if len(title) <= 120 else ""
        if hasattr(existing, "hero_heading"):
            existing.hero_heading = title
        if hasattr(existing, "page_heading"):
            existing.page_heading = title
        if isinstance(existing, ServicePage):
            existing.service_key = slug
        if isinstance(existing, JobsIndexPage):
            existing.hero_eyebrow = "PROJEKTE"
            existing.hero_heading = "Aktuelle Projekte"
            existing.hero_intro = "Finden Sie Ihre nächste Herausforderung in IT, Engineering und Financial Services."
            existing.search_label = "Suche"
            existing.search_placeholder = "Stellenbezeichnung oder Stichwort"
            existing.filter_heading = "Projekte filtern"
            existing.location_filter_label = "Standort"
            existing.category_filter_label = "Kategorie"
            existing.remote_filter_label = "Remote möglich"
            existing.empty_state_text = "Keine passenden Projekte gefunden."
            existing.result_count_format = "{count} Projekte gefunden"
        existing.save()
        existing.save_revision().publish()
        return existing

    def _upsert_job(self, parent, data, dry_run, summary):
        if dry_run:
            summary.skipped += 1
            return
        if parent is None:
            raise CommandError("JobsIndexPage is required before importing jobs")
        job = JobPage.objects.filter(source_key=data["source_key"]).first()
        if job is None:
            job = parent.add_child(instance=JobPage(title=data["t"], slug=data["slug"], source_key=data["source_key"]))
            summary.created += 1
        else:
            summary.updated += 1
        job.title = data["t"]
        job.slug = data["slug"]
        job.status = "open"
        job.publication_date = _parse_date(data.get("date"))
        job.location_display = data.get("loc", "")
        job.remote = bool(data.get("remote"))
        job.category = data.get("cat", "")
        job.specialization = data.get("mod", "")
        job.experience_display = data.get("exp", "")
        job.summary = data["t"]
        job.save()
        job.save_revision().publish()
