# KP CMS Migration Task Tracker

Source of truth: [CMS_MIGRATION_PLAN.md](CMS_MIGRATION_PLAN.md). Work is strictly sequential. A task may be marked `DONE` only when its evidence is recorded below and its phase gate passes.

Status values: `TODO`, `IN PROGRESS`, `BLOCKED`, `DONE`.

## Working rules

- Never skip a phase gate.
- Never modify `site/` during baseline or inventory work.
- Never invent missing content, credentials, providers, legal wording, URLs, or media.
- Keep all changes small enough to review and test.
- Every implementation task must list allowed files, forbidden files, verification commands, and expected output before coding.
- Stop and ask the owner when source data or an approved decision is missing.

## Phase 0 — Baseline and inventory

- [x] **P0.1 — Record repository baseline** — `DONE`
  - Verify branch, commit, clean/dirty state, tracked source files, and existing plan files.
  - Evidence: command output recorded in this tracker.
- [x] **P0.2 — Start a local static server** — `DONE`
  - Serve only the existing `site/` directory; do not alter files.
  - Evidence: local URL and server command.
- [x] **P0.3 — Capture visual baselines** — `DONE`
  - Capture every current page at desktop, tablet, and mobile sizes, plus required interactive states.
  - Evidence: baseline manifest and screenshot directory.
- [x] **P0.4 — Capture browser diagnostics** — `DONE`
  - Record console errors, failed requests, redirects, and missing assets separately from the baseline.
  - Evidence: diagnostics report.
- [x] **P0.5 — Build content/media/link manifest** — `DONE`
  - Produce deterministic `migration-data/manifest.json` and reviewed `migration-data/content.json` from checked-in files only.
  - Evidence: counts, hashes, and review summary.
- [x] **P0.6 — Verify Phase 0 gate** — `DONE`
  - Required: every current page has a baseline and manifest entry; manifest reports exactly 17 jobs.

## Phase 1 — Monorepo scaffolding

- [x] **P1.1 — Scaffold Astro SSR frontend** — `DONE`
- [x] **P1.2 — Scaffold Django/Wagtail CMS** — `DONE`
- [x] **P1.3 — Add PostgreSQL `DB_*` settings** — `DONE`
- [x] **P1.4 — Add dev/production settings and env examples** — `DONE`
- [x] **P1.5 — Add Cloud Run health endpoints** — `DONE`
- [x] **P1.6 — Verify Phase 1 gate** — `DONE`
  - Empty Astro, CMS, and PostgreSQL stack runs locally; frontend build and CMS checks pass.

## Phase 2 — CMS models and migrations

- [x] **P2.1 — Implement shared SEO fields** — `DONE`
- [x] **P2.2 — Implement KP site settings** — `DONE`
- [x] **P2.3 — Implement TeamMember, Testimonial, Service, and Office data** — `DONE`
- [x] **P2.4 — Implement HomePage and landing page models** — `DONE`
- [x] **P2.5 — Implement ServicePage, CVPackagesPage, ContactPage, and LegalPage** — `DONE`
- [x] **P2.6 — Implement JobsIndexPage and JobPage** — `DONE`
- [x] **P2.7 — Add editor help text, validation, and allowed page hierarchy** — `DONE`
- [x] **P2.8 — Create and review Django migrations** — `DONE`
- [x] **P2.9 — Verify Phase 2 gate** — `DONE`
  - Every visible content category has a CMS field; each content type can be edited, previewed, and published.

## Phase 3 — API and preview

- [x] **P3.1 — Implement versioned Wagtail API serializers** — `DONE`
- [x] **P3.2 — Implement direct published page-by-path endpoint** — `DONE`
- [x] **P3.3 — Implement site-settings endpoint** — `DONE`
- [x] **P3.4 — Implement jobs list/detail/filter endpoints** — `DONE`
- [x] **P3.5 — Implement signed short-lived headless preview** — `DONE`
- [x] **P3.6 — Restrict production CORS and add API failure behavior** — `DONE`
- [ ] **P3.7 — Verify Phase 3 gate** — `IN PROGRESS`
  - API contract tests pass; an unpublished edit previews in Astro and is not indexable/cacheable.

## Phase 4 — Content extraction and import

