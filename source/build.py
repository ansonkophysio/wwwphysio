"""Build the static site for www.wwwphysio.com (Traditional Chinese at /, English at /en/).

Usage:  python3 build.py            -> dist/     (the real website)
        python3 build.py --preview  -> preview/  (same site; index.html without the
                                                  document skeleton, for a Claude artifact preview)
Add an article: drop an HTML fragment with a JSON header comment into posts/ (Chinese)
and, with the same file name, into posts-en/ (English), then rebuild.
"""
import hashlib, html, json, os, re, shutil, sys
from urllib.parse import quote
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))  # this folder holds posts/, posts-en/ and src/
PREVIEW = "--preview" in sys.argv
OUT = os.path.join(ROOT, "preview" if PREVIEW else "dist")
SITE_URL = "https://www.wwwphysio.com"
WA_NUMBER = "5592 9407"
WA_LINK = "https://wa.me/85255929407"

def wa(text):
    return f"{WA_LINK}?text={quote(text)}"
MAP_LINK = "https://maps.app.goo.gl/wyFuP1kzYqcNsBYn6"
ADDRESS_ZH = "九龍尖沙咀麼地道 1–3 號德拓大廈 4 樓全層（Amazing Medical）"
ADDRESS_EN = "4/F, Yes & Right House, 1–3 Mody Road, Tsim Sha Tsui, Kowloon (Amazing Medical)"
INSTAGRAM = "https://www.instagram.com/ansonko_physio/"
FACEBOOK = ""  # Anson's Facebook page address: paste it here (the old guess was wrong); the footer link appears only when set

def asset_version(name):
    return hashlib.sha1(open(os.path.join(ROOT, "src", name), "rb").read()).hexdigest()[:8]

CSS_V = asset_version("style.css")
JS_V = asset_version("site.js")
FONTS = ("https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500"
         "&family=Chiron+Hei+HK:wght@300;400;500;700&display=swap")
LANGS = ("zh", "en")
PREFIX = {"zh": "", "en": "en/"}

# Facts waiting for Anson's confirmation (kept off the live site until confirmed):
#   - MTR station, exit and walking minutes (clinic-info.html)
#   - whether balance and strength training is offered (services.html)
#   - whether family can join the first visit (clinic-info.html)

# ---------- words used across pages ----------

T = {
 "zh": {
  "html_lang": "zh-Hant-HK", "og_locale": "zh_HK", "in_lang": "zh-HK",
  "site_name": "高浩維 Anson Ko｜註冊物理治療師", "sep": "｜",
  "brand": "高浩維 Anson Ko", "name_short": "高浩維 Anson Ko", "title": "註冊物理治療師",
  "nav": [("articles.html", "文章"), ("about.html", "關於我"), ("talks-onfield.html", "講座及場邊支援"), ("services.html", "服務範圍"),
          ("first-visit.html", "首次診症"), ("clinic-info.html", "診所資料")],
  "nav_label": "主要", "menu": "選單", "switch": "EN", "switch_label": "English version",
  "wa": "WhatsApp 查詢", "map": "Google 地圖", "clinic": "診所資料",
  "wa_link": wa("你好，我想查詢物理治療"), "wa_talks_link": wa("你好，我想查詢講座或場邊支援"),
  "days": "一二三四五六日",
  "hours_title": "應診時間", "tue_fri": "星期二至五", "sat": "星期六", "sun_mon": "星期日、一", "ph": "公眾假期",
  "closed": "休息", "hours_note": "公眾假期休息。所有診症均需預約。", "by_appt": "所有診症均需預約",
  "address": "地址", "contact": "聯絡", "lift": "大廈設有升降機，抵達 4 樓後請按門鐘。",
  "reception": "Amazing Medical 接待處",
  "fine": "本網站內容只供一般參考，不能取代專業診斷及治療。",
  "latest": "最新文章", "all_posts": "所有文章", "more_posts": "更多文章", "posts_soon": "文章即將推出。",
  "next_read": "下一篇",
  "filter_all": "全部", "filter_label": "按主題篩選",
  "read_min": "閱讀時間約 {n} 分鐘", "crumbs": "位置", "articles": "文章", "toc": "本文內容",
  "reel": "相關短片：", "reel_link": "在 Instagram 觀看",
  "author_line": "註冊物理治療師，於尖沙咀 Amazing Medical 應診。", "about": "關於我",
  "article_note": "本文只供一般參考，不能取代專業診斷及治療。如症狀持續或出現警號，請諮詢醫生或物理治療師。",
  "address_line": ADDRESS_ZH, "street": "麼地道 1–3 號德拓大廈 4 樓全層", "locality": "尖沙咀", "region": "九龍",
 },
 "en": {
  "html_lang": "en-HK", "og_locale": "en_HK", "in_lang": "en-HK",
  "site_name": "Anson Ko | Registered Physiotherapist", "sep": " | ",
  "brand": "Anson Ko 高浩維", "name_short": "Anson Ko 高浩維", "title": "Registered Physiotherapist",
  "nav": [("articles.html", "Articles"), ("about.html", "About"), ("talks-onfield.html", "Talks & on-field"), ("services.html", "Services"),
          ("first-visit.html", "First visit"), ("clinic-info.html", "Clinic info")],
  "nav_label": "Main", "menu": "Menu", "switch": "中文", "switch_label": "中文版",
  "wa": "WhatsApp", "map": "Google Maps", "clinic": "Clinic info",
  "wa_link": wa("Hi, I'd like to ask about physiotherapy"), "wa_talks_link": wa("Hi, I'd like to ask about a talk or on-field support"),
  "days": "MTWTFSS",
  "hours_title": "Opening hours", "tue_fri": "Tue–Fri", "sat": "Sat", "sun_mon": "Sun, Mon", "ph": "Public holidays",
  "closed": "Closed", "hours_note": "Closed on public holidays. By appointment only.", "by_appt": "By appointment only",
  "address": "Address", "contact": "Contact", "lift": "Take the lift to 4/F and ring the doorbell.",
  "reception": "Amazing Medical reception",
  "fine": "The information on this website is for general reference only and does not replace professional diagnosis or treatment.",
  "latest": "Latest article", "all_posts": "All articles", "more_posts": "More articles", "posts_soon": "Articles coming soon.",
  "next_read": "Read next",
  "filter_all": "All", "filter_label": "Filter by topic",
  "read_min": "{n} min read", "crumbs": "Breadcrumb", "articles": "Articles", "toc": "In this article",
  "reel": "Related video: ", "reel_link": "watch on Instagram",
  "author_line": "Registered Physiotherapist, seeing patients at Amazing Medical, Tsim Sha Tsui.", "about": "About me",
  "article_note": "This article is for general reference only and does not replace professional diagnosis or treatment. If symptoms persist or warning signs appear, please see a doctor or physiotherapist.",
  "address_line": ADDRESS_EN, "street": "4/F, Yes & Right House, 1–3 Mody Road", "locality": "Tsim Sha Tsui", "region": "Kowloon",
 },
}

def hours_dl(L):
    return f"""<dl class="hours">
  <dt>{L["tue_fri"]}</dt><dd>10:00–19:00</dd>
  <dt>{L["sat"]}</dt><dd>09:30–14:00</dd>
  <dt>{L["sun_mon"]}</dt><dd>{L["closed"]}</dd>
  <dt>{L["ph"]}</dt><dd>{L["closed"]}</dd>
</dl>"""

