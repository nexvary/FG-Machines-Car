from pathlib import Path
import re, sys, struct, zlib, binascii

root=Path(sys.argv[1]).resolve()
if not root.exists(): raise SystemExit(f'REBRAND_ROOT_MISSING {root}')

REPLS=[
('FG MACHINES CAR','NEXVARY'),('FG Machines Car','Nexvary'),('FG machines car','Nexvary'),
('FG-MACHINES-CAR','NEXVARY'),('FG-Machines-Car','Nexvary'),('fg-machines-car','nexvary'),
('FGMACHINESCAR','NEXVARY'),('FGMachinesCar','Nexvary'),('fgmachinescar','nexvary'),
('FG MACHINES','NEXVARY'),('FG Machines','Nexvary'),('FG machines','Nexvary'),
('FG-MACHINES','NEXVARY'),('FG-Machines','Nexvary'),('fg-machines','nexvary'),
('FG Connect','Nexvary Connect'),('FG CONNECT','NEXVARY CONNECT'),
('FG Chat','Nexvary Chat'),('FG CHAT','NEXVARY CHAT'),('FG Local Session','Nexvary Local Session'),
('FG Contacts','Nexvary Contacts'),('FG Requests','Nexvary Requests'),
('جهات اتصال FG','جهات اتصال Nexvary'),('طلبات FG','طلبات Nexvary'),
('FG KEY SERVICE SESSION','NEXVARY KEY SERVICE SESSION'),('FG Native Live Session','Nexvary Native Live Session'),
('FG Navigation Selftest','Nexvary Navigation Selftest'),('FG-SBOM-1','NEXVARY-SBOM-1')]
changed=0; replacements=0
for p in list(root.rglob('*')):
    if not p.is_file(): continue
    try:
        raw=p.read_bytes()
        if b'\0' in raw[:4096]: continue
        s=raw.decode('utf-8')
    except Exception: continue
    old=s
    for a,b in REPLS:
        n=s.count(a)
        if n: replacements+=n; s=s.replace(a,b)
    s=s.replace('"FG-','"NX-').replace("'FG-","'NX-")
    if 'native/ui-modern' in p.as_posix():
        s=s.replace('>FG</div>','>N</div>')
        s=re.sub(r'\bFG\b','Nexvary',s)
    if s!=old: p.write_text(s,encoding='utf-8'); changed+=1

for p in sorted(root.rglob('*'),key=lambda x:len(x.parts),reverse=True):
    name=p.name; new=name
    for a,b in [('FG-Machines-Car','Nexvary'),('fg-machines-car','nexvary'),('FGMachinesCar','Nexvary'),('fgmachinescar','nexvary'),('FG Machines Car','Nexvary')]: new=new.replace(a,b)
    if name=='fg-icon.svg': new='nexvary-icon.svg'
    if new!=name:
        t=p.with_name(new)
        if t.exists(): raise SystemExit(f'REBRAND_RENAME_COLLISION {t}')
        p.rename(t)

for rel in ['native/src/app/modern/ModernHost.cpp','native/src/app/modern/ModernHost.hpp']:
    p=root/rel
    if p.exists(): p.write_text(p.read_text('utf-8').replace('fg-icon.svg','nexvary-icon.svg'),'utf-8')

iss=root/'native/windows/installer/Nexvary.iss'
if iss.exists():
    s=iss.read_text('utf-8')
    s=re.sub(r'(?m)^AppId=\{\{[^\r\n]+$','AppId={{197C2843-369D-4B91-95C3-E54613706E20}',s)
    s=s.replace('AppPublisher=Nexvary','AppPublisher=NEXVARY Inc')
    iss.write_text(s,'utf-8')

svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><defs><linearGradient id="b" x1="0" x2="1"><stop stop-color="#d7e4ef"/><stop offset=".45" stop-color="#2ca8ff"/><stop offset="1" stop-color="#0b63ff"/></linearGradient><linearGradient id="g" x1="0" x2="1"><stop stop-color="#f4d88a"/><stop offset="1" stop-color="#c4942e"/></linearGradient></defs><path d="M128 14 224 50v72c0 64-39 103-96 120C71 225 32 186 32 122V50z" fill="#071525" stroke="url(#b)" stroke-width="9"/><path d="M74 74h25l83 104V74h26v119h-25L100 90v103H74z" fill="url(#g)"/><path d="M55 188c23-17 47-21 73-21 29 0 51 4 73 21" fill="none" stroke="#d9e7f3" stroke-width="8" stroke-linecap="round"/><circle cx="85" cy="193" r="9" fill="#169eff"/><circle cx="173" cy="193" r="9" fill="#169eff"/></svg>'''
web=root/'native/ui-modern'; web.mkdir(parents=True,exist_ok=True); (web/'nexvary-icon.svg').write_text(svg,'utf-8')
old=web/'fg-icon.svg'
if old.exists(): old.unlink()

def icon_pixels(n=64):
    out=[]
    for y in range(n):
        row=[]
        for x in range(n):
            r,g,b,a=4,12,28,255
            border=(x<3 or y<3 or x>=n-3 or y>=n-3)
            if border: r,g,b=20,125,240
            left=16<=x<=21 and 17<=y<=47
            right=42<=x<=47 and 17<=y<=47
            diag=17<=y<=47 and abs(x-(18+(y-17)*0.9))<=3
            if left or right or diag: r,g,b=232,188,72
            if 48<=y<=51 and 14<=x<=50: r,g,b=205,220,235
            row.append((r,g,b,a))
        out.append(row)
    return out

def make_png(path,n=64):
    px=icon_pixels(n); raw=b''.join(b'\x00'+b''.join(bytes((r,g,b,a)) for r,g,b,a in row) for row in px)
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',binascii.crc32(t+d)&0xffffffff)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    path.write_bytes(data)

def make_ico(path,n=64):
    px=icon_pixels(n); xor=b''.join(b''.join(bytes((b,g,r,a)) for r,g,b,a in px[y]) for y in range(n-1,-1,-1))
    mask_stride=((n+31)//32)*4; andmask=b'\x00'*(mask_stride*n)
    dib=struct.pack('<IIIHHIIIIII',40,n,n*2,1,32,0,len(xor)+len(andmask),0,0,0,0)+xor+andmask
    hdr=struct.pack('<HHH',0,1,1); ent=struct.pack('<BBBBHHII',n,n,0,0,1,32,len(dib),22)
    path.write_bytes(hdr+ent+dib)
res=root/'native/windows/resources'; res.mkdir(parents=True,exist_ok=True); make_png(res/'Nexvary.png'); make_ico(res/'Nexvary.ico')

viol=[]; needles=[b'fg machines',b'fg-machines',b'fgmachines']
for p in root.rglob('*'):
    rel=str(p.relative_to(root))
    if re.search(r'FG[-_ ]?Machines|FGMachines',rel,re.I): viol.append(f'PATH {rel}')
    if p.is_file():
        try: raw=p.read_bytes()
        except Exception: continue
        low=raw.lower()
        for n in needles:
            if n in low: viol.append(f'CONTENT {rel}: {n.decode()}'); break
if viol:
    print('\n'.join(viol[:100])); raise SystemExit(f'NEXVARY_BRAND_AUDIT_FAIL violations={len(viol)}')
print(f'NEXVARY_REBRAND_PASS files={changed} replacements={replacements} app=Nexvary forbiddenBrand=0 artwork=Nexvary appId=197C2843-369D-4B91-95C3-E54613706E20')
