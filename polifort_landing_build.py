# -*- coding: utf-8 -*-
"""
ПОЛИФОРТ — генератор одностраничного сайта, редакция V1.1.

Запуск:   python3 polifort_landing_build.py
Результат:
  site/index.html              — версия для хостинга (картинки отдельными файлами в site/assets/)
  Polifort_Landing.html        — один файл со всеми картинками внутри (для писем, мессенджеров,
                                 показа заказчику без хостинга; НЕ для хостинга)
  Polifort_site_deploy.zip     — архив для загрузки на хостинг (site/ + инструкция)

ВСЁ, ЧТО НУЖНО ПОПРАВИТЬ ПЕРЕД ПУБЛИКАЦИЕЙ, СОБРАНО В СЛОВАРЕ CONFIG:
телефоны, email, ставки калькулятора, адрес сайта.
Пометки [ЗАМЕНИТЬ] и [ПРОВЕРИТЬ] — места, требующие решения руководителя.
"""
import base64, os, shutil, pathlib, zipfile
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent            # deliverables/
WS = ROOT.parent                                          # корень workspace
ASSETS = WS / "assets"                                    # фото, подготовленные из презентации/АТР
WEBLOGO = WS / "work" / "web"                             # веб-размеры официальных логотипов
SITE = ROOT / "site"                                      # папка для хостинга

# ============================== CONFIG ======================================
CONFIG = {
    # [ПРОВЕРИТЬ] В карточке предприятия и брендбуке указан +7 (922) 090-60-90,
    # в презентации от 28.09.26 — +7 (995) 302-29-48. Сейчас на сайте оба мобильных.
    # Оставьте один основной, если нужно, и пересоберите сайт.
    "mob1": "+7 (995) 302-29-48",
    "mob2": "+7 (922) 090-60-90",
    "office": "+7 (3452) 60-62-38",
    "email": "mail@poly-fort.ru",
    # [ЗАМЕНИТЬ] домен после подключения хостинга; используется в canonical/og/robots
    "base_url": "https://poly-fort.ru",
    "address": "625502, Тюменская область, м.о. Тюменский, д. Ушакова, ул. Вольная, д. 12",
    "inn": "7224100558",
    "ogrn": "1267200010648",

    # Статус Huntsman. Письмо о представительстве выдано на прежнюю организацию;
    # Полифорт продолжает работу в регионе. На сайте формулировка — «представитель
    # Huntsman NMG в Тюменской области» без слова «официальный» и без ссылки на письмо.
    # РЕКОМЕНДАЦИЯ: запросить у ЗАО «Хантсман-НМГ» письмо-подтверждение на ООО «ПОЛИФОРТ»
    # (ИНН 7224100558) — после этого можно вернуть формулировку «официальный представитель».
    "huntsman_status": "Представитель Huntsman NMG в Тюменской области",

    # Производительность: формулировка привязана к типовому основанию и смене
    # (платформа бренда запрещает «всегда 200 м² на любом объекте»).
    "speed": "от 200 м² за смену",
    "warranty": "3 года",
    "service_life": "25 лет",

    # ---- СТАВКИ КАЛЬКУЛЯТОРА: [ЗАМЕНИТЬ] на свою фактическую экономику ----
    # Значения ниже — ОРИЕНТИРОВОВОЧНЫЕ ВИЛКИ для предварительного расчёта.
    # Это НЕ оферта: на сайте стоит дисклеймер «точно — после обследования».
    "rates": {
        "wm_mat": 3420,    # руб/м² материалы: праймер + полимочевина 2 мм + защитный слой ПОЛИФЛЕКС 105
        "wm_work": 1200,   # руб/м² работы по гидроизоляции (подготовка, нанесение, контроль)
        "ppu50": 1676,    # руб/м² доплата за слой ППУ 50 мм (материал+работа)
        "ppu100": 2852,   # руб/м² доплата за слой ППУ 100 мм (материал+работа)
        "spread": 0.15,   # разброс вилки, доли
        "k_base": {"ok": 1.00, "bad": 1.15, "metal": 1.10},   # состояние основания
        "k_geo": {"tyu": 1.00, "hmao": 1.15, "yanao": 1.30},  # регион (логистика, проживание)
    },
}
C = CONFIG

# ============================== ИЗОБРАЖЕНИЯ =================================
PHOTOS = {          # ключ -> файл в assets/ (подготовлены из презентации и АТР)
    "hero": "img_hero_roof.jpg",
    "case_after": "img_case_after.jpg",
    "case_parapet": "img_case_before_parapet.jpg",
    "case_legs": "img_case_before_legs.jpg",
    "case_joint": "img_case_joint.jpg",
    "dome": "img_polyurea_dome.jpg",
    "atr121": "atr_uzel_12_1.jpg",
    "atr12283": "atr_uzel_12_28_3.jpg",
    "atr12291": "atr_uzel_12_29_1.jpg",
}
LOGOS = {           # ключ -> файл в work/web/ (официальный лого-комплект, веб-размеры)
    "logo_h_color": "logo_horizontal_color.png",
    "logo_h_white": "logo_horizontal_white.png",
    "fav180": "favicon-180.png",
    "fav512": "favicon-512.png",
    "og": "og-image.png",
}

MODE = "embed"      # переключается при сборке: "embed" | "site"

def _b64(path):
    data = pathlib.Path(path).read_bytes()
    mime = "image/jpeg" if str(path).endswith((".jpg", ".jpeg")) else "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode()

def A(key):
    """Возвращает ссылку на ассет: data-URI (embed) или относительный путь (site)."""
    if key in PHOTOS:
        rel = "assets/img/" + PHOTOS[key]
        src = ASSETS / PHOTOS[key]
    else:
        rel = "assets/logo/" + LOGOS[key]
        src = WEBLOGO / LOGOS[key]
    return _b64(src) if MODE == "embed" else rel

# ============================== ИКОНКИ ======================================
def icon(path):
    return f'<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'

IC = {
 "flame":  icon('<path d="M32 8c6 8 14 13 14 24a14 14 0 0 1-28 0c0-6 3-10 6-14 1 4 3 6 6 7-2-6-1-12 2-17z"/><line x1="10" y1="54" x2="54" y2="10" stroke="#00D7CD"/>'),
 "crane":  icon('<line x1="12" y1="52" x2="52" y2="52"/><line x1="20" y1="52" x2="20" y2="16"/><line x1="14" y1="16" x2="46" y2="16"/><line x1="40" y1="16" x2="40" y2="28"/><rect x="35" y="28" width="10" height="8"/><line x1="8" y1="58" x2="56" y2="6" stroke="#00D7CD"/>'),
 "seam":   icon('<path d="M8 40 L24 28 L40 40 L56 28"/><path d="M8 48 L24 36 L40 48 L56 36" stroke="#00D7CD"/>'),
 "speed":  icon('<circle cx="32" cy="36" r="18"/><path d="M32 36 L42 26"/><path d="M18 20 L10 12 M46 20 L54 12"/>'),
 "shield": icon('<path d="M32 8 L52 16 V32 C52 44 44 52 32 56 C20 52 12 44 12 32 V16 Z"/><path d="M24 32 L30 38 L42 26" stroke="#00D7CD"/>'),
 "box":    icon('<path d="M12 22 L32 12 L52 22 L52 44 L32 54 L12 44 Z"/><path d="M12 22 L32 32 L52 22 M32 32 V54"/><path d="M22 17 L42 27" stroke="#00D7CD"/>'),
 "draw":   icon('<rect x="10" y="10" width="44" height="34"/><path d="M10 22 H54 M22 22 V44"/><path d="M28 30 H48 M28 36 H44" stroke="#00D7CD"/><line x1="18" y1="52" x2="46" y2="52"/>'),
 "pin":    icon('<path d="M32 56 C20 42 14 34 14 26 a18 18 0 0 1 36 0 c0 8-6 16-18 30z"/><circle cx="32" cy="26" r="6" stroke="#00D7CD"/>'),
 "doc":    icon('<path d="M16 8 H40 L50 18 V56 H16 Z"/><path d="M40 8 V18 H50"/><path d="M24 30 H42 M24 38 H42 M24 46 H36" stroke="#00D7CD"/>'),
 "drop":   icon('<path d="M32 8 C42 22 48 30 48 38 a16 16 0 0 1-32 0 c0-8 6-16 16-30z"/><path d="M24 40 a8 8 0 0 0 8 8" stroke="#00D7CD"/>'),
 "thermo": icon('<path d="M26 12 a6 6 0 0 1 12 0 v24 a10 10 0 1 1-12 0z"/><line x1="32" y1="22" x2="32" y2="42" stroke="#00D7CD"/><circle cx="32" cy="46" r="4" stroke="#00D7CD"/>'),
}

