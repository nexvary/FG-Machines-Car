from pathlib import Path
import re, sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
if not ui.exists():
    raise SystemExit(f'LOCALE_BOOT_UI_MISSING {ui}')

MARK = 'NEXVARY_LOCALE_BOOT_GUARD_V1'
STYLE = r'''<style id="nexvary-locale-boot-style">/* NEXVARY_LOCALE_BOOT_GUARD_V1 */
html.nx-locale-boot{background:#07111b!important;min-height:100%}
html.nx-locale-boot body{visibility:hidden!important}
html.nx-locale-boot::after{content:'NEXVARY';position:fixed;inset:0;z-index:2147483647;display:grid;place-items:center;background:radial-gradient(circle at 50% 42%,#102a3a 0,#07111b 48%,#040a11 100%);color:#d9d7d4;font:700 18px/1.2 system-ui,-apple-system,'Segoe UI',sans-serif;letter-spacing:.22em;text-shadow:0 0 18px rgba(106,136,160,.55)}
html[dir="rtl"].nx-locale-boot::after{letter-spacing:.16em}
</style>'''

SCRIPT = r'''<script id="nexvary-locale-boot-script">/* NEXVARY_LOCALE_BOOT_GUARD_V1 */
(()=>{'use strict';
const html=document.documentElement;
const supported=new Set(['ar','en','tr','es','de','it','fr','ur','fa','ru']);
const norm=v=>{if(v==null)return'';let s=String(v).trim();try{const j=JSON.parse(s);if(typeof j==='string')s=j;else if(j&&typeof j==='object')s=String(j.language||j.lang||j.locale||j.uiLanguage||s)}catch{}s=s.toLowerCase().replace('_','-');return s.split('-')[0]};
function fromStore(store){try{const preferred=[];for(let i=0;i<store.length;i++){const k=store.key(i)||'',v=store.getItem(k);if(/lang|locale|i18n|language/i.test(k))preferred.push(v)}for(const v of preferred){const n=norm(v);if(supported.has(n))return n}for(let i=0;i<store.length;i++){const n=norm(store.getItem(store.key(i)));if(supported.has(n))return n}}catch{}return''}
const target=fromStore(localStorage)||fromStore(sessionStorage)||norm(navigator.language);
const initial=norm(html.getAttribute('lang'))||'ar';
if(!target||target===initial){window.__NEXVARY_LOCALE_BOOT__={target:target||initial,initial,guarded:false};return}
html.classList.add('nx-locale-boot');
window.__NEXVARY_LOCALE_BOOT__={target,initial,guarded:true,released:false};
let released=false,quietTimer=0,hardTimer=0,observer=null;
const release=reason=>{if(released)return;released=true;clearTimeout(quietTimer);clearTimeout(hardTimer);observer?.disconnect();html.classList.remove('nx-locale-boot');window.__NEXVARY_LOCALE_BOOT__.released=true;window.__NEXVARY_LOCALE_BOOT__.reason=reason};
const schedule=()=>{clearTimeout(quietTimer);quietTimer=setTimeout(()=>{const lang=norm(html.getAttribute('lang'));if(lang===target)release('locale-stable')},180)};
document.addEventListener('DOMContentLoaded',()=>{observer=new MutationObserver(schedule);observer.observe(html,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['lang','dir','class','data-lang','data-language','data-locale']});schedule();hardTimer=setTimeout(()=>release('fallback-timeout'),1600)},{once:true});
})();
</script>'''

injected = 0
already = 0
missing_head = []
for p in sorted(ui.rglob('*.html')):
    text = p.read_text('utf-8', errors='ignore')
    if MARK in text:
        already += 1
        continue
    m = re.search(r'<head\b[^>]*>', text, re.I)
    if not m:
        missing_head.append(str(p.relative_to(root)))
        continue
    text = text[:m.end()] + '\n' + STYLE + '\n' + SCRIPT + text[m.end():]
    p.write_text(text, 'utf-8')
    injected += 1

if missing_head:
    raise SystemExit('NEXVARY_LOCALE_BOOT_HEAD_MISSING ' + ' | '.join(missing_head[:20]))

html_files = list(ui.rglob('*.html'))
if not html_files:
    raise SystemExit('NEXVARY_LOCALE_BOOT_NO_HTML')
for p in html_files:
    t = p.read_text('utf-8', errors='ignore')
    if t.count(MARK) != 2:
        raise SystemExit(f'NEXVARY_LOCALE_BOOT_AUDIT_FAIL {p}: markerCount={t.count(MARK)}')

# Add a static regression assertion to the Playwright suite. Behavioral locale translation
# remains owned by the application; this gate guarantees every physical page receives the
# pre-paint guard that prevents Arabic/English mixed-frame flashes during navigation.
qa = root / 'qa' / 'visual' / 'ui.spec.cjs'
if qa.exists():
    q = qa.read_text('utf-8')
    test_mark = 'locale boot guard is present before body paint'
    if test_mark not in q:
        q += "\n\ntest('locale boot guard is present before body paint', async ({ request }) => {\n  const r=await request.get('/modules/m010.html');expect(r.ok()).toBeTruthy();const h=await r.text();expect(h).toContain('NEXVARY_LOCALE_BOOT_GUARD_V1');expect(h.indexOf('NEXVARY_LOCALE_BOOT_GUARD_V1')).toBeLessThan(h.toLowerCase().indexOf('</head>'));\n});\n"
        qa.write_text(q, 'utf-8')

print(f'NEXVARY_LOCALE_BOOT_PASS html={len(html_files)} injected={injected} already={already} prePaint=true mixedLanguageFlashGuard=true fallbackMs=1600')
