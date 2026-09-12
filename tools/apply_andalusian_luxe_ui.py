from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
css = ui / 'app.css'

if not ui.exists() or not css.exists():
    raise SystemExit(f'ANDALUSIAN_UI_MISSING {ui}')

MARKER = '/* FG-ANDALUSIAN-LUXE-V2 */'

ANDALUSIAN_CSS = r'''
/* FG-ANDALUSIAN-LUXE-V2 */
:root{
  --fg-and-gold:#d4af37;
  --fg-and-gold-2:#f6da83;
  --fg-and-gold-3:#8f620b;
  --fg-and-plum:#250321;
  --fg-and-plum-2:#5f0b50;
  --fg-and-pink:#c52d84;
  --fg-and-ivory:#fff8ec;
  --fg-and-ink:#16245a;
}

body.fg-royal-purple.fg-andalusian-luxe{
  background:
    radial-gradient(circle at 50% -8%,rgba(255,92,182,.20),transparent 30%),
    radial-gradient(circle at 8% 20%,rgba(255,114,196,.12),transparent 23%),
    radial-gradient(circle at 92% 22%,rgba(255,114,196,.13),transparent 24%),
    linear-gradient(135deg,#23021f 0%,#4d073f 33%,#7e115e 66%,#2b0328 100%)!important;
}

/* Andalusian floral field */
body.fg-andalusian-luxe::after{
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  z-index:-1;
  opacity:.18;
  background-image:
    radial-gradient(circle at 12px 12px,rgba(246,218,131,.36) 0 1.2px,transparent 1.7px),
    conic-gradient(from 45deg at 50% 50%,transparent 0 12.5%,rgba(255,118,196,.18) 12.5% 14%,transparent 14% 37%,rgba(255,118,196,.16) 37% 39%,transparent 39% 100%);
  background-size:54px 54px,92px 92px;
}

/* Ornate gold frame primitive */
body.fg-andalusian-luxe .card,
body.fg-andalusian-luxe .panel,
body.fg-andalusian-luxe .module-card,
body.fg-andalusian-luxe .detail-card,
body.fg-andalusian-luxe .action-panel,
body.fg-andalusian-luxe .dashboard-card,
body.fg-andalusian-luxe .section-card,
body.fg-andalusian-luxe .content-card,
body.fg-andalusian-luxe .metric-card,
body.fg-andalusian-luxe .tile,
body.fg-andalusian-luxe .hero,
body.fg-andalusian-luxe .hero-card,
body.fg-andalusian-luxe .welcome,
body.fg-andalusian-luxe .overview-banner,
body.fg-andalusian-luxe .dashboard-hero{
  position:relative!important;
  border:2px solid var(--fg-and-gold)!important;
  outline:1px solid rgba(246,218,131,.44)!important;
  outline-offset:-6px!important;
  border-radius:14px!important;
  box-shadow:
    0 0 0 1px rgba(83,41,4,.55),
    0 8px 24px rgba(28,0,25,.26),
    inset 0 0 0 2px rgba(255,247,218,.68),
    inset 0 0 18px rgba(212,175,55,.12)!important;
}

/* Four decorative corners made from CSS, no image dependency */
body.fg-andalusian-luxe .card::before,
body.fg-andalusian-luxe .panel::before,
body.fg-andalusian-luxe .module-card::before,
body.fg-andalusian-luxe .detail-card::before,
body.fg-andalusian-luxe .action-panel::before,
body.fg-andalusian-luxe .dashboard-card::before,
body.fg-andalusian-luxe .section-card::before,
body.fg-andalusian-luxe .content-card::before,
body.fg-andalusian-luxe .metric-card::before,
body.fg-andalusian-luxe .tile::before,
body.fg-andalusian-luxe .hero::before,
body.fg-andalusian-luxe .hero-card::before,
body.fg-andalusian-luxe .welcome::before,
body.fg-andalusian-luxe .overview-banner::before,
body.fg-andalusian-luxe .dashboard-hero::before{
  content:"";
  position:absolute;
  inset:4px;
  border-radius:10px;
  pointer-events:none;
  z-index:2;
  background:
    radial-gradient(circle at 0 0,transparent 0 16px,var(--fg-and-gold) 16px 18px,transparent 18px 100%),
    radial-gradient(circle at 100% 0,transparent 0 16px,var(--fg-and-gold) 16px 18px,transparent 18px 100%),
    radial-gradient(circle at 0 100%,transparent 0 16px,var(--fg-and-gold) 16px 18px,transparent 18px 100%),
    radial-gradient(circle at 100% 100%,transparent 0 16px,var(--fg-and-gold) 16px 18px,transparent 18px 100%);
  box-shadow:inset 0 0 0 1px rgba(246,218,131,.40);
}

body.fg-andalusian-luxe .card::after,
body.fg-andalusian-luxe .module-card::after,
body.fg-andalusian-luxe .dashboard-card::after,
body.fg-andalusian-luxe .detail-card::after,
body.fg-andalusian-luxe .tile::after{
  content:"◆";
  position:absolute;
  top:-11px;
  left:50%;
  transform:translateX(-50%) rotate(45deg);
  width:20px;
  height:20px;
  display:grid;
  place-items:center;
  color:var(--fg-and-gold-2);
  background:linear-gradient(135deg,#7a4e05,#d4af37 48%,#fff1a8 52%,#8e6109);
  border:1px solid #6f4805;
  box-shadow:0 0 10px rgba(246,218,131,.45);
  font-size:8px;
  z-index:4;
}

/* Arabesque separators */
body.fg-andalusian-luxe .card>h1,
body.fg-andalusian-luxe .card>h2,
body.fg-andalusian-luxe .card>h3,
body.fg-andalusian-luxe .panel>h1,
body.fg-andalusian-luxe .panel>h2,
body.fg-andalusian-luxe .panel>h3,
body.fg-andalusian-luxe .section-title{
  position:relative;
  padding-bottom:10px!important;
}
body.fg-andalusian-luxe .card>h1::after,
body.fg-andalusian-luxe .card>h2::after,
body.fg-andalusian-luxe .card>h3::after,
body.fg-andalusian-luxe .panel>h1::after,
body.fg-andalusian-luxe .panel>h2::after,
body.fg-andalusian-luxe .panel>h3::after,
body.fg-andalusian-luxe .section-title::after{
  content:"✦  ◆  ✦";
  display:block;
  margin-top:6px;
  letter-spacing:5px;
  font-size:9px;
  color:var(--fg-and-gold);
  text-align:center;
  border-bottom:1px solid rgba(212,175,55,.48);
  line-height:8px;
}

/* Moorish arch for hero and VCI/primary diagnostic panels */
body.fg-andalusian-luxe .hero,
body.fg-andalusian-luxe .hero-card,
body.fg-andalusian-luxe .welcome,
body.fg-andalusian-luxe .overview-banner,
body.fg-andalusian-luxe .dashboard-hero,
body.fg-andalusian-luxe .vci-card,
body.fg-andalusian-luxe .vci-panel{
  border-radius:20px 20px 14px 14px!important;
  clip-path:polygon(0 7%,5% 7%,8% 2%,11% 7%,44% 7%,50% 0,56% 7%,89% 7%,92% 2%,95% 7%,100% 7%,100% 100%,0 100%)!important;
  padding-top:22px!important;
}

/* Sidebar: framed alcove feeling */
body.fg-andalusian-luxe aside,
body.fg-andalusian-luxe .sidebar,
body.fg-andalusian-luxe .side-nav,
body.fg-andalusian-luxe .app-sidebar{
  position:relative!important;
  border-inline-end:3px double var(--fg-and-gold)!important;
  box-shadow:inset -5px 0 0 rgba(246,218,131,.13),6px 0 22px rgba(24,0,24,.30)!important;
}
body.fg-andalusian-luxe aside::before,
body.fg-andalusian-luxe .sidebar::before,
body.fg-andalusian-luxe .side-nav::before,
body.fg-andalusian-luxe .app-sidebar::before{
  content:"✦  ❖  ✦";
  display:block;
  text-align:center;
  color:var(--fg-and-gold-2);
  letter-spacing:7px;
  padding:8px 0 10px;
  border-bottom:1px solid rgba(212,175,55,.55);
  text-shadow:0 0 9px rgba(246,218,131,.45);
}
body.fg-andalusian-luxe nav a,
body.fg-andalusian-luxe .nav-item,
body.fg-andalusian-luxe .side-link,
body.fg-andalusian-luxe .sidebar a{
  border-inline-start:2px solid rgba(212,175,55,.22)!important;
  border-radius:6px 16px 16px 6px!important;
  margin-block:3px!important;
}
body.fg-andalusian-luxe nav a.active,
body.fg-andalusian-luxe .nav-item.active,
body.fg-andalusian-luxe .side-link.active,
body.fg-andalusian-luxe [aria-current="page"]{
  box-shadow:
    0 0 0 1px rgba(246,218,131,.58),
    inset 0 0 0 1px rgba(255,245,214,.28),
    0 0 16px rgba(230,67,154,.45)!important;
}

/* Header/footer imperial framing */
body.fg-andalusian-luxe .topbar,
body.fg-andalusian-luxe .top-bar,
body.fg-andalusian-luxe .app-header,
body.fg-andalusian-luxe .main-header,
body.fg-andalusian-luxe .masthead,
body.fg-andalusian-luxe header.app-topbar{
  position:relative!important;
  border-top:2px solid var(--fg-and-gold)!important;
  border-bottom:3px double var(--fg-and-gold)!important;
  box-shadow:0 4px 0 rgba(246,218,131,.16),0 9px 26px rgba(28,0,25,.32)!important;
}
body.fg-andalusian-luxe .topbar::after,
body.fg-andalusian-luxe .app-header::after,
body.fg-andalusian-luxe .main-header::after,
body.fg-andalusian-luxe .masthead::after{
  content:"◆  ✦  ◆";
  position:absolute;
  bottom:-11px;
  left:50%;
  transform:translateX(-50%);
  color:var(--fg-and-gold-2);
  background:var(--fg-and-plum);
  padding:0 13px;
  font-size:10px;
  letter-spacing:5px;
  z-index:5;
}
body.fg-andalusian-luxe footer,
body.fg-andalusian-luxe .footer,
body.fg-andalusian-luxe .statusbar,
body.fg-andalusian-luxe .status-bar{
  border-top:3px double var(--fg-and-gold)!important;
  background:linear-gradient(90deg,#22031f,#5b0a4d,#260322)!important;
  color:#fff8e6!important;
}

/* Small diagnostic tiles resemble ivory plaques with gold filigree */
body.fg-andalusian-luxe .module-card,
body.fg-andalusian-luxe .metric-card,
body.fg-andalusian-luxe .tile{
  background:
    radial-gradient(circle at 8% 8%,rgba(212,175,55,.12),transparent 18%),
    radial-gradient(circle at 92% 92%,rgba(212,175,55,.10),transparent 18%),
    linear-gradient(145deg,#fffdf7,#f6e6ce)!important;
}
body.fg-andalusian-luxe .module-card:hover,
body.fg-andalusian-luxe .metric-card:hover,
body.fg-andalusian-luxe .tile:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 10px 26px rgba(36,0,33,.26),0 0 0 2px rgba(246,218,131,.38)!important;
}

/* Semantic views receive same ornament language */
body.fg-andalusian-luxe .sv-banner,
body.fg-andalusian-luxe .sv-diagram,
body.fg-andalusian-luxe .sv-doc,
body.fg-andalusian-luxe .sv-chat,
body.fg-andalusian-luxe .sv-quiz,
body.fg-andalusian-luxe .sv-split>div,
body.fg-andalusian-luxe .sv-cards>div,
body.fg-andalusian-luxe .sv-rows>div,
body.fg-andalusian-luxe .sv-langs span,
body.fg-andalusian-luxe .sv-themes div,
body.fg-andalusian-luxe .sv-track span{
  border:2px solid var(--fg-and-gold)!important;
  outline:1px solid rgba(246,218,131,.32)!important;
  outline-offset:-5px!important;
  border-radius:12px!important;
}

/* buttons as royal plaques */
body.fg-andalusian-luxe button,
body.fg-andalusian-luxe .btn,
body.fg-andalusian-luxe .action-btn,
body.fg-andalusian-luxe [role="button"]{
  border:2px solid var(--fg-and-gold)!important;
  box-shadow:inset 0 0 0 1px rgba(246,218,131,.32),0 5px 12px rgba(31,0,27,.18)!important;
}

@media(max-width:1000px){
  body.fg-andalusian-luxe .hero,
  body.fg-andalusian-luxe .hero-card,
  body.fg-andalusian-luxe .welcome,
  body.fg-andalusian-luxe .overview-banner,
  body.fg-andalusian-luxe .dashboard-hero,
  body.fg-andalusian-luxe .vci-card,
  body.fg-andalusian-luxe .vci-panel{
    clip-path:none!important;
    padding-top:14px!important;
  }
  body.fg-andalusian-luxe .card::after,
  body.fg-andalusian-luxe .module-card::after,
  body.fg-andalusian-luxe .dashboard-card::after,
  body.fg-andalusian-luxe .detail-card::after,
  body.fg-andalusian-luxe .tile::after{display:none!important;}
}
'''

text = css.read_text(encoding='utf-8')
if MARKER in text:
    text = text.split(MARKER)[0].rstrip() + '\n\n'
css.write_text(text + ANDALUSIAN_CSS + '\n', encoding='utf-8')

html_files = list(ui.rglob('*.html'))
changed = 0
marked = 0
for html in html_files:
    source = html.read_text(encoding='utf-8')
    if 'fg-andalusian-luxe' in source:
        marked += 1
        continue
    if '<body' not in source:
        continue
    if 'class="' in source[source.find('<body'):source.find('>', source.find('<body'))+1]:
        source = source.replace('class="fg-royal-purple', 'class="fg-royal-purple fg-andalusian-luxe', 1)
    else:
        source = source.replace('<body', '<body class="fg-andalusian-luxe"', 1)
    html.write_text(source, encoding='utf-8')
    changed += 1
    marked += 1

if marked == 0:
    raise SystemExit('ANDALUSIAN_UI_MARKING_FAIL no html marked')

print(f'ANDALUSIAN_LUXE_UI_APPLIED version=V2 html={len(html_files)} changed={changed} ornate_frames=true moorish_arches=true routes_untouched=true')
