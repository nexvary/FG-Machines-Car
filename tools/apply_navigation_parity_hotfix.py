from pathlib import Path
import re, sys

root=Path(sys.argv[1]).resolve()
ui=root/'native/ui-modern'
common=ui/'common.js'
module=ui/'module.js'
css=ui/'app.css'
for p in (common,module,css):
    if not p.exists(): raise SystemExit(f'NAV_PARITY_MISSING {p}')

NAV_MARK='NEXVARY_NAV_PARITY_V1'
MODULE_MARK='NEXVARY_MODULE_PARITY_V1'
CSS_MARK='NEXVARY_NAV_PARITY_CSS_V1'

nav_js=r'''
;/* NEXVARY_NAV_PARITY_V1 */
(()=>{'use strict';
const AR={dashboard:'الرئيسية',diagnostics:'التشخيص',cars:'السيارات',motorcycles:'الدراجات',yamaha:'Yamaha FJR',lancer:'Mitsubishi Lancer',keys:'المفاتيح والريموت',obdvci:'VCI و OBD',maintenance:'الصيانة',road:'الطريق والسلامة',garage:'المرآب',network:'Nexvary Connect',reports:'التقارير',settings:'الإعدادات',about:'عن النظام'};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sectionOf=m=>String(m.section||String(m.route||'').split('::')[0]||'other').toLowerCase();
const labelOf=m=>String(m.title||m.name||String(m.route||'').split('::')[1]||m.route||m.path||'وحدة');
function findNavHost(){
  const side=document.querySelector('aside,[class*="sidebar" i],[class*="side-bar" i]');
  if(!side)return null;
  const candidates=[...side.querySelectorAll('nav,[class*="menu" i],[class*="nav" i],[class*="links" i]')]
    .map(el=>({el,n:el.querySelectorAll('a[href]').length}))
    .filter(x=>x.n>=4).sort((a,b)=>b.n-a.n);
  return candidates[0]?.el||side;
}
async function verify(mods){
  const routes=new Set(),paths=new Set(),dups=[];
  for(const m of mods){const r=String(m.route||''),p=String(m.path||'');if(!r||!p){dups.push('missing route/path');continue}if(routes.has(r))dups.push('route '+r);if(paths.has(p))dups.push('path '+p);routes.add(r);paths.add(p)}
  if(dups.length){console.error('NEXVARY_NAV_DUPLICATE',dups.join(' | '));return {ok:false,bad:dups.length}}
  if(sessionStorage.getItem('nexvary-nav-audit')==='pass')return {ok:true,bad:0};
  const bad=[];let i=0;
  const workers=Array.from({length:8},async()=>{while(i<mods.length){const m=mods[i++];try{const r=await fetch(m.path,{cache:'no-store'});if(!r.ok)bad.push(`${m.path}:${r.status}`)}catch(e){bad.push(`${m.path}:ERR`)}}});
  await Promise.all(workers);
  if(bad.length){console.error('NEXVARY_NAV_BROKEN',bad.slice(0,20).join(' | '));return {ok:false,bad:bad.length}}
  sessionStorage.setItem('nexvary-nav-audit','pass');return {ok:true,bad:0};
}
async function install(){
  if(!window.fgManifest)return;
  const manifest=await window.fgManifest();
  const mods=(manifest.modules||[]).filter(m=>m&&m.route&&m.path);
  if(!mods.length)return;
  const current=String(document.body.dataset.route||''); const currentSection=String(document.body.dataset.section||current.split('::')[0]||'').toLowerCase();
  const groups=new Map();for(const m of mods){const s=sectionOf(m);if(!groups.has(s))groups.set(s,[]);groups.get(s).push(m)}
  const host=findNavHost();if(!host)return;
  let panel=document.getElementById('nexvary-parity-nav');if(panel)panel.remove();
  panel=document.createElement('div');panel.id='nexvary-parity-nav';panel.className='nexvary-parity-nav';
  const order=['dashboard','diagnostics','cars','motorcycles','yamaha','lancer','keys','obdvci','maintenance','road','garage','network','reports','settings','about'];
  const keys=[...groups.keys()].sort((a,b)=>{const ia=order.indexOf(a),ib=order.indexOf(b);return (ia<0?999:ia)-(ib<0?999:ib)||a.localeCompare(b)});
  panel.innerHTML=`<div class="np-head"><b>القائمة الكاملة</b><span id="np-audit">${mods.length} رابط</span></div><label class="np-search"><input id="np-search-input" type="search" placeholder="ابحث في جميع الأدوات والوحدات…" autocomplete="off"></label><div class="np-groups">${keys.map(s=>{const items=groups.get(s).slice().sort((a,b)=>labelOf(a).localeCompare(labelOf(b),'ar'));return `<details class="np-group" data-section="${esc(s)}" ${s===currentSection?'open':''}><summary><span>${esc(AR[s]||s)}</span><em>${items.length}</em></summary><div class="np-links">${items.map(m=>`<a data-route="${esc(m.route)}" href="${esc(m.path)}" class="${m.route===current?'active':''}"><span>${esc(labelOf(m))}</span><small>${esc(m.route)}</small></a>`).join('')}</div></details>`}).join('')}</div>`;
  if(host!==document.querySelector('aside') && host.querySelectorAll('a[href]').length>=4){host.replaceChildren(panel)}else{host.appendChild(panel)}
  const input=panel.querySelector('#np-search-input');input?.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();panel.querySelectorAll('.np-group').forEach(g=>{let visible=0;g.querySelectorAll('.np-links a').forEach(a=>{const on=!q||a.textContent.toLowerCase().includes(q);a.hidden=!on;if(on)visible++});g.hidden=visible===0;if(q&&visible)g.open=true})});
  const audit=await verify(mods);const badge=panel.querySelector('#np-audit');if(badge){badge.textContent=audit.ok?`${mods.length}/${mods.length} روابط سليمة`:`${audit.bad} روابط بها مشكلة`;badge.classList.toggle('bad',!audit.ok)}
  window.__NEXVARY_NAV_PARITY__={modules:mods.length,groups:groups.size,audit,current};
}
const boot=()=>install().catch(e=>console.error('NEXVARY_NAV_PARITY_FAIL',e));
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
'''