# ============================== CSS =========================================
CSS = """
:root{
  --g:#252A34; --t:#00D7CD; --td:#0A8F89; --ink:#2E3440; --mut:#5A6272;
  --line:#DCE0E6; --soft:#F5F7F9; --white:#fff;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:"DejaVu Sans","PT Sans","Segoe UI",Arial,sans-serif;color:var(--ink);background:#fff;font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:var(--td);text-decoration:none}
h1,h2,h3,h4{color:var(--g);line-height:1.2;margin:0 0 .5em;font-weight:700;letter-spacing:-.01em}
h1{font-size:clamp(30px,5vw,52px)}
h2{font-size:clamp(24px,3.4vw,36px)}
h3{font-size:20px}
p{margin:0 0 14px}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.kicker{color:var(--td);font-weight:700;font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:10px}
.sec{padding:72px 0}
.sec.dark{background:var(--g);color:#C9CFD8}
.sec.dark h2,.sec.dark h3{color:#fff}
.sec.soft{background:var(--soft)}
.lead{font-size:18px;color:var(--mut);max-width:820px}
.sec.dark .lead{color:#AEB6C2}
.rule{height:4px;width:52px;background:var(--t);border-radius:2px;margin:0 0 26px}

.topbar{background:var(--g);color:#9AA3B2;font-size:12.5px;padding:7px 0}
.topbar .wrap{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.topbar b{color:#fff;font-weight:700}
.topbar .dot{color:var(--t)}

header.nav{position:sticky;top:0;z-index:60;background:#fff;border-bottom:1px solid var(--line)}
header.nav .wrap{display:flex;align-items:center;gap:18px;height:70px}
.brand{display:flex;align-items:center;gap:12px}
.brand img{height:38px;width:auto}
nav.menu{display:flex;gap:2px;margin-left:auto;flex-wrap:wrap}
nav.menu a{color:var(--ink);font-size:13.5px;padding:8px 10px;border-radius:6px}
nav.menu a:hover{background:var(--soft);color:var(--td)}
.navtel{margin-left:8px;text-align:right;font-size:13px;color:var(--mut);line-height:1.3;white-space:nowrap}
.navtel a{display:block;color:var(--g);font-weight:700;font-size:14.5px;white-space:nowrap}
.navtel .office{white-space:nowrap}
.burger{display:none;margin-left:auto;background:none;border:1px solid var(--line);border-radius:6px;padding:8px 10px;font-size:16px;color:var(--g);cursor:pointer}

.btn{display:inline-block;background:var(--t);color:#0B3B39;font-weight:700;padding:14px 26px;border-radius:8px;border:none;cursor:pointer;font-size:15px;font-family:inherit}
.btn:hover{filter:brightness(1.06)}
.btn.ghost{background:transparent;color:#fff;border:2px solid rgba(255,255,255,.45)}
.btn.ghost:hover{border-color:#fff}
.btn.line{background:transparent;color:var(--td);border:2px solid var(--t)}
.btn.sm{padding:10px 18px;font-size:13.5px}

.hero{position:relative;background:var(--g);color:#fff;overflow:hidden}
.hero .bg{position:absolute;inset:0;background-size:cover;background-position:center 62%;opacity:.34}
.hero .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(37,42,52,.55) 0%,rgba(37,42,52,.86) 70%,#252A34 100%)}
.hero .wrap{position:relative;padding:84px 20px 64px}
.hero h1{color:#fff;max-width:820px}
.hero h1 em{font-style:normal;color:var(--t)}
.hero .sub{font-size:18px;color:#D5DAE2;max-width:760px;margin-bottom:26px}
.badges{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 30px}
.badge{background:rgba(0,215,205,.12);border:1px solid rgba(0,215,205,.5);color:#BFF7F4;border-radius:999px;padding:7px 14px;font-size:13px;font-weight:700}
.badge.solid{background:var(--t);color:#0B3B39;border-color:var(--t)}
.hero .cta{display:flex;gap:14px;flex-wrap:wrap}
.heroline{display:flex;gap:26px;flex-wrap:wrap;margin-top:40px;padding-top:22px;border-top:1px solid rgba(255,255,255,.16);font-size:13.5px;color:#AEB6C2}
.heroline b{color:#fff;display:block;font-size:15px}

.numbers{background:var(--t);color:#0B3B39}
.numbers .wrap{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:4px;padding:26px 20px}
.numbers div{text-align:center;padding:8px 6px}
.numbers b{display:block;font-size:30px;line-height:1.05}
.numbers span{font-size:12.5px;font-weight:700;opacity:.8}

.grid{display:grid;gap:18px}
.g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.g4{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:22px}
.card.soft{background:var(--soft)}
.card .ic{width:44px;height:44px;color:var(--g);margin-bottom:14px}
.card .ic svg{width:44px;height:44px}
.card h3{font-size:17px;margin-bottom:8px}
.card p{font-size:14px;color:var(--mut);margin:0}

.layers{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fff}
.layers .lr{display:flex;align-items:center;gap:14px;padding:12px 18px;border-bottom:1px solid var(--line);font-size:14px}
.layers .lr:last-child{border-bottom:none}
.layers .sw{width:64px;height:26px;border-radius:4px;flex:none}
.layers .lr b{color:var(--g)}
.layers .lr span{color:var(--mut);font-size:13px}

table.cmp{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;font-size:13.5px;box-shadow:0 1px 0 var(--line)}
table.cmp th,table.cmp td{padding:12px 12px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
table.cmp thead th{background:var(--g);color:#fff;font-size:13px}
table.cmp thead th.ours{background:var(--td)}
table.cmp td:first-child{font-weight:700;color:var(--g);width:22%}
table.cmp td.ours{background:#E9FBF9}
table.cmp tr:last-child td{border-bottom:none}
.yes{color:#0A8F89;font-weight:700}
.no{color:#B4443C;font-weight:700}
.mid{color:#8A6D1B;font-weight:700}

.casehead{display:flex;gap:26px;flex-wrap:wrap;align-items:baseline}
.casehead .big{font-size:34px;font-weight:700;color:var(--t)}
.gal{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:26px}
.gal figure{margin:0;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.gal img{width:100%;height:210px;object-fit:cover}
.gal figcaption{font-size:12.5px;color:var(--mut);padding:10px 12px}
.gal figcaption b{color:var(--g);display:block;margin-bottom:2px}

.atr{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
.atr figure{margin:0;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.atr .imgbox{background:#fff;padding:8px;border-bottom:1px solid var(--line)}
.atr img{width:100%;height:340px;object-fit:cover;object-position:top}
.atr figcaption{padding:12px 14px;font-size:13px;color:var(--mut)}
.atr figcaption b{color:var(--g);display:block;font-size:14px;margin-bottom:3px}

.mapbox{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px}
.mapbox svg{width:100%;height:auto;display:block}
.geo-cities{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.chip{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:12.5px;color:var(--g);font-weight:700}
.chip.t{background:#E9FBF9;border-color:#B7EFEB;color:#067C76}

.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px}
.step{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);border-radius:10px;padding:18px}
.step .n{font-size:12px;font-weight:700;color:var(--t);letter-spacing:.12em}
.step h3{color:#fff;font-size:16px;margin:6px 0 6px}
.step p{font-size:12.5px;color:#AEB6C2;margin:0}

details{background:#fff;border:1px solid var(--line);border-radius:10px;padding:0;margin-bottom:10px;overflow:hidden}
details summary{cursor:pointer;padding:16px 20px;font-weight:700;color:var(--g);font-size:15px;list-style:none;position:relative;padding-right:44px}
details summary::-webkit-details-marker{display:none}
details summary:after{content:"+";position:absolute;right:18px;top:12px;font-size:22px;color:var(--td);font-weight:700}
details[open] summary:after{content:"–"}
details .body{padding:0 20px 18px;font-size:14.5px;color:var(--mut)}
details[open] summary{border-bottom:1px solid var(--line)}

form.brief{background:#fff;border:1px solid var(--line);border-radius:12px;padding:26px;display:grid;gap:14px;grid-template-columns:1fr 1fr}
form.brief .full{grid-column:1/-1}
label{font-size:12.5px;font-weight:700;color:var(--g);display:block;margin-bottom:5px}
input,select,textarea{width:100%;font-family:inherit;font-size:14.5px;padding:11px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink)}
input:focus,select:focus,textarea:focus{outline:2px solid rgba(0,215,205,.5);border-color:var(--t)}
.formnote{font-size:12.5px;color:var(--mut)}
.formactions{display:flex;gap:12px;flex-wrap:wrap;align-items:center}

.calc{background:#fff;border:1px solid var(--line);border-radius:12px;padding:24px;display:grid;grid-template-columns:1.1fr .9fr;gap:24px}
.calc .fields{display:grid;gap:12px;grid-template-columns:1fr 1fr}
.calc .res{background:var(--g);border-radius:10px;padding:20px;color:#C9CFD8}
.calc .res .val{font-size:30px;font-weight:700;color:var(--t);line-height:1.15}
.calc .res ul{margin:12px 0 0;padding-left:18px;font-size:13px}
.calc .res li{margin-bottom:5px}
.calc .disc{font-size:11.5px;color:#8A93A2;margin-top:12px}

footer{background:var(--g);color:#9AA3B2;padding:44px 0;font-size:13px}
footer b{color:#fff}
footer .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:26px}
footer a{color:#C9CFD8}
footer img{height:34px;width:auto;margin-bottom:12px}
footer .fine{margin-top:26px;padding-top:18px;border-top:1px solid #3A4150;font-size:12px;color:#7C8595}

.mcall{display:none;position:fixed;right:16px;bottom:16px;z-index:80;background:var(--t);color:#0B3B39;border-radius:999px;padding:14px 20px;font-weight:700;box-shadow:0 8px 24px rgba(0,0,0,.25)}

.reveal{opacity:0;transform:translateY(14px);transition:opacity .5s ease,transform .5s ease}
.reveal.on{opacity:1;transform:none}
@media (prefers-reduced-motion: reduce){.reveal{opacity:1;transform:none;transition:none}}

@media (max-width:1150px){
  nav.menu{gap:0}
  nav.menu a{padding:7px 6px;font-size:12px}
  .navtel .office{display:none}
  .navtel{margin-left:4px;font-size:12px}
  .navtel a{font-size:13.5px}
  .brand img{height:32px}
}
@media (max-width:900px){
  nav.menu{display:none;position:absolute;top:70px;left:0;right:0;background:#fff;border-bottom:1px solid var(--line);flex-direction:column;padding:10px 16px}
  nav.menu.open{display:flex}
  .burger{display:block}
  .navtel{display:none}
  .calc{grid-template-columns:1fr}
  form.brief{grid-template-columns:1fr}
  .mcall{display:block}
  table.cmp{font-size:12.5px}
  table.cmp th,table.cmp td{padding:9px 8px}
  .brand img{height:30px}
}
@media print{header.nav,.mcall,.topbar{display:none}.sec{padding:24px 0}}
"""

