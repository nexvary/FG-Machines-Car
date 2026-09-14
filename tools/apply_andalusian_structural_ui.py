from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
css = ui / 'app.css'
if not ui.exists() or not css.exists():
    raise SystemExit(f'ANDALUSIAN_V3_MISSING {ui}')

MARKER = '/* FG-ANDALUSIAN-STRUCTURAL-V3 */'

CSS = r'''
/* FG-ANDALUSIAN-STRUCTURAL-V3 */
:root{
  --fg-v3-gold:#d4af37;
  --fg-v3-gold-hi:#ffe59a;
  --fg-v3-gold-deep:#8b5d08;
  --fg-v3-plum:#260321;
  --fg-v3-magenta:#7a0f5d;
  --fg-v3-pink:#c93689;
  --fg-v3-ivory:#fff8eb;
}

body.fg-andalusian-v3{
  background:
    radial-gradient(circle at 50% -8%,rgba(255,95,188,.22),transparent 28%),
    radial-gradient(circle at 8% 18%,rgba(229,54,155,.13),transparent 22%),
    radial-gradient(circle at 92% 18%,rgba(229,54,155,.13),transparent 22%),
    repeating-conic-gradient(from 45deg at 24px 24px,rgba(255,229,154,.025) 0 12deg,transparent 12deg 33deg),
    linear-gradient(135deg,#22021e 0%,#4b073e 34%,#7a0f5d 66%,#2b0327 100%)!important;
}

/* Full ornamental frame applied to real runtime cards */
body.fg-andalusian-v3 .fg-ornate-frame{
  position:relative!important;
  isolation:isolate;
  overflow:visible!important;
  border:2px solid var(--fg-v3-gold)!important;
  outline:1px solid rgba(255,229,154,.48)!important;
  outline-offset:-5px!important;
  box-shadow:
    0 0 0 1px rgba(113,69,4,.78),
    0 10px 24px rgba(29,0,25,.25),
    inset 0 0 0 1px rgba(255,239,184,.42),
    inset 0 0 22px rgba(212,175,55,.08)!important;
}
body.fg-andalusian-v3 .fg-ornate-frame::before{
  content:"";
  position:absolute;
  inset:7px;
  z-index:8;
  pointer-events:none;
  border:1px solid rgba(139,93,8,.65);
  border-radius:inherit;
  box-shadow:inset 0 0 0 1px rgba(255,229,154,.18);
}

body.fg-andalusian-v3 .fg-corner{
  position:absolute;
  width:48px;
  height:48px;
  z-index:12;
  pointer-events:none;
  filter:drop-shadow(0 1px 1px rgba(72,41,0,.25));
}
body.fg-andalusian-v3 .fg-corner::before,
body.fg-andalusian-v3 .fg-corner::after{
  content:"";
  position:absolute;
  inset:0;
}
body.fg-andalusian-v3 .fg-corner::before{
  background:
    radial-gradient(circle at 17px 17px,var(--fg-v3-gold-hi) 0 2px,var(--fg-v3-gold) 2.5px 4px,transparent 4.5px),
    conic-gradient(from 45deg at 18px 18px,transparent 0 11%,var(--fg-v3-gold) 11% 16%,transparent 16% 34%,var(--fg-v3-gold-hi) 34% 39%,transparent 39% 61%,var(--fg-v3-gold) 61% 66%,transparent 66%);
  clip-path:polygon(0 0,100% 0,100% 23%,53% 23%,53% 35%,36% 35%,36% 53%,23% 53%,23% 100%,0 100%);
}
body.fg-andalusian-v3 .fg-corner::after{
  width:15px;height:15px;
  left:10px;top:10px;
  border:2px solid var(--fg-v3-gold-hi);
  transform:rotate(45deg);
  background:linear-gradient(135deg,#6e0d57,#b72c7d);
  box-shadow:0 0 0 2px var(--fg-v3-gold),0 0 8px rgba(255,229,154,.46);
}
body.fg-andalusian-v3 .fg-corner.tl{top:-2px;left:-2px;}
body.fg-andalusian-v3 .fg-corner.tr{top:-2px;right:-2px;transform:scaleX(-1);}
body.fg-andalusian-v3 .fg-corner.bl{bottom:-2px;left:-2px;transform:scaleY(-1);}
body.fg-andalusian-v3 .fg-corner.br{bottom:-2px;right:-2px;transform:scale(-1);}

body.fg-andalusian-v3 .fg-crest{
  position:absolute;
  left:50%;
  width:74px;
  height:24px;
  transform:translateX(-50%);
  z-index:13;
  pointer-events:none;
}
body.fg-andalusian-v3 .fg-crest.top{top:-12px;}
body.fg-andalusian-v3 .fg-crest.bottom{bottom:-12px;transform:translateX(-50%) rotate(180deg);}
body.fg-andalusian-v3 .fg-crest::before{
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(180deg,var(--fg-v3-gold-hi),var(--fg-v3-gold) 48%,var(--fg-v3-gold-deep));
  clip-path:polygon(0 55%,16% 55%,25% 25%,36% 52%,50% 0,64% 52%,75% 25%,84% 55%,100% 55%,100% 67%,70% 67%,61% 100%,50% 70%,39% 100%,30% 67%,0 67%);
  filter:drop-shadow(0 2px 2px rgba(73,42,0,.3));
}
body.fg-andalusian-v3 .fg-crest::after{
  content:"";
  position:absolute;
  width:9px;height:9px;
  left:calc(50% - 4.5px);top:8px;
  background:#8f1468;
  border:1px solid #fff0b4;
  transform:rotate(45deg);
}

/* Stronger Andalusian treatment for side navigation */
body.fg-andalusian-v3 .fg-v3-sidebar{
  position:relative!important;
  border-inline-end:3px double var(--fg-v3-gold)!important;
  box-shadow:8px 0 28px rgba(24,0,22,.34),inset -6px 0 18px rgba(212,175,55,.06)!important;
  background:
    radial-gradient(circle at 50% 0,rgba(212,175,55,.13),transparent 22%),
    repeating-linear-gradient(135deg,rgba(255,229,154,.02) 0 8px,transparent 8px 16px),
    linear-gradient(180deg,#260321,#4a073d 48%,#22021e)!important;
}
body.fg-andalusian-v3 .fg-v3-sidebar::before,
body.fg-andalusian-v3 .fg-v3-sidebar::after{
  content:"";
  position:absolute;
  left:10px;right:10px;
  height:34px;
  z-index:20;
  pointer-events:none;
  background:linear-gradient(90deg,transparent,var(--fg-v3-gold) 18%,var(--fg-v3-gold-hi) 50%,var(--fg-v3-gold) 82%,transparent);
  clip-path:polygon(0 48%,16% 48%,23% 16%,34% 48%,44% 48%,50% 0,56% 48%,66% 48%,77% 16%,84% 48%,100% 48%,100% 58%,0 58%);
  opacity:.95;
}
body.fg-andalusian-v3 .fg-v3-sidebar::before{top:6px;}
body.fg-andalusian-v3 .fg-v3-sidebar::after{bottom:6px;transform:rotate(180deg);}

/* Header: thick royal frame and central Moorish crest */
body.fg-andalusian-v3 .fg-v3-header{
  position:relative!important;
  border-top:1px solid var(--fg-v3-gold-hi)!important;
  border-bottom:3px double var(--fg-v3-gold)!important;
  box-shadow:0 8px 22px rgba(36,0,31,.28),inset 0 -6px 16px rgba(212,175,55,.05)!important;
  background:linear-gradient(90deg,#24021f 0%,#760f5d 50%,#260321 100%)!important;
}
body.fg-andalusian-v3 .fg-header-crest{
  position:absolute;
  z-index:30;
  left:50%;bottom:-16px;
  width:112px;height:32px;
  transform:translateX(-50%);
  pointer-events:none;
  background:linear-gradient(180deg,var(--fg-v3-gold-hi),var(--fg-v3-gold) 52%,var(--fg-v3-gold-deep));
  clip-path:polygon(0 42%,18% 42%,25% 20%,34% 42%,41% 42%,50% 0,59% 42%,66% 42%,75% 20%,82% 42%,100% 42%,100% 58%,64% 58%,58% 100%,50% 69%,42% 100%,36% 58%,0 58%);
  filter:drop-shadow(0 3px 3px rgba(60,34,0,.32));
}

/* Hero arch treatment */
body.fg-andalusian-v3 .fg-v3-hero{
  position:relative!important;
  border:3px double var(--fg-v3-gold)!important;
  border-radius:30px 30px 12px 12px!important;
  overflow:visible!important;
}
body.fg-andalusian-v3 .fg-v3-hero::after{
  content:"";
  position:absolute;
  left:50%;top:-26px;
  width:180px;height:62px;
  transform:translateX(-50%);
  z-index:11;
  pointer-events:none;
  border:3px solid var(--fg-v3-gold);
  border-bottom:0;
  border-radius:90px 90px 0 0;
  background:linear-gradient(180deg,#5d0b4c,#7f1262 70%,transparent 71%);
  clip-path:polygon(0 100%,0 58%,12% 58%,20% 35%,31% 58%,40% 58%,50% 0,60% 58%,69% 58%,80% 35%,88% 58%,100% 58%,100% 100%);
  box-shadow:0 -2px 0 var(--fg-v3-gold-hi);
}

/* Nav entries gain gold rails */
body.fg-andalusian-v3 .fg-v3-sidebar a,
body.fg-andalusian-v3 .fg-v3-sidebar .nav-item,
body.fg-andalusian-v3 .fg-v3-sidebar .side-link{
  position:relative;
  border-inline-start:2px solid rgba(212,175,55,.42)!important;
  border-radius:4px 14px 14px 4px!important;
}
body.fg-andalusian-v3 .fg-v3-sidebar a.active,
body.fg-andalusian-v3 .fg-v3-sidebar .nav-item.active,
body.fg-andalusian-v3 .fg-v3-sidebar [aria-current="page"]{
  box-shadow:inset 4px 0 0 var(--fg-v3-gold-hi),0 0 16px rgba(231,57,157,.25)!important;
}

/* Decorative horizontal rails around grids */
body.fg-andalusian-v3 .fg-v3-grid{
  position:relative;
  padding-top:10px!important;
  padding-bottom:10px!important;
}
body.fg-andalusian-v3 .fg-v3-grid::before,
body.fg-andalusian-v3 .fg-v3-grid::after{
  content:"";
  position:absolute;
  left:0;right:0;
  height:2px;
  background:linear-gradient(90deg,transparent,var(--fg-v3-gold) 12%,var(--fg-v3-gold-hi) 50%,var(--fg-v3-gold) 88%,transparent);
  opacity:.85;
}
body.fg-andalusian-v3 .fg-v3-grid::before{top:0;}
body.fg-andalusian-v3 .fg-v3-grid::after{bottom:0;}

@media (max-width:900px){
  body.fg-andalusian-v3 .fg-corner{width:36px;height:36px;}
  body.fg-andalusian-v3 .fg-crest{width:58px;}
  body.fg-andalusian-v3 .fg-v3-hero::after{width:120px;height:45px;top:-20px;}
}
'''

