"""Build the static site for www.wwwphysio.com.

Usage:  python3 build.py            -> dist/     (the real website)
        python3 build.py --preview  -> preview/  (same site; index.html without the
                                                  document skeleton, for a Claude artifact preview)
Add an article: drop an HTML fragment with a JSON header comment into posts/, then rebuild.
"""
import html, json, os, re, shutil, sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))  # this folder holds posts/ and src/
PREVIEW = "--preview" in sys.argv
OUT = os.path.join(ROOT, "preview" if PREVIEW else "dist")
SITE_URL = "https://www.wwwphysio.com"
SITE_NAME = "高浩維 Anson Ko｜註冊物理治療師"
WA_NUMBER = "5592 9407"
WA_LINK = "https://wa.me/85255929407"
MAP_LINK = "https://maps.app.goo.gl/wyFuP1kzYqcNsBYn6"
ADDRESS_ZH = "九龍尖沙咀麼地道 1–3 號德拓大廈 4 樓全層（Amazing Medical）"
ADDRESS_EN = "4/F, Yes & Right House, 1–3 Mody Road, Tsim Sha Tsui, Kowloon"
INSTAGRAM = "https://www.instagram.com/ansonko_physio/"
FACEBOOK = "https://www.facebook.com/Ansonkophysio"
FONTS = ("https://fonts.googleapis.com/css2?family=LXGW+WenKai+TC:wght@400;700"
         "&family=Noto+Sans+TC:wght@400;500;700&display=swap")

NAV = [("index.html", "首頁"), ("services.html", "服務範圍"), ("first-visit.html", "首次診症"),
       ("clinic-info.html", "診所資料"), ("articles.html", "文章"), ("about.html", "關於我")]

def todo(text):
    """Facts still to confirm: highlighted on the page, and counted at build time."""
    return f'<span class="todo">{text}</span>'

HOURS_DL = """<dl class="hours">
  <dt>星期二至五</dt><dd>10:00–19:00</dd>
  <dt>星期六</dt><dd>09:30–14:00</dd>
  <dt>星期日、一</dt><dd>休息</dd>
  <dt>公眾假期</dt><dd>休息</dd>
</dl>"""

# ---------- shared parts ----------

def header(active, p):
    links = "".join(
        f'<a href="{p}{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for href, label in NAV)
    return f"""<header class="site-header"><div class="wrap">
  <a class="brand" href="{p}index.html"><b>高浩維 Anson Ko</b><span>註冊物理治療師｜尖沙咀</span></a>
  <nav class="nav nav-wide" aria-label="主要">{links}</nav>
  <details class="menu"><summary>選單</summary><nav class="nav" aria-label="主要">{links}</nav></details>
</div></header>"""

def footer(p):
    return f"""<footer class="band"><div class="wrap">
  <h2>應診資料</h2>
  <div class="cols">
    <div><h3>應診時間</h3>{HOURS_DL}<p class="small" style="color:var(--band-muted)">所有診症均需預約</p></div>
    <div><h3>地址</h3><p>{ADDRESS_ZH}</p><p><a href="{MAP_LINK}">Google 地圖</a></p></div>
    <div><h3>聯絡</h3><p>WhatsApp：<a href="{WA_LINK}">{WA_NUMBER}</a></p>
      <p><a href="{INSTAGRAM}">Instagram</a>　<a href="{FACEBOOK}">Facebook</a></p></div>
  </div>
  <div class="fine"><span>本網站內容只供一般參考，不能取代專業診斷及治療。</span>
    <span>© {date.today().year} 高浩維 Anson Ko</span></div>
</div></footer>"""

def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>")

BUSINESS = {
    "@context": "https://schema.org", "@type": "Physiotherapy",
    "name": SITE_NAME, "url": SITE_URL + "/", "image": SITE_URL + "/img/anson.jpg",
    "telephone": "+852 5592 9407",
    "address": {"@type": "PostalAddress", "streetAddress": "麼地道 1–3 號德拓大廈 4 樓全層",
                "addressLocality": "尖沙咀", "addressRegion": "九龍", "addressCountry": "HK"},
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification",
         "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "10:00", "closes": "19:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "09:30", "closes": "14:00"}],
    "employee": {"@type": "Person", "name": "高浩維 Anson Ko", "jobTitle": "註冊物理治療師"},
}