# ============================== БЛОКИ =======================================
def kv(icon_name, title, text, cls=""):
    return f'''<div class="card {cls}"><div class="ic">{IC[icon_name]}</div><h3>{title}</h3><p>{text}</p></div>'''

def tel_href(t):
    return t.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")

TOPBAR = f'''
<div class="topbar"><div class="wrap">
  <span><b>Тюменская компания</b> — база в Тюменском районе</span>
  <span class="dot">●</span><span>Работаем: <b>Тюменская область · ХМАО-Югра · ЯНАО</b></span>
  <span class="dot">●</span><span style="margin-left:auto">{C['huntsman_status']}</span>
</div></div>'''

def header_html():
  return f'''
<header class="nav"><div class="wrap">
  <a class="brand" href="#top"><img src="{A('logo_h_color')}" alt="ПОЛИФОРТ — промышленные полимерные решения"><span class="sr">ПОЛИФОРТ</span></a>
  <button class="burger" id="burger" aria-label="Меню">☰</button>
  <nav class="menu" id="menu">
    <a href="#roof">Напыляемая кровля</a>
    <a href="#compare">Сравнение</a>
    <a href="#case">Объект</a>
    <a href="#designers">Проектировщикам</a>
    <a href="#calc">Расчёт</a>
    <a href="#geo">География</a>
    <a href="#faq">Вопросы</a>
    <a href="#contact">Контакты</a>
  </nav>
  <div class="navtel"><a href="tel:{tel_href(C['mob1'])}">{C['mob1']}</a><span class="office">офис {C['office']}</span></div>
</div></header>'''

def hero_html():
  return f'''
<section class="hero" id="top">
  <div class="bg" style="background-image:url('{A('hero')}')"></div>
  <div class="shade"></div>
  <div class="wrap">
    <img src="{A('logo_h_white')}" alt="ПОЛИФОРТ" style="height:46px;width:auto;margin-bottom:16px">
    <div class="kicker" style="color:var(--t)">Тюменская компания · защита в каждом слое</div>
    <h1>Напыляемая кровля, которую <em>не нужно переделывать каждый год</em></h1>
    <p class="sub">Теплоизоляция ППУ и гидроизоляция полимочевиной — сплошное бесшовное покрытие
    по существующей кровле, без демонтажа и открытого огня.
    Мы — тюменская компания: база и склад в Тюменском районе, работаем по Тюменской области, ХМАО и ЯНАО.</p>
    <div class="badges">
      <span class="badge solid">{C['huntsman_status']}</span>
      <span class="badge">Материалы на складе в Тюмени</span>
      <span class="badge">Напыляем {C['speed']}</span>
      <span class="badge">Гарантия {C['warranty']} по договору</span>
    </div>
    <div class="cta">
      <a class="btn" href="#contact">Обсудить объект</a>
      <a class="btn ghost" href="#calc">Получить предварительный расчёт</a>
    </div>
    <div class="heroline">
      <div><b>Тюменская область</b>Тюмень · Тобольск · Ишим · Ялуторовск · Заводоуковск</div>
      <div><b>ХМАО — Югра</b>Сургут · Нижневартовск · Нефтеюганск · Когалым · Ханты-Мансийск</div>
      <div><b>ЯНАО</b>Новый Уренгой · Ноябрьск · Губкинский · Муравленко · Салехард</div>
    </div>
  </div>
</section>

<div class="numbers"><div class="wrap">
  <div><b>200+</b><span>м² напыления за смену</span></div>
  <div><b>3 года</b><span>гарантия по договору</span></div>
  <div><b>25 лет</b><span>срок службы полимочевины</span></div>
  <div><b>≥480%</b><span>удлинение полимочевины до разрыва (ЭКСТРАПЛАН 503, АТР Huntsman)</span></div>
  <div><b>550 м²</b><span>кровля в Ноябрьске за 3 дня</span></div>
  <div><b>0</b><span>огневых работ на объекте</span></div>
</div></div>'''

PROBLEM = f'''
<section class="sec" id="problem">
  <div class="wrap">
    <div class="kicker">Почему кровля снова течёт</div>
    <h2>Слабые места рулонной кровли — не материал, а швы и цикл ремонта</h2>
    <div class="rule"></div>
    <p class="lead">Рулонное покрытие собирают из кусков на крыше. Каждое соединение — участок,
    который нужно герметизировать вручную. Со временем материал теряет эластичность, отслаивается,
    и вода находит путь именно в этих деталях: примыкания, парапеты, ножки оборудования, воронки.</p>
    <div class="grid g4" style="margin-top:26px">
      {kv("seam","Примыкания и парапеты","Рубероид плохо клеится к выступающим элементам. Вода проходит через примыкания и разрушает парапет изнутри.")}
      {kv("crane","18 тонн вниз, 18 тонн вверх","Полный цикл ремонта: демонтаж до основания, спуск мусора и подъём новых материалов — автокран работает днями.")}
      {kv("flame","Открытый огонь","Наплавление — это огневые работы: охрана труда, допуски, ограничения. И риск для старого основания.")}
      {kv("speed","18–25 рабочих дней","Бригада 6–8 человек на одну кровлю. Каждый дополнительный день на объекте отодвигает следующий дом в программе.")}
    </div>
  </div>
</section>'''

ROOF = f'''
<section class="sec soft" id="roof">
  <div class="wrap">
    <div class="kicker">Решение</div>
    <h2>Напыляемая кровля: утеплитель и гидроизоляция за один цикл</h2>
    <div class="rule"></div>
    <div class="grid g2" style="align-items:start">
      <div>
        <p class="lead">Два жидких компонента смешиваются в установке высокого давления и наносятся на
        подготовленное основание. ППУ вспенивается в сплошной слой утеплителя, полимочевина за секунды
        образует сплошную водонепроницаемую мембрану. Покрытие повторяет рельеф кровли и сложные
        примыкания — без швов, нахлёстов и крепежа.</p>
        <div class="layers" style="margin-top:20px">
          <div class="lr"><span class="sw" style="background:#8C2F39"></span><div><b>Защитный слой ПОЛИФЛЕКС® 105</b> <span>· min 2 слоя, УФ-стойкая окраска</span></div></div>
          <div class="lr"><span class="sw" style="background:#252A34"></span><div><b>Гидроизоляционный слой ЭКСТРАПЛАН 501/503</b> <span>· полимочевина, δ ≥ 2,0 мм, сплошная мембрана</span></div></div>
          <div class="lr"><span class="sw" style="background:#E8D8A0"></span><div><b>Теплоизоляция EXTRAFOAM / DALTOTHERM</b> <span>· напыляемый ППУ, толщина по расчёту</span></div></div>
          <div class="lr"><span class="sw" style="background:#31445E"></span><div><b>Грунтовочный слой ПРАЙМЕР</b> <span>· адгезионная подготовка основания</span></div></div>
          <div class="lr"><span class="sw" style="background:#B9C1CC"></span><div><b>Основание</b> <span>· существующие слои кровли, ж/б плита, профлист</span></div></div>
        </div>
        <p class="formnote" style="margin-top:10px">Состав системы — по альбому технических решений ЗАО «Хантсман-НМГ» (раздел 12).
        Толщину утепления определяем по расчёту для конкретной кровли, а не «одной цифрой для всех».</p>
      </div>
      <div class="grid" style="gap:14px">
        <div class="card"><div class="ic">{IC['drop']}</div><h3>Полимочевина: сплошная мембрана без швов</h3>
          <p>Гель за 15–30 секунд, «до отлипа» за 40–90 секунд. Пешеходные нагрузки — через 2 часа.
          Удлинение до разрыва — не менее 350% (ЭКСТРАПЛАН 501/502) и не менее 480% (ЭКСТРАПЛАН 503/504)
          по ТУ и АТР производителя. Адгезия к бетону не менее 2,5 МПа.
          Рассчитана на контакт со стоячей водой. Класс пожарной опасности КМ2 (В2, Д2, Т2, РП1).</p></div>
        <div class="card"><div class="ic">{IC['thermo']}</div><h3>ППУ: лучший коэффициент теплопроводности</h3>
          <p>λ ≤ 0,026–0,027 Вт/(м·К) по ТУ производителя — против 0,036–0,041 у пенополистирола
          и 0,037–0,048 у минваты. Замкнутые ячейки ≥ 90%, водопоглощение ≤ 0,2 кг/м² за 24 ч.
          Сплошной слой без мостиков холода по стыкам плит.</p></div>
        <div class="card"><div class="ic">{IC['box']}</div><h3>Материалы на складе в Тюмени</h3>
          <p>Компоненты Huntsman NMG держим на собственном складе в Тюменской области:
          не ждём поставку под объект и держим срок выхода на площадку.
          Применяем системы по документации производителя: АТР, ТУ, сертификаты.</p></div>
      </div>
    </div>
  </div>
</section>'''