# ---------- shared parts ----------

def visit_block(L, lang, both_addresses=False):
    extra = ""
    if both_addresses:
        other = ADDRESS_EN if lang == "zh" else ADDRESS_ZH
        extra = f'<br><span class="small">{other}</span>'
    return f"""<section class="wrap visit reveal" aria-label="{L["clinic"]}">
  <figure><img src="img/reception.jpg" alt="{L["reception"]}" width="900" height="1200" loading="lazy">
    <figcaption class="chip chip-dark">{L["reception"]}</figcaption></figure>
  <div class="info">
    <h2>{L["clinic"]}</h2>
    <dl>
      <div><dt>{L["address"]}</dt><dd>{L["address_line"]}{extra}<br><span class="small">{L["lift"]}</span></dd></div>
      <div><dt>{L["hours_title"]}</dt><dd>{hours_dl(L)}</dd></div>
      <div><dt>WhatsApp</dt><dd>{WA_NUMBER}<br><span class="small">{L["by_appt"]}</span></dd></div>
    </dl>
    <div class="actions"><a class="pill solid" href="{L["wa_link"]}">{L["wa"]}</a><a class="pill line" href="{MAP_LINK}">{L["map"]}</a></div>
  </div>
</section>"""

def header(L, lang, active, lp, switch_href):
    links = "".join(
        f'<a href="{lp}{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for href, label in L["nav"])
    other = "en" if lang == "zh" else "zh"
    sw = (f'<a class="lang" href="{switch_href}" hreflang="{T[other]["html_lang"]}" lang="{T[other]["html_lang"]}" '
          f'aria-label="{L["switch_label"]}">{L["switch"]}</a>')
    return f"""<header class="site-header"><div class="wrap"><div class="navbar glass">
  <a class="brand" href="{lp}index.html">{L["brand"]}</a>
  <nav class="nav nav-wide" aria-label="{L["nav_label"]}">{links}</nav>
  {sw}
  <details class="menu"><summary>{L["menu"]}</summary><nav class="nav" aria-label="{L["nav_label"]}">{links}<a href="{switch_href}" lang="{T[other]["html_lang"]}">{L["switch_label"]}</a></nav></details>
</div></div></header>"""

def page_head(title, intro="", extra_class=""):
    intro_html = f"<p>{intro}</p>" if intro else ""
    return f'<div class="wrap page-head {extra_class}"><h1>{title}</h1>{intro_html}</div>'

def footer(L, lp=""):
    return f"""<footer class="site-footer">
<div class="wrap">
  <div class="cols">
    <div class="lead-col"><p>{L["name_short"]}<br>{L["title"]}</p></div>
    <div><h2>{L["hours_title"]}</h2>{hours_dl(L)}</div>
    <div><h2>{L["address"]}</h2><p>{L["address_line"]}</p><p><a href="{lp}clinic-info.html">{L["clinic"]}</a>　<a href="{MAP_LINK}">{L["map"]}</a></p></div>
    <div><h2>{L["contact"]}</h2><p>WhatsApp: <a href="{L["wa_link"]}">{WA_NUMBER}</a></p>
      <p><a href="{INSTAGRAM}">Instagram</a>{f'　<a href="{FACEBOOK}">Facebook</a>' if FACEBOOK else ""}</p></div>
  </div>
  <div class="fine"><span>{L["fine"]}</span><span>© {date.today().year} 高浩維 Anson Ko</span></div>
  <div class="wordmark" aria-hidden="true">Anson Ko</div>
</div>
</footer>"""

def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>")

def business(lang):
    L = T[lang]
    return {
        "@context": "https://schema.org", "@type": "Physiotherapy",
        "name": L["site_name"], "url": SITE_URL + "/" + PREFIX[lang], "image": SITE_URL + "/img/anson.jpg",
        "telephone": "+852 5592 9407",
        "address": {"@type": "PostalAddress", "streetAddress": L["street"],
                    "addressLocality": L["locality"], "addressRegion": L["region"], "addressCountry": "HK"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "10:00", "closes": "19:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "09:30", "closes": "14:00"}],
        "employee": {"@type": "Person", "name": "高浩維 Anson Ko", "jobTitle": L["title"]},
    }

def url_of(lang, path):
    full = PREFIX[lang] + path
    return SITE_URL + "/" + (full[:-len("index.html")] if full.endswith("index.html") else full)

def page(lang, path, title, desc, band, body, active=None, ld=None, og_type="website", has_twin=True):
    L = T[lang]
    full = PREFIX[lang] + path
    ap = "../" * full.count("/")          # to the site root (shared css, js, images)
    lp = "../" * path.count("/")          # to this language's root
    if path == "404.html" and not PREVIEW:
        ap = lp = "/"                     # the 404 page is served at any missing address
    other = "en" if lang == "zh" else "zh"
    twin = path if has_twin else "index.html"
    switch_href = ap + PREFIX[other] + twin
    full_title = title if title == L["site_name"] else f"{title}{L['sep']}{L['site_name']}"
    canonical = url_of(lang, path)
    alts = ""
    if has_twin:
        alts = (f'<link rel="alternate" hreflang="zh-HK" href="{url_of("zh", path)}">\n'
                f'<link rel="alternate" hreflang="en-HK" href="{url_of("en", path)}">\n'
                f'<link rel="alternate" hreflang="x-default" href="{url_of("zh", path)}">\n')
    head_bits = f"""<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#93a8cd">
<link rel="canonical" href="{canonical}">
{alts}<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/img/anson.jpg">
<meta property="og:locale" content="{L["og_locale"]}">
<meta name="color-scheme" content="light">
<link rel="icon" href="{ap}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{ap}style.css?v={CSS_V}">
<script>document.documentElement.classList.add("js")</script>
<script src="{ap}site.js?v={JS_V}" defer></script>
{jsonld(ld) if ld else ""}"""
    for attr in ("src", "poster"):
        body = body.replace(f'{attr}="img/', f'{attr}="{ap}img/')
        band = band.replace(f'{attr}="img/', f'{attr}="{ap}img/')
    mist_class = "mist" if path == "index.html" else "mist sub"
    content = (f'<div class="{mist_class}">\n{header(L, lang, active, lp, switch_href)}\n{band}\n</div>\n'
               f"<main>\n{body}\n</main>\n{footer(L, lp)}")
    if PREVIEW and full == "index.html":
        # Artifact pages are wrapped in their own skeleton: no doctype/html/head/body here.
        first, rest = head_bits.split("\n", 1)
        return f'{first}\n<meta name="claude:viewport-fit-sides" content="cover">\n{rest}\n{content}\n'
    return f"""<!doctype html>
<html lang="{L["html_lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head_bits}
</head>
<body>
{content}
</body>
</html>
"""

# ---------- posts ----------

def load_posts(folder):
    posts = []
    d = os.path.join(ROOT, folder)
    if not os.path.isdir(d):
        return posts
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html"):
            continue
        raw = open(os.path.join(d, f), encoding="utf-8").read()
        m = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S)
        meta = json.loads(m.group(1)); meta["body"] = m.group(2).strip()
        posts.append(meta)
    return sorted(posts, key=lambda x: (x["date"], x.get("time", "00:00")), reverse=True)

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]

