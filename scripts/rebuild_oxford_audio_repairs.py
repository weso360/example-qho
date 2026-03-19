#!/usr/bin/env python3
import html
import json
import re
import shutil
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "Main Files" / "HTML"
OUTPUT_DIR = ROOT / "oxford-audio-rebuild"
SITE_NAME = "Oxford Audio Repairs"
SITE_TAGLINE = "Repair, don't discard!"
BASE_API = "https://www.oxfordaudiorepair.com/wp-json/wp/v2"


PAGES = [
    {
        "endpoint": f"{BASE_API}/pages/7?_fields=id,slug,title,content,excerpt",
        "filename": "index.html",
        "nav_slug": "home",
        "title": "Home",
        "kind": "home",
        "hero_kicker": "Repair of Audio Equipment",
        "hero_title": "Expert repair for hi-fi, turntables, speakers, headphones, and more",
        "hero_text": (
            "Oxford Audio Repairs restores a wide range of audio equipment for customers in "
            "Kidlington, Oxford, and beyond."
        ),
    },
    {
        "endpoint": f"{BASE_API}/pages?slug=more-photos&_fields=id,slug,title,content,excerpt",
        "filename": "more-photos.html",
        "nav_slug": "more-photos",
        "title": "More Photos",
        "kind": "gallery",
        "hero_kicker": "Gallery",
        "hero_title": "More repair photos",
        "hero_text": "A larger gallery of repair, restoration, and diagnostic work.",
    },
    {
        "endpoint": f"{BASE_API}/pages?slug=contact-us&_fields=id,slug,title,content,excerpt",
        "filename": "contact-us.html",
        "nav_slug": "contact-us",
        "title": "Contact Us",
        "kind": "contact",
        "hero_kicker": "Contact",
        "hero_title": "Get in touch about your equipment",
        "hero_text": "Share the make, model, and fault details and you can discuss next steps.",
    },
    {
        "endpoint": f"{BASE_API}/pages?slug=electronic-waste&_fields=id,slug,title,content,excerpt",
        "filename": "electronic-waste.html",
        "nav_slug": "electronic-waste",
        "title": "Electronic Waste",
        "kind": "content",
        "hero_kicker": "Repair Culture",
        "hero_title": "About electronic waste and repairs",
        "hero_text": "Useful links about e-waste and the right to repair.",
    },
]


PAGE_LINK_MAP = {
    "/": "index.html",
    "/contact-us": "contact-us.html",
    "/contact-us/": "contact-us.html",
    "/more-photos": "more-photos.html",
    "/more-photos/": "more-photos.html",
    "/oxford-audio-repairs/electronic-waste": "electronic-waste.html",
    "/oxford-audio-repairs/electronic-waste/": "electronic-waste.html",
}


