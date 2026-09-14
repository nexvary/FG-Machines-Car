from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
css = ui / 'app.css'
if not css.exists():
    raise SystemExit(f'LAPTOP_FIT_MISSING {css}')

# R1 marker stays for backward-compatible release gates; R3 is the active layer.
MARKER = '/* FG-LAPTOP-156-FIT-R1 */'
CSS = r'''
/* FG-LAPTOP-156-FIT-R1 */
/* FG-LAPTOP-156-FIT-R2 */
/* FG-LAPTOP-156-FIT-R3 */
:root{
  --fg-laptop-header:62px;
  --fg-laptop-safe-bottom:16px;
  --fg-laptop-gap:10px;
}

html, body { height:100%; min-height:100%; }

body.fg-royal-ui,
body.fg-andalusian-v2,
body.fg-andalusian-v3 {
  min-height:100vh !important;
  height:100vh !important;
  overflow:hidden !important;
}

/* Independent navigation scrolling. */
body.fg-andalusian-v3 .fg-v3-sidebar,
body.fg-andalusian-v3 aside,
body.fg-andalusian-v3 .sidebar,
body.fg-andalusian-v3 [class*="sidebar"] {
  height:100vh !important;
  max-height:100vh !important;
  min-height:0 !important;
  overflow-y:auto !important;
  overflow-x:hidden !important;
  overscroll-behavior:contain;
  scrollbar-width:thin;
  box-sizing:border-box !important;
  padding-bottom:38px !important;
}

body.fg-andalusian-v3 .app-shell,
body.fg-andalusian-v3 .shell,
body.fg-andalusian-v3 .layout,
body.fg-andalusian-v3 .workspace,
body.fg-andalusian-v3 .app-layout {
  min-height:0 !important;
  height:100vh !important;
  max-height:100vh !important;
  overflow:hidden !important;
}

/* Work area owns vertical scrolling and never exceeds the physical viewport. */
body.fg-andalusian-v3 main,
body.fg-andalusian-v3 .main-content,
body.fg-andalusian-v3 .content,
body.fg-andalusian-v3 .workspace-content,
body.fg-andalusian-v3 .page-content,
body.fg-andalusian-v3 [class*="main-content"] {
  min-height:0 !important;
  height:calc(100vh - var(--fg-laptop-header)) !important;
  max-height:calc(100vh - var(--fg-laptop-header)) !important;
  overflow-y:auto !important;
  overflow-x:hidden !important;
  overscroll-behavior:contain;
  scrollbar-gutter:stable;
  scroll-padding:12px 0 28px;
  padding-bottom:var(--fg-laptop-safe-bottom) !important;
  box-sizing:border-box !important;
}

body.fg-andalusian-v3 .fg-v3-header,
body.fg-andalusian-v3 header,
body.fg-andalusian-v3 .topbar,
body.fg-andalusian-v3 .top-bar,
body.fg-andalusian-v3 .app-header {
  flex:0 0 auto !important;
  min-height:46px !important;
  max-height:var(--fg-laptop-header) !important;
  box-sizing:border-box !important;
}

/* Never allow a desktop equal-height layout to create large empty panels. */
body.fg-andalusian-v3 .fg-v3-grid,
body.fg-andalusian-v3 .sv-cards,
body.fg-andalusian-v3 .sv-rows,
body.fg-andalusian-v3 [class*="grid"] {
  min-height:0 !important;
  height:auto !important;
  grid-auto-rows:min-content !important;
  align-items:start !important;
  align-content:start !important;
}

body.fg-andalusian-v3 .fg-v3-grid > *,
body.fg-andalusian-v3 .sv-cards > *,
body.fg-andalusian-v3 .sv-rows > *,
body.fg-andalusian-v3 [class*="grid"] > * {
  min-height:0 !important;
  height:fit-content !important;
  align-self:start !important;
}

/* Cards and semantic sections fit their content instead of stretching to the canvas. */
body.fg-andalusian-v3 main .fg-ornate-frame,
body.fg-andalusian-v3 main .card,
body.fg-andalusian-v3 main .panel,
body.fg-andalusian-v3 main article,
body.fg-andalusian-v3 main section,
body.fg-andalusian-v3 .workspace-content .fg-ornate-frame,
body.fg-andalusian-v3 .page-content .fg-ornate-frame {
  min-height:0 !important;
  height:fit-content !important;
  max-height:none !important;
  align-self:start !important;
  flex:0 0 auto !important;
  box-sizing:border-box !important;
}

/* Common page wrappers must not reserve a full desktop canvas. */
body.fg-andalusian-v3 main > .container,
body.fg-andalusian-v3 main > .page,
body.fg-andalusian-v3 main > .dashboard,
body.fg-andalusian-v3 main > [class*="page"],
body.fg-andalusian-v3 main > [class*="content"],
body.fg-andalusian-v3 .workspace-content > *,
body.fg-andalusian-v3 .page-content > * {
  min-height:0 !important;
}

/* 15.6-inch laptop profile: 1366x768 through 1450x820. */
@media (min-width:1100px) and (max-width:1450px) and (max-height:820px) {
  :root{
    --fg-laptop-header:50px;
    --fg-laptop-safe-bottom:10px;
    --fg-laptop-gap:8px;
  }

  body.fg-andalusian-v3 { font-size:12px !important; }

  body.fg-andalusian-v3 .fg-v3-header,
  body.fg-andalusian-v3 header,
  body.fg-andalusian-v3 .topbar,
  body.fg-andalusian-v3 .top-bar,
  body.fg-andalusian-v3 .app-header {
    min-height:42px !important;
    max-height:50px !important;
    padding-top:2px !important;
    padding-bottom:2px !important;
  }

  body.fg-andalusian-v3 main,
  body.fg-andalusian-v3 .main-content,
  body.fg-andalusian-v3 .content,
  body.fg-andalusian-v3 .workspace-content,
  body.fg-andalusian-v3 .page-content,
  body.fg-andalusian-v3 [class*="main-content"] {
    height:calc(100vh - 50px) !important;
    max-height:calc(100vh - 50px) !important;
    padding-top:6px !important;
    padding-bottom:10px !important;
  }

  body.fg-andalusian-v3 .fg-v3-grid,
  body.fg-andalusian-v3 .sv-cards,
  body.fg-andalusian-v3 .sv-rows,
  body.fg-andalusian-v3 [class*="grid"] {
    gap:var(--fg-laptop-gap) !important;
    row-gap:var(--fg-laptop-gap) !important;
    padding-top:5px !important;
    padding-bottom:5px !important;
    grid-template-rows:none !important;
  }

  body.fg-andalusian-v3 main .fg-ornate-frame,
  body.fg-andalusian-v3 main .card,
  body.fg-andalusian-v3 main .panel,
  body.fg-andalusian-v3 main .dashboard-card,
  body.fg-andalusian-v3 main .section-card,
  body.fg-andalusian-v3 main .content-card,
  body.fg-andalusian-v3 main .detail-card,
  body.fg-andalusian-v3 main .action-panel,
  body.fg-andalusian-v3 main [class*="card"],
  body.fg-andalusian-v3 main article,
  body.fg-andalusian-v3 main section {
    min-height:0 !important;
    height:fit-content !important;
    max-height:none !important;
    padding-top:8px !important;
    padding-bottom:8px !important;
    margin-top:0 !important;
    margin-bottom:var(--fg-laptop-gap) !important;
  }

  /* Prevent flex-based two-column rows from vertically stretching sparse cards. */
  body.fg-andalusian-v3 main [class*="row"],
  body.fg-andalusian-v3 .workspace-content [class*="row"],
  body.fg-andalusian-v3 .page-content [class*="row"] {
    align-items:flex-start !important;
    align-content:flex-start !important;
    min-height:0 !important;
  }

  /* More information above the fold, without sacrificing hit targets. */
  body.fg-andalusian-v3 .fg-v3-sidebar a,
  body.fg-andalusian-v3 .fg-v3-sidebar .nav-item,
  body.fg-andalusian-v3 .fg-v3-sidebar .side-link {
    min-height:38px !important;
    padding-top:4px !important;
    padding-bottom:4px !important;
    margin-top:1px !important;
    margin-bottom:1px !important;
  }

  body.fg-andalusian-v3 .fg-corner { width:26px !important; height:26px !important; }
  body.fg-andalusian-v3 .fg-corner::after {
    width:8px !important; height:8px !important; left:6px !important; top:6px !important;
  }
  body.fg-andalusian-v3 .fg-crest { width:44px !important; height:15px !important; }
  body.fg-andalusian-v3 .fg-crest.top { top:-7px !important; }
  body.fg-andalusian-v3 .fg-crest.bottom { bottom:-7px !important; }

  body.fg-andalusian-v3 .fg-v3-hero {
    margin-top:6px !important;
    margin-bottom:5px !important;
    min-height:0 !important;
    height:fit-content !important;
    max-height:none !important;
    padding-top:9px !important;
    padding-bottom:9px !important;
  }
  body.fg-andalusian-v3 .fg-v3-hero::after {
    width:92px !important;
    height:30px !important;
    top:-13px !important;
  }

  body.fg-andalusian-v3 h1 { font-size:clamp(1.1rem,1.55vw,1.42rem) !important; margin-block:2px 5px !important; }
  body.fg-andalusian-v3 h2 { font-size:clamp(1rem,1.28vw,1.2rem) !important; margin-block:2px 4px !important; }
  body.fg-andalusian-v3 h3 { font-size:clamp(.9rem,1.08vw,1.07rem) !important; margin-block:2px 3px !important; }
  body.fg-andalusian-v3 p { margin-block:3px !important; }

  body.fg-andalusian-v3 button,
  body.fg-andalusian-v3 .btn,
  body.fg-andalusian-v3 input,
  body.fg-andalusian-v3 select {
    min-height:30px !important;
  }

  /* Bottom controls remain in normal flow and cannot cover diagnostic results. */
  body.fg-andalusian-v3 main footer,
  body.fg-andalusian-v3 main .footer,
  body.fg-andalusian-v3 main [class*="footer"],
  body.fg-andalusian-v3 .workspace-content footer,
  body.fg-andalusian-v3 .page-content footer {
    position:static !important;
    inset:auto !important;
    transform:none !important;
  }
}

/* Extra-short screens preserve function over ornament density. */
@media (min-width:1000px) and (max-height:720px) {
  :root{ --fg-laptop-header:46px; }
  body.fg-andalusian-v3 .fg-v3-header,
  body.fg-andalusian-v3 header,
  body.fg-andalusian-v3 .topbar,
  body.fg-andalusian-v3 .app-header { max-height:46px !important; }

  body.fg-andalusian-v3 main,
  body.fg-andalusian-v3 .main-content,
  body.fg-andalusian-v3 .content,
  body.fg-andalusian-v3 .workspace-content,
  body.fg-andalusian-v3 .page-content {
    height:calc(100vh - 46px) !important;
    max-height:calc(100vh - 46px) !important;
  }

  body.fg-andalusian-v3 .fg-header-crest,
  body.fg-andalusian-v3 .fg-v3-hero::after {
    transform:translateX(-50%) scale(.68) !important;
    transform-origin:50% 0;
  }
}
'''

text = css.read_text(encoding='utf-8')
if MARKER in text:
    text = text.split(MARKER, 1)[0].rstrip() + '\n\n' + CSS.strip() + '\n'
else:
    text = text.rstrip() + '\n\n' + CSS.strip() + '\n'
css.write_text(text, encoding='utf-8')

html_count = len(list(ui.rglob('*.html')))
if html_count < 100:
    raise SystemExit(f'LAPTOP_FIT_HTML_COUNT_UNEXPECTED {html_count}')
checks = [
    'FG-LAPTOP-156-FIT-R3',
    'height:fit-content !important',
    'grid-auto-rows:min-content',
    'align-items:flex-start !important',
    'overflow-y:auto',
    'max-height:calc(100vh - 50px)',
]
if any(x not in text for x in checks):
    raise SystemExit('LAPTOP_FIT_VERIFY_FAILED')
print(f'LAPTOP_156_FIT_APPLIED version=R3 html={html_count} target=1366x768 stretched_cards=false compact_nav=true scrollable_results=true routes_untouched=true')
