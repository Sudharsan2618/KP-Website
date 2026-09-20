"""Build deterministic Phase 0 inventory artifacts from the checked-in KP mirror.

This script reads only the repository's checked-in HTML/JS/assets. It does not
call the network and does not make CMS or database changes.
"""
from __future__ import annotations

import ast
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUT = ROOT / "migration-data"

URL_MAP = {
    "index.html": "/",
    "employers.html": "/arbeitgeber/",
    "candidates.html": "/kandidaten/",
    "about-us.html": "/ueber-uns/",
    "contact.html": "/kontakt/",
    "projekte.html": "/projekte/",
    "assessments.html": "/leistungen/eignungsdiagnostik/",
    "bg-global-recruitment.html": "/leistungen/internationale-rekrutierung/",
    "contingency-multiple-hiring.html": "/leistungen/volumen-projektbesetzung/",
    "world-connect.html": "/leistungen/employer-branding/",
    "cv-writing-packages.html": "/karriere-services/bewerbungsunterlagen/",
    "privacy-policy-2.html": "/datenschutz/",
    "terms-of-use.html": "/nutzungsbedingungen/",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta_description = ""
        self.in_title = False
        self.skip_depth = 0
        self.current_tag: str | None = None
        self.current_text: list[str] = []
        self.headings: list[dict[str, str]] = []
        self.paragraphs: list[str] = []
        self.links: list[dict[str, str]] = []
        self.media: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
        if tag == "meta" and values.get("name", "").lower() == "description":
            self.meta_description = values.get("content", "") or ""
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li"}:
            self.current_tag = tag
            self.current_text = []
        if tag == "a" and values.get("href"):
            self.links.append({"href": html.unescape(values["href"] or ""), "text": ""})
            self.current_tag = "a"
            self.current_text = []
        if tag in {"img", "video", "source"}:
            for key in ("src", "poster", "data-src", "data-lazy-src"):
                if values.get(key):
                    self.media.append({"kind": tag, "attribute": key, "src": html.unescape(values[key] or "")})

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        text = " ".join("".join(self.current_text).split())
        if self.in_title and tag == "title":
            self.title = text
            self.in_title = False
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and text:
            self.headings.append({"tag": tag, "text": text})
        elif tag in {"p", "li"} and text:
            self.paragraphs.append(text)
        elif tag == "a" and self.links:
            self.links[-1]["text"] = text
        if tag == self.current_tag:
            self.current_tag = None
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.current_tag:
            self.current_text.append(data)


def rel_asset(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def classify_link(href: str) -> str:
    if href.startswith(("mailto:", "tel:", "https://", "http://")):
        return "external"
    if href.startswith(("#", "javascript:")):
        return "fragment-or-script"
    return "internal-or-relative"


def extract_jobs() -> list[dict[str, object]]:
    source = (SITE / "local-fixes.js").read_text(encoding="utf-8", errors="strict")
    match = re.search(r"var JOBS = \[(.*?)\n  \];", source, re.S)
    if not match:
        raise RuntimeError("JOBS array was not found")
    records: list[dict[str, object]] = []
    for index, raw in enumerate(re.findall(r"\{(.*?)\}", match.group(1), re.S), start=1):
        fields: dict[str, object] = {}
        for key, value in re.findall(r"(\w+):\s*([^,]+)", raw):
            value = html.unescape(value.strip().strip("'\""))
            if value in {"true", "false"}:
                fields[key] = value == "true"
            else:
                fields[key] = value
        title = str(fields.get("t", ""))
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower(), flags=re.I).strip("-") or f"job-{index}"
        records.append({"source_key": f"legacy-job-{index:02d}", "slug": slug, **fields})
    if len(records) != 17:
        raise RuntimeError(f"Expected 17 jobs, found {len(records)}")
    return records


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pages: list[dict[str, object]] = []
    all_links: list[dict[str, str]] = []
    all_media: dict[str, dict[str, object]] = {}
    for path in sorted(SITE.glob("*.html")):
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8", errors="strict"))
        record = {
            "source_file": path.relative_to(ROOT).as_posix(),
            "source_slug": path.stem,
            "canonical_path": URL_MAP.get(path.name),
            "title": parser.title,
            "meta_description": parser.meta_description,
            "headings": parser.headings,
            "paragraphs": parser.paragraphs,
            "links": [{**link, "kind": classify_link(link["href"])} for link in parser.links],
            "media": parser.media,
        }
        pages.append(record)
        all_links.extend({"page": path.name, **link} for link in record["links"])
        for media in parser.media:
            if media["src"].startswith(("http://", "https://", "//", "data:")):
                continue
            candidate = (SITE / media["src"].split("?", 1)[0].lstrip("/"))
            if candidate.exists() and candidate.is_file():
                all_media[media["src"]] = rel_asset(candidate)

    assets = [rel_asset(path) for path in sorted(SITE.rglob("*")) if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg", ".mp4", ".webm", ".woff", ".woff2", ".ttf", ".otf"}]
    jobs = extract_jobs()
    content = {
        "schema_version": 1,
        "source_commit": "5938e76da55ba9acc06d4fd0b1908b76e664c46d",
        "language": "de",
        "pages": pages,
        "jobs": jobs,
    }
    manifest = {
        "schema_version": 1,
        "source_commit": content["source_commit"],
        "source_pages": len(pages),
        "mapped_pages": sum(1 for page in pages if page["canonical_path"] is not None),
        "unmapped_pages": [page["source_file"] for page in pages if page["canonical_path"] is None],
        "job_count": len(jobs),
        "job_source_keys": [job["source_key"] for job in jobs],
        "link_count": len(all_links),
        "external_link_count": sum(1 for link in all_links if link["kind"] == "external"),
        "media_reference_count": sum(len(page["media"]) for page in pages),
        "unique_local_media_count": len(all_media),
        "asset_count": len(assets),
        "assets": assets,
        "pages": [{"source_file": page["source_file"], "canonical_path": page["canonical_path"], "title": page["title"], "heading_count": len(page["headings"]), "paragraph_count": len(page["paragraphs"]), "link_count": len(page["links"]), "media_count": len(page["media"])} for page in pages],
    }
    (OUT / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(pages), "jobs": len(jobs), "assets": len(assets), "links": len(all_links), "media": len(all_media)}, indent=2))


if __name__ == "__main__":
    main()