SITE_CSS = """
:root {
  --bg: #f4efe7;
  --surface: #fffdf9;
  --surface-strong: #fffaf2;
  --ink: #1b1814;
  --muted: #5f584f;
  --line: #dfd2bf;
  --brand: #8a4b17;
  --brand-deep: #5b2f10;
  --accent: #d9b27b;
  --shadow: 0 24px 60px rgba(33, 23, 11, 0.12);
}

* {
  box-sizing: border-box;
}

body.site-body {
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(217, 178, 123, 0.28), transparent 32%),
    linear-gradient(180deg, #fbf7f0 0%, var(--bg) 50%, #efe4d3 100%);
  font-family: Georgia, "Times New Roman", serif;
}

a {
  color: var(--brand-deep);
}

a:hover,
a:focus {
  color: var(--brand);
  text-decoration: none;
}

.site-shell {
  position: relative;
  overflow-x: hidden;
}

.site-header {
  padding: 18px 0;
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(12px);
  background: rgba(251, 247, 240, 0.88);
  border-bottom: 1px solid rgba(138, 75, 23, 0.12);
}

.site-brand {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--ink);
}

.site-tagline {
  margin: 2px 0 0;
  color: var(--muted);
  font-size: 0.92rem;
}

.site-nav {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
  margin-top: 8px;
}

.site-nav a {
  padding: 10px 14px;
  border-radius: 999px;
  color: var(--ink);
  font-size: 0.95rem;
}

.site-nav a.is-active,
.site-nav a:hover {
  background: rgba(138, 75, 23, 0.12);
}

.hero {
  padding: 76px 0 36px;
}

.hero-card,
.content-card,
.gallery-card,
.contact-card,
.info-card,
.link-card {
  background: rgba(255, 253, 249, 0.94);
  border: 1px solid rgba(138, 75, 23, 0.13);
  box-shadow: var(--shadow);
  border-radius: 28px;
}

.hero-card {
  padding: 40px;
}

.hero-kicker {
  display: inline-block;
  margin-bottom: 14px;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(138, 75, 23, 0.1);
  color: var(--brand-deep);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0 0 16px;
  font-size: clamp(2.6rem, 5vw, 4.8rem);
  line-height: 0.95;
}

.hero p {
  color: var(--muted);
  font-size: 1.08rem;
  line-height: 1.7;
  max-width: 760px;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.btn-cta,
.btn-secondary {
  display: inline-block;
  padding: 13px 22px;
  border-radius: 999px;
  border: 1px solid transparent;
  font-weight: 700;
}

.btn-cta {
  background: var(--brand);
  color: #fff8f0;
}

.btn-cta:hover,
.btn-cta:focus {
  color: #fff8f0;
  background: var(--brand-deep);
}

.btn-secondary {
  border-color: rgba(138, 75, 23, 0.25);
  background: transparent;
  color: var(--ink);
}

.page-section {
  padding: 14px 0 42px;
}

.content-card,
.gallery-card,
.contact-card {
  padding: 32px;
}

.page-intro {
  margin-bottom: 26px;
}

.page-intro h2 {
  margin: 0 0 8px;
  font-size: 2rem;
}

.page-intro p {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.content-body {
  color: var(--ink);
}

.content-body > *:first-child {
  margin-top: 0 !important;
}

.content-body > *:last-child {
  margin-bottom: 0 !important;
}

.content-body h3,
.content-body h4 {
  margin: 28px 0 12px;
  line-height: 1.25;
}

.content-body p,
.content-body li {
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.8;
}

.content-body ul {
  padding-left: 20px;
}

.content-body .wp-block-gallery,
.content-body .is-layout-flex,
.home-grid,
.photo-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 20px 0 26px;
}

.content-body .wp-block-image,
.home-grid figure,
.photo-grid figure {
  margin: 0;
}

.content-body img,
.home-grid img,
.photo-grid img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 18px;
  background: #efe2d0;
}

.content-body .wp-block-columns {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 28px;
}

.content-body .wp-block-column {
  padding: 22px;
  border-radius: 20px;
  background: var(--surface-strong);
  border: 1px solid var(--line);
}

.content-body .wp-block-buttons {
  margin: 26px 0;
}

.content-body .wp-block-button__link {
  display: inline-block;
  padding: 12px 22px;
  border-radius: 999px;
  background: var(--brand);
  color: #fff8f0;
  font-weight: 700;
}

.photo-grid {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.photo-grid figure a {
  display: block;
}

.photo-grid figcaption {
  padding: 10px 4px 0;
  color: var(--muted);
  font-size: 0.92rem;
  line-height: 1.5;
}

.contact-layout {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 20px;
}

.info-card,
.link-card {
  padding: 24px;
  height: 100%;
}

.info-card h3,
.link-card h3 {
  margin-top: 0;
}

.contact-form {
  display: grid;
  gap: 16px;
}

.contact-form label {
  display: block;
  font-size: 0.92rem;
  font-weight: 700;
  margin-bottom: 6px;
}

.contact-form input,
.contact-form textarea {
  width: 100%;
  border: 1px solid rgba(95, 88, 79, 0.24);
  border-radius: 16px;
  background: #fff;
  padding: 14px 16px;
  color: var(--ink);
  font: inherit;
}

.contact-form textarea {
  min-height: 180px;
  resize: vertical;
}

.contact-note {
  margin: 0;
  color: var(--muted);
  font-size: 0.92rem;
}

.site-footer {
  padding: 28px 0 40px;
  color: var(--muted);
}

.site-footer .footer-card {
  padding: 24px 28px;
  border-radius: 24px;
  border: 1px solid rgba(138, 75, 23, 0.12);
  background: rgba(255, 252, 245, 0.9);
}

@media (max-width: 1199px) {
  .content-body .wp-block-gallery,
  .photo-grid,
  .home-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 991px) {
  .site-nav {
    justify-content: flex-start;
  }

  .contact-layout,
  .content-body .wp-block-columns {
    grid-template-columns: 1fr;
  }

  .content-body .wp-block-gallery,
  .photo-grid,
  .home-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 575px) {
  .hero-card,
  .content-card,
  .gallery-card,
  .contact-card {
    padding: 22px;
    border-radius: 22px;
  }

  .hero {
    padding-top: 44px;
  }

  .hero h1 {
    font-size: 2.4rem;
  }

  .content-body .wp-block-gallery,
  .photo-grid,
  .home-grid {
    grid-template-columns: 1fr;
  }
}
"""


class FooGalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attr_map = dict(attrs)
        classes = attr_map.get("class", "")
        if "fg-thumb" not in classes:
            return
        href = attr_map.get("href")
        if not href:
            return
        self.items.append(
            {
                "href": href,
                "title": html.unescape(attr_map.get("data-caption-title", "")).strip(),
                "desc": html.unescape(attr_map.get("data-caption-desc", "")).strip(),
            }
        )


def fetch_json(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_page(page):
    data = fetch_json(page["endpoint"])
    if isinstance(data, list):
        if not data:
            raise RuntimeError(f"No data returned for {page['endpoint']}")
        return data[0]
    return data


def ensure_output_dirs():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "css").mkdir(parents=True)
    (OUTPUT_DIR / "fonts").mkdir(parents=True)
    (OUTPUT_DIR / "images" / "oxford").mkdir(parents=True)


def copy_template_assets():
    shutil.copy2(TEMPLATE_DIR / "css" / "bootstrap.min.css", OUTPUT_DIR / "css" / "bootstrap.min.css")
    shutil.copy2(TEMPLATE_DIR / "css" / "font-awesome.min.css", OUTPUT_DIR / "css" / "font-awesome.min.css")
    shutil.copy2(TEMPLATE_DIR / "favicon.png", OUTPUT_DIR / "favicon.png")
    shutil.copytree(TEMPLATE_DIR / "fonts", OUTPUT_DIR / "fonts", dirs_exist_ok=True)
    (OUTPUT_DIR / "css" / "site.css").write_text(SITE_CSS.strip() + "\n", encoding="utf-8")


def normalise_url(url):
    return (
        url.replace("https://testsite.oxfordaudiorepair.com", "https://www.oxfordaudiorepair.com")
        .replace("http://testsite.oxfordaudiorepair.com", "https://www.oxfordaudiorepair.com")
        .replace("http://www.oxfordaudiorepair.com", "https://www.oxfordaudiorepair.com")
    )


def slugify_filename(url):
    path = urlparse(url).path
    name = Path(path).name
    return re.sub(r"[^A-Za-z0-9._-]", "-", name) or "asset"


def download_asset(url, asset_map):
    url = normalise_url(url)
    if url in asset_map:
        return asset_map[url]
    filename = slugify_filename(url)
    target = OUTPUT_DIR / "images" / "oxford" / filename
    counter = 1
    while target.exists():
        stem = target.stem
        suffix = target.suffix
        target = OUTPUT_DIR / "images" / "oxford" / f"{stem}-{counter}{suffix}"
        counter += 1
    last_error = None
    for attempt in range(4):
        try:
            urllib.request.urlretrieve(url, target)
            break
        except Exception as exc:
            last_error = exc
            if target.exists():
                target.unlink()
            if attempt == 3:
                raise
            time.sleep(1.2 * (attempt + 1))
    if last_error and not target.exists():
        raise last_error
    rel_path = f"images/oxford/{target.name}"
    asset_map[url] = rel_path
    return rel_path


def localise_images(raw_html, asset_map):
    raw_html = normalise_url(raw_html)
    urls = sorted(set(re.findall(r"https://(?:www|testsite)\.oxfordaudiorepair\.com/wp-content/uploads/[^\"' )>]+", raw_html)))
    updated = raw_html
    for url in urls:
        local = download_asset(url, asset_map)
        updated = updated.replace(url, local)
        updated = updated.replace(normalise_url(url), local)
    return updated


def relink_pages(raw_html):
    updated = raw_html
    replacements = {
        "https://www.oxfordaudiorepair.com/contact-us/": "contact-us.html",
        "https://www.oxfordaudiorepair.com/more-photos/": "more-photos.html",
        "https://www.oxfordaudiorepair.com/oxford-audio-repairs/electronic-waste/": "electronic-waste.html",
        "/contact-us": "contact-us.html",
        "/contact-us/": "contact-us.html",
        "/more-photos": "more-photos.html",
        "/more-photos/": "more-photos.html",
        "/oxford-audio-repairs/electronic-waste": "electronic-waste.html",
        "/oxford-audio-repairs/electronic-waste/": "electronic-waste.html",
    }
    for source, target in replacements.items():
        updated = updated.replace(source, target)
    return updated