def fmt_date(iso, lang):
    y, mo, dd = (int(v) for v in iso.split("-"))
    return f"{y} 年 {mo} 月 {dd} 日" if lang == "zh" else f"{dd} {MONTHS[mo - 1]} {y}"

def reading_minutes(body):
    text = re.sub(r"<[^>]+>", "", body)
    cjk = len(re.findall(r"[㐀-鿿]", text))
    words = len(re.findall(r"[A-Za-z]+", text))
    return max(1, round(cjk / 350 + words / 200 + 0.4))

def mins_range(posts):
    m = sorted(reading_minutes(x["body"]) for x in posts) or [3]
    return str(m[0]) if m[0] == m[-1] else f"{m[0]}–{m[-1]}"

TOPIC_IDS = {"肩頸痛": "neck", "腰痛": "back", "膝痛": "knee", "運動創傷": "sports",
             "Neck & shoulders": "neck", "Low back pain": "back", "Knee pain": "knee", "Sports injuries": "sports"}

def topic_id(t):
    return TOPIC_IDS.get(t) or re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "topic"

def topics_of(posts):
    out = []
    for x in posts:
        if x.get("topic") and x["topic"] not in out:
            out.append(x["topic"])
    return out

def hero_post(x, lang):
    L = T[lang]
    return f"""<article class="hero-post glass">
    <div class="thumb"><img src="{cover_of(x)}" alt="{x.get("cover_alt", "")}"></div>
    <div class="body">
      <div class="hp-top"><span class="label">{L["latest"]}</span><span class="chip-topic">{x.get("topic", "")}</span></div>
      <h2><a href="articles/{x["slug"]}.html">{x["title"]}</a></h2>
      <p class="ex">{x["description"]}</p>
      {meta_row(x, lang)}
    </div>
  </article>"""

def cover_of(x):
    return x.get("cover") or "img/covers/default.svg"

def meta_row(x, lang):
    L = T[lang]
    return (f'<div class="meta-row"><time datetime="{x["date"]}">{fmt_date(x["date"], lang)}</time>'
            f'<span class="sep"></span><span>{L["read_min"].format(n=reading_minutes(x["body"]))}</span></div>')

def post_grid(posts, lang, lp):
    items = "".join(
        f'<li class="post-card" data-topic="{x.get("topic", "")}">'
        f'<div class="thumb"><img src="{cover_of(x)}" alt="" loading="lazy"></div>'
        f'<div class="body"><span class="chip-topic">{x.get("topic", "")}</span>'
        f'<h3><a href="{lp}articles/{x["slug"]}.html">{x["title"]}</a></h3>'
        f'<p class="ex">{x["description"]}</p>{meta_row(x, lang)}</div></li>'
        for x in posts)
    return f'<ul class="post-grid stagger">{items}</ul>' if posts else ""

def featured_card(x, lang):
    L = T[lang]
    return f"""<article class="featured">
  <div class="thumb"><img src="{cover_of(x)}" alt="{x.get("cover_alt", "")}"></div>
  <div class="body">
    <p class="label">{L["latest"]}</p>
    <span class="chip-topic" style="justify-self:start">{x.get("topic", "")}</span>
    <h2><a href="articles/{x["slug"]}.html">{x["title"]}</a></h2>
    <p class="ex">{x["description"]}</p>
    <div class="byline"><img src="img/anson-sq.jpg" alt=""><div><b>{L["name_short"]}</b><span>{L["title"]}</span></div></div>
    {meta_row(x, lang)}
  </div>
</article>"""

def add_heading_ids(body):
    toc = []
    def repl(m):
        n = len(toc) + 1
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        toc.append((f"s{n}", text))
        return f'<h2 id="s{n}">{m.group(1)}</h2>'
    body = re.sub(r"<h2>(.*?)</h2>", repl, body)
    return body, toc

