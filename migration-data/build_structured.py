"""Extract snippet/page structures from the checked-in legacy HTML.

This intentionally reads only the frozen ``site`` tree and emits deterministic
JSON.  It does not invent values; every field is taken from a visible source
element or a controlled mapping used by the CMS schema.
"""
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

def text(node):
    value = node.get_text(" ", strip=True) if node else ""
    parts = value.split()
    # Some legacy headings render each character in its own span.  Preserve
    # normal word spacing while joining only genuinely character-split text.
    if len(parts) > 8 and sum(len(part) == 1 for part in parts) / len(parts) > 0.75:
        return "".join(parts)
    return value

def rich(value):
    return f"<p>{value}</p>" if value else ""

def page_extract(filename, hero_image=""):
    soup = BeautifulSoup((SITE / filename).read_text(encoding="utf-8"), "html.parser")
    frozen_path = ROOT / "migration-data" / "content.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8")) if frozen_path.exists() else {}
    frozen_page = next((item for item in frozen.get("pages", []) if item.get("source_file") == f"site/{filename}"), None)
    if frozen_page:
        frozen_headings = frozen_page.get("headings", [])
        headings = [item.get("text", "") for item in frozen_headings if item.get("text")]
        eyebrow = next((item.get("text", "") for item in frozen_headings if item.get("tag") == "h6"), "")
        hero_heading = next((item.get("text", "") for item in frozen_headings if item.get("tag") == "h4"), None) or next((item.get("text", "") for item in frozen_headings if item.get("tag") in {"h1", "h2"}), headings[0] if headings else "")
        paragraphs = [item for item in frozen_page.get("paragraphs", []) if item and not item.startswith("©")]
        return {"hero_eyebrow": eyebrow, "hero_heading": hero_heading, "hero_text": rich(paragraphs[0]) if paragraphs else "", "hero_background_src": hero_image, "paragraphs": paragraphs, "headings": headings}
    eyebrow = text(soup.select_one(".kpa-hero-row h6, .fancy-title h6"))
    headings = [text(x) for x in soup.select("h1, h2, h3, h4, h5") if text(x)]
    hero_heading = next((x for x in headings if x != eyebrow), headings[0] if headings else "")
    paragraphs = [text(x) for x in soup.select("p") if text(x) and not text(x).startswith("©")]
    return {
        "hero_eyebrow": eyebrow,
        "hero_heading": hero_heading,
        "hero_text": rich(paragraphs[0]) if paragraphs else "",
        "hero_background_src": hero_image,
        "paragraphs": paragraphs,
        "headings": headings,
    }

