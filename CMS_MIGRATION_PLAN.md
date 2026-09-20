# KP Website CMS Migration Plan

## 1. Purpose

Convert the existing KP static website into a German-only CMS website without intentionally changing its design, layout, responsive behavior, animation choreography, copy, media, or current user journeys.

This document is an implementation specification. An implementing agent must follow the phases in order, must not invent missing content, and must not redesign any component.

## 2. Approved decisions

These decisions are fixed:

| Area | Decision |
|---|---|
| Frontend | Astro SSR, following the Sunrise reference architecture |
| CMS | Django + Wagtail |
| Database | PostgreSQL |
| Database configuration | Sunrise-style `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_SSLMODE` environment variables |
| Frontend hosting | Vercel |
| CMS hosting | Google Cloud Run |
| Media storage | Cloudinary |
| Language | German only |
| Design | Preserve the current design exactly; no redesign is authorized |
| Editing scope | Every visible text, image, video, link, navigation item, footer item, job, person, testimonial, service, price, office, CTA, legal section, and SEO value must be editable in Wagtail |
| Styling scope | CSS, component structure, breakpoints, and animation logic remain code-controlled so editors cannot accidentally redesign the site |
| Jobs | Managed manually in Wagtail for now; the model must be ready for a future ATS identifier and synchronization |
| Applications | Preserve the existing email-based application behavior; do not add an application form or ATS integration |
| Contact submissions | Not implemented until the owner defines the future workflow |
| CMS access | One Wagtail superuser is sufficient |
| URLs | Use clean German URLs and permanent redirects from all old `.html` URLs |
| Existing content | Import all current content, assets, and the 17 hard-coded jobs |
| Scheduling | Calendly; the owner will later enter the actual URL in Wagtail |
| Analytics | Cloudflare Web Analytics, enabled only when its environment token is present |
| Cookie consent | Self-hosted open-source Klaro, with German consent copy editable in Wagtail |
| Spam protection | Cloudflare Turnstile is reserved for the future form endpoint; do not load it while no form exists |

## 3. Repository evidence and constraints

### 3.1 Current KP implementation

The current repository is not a running WordPress site. It is a static mirror assembled by `build_static.py` and deployed from `site/` through `vercel.json`.

Current facts:

- There are 13 checked-in HTML pages.
- The pages contain duplicated WordPress/Ave/WPBakery markup and assets.
- `site/local-fixes.css` contains the current visual system and responsive behavior.
- `site/local-fixes.js` contains the current intro video, homepage hero replacement, scroll animations, service reveals, team behavior, and job-board logic.
- The job board contains exactly 17 hard-coded jobs in `site/local-fixes.js`.
- The current application action creates an email to `kontakt@kastellpersonalberatung.com` with the job title in the subject.
- The repository contains legacy WordPress, Revolution Slider, WPBakery, Contact Form 7, theme, and duplicated third-party assets that should not survive in the final runtime unless a visual dependency is proven necessary.
- `executive-search.html` is referenced by the old build map but no longer exists in the current site.
- Several pages have empty or incorrect heading structures, missing descriptions, old English legal text, and mojibake visible during command-line extraction. Migration must preserve approved content but normalize all stored text to UTF-8.

### 3.2 Sunrise reference implementation

Use Sunrise as an architectural reference, not as code to copy blindly.

Keep these patterns:

- Astro SSR frontend.
- Django/Wagtail CMS.
- PostgreSQL.
- Wagtail page models and site settings.
- REST API consumed by Astro.
- Dockerized CMS deployment.
- Draft, revision, publish, image, and document workflows.

Do not copy these Sunrise weaknesses:

- Do not use unrestricted `CORS_ALLOW_ALL_ORIGINS` in production.
- Do not store production media on the container filesystem.
- Do not simulate successful contact form submissions.
- Do not silently replace missing CMS data with hard-coded production copy.
- Do not list every page and then fetch a second request just to resolve one route.
- Do not run database migrations during every web-container startup.
- Do not claim headless preview works unless it is tested end to end.
- Do not leave SEO, structured data, redirect, and test coverage incomplete.

## 4. Scope and non-goals

### 4.1 In scope

- Rebuild the frontend in Astro while reproducing the current site visually.
- Build the Wagtail CMS and its REST endpoints.
- Move all visible content into structured Wagtail fields.
- Import current pages, team members, testimonials, offices, service cards, packages, process steps, legal text, media, and jobs.
- Replace `.html` routes with clean routes plus permanent redirects.
- Deploy the CMS container to Cloud Run.
- Keep the frontend deployable to Vercel.
- Store Wagtail uploads in Cloudinary.
- Add SEO, sitemap, robots, structured data, analytics, consent, preview, health checks, and tests.

