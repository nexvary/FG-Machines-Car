#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

MARKER = "FG-NAVIGATION-INTEGRITY-HOTFIX-R1"

PRIMARY_NAV = f'''\n<!-- {MARKER} -->\n<nav class="fg-integrity-nav" data-fg-nav="primary" aria-label="Primary navigation integrity">\n  <a href="/" class="fg-integrity-nav-link">الرئيسية</a>\n  <a href="/services.html" class="fg-integrity-nav-link">الخدمات</a>\n  <a href="/about.html" class="fg-integrity-nav-link">حول النظام</a>\n</nav>\n'''

CSS = f'''\n/* {MARKER} */
.fg-integrity-nav {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 10px 8px;
  padding: 8px;
  border: 1px solid rgba(212,175,55,.72);
  border-radius: 12px;
  background: rgba(40,8,48,.72);
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.04), 0 0 14px rgba(212,175,55,.08);
}}
.fg-integrity-nav-link {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  padding: 5px 9px;
  border: 1px solid rgba(212,175,55,.72);
  border-radius: 9px;
  color: #f2df9b !important;
  background: linear-gradient(180deg, rgba(91,18,93,.96), rgba(44,8,51,.96));
  text-decoration: none !important;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}}
.fg-integrity-nav-link:hover,
.fg-integrity-nav-link:focus-visible {{
  filter: brightness(1.16);
  outline: 1px solid #f6d66d;
  outline-offset: 1px;
}}
.fg-integrity-page {{
  min-height: 100vh;
  margin: 0;
  padding: 24px;
  color: #f6efdf;
  background: radial-gradient(circle at 50% 0%, #42104d 0%, #210626 42%, #0d0711 100%);
  font-family: "Segoe UI", Tahoma, Arial, sans-serif;
}}
.fg-integrity-shell {{
  width: min(1180px, calc(100% - 24px));
  margin: 0 auto;
  padding: 22px;
  border: 1px solid #caa642;
  border-radius: 18px;
  background: rgba(25,8,30,.91);
  box-shadow: 0 18px 60px rgba(0,0,0,.34), inset 0 0 0 1px rgba(255,255,255,.04);
}}
.fg-integrity-shell h1 {{ margin: 0 0 8px; color: #f0cf63; }}
.fg-integrity-shell p {{ line-height: 1.8; color: #e9dfcf; }}
.fg-service-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  margin-top: 18px;
}}
.fg-service-link {{
  display: block;
  min-height: 42px;
  padding: 10px 12px;
  border: 1px solid rgba(202,166,66,.62);
  border-radius: 10px;
  color: #f7e7aa !important;
  background: rgba(78,16,83,.56);
  text-decoration: none !important;
  overflow-wrap: anywhere;
}}
.fg-service-link:hover, .fg-service-link:focus-visible {{ background: rgba(112,24,117,.74); }}
.fg-integrity-meta {{ color: #cfc2d2; font-size: 13px; }}
@media (max-width: 760px) {{
  .fg-integrity-page {{ padding: 10px; }}
  .fg-integrity-shell {{ width: auto; padding: 14px; }}
  .fg-service-grid {{ grid-template-columns: 1fr; }}
}}
'''


def route_for(root: Path, file: Path) -> str:
    rel = file.relative_to(root).as_posix()
    if rel.lower() == "index.html":
        return "/"
    if rel.lower().endswith("/index.html"):
        return "/" + rel[:-10]
    return "/" + rel


def label_for(root: Path, file: Path) -> str:
    rel = file.relative_to(root).as_posix()
    if rel.lower() == "index.html":
        return "Home / الرئيسية"
    return rel


def build_services(root: Path, existing: list[Path]) -> str:
    links = []
    for file in existing:
        route = route_for(root, file)
        if route == "/services.html":
            continue
        label = html.escape(label_for(root, file))
        links.append(f'      <a class="fg-service-link" href="{html.escape(route)}">{label}</a>')
    joined = "\n".join(links)
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>FG Machines Car — الخدمات</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body class="fg-integrity-page">
  <main class="fg-integrity-shell">
    <h1>الخدمات</h1>
    <p>مركز موحد للوصول إلى جميع أقسام ووحدات وصفحات FG Machines Car. كل عنصر بالأسفل رابط فعلي يتم فحصه ضمن Navigation Integrity Gate قبل إصدار نسخة Windows.</p>
    <p class="fg-integrity-meta">Connected pages at generation time: {len(existing)}</p>
    <div class="fg-service-grid" aria-label="All connected application pages">
{joined}
    </div>
  </main>