def main():
    index = BeautifulSoup((SITE / "index.html").read_text(encoding="utf-8"), "html.parser")
    home_headings = [text(x) for x in index.select("h4, h5") if text(x)]
    home_ctas = [{"label": text(a), "href": a.get("href", "")} for a in index.select("a") if text(a) in {"Ich bin Arbeitgeber", "Ich bin Kandidat:in"}]
    home = {"headings": home_headings, "ctas": home_ctas, "logo_src": "assets/logo.png", "compact_logo_src": "assets/logo-mark.png", "favicon_src": "favicon.svg",
            "intro_video_src": next((x.get("src") for x in index.select("video source") if x.get("src")), "")}
    about = BeautifulSoup((SITE / "about-us.html").read_text(encoding="utf-8"), "html.parser")
    team = []
    for card in about.select(".kpa-sticky-card"):
        name = text(card.select_one(".kpa-sticky-card__name"))
        team.append({
            "source_key": "legacy-team-" + name.lower().replace(" ", "-"),
            "name": name,
            "role": text(card.select_one(".kpa-sticky-card__role")),
            "biography": "".join(rich(text(p)) for p in card.select(".kpa-sticky-card__bio p")),
            "expertise_tags": [text(x) for x in card.select(".kpa-sticky-card__tags span")],
            "portrait_src": (card.select_one(".kpa-sticky-card__img img") or {}).get("src", ""),
        })

    services = []
    icon_by_title = {
        "Executive Search": "search",
        "Volumen- & Projektbesetzung": "people",
        "HR Advisory": "chart",
        "Employer Branding": "people",
        "Internationale Rekrutierung": "globe",
        "Eignungsdiagnostik": "chart",
        "Stellen entdecken": "search",
        "Unser Kandidaten-Netzwerk": "people",
        "Karriere-Services": "document",
    }
    for filename, audience in (("employers.html", "employer"), ("candidates.html", "candidate")):
        soup = BeautifulSoup((SITE / filename).read_text(encoding="utf-8"), "html.parser")
        for order, card in enumerate(soup.select(".kp-svc")):
            title = text(card.select_one("h3"))
            description = text(card.select_one("p"))
            key = "legacy-service-" + audience + "-" + title.lower().replace(" ", "-").replace("&", "and")
            services.append({"source_key": key, "title": title, "short_description": description,
                             "audience": audience, "display_order": order,
                             "icon_identifier": icon_by_title.get(title, "briefcase")})

    testimonials = []
    for filename, audience in (("employers.html", "employer"), ("candidates.html", "candidate")):
        soup = BeautifulSoup((SITE / filename).read_text(encoding="utf-8"), "html.parser")
        for order, item in enumerate(soup.select(".testimonial")):
            details = item.select(".testimonial-details h5, .testimonial-details h6")
            quote = text(item.select_one("blockquote"))
            # The legacy page contains decorative quote marks; keep the actual text.
            quote = quote.strip("\u00ab\u00bb\" ")
            testimonials.append({"source_key": f"legacy-testimonial-{audience}-{order+1}",
                                 "quote": quote, "person_label": text(details[0]) if details else "",
                                 "organization": text(details[1]) if len(details) > 1 else "",
                                 "audience": audience, "display_order": order})

    cv = BeautifulSoup((SITE / "cv-writing-packages.html").read_text(encoding="utf-8"), "html.parser")
    packages = []
    for card in cv.select(".pricing-table"):
        price = text(card.select_one(".pricing"))
        experience = text(card.select_one(".pricing-table-header h5"))
        body = [text(x) for x in card.select(".pricing-table-body li, .pricing-table-body p") if text(x)]
        packages.append({"name": text(card.select_one(".pricing-table-header h5")),
                         "price_display": price, "experience_range": experience,
                         "description": "".join(rich(x) for x in body),
                         "cta_label": text(card.select_one(".pricing-table-footer .btn-txt"))})
    steps = [{"heading": text(x.select_one("h3")), "text": rich(text(x.select_one("p")))}
             for x in cv.select(".ld-pb")]

    contact = BeautifulSoup((SITE / "contact.html").read_text(encoding="utf-8"), "html.parser")
    full = text(contact)
    offices = [
        {"label": "Standort Mannheim", "street": "Bellenstraße 50", "postal_code": "68163", "city": "Mannheim", "telephone": "+49 160 90 678 718", "email": "m.opper@kastellpersonalberatung.com"},
        {"label": "Standort Wiesbaden", "street": "Herderstraße 23", "postal_code": "65185", "city": "Wiesbaden", "telephone": "+49 152 08904616", "email": "b.hadjistojanov@kastellpersonalberatung.com"},
    ]

    pages = {
        "/arbeitgeber/": page_extract("employers.html", "wp-content/uploads/2019/12/bg-banner-2-4-scaled.jpg"),
        "/kandidaten/": page_extract("candidates.html"),
        "/ueber-uns/": page_extract("about-us.html", "wp-content/uploads/2019/12/bg-banner-1-3-scaled.jpg"),
        "/kontakt/": page_extract("contact.html", "wp-content/uploads/2019/12/bg-contact-scaled.jpg"),
        "/leistungen/eignungsdiagnostik/": page_extract("assessments.html"),
        "/leistungen/internationale-rekrutierung/": page_extract("bg-global-recruitment.html"),
        "/leistungen/volumen-projektbesetzung/": page_extract("contingency-multiple-hiring.html"),
        "/leistungen/employer-branding/": page_extract("world-connect.html"),
        "/karriere-services/bewerbungsunterlagen/": page_extract("cv-writing-packages.html"),
        "/datenschutz/": page_extract("privacy-policy-2.html"),
        "/nutzungsbedingungen/": page_extract("terms-of-use.html"),
    }
    candidate = pages["/kandidaten/"]
    candidate.update({
        "hero_text": "",
        "show_hero": False,
        "services_eyebrow": "LEISTUNGEN FÜR KANDIDAT:INNEN",
        "services_heading": "Entdecken Sie, was Kastell Personalberatung für Sie tun kann.",
        "testimonials_eyebrow": "STIMMEN VON KANDIDAT:INNEN",
        "show_testimonial_content": False,
        "testimonials_background_src": "wp-content/uploads/2019/12/BG-TESTIMONIALS2.jpg",
        "career_image_src": "wp-content/uploads/2019/12/34w.jpg",
        "career_heading": "Starten Sie noch heute Ihre Jobsuche!",
        "career_copy": rich("We believe most human interactions are not black & white – there are no right answers or standard recruitment processes that will hold true for all situations. Talented people have wonderful variables and aspirations at every stage of their career. To strike the right balance and effectively manage the grey areas of recruitment, we invest time and follow a humanized yet progressive recruitment and selection process that redefines the way you look at ‘experience’ in the recruitment process.") + rich("We are recruiting for DAX-Konzern’s, leading local organizations, small and medium-sized enterprises in Deutschland."),
        "contact_background_src": "wp-content/uploads/2019/12/bg-contact-scaled.jpg",
        "contact_heading": "Kastell Personalberatung",
        "contact_details": "<p>Mannheim &amp; Wiesbaden, Deutschland<br>+49 160 90 678 718<br>kontakt@kastellpersonalberatung.com<br>www.kastellpersonalberatung.com</p>",
    })
    employer = BeautifulSoup((SITE / "employers.html").read_text(encoding="utf-8"), "html.parser")
    why_section = next((section for section in employer.select("section") if "WARUM KASTELL" in text(section)), None)
    why_items = []
    if why_section:
        for figure in why_section.select("figure"):
            image = figure.select_one("img")
            caption = text(figure.select_one("figcaption"))
            if caption and image:
                why_items.append({"heading": caption, "body": "", "image_src": image.get("src", "")})
    pages["/arbeitgeber/"].update({
        # The production desktop hero contains only the heading. The first
        # paragraph in the generic extraction belongs to the services grid.
        "hero_text": "",
        "services_eyebrow": "UNSERE LEISTUNGEN",
        "services_heading": "Passgenaue Besetzung – fachlich, persönlich und kulturell.",
        "why_eyebrow": "WARUM KASTELL?",
        "why_heading": "Passgenaue Besetzung – fachlich, persönlich und kulturell.",
        "why_items": why_items,
        "testimonials_eyebrow": "KUNDENSTIMMEN",
        "show_testimonial_content": False,
        "testimonials_background_src": "wp-content/uploads/2019/12/BG-TESTIMONIALS2.jpg",
        "recruitment_region_heading": "Regionen, aus denen wir rekrutieren",
        "recruitment_region_copy": rich("Wir rekrutieren bundesweit und sprechen Spezialist:innen auch international an – mit tiefem Verständnis für den deutschen Fachkräftemarkt."),
        "recruitment_region_image_src": "wp-content/uploads/2019/12/map-bg.jpg",
        "recruitment_regions": ["Rhein-Neckar", "Rhein-Main", "Baden-Württemberg", "Hessen", "Bayern", "Bundesweit"],
        "closing_eyebrow": "LET'S MAKE THIS WORK",
        "closing_heading": "Sprechen wir darüber, wie wir Ihr Unternehmen dabei unterstützen, die richtigen Fachkräfte zu gewinnen.",
        "closing_copy": rich("Vereinbaren Sie ein Gespräch mit unseren Berater:innen."),
        "closing_background_src": "wp-content/uploads/2019/03/banner-cta-scaled.jpg",
        "calendly_cta_label": "Persönlich / Telefon / Video",
    })
    payload = {"schema_version": 1, "home": home, "pages": pages, "team_members": team, "services": services,
               "testimonials": testimonials, "cv_packages": packages, "cv_steps": steps,
               "office_text": offices}
    out = ROOT / "migration-data" / "structured.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