### 4.2 Explicitly out of scope

- Redesigning or visually modernizing the website.
- Rewriting, translating, correcting, or legally approving content.
- ATS synchronization.
- Candidate accounts.
- Job application forms or CV uploads.
- Contact form submission/storage/email delivery.
- A second language.
- A second CMS role or approval chain.
- Paid analytics, paid consent management, or paid spam protection.

## 5. Target architecture

```text
Browser
  |
  v
Vercel: Astro SSR frontend
  |-- renders the unchanged KP design
  |-- reads published content by path
  |-- emits clean URLs, SEO, sitemap, and redirects
  |
  v
Cloud Run: Django + Wagtail + REST API
  |-- /admin/ for the single administrator
  |-- /api/v1/pages/by-path/
  |-- /api/v1/site-settings/
  |-- /api/v1/jobs/
  |-- /api/v1/preview/
  |-- /health/live and /health/ready
  |
  +--> PostgreSQL through DB_* environment variables
  +--> Cloudinary for uploaded images, documents, and CMS-managed videos
```

The existing checked-in videos may remain frontend static assets if editors do not need to replace them. Because the approved scope says all visible media must be editable, the initial records must also reference CMS/Cloudinary copies. Frontend static copies may be retained only as deployment fallbacks for an emergency rollback, not as the published source of truth.

## 6. Proposed repository structure

Create this structure inside the KP repository:

```text
/
  astro.config.mjs
  package.json
  package-lock.json
  tsconfig.json
  vercel.json
  .env.example
  src/
    components/
    layouts/
    lib/
      cms.ts
      content-types.ts
      seo.ts
      consent.ts
    pages/
    scripts/
    styles/
  public/
    brand/
    legacy-fallback/
  cms/
    Dockerfile
    manage.py
    requirements.txt
    .env.example
    kp_cms/
      settings/
        base.py
        dev.py
        production.py
      urls.py
      api.py
    content/
      models/
      blocks.py
      snippets.py
      settings.py
      api.py
      migrations/
      management/commands/import_legacy_content.py
    templates/
    static/
  migration-data/
    content.json
    manifest.json
  tests/
    e2e/
    visual/
  site/                       # retain unchanged until final acceptance
  CMS_MIGRATION_PLAN.md
```

Do not delete or rewrite `site/` during implementation. It is the visual and content baseline and is also required for rollback until production acceptance is complete.

## 7. URL contract

Create these canonical routes. The redirect source must preserve its query string.

| Old route | New canonical route | Target content |
|---|---|---|
| `/index.html` | `/` | Homepage |
| `/employers.html` | `/arbeitgeber/` | Employer landing page |
| `/candidates.html` | `/kandidaten/` | Candidate landing page |
| `/about-us.html` | `/ueber-uns/` | About/team page |
| `/contact.html` | `/kontakt/` | Contact page |
| `/projekte.html` | `/projekte/` | Job index |
| `/assessments.html` | `/leistungen/eignungsdiagnostik/` | Service page |
| `/bg-global-recruitment.html` | `/leistungen/internationale-rekrutierung/` | Service page |
| `/contingency-multiple-hiring.html` | `/leistungen/volumen-projektbesetzung/` | Service page |
| `/world-connect.html` | `/leistungen/employer-branding/` | Service page |
| `/cv-writing-packages.html` | `/karriere-services/bewerbungsunterlagen/` | CV package page |
| `/privacy-policy-2.html` | `/datenschutz/` | Privacy page |
| `/terms-of-use.html` | `/nutzungsbedingungen/` | Terms page |
| `/executive-search.html` | `/arbeitgeber/#executive-search` | Preserve the deleted legacy route without inventing a new page |

Also redirect the same paths without `.html` when they differ from the canonical German slug. Use HTTP 308 or 301 consistently. Add redirect tests that assert status, `Location`, and query-string preservation.

Job detail URLs must be `/projekte/<job-slug>/`. The listing may continue opening a design-identical modal, but every job must also have a crawlable canonical detail URL. Use `history.pushState` when a modal opens and restore `/projekte/` when it closes. Direct access to a job URL must render the same job content without requiring a previous listing-page visit.

## 8. CMS content model

### 8.1 Shared SEO fields

All public page types must support:

- Wagtail `title` and `slug`.
- `seo_title`.
- `search_description`.
- Open Graph title and description overrides.
- Open Graph image.
- Canonical URL override, blank by default.
- `noindex` boolean, false by default.
- Navigation label.
- Last reviewed date for legal pages.

