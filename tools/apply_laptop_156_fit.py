from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
css = ui / 'app.css'
if not css.exists():
    raise SystemExit(f'LAPTOP_FIT_MISSING {css}')

MARKER = '/* FG-LAPTOP-156-FIT-R1 */'
CSS = r'''
/* FG-LAPTOP-156-FIT-R1 */
html, body { height: 100%; min-height: 100%; }

body.fg-royal-ui,
body.fg-andalusian-v2,
body.fg-andalusian-v3 {
  min-height: 100vh !important;
  height: 100vh !important;
  overflow: hidden !important;
}

/* Keep the navigation usable without pushing content below the viewport. */
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
}

/* The application shell itself must never be taller than the screen. */
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

/* Main work area gets its own vertical scroll, so result panels can always be reached. */
body.fg-andalusian-v3 main,
body.fg-andalusian-v3 .main-content,
body.fg-andalusian-v3 .content,
body.fg-andalusian-v3 .workspace-content,
body.fg-andalusian-v3 .page-content,
body.fg-andalusian-v3 [class*="main-content"] {
  min-height: 0 !important;
  max-height: calc(100vh - 64px) !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
  padding-bottom: 28px !important;
}

body.fg-andalusian-v3 .fg-v3-header,
body.fg-andalusian-v3 header,
body.fg-andalusian-v3 .topbar,
body.fg-andalusian-v3 .top-bar,
body.fg-andalusian-v3 .app-header {
  flex: 0 0 auto !important;
  min-height: 48px !important;
  max-height: 64px !important;
}

/* Compact density for the most common 15.6-inch 1366x768 laptop viewport. */
@media (min-width: 1100px) and (max-width: 1450px) and (max-height: 820px) {
  body.fg-andalusian-v3 {
    font-size: 13px !important;
  }

  body.fg-andalusian-v3 .fg-v3-header,
  body.fg-andalusian-v3 header,
  body.fg-andalusian-v3 .topbar,
  body.fg-andalusian-v3 .top-bar,
  body.fg-andalusian-v3 .app-header {
    min-height: 44px !important;
    max-height: 54px !important;
    padding-top: 4px !important;
    padding-bottom: 4px !important;
  }

  body.fg-andalusian-v3 main,
  body.fg-andalusian-v3 .main-content,
  body.fg-andalusian-v3 .content,
  body.fg-andalusian-v3 .workspace-content,
  body.fg-andalusian-v3 .page-content,
  body.fg-andalusian-v3 [class*="main-content"] {
    max-height: calc(100vh - 54px) !important;
    padding-top: 8px !important;
    padding-bottom: 22px !important;
  }

  body.fg-andalusian-v3 .fg-v3-grid,
  body.fg-andalusian-v3 [class*="grid"] {
    gap: 10px !important;
    row-gap: 10px !important;
  }

  body.fg-andalusian-v3 .fg-ornate-frame,
  body.fg-andalusian-v3 .card,
  body.fg-andalusian-v3 .panel,
  body.fg-andalusian-v3 [class*="card"] {
    padding-top: 10px !important;
    padding-bottom: 10px !important;
  }

  body.fg-andalusian-v3 .fg-corner {
    width: 30px !important;
    height: 30px !important;
  }
  body.fg-andalusian-v3 .fg-corner::after {
    width: 10px !important;
    height: 10px !important;
    left: 7px !important;
    top: 7px !important;
  }
  body.fg-andalusian-v3 .fg-crest {
    width: 52px !important;
    height: 18px !important;
  }
  body.fg-andalusian-v3 .fg-crest.top { top: -9px !important; }
  body.fg-andalusian-v3 .fg-crest.bottom { bottom: -9px !important; }

  body.fg-andalusian-v3 .fg-v3-hero {
    margin-top: 12px !important;
    margin-bottom: 8px !important;
    min-height: 0 !important;
  }
  body.fg-andalusian-v3 .fg-v3-hero::after {
    width: 120px !important;
    height: 40px !important;
    top: -18px !important;
  }

  body.fg-andalusian-v3 h1 { font-size: clamp(1.2rem, 1.8vw, 1.55rem) !important; margin-block: 4px 8px !important; }
  body.fg-andalusian-v3 h2 { font-size: clamp(1.05rem, 1.45vw, 1.3rem) !important; margin-block: 4px 6px !important; }
  body.fg-andalusian-v3 h3 { font-size: clamp(.95rem, 1.2vw, 1.15rem) !important; margin-block: 3px 5px !important; }

  body.fg-andalusian-v3 button,
  body.fg-andalusian-v3 .btn,
  body.fg-andalusian-v3 input,
  body.fg-andalusian-v3 select {
    min-height: 32px !important;
  }
}

/* Even shorter screens: preserve functionality over decoration. */
@media (min-width: 1000px) and (max-height: 720px) {
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
    max-height: calc(100vh - 48px) !important;
  }
  body.fg-andalusian-v3 .fg-header-crest,
  body.fg-andalusian-v3 .fg-v3-hero::after {
    transform: translateX(-50%) scale(.78) !important;
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

# Preserve routes and content; this layer is CSS-only by design.
html_count = len(list(ui.rglob('*.html')))
if html_count < 100:
    raise SystemExit(f'LAPTOP_FIT_HTML_COUNT_UNEXPECTED {html_count}')
if 'max-height: calc(100vh - 54px)' not in text or 'overflow-y: auto' not in text:
    raise SystemExit('LAPTOP_FIT_VERIFY_FAILED')
print(f'LAPTOP_156_FIT_APPLIED version=R1 html={html_count} target=1366x768 scrollable_results=true routes_untouched=true')