COMPARE = '''
<section class="sec" id="compare">
  <div class="wrap">
    <div class="kicker">Сравнение технологий</div>
    <h2>Напыляемая система против рубероида и мембраны</h2>
    <div class="rule"></div>
    <p class="lead">Сравниваем не цену квадратного метра материала, а весь цикл: подготовку, подъём,
    монтаж, примыкания, срок до следующего ремонта и обслуживание.</p>
    <div style="overflow-x:auto;margin-top:22px">
    <table class="cmp">
      <thead><tr>
        <th>Параметр</th><th>Наплавляемая рулонная кровля</th><th>ПВХ / ТПО мембрана</th><th class="ours">Напыляемая система ППУ + полимочевина</th>
      </tr></thead>
      <tbody>
        <tr><td>Демонтаж старых слоёв</td><td class="no">Полный: снять рубероид, утеплитель, стяжку; 18 т мусора вниз</td><td class="mid">Часто требуется выравнивание или разуклонка</td><td class="ours yes">Часто не нужен: убираем только отслоившееся, напыляем сверху</td></tr>
        <tr><td>Кран и подъём</td><td class="no">18 т материалов вверх: ещё день-два автокрана</td><td class="mid">Рулоны, крепёж, пригруз</td><td class="ours yes">9 бочек по 220 л на кровлю 800 м²; кран ~1,5 часа</td></tr>
        <tr><td>Открытый огонь</td><td class="no">Да, огневые работы и допуски</td><td class="yes">Нет (сварка горячим воздухом)</td><td class="ours yes">Нет</td></tr>
        <tr><td>Бригада и срок на объект</td><td class="no">6–8 человек, 18–25 рабочих дней</td><td class="mid">4–6 человек, 10–15 дней</td><td class="ours yes">4 человека; объект 550 м² — 3 дня полным циклом</td></tr>
        <tr><td>Швы и примыкания</td><td class="no">Нахлёсты и подрезки у каждого элемента; слабые места — парапеты, ножки, воронки</td><td class="mid">Сварные швы; сотни точек крепежа и примыканий</td><td class="ours yes">Бесшовная мембрана: примыкания, парапеты и ножки оборудования закрыты сплошным слоем</td></tr>
        <tr><td>Утепление</td><td class="mid">Плиты с заменой: мостики холода по стыкам</td><td class="mid">Отдельный слой и отдельный цикл</td><td class="ours yes">ППУ тем же циклом: сплошной слой, повторяющий основание</td></tr>
        <tr><td>Нагрузка на конструкции</td><td class="no">Тяжёлый пирог со стяжкой</td><td class="mid">Средняя, с пригрузом или балластом</td><td class="ours yes">Лёгкая: плотность ППУ 35–65 кг/м³</td></tr>
        <tr><td>Сложная геометрия</td><td class="no">Кусочки рубероида не дают монолита</td><td class="mid">Выкройки, сварка, крепёж</td><td class="ours yes">Повторяет любой рельеф: трубы, ножки, борта, воронки</td></tr>
        <tr><td>Срок до следующего ремонта</td><td class="no">3–7 лет по практике эксплуатации</td><td class="yes">15–25 лет по паспорту системы</td><td class="ours yes">25 лет минимальный срок службы полимочевины</td></tr>
        <tr><td>Стоячая вода</td><td class="no">Пузыри и отслоения в швах</td><td class="mid">Допустима, но швы — риск</td><td class="ours yes">Покрытие рассчитано на контакт со стоячей водой</td></tr>
        <tr><td>Когда выгодно</td><td>Дешёвый материал, если не считать цикл и простой</td><td>Новые кровли с ровным основанием и свободным фронтом работ</td><td class="ours">Ремонт действующих кровель, сложная геометрия, сжатый сезон, требование «без останова здания»</td></tr>
      </tbody>
    </table>
    </div>
    <p class="formnote" style="margin-top:12px">Мембрана — рабочее решение для нового строительства с ровным основанием.
    Мы говорим прямо: если вашему объекту подходит мембрана или рулонная система — скажем это на обследовании.
    Напыляемая система выигрывает там, где важны срок, геометрия и отсутствие демонтажа.</p>
  </div>
</section>'''

CYCLE = '''
<section class="sec dark" id="cycle">
  <div class="wrap">
    <div class="kicker">Экономика цикла</div>
    <h2>Это дешевле, чем каждый год переделывать наплавляемую кровлю</h2>
    <div class="rule"></div>
    <div class="grid g2" style="margin-top:8px">
      <div class="step">
        <div class="n">ЦИКЛ 1 · ТРАДИЦИОННЫЙ</div>
        <h3>Разобрать, вывезти, поднять, наплавить</h3>
        <p>Демонтаж до основания → 18 тонн мусора вниз (автокран от 8 часов) → 18 тонн утеплителя
        и рулонов вверх (ещё до 16 часов крана) → стяжка и ожидание её высыхания → наплавление
        бригадой 6–8 человек за 18–25 рабочих дней. И через 3–7 лет цикл повторяется:
        рубероид снова теряет эластичность на примыканиях.</p>
      </div>
      <div class="step">
        <div class="n">ЦИКЛ 2 · НАПЫЛЯЕМЫЙ</div>
        <h3>Подготовить, напылить, сдать</h3>
        <p>Обследование и акт готовности основания → праймер → ППУ (если нужен утепляющий слой) →
        полимочевина → защитная окраска. 9 бочек по 220 литров на кровлю 800 м² вместо 36 тонн
        груза. 4 человека вместо 6–8. Объект 550 м² — 3 дня от подъёма оборудования до спуска
        пустых бочек. Дальше — обслуживание осмотром, а не новый демонтаж.</p>
      </div>
    </div>
    <div class="grid g3" style="margin-top:22px">
      <div class="step"><div class="n">10 ЛЕТ</div><h3>Один цикл вместо двух-трёх</h3><p>Рулонная кровля за десятилетие потребует 2–3 ремонта с демонтажем и краном. Напыляемая система — один цикл и плановые осмотры.</p></div>
      <div class="step"><div class="n">СЕЗОН</div><h3>Больше кровель за то же лето</h3><p>Три дня на объект вместо трёх недель — это в разы больше домов, которые бригада успевает закрыть за сезон ремонтной программы.</p></div>
      <div class="step"><div class="n">ПРОСТОЙ</div><h3>Здание не останавливается</h3><p>Нет демонтажа до основания — нет риска залить верхние этажи во время вскрытия пирога и нет останова помещений под кровлей.</p></div>
    </div>
    <p style="margin-top:22px"><a class="btn" href="#contact">Получить расчёт цикла для своей кровли</a></p>
  </div>
</section>'''

def case_html():
  return f'''
<section class="sec" id="case">
  <div class="wrap">
    <div class="kicker">Подтверждённый объект</div>
    <h2>Ноябрьск, сентябрь 2026: административное здание, 550 м²</h2>
    <div class="rule"></div>
    <div class="casehead">
      <div><div class="big">550 м²</div><span style="color:var(--mut);font-size:13px">с парапетами и примыканиями</span></div>
      <div><div class="big">2 человека</div><span style="color:var(--mut);font-size:13px">бригада на объекте</span></div>
      <div><div class="big">3 дня</div><span style="color:var(--mut);font-size:13px">полный цикл: подъём — спуск пустых бочек</span></div>
      <div><div class="big">0 м²</div><span style="color:var(--mut);font-size:13px">демонтажа: рулонное покрытие сохранено</span></div>
    </div>
    <p class="lead" style="margin-top:18px">Кровля протекала: в кабинетах верхнего этажа подставляли тазики.
    Проблемные примыкания к парапетам, разрушающиеся парапетные крышки, вздутия покрытия,
    рассыпающаяся монтажная пена в узлах. Существующее рулонное покрытие сохранили: подготовили
    примыкания, нанесли праймер, полимочевину и защитную краску. Новый теплоизоляционный слой
    на этом объекте не устраивали — задача была остановить воду.</p>
    <div class="gal">
      <figure><img src="{A('case_parapet')}" alt="Парапет до работ: вода проходит через примыкание рулонного покрытия"><figcaption><b>До: парапет</b>Вода проходила через примыкание рубероида, бетон разрушался.</figcaption></figure>
      <figure><img src="{A('case_legs')}" alt="Ножки оборудования до работ: лоскуты рулонного материала"><figcaption><b>До: ножки оборудования</b>Из лоскутов рубероида монолитную защиту не собрать.</figcaption></figure>
      <figure><img src="{A('case_joint')}" alt="Примыкание: разрушенная монтажная пена"><figcaption><b>Узел: монтажная пена</b>Рассыпается и пропускает воду — узел раскрыт и подготовлен.</figcaption></figure>
      <figure><img src="{A('case_after')}" alt="После: сплошное полимочевинное покрытие кровли"><figcaption><b>После</b>Сплошная мембрана по всей плоскости, парапетам и примыканиям.</figcaption></figure>
    </div>
    <p class="formnote" style="margin-top:14px">Честно о результате: на момент публикации объект отработал без протечек
    первый период; эксплуатацию и поведение покрытия в дождь и снег отслеживаем по регламенту обслуживания.
    Фото — реальный объект Полифорта, съёмка сентябрь 2026.</p>
  </div>
</section>'''