JS = r'''
<script id="fg-andalusian-v3-runtime">
(()=>{
  const decorate=()=>{
    const B=document.body;
    B.classList.add('fg-andalusian-v3');

    const first=(sels)=>sels.map(s=>document.querySelector(s)).find(Boolean);
    const sidebar=first(['aside','.sidebar','.side-nav','.navigation-panel','.app-sidebar','[class*="sidebar"]']);
    if(sidebar) sidebar.classList.add('fg-v3-sidebar');
    const header=first(['.topbar','.top-bar','.app-header','.main-header','.masthead','header.app-topbar','body>header','header']);
    if(header && !header.querySelector('.fg-header-crest')){
      header.classList.add('fg-v3-header');
      header.insertAdjacentHTML('beforeend','<span class="fg-header-crest" aria-hidden="true"></span>');
    }

    const main=first(['main','.main-content','.content','.workspace-content']);
    if(!main) return;

    const selector=[
      '.card','.panel','.module-card','.detail-card','.action-panel','.dashboard-card','.section-card','.content-card','.metric-card','.tile',
      '.sv-banner','.sv-doc','.sv-chat','.sv-quiz','.sv-remote','.sv-gate','.sv-split>div','.sv-cards>div','.sv-rows>div',
      '[class*="card"]','article','main section','[role="group"]'
    ].join(',');

    const seen=new Set();
    const candidates=[...main.querySelectorAll(selector)];
    for(const el of candidates){
      if(seen.has(el) || el.closest('nav')) continue;
      const r=el.getBoundingClientRect();
      if(r.width<180 || r.height<70) continue;
      seen.add(el);
      el.classList.add('fg-ornate-frame');
      if(!el.querySelector(':scope > .fg-corner')){
        el.insertAdjacentHTML('beforeend',
          '<span class="fg-corner tl" aria-hidden="true"></span><span class="fg-corner tr" aria-hidden="true"></span><span class="fg-corner bl" aria-hidden="true"></span><span class="fg-corner br" aria-hidden="true"></span><span class="fg-crest top" aria-hidden="true"></span><span class="fg-crest bottom" aria-hidden="true"></span>');
      }
    }

    for(const grid of main.querySelectorAll('[class*="grid"],.sv-cards,.sv-rows')){
      const r=grid.getBoundingClientRect();
      if(r.width>400 && r.height>100) grid.classList.add('fg-v3-grid');
    }

    const heroCandidates=[...main.querySelectorAll('.hero,.hero-card,.welcome,.overview-banner,.dashboard-hero,.sv-banner,section')]
      .filter(el=>{const r=el.getBoundingClientRect();return r.width>500&&r.height>110;});
    if(heroCandidates[0]) heroCandidates[0].classList.add('fg-v3-hero');
  };
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>requestAnimationFrame(decorate));
  else requestAnimationFrame(decorate);
  setTimeout(decorate,700);
})();
</script>
'''

text = css.read_text(encoding='utf-8')
if MARKER not in text:
    css.write_text(text.rstrip() + '\n\n' + CSS + '\n', encoding='utf-8')

changed=0
html_files=list(ui.rglob('*.html'))
for p in html_files:
    s=p.read_text(encoding='utf-8')
    original=s
    if 'fg-andalusian-v3-runtime' not in s:
        if '</body>' in s:
            s=s.replace('</body>',JS+'\n</body>',1)
        else:
            s+=JS
    if '<body' in s and 'fg-andalusian-v3' not in s.split('>',1)[0]:
        s=re.sub(r'<body([^>]*)>',lambda m:'<body'+m.group(1)+' class="'+(('fg-andalusian-v3 '+re.search(r'class="([^"]*)"',m.group(0)).group(1)) if 'class="' in m.group(0) else 'fg-andalusian-v3')+'">',s,count=1)
    if s!=original:
        p.write_text(s,encoding='utf-8')
        changed+=1

print(f'ANDALUSIAN_STRUCTURAL_V3_APPLIED html={len(html_files)} changed={changed} runtime_frames=true structural=true')