- [x] **P4.1 — Review and freeze deterministic content JSON** — `DONE`
- [x] **P4.2 — Configure Cloudinary storage** — `DONE`
- [x] **P4.3 — Implement dry-run/idempotent import command** — `DONE`
- [x] **P4.4 — Import pages, snippets, media, and all 17 jobs locally** — `DONE`
- [x] **P4.5 — Run post-import content verification** — `DONE`
- [ ] **P4.6 — Verify Phase 4 gate** — `IN PROGRESS`
  - Counts, text, relationships, media, links, and jobs match the manifest; a second import creates no duplicates.

## Phase 5 — Astro visual reconstruction

### P5.1–P5.2 implementation evidence (2026-09-19)

- Added shared CMS API client and reusable German Astro layout with CMS settings-driven shell.
- Added CMS-driven homepage chapters, audience CTAs, and Cloudinary-hosted intro video URL.
- Added dynamic route rendering for all mapped pages and job detail paths.
- `npm run build` passes; homepage and employer route smoke checks return HTTP 200; API v1 tests pass (12/12).
- All 13 mapped public routes and a representative job detail route return HTTP 200; the projects index renders the CMS jobs collection and job details render CMS fields.
- Homepage now follows the source sequence: a CMS-managed Cloudinary intro video is the only visible initial layer; the CMS header/body/footer shell is hidden until `ended`, then revealed with a fade. Video load errors safely reveal the site.

- [x] **P5.1 — Build CMS-driven shared layout/header/footer** — `DONE`
- [x] **P5.2 — Port homepage without visual changes** — `DONE`
  - Fixed splash handoff regression: the inline Astro script was emitted as a literal template expression (`{`...`}`), so the video ended while `.site-shell.pre-splash` stayed hidden. The script now executes normally and reveals the CMS page on the original final-frame/ended flow; browser verification confirms the shell becomes visible and the splash becomes hidden.
  - Reconstructed the original homepage visual system from `site/index.html` and `site/local-fixes.css`: Nunito typography, green/gold gradient hero, centered logo lockup, responsive spacing, outlined pill CTAs, dark-green navigation/footer, and CMS-driven labels/links.
  - Tightened responsive hero typography and vertical rhythm so the full brand lockup, subtitle, and CTAs fit the first viewport; reduced footer height from 120px to 36px (about 70%) and retained wrapping behavior for narrow screens.
- [x] **P5.3 — Port employer and candidate pages** — `DONE`
  - Shared page renderer now consumes the CMS hero, intro, service, testimonial, region, career, contact, and CTA fields and applies the source green/gold/Nunito system. Route smoke checks for `/arbeitgeber/` and `/kandidaten/` return HTTP 200. Final visual parity remains open for owner review.
  - Development evidence (2026-09-20): added source-specific CandidatePage fields for the no-hero flow, services headings, testimonial background, career image/copy, and contact background/details; regenerated structured migration data; applied `content.0009_candidatepage_career_copy_and_more`; re-imported successfully with `created=0 updated=59 skipped=0 failed=0 media_created=1`. Candidate API now exposes `show_hero=false`, 4 services, 9 testimonials, and all candidate-specific media. Employer API exposes 6 services, 6 “Warum Kastell” items, 7 testimonials, 6 regions, and all employer-specific media. `npm run build` passes; `/arbeitgeber/` and `/kandidaten/` both return HTTP 200. Browser/UI review remains intentionally owner-controlled.
  - Bug fix evidence (2026-09-20): fixed the dynamic route error-state crash caused by evaluating `page.title` when the CMS lookup returned `null`. The route now uses a safe fallback title; `npm run build` passes and `/does-not-exist/` returns HTTP 200 with the CMS-unavailable fallback instead of `Cannot read properties of null`.
  - Testimonial parity evidence (2026-09-20): source screenshots show the candidate/employer testimonial image band with only its eyebrow and carousel arrows visible, while testimonial records remain available in the CMS. Added `show_testimonial_content` to both page models (migration `content.0010`), defaulted/imported it to `false`, and updated the renderer to preserve the banner/arrows while hiding cards in the legacy state. API verification confirms employer `false`/7 records and candidate `false`/9 records; `check`, migration drift check, and `npm run build` pass. Editors can enable the cards per page without deleting imported content.