def designers_html():
  return f'''
<section class="sec soft" id="designers">
  <div class="wrap">
    <div class="kicker">Проектировщикам</div>
    <h2>Узлы уже разработаны: альбом технических решений Хантсман-НМГ</h2>
    <div class="rule"></div>
    <p class="lead">Напыляемая система — не «кустарная технология», а конструктив с готовой документацией.
    ЗАО «Хантсман-НМГ» (Обнинск, производитель с 1992 года, сертификация ISO 9001/14001/OHSAS 18001)
    выпускает альбом технических решений с составами кровель и узлами примыканий.
    Мы работаем с системами производителя в Тюменской области, ХМАО и ЯНАО и передаём проектировщикам
    материалы под конкретный объект: узлы, спецификации, расчёт толщины, сертификаты и ТУ.</p>
    <div class="atr" style="margin-top:24px">
      <figure><div class="imgbox"><img src="{A('atr12283')}" alt="АТР Хантсман-НМГ, узел 12.28.3 — варианты ремонтируемой кровли"></div>
        <figcaption><b>Узел 12.28.3 · Варианты ремонтируемой кровли</b>Рулонные кровли без демонтажа существующих слоёв —
        с дополнительным теплоизоляционным слоем снаружи или изнутри. АТР «Хантсман-НМГ», раздел 12.</figcaption></figure>
      <figure><div class="imgbox"><img src="{A('atr121')}" alt="АТР Хантсман-НМГ, узел 12.1 — варианты кровли со сборными и монолитными железобетонными плитами"></div>
        <figcaption><b>Узел 12.1 · Кровля со сборными и монолитными ж/б плитами</b>Четыре состава покрытия:
        неотапливаемые здания, сборные и монолитные плиты, изоляция изнутри. АТР «Хантсман-НМГ», раздел 12.</figcaption></figure>
      <figure><div class="imgbox"><img src="{A('atr12291')}" alt="АТР Хантсман-НМГ, узел 12.29.1 — ремонт водоизоляционного ковра на примыканиях"></div>
        <figcaption><b>Узел 12.29.1 · Ремонт ковра на примыканиях</b>Парапет: фартуки из оцинкованной стали,
        стальные полосы, высоты заходов. АТР «Хантсман-НМГ», раздел 12.</figcaption></figure>
    </div>
    <div class="grid g3" style="margin-top:22px">
      {kv("draw","Альбом и узлы в работе","Передаём разделы АТР, узлы примыканий (парапеты, воронки, деформшвы, выходы) и помогаем вписать систему в ваш проект.")}
      {kv("doc","Спецификация и расчёт","Толщина ППУ — по расчёту сопротивления теплопередаче для конкретного здания; бренд и артикул материала фиксируем в спецификации.")}
      {kv("pin","Сопровождение до стройки","Выезжаем на обследование, уточняем состав слоёв «что сохранить — что заменить», участвуем в согласовании с заказчиком.")}
    </div>
    <p style="margin-top:22px"><a class="btn line" href="#contact">Запросить АТР и узлы под свой проект</a></p>
    <p class="formnote">Решение по конкретному зданию принимается после обследования: альбом даёт основу,
    а не ответ «для всех». Номера узлов и источник сохраняем в документации.</p>
  </div>
</section>'''

CALC = '''
<section class="sec" id="calc">
  <div class="wrap">
    <div class="kicker">Предварительный расчёт</div>
    <h2>Посчитать вилку по своей кровле</h2>
    <div class="rule"></div>
    <p class="lead">Калькулятор даёт ориентировочную вилку по четырём исходным параметрам.
    Точная стоимость — после обследования: состояние основания и узлы решают больше, чем площадь.</p>
    <div class="calc" style="margin-top:22px">
      <div class="fields">
        <div style="grid-column:1/-1"><label for="c-area">Площадь кровли, м²</label><input id="c-area" type="number" min="50" value="800"></div>
        <div><label for="c-task">Задача</label><select id="c-task">
          <option value="wm">Только гидроизоляция (полимочевина)</option>
          <option value="ppu50" selected>Гидроизоляция + утепление ППУ 50 мм</option>
          <option value="ppu100">Гидроизоляция + утепление ППУ 100 мм</option></select></div>
        <div><label for="c-base">Основание</label><select id="c-base">
          <option value="ok" selected>Рулонная кровля, удовлетворительное состояние</option>
          <option value="bad">Вздутия, отслоения, мокрый утеплитель</option>
          <option value="metal">Металл / профлист</option></select></div>
        <div style="grid-column:1/-1"><label for="c-geo">Регион работ</label><select id="c-geo">
          <option value="tyu" selected>Тюменская область</option><option value="hmao">ХМАО — Югра</option><option value="yanao">ЯНАО</option></select></div>
        <div style="grid-column:1/-1" class="formnote">Минимальный объём напыления и логистику считаем индивидуально:
        на малых площадях стоимость определяет не м², а выезд.</div>
      </div>
      <div class="res">
        <div style="font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;color:#8A93A2;font-weight:700">Предварительно, без НДС</div>
        <div class="val" id="c-val">—</div>
        <ul id="c-brk"></ul>
        <div class="disc">Вилка ±15%. Не является офертой: точный состав и стоимость фиксируем в предложении
        после обследования основания и узлов. Материалы, работы, подготовка и логистика в предложении указываются отдельными строками.</div>
      </div>
    </div>
  </div>
</section>'''

GEO = f'''
<section class="sec" id="geo">
  <div class="wrap">
    <div class="kicker">География</div>
    <h2>Тюменская компания. Три региона работы.</h2>
    <div class="rule"></div>
    <div class="grid g2" style="align-items:start">
      <div class="mapbox">
        <svg viewBox="0 0 640 560" role="img" aria-label="Схема регионов работы: ЯНАО, ХМАО-Югра, Тюменская область">
          <defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#00D7CD"/></marker></defs>
          <rect x="20" y="20" width="600" height="150" rx="14" fill="#252A34"/>
          <text x="44" y="58" fill="#00D7CD" font-size="20" font-weight="700" font-family="DejaVu Sans,Arial">ЯНАО</text>
          <text x="44" y="80" fill="#9AA3B2" font-size="13" font-family="DejaVu Sans,Arial">Ямало-Ненецкий автономный округ</text>
          <g fill="#fff" font-size="13" font-family="DejaVu Sans,Arial">
            <circle cx="120" cy="120" r="5" fill="#00D7CD"/><text x="134" y="125">Салехард</text>
            <circle cx="260" cy="112" r="5" fill="#00D7CD"/><text x="274" y="117">Надым</text>
            <circle cx="392" cy="104" r="6" fill="#00D7CD"/><text x="406" y="109">Новый Уренгой</text>
            <circle cx="520" cy="118" r="6" fill="#00D7CD"/><text x="534" y="123">Ноябрьск</text>
          </g>
          <rect x="20" y="190" width="600" height="150" rx="14" fill="#2E3440"/>
          <text x="44" y="228" fill="#00D7CD" font-size="20" font-weight="700" font-family="DejaVu Sans,Arial">ХМАО — Югра</text>
          <text x="44" y="250" fill="#9AA3B2" font-size="13" font-family="DejaVu Sans,Arial">Ханты-Мансийский автономный округ</text>
          <g fill="#fff" font-size="13" font-family="DejaVu Sans,Arial">
            <circle cx="110" cy="296" r="5" fill="#00D7CD"/><text x="124" y="301">Ханты-Мансийск</text>
            <circle cx="250" cy="288" r="6" fill="#00D7CD"/><text x="264" y="293">Нефтеюганск</text>
            <circle cx="352" cy="280" r="7" fill="#00D7CD"/><text x="366" y="285">Сургут</text>
            <circle cx="470" cy="288" r="6" fill="#00D7CD"/><text x="484" y="293">Нижневартовск</text>
            <circle cx="420" cy="316" r="5" fill="#00D7CD"/><text x="434" y="321">Когалым</text>
          </g>
          <rect x="20" y="360" width="600" height="180" rx="14" fill="#39404D"/>
          <text x="44" y="398" fill="#00D7CD" font-size="20" font-weight="700" font-family="DejaVu Sans,Arial">Тюменская область</text>
          <text x="44" y="420" fill="#9AA3B2" font-size="13" font-family="DejaVu Sans,Arial">база и склад материалов — Тюменский район</text>
          <g fill="#fff" font-size="13" font-family="DejaVu Sans,Arial">
            <circle cx="120" cy="470" r="5" fill="#00D7CD"/><text x="134" y="475">Ишим</text>
            <circle cx="230" cy="462" r="5" fill="#00D7CD"/><text x="244" y="467">Ялуторовск</text>
            <circle cx="330" cy="452" r="7" fill="#fff"/><text x="344" y="457" font-weight="700">Тюмень · база</text>
            <circle cx="450" cy="440" r="6" fill="#00D7CD"/><text x="464" y="445">Тобольск</text>
            <circle cx="540" cy="470" r="5" fill="#00D7CD"/><text x="554" y="475">Заводоуковск</text>
          </g>
          <path d="M330 445 C 340 380 350 340 352 292" stroke="#00D7CD" stroke-width="2" stroke-dasharray="6 6" fill="none" marker-end="url(#ar)"/>
          <path d="M352 272 C 370 220 385 170 392 122" stroke="#00D7CD" stroke-width="2" stroke-dasharray="6 6" fill="none" marker-end="url(#ar)"/>
          <text x="368" y="352" fill="#9AA3B2" font-size="12" font-family="DejaVu Sans,Arial">выезды бригад и оборудования</text>
        </svg>
        <div class="geo-cities">
          <span class="chip t">Тюмень</span><span class="chip t">Тобольск</span><span class="chip t">Ишим</span><span class="chip t">Ялуторовск</span><span class="chip t">Заводоуковск</span>
          <span class="chip">Сургут</span><span class="chip">Нижневартовск</span><span class="chip">Нефтеюганск</span><span class="chip">Когалым</span><span class="chip">Ханты-Мансийск</span><span class="chip">Муравленко</span>
          <span class="chip">Новый Уренгой</span><span class="chip">Ноябрьск</span><span class="chip">Губкинский</span><span class="chip">Салехард</span><span class="chip">Надым</span>
        </div>
      </div>
      <div class="grid" style="gap:14px">
        <div class="card"><div class="ic">{IC['pin']}</div><h3>База — Тюменский район, д. Ушакова</h3>
          <p>Юридический адрес и склад: {C['address']}. Оборудование, бригада и материалы — здесь,
          а не «в другом регионе»: быстрый выезд на обследование и короткое плечо логистики по югу области.</p></div>
        <div class="card"><div class="ic">{IC['speed']}</div><h3>ХМАО и ЯНАО — вахтовым форматом</h3>
          <p>Работаем на объектах Югры и Ямала: командировки, проживание, пропускной режим, требования ПБ
          объекта и наряд-допуски учитываем в организации работ заранее, а не по факту приезда.</p></div>
        <div class="card"><div class="ic">{IC['thermo']}</div><h3>Северный климат — в расчёте, а не в оправданиях</h3>
          <p>Минимальная рекомендуемая температура основания по ТУ производителя — +10 °С.
          В межсезонье и зимой применяем прогрев, укрытие и контроль точки росы;
          границы применения системы фиксируем в предложении до начала работ.</p></div>
      </div>
    </div>
  </div>
</section>'''