</body>
</html>
'''


def build_about() -> str:
    return '''<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>FG Machines Car — حول النظام</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body class="fg-integrity-page">
  <main class="fg-integrity-shell">
    <h1>حول النظام</h1>
    <p><strong>FG Machines Car</strong> منصة تشخيص سيارات مبنية على Native C++20، تجمع أدوات OBD/VCI، وحدات التشخيص، المفاتيح والريموت والترانسبوندر، مع واجهة متعددة اللغات ودعم العربية RTL.</p>
    <p>إصدار Windows لا يُعبأ للتجربة إلا بعد نجاح اختبارات Native وVisual QA وفحص الثغرات المعروفة وNavigation Integrity Gate واختبار ملاءمة شاشة 1366×768.</p>
    <p>الوظائف الحساسة التي تتطلب كتابة فعلية إلى وحدات المركبة تظل ضمن سياسة Read Only إلى أن يكتمل التحقق على أجهزة VCI وسيارات حقيقية.</p>
    <div class="fg-service-grid">
      <a class="fg-service-link" href="/services.html">فتح كل الخدمات والصفحات</a>
      <a class="fg-service-link" href="/navigation-selftest.html">Navigation Self-Test</a>
      <a class="fg-service-link" href="/">العودة للرئيسية</a>
    </div>
  </main>
</body>
</html>
'''


def inject_nav(text: str) -> str:
    if MARKER in text:
        return text
    # Prefer the real sidebar when present so primary navigation remains part of the app shell.
    if re.search(r"</aside\s*>", text, flags=re.I):
        return re.sub(r"</aside\s*>", PRIMARY_NAV + "</aside>", text, count=1, flags=re.I)
    if re.search(r"<body\b[^>]*>", text, flags=re.I):
        return re.sub(r"(<body\b[^>]*>)", r"\1" + PRIMARY_NAV, text, count=1, flags=re.I)
    raise RuntimeError("HTML file has no body/aside insertion point")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: apply_navigation_integrity_hotfix.py <PROJECT_DIR>", file=sys.stderr)
        return 2
    project = Path(sys.argv[1]).resolve()
    root = project / "native" / "ui-modern"
    if not root.is_dir():
        raise SystemExit(f"UI root not found: {root}")

    before = sorted(root.rglob("*.html"))
    if len(before) < 100:
        raise SystemExit(f"Unexpectedly small UI: {len(before)} html files")

    services = root / "services.html"
    about = root / "about.html"
    services.write_text(build_services(root, before + [about]), encoding="utf-8")
    about.write_text(build_about(), encoding="utf-8")

    changed = 0
    all_html = sorted(root.rglob("*.html"))
    for file in all_html:
        text = file.read_text(encoding="utf-8", errors="strict")
        new = inject_nav(text)
        if new != text:
            file.write_text(new, encoding="utf-8")
            changed += 1

    css = root / "app.css"
    if not css.exists():
        raise SystemExit(f"app.css missing: {css}")
    css_text = css.read_text(encoding="utf-8", errors="strict")
    if MARKER not in css_text:
        css.write_text(css_text.rstrip() + "\n" + CSS + "\n", encoding="utf-8")

    # Static release gate: exact required labels + hub coverage for every pre-existing page.
    home = (root / "index.html").read_text(encoding="utf-8", errors="strict")
    for label in ("الرئيسية", "الخدمات", "حول النظام"):
        if f">{label}<" not in home:
            raise SystemExit(f"Primary navigation label missing from Home: {label}")
    services_text = services.read_text(encoding="utf-8", errors="strict")
    missing = [route_for(root, f) for f in before if route_for(root, f) not in services_text]
    if missing:
        raise SystemExit(f"Services hub missing {len(missing)} routes; first={missing[0]}")

    print(
        f"NAVIGATION_INTEGRITY_HOTFIX_APPLIED version=R1 html={len(all_html)} changed={changed} "
        f"services=true about=true connected_legacy_pages={len(before)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