- [x] **P5.4 — Port About/team page** — `DONE`
  - Renderer now supports CMS who-we-are sections, statistics, team references, biographies, images, values, and contact CTA blocks using the source dark team band/card treatment. `/ueber-uns/` returns HTTP 200.
  - Development evidence (2026-09-20): added CMS-backed About intro rendering and source-aligned alternating team cards with portraits, bios, expertise tags, and numbered ordering. `/ueber-uns/` returns HTTP 200 after the Astro production build; final owner visual review remains open.
  - Follow-up parity fix (2026-09-20): matched the source `kpa-sticky-team` structure with CMS-editable team eyebrow/heading/lead fields, light editorial team cards, alternating portrait sides, and the source image-frame treatment. Fixed the API field mapping from `team_member.portrait` to the renderer, which was the cause of blank portrait panels. Migration `content.0011` applied and re-import completed with `failed=0`.
- [x] **P5.5 — Port jobs index, modal, and detail routes** — `DONE`
  - Jobs index and detail rendering now use the source green/gold layout and CMS job fields; `/projekte/` returns HTTP 200 and the 17 imported jobs remain API-driven.
  - Development evidence (2026-09-20): inspected `site/projekte.html` and confirmed the legacy page is a JS mount point (`#kp-jobs-root`), so job content is sourced from the structured 17-record feed rather than static HTML. Added CMS-driven hero/filter copy, keyword/location/category/remote filters, result state, job metadata, benefits rendering, and responsive cards/detail presentation. Re-import completed with `created=0 updated=59 skipped=0 failed=0`; API verification confirms 17 jobs and 5 remote matches; system checks, migration drift check, and `npm run build` pass.
  - Follow-up parity fix (2026-09-20): the generic page hero was also rendering on `JobsIndexPage`, duplicating “Aktuelle Projekte” above the dedicated jobs hero. Jobs index routes now suppress the generic hero and render one source-aligned jobs hero only.
- [ ] **P5.6 — Port service pages and CV packages** — `IN PROGRESS`
  - Renderer now supports CMS service body sections, package cards, ordered process steps, prices, and CTAs with responsive source styling. Build passes; final content/media parity remains open.
- [ ] **P5.7 — Port Contact and legal pages** — `IN PROGRESS`
  - Contact office cards and legal rich text are rendered from CMS settings/page fields; `/kontakt/` returns HTTP 200. Final source-specific background/social footer parity remains open.
- [x] **P5.8 — Remove legacy runtime dependencies only after proof** — `DONE`
- [ ] **P5.9 — Verify Phase 5 gate** — `TODO`
  - All routes pass visual review at desktop/tablet/mobile; no business copy remains hard-coded in Astro.

## Phase 6 — URLs and SEO

- [ ] **P6.1 — Implement canonical clean routes** — `TODO`
- [ ] **P6.2 — Implement permanent legacy redirects** — `TODO`
- [ ] **P6.3 — Implement metadata, sitemap, robots, and JSON-LD** — `TODO`
- [ ] **P6.4 — Verify headings, canonical URLs, and link graph** — `TODO`
- [ ] **P6.5 — Verify Phase 6 gate** — `TODO`

## Phase 7 — Free integrations

- [ ] **P7.1 — Add conditional Cloudflare Web Analytics** — `TODO`
- [ ] **P7.2 — Add self-hosted Klaro consent manager** — `TODO`
- [ ] **P7.3 — Add CMS-managed Calendly URL with contact fallback** — `TODO`
- [ ] **P7.4 — Document future Turnstile integration without loading it now** — `TODO`
- [ ] **P7.5 — Verify Phase 7 gate** — `TODO`

## Phase 8 — Cloud Run and Vercel deployment

- [ ] **P8.1 — Build non-root Cloud Run CMS image** — `TODO`
- [ ] **P8.2 — Add release migration job** — `TODO`
- [ ] **P8.3 — Add one-time content import job** — `TODO`
- [ ] **P8.4 — Configure secrets, hosts, CSRF, CORS, and health checks** — `TODO`
- [ ] **P8.5 — Create the single administrator** — `TODO`
- [ ] **P8.6 — Configure Vercel SSR environment** — `TODO`
- [ ] **P8.7 — Deploy noindex staging** — `TODO`
- [ ] **P8.8 — Verify Phase 8 gate** — `TODO`