module_js=r'''
;/* NEXVARY_MODULE_PARITY_V1 */
(()=>{'use strict';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const route=String(document.body.dataset.route||''),section=String(document.body.dataset.section||route.split('::')[0]||''),t=route.toLowerCase();
function kind(){if(/efi|injection|fuel|ignition/.test(t))return'efi';if(/charg|battery|alternator|stator|electrical/.test(t))return'electrical';if(/handling|chassis|suspension|steering|alignment/.test(t))return'handling';if(/safety|brake|abs|airbag/.test(t))return'safety';if(/acoustic|noise|vibration|sound/.test(t))return'acoustic';if(/performance|power|acceleration|throttle/.test(t))return'performance';if(/dtc|fault|freeze/.test(t))return'fault';if(/live|pid|measurement|monitor/.test(t))return'live';if(/vci|obd|protocol|adapter|can|isotp|uds/.test(t))return'protocol';if(/key|remote|transponder|immobilizer/.test(t))return'keys';if(/report|evidence|export|history|timeline/.test(t))return'report';if(/network|chat|contact|privacy/.test(t)||section==='network')return'network';if(/maintenance|service|due/.test(t))return'maintenance';if(/vehicle|profile|select car|motorcycle/.test(t))return'profile';return'workspace'}
const K=kind();
const P={
 efi:['منظومة الوقود','الإشعال','الحساسات','الخمول والتحميل'],electrical:['البطارية','منظومة الشحن','دوائر القدرة','التسريب الكهربائي'],handling:['الإطارات والضغط','التوجيه','التعليق','الثبات والمحاذاة'],safety:['الفرامل','ABS / أنظمة الأمان','الإضاءة والتحذيرات','فحص السلامة'],acoustic:['تحديد مصدر الصوت','ربط الصوت مع RPM','الاهتزاز','مقارنة ظروف التشغيل'],performance:['استجابة الخانق','RPM والحمل','درجات الحرارة','قراءات الأداء'],fault:['رمز العطل','Freeze Frame','السياق المرتبط','خطة التحقق'],live:['القنوات المختارة','القراءة الحية','الحدود المرجعية','تسجيل الجلسة'],protocol:['حالة VCI','البروتوكول','جلسة الاتصال','سلامة القراءة فقط'],keys:['هوية المفتاح','حالة الريموت','الترانسبوندر','تفويض الملكية'],report:['مصدر الأدلة','سلامة السجل','المعاينة','التصدير'],network:['الحالة المحلية','الخصوصية','الجلسات','سجل الاتصال'],maintenance:['البند','موعد الاستحقاق','السجل السابق','ملاحظة الورشة'],profile:['بيانات المركبة','VIN / الهوية','المحرك والمنصة','السجل التشخيصي'],workspace:['نطاق الوحدة','مدخلات القراءة','مسار التحقق','الأدلة المرتبطة']};
const descriptions={efi:'تشخيص منظومة إدارة المحرك دون اختلاق قراءات عند عدم اتصال VCI.',electrical:'مساحة فحص كهربائي منظمة؛ القيم الفعلية تظهر فقط عند توفر مصدر قراءة موثوق.',handling:'عرض مستقل لمكونات الثبات والتوجيه والتعليق بدل القالب العام المتكرر.',safety:'قائمة سلامة مخصصة للوحدة مع فصل واضح بين الفحص والعمليات المقفلة.',acoustic:'تحليل الضوضاء والاهتزاز في مسار مستقل مرتبط بظروف التشغيل.',performance:'لوحة أداء مستقلة تعرض القنوات المتاحة فقط عند اتصال مصدر بيانات.',fault:'مسار أعطال مستقل يربط DTC بالسياق والأدلة.',live:'لوحة قراءات حية مستقلة مع حالة اتصال واضحة.',protocol:'صفحة اتصال وبروتوكول مستقلة مع إبقاء الوضع READ ONLY.',keys:'صفحة مفاتيح وريموت مستقلة مرتبطة بالتفويض والجرد.',report:'صفحة أدلة وتقارير مستقلة قابلة للمراجعة.',network:'صفحة اتصال محلي وخصوصية مستقلة.',maintenance:'صفحة صيانة مستقلة للسجل والاستحقاقات.',profile:'صفحة ملف مركبة مستقلة.',workspace:'مساحة عمل مستقلة مرتبطة بالمسار الحالي.'};
function render(){
  const root=document.querySelector('#moduleData');if(!root||root.querySelector('.np-module-context'))return false;
  const title=(route.split('::')[1]||route||'الوحدة');
  const labels=P[K]||P.workspace;
  const block=document.createElement('section');block.className=`np-module-context np-kind-${K}`;block.dataset.routeFingerprint=route;
  block.innerHTML=`<header><div><small>مسار مستقل · ${esc(section)}</small><h3>${esc(title)}</h3><p>${esc(descriptions[K]||descriptions.workspace)}</p></div><span class="np-route-badge">${esc(K)}</span></header><div class="np-context-grid">${labels.map((x,i)=>`<article><i>${i+1}</i><b>${esc(x)}</b><span>${/live|efi|electrical|performance|protocol/.test(K)?'بانتظار بيانات VCI الفعلية':'جاهز للمراجعة'}</span></article>`).join('')}</div><footer><code>${esc(route)}</code><span>لا يتم عرض قيم افتراضية على أنها قراءات حقيقية.</span></footer>`;
  root.prepend(block);document.body.dataset.parityView=K;window.__NEXVARY_MODULE_PARITY__={route,section,view:K};return true;
}
let tries=0;const timer=setInterval(()=>{if(render()||++tries>50)clearInterval(timer)},60);
})();
'''

