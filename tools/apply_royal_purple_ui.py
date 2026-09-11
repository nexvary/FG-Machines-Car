from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
css = ui / 'app.css'

if not ui.exists() or not css.exists():
    raise SystemExit(f'ROYAL_UI_MISSING {ui}')

MARKER = '/* FG-ROYAL-PURPLE-UI-V1 */'

ROYAL_CSS = r'''
/* FG-ROYAL-PURPLE-UI-V1 */
:root{
  --fg-royal-plum-950:#21051f;
  --fg-royal-plum-900:#31072f;
  --fg-royal-purple-850:#460a4c;
  --fg-royal-purple-750:#6a145f;
  --fg-royal-fuchsia:#a12276;
  --fg-royal-pink:#d44f96;
  --fg-royal-pink-soft:#ed9ec5;
  --fg-royal-gold:#d4af37;
  --fg-royal-gold-deep:#9b6d10;
  --fg-royal-gold-light:#f6da83;
  --fg-royal-ivory:#fff7eb;
  --fg-royal-ivory-2:#f9ead6;
  --fg-royal-ink:#17234a;
  --fg-royal-muted:#74566f;
  --fg-royal-success:#2acb78;
  --fg-royal-danger:#cf304e;
}

html,body{min-height:100%;}
body.fg-royal-purple{
  color:var(--fg-royal-ink)!important;
  background:
    radial-gradient(circle at 12% 8%,rgba(237,98,171,.28),transparent 28%),
    radial-gradient(circle at 88% 4%,rgba(135,33,113,.34),transparent 30%),
    radial-gradient(circle at 80% 82%,rgba(207,57,142,.22),transparent 34%),
    linear-gradient(135deg,#31072f 0%,#641052 42%,#8a1d68 72%,#4a0b49 100%)!important;
  background-attachment:fixed!important;
}
body.fg-royal-purple::before{
  content:"";
  position:fixed;
  inset:0;
  z-index:-1;
  pointer-events:none;
  opacity:.34;
  background-image:
    radial-gradient(circle at 18px 18px,rgba(246,218,131,.24) 0 1px,transparent 1.7px),
    radial-gradient(circle at 46px 46px,rgba(255,176,220,.18) 0 1px,transparent 1.7px);
  background-size:64px 64px;
}

body.fg-royal-purple .app-shell,
body.fg-royal-purple .shell,
body.fg-royal-purple .workspace,
body.fg-royal-purple .main-shell,
body.fg-royal-purple .page-shell{
  background:transparent!important;
}

body.fg-royal-purple .topbar,
body.fg-royal-purple .top-bar,
body.fg-royal-purple .app-header,
body.fg-royal-purple .main-header,
body.fg-royal-purple .masthead,
body.fg-royal-purple header.app-topbar{
  color:#fff9ef!important;
  background:
    linear-gradient(90deg,rgba(33,5,31,.98),rgba(112,17,84,.96) 55%,rgba(70,10,76,.98))!important;
  border-bottom:1px solid var(--fg-royal-gold)!important;
  box-shadow:0 7px 22px rgba(33,5,31,.32),inset 0 -1px 0 rgba(246,218,131,.4)!important;
}

body.fg-royal-purple aside,
body.fg-royal-purple .sidebar,
body.fg-royal-purple .side-nav,
body.fg-royal-purple .navigation-panel,
body.fg-royal-purple .app-sidebar{
  color:#fff9ef!important;
  background:
    radial-gradient(circle at 50% 5%,rgba(192,44,132,.24),transparent 25%),
    linear-gradient(180deg,#260523 0%,#3a0838 46%,#22051f 100%)!important;
  border-inline-end:1px solid rgba(246,218,131,.86)!important;
  box-shadow:6px 0 22px rgba(24,0,24,.24),inset -1px 0 0 rgba(212,175,55,.28)!important;
}

body.fg-royal-purple nav a,
body.fg-royal-purple .nav-item,
body.fg-royal-purple .side-link,
body.fg-royal-purple .sidebar a{
  color:#fff7ed!important;
  border:1px solid transparent!important;
  border-radius:12px!important;
  transition:background .16s ease,border-color .16s ease,transform .16s ease,box-shadow .16s ease!important;
}
body.fg-royal-purple nav a:hover,
body.fg-royal-purple .nav-item:hover,
body.fg-royal-purple .side-link:hover,
body.fg-royal-purple .sidebar a:hover{
  color:#fffdf8!important;
  background:linear-gradient(90deg,rgba(149,24,105,.72),rgba(205,55,139,.5))!important;
  border-color:rgba(246,218,131,.65)!important;
  transform:translateX(2px);
  box-shadow:0 5px 16px rgba(21,1,23,.2)!important;
}
body.fg-royal-purple nav a.active,
body.fg-royal-purple .nav-item.active,
body.fg-royal-purple .side-link.active,
body.fg-royal-purple [aria-current="page"]{
  color:#fffdf8!important;
  background:linear-gradient(90deg,#a52573,#d54c96)!important;
  border-color:var(--fg-royal-gold-light)!important;
  box-shadow:0 0 0 1px rgba(155,109,16,.42),0 7px 20px rgba(59,5,55,.32),inset 0 1px 0 rgba(255,255,255,.22)!important;
}

body.fg-royal-purple main,
body.fg-royal-purple .main-content,
body.fg-royal-purple .content,
body.fg-royal-purple .workspace-content{
  background:transparent!important;
}

body.fg-royal-purple .card,
body.fg-royal-purple .panel,
body.fg-royal-purple .module-card,
body.fg-royal-purple .detail-card,
body.fg-royal-purple .action-panel,
body.fg-royal-purple .dashboard-card,
body.fg-royal-purple .section-card,
body.fg-royal-purple .content-card,
body.fg-royal-purple .metric-card,
body.fg-royal-purple .tile,
body.fg-royal-purple [class*="card"]{
  color:var(--fg-royal-ink)!important;
  background:
    linear-gradient(145deg,rgba(255,250,242,.985),rgba(249,234,214,.965))!important;
  border:1px solid var(--fg-royal-gold)!important;
  border-radius:15px!important;
  box-shadow:
    0 10px 26px rgba(48,5,48,.18),
    inset 0 0 0 1px rgba(246,218,131,.44),
    inset 0 1px 0 rgba(255,255,255,.9)!important;
}

body.fg-royal-purple .card:hover,
body.fg-royal-purple .module-card:hover,
body.fg-royal-purple .tile:hover{
  border-color:var(--fg-royal-gold-light)!important;
  box-shadow:0 13px 31px rgba(48,5,48,.24),0 0 0 1px rgba(246,218,131,.45)!important;
}

body.fg-royal-purple .hero,
body.fg-royal-purple .hero-card,
body.fg-royal-purple .welcome,
body.fg-royal-purple .overview-banner,
body.fg-royal-purple .dashboard-hero{
  color:var(--fg-royal-ink)!important;
  background:
    radial-gradient(circle at 78% 38%,rgba(216,77,150,.17),transparent 27%),
    linear-gradient(135deg,#fff9f0 0%,#f9e7d8 58%,#f0c4d8 100%)!important;
  border:1px solid var(--fg-royal-gold)!important;
  box-shadow:0 13px 30px rgba(46,4,44,.22),inset 0 0 0 1px rgba(246,218,131,.46)!important;
}

body.fg-royal-purple h1,
body.fg-royal-purple h2,
body.fg-royal-purple h3,
body.fg-royal-purple h4,
body.fg-royal-purple .title,
body.fg-royal-purple .section-title{
  color:#17265c!important;
  text-shadow:0 1px 0 rgba(255,255,255,.7);
}
body.fg-royal-purple aside h1,
body.fg-royal-purple aside h2,
body.fg-royal-purple aside h3,
body.fg-royal-purple .sidebar h1,
body.fg-royal-purple .sidebar h2,
body.fg-royal-purple .sidebar h3,
body.fg-royal-purple .topbar h1,
body.fg-royal-purple .topbar h2,
body.fg-royal-purple .app-header h1,
body.fg-royal-purple .app-header h2{
  color:#fff8e8!important;
  text-shadow:none!important;
}

body.fg-royal-purple button,
body.fg-royal-purple .btn,
body.fg-royal-purple .action-btn,
body.fg-royal-purple [role="button"]{
  border:1px solid var(--fg-royal-gold)!important;
  border-radius:11px!important;
}
body.fg-royal-purple button:not(:disabled),
body.fg-royal-purple .btn:not(.secondary),
body.fg-royal-purple .action-btn:not(.action-write-locked){
  color:#fff9ef!important;
  background:linear-gradient(135deg,#4b0a4e,#9d1f72)!important;
  box-shadow:0 6px 16px rgba(53,4,48,.2),inset 0 1px 0 rgba(255,255,255,.16)!important;
}
body.fg-royal-purple button:not(:disabled):hover,
body.fg-royal-purple .btn:not(.secondary):hover,
body.fg-royal-purple .action-btn:not(.action-write-locked):hover{
  background:linear-gradient(135deg,#68105c,#c43688)!important;
  border-color:var(--fg-royal-gold-light)!important;
  transform:translateY(-1px);
}
body.fg-royal-purple button:focus-visible,
body.fg-royal-purple a:focus-visible,
body.fg-royal-purple input:focus-visible,
body.fg-royal-purple select:focus-visible{
  outline:2px solid var(--fg-royal-gold-light)!important;
  outline-offset:2px!important;
}

body.fg-royal-purple input,
body.fg-royal-purple select,
body.fg-royal-purple textarea{
  color:var(--fg-royal-ink)!important;
  background:rgba(255,249,240,.96)!important;
  border:1px solid rgba(155,109,16,.58)!important;
  border-radius:10px!important;
}

body.fg-royal-purple table,
body.fg-royal-purple .table,
body.fg-royal-purple .data-table{
  background:rgba(255,250,242,.95)!important;
  color:var(--fg-royal-ink)!important;
  border-color:rgba(155,109,16,.42)!important;
}
body.fg-royal-purple th{
  color:#fff8ee!important;
  background:linear-gradient(90deg,#4a0a48,#7d1768)!important;
  border-color:rgba(246,218,131,.45)!important;
}
body.fg-royal-purple td{border-color:rgba(155,109,16,.22)!important;}
body.fg-royal-purple tr:nth-child(even) td{background:rgba(235,197,218,.13)!important;}

body.fg-royal-purple .badge,
body.fg-royal-purple .chip,
body.fg-royal-purple .tag,
body.fg-royal-purple .status-pill{
  color:#4b0a43!important;
  background:#f7dc91!important;
  border:1px solid #c49223!important;
}
body.fg-royal-purple .success,
body.fg-royal-purple .status-ok{color:#0f7845!important;}
body.fg-royal-purple .danger,
body.fg-royal-purple .error,
body.fg-royal-purple .status-error{color:#a51f3b!important;}

body.fg-royal-purple .sv-banner,
body.fg-royal-purple .sv-diagram,
body.fg-royal-purple .sv-doc,
body.fg-royal-purple .sv-chat,
body.fg-royal-purple .sv-quiz,
body.fg-royal-purple .sv-split>div,
body.fg-royal-purple .sv-cards>div,
body.fg-royal-purple .sv-rows>div,
body.fg-royal-purple .sv-langs span,
body.fg-royal-purple .sv-themes div,
body.fg-royal-purple .sv-track span{
  color:var(--fg-royal-ink)!important;
  background:linear-gradient(145deg,#fffaf2,#f8e8d8)!important;
  border-color:rgba(180,126,25,.72)!important;
  box-shadow:inset 0 0 0 1px rgba(246,218,131,.28)!important;
}
body.fg-royal-purple .sv-banner b,
body.fg-royal-purple .sv-cards b,
body.fg-royal-purple .sv-rows b,
body.fg-royal-purple .sv-doc h4,
body.fg-royal-purple .sv-split b,
body.fg-royal-purple .sv-diagram b{
  color:#17265c!important;
}
body.fg-royal-purple .sv-banner span,
body.fg-royal-purple .sv-cards small,
body.fg-royal-purple .sv-rows small,
body.fg-royal-purple .sv-split small,
body.fg-royal-purple .sv-listhead{
  color:#8b4d74!important;
}
body.fg-royal-purple .sv-diagram b{
  border-color:var(--fg-royal-gold)!important;
  background:rgba(255,250,240,.72)!important;
}
body.fg-royal-purple .sv-diagram span{
  background:var(--fg-royal-gold-light)!important;
  box-shadow:0 0 14px rgba(246,218,131,.9)!important;
}
body.fg-royal-purple .sv-gate{
  color:#17653f!important;
  border-color:#55bc83!important;
  background:rgba(242,255,247,.88)!important;
}
body.fg-royal-purple .sv-gate strong{color:#145336!important;}
body.fg-royal-purple .sv-remote{
  color:#fff4cf!important;
  background:linear-gradient(150deg,#420940,#26051f)!important;
  border-color:var(--fg-royal-gold)!important;
  box-shadow:0 10px 24px rgba(37,3,35,.28),inset 0 0 0 1px rgba(246,218,131,.28)!important;
}
body.fg-royal-purple .sv-remote i{border-color:var(--fg-royal-gold-light)!important;}

body.fg-royal-purple .status-card,
body.fg-royal-purple .vci-card,
body.fg-royal-purple [class*="vci-status"],
body.fg-royal-purple [class*="connection-card"]{
  color:#fff8ea!important;
  background:linear-gradient(145deg,#25102f,#0c1d46)!important;
  border-color:var(--fg-royal-gold)!important;
}
body.fg-royal-purple .status-card h3,
body.fg-royal-purple .vci-card h3,
body.fg-royal-purple [class*="connection-card"] h3{color:#f6d978!important;}

body.fg-royal-purple svg,
body.fg-royal-purple .icon{filter:saturate(.92) contrast(1.03);}
body.fg-royal-purple .sidebar svg,
body.fg-royal-purple .side-nav svg{color:var(--fg-royal-gold-light)!important;}

body.fg-royal-purple footer,
body.fg-royal-purple .statusbar,
body.fg-royal-purple .status-bar,
body.fg-royal-purple .app-footer{
  color:#fff4e4!important;
  background:linear-gradient(90deg,#250521,#5e0e52,#280522)!important;
  border-top:1px solid var(--fg-royal-gold)!important;
}

@media(max-width:1100px){
  body.fg-royal-purple .card,
  body.fg-royal-purple .panel,
  body.fg-royal-purple [class*="card"]{border-radius:13px!important;}
}
@media(max-width:760px){
  body.fg-royal-purple{background:linear-gradient(180deg,#3b0739,#74135c 52%,#3a073d)!important;}
  body.fg-royal-purple aside,
  body.fg-royal-purple .sidebar,
  body.fg-royal-purple .side-nav{box-shadow:none!important;}
}
'''

