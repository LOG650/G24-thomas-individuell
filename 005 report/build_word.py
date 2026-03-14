"""
Bygg Word-dokument frå HiMolde-malen + MD-rapport.
Opnar malen, fyller inn forsider, slettar plasshaldarar,
og legg til alt innhald frå MD-fila.
"""

import re, os, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

TEMPLATE = '../000 templates/Mal prosjekt LOG650 v2.docx'
MD_FILE = 'LOG650_Rapport_FINAL_v10 (1).md'
OUTPUT = 'LOG650_Rapport_FINAL_word.docx'

doc = Document(TEMPLATE)

# ════════════════════════════════════════════════════
# STEG 1: Fyll inn forsidefelter
# ════════════════════════════════════════════════════
print("Steg 1: Fyller inn forsider...")

field_map = {
    'Tittel (norsk og/eller engelsk)': 'Fra lokalt forsyningslager til regional sentralforsyning:\nMultikriterieklassifisering og klyngeanalyse for identifisering av overføringskandidater ved Helse Bergen',
    'Forfatter(e)': 'Thomas Ekrem Jensen',
    'Molde, Innleveringsdato': 'Stavanger, Mai 2026',
}

for para in doc.paragraphs:
    t = para.text.strip()
    for key, val in field_map.items():
        if t == key or t.startswith(key):
            para.clear()
            run = para.add_run(val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            break
    # Studiepoeng og veileder (delvis match)
    if t.startswith('Studiepoeng:'):
        para.clear()
        r = para.add_run('Studiepoeng: 15')
        r.font.name = 'Times New Roman'; r.font.size = Pt(12)
    elif t.startswith('Veileder:'):
        para.clear()
        r = para.add_run('Veileder: Bård Inge Austigard Pettersen')
        r.font.name = 'Times New Roman'; r.font.size = Pt(12)
    elif t.startswith('Dato:') and len(t) < 20:
        para.clear()
        r = para.add_run('Dato: Mai 2026')
        r.font.name = 'Times New Roman'; r.font.size = Pt(12)
    elif t.startswith('Antall ord:'):
        para.clear()
    elif t.startswith('Forfattererklæring:'):
        para.clear()

# ════════════════════════════════════════════════════
# STEG 2: Les MD-fila
# ════════════════════════════════════════════════════
print("Steg 2: Les MD-fil...")

with open(MD_FILE, 'r', encoding='utf-8') as f:
    md_all = f.read()

# Hent ut Forord-tekst
forord_m = re.search(r'^# Forord\s*\n(.*?)(?=\n---)', md_all, re.DOTALL | re.MULTILINE)
forord_text = forord_m.group(1).strip() if forord_m else ''

# Hent ut Sammendrag-tekst
sammendrag_m = re.search(r'^# Sammendrag\s*\n(.*?)(?=\n---)', md_all, re.DOTALL | re.MULTILINE)
sammendrag_text = sammendrag_m.group(1).strip() if sammendrag_m else ''

# ════════════════════════════════════════════════════
# STEG 3: Sett inn Sammendrag-tekst etter "Sammendrag"-overskrifta
# ════════════════════════════════════════════════════
print("Steg 3: Setter inn Forord og Sammendrag...")

def insert_text_after(anchor_para, text):
    """Set inn avsnitt etter eit gitt avsnitt."""
    current = anchor_para._element
    for chunk in text.split('\n\n'):
        chunk = chunk.strip()
        if not chunk:
            continue
        new_p = OxmlElement('w:p')
        # Stil
        pPr = OxmlElement('w:pPr')
        pStyle = OxmlElement('w:pStyle')
        pStyle.set(qn('w:val'), 'Normal')
        pPr.append(pStyle)
        # Linjeavstand 1.5
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:line'), '360')
        spacing.set(qn('w:lineRule'), 'auto')
        pPr.append(spacing)
        new_p.append(pPr)
        # Tekst
        new_r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:ascii'), 'Times New Roman')
        rFonts.set(qn('w:hAnsi'), 'Times New Roman')
        rPr.append(rFonts)
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), '24')  # 12pt = 24 half-points
        rPr.append(sz)
        new_r.append(rPr)
        new_t = OxmlElement('w:t')
        new_t.set(qn('xml:space'), 'preserve')
        # Fjern markdown-formatering for enkel innsetting
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', chunk)
        clean = re.sub(r'\*(.+?)\*', r'\1', clean)
        clean = re.sub(r'\$(.+?)\$', r'\1', clean)
        new_t.text = clean
        new_r.append(new_t)
        new_p.append(new_r)
        current.addnext(new_p)
        current = new_p