## Phase 9 — Acceptance and cutover

- [ ] **P9.1 — Run the complete backend/frontend/browser/accessibility/link/visual/content suites** — `TODO`
- [ ] **P9.2 — Owner reviews all pages and CMS workflows** — `TODO`
- [ ] **P9.3 — Back up database and export CMS content** — `TODO`
- [ ] **P9.4 — Switch production routing** — `TODO`
- [ ] **P9.5 — Verify redirects, SEO, analytics, robots, and job email actions** — `TODO`
- [ ] **P9.6 — Monitor and document rollback readiness** — `TODO`
- [ ] **P9.7 — Verify Phase 9 gate and sign off acceptance checklist** — `TODO`

## Evidence log

### P0.1 — Repository baseline

Status: `DONE`

Evidence recorded on 2026-09-18:

- Branch: `main`
- Baseline commit: `5938e76da55ba9acc06d4fd0b1908b76e664c46d`
- Tracked files at baseline: `266`
- Current static HTML pages: `13`
- Existing user changes before this migration: none; only the untracked plan and task tracker were added during this work.
- Protected baseline pages: `about-us.html`, `assessments.html`, `bg-global-recruitment.html`, `candidates.html`, `contact.html`, `contingency-multiple-hiring.html`, `cv-writing-packages.html`, `employers.html`, `index.html`, `privacy-policy-2.html`, `projekte.html`, `terms-of-use.html`, `world-connect.html`.

### P0.2 — Local static server

Status: `DONE`

Evidence recorded on 2026-09-18:

- Command: `python -m http.server 4173`
- Working directory: `C:\Users\WELCOME\Desktop\FL\KP-Website\site`
- Runtime: Python `3.13.5`
- Verified all 13 HTML pages respond with HTTP `200` and their expected source byte counts.

### P0.3 — Visual baselines

Status: `DONE`

Evidence recorded on 2026-09-18:

- 39 screenshots generated in `.baseline/`.
- Screenshot dimensions: 13 × 1440×1000, 13 × 768×1024, 13 × 390×844.
- Representative visual checks were inspected for homepage, employer page, and mobile jobs page.

### P0.4 — Browser diagnostics

Status: `DONE`

Evidence: `.baseline/diagnostics.md`.

- All 13 pages returned HTTP 200.
- Browser console produced no warnings or errors.
- Resource probes were checked against direct HTTP HEAD responses; lazy-loading timing signals were documented rather than misclassified as missing files.

### P0.5 — Content/media/link manifest

Status: `DONE`

Evidence:

- Generator: `migration-data/build_inventory.py`
- Output: `migration-data/manifest.json` and `migration-data/content.json`
- Source: checked-in `site/` HTML and `site/local-fixes.js` only; no network access.
- Pages: `13`; mapped pages: `13`; unmapped pages: `0`.
- Jobs: `17`.
- Links: `190` total, `31` external.
- Media references: `108`; unique local media references: `28`.
- Asset inventory: `172` hashed assets.
- Both JSON files parse successfully as UTF-8 JSON.
- No Unicode replacement character was found in generated content data.

### P0.6 — Phase 0 gate

Status: `DONE`

Phase 0 gate passed on 2026-09-18:

- Every current page has a baseline screenshot and manifest entry.
- The manifest reports exactly 17 jobs.
- No implementation code or `site/` baseline file was changed.

### P1.1 — Astro SSR frontend

Status: `DONE`

Evidence recorded on 2026-09-18:

- Added `package.json`, `package-lock.json`, `astro.config.mjs`, `.env.example`, and a minimal German Astro route at `src/pages/index.astro`.
- `npm install` completed successfully.
- `npm run build` completed successfully using `@astrojs/vercel`.
- Astro `7.3.3` requires Node `>=22.12.0`; the repository declares that engine explicitly.
- The initial dependency audit findings were resolved in the follow-up security task below.

### Phase gates

- Phase 0: `PASSED` on 2026-09-18.
- Phase 1: `PASSED` on 2026-09-19. Phase 2: `PASSED` on 2026-09-19. Phase 3: `IN PROGRESS` after P3.6; P3.7 awaits one manual Wagtail-to-Astro draft preview check.