existing = css.read_text(encoding='utf-8')
if MARKER in existing:
    existing = existing.split(MARKER)[0].rstrip() + '\n'
css.write_text(existing + '\n' + ROYAL_CSS.strip() + '\n', encoding='utf-8')

html_files = sorted(ui.rglob('*.html'))
if not html_files:
    raise SystemExit('ROYAL_UI_NO_HTML')

changed_html = 0
for page in html_files:
    text = page.read_text(encoding='utf-8')
    original = text
    if 'fg-royal-purple' not in text:
        def patch_body(match):
            attrs = match.group(1)
            class_match = re.search(r'class=("|\')(.*?)(\1)', attrs, flags=re.I | re.S)
            if class_match:
                quote = class_match.group(1)
                classes = class_match.group(2).strip()
                replacement = f'class={quote}{classes} fg-royal-purple{quote}'
                attrs2 = attrs[:class_match.start()] + replacement + attrs[class_match.end():]
                return '<body' + attrs2 + '>'
            return '<body class="fg-royal-purple"' + attrs + '>'
        text, n = re.subn(r'<body([^>]*)>', patch_body, text, count=1, flags=re.I | re.S)
        if n == 0:
            raise SystemExit(f'ROYAL_UI_BODY_NOT_FOUND {page}')
    text = re.sub(r'<meta\s+name=["\']theme-color["\'][^>]*>',
                  '<meta name="theme-color" content="#5e0e52">', text,
                  count=1, flags=re.I)
    if text != original:
        page.write_text(text, encoding='utf-8')
        changed_html += 1

# Static contract checks: styling only, no route/action mutation.
css_after = css.read_text(encoding='utf-8')
required_tokens = [
    'FG-ROYAL-PURPLE-UI-V1',
    '--fg-royal-gold:#d4af37',
    '--fg-royal-pink:#d44f96',
    'body.fg-royal-purple .sidebar',
    'body.fg-royal-purple .card',
]
for token in required_tokens:
    if token not in css_after:
        raise SystemExit(f'ROYAL_UI_CONTRACT_FAIL {token}')

marked = 0
for page in html_files:
    if 'fg-royal-purple' in page.read_text(encoding='utf-8'):
        marked += 1
if marked != len(html_files):
    raise SystemExit(f'ROYAL_UI_MARKING_FAIL marked={marked} total={len(html_files)}')

print(f'ROYAL_PURPLE_UI_APPLIED version=V1 html={len(html_files)} changed={changed_html} palette=purple-pink+royal-gold routes_untouched=true')
