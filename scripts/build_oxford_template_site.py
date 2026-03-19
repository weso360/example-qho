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
SOURCE_SITE_DIR = ROOT / "oxford-audio-rebuild"
SITE_DIR = ROOT / "docs"
BASE_API = "https://www.oxfordaudiorepair.com/wp-json/wp/v2"


def fetch_json(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def sync_static_site_files():
    ensure_dir(SITE_DIR)
    for dirname in ("css", "fonts", "images", "js"):
        shutil.copytree(SOURCE_SITE_DIR / dirname, SITE_DIR / dirname, dirs_exist_ok=True)
    for filename in ("favicon.png", "style.css", "style.scss"):
        shutil.copy2(SOURCE_SITE_DIR / filename, SITE_DIR / filename)
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")


def normalise_url(url):
    return (
        url.replace("https://testsite.oxfordaudiorepair.com", "https://www.oxfordaudiorepair.com")
        .replace("http://testsite.oxfordaudiorepair.com", "https://www.oxfordaudiorepair.com")
        .replace("http://www.oxfordaudiorepair.com", "https://www.oxfordaudiorepair.com")
    )


def download(url, dest):
    url = normalise_url(url)
    ensure_dir(dest.parent)
    last_error = None
    for attempt in range(4):
        try:
            urllib.request.urlretrieve(url, dest)
            return
        except Exception as exc:
            last_error = exc
            if dest.exists():
                dest.unlink()
            time.sleep(1 + attempt)
    raise last_error


def download_asset(url, asset_map):
    url = normalise_url(url)
    if url in asset_map:
        return asset_map[url]
    filename = Path(urlparse(url).path).name
    target = SITE_DIR / "images" / "oxford" / filename
    if not target.exists():
        download(url, target)
    rel = f"images/oxford/{filename}"
    asset_map[url] = rel
    return rel


def relocalise(html_text, asset_map):
    html_text = normalise_url(html_text)
    urls = sorted(set(re.findall(r"https://(?:www|testsite)\.oxfordaudiorepair\.com/wp-content/uploads/[^\"' )>]+", html_text)))
    out = html_text
    for url in urls:
        local = download_asset(url, asset_map)
        out = out.replace(url, local)
    return out


class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        if "fg-thumb" not in attrs.get("class", ""):
            return
        href = attrs.get("href")
        if not href:
            return
        self.items.append(
            {
                "href": href,
                "title": html.unescape(attrs.get("data-caption-title", "")).strip(),
                "desc": html.unescape(attrs.get("data-caption-desc", "")).strip(),
            }
        )


def template_head(title, description):
    return f"""<!doctype html>
<html class="no-js" lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>{html.escape(title)} | Oxford Audio Repairs</title>
        <meta name="description" content="{html.escape(description)}">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" type="image/x-icon" href="favicon.png">
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
        <link rel="stylesheet" href="css/oxford-custom.css">
        <script src="js/vendor/modernizr-2.8.3.min.js"></script>
    </head>
"""


def header(active):
    def nav_item(label, href, key):
        cls = ' class="active"' if key == active else ""
        return f'<li{cls}><a href="{href}">{label}</a></li>'

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
                            <div class="col-lg-8 col-md-8 col-sm-9 col-xs-12 pd-0">
                                <div class="contact-info-top">
                                    <ul class="list-inline">
                                        <li><img src="images/icons/5.png" alt=""><span>BY APPOINTMENT</span></li>
                                        <li><img src="images/icons/6.png" alt=""><span>Kidlington, OX5 2EQ</span></li>
                                        <li><img src="images/icons/7.png" alt=""><span>Repair, don't discard!</span></li>
                                    </ul>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-4 col-sm-3 col-xs-12 pd-0">
                                <div class="top-button text-right">
                                    <a href="contact.html" class="btn4"><span>Contact Us</span></a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div id="sticky">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                            <div class="main-header">
                                <div class="col-lg-3 col-md-3 col-sm-12 col-xs-12">
                                    <div class="logo-area oxford-logo-text">
                                        <a href="index.html">Oxford Audio Repairs</a>
                                    </div>
                                </div>
                                <div class="col-lg-9 col-md-9 col-sm-12 col-xs-12">
                                    <div class="menu-area">
                                        <nav>
                                            <ul class="list-inline">
                                                {nav_item("Home", "index.html", "home")}
                                                {nav_item("About Repairs", "about.html", "about")}
                                                {nav_item("More Photos", "gallery.html", "gallery")}
                                                {nav_item("Contact", "contact.html", "contact")}
                                            </ul>
                                        </nav>
                                    </div>
                                </div>
                                <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                                    <div class="search-box oxford-search-box">
                                        <form>
                                            <input type="search" placeholder="Oxford Audio Repairs">
                                            <button><i class="fa fa-search"></i></button>
                                            <span class="close-search"><i class="fa fa-close"></i></span>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mobile-menu-area">
                <div class="container">
                    <div class="row">
                      <div class="col-md-12">
                        <div class="mobile-menu">
                            <nav id="dropdown">
                                <ul>
                                    <li><a href="index.html">Home</a></li>
                                    <li><a href="about.html">About Repairs</a></li>
                                    <li><a href="gallery.html">More Photos</a></li>
                                    <li><a href="contact.html">Contact</a></li>
                                </ul>
                            </nav>
                        </div>
                      </div>
                    </div>
                </div>
            </div>
        </header>
"""


def footer():
    return """
        <footer>
            <div class="footer-top">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-3 col-md-6 col-sm-12 col-xs-12">
                            <div class="foo-about">
                                <div class="foo-logo oxford-footer-logo">
                                    <a href="index.html">Oxford Audio Repairs</a>
                                </div>
                                <div class="content">
                                    <p>Repair of amplifiers, turntables, cassette decks, speakers, headphones, bluetooth speakers, and many other devices.</p>
                                    <span>Kidlington, Oxfordshire</span>
                                    <p>Appointments are arranged after you get in touch about the make, model, and fault.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 col-sm-12 col-xs-12">
                            <div class="weight foo-link">
                                <h3>Site Pages</h3>
                                <ul>
                                    <li><a href="index.html"><i class="fa fa-angle-double-right"></i><span>Home</span></a></li>
                                    <li><a href="about.html"><i class="fa fa-angle-double-right"></i><span>About Repairs</span></a></li>
                                    <li><a href="gallery.html"><i class="fa fa-angle-double-right"></i><span>More Photos</span></a></li>
                                    <li><a href="contact.html"><i class="fa fa-angle-double-right"></i><span>Contact Us</span></a></li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 col-sm-12 col-xs-12">
                            <div class="weight foo-link">
                                <h3>Services</h3>
                                <ul>
                                    <li><a href="#"><i class="fa fa-angle-double-right"></i><span>Amplifier Repair</span></a></li>
                                    <li><a href="#"><i class="fa fa-angle-double-right"></i><span>Turntable Restoration</span></a></li>
                                    <li><a href="#"><i class="fa fa-angle-double-right"></i><span>Cassette Deck Service</span></a></li>
                                    <li><a href="#"><i class="fa fa-angle-double-right"></i><span>Speaker Repair</span></a></li>
                                    <li><a href="#"><i class="fa fa-angle-double-right"></i><span>Headphone Repair</span></a></li>
                                    <li><a href="electronic-waste.html"><i class="fa fa-angle-double-right"></i><span>About E-Waste</span></a></li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 col-sm-12 col-xs-12">
                            <div class="weight offer">
                                <h3>How to Get Help</h3>
                                <div class="content">
                                    <p>Use the contact page to describe your equipment and the faults you are seeing.</p>
                                    <span class="tit">Appointments</span>
                                    <p>Detailed location information is sent out after an appointment is arranged.</p>
                                    <a href="contact.html" class="btn4"><span>Contact Us</span></a>
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
                            <div class="top-link-button text-center">
                                <a id="totop" href="#"><i class="fa fa-angle-up"></i></a>
                            </div>
                        </div>
                        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                            <div class="copyright oxford-footer-credit">
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


def breadcumb(title):
    return f"""
        <div class="breadcumb-area jarallax oxford-breadcumb">
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
								<li><a href="index.html">Home</a> &nbsp;&nbsp;&nbsp;> </li>
								<li>{html.escape(title)}</li>
							</ul>
						</div>
					</div>
				</div>
			</div>
		</div>
"""


def write_css():
    css = """
.oxford-logo-text a,
.oxford-footer-logo a {
    display: inline-block;
    font-size: 20px;
    font-weight: 700;
    line-height: 0.95;
    letter-spacing: -0.02em;
    text-transform: uppercase;
}
.oxford-logo-text a {
    color: #222;
    max-width: 170px;
    padding-left: 0 !important;
    white-space: normal;
}
.oxford-logo-text a:hover,
.oxford-logo-text a:focus {
    color: #c59d5f;
}
.oxford-logo-text {
    align-items: center;
    display: flex;
    min-height: 120px;
    padding-top: 0;
}
header .main-header .logo-area.oxford-logo-text a {
    line-height: 0.9 !important;
    padding-left: 0 !important;
    vertical-align: middle;
}
.oxford-footer-logo a { font-size: 24px; }
.oxford-footer-logo a { color: #fff; }
.menu-area nav ul li.active > a { color: #c59d5f; }
.oxford-search-box { display: none; }
.section-head {
    background: url('../images/oxford/pattern-audio-light.svg') no-repeat center !important;
    background-size: cover !important;
}
.info-area-one .info-middel {
    background: url('../images/oxford/pattern-audio-light.svg') no-repeat center !important;
    background-size: cover !important;
}
.info-area-one .row {
    align-items: stretch;
    display: flex;
    flex-wrap: wrap;
}
.info-area-one .row > div {
    display: flex;
}
.info-area-one .info-list,
.info-area-one .info-middel {
    min-height: 520px;
    width: 100%;
}
.info-area-one .info-list figure,
.info-area-one .info-list figure img {
    height: 520px;
}
.info-area-one .info-list figure img {
    object-fit: cover;
}
.info-area-one .info-middel {
    margin-top: 0 !important;
    padding-top: 0;
    align-items: center;
    display: flex;
    justify-content: center;
}
.info-area-one .info-middel .content {
    padding: 60px 25px;
}
.services-area-one {
    background: url('../images/oxford/pattern-audio-dark.svg') no-repeat center !important;
    background-size: cover !important;
}
footer {
    background: url('../images/oxford/pattern-audio-warm.svg') no-repeat center !important;
    background-size: cover !important;
}
.oxford-breadcumb { background-image: url('../images/oxford/CB74BB07-B9DB-4FCF-A8DE-84E4DB27FF79_1_201_a-scaled.jpeg'); background-size: cover; background-position: center; }
.oxford-slider .item { min-height: 760px; background-size: cover; background-position: center; }
.oxford-slider .caption-1 {
    background-color: rgba(0,0,0,0.18) !important;
    background-image: none !important;
    min-height: 760px;
}
.oxford-slider .caption-1:after {
    background: rgba(0,0,0,0.28) !important;
}
.oxford-slider .content { padding: 220px 0 180px; }
.oxford-slider .content h2 { max-width: 820px; }
.oxford-slider .content p { max-width: 760px; }
.oxford-service .services-list { min-height: 280px; padding: 50px 30px; }
.oxford-service .services-list .icons .ico-imgs {
    background: none !important;
    height: 70px;
    width: 70px;
}
.oxford-service .services-list .icons .ico-imgs:before {
    color: #cf9c67;
    display: block;
    font-family: FontAwesome;
    font-size: 34px;
    left: 50%;
    line-height: 70px;
    position: absolute;
    text-align: center;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 70px;
}
.oxford-service .services-list .icons .ico-imgs.ico1:before { content: '\f1de'; }
.oxford-service .services-list .icons .ico-imgs.ico2:before { content: '\f192'; }
.oxford-service .services-list .icons .ico-imgs.ico3:before { content: '\f0ad'; }
.oxford-service .services-list .icons .ico-imgs.ico4:before { content: '\f028'; }
.oxford-service .services-list .icons:hover .ico-imgs:before {
    color: #fff;
}
.oxford-card-grid .about-list-right figure img,
.oxford-card-grid .about-list-left figure img { height: 270px; object-fit: cover; width: 100%; }
.oxford-card-grid .oxford-click-card {
    position: relative;
}
.oxford-card-grid .oxford-card-link {
    inset: 0;
    position: absolute;
    z-index: 20;
}
.oxford-card-grid .oxford-click-card .content,
.oxford-card-grid .oxford-click-card figure {
    position: relative;
    z-index: 5;
}
.oxford-card-grid .oxford-click-card:hover {
    cursor: pointer;
}
.oxford-card-grid .section-heading-two h2 {
    color: #1f1f1f;
}
.oxford-card-grid .section-heading-two p {
    color: #3f3f3f;
}
.oxford-richtext p,
.oxford-richtext li { color: #666; font-size: 16px; line-height: 28px; }
.oxford-richtext ul { padding-left: 22px; margin: 0; }
.oxford-gallery-intro { margin-bottom: 40px; }
.oxford-gallery-grid .grid {
    display: flex;
    flex-wrap: wrap;
}
.oxford-gallery-grid .grid-item {
    display: flex;
    margin-bottom: 0;
}
.oxford-gallery-grid .gallery-list {
    display: flex;
    flex-direction: column;
    width: 100%;
}
.oxford-gallery-grid .gallery-list figure a { display: block; }
.oxford-gallery-grid .gallery-list figure img { height: 320px; object-fit: cover; width: 100%; }
.oxford-caption {
    background: #fff;
    display: flex;
    flex: 1 1 auto;
    flex-direction: column;
    justify-content: flex-start;
    min-height: 120px;
    padding: 18px 18px 24px;
}
.oxford-caption h4 { font-size: 18px; margin: 0 0 8px; }
.oxford-caption p { color: #666; margin: 0; min-height: 48px; }
.oxford-contact-copy { margin-bottom: 40px; }
.oxford-contact-copy .contact-info { min-height: 220px; }
.oxford-form-note { color: #777; margin-bottom: 26px; text-align: center; }
.oxford-static-map { background: url('../images/icons/g-map.png') center/cover no-repeat; height: 450px; position: relative; }
.oxford-static-map::after { background: rgba(0,0,0,0.25); content: ''; inset: 0; position: absolute; }
.oxford-static-map-label { color: #fff; left: 50%; position: absolute; top: 50%; transform: translate(-50%, -50%); z-index: 2; text-align: center; }
.foo-about .content span {
    display: inline-block;
    margin: 10px 0 14px;
}
footer .footer-bottom .oxford-footer-credit {
    display: flex;
    justify-content: flex-end;
    text-align: right !important;
}
footer .footer-bottom .oxford-footer-credit p {
    margin: 0;
}
footer .footer-bottom .oxford-footer-credit a {
    color: #f2d8b0 !important;
    font-weight: 600;
}
footer .footer-bottom .oxford-footer-credit a:hover,
footer .footer-bottom .oxford-footer-credit a:focus {
    color: #ffffff !important;
}
"""
    (SITE_DIR / "css" / "oxford-custom.css").write_text(css.strip() + "\n", encoding="utf-8")


def home_sections(home_html, asset_map):
    home_html = relocalise(home_html, asset_map)
    images = re.findall(r'src="(images/oxford/[^"]+)"', home_html)
    hero = images[0]
    cards = []
    for img in images[1:7]:
        cards.append(img)
    extra = images[7:19]
    return hero, cards, extra


def build_home(home_page, asset_map):
    hero, cards, extra = home_sections(home_page["content"]["rendered"], asset_map)
    excerpt = html.unescape(re.sub(r"<[^>]+>", "", home_page["excerpt"]["rendered"])).strip()
    excerpt = excerpt.replace("[…]", "").replace("[...]", "").strip()
    services = [
        ("Amplifiers", "Repairs and restoration for integrated amps, receivers, and power amplifiers."),
        ("Turntables", "Set-up, service, fault finding, and return to normal operation."),
        ("Cassette Decks", "Cleaning, demagnetising, alignment, and testing."),
        ("Speakers", "Many loudspeakers can be fully restored."),
    ]
    service_html = "\n".join(
        f"""<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                                <div class="services-list text-center">
                                    <div class="icons">
                                        <span class="ico-imgs ico{(idx % 4) + 1}"></span>
                                    </div>
                                    <h4>{title}</h4>
                                    <p>{desc}</p>
                                    <a href="contact.html">Ask About Repairs <i class="fa fa-angle-double-right"></i></a>
                                </div>
                            </div>"""
        for idx, (title, desc) in enumerate(services)
    )
    card_titles = [
        "Brands and equipment",
        "Repair-led approach",
        "Appointment-based service",
        "Kidlington location",
        "Over 100 brands catered for",
        "Photos of real repair work",
    ]
    card_texts = [
        "Amplifiers, turntables, cassette decks, headphones, bluetooth speakers, loudspeakers, and many more.",
        "Repair before replacement, with practical diagnostics and careful restoration work.",
        "Start by getting in touch with the make, model, and fault details.",
        "Located in Kidlington, OX5 2EQ, near Oxford, UK.",
        "Brands include Bose, Ruark, Roberts, Technics, Sony, Pioneer, JBL, Thorens, Rega, NAD, and many others.",
        "See more examples of completed work on the photo gallery page.",
    ]
    about_cards = []
    for idx, img in enumerate(cards):
        block = "about-list-right" if idx < 3 else "about-list-left"
        about_cards.append(
            f"""<div class="col-lg-4 col-md-6 col-sm-6 col-xs-12 pd-0">
                        <div class="{block} oxford-click-card">
                            <a class="oxford-card-link" href="contact.html" aria-label="Contact Oxford Audio Repairs about {html.escape(card_titles[idx].lower())}"></a>
                            <figure><img src="{img}" alt=""></figure>
                            <div class="content">
                                <h4>{card_titles[idx]}</h4>
                                <p>{card_texts[idx]}</p>
                            </div>
                        </div>
                    </div>"""
        )
    gallery_preview = "\n".join(
        f"""<div class="grid-item branding col-lg-4 col-md-6 col-sm-6 col-xs-12 pd-0">
                            <div class="gallery-list">
                                <figure>
                                    <a href="{img}"><img src="{img}" alt=""><span><i class="fa fa-search"></i></span></a>
                                </figure>
                            </div>
                        </div>"""
        for img in extra[:6]
    )
    body = f"""
{header('home')}
        <section class="slider-area oxford-slider">
            <div id="carousel-example-generic" class="carousel slide" data-ride="carousel">
                <div class="carousel-inner" role="listbox">
                    <div class="item active" style="background-image:url('{hero}');">
                        <div class="carousel-captions caption-1">
                            <div class="container">
                                <div class="row">
                                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                                        <div class="content">
                                            <h2 class="wow animated fadeInLeft" data-wow-duration="1s"><span>Repair</span> audio equipment<br> with care and experience.</h2>
                                            <p class="wow animated fadeInLeft" data-wow-duration="2s">{excerpt}</p>
                                            <a href="contact.html" class="btn1 wow animated fadeInUp" data-wow-duration="2s"><span>contact us</span></a>
                                            <div class="clear"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <ol class="carousel-indicators">
                    <li data-target="#carousel-example-generic" data-slide-to="0" class="active"><span class="number">1</span><span class="con">Repairs</span></li>
                </ol>
            </div>
        </section>

        <section class="info-area-one">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-lg-4 col-md-4 col-sm-12 col-xs-12 pd-0">
                        <div class="info-list">
                            <figure>
                                <img src="{cards[0]}" alt="">
                                <div class="content">
                                    <h2>Amplifiers & Hi-Fi</h2>
                                    <a href="contact.html">Ask about repair <i class="fa fa-angle-double-right"></i></a>
                                </div>
                            </figure>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-4 col-sm-12 col-xs-12 pd-0">
                        <div class="info-middel text-center bg-img jarallax">
                            <div class="content">
                                <div class="section-heading-one">
                                    <h2>Oxford Audio Repairs</h2>
                                </div>
                                <p>Repair, don't discard. Oxford Audio Repairs handles a wide range of audio equipment including turntables, cassette decks, loudspeakers, bluetooth speakers, headphones, and many other devices.</p>
                                <a href="about.html" class="btn1"><span>Read More</span></a>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-4 col-sm-12 col-xs-12 pd-0">
                        <div class="info-list">
                            <figure>
                                <img src="{cards[1]}" alt="">
                                <div class="content">
                                    <h2>Turntables & Decks</h2>
                                    <a href="gallery.html">See photos <i class="fa fa-angle-double-right"></i></a>
                                </div>
                            </figure>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="services-area-one bg-img jarallax oxford-service">
            <div class="container">
                <div class="row">
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 pd-0">
                        <div class="services-slider">
                            {service_html}
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="about-area-one oxford-card-grid">
            <div class="section-head">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                            <div class="section-heading-two">
                                <h2>What Gets Repaired</h2>
                                <p>Brands repaired include Bose, Ruark, Roberts, Technics, Sony, Pioneer, JVC, Panasonic, B&amp;W, JBL, Nakamichi, B&amp;O, Rotel, Thorens, Rega, Dual, NAD, and many others.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="container-fluid">
                <div class="row">
                    {''.join(about_cards)}
                </div>
            </div>
        </section>

        <div class="gallery-area section">
            <div class="container">
                <div class="row">
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="section-heading-three">
                            <h2>Repair Photos</h2>
                            <p>A preview of the Oxford Audio Repairs work gallery.</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="container-fluid">
                <div class="row">
                    <div id="gallery" class="gall-img col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="grid">
                            {gallery_preview}
                        </div>
                        <div class="text-center" style="margin-top:40px;">
                            <a href="gallery.html" class="btn1 mfp-exclude"><span>view more photos</span></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
{footer()}
"""
    return template_head("Home", excerpt) + body


def build_gallery(page, asset_map):
    parser = GalleryParser()
    parser.feed(page["content"]["rendered"])
    cards = []
    for idx, item in enumerate(parser.items):
        img = download_asset(item["href"], asset_map)
        title = item["title"] or "Repair photo"
        desc = item["desc"] or "Oxford Audio Repairs work example."
        cards.append(
            f"""<div class="grid-item branding col-lg-4 col-md-6 col-sm-6 col-xs-12 pd-0">
                        <div class="gallery-list">
                            <figure>
                                <a href="{img}" target="_blank" rel="noreferrer noopener"><img src="{img}" alt="{html.escape(title)}"><span><i class="fa fa-search"></i></span></a>
                            </figure>
                            <div class="oxford-caption">
                                <h4>{html.escape(title)}</h4>
                                <p>{html.escape(desc)}</p>
                            </div>
                        </div>
                    </div>"""
        )
    body = f"""
{header('gallery')}
{breadcumb('More Photos')}
        <div class="gallery-area section">
            <div class="container">
                <div class="row oxford-gallery-intro">
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="section-heading-three">
                            <h2>Click any photo to enlarge</h2>
                            <p>Examples of repair, restoration, diagnostics, and verification work.</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="container-fluid oxford-gallery-grid">
                <div class="row">
                    <div id="gallery" class="gall-img col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="grid">
                            {''.join(cards)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
{footer()}
"""
    return template_head("More Photos", "A template-based Oxford Audio Repairs gallery page.") + body


def build_about(page):
    links = re.findall(r'<a href="([^"]+)".*?>(.*?)</a>', page["content"]["rendered"])
    items = "\n".join(
        f'<li><a href="{html.escape(normalise_url(url))}" target="_blank" rel="noreferrer noopener">{html.unescape(re.sub(r"<[^>]+>", "", text)).strip()}</a></li>'
        for url, text in links
    )
    body = f"""
{header('about')}
{breadcumb('About Repairs')}
        <section class="about-area-two section">
            <div class="container">
                <div class="row">
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="section-heading-three">
                            <h2>About electronic waste and repairs</h2>
                            <p>Useful links that support repair, right to repair, and awareness around electronic waste.</p>
                        </div>
                    </div>
                    <div class="col-lg-8 col-md-8 col-sm-12 col-xs-12">
                        <div class="oxford-richtext">
                            <ul>{items}</ul>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-4 col-sm-12 col-xs-12">
                        <div class="contact-info">
                            <span><i class="fa fa-recycle"></i></span>
                            <p>Repair keeps equipment in use longer and helps reduce unnecessary disposal.</p>
                        </div>
                        <div class="contact-info">
                            <span><i class="fa fa-wrench"></i></span>
                            <p>Independent repair work remains valuable because many devices can be restored cost effectively.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
{footer()}
"""
    return template_head("About Repairs", "About electronic waste and repairs.") + body


def build_contact():
    body = f"""
{header('contact')}
{breadcumb('Contact Us')}
        <section class="contact-area section">
            <div class="container">
                <div class="row">
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="map-area">
                            <a href="https://www.oxfordaudiorepair.com/contact-us/" class="go-map" target="_blank" rel="noreferrer noopener">Original Contact Page</a>
                            <div class="oxford-static-map">
                                <div class="oxford-static-map-label">
                                    <h3>Kidlington, OX5 2EQ</h3>
                                    <p>Detailed address information is shared once an appointment is arranged.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row mr-b80 oxford-contact-copy">
                    <div class="col-lg-4 col-md-12 col-xs-12 col-sm-12">
                        <div class="contact-info">
                            <span><i class="fa fa-map-marker"></i></span>
                            <p>Kidlington, OX5 2EQ,<br>near Oxford, UK</p>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-12 col-xs-12 col-sm-12">
                        <div class="contact-info">
                            <span><i class="fa fa-envelope"></i></span>
                            <p>Use this form to describe your equipment and the faults.</p>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-12 col-xs-12 col-sm-12">
                        <div class="contact-info">
                            <span><i class="fa fa-clock-o"></i></span>
                            <p>If you have not heard back in a week, check your spam folder.</p>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="section-heading-three">
                            <h2>Get in touch</h2>
                            <p>Please fill in your details. If you have more than one item, list them in the one form.</p>
                        </div>
                    </div>
                    <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                        <div class="form-area">
                            <p class="oxford-form-note">This keeps the template contact layout. The original site uses a WordPress backend, so this local version is a static handoff.</p>
                            <form>
                                <fieldset>
                                    <div class="row">
                                        <div class="col-sm-4 col-xs-12 feld">
                                            <input type="text" placeholder="Full Name *">
                                            <span><i class="fa fa-user"></i></span>
                                        </div>
                                        <div class="col-sm-4 col-xs-12 feld">
                                            <input type="text" placeholder="Email *">
                                            <span><i class="fa fa-envelope"></i></span>
                                        </div>
                                        <div class="col-sm-4 col-xs-12 feld">
                                            <input type="text" placeholder="Devices: makes and models *">
                                            <span><i class="fa fa-star"></i></span>
                                        </div>
                                    </div>
                                </fieldset>
                                <fieldset>
                                    <div class="feld">
                                        <textarea placeholder="Description of the issues *"></textarea>
                                        <span class="msg"><i class="fa fa-pencil-square-o"></i></span>
                                    </div>
                                </fieldset>
                                <div class="btn-area text-center">
                                    <a href="https://www.oxfordaudiorepair.com/contact-us/" class="btn3" target="_blank" rel="noreferrer noopener"><span>open original form</span></a>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </section>
{footer()}
"""
    return template_head("Contact Us", "Template-based contact page for Oxford Audio Repairs.") + body


def duplicate(source, target):
    (SITE_DIR / target).write_text((SITE_DIR / source).read_text(encoding="utf-8"), encoding="utf-8")


def main():
    asset_map = {}
    sync_static_site_files()
    ensure_dir(SITE_DIR / "images" / "oxford")
    write_css()

    home = fetch_json(f"{BASE_API}/pages/7?_fields=id,title,content,excerpt")
    gallery = fetch_json(f"{BASE_API}/pages?slug=more-photos&_fields=id,title,content")[0]
    about = fetch_json(f"{BASE_API}/pages?slug=electronic-waste&_fields=id,title,content")[0]

    (SITE_DIR / "index.html").write_text(build_home(home, asset_map), encoding="utf-8")
    (SITE_DIR / "gallery.html").write_text(build_gallery(gallery, asset_map), encoding="utf-8")
    (SITE_DIR / "about.html").write_text(build_about(about), encoding="utf-8")
    (SITE_DIR / "contact.html").write_text(build_contact(), encoding="utf-8")

    duplicate("gallery.html", "more-photos.html")
    duplicate("contact.html", "contact-us.html")
    duplicate("about.html", "electronic-waste.html")


if __name__ == "__main__":
    main()
