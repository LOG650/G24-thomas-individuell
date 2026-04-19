import re, sys, difflib
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


def normalize_for_compare(s, is_md=True):
    if is_md:
        lines = [l for l in s.split('\n') if not l.strip().startswith('|')]
        s = '\n'.join(lines)
        # Turn images into just alt-text
        s = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', s)
        # Drop latex math blocks
        s = re.sub(r'\$\$[^$]+\$\$', 'MATH', s, flags=re.DOTALL)
        s = re.sub(r'\$[^$]+\$', 'MATH', s)
        # Un-escape underscores and stars
        s = re.sub(r'\\([_*])', r'\1', s)
        # Drop formatting markers
        s = re.sub(r'[*_#>`]', '', s)
    else:
        # Remove tables in word
        s = re.sub(r'\[TABELL\].*?\[/TABELL\]', '', s, flags=re.DOTALL)
    # Normalize dashes
    s = s.replace('\u2014', '\u2013')
    # Normalize Planck-h to regular h
    s = s.replace('\u210e', 'h')
    # Sentence split on periods, bullet points, etc.
    # First collapse whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[\.\!\?])\s+', s)
    return [x.strip() for x in sentences if x.strip()]


md_s = md_sections(md)
word_s = word_sections(word)

target = sys.argv[1] if len(sys.argv) > 1 else None
focus = [target] if target else [
    '5.1 ABC-modellen', '5.3 EOQ-modellen og besparelsesformelen',
    '5.4 K-means klyngemodellen', '5.5 Regelmotor',
    '6.1 ABC-analyse av 709 artikler', '6.2 XYZ-klassifisering',
    '6.3 EOQ-avviksberegning', '6.4 K-means klyngeanalyse',
    '6.5 Regelmotor og HVFS-scoring', '7.6 Besparelse og sensitivitet',
    '8.2 Metodekritikk',
]

for sec in focus:
    if sec not in md_s or sec not in word_s:
        print(f'{sec}: NOT FOUND')
        continue
    m_sent = normalize_for_compare(md_s[sec], True)
    w_sent = normalize_for_compare(word_s[sec], False)
    print(f'\n=== {sec} ===')
    print(f'MD: {len(m_sent)} sentences, Word: {len(w_sent)} sentences')
    # Use difflib on sentences
    sm = difflib.SequenceMatcher(None, m_sent, w_sent)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        if tag == 'delete':
            for k in range(i1, i2):
                print(f'  [MD-only]  {m_sent[k][:200]}')
        elif tag == 'insert':
            for k in range(j1, j2):
                print(f'  [W-only ]  {w_sent[k][:200]}')
        elif tag == 'replace':
            for k in range(i1, i2):
                print(f'  [MD->  ]  {m_sent[k][:200]}')
            for k in range(j1, j2):
                print(f'  [  ->W ]  {w_sent[k][:200]}')
