import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('005 report/LOG650_Rapport_FINAL.md', encoding='utf-8') as f:
    md = f.read()
with open('005 report/__word_extract/word_content.txt', encoding='utf-8') as f:
    word = f.read()

def md_sections(md):
    out = {}
    cur = 'PREAMBLE'
    buf = []
    for line in md.split('\n'):
        m = re.match(r'^(#{1,2})\s+(.+)$', line)
        if m:
            if buf:
                out[cur] = '\n'.join(buf)
            cur = m.group(2).strip()
            buf = []
        else:
            buf.append(line)
    if buf:
        out[cur] = '\n'.join(buf)
    return out

def word_sections(word):
    out = {}
    cur = 'PREAMBLE'
    buf = []
    for line in word.split('\n'):
        m = re.match(r'^\[Overskrift[12]\]\s*(.*)$', line)
        if m:
            if buf:
                out[cur] = '\n'.join(buf)
            cur = m.group(1).strip()
            buf = []
        elif line.startswith('===='):
            continue
        else:
            buf.append(line)
    if buf:
        out[cur] = '\n'.join(buf)
    return out

def strip_to_prose(s, is_md=True):
    if is_md:
        # Drop pipe tables
        lines = [l for l in s.split('\n') if not l.strip().startswith('|')]
        s = '\n'.join(lines)
        # Keep image alt text (figurtekst), drop only the URL part
        s = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', s)
        # Drop math
        s = re.sub(r'\$\$[^$]+\$\$', '', s, flags=re.DOTALL)
        s = re.sub(r'\$[^$]+\$', '', s)
        # Drop markdown markers (but not escape backslashes that precede underscore)
        s = re.sub(r'\\([_*])', r'\1', s)  # un-escape
        s = re.sub(r'[*_#>`]', '', s)
    else:
        s = re.sub(r'\[TABELL\].*?\[/TABELL\]', '', s, flags=re.DOTALL)
    s = s.replace('\u2014', '\u2013')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

md_s = md_sections(md)
word_s = word_sections(word)

print(f'{"Section":60s} {"MD":>6s} {"W":>6s} {"diff":>7s}')
print('-' * 85)
for k in sorted(set(md_s) & set(word_s)):
    if k in ['PREAMBLE']:
        continue
    m = strip_to_prose(md_s[k], True)
    w = strip_to_prose(word_s[k], False)
    d = len(w) - len(m)
    if abs(d) > 20:
        print(f'{k[:60]:60s} {len(m):6d} {len(w):6d} {d:+7d}')