def cleanup_html(raw_html):
    updated = raw_html
    updated = updated.replace("\r", "")
    updated = re.sub(r"<style.*?</style>", "", updated, flags=re.DOTALL)
    updated = re.sub(r'\sstyle="[^"]*"', "", updated)
    updated = re.sub(r"\sdata-[a-zA-Z0-9_-]+=\"[^\"]*\"", "", updated)
    updated = re.sub(r"\saria-hidden=\"true\"", "", updated)
    updated = re.sub(r"\sclass=\"[^\"]*wp-container[^\"]*\"", "", updated)
    updated = updated.replace("wp-block-group alignfull", "content-group")
    updated = updated.replace("wp-block-group", "content-group")
    updated = updated.replace("has-global-padding", "")
    updated = updated.replace("is-layout-constrained", "")
    updated = updated.replace("wp-block-heading", "")
    updated = updated.replace("has-text-align-center", "text-center")
    updated = updated.replace("has-text-align-left", "text-left")
    updated = updated.replace("has-body-font-family", "")
    updated = updated.replace("has-medium-font-size", "")
    updated = updated.replace("is-style-asterisk", "")
    updated = updated.replace("wp-block-spacer", "content-spacer")
    updated = re.sub(r'\sclass="\s+"', "", updated)
    updated = re.sub(r"\n{3,}", "\n\n", updated)
    return updated.strip()


def build_more_photos(content_html, asset_map):
    parser = FooGalleryParser()
    parser.feed(content_html)
    figures = []
    for item in parser.items:
        full = download_asset(item["href"], asset_map)
        caption = " ".join(part for part in [item["title"], item["desc"]] if part).strip()
        caption_html = f"<figcaption>{html.escape(caption)}</figcaption>" if caption else ""
        figures.append(
            f"""
            <figure>
              <a href="{full}" target="_blank" rel="noopener noreferrer">
                <img src="{full}" alt="{html.escape(item['title'] or 'Repair photo')}">
              </a>
              {caption_html}
            </figure>
            """.strip()
        )
    return '<div class="photo-grid">\n' + "\n".join(figures) + "\n</div>"


def extract_contact_intro(content_html):
    match = re.search(r'<div class="wpforms-description">(.*?)</div>', content_html, re.DOTALL)
    if not match:
        return ""
    intro = match.group(1)
    intro = intro.replace("<br><br>", "\n\n")
    intro = intro.replace("<br>", " ")
    intro = re.sub(r"</?i>", "", intro)
    intro = re.sub(r"</?b>", "", intro)
    intro = re.sub(r"<[^>]+>", "", intro)
    chunks = [html.unescape(chunk).strip() for chunk in intro.split("\n\n")]
    chunks = [chunk for chunk in chunks if chunk]
    return "\n".join(f"<p>{html.escape(chunk)}</p>" for chunk in chunks)


def build_contact_page(content_html):
    intro_html = extract_contact_intro(content_html)
    return f"""
    <div class="contact-layout">
      <div class="info-card">
        <h3>Before you send your details</h3>
        <div class="content-body">
          {intro_html}
        </div>
      </div>
      <div class="info-card">
        <h3>Location</h3>
        <p>Oxford Audio Repairs is in Kidlington, OX5 2EQ, near Oxford, UK.</p>
        <p>Detailed information is shared once an appointment has been arranged.</p>
      </div>
    </div>
    <div style="height:20px"></div>
    <div class="contact-card">
      <div class="page-intro">
        <h2>Contact form</h2>
        <p>
          This rebuild keeps the form layout from the live site. The original site uses a WordPress
          form backend, so submissions are not wired up in this static version yet.
        </p>
      </div>
      <form class="contact-form">
        <div class="row">
          <div class="col-sm-6">
            <label for="first-name">First name</label>
            <input id="first-name" type="text" placeholder="First">
          </div>
          <div class="col-sm-6">
            <label for="last-name">Last name</label>
            <input id="last-name" type="text" placeholder="Last">
          </div>
        </div>
        <div>
          <label for="email">Email</label>
          <input id="email" type="email" placeholder="Take care to enter correct address">
        </div>
        <div>
          <label for="telephone">Telephone number</label>
          <input id="telephone" type="text" placeholder="Enter your full phone number here">
        </div>
        <div>
          <label for="devices">Devices: makes and models</label>
          <input id="devices" type="text" placeholder="If more than one, list them comma-separated">
        </div>
        <div>
          <label for="issues">Description of the issues</label>
          <textarea id="issues" placeholder="Please describe the faults"></textarea>
        </div>
        <p class="contact-note">
          Static preview only. If you want, the next step can be wiring this to a real form endpoint.
        </p>
        <div>
          <button class="btn-cta" type="button">Submit</button>
        </div>
      </form>
    </div>
    """.strip()