css_add=r'''
/* NEXVARY_NAV_PARITY_CSS_V1 */
.nexvary-parity-nav{height:100%;min-height:0;display:flex;flex-direction:column;gap:10px;padding:10px 8px 18px;overflow:hidden;color:#d9e5ef;direction:rtl}.np-head{display:flex;align-items:center;justify-content:space-between;padding:6px 8px}.np-head b{font-size:13px}.np-head span{font-size:10px;color:#74d9ff;border:1px solid rgba(106,136,160,.45);padding:4px 7px;border-radius:999px}.np-head span.bad{color:#ffb0a8;border-color:#b84b45}.np-search{display:block;padding:0 4px}.np-search input{width:100%;box-sizing:border-box;background:#081827;border:1px solid #2e3945;color:#d9d7d4;border-radius:10px;padding:10px 11px;text-align:right;outline:none}.np-search input:focus{border-color:#6a88a0;box-shadow:0 0 0 2px rgba(106,136,160,.12)}.np-groups{overflow:auto;min-height:0;padding:0 3px 12px;scrollbar-width:thin}.np-group{border-bottom:1px solid rgba(158,155,152,.13)}.np-group summary{cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 7px;font-weight:700}.np-group summary::-webkit-details-marker{display:none}.np-group summary em{font-style:normal;font-size:10px;min-width:24px;text-align:center;border:1px solid rgba(106,136,160,.35);border-radius:999px;color:#9ecfe4}.np-links{display:grid;gap:4px;padding:0 3px 9px}.np-links a{display:block;text-decoration:none;color:#bfcbd4;border:1px solid transparent;border-radius:9px;padding:8px 9px;white-space:normal;overflow-wrap:anywhere;line-height:1.25;background:rgba(12,19,25,.28)}.np-links a span{display:block;font-size:12px}.np-links a small{display:block;margin-top:3px;font-size:8px;opacity:.55;direction:ltr;text-align:left}.np-links a:hover,.np-links a.active{color:#fff;border-color:#6a88a0;background:rgba(46,57,69,.62);box-shadow:inset 2px 0 0 #6a88a0}.np-links a[hidden],.np-group[hidden]{display:none!important}.np-module-context{margin:0 0 16px;border:1px solid rgba(158,155,152,.32);border-radius:16px;padding:16px;background:linear-gradient(135deg,rgba(12,19,25,.92),rgba(20,42,62,.48));box-shadow:0 10px 34px rgba(0,0,0,.16)}.np-module-context header{display:flex;justify-content:space-between;align-items:flex-start;gap:18px}.np-module-context header small{color:#6a88a0;letter-spacing:.08em}.np-module-context h3{margin:5px 0 7px;font-size:20px;color:#d9d7d4}.np-module-context p{margin:0;color:#aebac4;max-width:820px}.np-route-badge{border:1px solid rgba(106,136,160,.5);border-radius:999px;padding:6px 9px;color:#b9d7e4;font-size:10px;direction:ltr}.np-context-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-top:14px}.np-context-grid article{min-height:74px;border:1px solid rgba(158,155,152,.22);border-radius:12px;padding:11px;background:rgba(7,21,37,.58);display:grid;grid-template-columns:auto 1fr;gap:5px 9px;align-items:center}.np-context-grid article i{grid-row:1/3;width:24px;height:24px;display:grid;place-items:center;border-radius:50%;font-style:normal;background:#102c42;color:#75cdf2}.np-context-grid article b{font-size:12px}.np-context-grid article span{font-size:9px;color:#8193a2}.np-module-context footer{margin-top:12px;padding-top:10px;border-top:1px solid rgba(158,155,152,.15);display:flex;justify-content:space-between;gap:12px;font-size:9px;color:#8193a2}.np-module-context footer code{direction:ltr;color:#9fc4d4}.np-kind-efi{border-top-color:#6a88a0}.np-kind-electrical{border-top-color:#d0ad55}.np-kind-handling{border-top-color:#8ca6b5}.np-kind-safety{border-top-color:#74a594}.np-kind-acoustic{border-top-color:#9a8ab5}.np-kind-performance{border-top-color:#b9925c}.np-kind-fault{border-top-color:#b26a62}.np-kind-protocol{border-top-color:#6b86b8}.np-kind-keys{border-top-color:#c3a65a}.np-kind-report{border-top-color:#9e9b98}.np-kind-network{border-top-color:#6a88a0}@media(max-width:1100px){.np-context-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:760px){.np-context-grid{grid-template-columns:1fr}.np-module-context header,.np-module-context footer{flex-direction:column}.np-links a small{display:none}}
'''