Validation:

- SEO title: maximum 60 characters, with an editor warning rather than destructive truncation.
- Search description: maximum 160 characters, with an editor warning.
- Canonical override must be an absolute HTTPS URL.
- Only published pages appear in public API responses.

### 8.2 Site settings

Implement `KPSettings` as a Wagtail site setting with these editable fields:

- Site name.
- Full logo, compact logo, mobile logo, favicon, and default social image.
- Primary navigation as an ordered list of internal-page or external-URL items.
- Footer navigation and legal navigation.
- Social links.
- Default telephone and email.
- Ordered office list: label, street, postal code, city, telephone, email, and optional map URL.
- Footer company text and copyright text.
- Default CTA labels.
- Calendly URL.
- Cookie-banner German heading, explanation, accept label, reject label, customize label, privacy-link label, and privacy-page chooser.
- Analytics enabled boolean. The analytics token remains an environment variable, not a CMS secret.
- Organization structured-data fields: legal name, address, telephone, email, logo, and social profiles.

Navigation must not store raw page paths when a Wagtail page chooser can be used. External URLs must be explicitly marked external.

### 8.3 Reusable snippets

Create these snippets:

#### TeamMember

- Stable `source_key`.
- Name.
- Role.
- Portrait.
- Biography as rich text.
- Expertise tags as ordered values.
- Email, telephone, LinkedIn URL; all optional.
- Active boolean.

#### Testimonial

- Stable `source_key`.
- Quote.
- Person label, if present in the source.
- Role.
- Organization.
- Audience: employer or candidate.
- Display order.
- Active boolean.

Do not invent missing real names. Preserve anonymous labels exactly as currently displayed.

#### Service

- Stable `source_key`.
- Title.
- Short card description.
- Icon identifier from a controlled list that maps to the existing visual icon.
- Optional internal detail-page chooser.
- Display order.
- Audience placement: employer, candidate, or both.
- Active boolean.

#### Office

Use either a snippet or an ordered structure inside site settings, but not both. The same records must power the contact page and footer.

### 8.4 Page types

#### HomePage

Editable fields:

- Intro video, poster, tap-to-play label, and accessible video label.
- Scroll-hero video and poster.
- Ordered hero chapters, each containing eyebrow, heading, paragraph, CTA label, CTA destination, and video time/progress range.
- Employer CTA and candidate CTA.
- Any visible follow-on sections currently present in the final homepage DOM.

The mapping between scroll progress and video playback stays in code. Editors change content and media, not animation mathematics.

#### EmployerPage

Editable fields:

- Hero eyebrow, heading, text, background media, and CTAs.
- Intro heading and body.
- Ordered service references.
- “Warum Kastell” content and statistics found in the source.
- Ordered employer testimonials.
- Recruitment-region heading, copy, and ordered region labels.
- Closing CTA and Calendly CTA label.

The `Executive Search` section/card must have the DOM anchor `executive-search`.

#### CandidatePage

Editable fields:

- Hero content and media.
- Ordered candidate service references.
- Ordered candidate testimonials.
- Closing CTA content.
- Contact details shown on the page.

#### AboutPage

Editable fields:

- Hero content and media.
- “Wer wir sind” heading and ordered paragraphs/insights.
- Ordered statistics.
- Ordered team member references.
- Values strip entries.
- Contact CTA content.

Keep the current sticky team-card layout and animation intact.

#### ServicePage

Use one model for Eignungsdiagnostik, Internationale Rekrutierung, Volumen- & Projektbesetzung, and Employer Branding.

Editable fields:

- Eyebrow, title, hero background media.
- Intro and rich body sections.
- CTA heading, text, button label, and destination.
- Show Calendly CTA boolean.

The imported records must reproduce the current four pages. Do not create new service copy for HR Advisory or Executive Search unless it already exists in the source.

#### CVPackagesPage

Editable fields:

- Hero heading and intro.
- Ordered packages containing price, experience range, audience, description, CTA label, and CTA destination.
- “How it works” heading, introduction, and ordered steps.
- Delivery-time text.

Prices must be stored as display strings initially so the rendered source text remains exact. Do not add checkout or currency conversion.

#### ContactPage

Editable fields:

- Page heading and introduction.
- Ordered office references.
- Website URL label and URL.
- Optional closing copy.

Do not add a contact form in this phase.

#### JobsIndexPage

Editable fields:

- Hero eyebrow, heading, and intro.
- Search field labels and placeholders.
- Filter headings and labels.
- Empty-state text.
- Result-count format.
- Application note.
- Default application email.