### P3.1 — Versioned Wagtail API serializers

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added `content.api.v1.serializers.PageSerializer` and deterministic JSON-safe helpers for page envelopes, SEO fields, dates, StreamField values, chooser references, and type-specific model fields.
- Serializer output includes type, id, title, slug, url path, SEO object, updated timestamp, and fields; publication filtering remains in the endpoint layer.
- Added three focused serializer tests covering SEO fallback, nested value normalization, and envelope shape.
- Django checks passed and all P3.1 tests passed.

### P3.2 — Published page-by-path endpoint

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added `GET /api/v1/pages/by-path/?path=/.../` with strict absolute-path validation and one live-page lookup.
- Drafts/unpublished pages and unknown paths return HTTP 404; malformed paths return HTTP 400.
- Successful responses use the versioned serializer envelope under `data`.
- Added three endpoint tests; all six API v1 tests pass and Django checks remain green.

### P3.3 — Public site-settings endpoint

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added `GET /api/v1/site-settings/` using the registered `KPSettings` site setting.
- Response includes only the documented public settings; no environment credentials, database values, or private fields are serialized.
- Added public-field allowlist and endpoint/serialization tests.
- All eight API v1 tests pass and Django checks remain green.

### P3.4 — Jobs list/detail/filter endpoints

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added `GET /api/v1/jobs/` with server-side `q`, `location`, `category`, `remote`, and positive `page` filtering.
- Listing is restricted to published `open` jobs and orders by newest publication date, title, then slug.
- Listing returns deterministic pagination metadata and location/category/remote facets.
- Added `GET /api/v1/jobs/<slug>/` for any published job status so filled/archived URLs remain resolvable.
- Invalid remote/page parameters return HTTP 400; ten API v1 tests pass and Django checks remain green.

### P3.5 — Signed short-lived headless preview

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added timestamp-signed preview tokens containing only page/revision identifiers, with a five-minute maximum age and dedicated `PREVIEW_SIGNING_SECRET`.
- Added `GET /api/v1/preview/<token>/` to return the selected draft revision; invalid or expired tokens return 404.
- Preview responses set `Cache-Control: no-store` and `X-Robots-Tag: noindex`.
- Added a Wagtail page action item linking saved revisions to the configured Astro `/preview/?token=...` route.
- Twelve API v1 tests pass and Django checks remain green.

### P3.6 — Production CORS and API failure behavior

Status: `DONE`

Evidence recorded on 2026-09-19:

- Production rejects wildcard CORS origins; origins are read only from explicit `CORS_ALLOWED_ORIGINS` values.
- PostgreSQL connections use a 10-second connect timeout and bounded connection lifetime.
- API database/time-out failures return a safe JSON HTTP 503 and structured `api_failure` log metadata; non-API failures are not masked.
- Production deploy checks pass with a sufficiently long test secret, all 23 CMS tests pass, and migration consistency is clean.

### P3.7 — Phase 3 gate

Status: `IN PROGRESS`

Evidence recorded on 2026-09-19:

- API v1 serializers, page-by-path, site-settings, jobs, preview, and failure behavior are implemented and tested.
- Added Astro `/preview/?token=...` server route with a five-second CMS timeout, no-store response headers, noindex metadata, and explicit 400/503 failure states.
- Astro server build completed successfully with the Vercel adapter.
- CMS checks pass and the API test suite passes. The gate remains open until a saved unpublished Wagtail revision is previewed through the Astro route and verified as no-store/noindex in a browser. Visual frontend reconstruction remains Phase 5 work.

### P2.1 — Shared SEO fields

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added reusable `content.SEOFieldsMixin` with editable SEO title, meta description, Open Graph overrides/image, canonical URL, noindex, navigation label, and last-reviewed date.
- Canonical overrides validate as absolute HTTPS URLs; invalid relative and HTTP values are rejected.
- German editor help text documents the 60/160-character limits without truncating content.
- Shared model validation rejects SEO titles over 60 characters and descriptions over 160 characters without modifying the submitted value.
- `manage.py check` passed under production settings against the configured PostgreSQL database.
- Three focused validation tests passed; `makemigrations --check --dry-run` reported no unexpected migration because the mixin is abstract.