PROCESS = '''
<section class="sec dark" id="process">
  <div class="wrap">
    <div class="kicker">Процесс</div>
    <h2>Шесть шагов от запроса до передачи</h2>
    <div class="rule"></div>
    <div class="steps">
      <div class="step"><div class="n">01</div><h3>Запрос</h3><p>Собираем задачу: площадь, основание, условия, сроки, город.</p></div>
      <div class="step"><div class="n">02</div><h3>Оценка</h3><p>Уточняем данные, выезжаем на обследование: тепловизор, влагомер, акт осмотра с фото.</p></div>
      <div class="step"><div class="n">03</div><h3>Предложение</h3><p>Состав системы, послойная спецификация, цена раздельно по материалам и работам, этапы.</p></div>
      <div class="step"><div class="n">04</div><h3>Подготовка</h3><p>Согласуем доступ, основание и ответственность сторон. Акт готовности основания — условие начала.</p></div>
      <div class="step"><div class="n">05</div><h3>Выполнение</h3><p>Напыление по регламенту, контроль толщины и адгезии, фотофиксация по этапам, сообщение о ходе.</p></div>
      <div class="step"><div class="n">06</div><h3>Передача</h3><p>КС-2/КС-3, акты скрытых работ, паспорта материалов, исполнительная документация, рекомендации по обслуживанию.</p></div>
    </div>
  </div>
</section>'''

DOCS = f'''
<section class="sec" id="docs">
  <div class="wrap">
    <div class="kicker">Гарантии и документы</div>
    <h2>Обещания, которые подтверждаются бумагой</h2>
    <div class="rule"></div>
    <div class="grid g4">
      {kv("shield", f"Гарантия {C['warranty']}", "Гарантийные обязательства фиксируем в договоре: на что распространяются, от чего зависят (система, подготовка основания, режим эксплуатации) и как снимаются.")}
      {kv("doc","Исполнительная документация","КС-2, КС-3, акты скрытых работ, журнал работ, фотофиксация по этапам, паспорта и сертификаты на материалы. Работаем с НДС.")}
      {kv("box","Материалы: бренд и артикул в спецификации","Huntsman NMG (ЭКСТРАПЛАН, EXTRAFOAM/DALTOTHERM, ПРАЙМЕР, ПОЛИФЛЕКС). ТУ, сертификаты соответствия, СГР, пожарные декларации — в пакете к договору.")}
      {kv("seam","Контроль результата","Замер толщины толщиномером, проверка адгезии, визуальный контроль сплошности. Контрольные точки согласуем до начала нанесения.")}
    </div>
  </div>
</section>'''

ABOUT = f'''
<section class="sec soft" id="about">
  <div class="wrap">
    <div class="kicker">О компании</div>
    <h2>Полифорт — тюменская команда полимерных систем</h2>
    <div class="rule"></div>
    <div class="grid g2">
      <div>
        <p>ООО «Полифорт» — компания из Тюмени. Мы занимаемся промышленными полимерными решениями:
        напыляемая теплоизоляция ППУ, гидроизоляция полимочевиной, полимерные полы.
        Наша команда годами работает на объектах Тюменской области и северных округов;
        «Полифорт» собран вокруг работы с полимерными системами Huntsman.</p>
        <p>Мы представляем Huntsman NMG в Тюменской области: применяем системы производителя
        по его документации, держим компоненты на собственном складе в регионе и опираемся на альбом
        технических решений при проектировании.</p>
        <p>Принцип работы — инженерная ясность: объясняем, почему выбрана система, указываем ограничения
        и альтернативы, фиксируем договорённости документами и показываем ход выполнения.</p>
      </div>
      <div class="card">
        <h3 style="margin-bottom:12px">Реквизиты</h3>
        <p style="font-size:14px;color:var(--mut)">ООО «ПОЛИФОРТ»<br>ИНН / КПП: {C['inn']} / 722401001<br>ОГРН: {C['ogrn']}<br>{C['address']}
        Email: <a href="mailto:{C['email']}">{C['email']}</a><br>Сайт: {C['site'] if 'site' in C else C['base_url'].replace('https://','')}</p>
        <p style="font-size:13px;color:var(--mut);margin:0">Объекты публикуем с указанием фактического исполнителя
        и подтверждающих материалов — так, как требует наша же политика бренда.</p>
      </div>
    </div>
  </div>
</section>'''