It owns `JobPage` children and exposes filters for keyword, location, category, and remote status.

#### JobPage

Fields:

- Stable `source_key`.
- Title and slug.
- Status: draft, open, filled, or archived.
- Publication date.
- Optional closing date.
- Location display text.
- Remote boolean.
- Category.
- Specialization/module.
- Experience display text.
- Employment type, optional.
- Intro/summary.
- Responsibilities as ordered rich-text/list items.
- Candidate profile as ordered rich-text/list items.
- Benefits as ordered rich-text/list items.
- Application email override, optional.
- External ATS identifier, optional and unused for now.
- External ATS URL, optional and unused for now.
- SEO fields.

Only `open` published jobs appear in default results. Archived or filled jobs retain their URL but display a German closed-position state and are excluded from `JobPosting` structured data.

#### LegalPage

Use for Datenschutz and Nutzungsbedingungen.

Fields:

- Intro.
- Flexible rich-text body with headings, paragraphs, lists, and links.
- Last reviewed date.

Import the existing text exactly after UTF-8 normalization. Do not claim that the migrated legal wording has been legally reviewed.

## 9. API contract

Use a versioned `/api/v1/` namespace.

### 9.1 Published page by path

`GET /api/v1/pages/by-path/?path=/arbeitgeber/`

Requirements:

- Resolve directly in one backend request.
- Return page type, canonical path, SEO object, updated timestamp, and type-specific fields.
- Return 404 for unknown/unpublished content.
- Never include draft content without a valid preview token.

### 9.2 Site settings

`GET /api/v1/site-settings/`

Return only public settings. Never return secrets or private environment values.

### 9.3 Jobs

- `GET /api/v1/jobs/`
- `GET /api/v1/jobs/<slug>/`

Supported query parameters:

- `q`
- `location`
- `category`
- `remote`
- `page`

Use server-side filtering with deterministic ordering: newest publication date first, then title. Return filter facets and total count with the listing response.

### 9.4 Preview

Implement a signed, short-lived preview flow:

1. Wagtail generates a preview URL pointing to the Astro preview route.
2. The URL contains an opaque, time-limited signed token; it must not expose credentials.
3. Astro validates or exchanges the token server-to-server with the CMS.
4. The CMS returns the selected draft revision.
5. Preview responses use `Cache-Control: no-store` and `X-Robots-Tag: noindex`.

Test preview from the Wagtail edit screen. Do not mark this phase complete based only on an API unit test.

### 9.5 Failure behavior

- Development may show a descriptive CMS connection error.
- Production must return a designed 503 page when required CMS content cannot be loaded.
- Do not serve hidden hard-coded production copy when the CMS is unavailable.
- Add finite request timeouts and structured server logs without credentials.

## 10. Frontend reconstruction rules

### 10.1 Visual preservation

- Capture baseline screenshots before changing runtime code.
- Reproduce the current header, footer, typography, spacing, colors, cards, shadows, media cropping, breakpoints, and motion.
- Port relevant rules from `local-fixes.css` into organized Astro styles without changing computed output.
- Port relevant behavior from `local-fixes.js` into small scripts/components.
- Preserve GSAP/ScrollTrigger/Lenis only where currently required and license-compatible.
- Remove Revolution Slider, WPBakery, Contact Form 7, old WordPress theme JavaScript, jQuery, and unused Font Awesome assets after proving they are no longer required.
- Do not rename CSS classes during the first visual-equivalence pass unless the rendered output and behavior remain verified.
- Respect `prefers-reduced-motion` while keeping the existing reduced-motion behavior.

### 10.2 Component boundaries

Create at least these components:

- `SiteHeader`
- `SiteFooter`
- `IntroVideo`
- `ScrollVideoHero`
- `PrimaryCTA`
- `ServiceCard`
- `TestimonialCarousel` or the existing equivalent layout
- `TeamStickyCards`
- `JobFilters`
- `JobCard`
- `JobDetailModal`
- `OfficeDetails`
- `CalendlyLink`
- `ConsentManager`
- `SEOHead`

The components receive CMS data. They must not contain business copy except accessibility-safe structural labels that are also moved to settings when visible.

### 10.3 Encoding and language

- Store source and database content as UTF-8.
- Render `<html lang="de">`.
- Add German date formatting using `de-DE`.
- Preserve gender-inclusive punctuation and German characters.
- Add a migration assertion that rejects Unicode replacement characters such as `�` in imported published fields.

## 11. Legacy content migration

### 11.1 Inventory first

Generate `migration-data/manifest.json` containing:

- Every source page.
- Every canonical target path.
- Normalized text-block counts.
- Referenced images and videos.
- Link targets.
- Team member count.
- Testimonial counts split by audience.
- Package and process-step counts.
- Exactly 17 job records.
- SHA-256 checksums for source assets.

This manifest is a verification artifact, not CMS content.

### 11.2 Extract to deterministic data

Create `migration-data/content.json` from the current repository. Review it before importing.

Rules:

- Decode HTML entities.
- Normalize content to UTF-8 without silently dropping characters.
- Preserve paragraph and list ordering.
- Preserve source labels, including anonymous testimonial labels.
- Resolve internal links through the URL contract.
- Mark missing media instead of substituting invented media.
- Do not scrape the live website during the import; the checked-in repository is the approved source.

### 11.3 Idempotent import command

Implement:

```text
python manage.py import_legacy_content --data /path/to/content.json
```

Requirements:

- Run inside a database transaction where practical.
- Use `source_key` to update existing imported records instead of duplicating them.
- Create the required Wagtail root/site records.
- Upload imported media to Cloudinary through Django storage.
- Create and publish the page tree.
- Create all snippets and page relationships.
- Create exactly 17 initial `JobPage` records.
- Produce a summary of created, updated, skipped, and failed records.
- Exit nonzero on a partial migration.
- Support `--dry-run` without persistent database or Cloudinary changes.

Do not run the content import automatically at every container startup.

### 11.4 Post-import verification

Automated checks must compare the CMS/API result with the manifest:

- Expected page count and canonical paths.
- 17 jobs.
- Three team members currently visible on the About page.
- Testimonial counts per audience.
- Service cards and detail pages.
- Three CV packages and four process steps.
- Offices, phone numbers, and email addresses.
- Legal body section counts.
- All internal links resolve.
- All required media URLs return success.
- No Unicode replacement characters exist.

## 12. Search, filtering, and future ATS readiness

- Implement job search against PostgreSQL/Wagtail fields, not a client-side hard-coded array.
- Preserve the current filter design and modal interaction.
- Keep the API boundary independent of the page model so a later ATS adapter can upsert jobs using `external_ats_id`.
- Add a unique conditional constraint for nonblank `external_ats_id`.
- Do not build an ATS scheduler, webhook, or vendor-specific mapping now.
- Document the future integration point in `cms/content/services/jobs.py` without adding dead vendor code.

## 13. SEO and discoverability

- Generate canonical tags for every page.
- Generate `sitemap.xml` from published Wagtail pages and open jobs.
- Generate `robots.txt` with production/staging behavior controlled by environment.
- Add Open Graph and Twitter-compatible metadata.
- Add `Organization` or appropriate `EmploymentAgency` structured data from site settings.
- Add `JobPosting` JSON-LD for each open job detail URL.
- Add `BreadcrumbList` JSON-LD for nested pages.
- Ensure exactly one meaningful H1 on every page.
- Preserve meaningful existing page titles while allowing CMS editing.
- Set preview and nonproduction deployments to `noindex`.
- Do not fabricate review ratings, salary data, addresses, or job details for structured data.

## 14. Free integrations

### 14.1 Cloudflare Web Analytics

- Load the beacon only when `CLOUDFLARE_WEB_ANALYTICS_TOKEN` is present and analytics is enabled in Wagtail settings.
- Do not hard-code the token.
- Document how to disable it without a code deployment.
- Verify that no analytics request occurs in preview or automated visual tests.

### 14.2 Klaro consent manager

- Self-host the open-source Klaro package/assets rather than using a paid hosted service.
- Provide German consent UI copy through `KPSettings`.
- Configure services explicitly; do not use a generic accept-all script loader.
- Essential storage is always active.
- Analytics and any future embedded third-party service must respect the stored consent configuration where legally required.
- Link to `/datenschutz/`.
- Test accept, reject, reopen, and preference persistence.

This is a technical implementation, not legal advice. The site owner must approve the final German privacy and consent wording.

### 14.3 Calendly

- Store the Calendly URL in `KPSettings`.
- Until the URL is supplied, keep the existing CTA design but route it to `/kontakt/`.
- Once present, open the Calendly URL using the current button design.
- Prefer an external link for the initial release. Do not load Calendly JavaScript or an iframe unless the owner later requests an embedded scheduler.

### 14.4 Cloudflare Turnstile

- Do not load Turnstile in the current release because there is no submission form.
- When a future contact or application endpoint is implemented, require server-side token verification before processing a submission.
- Reserve documented environment names: `TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY`.
- Never treat client-side verification as sufficient.

## 15. Security requirements