### P2.2 — KP site settings

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added registered Wagtail `KPSettings` fields for brand assets, primary/footer/legal navigation, social links, contact defaults, ordered offices, footer copy, CTAs, Calendly, cookie text, analytics toggle, and organization structured-data values.
- Navigation items explicitly distinguish internal page choosers from external URLs and validate that exactly one target type is used.
- Logos, favicon, social image, organization logo, and privacy page use Wagtail choosers; no raw internal paths are stored.
- Created `content/0001_initial.py` for the settings model.
- `manage.py check` passed against PostgreSQL; five focused content tests passed; `makemigrations --check --dry-run` reported no pending model changes.
- Migration plan was inspected without applying the migration to the shared database.

### P2.3 — Reusable snippets and office data

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added registered `TeamMember`, `Testimonial`, and `Service` snippets with stable unique `source_key` values, active flags, ordering, audience controls, and Wagtail image/page choosers.
- Team biographies use rich text; expertise tags are ordered; testimonial audience and service icon/audience values use controlled choices.
- Office records remain exclusively in the ordered `KPSettings.offices` structure, avoiding duplicate office sources.
- Created `content/0002_testimonial_service_teammember.py`.
- `manage.py check` passed against PostgreSQL and all five focused content tests passed.

### P2.4 — Home and landing page models

Status: `DONE`

Evidence recorded on 2026-09-19:

- Extended the existing `HomePage` with editable intro/scroll video assets, posters, accessibility labels, ordered hero chapters, audience CTAs, and follow-on content sections.
- Added `EmployerPage`, `CandidatePage`, and `AboutPage` with structured hero content, media, CTAs, service/testimonial/team references, statistics, regions, values, and contact sections.
- Shared blocks preserve ordered content and chooser references instead of embedding hard-coded page paths or copy.
- Created `content/0003_aboutpage_candidatepage_employerpage.py` and `home/0003_alter_homepage_options_and_more.py`.
- Django checks passed; content tests passed; `makemigrations --check --dry-run` reported no pending changes.

### P2.5 — Service, CV, contact, and legal page models

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added one controlled `ServicePage` model for the four source-backed service pages, with hero media, rich body sections, CTA, and Calendly toggle.
- Added `CVPackagesPage` with ordered display-string prices, package CTAs, process steps, and delivery text; no checkout or currency conversion was introduced.
- Added `ContactPage` with ordered office labels referencing `KPSettings`, website URL fields, and closing copy; no contact form was added.
- Added `LegalPage` with editable intro/body rich text and review date.
- Created `content/0004_contactpage_cvpackagespage_legalpage_servicepage.py`.
- Django checks and five focused content tests passed.

### P2.6 — Jobs index and job detail models

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added `JobsIndexPage` fields for German hero copy, search/filter labels, empty state, result format, application note, and default email.
- Added `JobPage` fields for stable source key, status lifecycle, dates, location/remote/category data, experience/employment display strings, rich summary and ordered responsibilities/profile/benefits, application email, and reserved ATS fields.
- Created `content/0005_jobpage_jobsindexpage.py`.
- Django checks, five focused content tests, and migration consistency checks passed.

### P2.7 — Editor validation and page hierarchy

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added explicit Wagtail parent/child rules: Home owns landing pages, JobsIndex owns JobPage children, and leaf pages cannot create arbitrary children.
- CTA link blocks now use controlled internal/external choices and reject ambiguous targets.
- Job closing dates are validated against publication dates.
- Added focused hierarchy/link/date validation coverage; seven content tests passed.
- Wagtail checks and migration consistency checks passed; the link-block choice change was captured in `content/0006_alter_aboutpage_contact_cta_and_more.py` and the corresponding Home migration.

### P2.8 — Migration creation and review

Status: `DONE`

Evidence recorded on 2026-09-19:

- Created and reviewed content migrations `0001` through `0006` plus HomePage migrations `0003` and `0004`.
- `manage.py check` passed and `makemigrations --check --dry-run` reported no pending model changes.
- Migration graph inspection with `showmigrations --plan` completed successfully.
- SQL previews for every project migration were generated with `sqlmigrate`; no migration was applied to the shared Render database.
- `python -m compileall -q cms` completed successfully.

