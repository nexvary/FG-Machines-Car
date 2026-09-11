from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
ui = root / 'native' / 'ui-modern'
if not ui.exists():
    raise SystemExit(f'UBUNTU24_BRANDING_UI_MISSING {ui}')

replacements = {
    'Windows Native Core': 'Ubuntu 24.04 Native Core',
    'Windows Native': 'Ubuntu Native',
}

changed = 0
hits = 0
for pattern in ('*.html', '*.js', '*.json'):
    for p in ui.rglob(pattern):
        text = p.read_text(encoding='utf-8')
        new = text
        for old, repl in replacements.items():
            count = new.count(old)
            if count:
                hits += count
                new = new.replace(old, repl)
        if new != text:
            p.write_text(new, encoding='utf-8')
            changed += 1

# Give the Linux build a stable hook for any future platform-specific UI refinements.
for p in ui.rglob('*.html'):
    text = p.read_text(encoding='utf-8')
    if '<body' in text and 'fg-ubuntu24' not in text:
        if 'class="' in text[text.find('<body'):text.find('>', text.find('<body')) + 1]:
            start = text.find('<body')
            end = text.find('>', start)
            tag = text[start:end + 1]
            tag2 = tag.replace('class="', 'class="fg-ubuntu24 ', 1)
            text = text[:start] + tag2 + text[end + 1:]
        else:
            text = text.replace('<body', '<body class="fg-ubuntu24"', 1)
        p.write_text(text, encoding='utf-8')

# Fail rather than shipping a Linux screenshot that still advertises the Windows host.
leftovers = []
for p in ui.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.html', '.js', '.json'}:
        text = p.read_text(encoding='utf-8')
        if 'Windows Native Core' in text:
            leftovers.append(str(p.relative_to(ui)))
if leftovers:
    raise SystemExit('UBUNTU24_BRANDING_LEFTOVER ' + ','.join(leftovers[:20]))

print(f'UBUNTU24_BRANDING_APPLIED changed={changed} replacements={hits} label=Ubuntu-24.04-Native-Core')