FAQ = f'''
<section class="sec" id="faq">
  <div class="wrap" style="max-width:860px">
    <div class="kicker">Вопросы и ответы</div>
    <h2>Что спрашивают перед решением</h2>
    <div class="rule"></div>
    <details open><summary>Почему это дешевле, чем переделывать наплавляемую кровлю каждый год?</summary>
      <div class="body">Считайте цикл, а не квадратный метр. Рулонный ремонт — это демонтаж, 18 тонн мусора вниз
      и 18 тонн материалов вверх, автокран, стяжка с ожиданием, бригада 6–8 человек на 18–25 дней —
      и повтор того же цикла через 3–7 лет. Напыляемая система: один цикл, 4 человека, объект 550 м² за 3 дня,
      срок службы полимочевины 25 лет, дальше — осмотры. За 10 лет это один цикл против двух-трёх рулонных.</div></details>
    <details><summary>Можно ли напылять по старой рулонной кровле без демонтажа?</summary>
      <div class="body">Да, это основной сценарий ремонта по узлу 12.28.3 альбома Хантсман-НМГ: рулонные кровли
      без демонтажа существующих слоёв, с дополнительным утеплением снаружи или изнутри либо только с
      восстановлением водоизоляционного ковра. Что сохранить, а что заменить — решает обследование:
      отслоившиеся участки убираем, прочные слои работают дальше.</div></details>
    <details><summary>Что с примыканиями, парапетами и ножками оборудования?</summary>
      <div class="body">Это главные точки протечек рулонной кровли и главное преимущество напыления:
      мембрана формируется сплошной, повторяя парапеты на всю высоту, борта, трубы и ножки оборудования.
      Узлы примыканий есть в АТР (12.7–12.16, 12.29): парапеты, воронки, деформационные швы, выходы на кровлю.</div></details>
    <details><summary>Не потечёт ли снова? Какая гарантия?</summary>
      <div class="body">Гарантия {C['warranty']} фиксируется в договоре вместе с условиями: система, подготовка
      основания, режим эксплуатации. Полимочевина рассчитана на контакт со стоячей водой, а её удлинение
      до разрыва — не менее 480% у ЭКСТРАПЛАН 503/504 по данным производителя: покрытие работает на
      деформациях основания, а не трескается на них. «Пожизненно и никогда не потечёт» не обещаем:
      так формулируют те, кто потом не отвечает.</div></details>
    <details><summary>Зимой и в дождь работать можно?</summary>
      <div class="body">Ограничение честное и техническое: основание должно быть сухим, его температура —
      выше точки росы не менее чем на 3 °C, рекомендуемый минимум по ТУ производителя — +10 °C.
      Поэтому сезонные окна планируем заранее, а в холодный период применяем прогрев, укрытие и контроль
      точки росы — это отдельная позиция в смете, которую мы показываем открыто.</div></details>
    <details><summary>Вы правда напыляете от 200 м² в день?</summary>
      <div class="body">{C['speed']} — на типовом основании при готовой площадке и согласованном доступе.
      Производительность считаем под конкретный объект: толщина, высота, геометрия, сменность.
      Реальный пример: 550 м² с парапетами и примыканиями в Ноябрьске — 3 дня полным циклом, бригада 2 человека.</div></details>
    <details><summary>Чем это лучше мембраны?</summary>
      <div class="body">Для новой кровли с ровным основанием мембрана — нормальное решение, и мы скажем это прямо.
      Напыление выигрывает на ремонте действующих кровель: без демонтажа, без швов и точек крепежа,
      сложная геометрия закрывается сплошным слоем, утепление добавляется тем же циклом.</div></details>
    <details><summary>Как это проектировать? Есть ли документация?</summary>
      <div class="body">Есть альбом технических решений ЗАО «Хантсман-НМГ»: составы кровель и узлы примыканий
      (разделы 11–13). Передаём проектировщикам узлы и спецификации, считаем толщину ППУ под требуемое
      сопротивление теплопередаче, выезжаем на обследование и участвуем в согласовании.</div></details>
    <details><summary>Работаете ли вы в нашем городе?</summary>
      <div class="body">База — Тюменский район, работаем по всей Тюменской области, ХМАО и ЯНАО:
      Тюмень, Тобольск, Ишим, Сургут, Нижневартовск, Нефтеюганск, Когалым, Новый Уренгой, Ноябрьск,
      Губкинский, Муравленко, Салехард и другие города. Логистику и проживание считаем отдельной строкой.</div></details>
    <details><summary>Материалы точно оригинальные?</summary>
      <div class="body">Мы работаем с компонентами Huntsman NMG напрямую и держим их на своём складе в регионе.
      Бренд и артикул фиксируются в спецификации, к договору прикладываем паспорта, сертификаты и ТУ —
      партию можно проверить у производителя.</div></details>
  </div>
</section>'''

CONTACT = f'''
<section class="sec soft" id="contact">
  <div class="wrap">
    <div class="kicker">Контакты</div>
    <h2>Обсудить объект</h2>
    <div class="rule"></div>
    <div class="grid g2" style="align-items:start">
      <form class="brief" id="brief" onsubmit="return false">
        <div><label for="f-name">Имя и компания</label><input id="f-name" name="name" placeholder="Иван Петров, УК «Север»"></div>
        <div><label for="f-tel">Телефон *</label><input id="f-tel" name="tel" required placeholder="+7 ___ ___-__-__"></div>
        <div><label for="f-city">Город / регион</label><select id="f-city" name="city">
          <option>Тюменская область</option><option>ХМАО — Югра</option><option>ЯНАО</option><option>Другой регион</option></select></div>
        <div><label for="f-obj">Тип объекта</label><select id="f-obj" name="obj">
          <option>Многоквартирный дом</option><option>Административное здание</option><option>Производство / цех</option>
          <option>Склад / ангар</option><option>Соцобъект</option><option>Другое</option></select></div>
        <div><label for="f-roof">Кровля сейчас</label><select id="f-roof" name="roof">
          <option>Рулонная наплавляемая</option><option>Ж/б плита без покрытия</option><option>Металл / профлист</option>
          <option>Мембрана</option><option>Не знаю</option></select></div>
        <div><label for="f-area">Площадь кровли, м²</label><input id="f-area" name="area" inputmode="numeric" placeholder="800"></div>
        <div class="full"><label for="f-task">Задача</label><select id="f-task" name="task">
          <option>Остановить протечки (гидроизоляция)</option>
          <option>Гидроизоляция + утепление</option>
          <option>Полная система с защитным слоем</option>
          <option>Полимочевина по другой конструкции (пол, резервуар, фундамент)</option>
          <option>Нужна консультация проектировщика</option></select></div>
        <div class="full"><label for="f-msg">Что важно знать (протечки, сроки, доступ)</label><textarea id="f-msg" name="msg" rows="3" placeholder="Течёт у парапетов, верхний этаж залывает в дождь…"></textarea></div>
        <div class="full formactions">
          <button class="btn" id="send">Отправить заявку</button>
          <button class="btn line sm" id="copy">Скопировать бриф</button>
          <span class="formnote">Или сразу: <a href="tel:{tel_href(C['mob1'])}">{C['mob1']}</a>,
          <a href="mailto:{C['email']}">{C['email']}</a>. Ответим в течение рабочего дня.</span>
        </div>
        <p class="formnote full" style="margin:0">Нажимая кнопку, вы отправляете бриф письмом на {C['email']}.
        Цена «по телефону без данных» не называется: сначала исходные данные или обследование.</p>
      </form>
      <div class="grid" style="gap:14px">
        <div class="card"><h3>Полифорт · Тюмень</h3>
          <p style="font-size:15px;color:var(--ink)">Моб.: <a href="tel:{tel_href(C['mob1'])}"><b>{C['mob1']}</b></a><br>
          Моб.: <a href="tel:{tel_href(C['mob2'])}"><b>{C['mob2']}</b></a><br>
          Офис: <a href="tel:{tel_href(C['office'])}"><b>{C['office']}</b></a><br>
          Email: <a href="mailto:{C['email']}"><b>{C['email']}</b></a><br>{C['base_url'].replace('https://','').replace('http://','')}</p>
          <p style="font-size:13px;color:var(--mut);margin:0">{C['address']}</p></div>
        <div class="card soft"><h3>Что будет после заявки</h3>
          <p>1. Уточним исходные данные и согласуем время обследования.<br>
          2. Приедем с тепловизором и влагомером, выдадим акт осмотра с фото.<br>
          3. Подготовим предложение: состав системы, спецификация, цена по строкам, этапы и условия.<br>
          Срок первого содержательного ответа — не позднее одного рабочего дня.</p></div>
        <div class="card soft"><h3>Быстрее, чем вы думаете</h3>
          <p>Материалы на складе в Тюмени, бригада и оборудование — в регионе.
          Выход на площадку планируем от обследования, а не от поставки.</p></div>
      </div>
    </div>
  </div>
</section>'''

def footer_html():
  return f'''
<footer><div class="wrap">
  <div class="cols">
    <div><img src="{A('logo_h_white')}" alt="ПОЛИФОРТ"><br>
      Промышленные полимерные решения<br>ППУ · Полимочевина · Полимерные полы<br><br>
      Тюменская компания: база и склад в Тюменском районе.<br>Работаем: Тюменская область, ХМАО-Югра, ЯНАО.</div>
    <div><b>Контакты</b><br>{C['mob1']} · {C['mob2']}<br>офис {C['office']}<br><a href="mailto:{C['email']}">{C['email']}</a><br>{C['base_url'].replace('https://','').replace('http://','')}</div>
    <div><b>Направления</b><br>Напыляемая теплоизоляция ППУ<br>Гидроизоляция полимочевиной<br>Ремонт кровель без демонтажа<br>Полимерные промышленные полы</div>
    <div><b>Реквизиты</b><br>ООО «ПОЛИФОРТ», ИНН {C['inn']}, ОГРН {C['ogrn']}<br>{C['address']}</div>
  </div>
  <div class="fine">© 2026 ООО «Полифорт». Характеристики материалов — по ТУ и альбому технических решений
  ЗАО «Хантсман-НМГ»; узлы 12.1, 12.28.3, 12.29.1 приведены с сохранением источника.
  Предварительные расчёты на сайте не являются офертой: точная стоимость определяется после обследования.</div>
</div></footer>
<a class="mcall" href="tel:{tel_href(C['mob1'])}">Позвонить</a>'''

