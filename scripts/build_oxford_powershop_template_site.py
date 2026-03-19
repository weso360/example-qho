#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
MIRROR_DIR = Path("/tmp/oxford-powershop-mirror/www.oxfordpowershop.co.uk")
SITE_DIR = ROOT / "oxford-audio-rebuild"
DOCS_DIR = ROOT / "docs"


SOURCE_PAGES = {
    "index.html": "index.html",
    "pages/Contents.html": "services.html",
    "pages/FindUs.html": "finding-us.html",
    "pages/FindUso.html": "finding-us.html",
    "pages/talk from the workshop.html": "knowledge-hub.html",
    "pages/email me.html": "email-us.html",
    "pages/hifi repairs.html": "hifi-repairs.html",
    "pages/record player radio cassette repair.html": "record-player-repairs.html",
    "pages/amplifier & Speaker repairs.html": "amplifier-speaker-repairs.html",
    "pages/Guitar amplifiers servicing & repairs.html": "guitar-amplifier-repairs.html",
    "pages/home theatre system repairs.html": "home-theatre-repairs.html",
    "pages/dj equipment & decks repairs.html": "dj-equipment-repairs.html",
    "pages/hoover repairs.html": "vacuum-cleaner-repairs.html",
    "pages/aerial installations.html": "aerial-installations.html",
    "pages/television & projector repairs.html": "television-projector-repairs.html",
    "pages/computer repair.html": "computer-monitor-repairs.html",
    "pages/kitchen appliance repair.html": "kitchen-appliance-repairs.html",
    "pages/Gaming-controller-repairs.html": "gaming-controller-repairs.html",
}

LINK_OVERRIDES = {
    "pages/pages/Contents.html": "services.html",
    "pages/pages/FindUs.html": "finding-us.html",
    "pages/pages/FindUso.html": "finding-us.html",
    "pages/pages/home theatre system repairs.html": "home-theatre-repairs.html",
    "pages/pages/hifi repairs.html": "hifi-repairs.html",
    "pages/pages/amplifier & Speaker repairs.html": "amplifier-speaker-repairs.html",
    "pages/pages/dj equipment & decks repairs.html": "dj-equipment-repairs.html",
    "pages/pages/hoover repairs.html": "vacuum-cleaner-repairs.html",
    "pages/pages/kitchen appliance repair.html": "kitchen-appliance-repairs.html",
}

SERVICE_ORDER = [
    "hifi-repairs.html",
    "record-player-repairs.html",
    "amplifier-speaker-repairs.html",
    "guitar-amplifier-repairs.html",
    "home-theatre-repairs.html",
    "dj-equipment-repairs.html",
    "vacuum-cleaner-repairs.html",
    "aerial-installations.html",
    "television-projector-repairs.html",
    "gaming-controller-repairs.html",
    "computer-monitor-repairs.html",
    "kitchen-appliance-repairs.html",
]

TOP_NAV = [
    ("Home", "index.html"),
    ("Repair Services", "services.html"),
    ("Finding Us", "finding-us.html"),
    ("Knowledge Hub", "knowledge-hub.html"),
    ("Email Us", "email-us.html"),
]