def article_page(x, posts, lang, twins):
    L = T[lang]
    body_html, toc = add_heading_ids(x["body"])
    toc_items = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)
    reel = (f'<p>{L["reel"]}<a href="{x["reel"]}">{L["reel_link"]}</a></p>' if x.get("reel") else "")
    nxt = next((o for o in posts if o["slug"] == x.get("next")), None)
    next_card = ""
    if nxt:
        next_card = (f'<a class="next-read" href="{nxt["slug"]}.html"><span class="label">{L["next_read"]}</span>'
                     f'<span class="t">{nxt["title"]}</span>'
                     f'<span class="meta">{L["read_min"].format(n=reading_minutes(nxt["body"]))}</span></a>')
    others = [o for o in posts if o["slug"] not in (x["slug"], x.get("next"))][:3]
    more = (f'<section class="wrap reveal"><h2>{L["more_posts"]}</h2>{post_grid(others, lang, "../")}</section>' if others else "")
    band = f"""<div class="wrap article-head">
  <nav class="crumbs" aria-label="{L["crumbs"]}"><a href="../articles.html">{L["articles"]}</a><span aria-hidden="true">›</span><span class="chip-topic">{x.get("topic", "")}</span></nav>
  <h1>{x["title"]}</h1>
  <div class="byline"><img src="img/anson-sq.jpg" alt=""><div><b>{L["name_short"]}</b><span>{L["title"]}</span></div></div>
  {meta_row(x, lang)}
</div>"""
    body = f"""<div class="progress" aria-hidden="true"></div>
<div class="wrap cover-wrap"><img src="{cover_of(x)}" alt="{x.get("cover_alt", "")}"></div>
<div class="wrap article-grid">
  <aside class="toc" aria-label="{L["toc"]}"><p>{L["toc"]}</p><ol>{toc_items}</ol></aside>
  <article class="article-body">
    <details class="toc-mobile"><summary>{L["toc"]}</summary><ol>{toc_items}</ol></details>
    {body_html}
    {reel}
    {next_card}
    <div class="author-box"><img src="img/anson-sq.jpg" alt="{L["name_short"]}">
      <p><b>{L["name_short"]}</b><br>{L["author_line"]}<a href="../about.html">{L["about"]}</a></p></div>
    <p class="note">{L["article_note"]}</p>
  </article>
</div>
{more}"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": x["title"],
          "description": x["description"], "inLanguage": L["in_lang"],
          "datePublished": x["date"], "dateModified": x["updated"],
          "author": {"@type": "Person", "name": "高浩維 Anson Ko", "jobTitle": L["title"],
                     "url": url_of(lang, "about.html")},
          "mainEntityOfPage": url_of(lang, f'articles/{x["slug"]}.html'),
          "image": SITE_URL + "/img/anson.jpg"}
    return page(lang, f'articles/{x["slug"]}.html', x["title"], x["description"], band, body,
                "articles.html", ld, "article", has_twin=x["slug"] in twins)

def articles_body(posts, lang):
    L = T[lang]
    if not posts:
        return f'<div class="wrap"><p class="small">{L["posts_soon"]}</p></div>'
    topics = []
    for x in posts:
        if x.get("topic") and x["topic"] not in topics:
            topics.append(x["topic"])
    rest = posts[1:]
    filters = ""
    if len(topics) > 1 and rest:
        btns = f'<button type="button" aria-pressed="true" data-filter="">{L["filter_all"]}</button>' + "".join(
            f'<button type="button" aria-pressed="false" data-filter="{t}" data-id="{topic_id(t)}">{t}</button>' for t in topics)
        filters = f'<div class="filters" role="group" aria-label="{L["filter_label"]}">{btns}</div>'
    grid = (f'<section class="wrap reveal"><div class="section-head"><h2>{L["all_posts"]}</h2>{filters}</div>{post_grid(rest, lang, "")}</section>'
            if rest else "")
    return f'<div class="wrap reveal featured-wrap" data-topic="{posts[0].get("topic", "")}">{featured_card(posts[0], lang)}</div>\n{grid}'

# ---------- page content, per language ----------

C = {
 "zh": {
  "home_desc": "以淺白文字講解常見痛症及運動創傷，並附可在家進行的練習。由香港註冊物理治療師高浩維 Anson Ko 撰寫，於尖沙咀 Amazing Medical 應診。",
  "author_p": "<b>高浩維 Anson Ko</b>，香港註冊物理治療師，於尖沙咀 Amazing Medical 應診。前香港水球隊運動員（2017–2024），現任香港水球隊物理治療師。",
  "author_h": "關於作者",
  "topics_label": "按主題瀏覽",
  "blog_lead": "以淺白文字講解常見痛症及運動創傷，並附可在家進行的練習。",
  "blog_h1": "了解痛症與運動創傷",
  "photo_alt": "註冊物理治療師高浩維 Anson Ko",
  "intro_p": "物理治療以評估為基礎，透過運動治療、手法治療等方法，幫助改善痛楚及活動能力。",
  "stats": [["45–60<small>分鐘</small>", "首次診症", "包括問診、檢查，以及講解評估結果與治療計劃。"], ["HK$900", "每節物理治療", "每節 45–60 分鐘。其他治療項目的收費，歡迎以 WhatsApp 查詢。"], ["5<small>天</small>", "每週應診", "星期二至六應診；星期日、一及公眾假期休息。"]],
  "first_h": "首次診症", "first_p": "首次診症約需 45–60 分鐘。",
  "steps": [["問診", "了解病歷、症狀及康復目標"], ["評估", "檢查關節活動、肌力及日常動作"], ["講解", "說明評估結果及治療方案"], ["治療", "按需要開始治療，並指導家居練習"]],
  "faq_h": "常見問題",
  "referral": "預約前，可先以 WhatsApp 查詢你的情況是否需要醫生轉介信。如已備有轉介信、診斷書或相關報告，請於首次診症時一併帶來。",
  "bring": "<ul><li>醫生轉介信、診斷書或相關報告（如有）</li><li>X 光或磁力共振報告（如有）</li><li>現正服用的藥物名單</li><li>便於活動的衣著</li></ul>",
  "fee": "物理治療每節 HK$900（45–60 分鐘）。其他治療項目的收費，歡迎以 WhatsApp 查詢。",
  "family_q": "可以代父母或家人查詢嗎？",
  "family_a": "可以。請以 WhatsApp 聯絡，簡述家人的情況（例如疼痛部位、是否剛接受手術）及方便的時間。如家人行動不便或需使用輪椅，請預先告知。",
  "sessions": "視乎個別情況及康復目標而定。首次評估後，我會說明預計所需的時間及次數，以及可在家進行的練習。",
  "not_fit": "評估後，如我認為你需要先由醫生診治或接受進一步檢查，會直接告知，並協助你尋找合適的醫護人員跟進。",
  "faq": [["需要醫生轉介信嗎？", "referral"], ["首次診症需要帶備甚麼？", "bring"], ["收費是多少？", "fee"], ["需要接受多少次治療？", "sessions"], ["物理治療是否適合我的情況？", "not_fit"]],
  "services_t": "服務範圍",
  "services_desc": "高浩維 Anson Ko 的物理治療服務：肩頸、腰背及關節痛、運動創傷、手術後復康。於尖沙咀 Amazing Medical 應診。",
  "services_rows": [["肩頸、腰背及關節痛", "例如久坐引起的肩頸及腰背痛、手腕及手肘痛，以及膝關節退化。治療可包括運動治療、手法治療及家居練習。"], ["運動創傷", "例如扭傷、拉傷、跑步或行山後的膝痛，以及反覆出現的舊患。治療會配合你的運動項目，循序漸進地安排重返訓練。"], ["手術後復康", "例如膝關節或髖關節置換、韌帶手術後的康復訓練，並按手術醫生的指示及個人進度分階段進行。"]],
  "limits": "治療效果因人而異。評估後，我會說明治療計劃、預計所需時間及治療的限制；如你的情況需要先由醫生跟進，我會直接告知。如症狀持續或出現警號，請諮詢醫生或物理治療師。",
  "first_visit_link": "首次診症須知",
  "fv_desc": "首次物理治療診症約 45–60 分鐘：了解病歷、檢查、解釋評估結果及治療計劃。請帶備轉介信或報告（如有）。收費每節 HK$900。",
  "fv_ref": "需要醫生轉介信嗎？",
  "ci_desc": "應診時間、地址及交通：九龍尖沙咀麼地道 1–3 號德拓大廈 4 樓全層（Amazing Medical）。WhatsApp 5592 9407。",
  "ci_family_h": "給家人的資料",
  "ci_family": "<p>如為父母或家人查詢或預約，可直接以 WhatsApp 聯絡，並提供以下資料：</p><ul><li>家人的大致情況（例如疼痛部位、是否剛接受手術）</li><li>方便的時間</li></ul><p>如家人行動不便或需使用輪椅，請預先告知，以便安排。</p>",
  "articles_desc": "註冊物理治療師高浩維 Anson Ko 以簡單易明的方式講解肩頸痛、腰痛、運動創傷等常見問題。",
  "articles_intro": "以淺白的文字，講解常見痛症及運動創傷。",
  "nf_t": "找不到頁面", "nf_link": "返回首頁",
  "about_desc": "高浩維 Anson Ko，香港註冊物理治療師，香港水球隊物理治療師，前香港水球隊運動員（2017–2024），於尖沙咀 Amazing Medical 應診。",
  "about_intro": "香港註冊物理治療師。前香港水球隊運動員，現任香港水球隊物理治療師。",
  "bio": """<h2>你好，我是高浩維 Anson Ko</h2>
    <p class="lead">我是香港註冊物理治療師，於尖沙咀 Amazing Medical 應診。</p>
    <p>2017 至 2024 年，我是香港水球隊運動員，曾代表香港參加第十九屆亞運會及亞洲水球錦標賽。七年的訓練及比賽，讓我深切體會運動員所承受的訓練量和比賽壓力，以及受傷後希望盡快重返訓練的心情。</p>
    <p>退役後，我擔任香港水球隊物理治療師，並於 2025 年全國運動會負責港隊的場邊傷患處理及恢復安排。我亦曾連續兩季於香港超級聯賽擔任香港足球會的場邊物理治療師。作為拔萃男書院舊生，我現時亦為母校運動隊提供物理治療支援。</p>
    <p>在診所，我為不同人士處理痛症及運動創傷，包括長時間伏案工作的上班族、週末運動愛好者、游泳及水上運動人士，以及手術後需要復康的人士。</p>
    <div class="facts-row">
      <div><b>2017–2024</b><span>香港水球隊運動員</span></div>
      <div><b>第十九屆</b><span>亞運會（水球）</span></div>
      <div><b>現任</b><span>香港水球隊物理治療師</span></div>
    </div>
    <h2>學歷</h2>
    <ul class="quals">
      <li>Bachelor of Science (Hons) in Physiotherapy – The Hong Kong Polytechnic University</li>
      <li>Postgraduate Diploma in Modern Acupuncture for Rehabilitation – HKU SPACE</li>
      <li>Advanced Certificate in Sport and Exercise Nutrition – HKU SPACE</li>
    </ul>
    <h2>專業資格及證書</h2>
    <ul class="quals">
      <li>香港註冊物理治療師 Registered Physiotherapist (Hong Kong)</li>
      <li>Certified DMA Clinical Pilates Clinician</li>
      <li>Certified Kinesio Taping Practitioner</li>
    </ul>
    <p>診症語言：廣東話、英語</p>""",
  "ig_line": '我亦會於 <a href="{ig}">Instagram</a> 分享痛症及運動相關的健康知識。',
 },
 "en": {
  "home_desc": "Common pain and sports injuries explained in plain language, with exercises you can do at home. Written by Anson Ko, a Registered Physiotherapist in Hong Kong who sees patients at Amazing Medical, Tsim Sha Tsui.",
  "author_p": "<b>Anson Ko</b> is a Registered Physiotherapist in Hong Kong, seeing patients at Amazing Medical, Tsim Sha Tsui. He played for the Hong Kong Water Polo Team from 2017 to 2024 and is now the team's physiotherapist.",
  "author_h": "About the author",
  "topics_label": "Browse by topic",
  "blog_lead": "Common pain and sports injuries explained in plain language, with exercises you can do at home.",
  "blog_h1": "Understanding pain and sports injuries",
  "photo_alt": "Registered Physiotherapist Anson Ko",
  "intro_p": "Physiotherapy starts with an assessment, then uses exercise therapy, manual therapy and other methods to help improve pain and movement.",
  "stats": [["45–60<small>min</small>", "First visit", "History, examination, and an explanation of the findings and treatment plan."], ["HK$900", "Per physiotherapy session", "Each session is 45–60 minutes. For other treatment fees, please ask on WhatsApp."], ["5<small>days</small>", "Open each week", "Tuesday to Saturday. Closed on Sunday, Monday and public holidays."]],
  "first_h": "Your first visit", "first_p": "A first visit takes about 45–60 minutes.",
  "steps": [["Consultation", "Your history, symptoms and goals"], ["Assessment", "Joint movement, strength and everyday movements"], ["Explanation", "Your findings and treatment plan, in plain terms"], ["Treatment", "Treatment as needed, with exercises for home"]],
  "faq_h": "Common questions",
  "referral": "Before booking, you can ask on WhatsApp whether your situation needs a doctor's referral letter. If you already have a referral letter, medical certificate or reports, please bring them to your first visit.",
  "bring": "<ul><li>Doctor's referral letter, medical certificate or related reports (if any)</li><li>X-ray or MRI reports (if any)</li><li>A list of your current medicines</li><li>Comfortable clothing</li></ul>",
  "fee": "HK$900 per physiotherapy session (45–60 minutes). For other treatment fees, please ask on WhatsApp.",
  "family_q": "Can I enquire on behalf of a parent or family member?",
  "family_a": "Yes. Send a WhatsApp message with a brief description of their condition (for example, where the pain is, or whether they have recently had surgery) and the times that suit them. If they have limited mobility or use a wheelchair, please let me know in advance.",
  "sessions": "It depends on your condition and goals. After the first assessment, I'll explain the likely time frame and number of sessions, and what you can practise at home.",
  "not_fit": "If, after the assessment, I think you need to see a doctor or have further tests first, I'll tell you directly and help you find the right professional to follow up.",
  "faq": [["Do I need a doctor's referral?", "referral"], ["What should I bring to my first visit?", "bring"], ["How much does it cost?", "fee"], ["How many sessions will I need?", "sessions"], ["Is physiotherapy right for my condition?", "not_fit"]],
  "services_t": "Services",
  "services_desc": "Physiotherapy services by Anson Ko: neck, back and joint pain, sports injuries, and rehabilitation after surgery. At Amazing Medical, Tsim Sha Tsui.",
  "services_rows": [["Neck, back and joint pain", "Such as neck and back pain from long hours of sitting, wrist and elbow pain, and knee osteoarthritis. Treatment may include exercise therapy, manual therapy and a home exercise programme."], ["Sports injuries", "Such as sprains, strains, knee pain after running or hiking, and recurring old injuries. Treatment is planned around your sport, with a gradual return to training."], ["Rehab after surgery", "Such as rehabilitation after a knee or hip replacement, or ligament surgery, progressed in stages according to your surgeon's instructions and your recovery."]],
  "limits": "Results vary from person to person. After the assessment, I'll explain the treatment plan, the likely time frame and its limits; if you need to see a doctor first, I'll tell you directly. If symptoms persist or warning signs appear, please see a doctor or physiotherapist.",
  "first_visit_link": "Your first visit",
  "fv_desc": "A first physiotherapy visit takes about 45–60 minutes: your history, an examination, and an explanation of the findings and treatment plan. Please bring any referral letter or reports. HK$900 per session.",
  "fv_ref": "Do I need a doctor's referral?",
  "ci_desc": "Opening hours and address: 4/F, Yes & Right House, 1–3 Mody Road, Tsim Sha Tsui (Amazing Medical). WhatsApp 5592 9407.",
  "ci_family_h": "For family members",
  "ci_family": "<p>If you are enquiring or booking for a parent or family member, please send a WhatsApp message with:</p><ul><li>a brief description of their condition (for example, where the pain is, or whether they have recently had surgery)</li><li>the times that suit them</li></ul><p>If they have limited mobility or use a wheelchair, please let me know in advance so I can make arrangements.</p>",
  "articles_desc": "Registered Physiotherapist Anson Ko explains common problems such as neck pain, back pain and sports injuries in plain language.",
  "articles_intro": "Common pain and sports injuries, explained in plain language.",
  "nf_t": "Page not found", "nf_link": "Back to home",
  "about_desc": "Anson Ko is a Registered Physiotherapist in Hong Kong, Team Physiotherapist for the Hong Kong Water Polo Team and a former Hong Kong water polo player (2017–2024), seeing patients at Amazing Medical, Tsim Sha Tsui.",
  "about_intro": "Registered Physiotherapist in Hong Kong. Former Hong Kong Water Polo Team player, now the team's physiotherapist.",
  "bio": """<h2>Hi, I'm Anson Ko</h2>
    <p class="lead">I'm a Registered Physiotherapist in Hong Kong, seeing patients at Amazing Medical in Tsim Sha Tsui.</p>
    <p>From 2017 to 2024 I played for the Hong Kong Water Polo Team, representing Hong Kong at the 19th Asian Games and the Asian Water Polo Championship. Seven years of training and competing showed me what athletes deal with every day: the training volume, the pressure of competition, and the urge to get back in the water after an injury.</p>
    <p>Today I'm the Team Physiotherapist for the Hong Kong Water Polo Team, and at the 2025 National Games of China I led the team's on-site injury management and recovery. I have also spent two consecutive seasons as field-side physiotherapist for Hong Kong Football Club in the Hong Kong Premier League. As a Diocesan Boys' School (DBS) alumnus, I also provide physiotherapy support to the school's sports teams.</p>
    <p>At the clinic, I help people with pain and sports injuries: office workers who sit for long hours, weekend athletes, swimmers and water-sports players, and people recovering after surgery.</p>
    <div class="facts-row">
      <div><b>2017–2024</b><span>Hong Kong Water Polo Team player</span></div>
      <div><b>19th</b><span>Asian Games (water polo)</span></div>
      <div><b>Current</b><span>Hong Kong Water Polo Team physiotherapist</span></div>
    </div>
    <h2>Academic qualifications</h2>
    <ul class="quals">
      <li>Bachelor of Science (Hons) in Physiotherapy – The Hong Kong Polytechnic University</li>
      <li>Postgraduate Diploma in Modern Acupuncture for Rehabilitation – HKU SPACE</li>
      <li>Advanced Certificate in Sport and Exercise Nutrition – HKU SPACE</li>
    </ul>
    <h2>Certifications and licences</h2>
    <ul class="quals">
      <li>Registered Physiotherapist (Hong Kong)</li>
      <li>Certified DMA Clinical Pilates Clinician</li>
      <li>Certified Kinesio Taping Practitioner</li>
    </ul>
    <p>Languages: Cantonese and English</p>""",
  "ig_line": 'I also share pain and exercise tips on <a href="{ig}">Instagram</a>.',
 },
}


# ---------- talks, on-field support and the clinic gallery ----------

XC = {
 "zh": {
  "page_t": "講座及場邊支援",
  "page_desc": "註冊物理治療師高浩維 Anson Ko 為公司、學校、運動隊及社區團體提供健康講座、工作坊及場邊物理治療支援。",
  "page_intro": "為公司、學校、運動隊及社區團體提供健康講座、工作坊及場邊物理治療支援。",
  "talks_h": "講座及工作坊",
  "talks_p": "我為公司、學校、運動隊及社區團體主持健康講座及工作坊。內容以健康教育為主，並設示範及練習環節，讓參加者掌握可於日常生活中實踐的方法。",
  "for": "對象",
  "talks_for": ["公司及工作間", "學校", "運動隊及會所", "社區團體及安老院舍"],
  "topics_h": "常見主題",
  "topics": ["痛症與日常運動", "辦公室肩頸腰背痛", "跑步、行山及球類運動的創傷預防", "比賽前準備：睡眠、熱身及恢復", "長者肌力及預防跌倒"],
  "recent_h": "最近的講座",
  "recent": [("2026 年 10 月", "長者痛症與運動工作坊（社區機構，一小時，包括示範及練習）"),
             ("2026 年 10 月", "比賽週準備講座（中學游泳隊）")],
  "field_h": "場邊支援",
  "field_p": "我為運動隊及比賽提供場邊物理治療支援，於訓練及比賽期間處理傷患，並與教練及隊伍醫療人員合作。",
  "field_for": ["運動隊", "學校運動隊", "比賽及運動活動"],
  "field_what_h": "內容",
  "field_what": ["場邊傷患評估及即時處理", "貼紮及賽前準備", "賽後恢復安排", "評估能否繼續比賽，並安排重返訓練"],
  "field_exp_h": "經驗",
  "field_exp": ["香港水球隊物理治療師（現任）", "2025 年全國運動會：負責港隊水球的場邊傷患處理及恢復安排",
                "香港足球會（香港超級聯賽）場邊物理治療師，連續兩季", "拔萃男書院運動隊物理治療支援"],
  "ask_h": "查詢", "ask_p": "講座及場邊支援的日期、地點及內容，可按需要安排。",
  "more": "了解更多",
  "teaser_talks": "為公司、學校、運動隊及社區團體主持健康講座和工作坊。",
  "teaser_field": "為運動隊及比賽提供場邊物理治療支援。",
  "talk_alt": "物理治療師在屏幕前講解，參加者手持練習單張", "field_alt": "物理治療師為球員檢查肩膊活動",
  "field_media": [("video", "img/media/event-room", "為賽事預備的治療區", "預先佈置好的治療區，有幾張治療床和放滿物資的桌子"),
                  ("img", "img/field-ankle.jpg", "為球員檢查腳踝", "物理治療師俯身檢查躺在地墊上的球員的腳踝")],
  "gallery_h": "診所環境",
  "gallery": [("img", "img/waiting-area.jpg", "候診區"), ("video", "img/media/gym-area", "運動訓練區"),
              ("img", "img/treatment-room.jpg", "治療室"), ("img", "img/equipment.jpg", "治療儀器")],
  "way_h": "怎樣找到診所",
  "way_steps": ["於麼地道 1–3 號德拓大廈（Yes &amp; Right House）正門進入。", "乘升降機至 4 樓。", "於 Amazing Medical 玻璃門前按門鐘。"],
  "way_bldg": "德拓大廈，麼地道 1–3 號", "way_bldg_alt": "德拓大廈入口，可見大廈招牌及門牌「麼地道 1–3 號」",
  "way_door": "4 樓 Amazing Medical", "way_door_alt": "Amazing Medical 的玻璃門及標誌",
 },
 "en": {
  "page_t": "Talks & on-field support",
  "page_desc": "Registered Physiotherapist Anson Ko gives health talks and workshops and provides on-field physiotherapy support for companies, schools, sports teams and community groups.",
  "page_intro": "Health talks, workshops and on-field physiotherapy support for companies, schools, sports teams and community groups.",
  "talks_h": "Talks and workshops",
  "talks_p": "I give health talks and workshops for companies, schools, sports teams and community groups. The focus is health education, with demonstrations and practice so participants leave with methods they can use in daily life.",
  "for": "For",
  "talks_for": ["Companies and workplaces", "Schools", "Sports teams and clubs", "Community groups and care homes"],
  "topics_h": "Common topics",
  "topics": ["Pain and everyday exercise", "Neck, shoulder and back pain at the office", "Injury prevention for running, hiking and ball sports",
             "Competition preparation: sleep, warm-up and recovery", "Strength and fall prevention for older adults"],
  "recent_h": "Recent talks",
  "recent": [("October 2026", "Pain and exercise workshop for older adults (community organisation; one hour, with demonstrations and practice)"),
             ("October 2026", "Race-week preparation talk (secondary school swim team)")],
  "field_h": "On-field support",
  "field_p": "I provide field-side physiotherapy for sports teams and events, managing injuries during training and competition and working with coaches and the team's medical staff.",
  "field_for": ["Sports teams", "School teams", "Competitions and sports events"],
  "field_what_h": "What's included",
  "field_what": ["Field-side injury assessment and immediate care", "Taping and pre-competition preparation", "Post-match recovery",
                 "Deciding whether an athlete can continue, and planning the return to training"],
  "field_exp_h": "Experience",
  "field_exp": ["Team Physiotherapist, Hong Kong Water Polo Team (current)",
                "2025 National Games of China: on-site injury management and recovery for the Hong Kong water polo team",
                "Field-side physiotherapist, Hong Kong Football Club (Hong Kong Premier League), two consecutive seasons",
                "Physiotherapy support for Diocesan Boys' School sports teams"],
  "ask_h": "Enquiries", "ask_p": "Dates, venues and content for talks and on-field support can be arranged to suit you.",
  "more": "Learn more",
  "teaser_talks": "Health talks and workshops for companies, schools, sports teams and community groups.",
  "teaser_field": "Field-side physiotherapy for sports teams and events.",
  "talk_alt": "A physiotherapist presenting in front of a screen; participants hold exercise handouts",
  "field_alt": "A physiotherapist checking a player's shoulder movement",
  "field_media": [("video", "img/media/event-room", "A treatment area set up for an event", "A treatment area set up in advance, with several treatment tables and tables of supplies"),
                  ("img", "img/field-ankle.jpg", "Checking a player's ankle", "A physiotherapist bending over to check the ankle of a player lying on a mat")],
  "gallery_h": "The clinic",
  "gallery": [("img", "img/waiting-area.jpg", "Waiting area"), ("video", "img/media/gym-area", "Exercise area"),
              ("img", "img/treatment-room.jpg", "Treatment room"), ("img", "img/equipment.jpg", "Treatment equipment")],
  "way_h": "Finding the clinic",
  "way_steps": ["Enter Yes &amp; Right House (德拓大廈) at 1–3 Mody Road.", "Take the lift to 4/F.", "Ring the doorbell at the Amazing Medical glass door."],
  "way_bldg": "Yes &amp; Right House, 1–3 Mody Road", "way_bldg_alt": "The entrance of Yes &amp; Right House, showing the building sign and the street number 1–3 Mody Road",
  "way_door": "Amazing Medical, 4/F", "way_door_alt": "The Amazing Medical glass door and logo",
 },
}

CLIP_LABELS = {"zh": ("播放影片", "暫停影片"), "en": ("Play video", "Pause video")}

def clip(base, alt, lang):
    """A short silent loop. site.js plays it while it is on screen (never with reduced motion);
    without script the poster frame shows. The button pauses and resumes it."""
    play, pause = CLIP_LABELS[lang]
    return (f'<video class="clip" muted loop playsinline preload="none" poster="{base}.jpg" aria-label="{alt}">'
            f'<source src="{base}.mp4" type="video/mp4"></video>'
            f'<button class="clip-btn" type="button" aria-label="{play}" data-play="{play}" data-pause="{pause}"></button>')

def media(kind, src, alt, lang):
    return clip(src, alt, lang) if kind == "video" else f'<img src="{src}" alt="{alt}" loading="lazy">'

def gallery(lang):
    G = XC[lang]
    figs = "".join(f'<figure class="b{i + 1}">{media(kind, src, cap, lang)}<figcaption class="chip chip-dark">{cap}</figcaption></figure>'
                   for i, (kind, src, cap) in enumerate(G["gallery"]))
    return f'<section class="wrap reveal"><h2>{G["gallery_h"]}</h2><div class="bento stagger">{figs}</div></section>'

def wayfind(lang):
    G, L = XC[lang], T[lang]
    steps = "".join(f"<li><span>{s}</span></li>" for s in G["way_steps"])
    return f"""<section class="wrap reveal" id="find">
  <div class="section-head"><h2>{G["way_h"]}</h2><a class="pill line" href="{MAP_LINK}">{L["map"]}</a></div>
  <div class="way-grid">
    <figure class="w1"><img src="img/building-entrance.jpg" alt="{G["way_bldg_alt"]}" width="800" height="1000" loading="lazy">
      <figcaption class="chip chip-dark">{G["way_bldg"]}</figcaption></figure>
    <figure class="w2"><img src="img/clinic-door.jpg" alt="{G["way_door_alt"]}" width="1040" height="780" loading="lazy">
      <figcaption class="chip chip-dark">{G["way_door"]}</figcaption></figure>
    <ol class="way-steps">{steps}</ol>
  </div>