JS = """
<script>
(function(){
  var b=document.getElementById('burger'), m=document.getElementById('menu');
  if(b){b.addEventListener('click',function(){m.classList.toggle('open')});}
  m.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){m.classList.remove('open')})});
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target)}})},{threshold:.08});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
  } else {document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('on')})}

  var R = __RATES__;
  function fmt(n){return Math.round(n/1000)*1000}
  function money(n){return n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,' ')+' ₽'}
  function calc(){
    var a=parseFloat((document.getElementById('c-area')||{}).value)||0;
    var task=(document.getElementById('c-task')||{}).value||'wm';
    var base=(document.getElementById('c-base')||{}).value||'ok';
    var geo=(document.getElementById('c-geo')||{}).value||'tyu';
    if(a<=0){document.getElementById('c-val').textContent='укажите площадь';document.getElementById('c-brk').innerHTML='';return}
    var per = R.wm_mat + R.wm_work;
    if(task==='ppu50') per += R.ppu50;
    if(task==='ppu100') per += R.ppu100;
    var k = (R.k_base[base]||1) * (R.k_geo[geo]||1);
    var mid = per * k * a;
    var lo = mid*(1-R.spread), hi = mid*(1+R.spread);
    document.getElementById('c-val').textContent = money(fmt(lo))+' — '+money(fmt(hi));
    var mat = (R.wm_mat + (task==='ppu50'?R.ppu50*0.62:(task==='ppu100'?R.ppu100*0.62:0))) * k * a;
    var wrk = mid - mat;
    document.getElementById('c-brk').innerHTML =
      '<li>Материалы Huntsman (праймер, полимочевина, защита' + (task!=='wm'?', ППУ':'') + '): ≈ '+money(fmt(mat))+'</li>'+
      '<li>Работы: подготовка, нанесение, контроль: ≈ '+money(fmt(wrk))+'</li>'+
      '<li>Основание: '+base+', регион: '+geo+' — коэффициенты учтены</li>'+
      '<li>Площадь: '+a+' м², задача: '+(task==='wm'?'гидроизоляция':(task==='ppu50'?'+ППУ 50 мм':'+ППУ 100 мм'))+'</li>';
  }
  ['c-area','c-task','c-base','c-geo'].forEach(function(id){
    var el=document.getElementById(id); if(el){el.addEventListener('input',calc);el.addEventListener('change',calc)}
  });
  calc();

  function briefText(){
    function v(id){var e=document.getElementById(id);return e?(e.value||'—').trim():'—'}
    return 'ЗАЯВКА С САЙТА ПОЛИФОРТ\\n'+
      'Имя/компания: '+v('f-name')+'\\n'+
      'Телефон: '+v('f-tel')+'\\n'+
      'Регион: '+v('f-city')+'\\n'+
      'Объект: '+v('f-obj')+'\\n'+
      'Кровля сейчас: '+v('f-roof')+'\\n'+
      'Площадь, м2: '+v('f-area')+'\\n'+
      'Задача: '+v('f-task')+'\\n'+
      'Комментарий: '+v('f-msg');
  }
  var s=document.getElementById('send');
  if(s){s.addEventListener('click',function(){
    var t=document.getElementById('f-tel');
    if(!t.value.trim()){t.focus();t.style.outline='2px solid #D64545';return}
    var body=encodeURIComponent(briefText());
    var subj=encodeURIComponent('Заявка с сайта: '+(document.getElementById('f-obj').value)+' / '+(document.getElementById('f-area').value||'—')+' м2');
    window.location.href='mailto:__EMAIL__?subject='+subj+'&body='+body;
  })}
  var cp=document.getElementById('copy');
  if(cp){cp.addEventListener('click',function(){
    var txt=briefText();
    function done(){cp.textContent='Скопировано';setTimeout(function(){cp.textContent='Скопировать бриф'},2000)}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(done)}
    else{var ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done()}catch(e){}document.body.removeChild(ta)}
  })}
})();
</script>
"""

JSONLD = f'''
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"GeneralContractor",
  "name":"ПОЛИФОРТ",
  "legalName":"ООО «ПОЛИФОРТ»",
  "description":"Напыляемая теплоизоляция ППУ, гидроизоляция полимочевиной, полимерные полы и ремонт кровель без демонтажа. Представитель Huntsman NMG в Тюменской области.",
  "url":"{C['base_url']}/",
  "logo":"{C['base_url']}/assets/logo/logo_horizontal_color.png",
  "image":"{C['base_url']}/assets/logo/og-image.png",
  "telephone":["{C['mob1']}", "{C['mob2']}", "{C['office']}"],
  "email":"{C['email']}",
  "address":{{"@type":"PostalAddress","streetAddress":"ул. Вольная, д. 12, д. Ушакова","addressLocality":"Тюменский район","addressRegion":"Тюменская область","postalCode":"625502","addressCountry":"RU"}},
  "areaServed":["Тюменская область","Ханты-Мансийский автономный округ — Югра","Ямало-Ненецкий автономный округ"],
  "taxID":"{C['inn']}",
  "makesOffer":[
    {{"@type":"Offer","itemOffered":{{"@type":"Service","name":"Напыляемая теплоизоляция ППУ"}}}},
    {{"@type":"Offer","itemOffered":{{"@type":"Service","name":"Гидроизоляция полимочевиной"}}}},
    {{"@type":"Offer","itemOffered":{{"@type":"Service","name":"Ремонт кровель напыляемой системой без демонтажа"}}}},
    {{"@type":"Offer","itemOffered":{{"@type":"Service","name":"Полимерные промышленные полы"}}}}
  ]
}}
</script>'''

def head_extra():
  return f'''
<link rel="icon" type="image/png" sizes="180x180" href="{A('fav180')}">
<link rel="apple-touch-icon" sizes="512x512" href="{A('fav512')}">
<meta property="og:image" content="{C['base_url']}/assets/logo/og-image.png">'''

def page_html():
  return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Напыляемая кровля, ППУ и полимочевина в Тюмени, ХМАО и ЯНАО — ПОЛИФОРТ</title>
<meta name="description" content="Полифорт — тюменская компания: ремонт кровель напыляемой полимочевиной без демонтажа, теплоизоляция ППУ, полимерные полы. Представитель Huntsman NMG в Тюменской области, материалы на складе. Работаем по Тюменской области, ХМАО и ЯНАО. Гарантия 3 года.">
<meta name="keywords" content="напыляемая кровля Тюмень, полимочевина Тюмень, ППУ напыление, ремонт рулонной кровли без демонтажа, гидроизоляция полимочевиной ХМАО, утепление ППУ ЯНАО, Huntsman Тюмень">
<link rel="canonical" href="{C['base_url']}/">
<meta property="og:type" content="website">
<meta property="og:title" content="ПОЛИФОРТ — напыляемая кровля, которую не нужно переделывать каждый год">
<meta property="og:description" content="Полимочевина и ППУ: сплошная бесшовная защита по существующей кровле, без демонтажа и огня. Тюмень · ХМАО · ЯНАО. Представитель Huntsman NMG, материалы на складе.">
<meta property="og:locale" content="ru_RU">
{head_extra()}
{JSONLD}
<style>{CSS}</style>
</head>
<body>
{TOPBAR}
{header_html()}
{hero_html()}
{PROBLEM}
{ROOF}
{COMPARE}
{CYCLE}
{case_html()}
{designers_html()}
{CALC}
{GEO}
{PROCESS}
{DOCS}
{ABOUT}
{FAQ}
{CONTACT}
{footer_html()}
{JS.replace("__RATES__", repr(C["rates"])).replace("__EMAIL__", C["email"])}
</body>
</html>'''

# ============================== СБОРКА ======================================
HTACCESS = """# ПОЛИФОРТ — базовый .htaccess для Apache-хостинга
Options -Indexes
AddDefaultCharset UTF-8

# HTTPS и единый хост (замените domain на свой, если отличается)
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]
RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]
RewriteRule ^(.*)$ https://%1/$1 [R=301,L]

# Кэш для статики
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpeg "access plus 30 days"
  ExpiresByType image/png "access plus 30 days"
  ExpiresByType image/svg+xml "access plus 30 days"
  ExpiresByType text/css "access plus 7 days"
  ExpiresByType text/html "access plus 0 seconds"
</IfModule>
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>
"""

ROBOTS = f"""User-agent: *
Allow: /
Sitemap: {C['base_url']}/sitemap.xml
"""

def build():
    global MODE
    # 1) single-file версия (для писем/мессенджеров)
    MODE = "embed"
    html_embed = page_html()
    (ROOT / "Polifort_Landing.html").write_text(html_embed, encoding="utf-8")
    print("embed :", ROOT / "Polifort_Landing.html", round((ROOT / "Polifort_Landing.html").stat().st_size / 1024), "KB")

    # 2) версия для хостинга
    MODE = "site"
    (SITE / "assets" / "img").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "logo").mkdir(parents=True, exist_ok=True)
    for f in PHOTOS.values():
        shutil.copy2(ASSETS / f, SITE / "assets" / "img" / f)
    for f in LOGOS.values():
        shutil.copy2(WEBLOGO / f, SITE / "assets" / "logo" / f)
    shutil.copy2(WEBLOGO / "logo_horizontal_color.png", SITE / "assets" / "logo" / "logo_horizontal_color.png")
    html_site = page_html()
    (SITE / "index.html").write_text(html_site, encoding="utf-8")
    (SITE / ".htaccess").write_text(HTACCESS, encoding="utf-8")
    (SITE / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    print("site  :", SITE / "index.html", round((SITE / "index.html").stat().st_size / 1024), "KB")

    # 3) архив для загрузки на хостинг
    zpath = ROOT / "Polifort_site_deploy.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SITE.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(ROOT).as_posix())
        z.write(ROOT / "polifort_landing_build.py", "polifort_landing_build.py")
        if (ROOT / "README_hosting.md").exists():
            z.write(ROOT / "README_hosting.md", "README_hosting.md")
    print("zip   :", zpath, round(zpath.stat().st_size / 1024), "KB")

if __name__ == "__main__":
    build()