- Production `DEBUG=False`.
- Require `DJANGO_SECRET_KEY` from Secret Manager/environment.
- Restrict `ALLOWED_HOSTS` to the Cloud Run hostname and approved custom CMS hostname.
- Restrict CORS to the production Vercel/custom frontend origins and explicit preview origins.
- Set `CSRF_TRUSTED_ORIGINS` explicitly.
- Enable secure session and CSRF cookies in production.
- Enable HSTS only after HTTPS/custom-domain verification.
- Trust the forwarded HTTPS header from Cloud Run.
- Keep the Wagtail admin and Django admin paths separate; Django admin may be disabled if unused.
- Rate-limit preview/token endpoints and future form endpoints.
- Never expose DB or Cloudinary secrets to the Astro client bundle.
- Do not log request authorization headers, cookies, database URLs, or Cloudinary secrets.
- Run Django's deployment checks before release.

## 16. Environment variables

### 16.1 CMS local/Cloud Run environment

Document these in `cms/.env.example` without real values:

```text
DJANGO_SETTINGS_MODULE=kp_cms.settings.production
DJANGO_SECRET_KEY=
ALLOWED_HOSTS=
CSRF_TRUSTED_ORIGINS=
CORS_ALLOWED_ORIGINS=
WAGTAILADMIN_BASE_URL=
FRONTEND_BASE_URL=
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_SSLMODE=require
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
PREVIEW_SIGNING_SECRET=
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=
```

### 16.2 Astro/Vercel environment

Document these in root `.env.example`:

```text
CMS_URL=http://127.0.0.1:8000
CMS_SERVER_TOKEN=
CLOUDFLARE_WEB_ANALYTICS_TOKEN=
PUBLIC_SITE_URL=http://localhost:4321
ROBOTS_ALLOW_INDEXING=false
```

Use `CMS_SERVER_TOKEN` only in server-side code. Do not prefix secrets with `PUBLIC_`.

## 17. Cloud Run deployment design

### 17.1 CMS image

- Use a pinned supported Python slim base image.
- Install pinned compatible Django, Wagtail, PostgreSQL, Cloudinary storage, Gunicorn, CORS, and test dependencies.
- Run as a non-root user.
- Collect static admin assets during image build when configuration permits; otherwise use a dedicated release step, not each request-serving startup.
- Bind Gunicorn to `0.0.0.0:$PORT`.
- Add a container health endpoint that does not leak configuration.

### 17.2 Migrations

- Create a Cloud Run Job or explicit release command for `python manage.py migrate --noinput`.
- Run the migration job before routing traffic to a revision that depends on the schema.
- Run `import_legacy_content` once as a separately invoked job after schema migration.
- Do not run migrations or the legacy import in the web container's startup command.

### 17.3 Superuser

- Provide an idempotent one-time command that reads the `DJANGO_SUPERUSER_*` variables.
- Store the password in Google Secret Manager.
- Remove or rotate the bootstrap password after first successful login.

### 17.4 Storage and statelessness

- All user-uploaded media must use Cloudinary.
- Do not rely on Cloud Run's ephemeral filesystem for persisted uploads.
- Static Wagtail admin assets may be served with WhiteNoise.
- Database connections must be safe for autoscaling and closed/reused appropriately.

## 18. Verification strategy

### 18.1 Backend tests

Test:

- Model validation and allowed page hierarchy.
- Site settings serialization.
- Published versus draft API visibility.
- Direct path resolution.
- Job filters, ordering, open/filled behavior, and pagination.
- Preview-token expiry and tamper rejection.
- Import idempotency and dry-run behavior.
- Redirect target data.
- Cloudinary storage configuration through a mocked storage backend.
- Health endpoints.
- Production security settings.

Suggested commands:

```text
python cms/manage.py check
python cms/manage.py check --deploy --settings=kp_cms.settings.production
python cms/manage.py test
```

### 18.2 Frontend tests

Test:

- CMS client success, 404, timeout, malformed response, and unavailable-CMS behavior.
- All routes render German content.
- Header and footer use CMS values.
- Jobs filter correctly and each modal/detail route is accessible.
- `mailto:` application subject contains the selected job title.
- Calendly fallback and configured URL behavior.
- Consent accept/reject/reopen behavior.
- Analytics script is conditional.
- Sitemap, robots, canonical, Open Graph, and JSON-LD output.

Suggested commands:

```text
npm ci
npm run typecheck
npm run lint
npm run test
npm run build
npm run test:e2e
```

Add these scripts if the chosen tooling requires them; none currently exist in KP.

### 18.3 Visual regression