# Finn Sammendrag og Abstract i malen
for para in doc.paragraphs:
    if para.text.strip() == 'Sammendrag':
        insert_text_after(para, sammendrag_text)
    elif para.text.strip() == 'Abstract':
        # Sett inn ei enkel melding
        insert_text_after(para, '(Sammendrag på norsk — sjå avsnittet over.)')

# Sett inn Forord mellom "Antall ord"/"Forfattererklæring" og "Sammendrag"
# Finn sammendrag-paragrafen og set inn Forord-heading + tekst FØR den
for para in doc.paragraphs:
    if para.text.strip() == 'Sammendrag':
        # Lag Forord-heading
        forord_heading = OxmlElement('w:p')
        fh_pPr = OxmlElement('w:pPr')
        fh_pStyle = OxmlElement('w:pStyle')
        fh_pStyle.set(qn('w:val'), 'Heading1')
        fh_pPr.append(fh_pStyle)
        # Sideskift før
        fh_pb = OxmlElement('w:pageBreakBefore')
        fh_pb.set(qn('w:val'), 'true')
        fh_pPr.append(fh_pb)
        forord_heading.append(fh_pPr)
        fh_r = OxmlElement('w:r')
        fh_t = OxmlElement('w:t')
        fh_t.text = 'Forord'
        fh_r.append(fh_t)
        forord_heading.append(fh_r)
        para._element.addprevious(forord_heading)
        # Set inn forord-tekst etter heading
        insert_text_after_elem = forord_heading
        current = forord_heading
        for chunk in forord_text.split('\n\n'):
            chunk = chunk.strip()
            if not chunk:
                continue
            new_p = OxmlElement('w:p')
            pPr = OxmlElement('w:pPr')
            sp = OxmlElement('w:spacing')
            sp.set(qn('w:line'), '360')
            sp.set(qn('w:lineRule'), 'auto')
            pPr.append(sp)
            new_p.append(pPr)
            r = OxmlElement('w:r')
            rPr = OxmlElement('w:rPr')
            rf = OxmlElement('w:rFonts')
            rf.set(qn('w:ascii'), 'Times New Roman')
            rf.set(qn('w:hAnsi'), 'Times New Roman')
            rPr.append(rf)
            szz = OxmlElement('w:sz')
            szz.set(qn('w:val'), '24')
            rPr.append(szz)
            r.append(rPr)
            t = OxmlElement('w:t')
            t.set(qn('xml:space'), 'preserve')
            clean = re.sub(r'\*\*(.+?)\*\*', r'\1', chunk)
            clean = re.sub(r'\*(.+?)\*', r'\1', clean)
            t.text = clean
            r.append(t)
            new_p.append(r)
            current.addnext(new_p)
            current = new_p
        break

# ════════════════════════════════════════════════════
# STEG 4: Slett plasshaldar-kapittel (frå "Innledning" til slutt)
# ════════════════════════════════════════════════════
print("Steg 4: Slettar plasshaldarar...")

body = doc.element.body
to_remove = []
found = False
for child in list(body):
    if child.tag.endswith('}sectPr'):
        continue
    if not found:
        if child.tag.endswith('}p'):
            pPr_elem = child.find(qn('w:pPr'))
            ps = pPr_elem.find(qn('w:pStyle')) if pPr_elem is not None else None
            if ps is not None:
                val = ps.get(qn('w:val'), '')
                if 'Heading' in val or 'Overskrift' in val or val == 'Overskrift1':
                    txt = ''.join(t.text or '' for t in child.iter(qn('w:t')))
                    if 'Innledning' in txt:
                        found = True
                        to_remove.append(child)
    else:
        to_remove.append(child)

for elem in to_remove:
    body.remove(elem)

print(f"  Fjerna {len(to_remove)} plasshaldar-element")

# ════════════════════════════════════════════════════
# STEG 5: Legg til kapittelinnhald frå MD
# ════════════════════════════════════════════════════
print("Steg 5: Legg til kapittelinnhald...")