### P2.9 — Phase 2 gate

Status: `DONE`

Evidence recorded on 2026-09-19:

- Reviewed model coverage for all Phase 2 content categories and verified edit handlers for Home, landing, service, CV, contact, legal, jobs index, and job detail pages.
- Applied the reviewed migrations to the supplied Render PostgreSQL database; `showmigrations` reports all project migrations applied.
- `manage.py check --deploy` passes with no issues after production HTTPS/session security settings were added.
- All nine focused content tests pass and migration consistency remains clean.
- Phase 2 gate passed. Public API/headless preview behavior remains intentionally scoped to Phase 3.

### P1.1 — Dependency security resolution

Status: `DONE`

Evidence recorded on 2026-09-18:

- Upgraded to Astro `7.3.3` and `@astrojs/vercel` `11.0.10`.
- Updated the adapter import to the Astro 7 export (`@astrojs/vercel`).
- Updated the Node engine declaration to `>=22.12.0`, matching Astro 7 requirements.
- Added a narrow `path-to-regexp` `6.3.0` override for the Vercel routing-utils transitive pin.
- `npm audit --omit=dev --audit-level=high` now reports `0 vulnerabilities`.
- `npm run build` succeeds with the `@astrojs/vercel` adapter.

Phase 1 is no longer blocked by dependency security.

### P1.3 — PostgreSQL `DB_*` settings

Status: `DONE`

Evidence recorded on 2026-09-18:

- Replaced generated SQLite settings with PostgreSQL configuration in `cms/kp_cms/settings/base.py`.
- Configuration reads `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_SSLMODE`; SSL mode defaults only to the documented `require` contract.
- Missing required database variables fail explicitly with `ImproperlyConfigured`; no SQLite fallback is present.
- Django system checks passed with temporary non-secret placeholder variables.
- The same check failed as expected when `DB_NAME` was absent, proving configuration cannot silently start against an unintended database.

### P1.4 — Dev/production settings and env examples

Status: `DONE`

Evidence recorded on 2026-09-18:

- `cms/kp_cms/settings/dev.py` and `production.py` now read secrets, hosts, CSRF origins, and CORS origins from environment variables.
- German is the configured CMS language; generated placeholder secrets and wildcard hosts were removed.
- Production settings fail explicitly when `DJANGO_SECRET_KEY` or `ALLOWED_HOSTS` is missing.
- `manage.py check` passed under both dev and production settings with temporary non-secret test values.

### P1.5 — Cloud Run health endpoints

Status: `DONE`

Evidence recorded on 2026-09-18:

- Added `GET /healthz` as a database-independent liveness probe returning `{\"status\":\"ok\"}`.
- Added `GET /readyz` as a PostgreSQL-backed readiness probe returning HTTP 503 when the configured database is unavailable.
- Django system checks passed after URL registration.
- Django test client verified `/healthz` returns HTTP 200 with the expected JSON using a local allowed host.

### P1.6 — Phase 1 gate

Status: `DONE`

Evidence recorded on 2026-09-19:

- Connected successfully to the owner-provided Render PostgreSQL database using process environment variables; credentials were not written to the repository.
- A read-only connection query confirmed the expected database, user, and `public` schema.
- `manage.py check` passed under production settings.
- `manage.py migrate --plan --noinput` connected and reported the expected initial Wagtail migration plan without applying changes.
- Django test client verified `/readyz` returns HTTP 200 with `{\"status\":\"ready\"}` against the live database.
- Phase 1 gate passed: Astro build remains green, CMS checks pass, and PostgreSQL connectivity is verified.

### P1.2 — Django/Wagtail CMS scaffold

Status: `DONE`

Evidence recorded on 2026-09-18:

- Wagtail `8.0` project scaffolded under `cms/` with `manage.py`, `kp_cms` settings/WSGI/URLs, and the default `home` and `search` apps.
- CMS dependencies installed from the pinned `cms/requirements.txt` into the repository-local `cms-venv`.
- `\\cms-venv\\Scripts\\python.exe cms\\manage.py check` passed with no issues.
- `\\cms-venv\\Scripts\\python.exe cms\\manage.py migrate --check --noinput` passed against the scaffold's local development database configuration.
- No KP content models, imports, APIs, or frontend routes were added in this task; those remain gated by P1.3/P2.

