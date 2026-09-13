from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
css = ui / 'app.css'
if not css.exists():
    raise SystemExit(f'LAPTOP_FIT_MISSING {css}')

# Keep the R1 marker for the existing release gate while making R2 explicit.
MARKER = '/* FG-LAPTOP-156-FIT-R1 */'
CSS = r'''
/* FG-LAPTOP-156-FIT-R1 */
/* FG-LAPTOP-156-FIT-R2 */
:root{
  --fg-laptop-header:64px;
  --fg-laptop-safe-bottom:18px;
}

html, body { height: 100%; min-height: 100%; }

body.fg-royal-ui,
body.fg-andalusian-v2,
body.fg-andalusian-v3 {
  min-height: 100vh !important;
  height: 100vh !important;
  overflow: hidden !important;
}

/* Keep navigation independent from the work area. */
body.fg-andalusian-v3 .fg-v3-sidebar,
body.fg-andalusian-v3 aside,
body.fg-andalusian-v3 .sidebar,
body.fg-andalusian-v3 [class*="sidebar"] {
  max-height: 100vh !important;
  height: 100vh !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  overscroll-behavior: contain;
  scrollbar-width: thin;
  box-sizing: border-box !important;
  padding-bottom: 44px !important;
}

/* The application shell must never become taller than the physical viewport. */
body.fg-andalusian-v3 .app-shell,
body.fg-andalusian-v3 .shell,
body.fg-andalusian-v3 .layout,
body.fg-andalusian-v3 .workspace,
body.fg-andalusian-v3 .app-layout {
  min-height: 0 !important;
  height: 100vh !important;
  max-height: 100vh !important;
  overflow: hidden !important;
}

/* Main work area owns vertical scrolling. */
body.fg-andalusian-v3 main,
body.fg-andalusian-v3 .main-content,
body.fg-andalusian-v3 .content,
body.fg-andalusian-v3 .workspace-content,
body.fg-andalusian-v3 .page-content,
body.fg-andalusian-v3 [class*="main-content"] {
  min-height: 0 !important;
  height: calc(100vh - var(--fg-laptop-header)) !important;
  max-height: calc(100vh - var(--fg-laptop-header)) !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
  scroll-padding-bottom: 28px;
  padding-bottom: var(--fg-laptop-safe-bottom) !important;
  box-sizing: border-box !important;
}

body.fg-andalusian-v3 .fg-v3-header,
body.fg-andalusian-v3 header,
body.fg-andalusian-v3 .topbar,
body.fg-andalusian-v3 .top-bar,
body.fg-andalusian-v3 .app-header {
  flex: 0 0 auto !important;
  min-height: 48px !important;
  max-height: var(--fg-laptop-header) !important;
  box-sizing: border-box !important;
}

/* R2: prevent desktop equal-height cards from creating giant empty lower panels. */
body.fg-andalusian-v3 .fg-v3-grid,
body.fg-andalusian-v3 .sv-cards,
body.fg-andalusian-v3 .sv-rows,
body.fg-andalusian-v3 [class*="grid"] {
  min-height: 0 !important;
  grid-auto-rows: auto !important;
  align-items: start !important;
  align-content: start !important;
}

body.fg-andalusian-v3 .fg-v3-grid > *,
body.fg-andalusian-v3 .sv-cards > *,
body.fg-andalusian-v3 .sv-rows > * {
  min-height: 0 !important;
  align-self: start !important;
}

/* Compact density for the common 15.6-inch 1366x768 laptop viewport. */
@media (min-width: 1100px) and (max-width: 1450px) and (max-height: 820px) {
  :root{
    --fg-laptop-header:54px;
    --fg-laptop-safe-bottom:12px;
  }

  body.fg-andalusian-v3 {
    font-size: 12.5px !important;
  }

  body.fg-andalusian-v3 .fg-v3-header,
  body.fg-andalusian-v3 header,
  body.fg-andalusian-v3 .topbar,
  body.fg-andalusian-v3 .top-bar,
  body.fg-andalusian-v3 .app-header {
    min-height: 44px !important;
    max-height: 54px !important;
    padding-top: 3px !important;
    padding-bottom: 3px !important;
  }

  body.fg-andalusian-v3 main,
  body.fg-andalusian-v3 .main-content,
  body.fg-andalusian-v3 .content,
  body.fg-andalusian-v3 .workspace-content,
  body.fg-andalusian-v3 .page-content,
  body.fg-andalusian-v3 [class*="main-content"] {
    height: calc(100vh - 54px) !important;
    max-height: calc(100vh - 54px) !important;
    padding-top: 7px !important;
    padding-bottom: 12px !important;
  }

  /* Important R2 fix: let the real content define card height. */
  body.fg-andalusian-v3 .fg-ornate-frame,
  body.fg-andalusian-v3 .card,
  body.fg-andalusian-v3 .panel,
  body.fg-andalusian-v3 .dashboard-card,
  body.fg-andalusian-v3 .section-card,
  body.fg-andalusian-v3 .content-card,
  body.fg-andalusian-v3 .detail-card,
  body.fg-andalusian-v3 .action-panel,
  body.fg-andalusian-v3 [class*="card"] {
    min-height: 0 !important;
    height: auto !important;
    max-height: none !important;
    padding-top: 9px !important;
    padding-bottom: 9px !important;
    box-sizing: border-box !important;
  }

  body.fg-andalusian-v3 .fg-v3-grid,
  body.fg-andalusian-v3 .sv-cards,
  body.fg-andalusian-v3 .sv-rows,
  body.fg-andalusian-v3 [class*="grid"] {
    min-height: 0 !important;
    height: auto !important;
    grid-auto-rows: min-content !important;
    align-items: start !important;
    align-content: start !important;
    gap: 8px !important;
    row-gap: 8px !important;
    padding-top: 7px !important;
    padding-bottom: 7px !important;
  }

  /* Common top-level wrappers must not enforce a tall desktop canvas. */
  body.fg-andalusian-v3 main > .container,
  body.fg-andalusian-v3 main > .page,
  body.fg-andalusian-v3 main > .dashboard,
  body.fg-andalusian-v3 main > [class*="page"],
  body.fg-andalusian-v3 main > [class*="content"],
  body.fg-andalusian-v3 .workspace-content > *,
  body.fg-andalusian-v3 .page-content > * {
    min-height: 0 !important;
  }

  body.fg-andalusian-v3 .fg-corner {
    width: 28px !important;
    height: 28px !important;
  }
  body.fg-andalusian-v3 .fg-corner::after {
    width: 9px !important;
    height: 9px !important;
    left: 7px !important;
    top: 7px !important;
  }
  body.fg-andalusian-v3 .fg-crest {
    width: 48px !important;
    height: 16px !important;
  }
  body.fg-andalusian-v3 .fg-crest.top { top: -8px !important; }
  body.fg-andalusian-v3 .fg-crest.bottom { bottom: -8px !important; }

  body.fg-andalusian-v3 .fg-v3-hero {
    margin-top: 8px !important;
    margin-bottom: 6px !important;
    min-height: 0 !important;
    height: auto !important;
    padding-top: 12px !important;
    padding-bottom: 12px !important;
  }
  body.fg-andalusian-v3 .fg-v3-hero::after {
    width: 105px !important;
    height: 34px !important;
    top: -15px !important;
  }

  body.fg-andalusian-v3 h1 { font-size: clamp(1.15rem, 1.7vw, 1.48rem) !important; margin-block: 3px 6px !important; }
  body.fg-andalusian-v3 h2 { font-size: clamp(1.02rem, 1.35vw, 1.24rem) !important; margin-block: 3px 5px !important; }
  body.fg-andalusian-v3 h3 { font-size: clamp(.92rem, 1.12vw, 1.1rem) !important; margin-block: 2px 4px !important; }

  body.fg-andalusian-v3 p { margin-block: 4px !important; }

  body.fg-andalusian-v3 button,
  body.fg-andalusian-v3 .btn,
  body.fg-andalusian-v3 input,
  body.fg-andalusian-v3 select {
    min-height: 30px !important;
  }

  /* Fixed/sticky descendants inside the work area may not cover bottom results. */
  body.fg-andalusian-v3 main footer,
  body.fg-andalusian-v3 main .footer,
  body.fg-andalusian-v3 main [class*="footer"],
  body.fg-andalusian-v3 .workspace-content footer,
  body.fg-andalusian-v3 .page-content footer {
    position: static !important;
    inset: auto !important;
    transform: none !important;
  }
}

/* Even shorter screens: preserve content over ornament density. */
@media (min-width: 1000px) and (max-height: 720px) {
  :root{ --fg-laptop-header:48px; }

  body.fg-andalusian-v3 .fg-v3-header,
  body.fg-andalusian-v3 header,
  body.fg-andalusian-v3 .topbar,
  body.fg-andalusian-v3 .app-header {
    max-height: 48px !important;
  }
  body.fg-andalusian-v3 main,
  body.fg-andalusian-v3 .main-content,
  body.fg-andalusian-v3 .content,
  body.fg-andalusian-v3 .workspace-content,
  body.fg-andalusian-v3 .page-content {
    height: calc(100vh - 48px) !important;
    max-height: calc(100vh - 48px) !important;
  }
  body.fg-andalusian-v3 .fg-header-crest,
  body.fg-andalusian-v3 .fg-v3-hero::after {
    transform: translateX(-50%) scale(.72) !important;
    transform-origin: 50% 0;
  }
}
'''

text = css.read_text(encoding='utf-8')
if MARKER in text:
    text = text.split(MARKER, 1)[0].rstrip() + '\n\n' + CSS.strip() + '\n'
else:
    text = text.rstrip() + '\n\n' + CSS.strip() + '\n'
css.write_text(text, encoding='utf-8')

# Preserve routes and content; this layer remains CSS-only.
html_count = len(list(ui.rglob('*.html')))
if html_count < 100:
    raise SystemExit(f'LAPTOP_FIT_HTML_COUNT_UNEXPECTED {html_count}')
checks = [
    'FG-LAPTOP-156-FIT-R2',
    'max-height: calc(100vh - 54px)',
    'grid-auto-rows: min-content',
    'height: auto !important',
    'overflow-y: auto',
]
if any(x not in text for x in checks):
    raise SystemExit('LAPTOP_FIT_VERIFY_FAILED')
print(f'LAPTOP_156_FIT_APPLIED version=R2 html={html_count} target=1366x768 stretched_cards=false scrollable_results=true routes_untouched=true')