# Finn start av kapittelinnhald i MD
kap_start = md_all.find('# Kapittel 1')
chapter_md = md_all[kap_start:]
lines = chapter_md.split('\n')

def add_formatted_para(doc, text):
    """Legg til avsnitt med enkel inline-formatering."""
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = 1.5

    # Fjern $ math markers for enkel visning
    text = re.sub(r'\$\$(.+?)\$\$', r'\1', text)

    # Del opp i bold/italic/normal segment
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            r = para.add_run(part[2:-2])
            r.font.bold = True
        elif part.startswith('*') and part.endswith('*'):
            r = para.add_run(part[1:-1])
            r.font.italic = True
        else:
            r = para.add_run(part)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        # rFonts
        rpr = r._element.get_or_add_rPr()
        rf = rpr.find(qn('w:rFonts'))
        if rf is None:
            rf = OxmlElement('w:rFonts')
            rpr.insert(0, rf)
        rf.set(qn('w:ascii'), 'Times New Roman')
        rf.set(qn('w:hAnsi'), 'Times New Roman')
        rf.set(qn('w:cs'), 'Times New Roman')
    return para

def add_heading_formatted(doc, text, level):
    """Legg til overskrift med Times New Roman."""
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = 'Times New Roman'
        r.font.color.rgb = RGBColor(0, 0, 0)
        rpr = r._element.get_or_add_rPr()
        rf = rpr.find(qn('w:rFonts'))
        if rf is None:
            rf = OxmlElement('w:rFonts')
            rpr.insert(0, rf)
        rf.set(qn('w:ascii'), 'Times New Roman')
        rf.set(qn('w:hAnsi'), 'Times New Roman')
        if level == 1:
            r.font.size = Pt(18)
        elif level == 2:
            r.font.size = Pt(16)
        elif level == 3:
            r.font.size = Pt(14)
    return h

def set_table_borders(table):
    """Legg til kantlinjer."""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    for old in tblPr.findall(qn('w:tblBorders')):
        tblPr.remove(old)
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)

# Figurstiar
fig_map = {
    'Fig00': 'Fig00_Konseptuelt_Rammeverk.png',
    'Fig01': 'Fig01_Lagerstruktur.png',
    'Fig02': 'Fig02_Analysepipeline.png',
    'Fig03': 'Fig03_Regelmotor.png',
    'Fig04': 'Fig04_ABC_Pareto.png',
    'Fig05': 'Fig05_ABC_XYZ_Matrise.png',
    'Fig06': 'Fig06_EOQ_Avvik.png',
    'Fig07': 'Fig07_Silhouette.png',
    'Fig08': 'Fig08_Kmeans_Klynger.png',
    'Fig09': 'Fig09_Kmeans_Profil.png',
    'Fig10': 'Fig10_Regelmotor_Besparelse.png',
}
plots_dir = os.path.abspath('../006 Analyse/plots')