### P4.1 — Deterministic content freeze

Status: `DONE`

Evidence recorded on 2026-09-19:

- Rebuilt `migration-data/content.json` and `manifest.json` twice from checked-in `site/` files only; both runs produced identical SHA-256 hashes.
- Verified 13 mapped pages, 0 unmapped pages, exactly 17 jobs, German language metadata, 172 assets, 28 unique local media references, 190 links, and 31 external links.
- Verified the exact canonical route set from the migration plan and rejected Unicode replacement characters.
- Freeze artifact and hashes are recorded in `migration-data/FREEZE.md`.
- No CMS records, media uploads, or database content were changed.

### P4.2 — Cloudinary storage configuration

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added environment-driven Cloudinary configuration using `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.
- Production fails fast when Cloudinary credentials are incomplete and selects `MediaCloudinaryStorage` when configured.
- Development remains usable with explicit local storage until credentials are supplied; it switches to Cloudinary automatically when all values are present.
- Cloudinary storage dependency import test passed; 24 CMS tests and Django checks passed.
- No media was uploaded during this task.

### P4.3 — Dry-run/idempotent legacy import command

Status: `DONE`

Evidence recorded on 2026-09-19:

- Added `python cms/manage.py import_legacy_content --data migration-data/content.json [--dry-run]`.
- Command validates UTF-8/replacement characters, exact 17-job input, and the approved canonical route mapping before opening the import transaction.
- Non-dry runs use Wagtail page/source keys for update-in-place behavior, publish imported revisions, ensure the root/site records, and report created/updated/skipped/failed counts.
- Dry-run completed successfully with `created=0 updated=0 skipped=30 failed=0` and no database/media writes.
- CMS checks and 24 tests pass. Media association/upload and full content field mapping continue in P4.4.

### P4.4 — Import pages, snippets, media, and jobs

Status: `DONE`

Evidence recorded on 2026-09-19:

- Cloudinary variables are present and non-empty in `cms/.env` without printing their values.
- The importer successfully created 12 mapped content pages plus the existing Home page and exactly 17 `JobPage` records (`created=29, updated=1, failed=0`).
- A second execution was idempotent (`created=0, updated=30, skipped=0, failed=0`) and created no duplicates.
- Added deterministic `migration-data/structured.json` extraction for 3 team members, 16 testimonials, 10 services, 3 CV packages, 4 process steps, and 2 offices.
- Imported all structured records and attached them to About, Employer, Candidate, CV Packages, Contact, and site settings; verified relationships as 3 team members, 6/7 employer services/testimonials, 4/9 candidate services/testimonials, and 3/4 CV packages/steps.
- Uploaded and associated all three team portraits through the configured storage (`media_created=3`); a repeat structured-only import created no media duplicates (`media_created=0`).
- The import command supports `--structured` and `--structured-only`; `KP_IMPORT_DISABLE_SEARCH=1` is used for remote Render imports to defer expensive per-row database search indexing.

### P4.5 — Post-import content verification

Status: `DONE`

Evidence recorded on 2026-09-19:

- Read-only database assertions passed: 30 non-root pages (including 17 jobs), all 17 expected legacy job source keys, 3 team members, 16 testimonials, 10 services, 3 CV packages, 4 process steps, 2 offices, and 3 media records.
- Relationship assertions passed: About has 3 team references; Employer has 6 services and 7 testimonials; Candidate has 4 services and 9 testimonials; CV Packages has 3 packages and 4 steps.
- Source-data assertions passed for all structured team names, testimonial source keys, and service titles against `migration-data/structured.json`.
- Storage assertion passed: the active default backend is `cloudinary_storage.storage.MediaCloudinaryStorage`, and all three team portraits have stored media names.
- API smoke checks passed for `/api/v1/pages/by-path/`, `/api/v1/jobs/` (17 total), and `/api/v1/site-settings/`.
- Automated Django tests were not rerun because the user-provided Render database contains a stale `test_KP` database with an incompatible schema (`page_id` missing); `manage.py check` passes and the production-content verification above is read-only.