Before implementation, serve `site/` and capture baselines at minimum for:

- Desktop Chromium: 1440 × 1000.
- Tablet Chromium: 768 × 1024.
- Mobile Chromium: 390 × 844.

Capture every canonical page and these interactive states:

- Homepage intro video fallback prompt.
- Homepage hero start, middle, and final scroll chapters.
- Desktop and mobile navigation open states.
- Employer and candidate service sections.
- About team cards at multiple scroll positions.
- Job list with no filters, filters applied, empty result, and modal open.

For stable screenshot tests, disable animation transitions, freeze time, use deterministic video posters, and wait for fonts. Use a maximum diff ratio of `0.005` as an automated alarm, followed by manual review of every reported difference. Dynamic video frames and animation interpolation require manual sequence review.

No intentional visual difference is acceptable without written owner approval.

### 18.4 Accessibility and compatibility

- Test keyboard navigation, visible focus, modal focus trap/return, Escape close, mobile menu, reduced motion, color contrast, image alternatives, and heading order.
- Run an automated accessibility scan and ship with zero critical or serious violations.
- Run Playwright smoke tests in Chromium, Firefox, and WebKit.
- Test current mobile Safari behavior through WebKit and at least one real mobile device before production acceptance when available.

### 18.5 Content and link checks

- Compare rendered normalized text to the migration manifest.
- Crawl all canonical routes.
- Fail for internal 4xx/5xx responses, redirect loops, missing assets, empty required metadata, duplicate canonical URLs, or duplicate job slugs.
- Confirm every legacy URL permanently redirects to the specified destination.

## 19. Ordered implementation phases

Each phase has a hard completion gate. Do not start a dependent phase while its gate is failing.

### Phase 0 — Baseline and inventory

Tasks:

1. Record the current Git commit.
2. Serve the static site locally.
3. Capture all visual baselines and interactive states.
4. Produce the content/media/link manifest.
5. Record current browser console errors and network failures separately so they are not mistaken for new regressions.

Gate:

- Every current page has a baseline screenshot and manifest entry.
- The manifest reports exactly 17 jobs.

### Phase 1 — Monorepo scaffolding

Tasks:

1. Add Astro SSR and Vercel adapter.
2. Add Django/Wagtail CMS under `cms/`.
3. Add PostgreSQL-only settings using the approved `DB_*` variables.
4. Add dev and production settings.
5. Add example environment files and ignore rules.
6. Add health endpoints.

Gate:

- Empty Astro, CMS, and PostgreSQL stack runs locally.
- Both build/check commands pass.

### Phase 2 — CMS models and migrations

Tasks:

1. Implement shared SEO fields, snippets, site settings, and every page model in Section 8.
2. Define allowed page hierarchy.
3. Add editor help text and field validation.
4. Create and review Django migrations.

Gate:

- The administrator can create/edit/preview/publish each content type.
- No visible content category identified in the manifest lacks a CMS field.

### Phase 3 — API and preview

Tasks:

1. Implement versioned API serializers/endpoints.
2. Implement direct page-path resolution.
3. Implement jobs list/detail/filter endpoints.
4. Implement settings endpoint.
5. Implement signed headless preview.
6. Restrict production CORS.

Gate:

- API contract tests pass.
- Wagtail preview displays an unpublished edit in Astro and is not indexable/cacheable.

### Phase 4 — Content extraction and import

Tasks:

1. Produce reviewed deterministic `content.json`.
2. Configure Cloudinary storage.
3. Implement dry-run and real import command.
4. Import all content and media into a clean local database.
5. Run post-import verification.

Gate:

- Counts, text, relationships, media, links, and 17 jobs match the manifest.
- Running the import twice creates no duplicates.

### Phase 5 — Astro visual reconstruction

Tasks:

1. Build shared layout/header/footer.
2. Port each route one at a time.
3. Bind all visible values to CMS API data.
4. Port animation and interactive behavior.
5. Remove each legacy runtime dependency only after the replacement passes visual comparison.
6. Implement designed 404 and 503 pages using the existing design language.

Recommended route order:

1. `/`
2. `/arbeitgeber/`
3. `/kandidaten/`
4. `/ueber-uns/`
5. `/projekte/` and job detail routes
6. Four service pages
7. CV packages
8. Contact
9. Legal pages

Gate:

- Every route passes desktop/tablet/mobile visual review.
- No business copy remains hard-coded in Astro components.

### Phase 6 — URLs and SEO

Tasks:

1. Add permanent redirects.
2. Add canonical metadata, sitemap, robots, Open Graph, and JSON-LD.
3. Verify page headings and link graph.
4. Add staging/preview noindex behavior.