</section>"""

def talks_body(lang):
    G, L = XC[lang], T[lang]
    chips = lambda items: "".join(f'<span class="chip-topic">{x}</span>' for x in items)
    li = lambda items: "".join(f"<li>{x}</li>" for x in items)
    recent = "".join(f'<li><time>{d}</time><span>{x}</span></li>' for d, x in G["recent"])
    field_figs = "".join(f'<figure><div class="frame">{media(kind, src, alt, lang)}</div><figcaption>{cap}</figcaption></figure>'
                         for kind, src, cap, alt in G["field_media"])
    return f"""<section class="wrap feature reveal" id="talks">
  <figure><img src="img/talk-workshop.jpg" alt="{G["talk_alt"]}" width="1440" height="898"></figure>
  <div class="feature-text">
    <h2>{G["talks_h"]}</h2>
    <p>{G["talks_p"]}</p>
    <div class="chips" aria-label="{G["for"]}">{chips(G["talks_for"])}</div>
    <h3>{G["topics_h"]}</h3>
    <ul class="ticks">{li(G["topics"])}</ul>
    <h3>{G["recent_h"]}</h3>
    <ul class="dated">{recent}</ul>
  </div>
</section>
<section class="wrap feature reverse reveal" id="onfield">
  <figure class="tall"><img src="img/field-shoulder.jpg" alt="{G["field_alt"]}" width="960" height="1200" loading="lazy"></figure>
  <div class="feature-text">
    <h2>{G["field_h"]}</h2>
    <p>{G["field_p"]}</p>
    <div class="chips" aria-label="{G["for"]}">{chips(G["field_for"])}</div>
    <h3>{G["field_what_h"]}</h3>
    <ul class="ticks">{li(G["field_what"])}</ul>
    <h3>{G["field_exp_h"]}</h3>
    <ul class="ticks">{li(G["field_exp"])}</ul>
  </div>