SOCIAL_LINKS = [
    ("Facebook", "https://www.facebook.com/pages/Oxford-Powershop-Television-TV-Hi-Fi-Electronic-Repairs/209253849199610?fref=ts", "fa-facebook"),
    ("Twitter", "https://twitter.com/oxfordpowershop", "fa-twitter"),
    ("LinkedIn", "http://www.linkedin.com/company/oxford-powershop-ltd?trk=company_name", "fa-linkedin"),
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_if_exists(src: Path, dest: Path) -> None:
    if src.exists():
        ensure_dir(dest.parent)
        shutil.copy2(src, dest)


def sync_static_assets() -> None:
    ensure_dir(SITE_DIR)
    for name in ("css", "fonts", "images", "js", "sass"):
        src = SITE_DIR / name
        if src.exists():
            continue
    mirror_webpics = MIRROR_DIR / "webpics"
    if mirror_webpics.exists():
        shutil.copytree(mirror_webpics, SITE_DIR / "webpics", dirs_exist_ok=True)

    if (MIRROR_DIR / "css" / "OPS_Positioning.css").exists():
        ensure_dir(SITE_DIR / "legacy-css")
        copy_if_exists(MIRROR_DIR / "css" / "OPS_Positioning.css", SITE_DIR / "legacy-css" / "OPS_Positioning.css")
        copy_if_exists(MIRROR_DIR / "css" / "OPS_Styles.css", SITE_DIR / "legacy-css" / "OPS_Styles.css")


def normalise_asset_path(value: str) -> str:
    value = html.unescape(value.strip())
    if not value:
        return value
    prefixes = (
        "https://www.oxfordpowershop.co.uk/",
        "http://www.oxfordpowershop.co.uk/",
        "../",
        "./",
    )
    for prefix in prefixes:
        if value.startswith(prefix):
            value = value[len(prefix):]
    value = urllib.parse.unquote(value)
    return value.lstrip("/")


def output_slug_from_href(href: str, current_source: str) -> str:
    href = html.unescape(href.strip())
    if not href or href.startswith("#"):
        return href
    if href.startswith("mailto:") or href.startswith("tel:"):
        return href
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urllib.parse.urlparse(href)
        if parsed.netloc.endswith("oxfordpowershop.co.uk"):
            path = urllib.parse.unquote(parsed.path.lstrip("/"))
        else:
            return href
    else:
        current_parent = (MIRROR_DIR / current_source).parent
        path = urllib.parse.unquote(str((current_parent / href).resolve().relative_to(MIRROR_DIR.resolve())))
    return LINK_OVERRIDES.get(path, SOURCE_PAGES.get(path, href))


def clean_fragment(node, current_source: str):
    fragment = BeautifulSoup(str(node), "html.parser")
    for tag in fragment.find_all(["script", "style", "iframe"]):
        tag.decompose()
    for img in fragment.find_all("img"):
        src = img.get("src", "")
        img["src"] = normalise_asset_path(src)
        img["loading"] = "lazy"
        for attr in ("width", "height", "border", "align"):
            img.attrs.pop(attr, None)
    for anchor in fragment.find_all("a"):
        href = anchor.get("href", "").strip()
        rewritten = output_slug_from_href(href, current_source)
        anchor["href"] = rewritten
        if rewritten.startswith("http://") or rewritten.startswith("https://"):
            anchor["target"] = "_blank"
            anchor["rel"] = "noreferrer noopener"
    for tag in fragment.find_all(True):
        for attr in ("style", "width", "height", "border", "onmouseover", "onmouseout", "name", "id", "class", "align"):
            if attr in tag.attrs and tag.name not in ("ul", "ol", "li", "a", "img", "strong", "em", "p", "br", "h1", "h2", "h3", "h4"):
                tag.attrs.pop(attr, None)
    return fragment


def fragment_html(node, current_source: str) -> str:
    if node is None:
        return ""
    fragment = clean_fragment(node, current_source)
    body = fragment.body or fragment
    return "".join(str(child) for child in body.contents).strip()


def read_page(source_rel: str):
    path = MIRROR_DIR / source_rel
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    return soup


def page_title(soup: BeautifulSoup) -> str:
    raw = soup.title.get_text(" ", strip=True) if soup.title else "Oxford Powershop"
    raw = raw.replace(":: Oxford Powershop Ltd ::", "")
    raw = raw.replace(":: Oxford Powershop ::", "")
    raw = raw.replace("Oxford Powershop Ltd ::", "")
    raw = raw.replace("Oxford Powershop Ltd :", "")
    raw = raw.replace("Oxford Powershop Ltd", "")
    raw = raw.replace("::", " ")
    return " ".join(raw.split()).strip(" -|") or "Oxford Powershop"


def page_heading(soup: BeautifulSoup) -> str | None:
    heading = soup.select_one("#AboutUsHome h1, #location h1, #TechTalkLeft .NewsTitlesSMALL, #emailWRAPPER .NewsTitles")
    if heading:
        text = " ".join(heading.get_text(" ", strip=True).split())
        return text.strip(" -|") or None
    return None


def page_description(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"name": lambda v: v and v.lower() == "description"})
    if meta and meta.get("content"):
        return " ".join(meta["content"].split())
    return "Electrical repair specialists keeping appliances working since 1966."


def hero_image(soup: BeautifulSoup) -> str:
    tag = soup.select_one("#MainPicture img, #MapBox img")
    return normalise_asset_path(tag["src"]) if tag and tag.get("src") else "webpics/Large Images/ops690x312.jpg"