def build_navigation(active_slug):
    items = [
        ("Home", "index.html", "home"),
        ("More Photos", "more-photos.html", "more-photos"),
        ("Contact Us", "contact-us.html", "contact-us"),
        ("About E-Waste", "electronic-waste.html", "electronic-waste"),
    ]
    links = []
    for label, href, slug in items:
        active = " is-active" if slug == active_slug else ""
        links.append(f'<a class="{active.strip()}" href="{href}">{label}</a>' if active else f'<a href="{href}">{label}</a>')
    return "\n".join(links)


def build_page_html(page, body_html):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="x-ua-compatible" content="ie=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page['title'])} | {SITE_NAME}</title>
  <meta name="description" content="{html.escape(page['hero_text'])}">
  <link rel="shortcut icon" type="image/png" href="favicon.png">
  <link rel="stylesheet" href="css/bootstrap.min.css">
  <link rel="stylesheet" href="css/font-awesome.min.css">
  <link rel="stylesheet" href="css/site.css">
</head>
<body class="site-body">
  <div class="site-shell">
    <header class="site-header">
      <div class="container">
        <div class="row">
          <div class="col-md-5">
            <a class="site-brand" href="index.html">{SITE_NAME}</a>
            <p class="site-tagline">{SITE_TAGLINE}</p>
          </div>
          <div class="col-md-7">
            <nav class="site-nav">
              {build_navigation(page['nav_slug'])}
            </nav>
          </div>
        </div>
      </div>
    </header>

    <section class="hero">
      <div class="container">
        <div class="hero-card">
          <span class="hero-kicker">{html.escape(page['hero_kicker'])}</span>
          <h1>{html.escape(page['hero_title'])}</h1>
          <p>{html.escape(page['hero_text'])}</p>
          <div class="hero-actions">
            <a class="btn-cta" href="contact-us.html">Contact Us</a>
            <a class="btn-secondary" href="more-photos.html">View More Photos</a>
          </div>
        </div>
      </div>
    </section>

    <main class="page-section">
      <div class="container">
        {body_html}
      </div>
    </main>

    <footer class="site-footer">
      <div class="container">
        <div class="footer-card">
          <strong>{SITE_NAME}</strong><br>
          {SITE_TAGLINE}<br>
          Kidlington, OX5 2EQ, near Oxford, UK.
        </div>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def build_body(page, page_data, asset_map):
    content_html = page_data["content"]["rendered"]

    if page["kind"] == "gallery":
        gallery_html = build_more_photos(content_html, asset_map)
        body_html = f"""
        <section class="gallery-card">
          <div class="page-intro">
            <h2>{html.escape(page_data['title']['rendered'])}</h2>
            <p>Click any photo to open the full-size image.</p>
          </div>
          {gallery_html}
        </section>
        """
        return body_html.strip()

    content_html = relink_pages(localise_images(content_html, asset_map))

    if page["kind"] == "contact":
        return build_contact_page(content_html)

    cleaned = cleanup_html(content_html)
    intro = page_data.get("excerpt", {}).get("rendered", "")
    intro = html.unescape(re.sub(r"<[^>]+>", "", intro)).strip()
    intro = re.sub(r"\s*\[(?:\.\.\.|…)\]\s*$", "", intro).strip()
    return f"""
    <section class="content-card">
      <div class="page-intro">
        <h2>{html.escape(page_data['title']['rendered'])}</h2>
        <p>{html.escape(intro or page['hero_text'])}</p>
      </div>
      <div class="content-body">
        {cleaned}
      </div>
    </section>
    """.strip()


def main():
    ensure_output_dirs()
    copy_template_assets()
    asset_map = {}

    for page in PAGES:
        page_data = fetch_page(page)
        body_html = build_body(page, page_data, asset_map)
        page_html = build_page_html(page, body_html)
        (OUTPUT_DIR / page["filename"]).write_text(page_html, encoding="utf-8")

    print(f"Generated site in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