</section>
<div class="wrap reveal"><div class="media-row{" two" if len(G["field_media"]) == 2 else ""} stagger">{field_figs}</div></div>
<section class="wrap center reveal ask">
  <h2>{G["ask_h"]}</h2>
  <p>{G["ask_p"]}</p>
  <div class="actions"><a class="pill solid" href="{L["wa_talks_link"]}">{L["wa"]}</a></div>
</section>"""

def build_lang(lang, posts, twins):
    L, K = T[lang], C[lang]
    pages = {}
    stats = "".join(f'<div><p class="fig">{f}</p><h3>{h}</h3><p>{d}</p></div>' for f, h, d in K["stats"])
    steps = "".join(f"<li><div><b>{t}</b><span>{d}</span></div></li>" for t, d in K["steps"])
    faq = "".join(
        f'<details><summary>{q}</summary><div class="answer-text">{K[key] if key == "bring" else "<p>" + K[key] + "</p>"}</div></details>'
        for q, key in K["faq"])
    faq += f'<details><summary>{K["family_q"]}</summary><div class="answer-text"><p>{K["family_a"]}</p></div></details>'

    topic_links = "".join(f'<a href="articles.html#{topic_id(t)}">{t}</a>' for t in topics_of(posts))
    hero = f"""<section class="wrap blog-hero">
  <div class="bh-text">
    <h1>{K["blog_h1"]}</h1>
    <p class="lead">{K["blog_lead"]}</p>
    <div class="byline"><img src="img/anson-sq.jpg" alt=""><div><b>{L["name_short"]}</b><span>{L["title"]}</span></div></div>
    {f'<nav class="topic-links" aria-label="{K["topics_label"]}">{topic_links}</nav>' if topic_links else ""}
  </div>
  {hero_post(posts[0], lang) if posts else ""}