Gate:

- Redirect, crawl, metadata, and structured-data tests pass.

### Phase 7 — Free integrations

Tasks:

1. Add conditional Cloudflare Web Analytics.
2. Add self-hosted Klaro and German CMS-managed consent copy.
3. Add the CMS-managed Calendly URL with contact fallback.
4. Document but do not load Turnstile until a form exists.

Gate:

- No optional third-party script loads when disabled or rejected.
- Calendly/contact fallback behaves as specified.

### Phase 8 — Deployment

Tasks:

1. Build the non-root Cloud Run CMS image.
2. Configure Cloud Run service, secrets, health checks, allowed hosts, CSRF, and CORS.
3. Configure and run the schema migration job.
4. Configure and run the one-time content import job.
5. Create the single administrator.
6. Configure Vercel SSR environment values.
7. Deploy a noindex staging frontend.

Gate:

- CMS admin, API, Cloudinary uploads, preview, and frontend work in staging.
- Production security checks pass.

### Phase 9 — Acceptance and cutover

Tasks:

1. Run the full backend, frontend, browser, accessibility, link, visual, and content suites.
2. Have the owner review all pages and CMS editing workflows.
3. Back up the database and export the Wagtail content state.
4. Switch production routing.
5. Verify redirects, canonical URLs, analytics, robots, and job email actions.
6. Monitor Cloud Run and Vercel errors after cutover.

Gate:

- The acceptance checklist in Section 20 is signed off.

## 20. Final acceptance checklist

The migration is complete only when every item is true:

- [ ] The website is German-only.
- [ ] The visual design has no intentional change.
- [ ] All 13 current page equivalents are available through canonical clean URLs.
- [ ] Every old `.html` URL permanently redirects correctly.
- [ ] All visible copy, images, videos, links, jobs, people, testimonials, services, prices, offices, CTAs, and legal text are editable in Wagtail.
- [ ] Styling and animation code cannot be accidentally changed from the CMS.
- [ ] Exactly 17 current jobs were imported.
- [ ] Jobs are searchable/filterable and have crawlable detail URLs.
- [ ] Job applications retain the current email behavior.
- [ ] No contact or application form falsely reports success.
- [ ] The Calendly URL is CMS-editable and falls back to `/kontakt/` while blank.
- [ ] Cloudinary stores all CMS-uploaded media.
- [ ] PostgreSQL uses the approved `DB_*` environment variables.
- [ ] The CMS runs statelessly on Cloud Run.
- [ ] The frontend runs as Astro SSR on Vercel.
- [ ] Wagtail draft preview works end to end.
- [ ] Production CORS, hosts, CSRF, cookies, secrets, and HTTPS settings are restricted.
- [ ] Analytics and consent integrations can be disabled without source edits.
- [ ] Sitemap, robots, canonical tags, social metadata, and valid structured data exist.
- [ ] All content and link verification checks pass.
- [ ] Automated tests pass.
- [ ] Visual regression review passes at desktop, tablet, and mobile widths.
- [ ] There are no critical or serious automated accessibility violations.
- [ ] A rollback path to the unchanged `site/` deployment and a database backup exist.

## 21. Instructions for low-level implementation models

Every implementation task passed to a model must include:

1. The exact phase and numbered task from this document.
2. The files the model may modify.
3. The files it must not modify.
4. The expected input data or API contract.
5. The exact verification commands.
6. The phase gate that must pass.

Rules for those models:

- Read the relevant existing files before editing.
- Do not change visual values to make implementation easier.
- Do not invent content, URLs, people, legal claims, job details, or credentials.
- Do not add a fallback that masks a CMS/API failure.
- Do not delete `site/`.
- Do not combine multiple phases into one unreviewed change.
- Stop and report if a required source value is missing.
- Include migration and test updates with every model/API change.
- Report changed files, commands run, results, and remaining failures.

Recommended change size: one model/content family, one route, or one infrastructure concern per task. Avoid assigning “build the entire CMS” as a single task.

## 22. Owner-provided values still required during deployment

Implementation can begin without these values, but staging/production activation cannot finish until the owner supplies them:

- PostgreSQL `DB_*` values.
- Cloudinary cloud name, API key, and API secret.
- Google Cloud project, region, Cloud Run service name, and approved CMS hostname.
- Vercel production/custom frontend hostname.
- Django and preview signing secrets.
- Initial administrator username, email, and bootstrap password.
- Calendly URL.
- Cloudflare Web Analytics token, if analytics is to be enabled.
- Final legally approved German privacy and consent wording.