def side_image(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one("#NavBarAdvert img, #TechTalkLeft img")
    if tag and tag.get("src"):
        return normalise_asset_path(tag["src"])
    return None


def home_intro_html(soup: BeautifulSoup) -> str:
    node = soup.select_one("#TechTalkTwitter")
    return fragment_html(node, "index.html")


def service_content_html(soup: BeautifulSoup, source_rel: str) -> str:
    for selector in ("#AboutUsHome", "#location", "#Payments", "#times"):
        node = soup.select_one(selector)
        if node:
            return fragment_html(node, source_rel)
    return ""


def workshop_links_html(soup: BeautifulSoup) -> str:
    node = soup.select_one("#TechTalkLeft")
    return fragment_html(node, "pages/talk from the workshop.html")


def service_excerpt(html_text: str) -> str:
    text = BeautifulSoup(html_text, "html.parser").get_text(" ", strip=True)
    return text[:170].rsplit(" ", 1)[0] + "..." if len(text) > 170 else text


def slug_name(output_slug: str) -> str:
    return output_slug.rsplit(".", 1)[0]


def head(title: str, description: str) -> str:
    return f"""<!doctype html>
<html class="no-js" lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>{html.escape(title)} | Oxford Powershop</title>
        <meta name="description" content="{html.escape(description)}">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" type="image/png" href="favicon.png">
        <link rel="stylesheet" href="css/bootstrap.min.css">
        <link rel="stylesheet" href="css/animate.css">
        <link rel="stylesheet" href="css/jquery-ui.min.css">
        <link rel="stylesheet" href="css/meanmenu.min.css">
        <link rel="stylesheet" href="css/owl.carousel.min.css">
        <link rel="stylesheet" href="css/jquery.bxslider.css">
        <link rel="stylesheet" href="css/magnific-popup.css">
        <link rel="stylesheet" href="css/jquery.bootstrap-touchspin.min.css">
        <link rel="stylesheet" href="css/font-awesome.min.css">
        <link rel="stylesheet" href="style.css">
        <link rel="stylesheet" href="css/responsive.css">
        <link rel="stylesheet" href="css/powershop-custom.css">
        <script src="js/vendor/modernizr-2.8.3.min.js"></script>
    </head>
"""


def header(active: str) -> str:
    nav = []
    for label, href in TOP_NAV:
        cls = ' class="active"' if href == active else ""
        nav.append(f'<li{cls}><a href="{href}">{html.escape(label)}</a></li>')
    return f"""
    <body>
        <div id="loader_wrapper">
            <div class="loader"></div>
        </div>
        <header>
            <div class="container">
                <div class="row">
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="header-top">
                            <div class="col-lg-7 col-md-7 col-sm-8 col-xs-12 pd-0">
                                <div class="contact-info-top">
                                    <ul class="list-inline">
                                        <li><img src="images/icons/5.png" alt=""><span>Keeping appliances working since 1966</span></li>
                                        <li><img src="images/icons/6.png" alt=""><span>129-131 Mill Street, Kidlington, OX5 2EE</span></li>
                                        <li><img src="images/icons/7.png" alt=""><span>Talk to an engineer: 01865 375834</span></li>
                                    </ul>
                                </div>
                            </div>
                            <div class="col-lg-5 col-md-5 col-sm-4 col-xs-12 pd-0">
                                <div class="social-media-area">
                                    <ul class="list-inline text-right">
                                        {''.join(f'<li><a href="{href}" target="_blank" rel="noreferrer noopener" aria-label="{label}"><i class="fa {icon}"></i></a></li>' for label, href, icon in SOCIAL_LINKS)}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div id="sticky" class="main-header">
                            <div class="col-lg-3 col-md-3 col-sm-9 col-xs-6 pd-0">
                                <div class="logo-area powershop-logo">
                                    <a href="index.html"><img src="webpics/Service Buttons/ops-logo-615-white.png" alt="Oxford Powershop"></a>
                                </div>
                            </div>
                            <div class="col-lg-9 col-md-9 hidden-sm hidden-xs pd-0">
                                <div class="menu-area">
                                    <nav>
                                        <ul class="list-inline">{''.join(nav)}</ul>
                                    </nav>
                                </div>
                            </div>
                            <div class="col-sm-3 col-xs-6 hidden-lg hidden-md pd-0">
                                <div class="responsive-menu-wrap floatright"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </header>
"""


def breadcrumb(title: str) -> str:
    return f"""
        <div class="breadcumb-area jarallax powershop-breadcumb">
            <div class="container">
                <div class="row">
                    <div class="col-lg-6 col-md-6 col-sm-8 col-xs-12 full_width">
                        <div class="indx_title_left_wrapper">
                            <h2>{html.escape(title)}</h2>
                        </div>
                    </div>
                    <div class="col-lg-6 col-md-6 col-sm-4 col-xs-12 full_width">
                        <div class="indx_title_right_wrapper">
                            <ul>
                                <li><a href="index.html">Home</a> &nbsp;&nbsp;&nbsp;&gt; </li>
                                <li>{html.escape(title)}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""


def footer(service_cards) -> str:
    footer_links = " | ".join(
        f'<a href="{card["output"]}">{html.escape(card["short_title"])}</a>'
        for card in service_cards[:8]
    )
    return f"""
        <footer>
            <div class="footer-top section">
                <div class="container">
                    <div class="row">
                        <div class="col-md-4 col-sm-6 col-xs-12 col wow fadeInUp">
                            <div class="f-about">
                                <div class="logo-area powershop-footer-logo">
                                    <a href="index.html"><img src="webpics/Service Buttons/ops-logo-615-white.png" alt="Oxford Powershop"></a>
                                </div>
                                <p>Electrical repair specialists for hi-fi, turntables, vacuum cleaners, kitchen appliances, TVs, gaming controllers, and more.</p>
                                <div class="social-media-area">
                                    <ul class="list-inline">
                                        {''.join(f'<li><a href="{href}" target="_blank" rel="noreferrer noopener" aria-label="{label}"><i class="fa {icon}"></i></a></li>' for label, href, icon in SOCIAL_LINKS)}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 col-sm-6 col-xs-12 col wow fadeInUp">
                            <div class="foo-link">
                                <h2>Repair Services</h2>
                                <ul>{''.join(f'<li><a href="{card["output"]}">{html.escape(card["title"])}</a></li>' for card in service_cards[:6])}</ul>
                            </div>
                        </div>
                        <div class="col-md-4 col-sm-12 col-xs-12 col wow fadeInUp">
                            <div class="foo-about">
                                <h2>Visit The Workshop</h2>
                                <div class="content">
                                    <p>129-131 Mill Street, Kidlington, Oxfordshire, OX5 2EE</p>
                                    <span>Monday to Friday: 9:00 am - 4:00 pm</span>
                                    <span>Saturday and Sunday: Closed</span>
                                    <a href="finding-us.html">Directions, parking and payment details</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                            <div class="copyright powershop-credit">
                                <p>{footer_links}</p>
                                <p><a href="https://aivora.uk" target="_blank" rel="noreferrer noopener">Created by Aivora</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
        <script src="js/vendor/jquery-3.2.1.min.js"></script>
        <script src="js/tether.min.js"></script>
        <script src="js/bootstrap.min.js"></script>
        <script src="js/owl.carousel.min.js"></script>
        <script src="js/jquery.bxslider.min.js"></script>
        <script src="js/isotope.pkgd.min.js"></script>
        <script src="js/jquery.magnific-popup.min.js"></script>
        <script src="js/jquery.meanmenu.js"></script>
        <script src="js/jarallax.min.js"></script>
        <script src="js/jquery-ui.min.js"></script>
        <script src="js/jquery.bootstrap-touchspin.min.js"></script>
        <script src="js/jquery.waypoints.min.js"></script>
        <script src="js/jquery.counterup.min.js"></script>
        <script src="js/wow.min.js"></script>
        <script src="js/plugins.js"></script>
        <script src="js/main.js"></script>
    </body>
</html>
"""


def build_home(home, services_cards) -> str:
    cards = "".join(
        f"""
        <div class="col-md-4 col-sm-6 col-xs-12">
            <div class="powershop-service-card">
                <a class="powershop-service-card__image" href="{card['output']}"><img src="{card['hero']}" alt="{html.escape(card['title'])}"></a>
                <div class="powershop-service-card__body">
                    <h3><a href="{card['output']}">{html.escape(card['title'])}</a></h3>
                    <p>{html.escape(card['excerpt'])}</p>
                    <a class="btn1" href="{card['output']}"><span>Read More</span></a>
                </div>
            </div>
        </div>
"""
        for card in services_cards[:6]
    )
    return head(home["title"], home["description"]) + header("index.html") + f"""
        <section class="slider-area powershop-hero">
            <div class="slider-list">
                <div class="item active" style="background-image:url('{home['hero']}');">
                    <div class="carousel-captions caption-1">
                        <div class="container">
                            <div class="row">
                                <div class="col-sm-12">
                                    <div class="content">
                                        <h2>Electrical Repair Specialists keeping appliances working since 1966</h2>
                                        <div class="powershop-richtext powershop-home-intro">{home['intro_html']}</div>
                                        <div class="btn-area">
                                            <a href="services.html" class="btn1"><span>Repair Services</span></a>
                                            <a href="finding-us.html" class="btn2"><span>Finding Us</span></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        <section class="about-area section">
            <div class="container">
                <div class="row powershop-home-feature">
                    <div class="col-md-8 col-sm-12">
                        <div class="section-heading-two">
                            <h2>Oxford Powershop Ltd</h2>
                            <p>We specialise in repairing modern and vintage electrical appliances for domestic and commercial use.</p>
                        </div>
                        <div class="powershop-richtext">{home['intro_html']}</div>
                    </div>
                    <div class="col-md-4 col-sm-12">
                        <div class="powershop-side-promo">
                            <img src="{home['aside']}" alt="Oxford Powershop promotion">
                        </div>
                    </div>
                </div>
            </div>
        </section>
        <section class="services-area-one section bg-img1">
            <div class="container">
                <div class="row">
                    <div class="col-sm-12">
                        <div class="section-heading-two text-center">
                            <h2>Repair Services</h2>
                            <p>Hi-fi, turntables, amplifiers, gaming controllers, kitchen appliances, TVs and more.</p>
                        </div>
                    </div>
                </div>
                <div class="row">{cards}</div>
            </div>
        </section>
        <section class="brand-area section">
            <div class="container">
                <div class="row powershop-callout">
                    <div class="col-md-7 col-sm-12">
                        <h2>Visit the workshop in Kidlington</h2>
                        <p>Drop in without appointment for prompt inspections and repairs. Parking is available outside the workshop.</p>
                    </div>
                    <div class="col-md-5 col-sm-12 text-right">
                        <a href="finding-us.html" class="btn1"><span>Get Directions</span></a>
                        <a href="email-us.html" class="btn2"><span>Email Us</span></a>
                    </div>
                </div>
            </div>
        </section>
""" + footer(services_cards)


def build_services_overview(page, services_cards) -> str:
    grid = "".join(
        f"""
        <div class="col-md-4 col-sm-6 col-xs-12">
            <div class="powershop-service-card">
                <a class="powershop-service-card__image" href="{card['output']}"><img src="{card['hero']}" alt="{html.escape(card['title'])}"></a>
                <div class="powershop-service-card__body">
                    <h3><a href="{card['output']}">{html.escape(card['title'])}</a></h3>
                    <p>{html.escape(card['excerpt'])}</p>
                    <a class="btn1" href="{card['output']}"><span>Open Service Page</span></a>
                </div>
            </div>
        </div>
"""
        for card in services_cards
    )
    return head(page["title"], page["description"]) + header("services.html") + breadcrumb("Repair Services") + f"""
        <section class="services-area-one section powershop-service-index">
            <div class="container">
                <div class="row">
                    <div class="col-sm-12">
                        <div class="section-heading-two text-center">
                            <h2>{html.escape(page['title'])}</h2>
                            <p>{html.escape(page['description'])}</p>
                        </div>
                    </div>
                </div>
                <div class="row">{grid}</div>
            </div>
        </section>
""" + footer(services_cards)


def build_standard_page(page, services_cards, active: str = "") -> str:
    side = (
        f'<div class="col-md-4 col-sm-12"><div class="powershop-side-promo"><img src="{page["aside"]}" alt="{html.escape(page["title"])}"></div></div>'
        if page.get("aside")
        else ""
    )
    main_class = "col-md-8 col-sm-12" if side else "col-md-12 col-sm-12"
    return head(page["title"], page["description"]) + header(active) + breadcrumb(page["title"]) + f"""
        <section class="about-area section">
            <div class="container">
                <div class="row powershop-page-hero">
                    <div class="col-sm-12">
                        <div class="powershop-inline-hero"><img src="{page['hero']}" alt="{html.escape(page['title'])}"></div>
                    </div>
                </div>
                <div class="row">
                    <div class="{main_class}">
                        <div class="section-heading-two">
                            <h2>{html.escape(page['title'])}</h2>
                            <p>{html.escape(page['description'])}</p>
                        </div>
                        <div class="powershop-richtext">{page['content_html']}</div>
                    </div>
                    {side}
                </div>
            </div>
        </section>
""" + footer(services_cards)


def build_finding_us(page, services_cards) -> str:
    return head(page["title"], page["description"]) + header("finding-us.html") + breadcrumb("Finding Us") + f"""
        <section class="contact-area section">
            <div class="container">
                <div class="row powershop-page-hero">
                    <div class="col-sm-12">
                        <div class="powershop-inline-hero"><img src="{page['hero']}" alt="Oxford Powershop workshop"></div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-7 col-sm-12">
                        <div class="powershop-map-frame">
                            <iframe src="https://www.google.com/maps?q=129-131%20Mill%20Street%2C%20Kidlington%2C%20OX5%202EE&output=embed" loading="lazy"></iframe>
                        </div>
                    </div>
                    <div class="col-md-5 col-sm-12">
                        <div class="section-heading-two">
                            <h2>Finding Us</h2>
                            <p>{html.escape(page['description'])}</p>
                        </div>
                        <div class="powershop-richtext">{page['content_html']}</div>
                    </div>
                </div>
            </div>
        </section>
""" + footer(services_cards)


def build_workshop(page, services_cards) -> str:
    return head(page["title"], page["description"]) + header("knowledge-hub.html") + breadcrumb("Knowledge Hub") + f"""
        <section class="blog-area section">
            <div class="container">
                <div class="row powershop-page-hero">
                    <div class="col-sm-12">
                        <div class="powershop-inline-hero"><img src="{page['hero']}" alt="Workshop"></div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-7 col-sm-12">
                        <div class="section-heading-two">
                            <h2>{html.escape(page['title'])}</h2>
                            <p>{html.escape(page['description'])}</p>
                        </div>
                        <div class="powershop-richtext">{page['content_html']}</div>
                    </div>
                    <div class="col-md-5 col-sm-12">
                        <div class="powershop-resource-box">
                            <h3>Useful Links</h3>
                            <div class="powershop-richtext">{page['links_html']}</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
""" + footer(services_cards)


def build_email(page, services_cards) -> str:
    return head(page["title"], page["description"]) + header("email-us.html") + breadcrumb("Email Us") + f"""
        <section class="contact-area section">
            <div class="container">
                <div class="row">
                    <div class="col-md-7 col-sm-12">
                        <div class="section-heading-two">
                            <h2>Email Us</h2>
                            <p>{html.escape(page['description'])}</p>
                        </div>
                        <div class="powershop-email-panel">
                            <div class="powershop-richtext">{page['content_html']}</div>
                            <form class="powershop-form">
                                <div class="row">
                                    <div class="col-sm-6"><input type="text" placeholder="Your name"></div>
                                    <div class="col-sm-6"><input type="email" placeholder="Your email"></div>
                                    <div class="col-sm-12"><textarea placeholder="Message"></textarea></div>
                                    <div class="col-sm-12"><button type="button" class="btn1"><span>Email enquiries are not wired up in this static copy</span></button></div>
                                </div>
                            </form>
                        </div>
                    </div>
                    <div class="col-md-5 col-sm-12">
                        <div class="powershop-side-promo"><img src="webpics/Large Images/workshop.jpg" alt="Oxford Powershop workshop"></div>
                    </div>
                </div>
            </div>
        </section>
""" + footer(services_cards)


def build_css() -> str:
    return """
.powershop-logo,
.powershop-footer-logo {
    align-items: center;
    display: flex;
    min-height: 120px;
}
.powershop-logo img,
.powershop-footer-logo img {
    max-width: 100%;
}
.social-media-area ul li a {
    color: #2f2f2f;
}
.menu-area nav ul li.active > a,
.menu-area nav ul li > a:hover,
.menu-area nav ul li > a:focus {
    color: #c53a3e;
}
.powershop-breadcumb {
    background: linear-gradient(rgba(20, 20, 22, 0.74), rgba(20, 20, 22, 0.74)), url('../webpics/Large Images/workshop.jpg') center/cover no-repeat;
}
.powershop-hero .item {
    background-position: center;
    background-size: cover;
    min-height: 780px;
}
.powershop-hero .caption-1 {
    background: rgba(0, 0, 0, 0.18) !important;
    background-image: none !important;
    min-height: 780px;
}
.powershop-hero .caption-1:after {
    background: linear-gradient(90deg, rgba(18, 18, 18, 0.88) 0%, rgba(18, 18, 18, 0.55) 52%, rgba(18, 18, 18, 0.2) 100%) !important;
}
.powershop-hero .content {
    padding: 180px 0 140px;
}
.powershop-hero .content h2 {
    color: #fff;
    font-size: 60px;
    line-height: 1.08;
    margin-bottom: 24px;
    max-width: 720px;
}
.powershop-home-intro,
.powershop-richtext {
    color: #4d4d4d;
    font-size: 17px;
    line-height: 1.8;
}
.powershop-hero .powershop-home-intro,
.powershop-hero .powershop-home-intro a,
.powershop-hero .powershop-home-intro li,
.powershop-hero .powershop-home-intro p {
    color: #fff;
}
.powershop-richtext ul,
.powershop-home-intro ul {
    padding-left: 20px;
}
.powershop-richtext a {
    color: #c53a3e;
}
.powershop-side-promo,
.powershop-inline-hero,
.powershop-map-frame,
.powershop-resource-box,
.powershop-email-panel {
    background: #fff;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.08);
}
.powershop-side-promo img,
.powershop-inline-hero img {
    display: block;
    width: 100%;
}
.powershop-inline-hero {
    margin-bottom: 40px;
}
.powershop-home-feature,
.powershop-page-hero {
    align-items: center;
}
.powershop-service-index,
.services-area-one {
    background: linear-gradient(180deg, #1f2327 0%, #23282d 100%) !important;
}
.powershop-service-card {
    background: #fff;
    display: flex;
    flex-direction: column;
    height: 100%;
    margin-bottom: 30px;
}
.powershop-service-card__image img {
    display: block;
    height: 230px;
    object-fit: cover;
    width: 100%;
}
.powershop-service-card__body {
    display: flex;
    flex: 1 1 auto;
    flex-direction: column;
    padding: 26px;
}
.powershop-service-card__body h3 {
    font-size: 24px;
    line-height: 1.25;
    margin: 0 0 16px;
}
.powershop-service-card__body h3 a {
    color: #222;
}
.powershop-service-card__body p {
    color: #5f5f5f;
    flex: 1 1 auto;
    margin: 0 0 24px;
}
.powershop-callout {
    align-items: center;
    background: linear-gradient(135deg, #f4f1eb 0%, #ffffff 100%);
    border-left: 6px solid #c53a3e;
    padding: 36px 28px;
}
.powershop-callout h2 {
    margin: 0 0 10px;
}
.powershop-map-frame iframe {
    border: 0;
    display: block;
    height: 480px;
    width: 100%;
}
.powershop-resource-box,
.powershop-email-panel {
    padding: 30px;
}
.powershop-form input,
.powershop-form textarea {
    border: 1px solid #d9d9d9;
    margin-bottom: 18px;
    min-height: 54px;
    padding: 14px 16px;
    width: 100%;
}
.powershop-form textarea {
    min-height: 180px;
    resize: vertical;
}
.powershop-credit {
    align-items: flex-end;
    display: flex;
    flex-direction: column;
    gap: 6px;
    text-align: right;
}
.powershop-credit p {
    margin: 0;
}
.powershop-credit a {
    color: #f0d4c0 !important;
}
.footer-top,
footer {
    background: linear-gradient(180deg, #141719 0%, #0d1012 100%) !important;
}
.foo-link ul li a,
.foo-about .content a,
.f-about p,
.foo-about .content p,
.foo-about .content span {
    color: #d0d3d5;
}
.foo-link h2,
.foo-about h2,
.f-about h2 {
    color: #fff;
}
@media (max-width: 991px) {
    .powershop-logo img {
        max-width: 240px;
    }
    .powershop-hero .content h2 {
        font-size: 42px;
    }
    .powershop-credit {
        align-items: flex-start;
        text-align: left;
    }
}
@media (max-width: 767px) {
    .powershop-hero .item,
    .powershop-hero .caption-1 {
        min-height: 640px;
    }
    .powershop-hero .content {
        padding: 140px 0 100px;
    }
    .powershop-hero .content h2 {
        font-size: 34px;
    }
}
""".strip() + "\n"


def write_favicon() -> None:
    copy_if_exists(MIRROR_DIR / "webpics" / "Service Buttons" / "ops-logo-615-white.png", SITE_DIR / "favicon.png")


def mirror_site_to_docs() -> None:
    ensure_dir(DOCS_DIR)
    source_names = {item.name for item in SITE_DIR.iterdir()}
    for existing in list(DOCS_DIR.iterdir()):
        if existing.name == ".nojekyll":
            continue
        if existing.name not in source_names:
            if existing.is_dir():
                shutil.rmtree(existing)
            else:
                existing.unlink()
    for item in SITE_DIR.iterdir():
        target = DOCS_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")


def parse_pages():
    parsed = {}
    for source_rel, output in SOURCE_PAGES.items():
        soup = read_page(source_rel)
        parsed[output] = {
            "source": source_rel,
            "output": output,
            "title": page_heading(soup) or page_title(soup),
            "description": page_description(soup),
            "hero": hero_image(soup),
            "aside": side_image(soup),
            "content_html": service_content_html(soup, source_rel),
        }

    home_soup = read_page("index.html")
    parsed["index.html"]["title"] = "Oxford Powershop Ltd"
    parsed["index.html"]["intro_html"] = home_intro_html(home_soup)
    parsed["index.html"]["aside"] = "webpics/Adverts/THATS-AUDIO-Banner-Advert.jpg"

    services_soup = read_page("pages/Contents.html")
    parsed["services.html"]["title"] = "Repair Services"
    parsed["services.html"]["description"] = page_description(services_soup)

    finding_soup = read_page("pages/FindUs.html")
    parsed["finding-us.html"]["content_html"] = (
        fragment_html(finding_soup.select_one("#location"), "pages/FindUs.html")
        + fragment_html(finding_soup.select_one("#Payments"), "pages/FindUs.html")
        + fragment_html(finding_soup.select_one("#times"), "pages/FindUs.html")
    )

    workshop_soup = read_page("pages/talk from the workshop.html")
    parsed["knowledge-hub.html"]["content_html"] = "<p>Follow Oxford Powershop for the latest repair news, workshop updates and useful audio links.</p>"
    parsed["knowledge-hub.html"]["links_html"] = workshop_links_html(workshop_soup)

    email_soup = read_page("pages/email me.html")
    parsed["email-us.html"]["content_html"] = '<p>Please use the contact details below or visit the workshop in Kidlington. This static version keeps the original email page content as a layout reference.</p>'
    parsed["email-us.html"]["description"] = "Talk to an engineer, visit the workshop, or use the original contact details."

    return parsed


def main():
    if not MIRROR_DIR.exists():
        raise SystemExit("Oxford Powershop mirror not found at /tmp/oxford-powershop-mirror/www.oxfordpowershop.co.uk")

    sync_static_assets()
    write_favicon()
    ensure_dir(SITE_DIR / "css")
    (SITE_DIR / "css" / "powershop-custom.css").write_text(build_css(), encoding="utf-8")

    pages = parse_pages()
    service_cards = []
    for output in SERVICE_ORDER:
        page = pages[output]
        service_cards.append(
            {
                "output": output,
                "title": page["title"],
                "short_title": page["title"].replace("Repairs & Servicing", "Repairs").replace("Repairs &", "Repair &"),
                "hero": page["hero"],
                "excerpt": service_excerpt(page["content_html"]),
            }
        )

    (SITE_DIR / "index.html").write_text(build_home(pages["index.html"], service_cards), encoding="utf-8")
    (SITE_DIR / "services.html").write_text(build_services_overview(pages["services.html"], service_cards), encoding="utf-8")
    (SITE_DIR / "finding-us.html").write_text(build_finding_us(pages["finding-us.html"], service_cards), encoding="utf-8")
    (SITE_DIR / "knowledge-hub.html").write_text(build_workshop(pages["knowledge-hub.html"], service_cards), encoding="utf-8")
    (SITE_DIR / "email-us.html").write_text(build_email(pages["email-us.html"], service_cards), encoding="utf-8")

    for output in SERVICE_ORDER:
        (SITE_DIR / output).write_text(build_standard_page(pages[output], service_cards), encoding="utf-8")

    for alias, target in (
        ("about.html", "services.html"),
        ("gallery.html", "knowledge-hub.html"),
        ("more-photos.html", "knowledge-hub.html"),
        ("contact.html", "finding-us.html"),
        ("contact-us.html", "finding-us.html"),
        ("electronic-waste.html", "services.html"),
    ):
        shutil.copy2(SITE_DIR / target, SITE_DIR / alias)

    mirror_site_to_docs()


if __name__ == "__main__":
    main()