</section>"""
    more = (f"""<section class="wrap reveal">
  <div class="section-head"><h2>{L["more_posts"]}</h2><a class="pill line" href="articles.html">{L["all_posts"]}</a></div>
  {post_grid(posts[1:7], lang, "")}
</section>""" if len(posts) > 1 else "")

    pages["index.html"] = page(lang, "index.html", L["site_name"], K["home_desc"], hero, f"""{more}

<section class="wrap reveal">
  <div class="author-card">
    <img src="img/anson-sq.jpg" alt="{K["photo_alt"]}" width="400" height="400" loading="lazy">
    <div class="txt">
      <h2>{K["author_h"]}</h2>
      <p>{K["author_p"]}</p>
      <div class="actions"><a class="pill line" href="about.html">{L["about"] if lang == "en" else "關於我"}</a><a class="pill line" href="clinic-info.html">{L["clinic"]}</a></div>
    </div>
  </div>
</section>""", "index.html", business(lang))

    rows = "".join(f"<div><h2>{h}</h2><p>{d}</p></div>" for h, d in K["services_rows"])
    pages["services.html"] = page(lang, "services.html", K["services_t"], K["services_desc"],
        page_head(K["services_t"], K["intro_p"]),
        f"""<section class="wrap reveal"><div class="stats stagger">{stats}</div></section>