def page(path, title, desc, body, active=None, ld=None, og_type="website"):
    depth = path.count("/")
    p = "../" * depth
    full_title = title if title == SITE_NAME else f"{title}｜{SITE_NAME}"
    canonical = SITE_URL + "/" + ("" if path == "index.html" else path)
    head_bits = f"""<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/img/anson.jpg">
<meta property="og:locale" content="zh_HK">
<link rel="icon" href="{p}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{p}style.css">
{jsonld(ld) if ld else ""}"""
    content = f"{header(active, p)}\n<main>\n{body}\n</main>\n{footer(p)}"
    if PREVIEW and path == "index.html":
        # Artifact pages are wrapped in their own skeleton: no doctype/html/head/body here.
        first, rest = head_bits.split("\n", 1)
        return f'{first}\n<meta name="claude:viewport-fit-sides" content="cover">\n{rest}\n{content}\n'
    return f"""<!doctype html>
<html lang="zh-Hant-HK">
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

def load_posts():
    posts = []
    d = os.path.join(ROOT, "posts")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html"):
            continue
        raw = open(os.path.join(d, f), encoding="utf-8").read()
        m = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S)
        meta = json.loads(m.group(1)); meta["body"] = m.group(2).strip()
        posts.append(meta)
    return sorted(posts, key=lambda x: x["date"], reverse=True)

def fmt_date(iso):
    y, mo, dd = iso.split("-")
    return f"{int(y)} 年 {int(mo)} 月 {int(dd)} 日"

def post_list(posts, p, limit=None):
    items = "".join(
        f'<li><time datetime="{x["date"]}">{fmt_date(x["date"])}</time>'
        f'<a href="{p}articles/{x["slug"]}.html">{x["title"]}</a><p>{x["description"]}</p></li>'
        for x in posts[:limit])
    return f'<ul class="posts">{items}</ul>' if posts else '<p class="small">文章即將推出。</p>'

def article_page(x):
    reel = (f'<p>相關短片：<a href="{x["reel"]}">在 Instagram 觀看</a></p>' if x.get("reel") else "")
    body = f"""<article class="wrap prose">
  <p class="eyebrow">{x.get("topic", "")}</p>
  <h1>{x["title"]}</h1>
  <p class="meta"><span>作者：高浩維 Anson Ko，註冊物理治療師</span><span>發佈：{fmt_date(x["date"])}</span><span>最後更新：{fmt_date(x["updated"])}</span></p>
  {x["body"]}
  {reel}
  <div class="author"><img src="../img/anson-sq.jpg" alt="高浩維 Anson Ko" width="64" height="64">
    <div><p><b>高浩維 Anson Ko</b></p><p class="small">註冊物理治療師｜<a href="../about.html">關於我</a></p></div></div>
  <p class="note">本文只供一般參考，不能取代專業診斷及治療。如症狀持續或出現警號，請諮詢醫生或物理治療師。</p>
</article>"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": x["title"],
          "description": x["description"], "inLanguage": "zh-HK",
          "datePublished": x["date"], "dateModified": x["updated"],
          "author": {"@type": "Person", "name": "高浩維 Anson Ko", "jobTitle": "註冊物理治療師",
                     "url": SITE_URL + "/about.html"},
          "mainEntityOfPage": f'{SITE_URL}/articles/{x["slug"]}.html',
          "image": SITE_URL + "/img/anson.jpg"}
    return page(f'articles/{x["slug"]}.html', x["title"], x["description"], body, "articles.html", ld, "article")

# ---------- pages ----------