s=common.read_text('utf-8')
if NAV_MARK not in s: common.write_text(s+'\n'+nav_js+'\n','utf-8')
s=module.read_text('utf-8')
if MODULE_MARK not in s: module.write_text(s+'\n'+module_js+'\n','utf-8')
s=css.read_text('utf-8')
if CSS_MARK not in s: css.write_text(s+'\n'+css_add+'\n','utf-8')

# Static local-link gate: every explicit relative HTML link in the UI must resolve.
broken=[]
for p in ui.rglob('*.html'):
    text=p.read_text('utf-8',errors='ignore')
    for href in re.findall(r'href=["\']([^"\']+)["\']',text,re.I):
        if not href or href.startswith(('#','http://','https://','mailto:','javascript:','/')): continue
        target=(p.parent/href.split('#',1)[0].split('?',1)[0]).resolve()
        try: target.relative_to(ui.resolve())
        except ValueError: continue
        if href.lower().endswith('.html') and not target.exists(): broken.append(f'{p.relative_to(ui)} -> {href}')
if broken:
    print('\n'.join(broken[:100])); raise SystemExit(f'NAV_PARITY_BROKEN_LINKS count={len(broken)}')
print('NEXVARY_NAV_PARITY_PASS fullManifestSidebar=true brokenStaticLinks=0 routeSpecificViews=true runtimeLinkAudit=true')