<div class="wrap"><div class="prose">
  <div class="rows">{rows}</div>
  <p>{K["limits"]}</p>
  <div class="actions"><a class="pill solid" href="first-visit.html">{K["first_visit_link"]}</a><a class="pill line" href="clinic-info.html">{L["clinic"]}</a></div>
</div></div>""", "services.html")

    pages["first-visit.html"] = page(lang, "first-visit.html", K["first_h"], K["fv_desc"],
        page_head(K["first_h"], K["first_p"]),
        f"""<section class="wrap reveal"><ol class="steps stagger">{steps}</ol></section>
<div class="wrap"><div class="faq reveal">
  <h2>{K["faq_h"]}</h2>
  <div class="faq-list">{faq}</div>
</div></div>
<div class="wrap"><div class="actions"><a class="pill solid" href="clinic-info.html">{L["clinic"]}</a></div></div>""", "first-visit.html")

    pages["clinic-info.html"] = page(lang, "clinic-info.html", L["clinic"], K["ci_desc"],
        page_head(L["clinic"], L["by_appt"] + ("。" if lang == "zh" else ".")),
        f"""{visit_block(L, lang, both_addresses=True)}
{wayfind(lang)}
{gallery(lang)}
<div class="wrap"><div class="prose">
  <h2>{K["fv_ref"]}</h2>
  <p>{K["referral"]}</p>
  <h2>{K["ci_family_h"]}</h2>
  {K["ci_family"]}
</div></div>""", "clinic-info.html", business(lang))

    pages["about.html"] = page(lang, "about.html", L["about"] if lang == "en" else "關於我", K["about_desc"],
        page_head(L["about"] if lang == "en" else "關於我", K["about_intro"]),
        f"""<div class="wrap about">
  <figure><img src="img/anson.jpg" alt="{K["photo_alt"]}" width="800" height="1000"></figure>
  <div class="prose bio">
    {K["bio"]}
    <p>{K["ig_line"].format(ig=INSTAGRAM)}</p>
    <div class="actions"><a class="pill solid" href="clinic-info.html">{L["clinic"]}</a><a class="pill line" href="first-visit.html">{K["first_visit_link"]}</a></div>
  </div>
</div>""", "about.html")

    G = XC[lang]
    pages["talks-onfield.html"] = page(lang, "talks-onfield.html", G["page_t"], G["page_desc"],
        page_head(G["page_t"], G["page_intro"]), talks_body(lang), "talks-onfield.html")

    pages["articles.html"] = page(lang, "articles.html", L["articles"], K["articles_desc"],
        page_head(L["articles"], K["articles_intro"].format(mins=mins_range(posts))), articles_body(posts, lang), "articles.html")

    pages["404.html"] = page(lang, "404.html", K["nf_t"], K["nf_t"], page_head(K["nf_t"]),
        f'<div class="wrap"><a class="pill solid" href="index.html">{K["nf_link"]}</a></div>')

    for x in posts:
        pages[f'articles/{x["slug"]}.html'] = article_page(x, posts, lang, twins)
    return pages

# ---------- build ----------

def build():
    posts = {"zh": load_posts("posts"), "en": load_posts("posts-en")}
    twins = {x["slug"] for x in posts["zh"]} & {x["slug"] for x in posts["en"]}
    shutil.rmtree(OUT, ignore_errors=True)
    written = []
    for lang in LANGS:
        for path, text in build_lang(lang, posts[lang], twins).items():
            if lang == "en" and path == "404.html":
                continue                      # one site-wide 404 page (Chinese, with the language switch)
            full = PREFIX[lang] + path
            os.makedirs(os.path.dirname(os.path.join(OUT, full)) or OUT, exist_ok=True)
            open(os.path.join(OUT, full), "w", encoding="utf-8").write(text)
            written.append(full)
    shutil.copy(os.path.join(ROOT, "src", "style.css"), OUT)
    shutil.copy(os.path.join(ROOT, "src", "site.js"), OUT)
    shutil.copytree(os.path.join(ROOT, "src", "img"), os.path.join(OUT, "img"))
    open(os.path.join(OUT, "img", "covers", "default.svg"), "w", encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#a9bbdc"/><stop offset="1" stop-color="#eaf0f9"/></linearGradient></defs>'
        '<rect width="1600" height="900" fill="url(#g)"/><circle cx="1250" cy="220" r="280" fill="#fff" opacity=".35"/>'
        '<circle cx="260" cy="760" r="320" fill="#fff" opacity=".3"/></svg>')
    open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#48658f"/><stop offset="1" stop-color="#b3c4dc"/></linearGradient></defs>'
        '<rect width="64" height="64" rx="16" fill="url(#g)"/>'
        '<text x="32" y="43" font-size="32" text-anchor="middle" fill="#ffffff" font-family="sans-serif">高</text></svg>')
    if not PREVIEW:
        urls = [u for u in written if not u.endswith("404.html")]
        sm = "".join(f"<url><loc>{SITE_URL}/{u[:-len('index.html')] if u.endswith('index.html') else u}</loc></url>" for u in urls)
        open(os.path.join(OUT, "sitemap.xml"), "w").write(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
        open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
        open(os.path.join(OUT, "CNAME"), "w").write("www.wwwphysio.com")
        open(os.path.join(OUT, ".nojekyll"), "w").write("")
    n_todo = sum(open(os.path.join(OUT, u), encoding="utf-8").read().count('class="todo"') for u in written)
    print(f"Built {len(written)} pages into {OUT}. Facts still to confirm: {n_todo}")

if __name__ == "__main__":
    build()