def build():
    posts = load_posts()
    pages = {}

    pages["index.html"] = page("index.html", SITE_NAME,
        "高浩維 Anson Ko，香港註冊物理治療師，於尖沙咀 Amazing Medical 應診。服務包括肩頸腰背痛、運動創傷及手術後復康，並以廣東話簡單講解痛症知識。",
        f"""<section class="wrap hero">
  <div class="hero-text">
    <p class="eyebrow">註冊物理治療師｜尖沙咀</p>
    <h1>高浩維 Anson Ko</h1>
    <p class="lead">用廣東話簡單講解痛症和運動創傷</p>
    <p>於尖沙咀 Amazing Medical 應診，服務包括肩頸腰背痛、運動創傷及手術後復康。</p>
    <div class="actions"><a class="btn" href="{WA_LINK}">WhatsApp 查詢</a><a class="btn outline" href="clinic-info.html">診所資料</a></div>
  </div>
  <figure><img src="img/anson.jpg" alt="註冊物理治療師高浩維 Anson Ko" width="800" height="1000"></figure>
</section>

<section class="wrap" aria-label="應診資料">
  <div class="facts">
    <div><h3>應診時間</h3>{HOURS_DL}</div>
    <div><h3>地址</h3><p>{ADDRESS_ZH}</p><p class="small">到達 4 樓後請按門鐘</p></div>
    <div><h3>聯絡</h3><p>WhatsApp：<a href="{WA_LINK}">{WA_NUMBER}</a></p><p class="small">所有診症均需預約</p></div>
  </div>
</section>

<section class="wrap">
  <h2>服務範圍</h2>
  <div class="svc">
    <div><h3>肩頸、腰背及關節痛</h3><p>例如長時間坐著工作引起的痛楚、膝關節退化</p></div>
    <div><h3>運動創傷</h3><p>例如扭傷、拉傷、行山或跑步後的膝蓋痛</p></div>
    <div><h3>手術後復康</h3><p>例如膝關節或髖關節置換手術後的康復訓練</p></div>
  </div>
  <p><a href="services.html">服務範圍詳情</a>　　<a href="first-visit.html">首次診症須知</a></p>
</section>

<section class="wrap">
  <h2>診所環境</h2>
  <div class="gallery-scroll"><div class="gallery">
    <figure><img src="img/treatment-room.jpg" alt="物理治療室，設有電動治療床" width="900" height="1200" loading="lazy"><figcaption>治療室</figcaption></figure>
    <figure><img src="img/gym-area.jpg" alt="運動訓練區，設有訓練架及彈力帶" width="900" height="1200" loading="lazy"><figcaption>運動訓練區</figcaption></figure>
    <figure><img src="img/reception.jpg" alt="Amazing Medical 接待處" width="900" height="1200" loading="lazy"><figcaption>接待處</figcaption></figure>
  </div></div>
</section>

<section class="wrap">
  <h2>最新文章</h2>
  {post_list(posts, "", 3)}
  <p><a href="articles.html">所有文章</a></p>
</section>""", "index.html", BUSINESS)

    pages["services.html"] = page("services.html", "服務範圍",
        "高浩維 Anson Ko 的物理治療服務：肩頸、腰背及關節痛、運動創傷、手術後復康。於尖沙咀 Amazing Medical 應診。",
        f"""<div class="wrap page-head"><h1>服務範圍</h1>
  <p>物理治療透過評估、運動訓練、手法治療及其他物理治療方法，幫助改善痛楚和活動能力。</p></div>
<div class="wrap prose">
  <h2>肩頸、腰背及關節痛</h2>
  <p>例如長時間坐著工作引起的肩頸或腰背痛楚、手腕及手肘痛、膝關節退化。</p>
  <h2>運動創傷</h2>
  <p>例如扭傷、拉傷、行山或跑步後的膝蓋痛，以及重複出現的舊患。</p>
  <h2>手術後復康</h2>
  <p>例如膝關節或髖關節置換手術後，以及韌帶手術後的康復訓練。</p>
  <h2>平衡及肌力訓練</h2>
  <p>{todo("確認是否提供")} 例如為減少跌倒風險而設的平衡及肌力運動。</p>
  <p>治療效果因人而異。評估後，我會向你解釋治療計劃、預計所需時間，以及治療的限制。如症狀持續或出現警號，請諮詢醫生或物理治療師。</p>
  <div class="actions"><a class="btn outline" href="first-visit.html">首次診症須知</a><a class="btn outline" href="clinic-info.html">診所資料</a></div>
</div>""", "services.html")

    pages["first-visit.html"] = page("first-visit.html", "首次診症",
        "首次物理治療診症約 45–60 分鐘：了解病歷、身體檢查、解釋評估結果及治療計劃。請帶備轉介信或報告（如有）。收費每節 HK$900。",
        """<div class="wrap page-head"><h1>首次診症</h1><p>首次診症約 45–60 分鐘。</p></div>
<div class="wrap prose">
  <h2>診症內容</h2>
  <ol><li>了解病歷及症狀</li><li>身體檢查及活動能力評估</li><li>解釋評估結果及治療計劃</li><li>按需要開始治療，並教授家居運動</li></ol>
  <h2>請帶備</h2>
  <ul><li>醫生轉介信、診斷書或相關報告（如有）</li><li>X 光或磁力共振報告（如有）</li><li>正在服用的藥物名單</li><li>方便活動的衣服</li></ul>
  <h2>收費</h2>
  <p>物理治療每節 HK$900（45–60 分鐘）。其他治療項目收費，歡迎 WhatsApp 查詢。</p>
  <h2>需要醫生轉介信嗎？</h2>
  <p>首次預約前，請以 WhatsApp 查詢你的情況是否需要醫生轉介信。如已有轉介信、診斷書或相關報告，請於首次診症時帶備。</p>
  <div class="actions"><a class="btn outline" href="clinic-info.html">診所資料</a></div>
</div>""", "first-visit.html")

    pages["clinic-info.html"] = page("clinic-info.html", "診所資料",
        "應診時間、地址及交通：九龍尖沙咀麼地道 1–3 號德拓大廈 4 樓全層（Amazing Medical）。WhatsApp 5592 9407。",
        f"""<div class="wrap page-head"><h1>診所資料</h1><p>所有診症均需預約。</p></div>
<div class="wrap prose">
  <h2>應診時間</h2>
  {HOURS_DL}
  <h2>地址</h2>
  <p>{ADDRESS_ZH}</p>
  <p class="small">{ADDRESS_EN}</p>
  <ul><li>交通：港鐵{todo("尖沙咀／尖東")}站 {todo("X")} 出口，步行約 {todo("X")} 分鐘</li><li>大廈設有升降機，到達 4 樓後請按門鐘。</li></ul>
  <div class="actions"><a class="btn outline" href="{MAP_LINK}">Google 地圖</a></div>
  <h2>聯絡</h2>
  <p>WhatsApp：{WA_NUMBER}</p>
  <div class="actions"><a class="btn" href="{WA_LINK}">WhatsApp 查詢</a></div>
  <h2>需要醫生轉介信嗎？</h2>
  <p>首次預約前，請以 WhatsApp 查詢你的情況是否需要醫生轉介信。如已有轉介信、診斷書或相關報告，請於首次診症時帶備。</p>
  <h2>給家人的資料</h2>
  <p>如你為父母或家人查詢或預約，可直接以 WhatsApp 聯絡，並提供：</p>
  <ul><li>家人的大致情況（例如哪裡痛、是否剛做完手術）</li><li>方便的時間</li></ul>
  <p>{todo("家人可陪同首次診症。")} 如家人行動不便或需要輪椅，請預先告知，以便安排。</p>
</div>""", "clinic-info.html", BUSINESS)

    pages["about.html"] = page("about.html", "關於我",
        "高浩維 Anson Ko，香港註冊物理治療師，於尖沙咀 Amazing Medical 應診。",
        f"""<div class="wrap hero">
  <div class="hero-text"><h1>關於我</h1>
    <p class="lead">高浩維 Anson Ko</p>
    <ul class="prose" style="padding-left:1.2em">
      <li>香港註冊物理治療師 Registered Physiotherapist RPT(HK)</li>
      <li>BSc (Hons) Physiotherapy (HKPU) {todo("按管理委員會認可格式確認")}</li>
      <li>前港隊水球運動員</li>
      <li>語言：廣東話、英語</li>
    </ul>
    <p>診症地點：Amazing Medical，尖沙咀麼地道 1–3 號德拓大廈 4 樓全層</p>
    <div class="actions"><a class="btn outline" href="clinic-info.html">診所資料</a></div>
  </div>
  <figure><img src="img/anson.jpg" alt="註冊物理治療師高浩維 Anson Ko" width="800" height="1000"></figure>
</div>""", "about.html")

    pages["articles.html"] = page("articles.html", "文章",
        "註冊物理治療師高浩維 Anson Ko 以簡單易明的方式講解肩頸痛、腰痛、運動創傷等常見問題。",
        f"""<div class="wrap page-head"><h1>文章</h1><p>用簡單的方式，講解常見痛症和運動創傷。</p></div>
<div class="wrap prose">{post_list(posts, "")}</div>""", "articles.html")

    pages["404.html"] = page("404.html", "找不到頁面", "找不到頁面。",
        """<div class="wrap page-head"><h1>找不到頁面</h1><p><a href="index.html">返回首頁</a></p></div>""")

    for x in posts:
        pages[f'articles/{x["slug"]}.html'] = article_page(x)

    # ---------- write ----------
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "articles"))
    for path, text in pages.items():
        open(os.path.join(OUT, path), "w", encoding="utf-8").write(text)
    shutil.copy(os.path.join(ROOT, "src", "style.css"), OUT)
    shutil.copytree(os.path.join(ROOT, "src", "img"), os.path.join(OUT, "img"))
    open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#15191d"/>'
        '<text x="32" y="44" font-size="34" text-anchor="middle" fill="#ffffff" font-family="sans-serif">高</text></svg>')
    if not PREVIEW:
        urls = [p for p in pages if p != "404.html"]
        sm = "".join(f"<url><loc>{SITE_URL}/{'' if u == 'index.html' else u}</loc></url>" for u in urls)
        open(os.path.join(OUT, "sitemap.xml"), "w").write(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
        open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
        open(os.path.join(OUT, "CNAME"), "w").write("www.wwwphysio.com\n")
        open(os.path.join(OUT, ".nojekyll"), "w").write("")
    n_todo = sum(t.count('class="todo"') for t in pages.values())
    print(f"Built {len(pages)} pages into {OUT}. Facts still to confirm: {n_todo}")

if __name__ == "__main__":
    build()