table_count = 0
fig_count = 0
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    # ── Heading 1 ──
    if line.startswith('# ') and not line.startswith('## '):
        text = line[2:].strip()
        h = add_heading_formatted(doc, text, 1)
        # Sideskift før kapittel
        if any(kw in text for kw in ['Kapittel', 'Referanseliste', 'Vedlegg']):
            pPr = h._element.get_or_add_pPr()
            pb = OxmlElement('w:pageBreakBefore')
            pb.set(qn('w:val'), 'true')
            pPr.append(pb)

    # ── Heading 2 ──
    elif line.startswith('## '):
        add_heading_formatted(doc, line[3:].strip(), 2)

    # ── Heading 3 ──
    elif line.startswith('### '):
        add_heading_formatted(doc, line[4:].strip(), 3)

    # ── Horisontal linje ──
    elif stripped == '---':
        pass

    # ── Figur ──
    elif stripped.startswith('!['):
        m = re.match(r'!\[(.+?)\]\((.+?)\)', stripped)
        if m:
            caption = m.group(1)
            rel_path = m.group(2)
            # Finn biletet
            abs_path = os.path.abspath(os.path.join('.', rel_path))
            if os.path.exists(abs_path):
                doc.add_picture(abs_path, width=Cm(15))
                fig_count += 1
                # Bildetekst under
                cap_p = doc.add_paragraph()
                cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = cap_p.add_run(caption)
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)
                r.font.italic = True
            else:
                print(f"  ÅTVARING: Fann ikkje {abs_path}")

    # ── Tabell ──
    elif stripped.startswith('|') and not stripped.startswith('|---'):
        table_lines = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            table_lines.append(lines[i].strip())
            i += 1
        i -= 1

        if len(table_lines) >= 3:
            # Parse headers
            headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
            # Skip separator (line 1)
            # Data rows
            data_rows = []
            for tl in table_lines[2:]:
                cells = [c.strip() for c in tl.split('|')[1:-1]]
                data_rows.append(cells)

            ncols = len(headers)
            nrows = len(data_rows) + 1

            table = doc.add_table(rows=nrows, cols=ncols)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            # Header
            for j, h in enumerate(headers):
                if j < ncols:
                    cell = table.rows[0].cells[j]
                    cell.text = ''
                    p = cell.paragraphs[0]
                    r = p.add_run(h.replace('\\', ''))
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(10)
                    r.font.bold = True
                    # Skuggelegging
                    tc = cell._element
                    tcPr = tc.get_or_add_tcPr()
                    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="D9E2F3" w:val="clear"/>')
                    tcPr.append(shd)

            # Data
            for ri, row_data in enumerate(data_rows):
                for j, ct in enumerate(row_data):
                    if j < ncols:
                        cell = table.rows[ri + 1].cells[j]
                        cell.text = ''
                        p = cell.paragraphs[0]
                        clean = ct.replace('\\', '').replace('**', '')
                        r = p.add_run(clean)
                        r.font.name = 'Times New Roman'
                        r.font.size = Pt(10)

            set_table_borders(table)
            table_count += 1

    # ── Tabelltittel (kursiv med asterisk) ──
    elif stripped.startswith('*Tabell') or stripped.startswith('*Figur'):
        caption_text = stripped.strip('*')
        p = doc.add_paragraph()
        r = p.add_run(caption_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.italic = True

    # ── Blokkitat ──
    elif stripped.startswith('> '):
        quote = stripped[2:]
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.line_spacing = 1.5
        # Fjern markdown
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', quote)
        r = p.add_run(clean)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        if '**' in quote:
            r.font.bold = True

    # ── Matteblokk ──
    elif stripped.startswith('$$'):
        math = stripped
        if not stripped.endswith('$$') or stripped == '$$':
            i += 1
            while i < len(lines) and not lines[i].strip().endswith('$$'):
                math += ' ' + lines[i].strip()
                i += 1
            if i < len(lines):
                math += ' ' + lines[i].strip()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(math.replace('$$', '').strip())
        r.font.name = 'Cambria Math'
        r.font.size = Pt(11)
        r.font.italic = True

    # ── HTML (skip) ──
    elif stripped.startswith('<') and stripped.endswith('>'):
        pass

    # ── Vanleg avsnitt ──
    elif stripped and not stripped.startswith('```'):
        add_formatted_para(doc, stripped)

    i += 1

print(f"  Lagt til {table_count} tabellar, {fig_count} figurar")

# ════════════════════════════════════════════════════
# STEG 6: Global formatering
# ════════════════════════════════════════════════════
print("Steg 6: Formatering...")

# Margar
for section in doc.sections:
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)

# Heading-stilar
for name, size in [('Heading 1', 18), ('Heading 2', 16), ('Heading 3', 14)]:
    if name in doc.styles:
        s = doc.styles[name]
        s.font.name = 'Times New Roman'
        s.font.size = Pt(size)
        s.font.bold = True
        s.font.color.rgb = RGBColor(0, 0, 0)

# Normal-stil
ns = doc.styles['Normal']
ns.font.name = 'Times New Roman'
ns.font.size = Pt(12)
ns.paragraph_format.line_spacing = 1.5

# ════════════════════════════════════════════════════
# STEG 7: Lagre
# ════════════════════════════════════════════════════
doc.save(OUTPUT)
print(f"\nFerdig! Lagra som: {OUTPUT}")
print(f"  Totalt avsnitt: {len(doc.paragraphs)}")
print(f"  Tabellar: {len(doc.tables)}")
