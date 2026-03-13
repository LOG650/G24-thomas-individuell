"""
Genererer konseptuelle figurer for rapporten:
- Figur 0: Konseptuelt rammeverk
- Figur 1: Lagerstruktur Helse Vest
- Figur 2: Analysepipeline
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

os.makedirs('plots', exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'text.color': '#212121',
})

# ── Figur 0: Konseptuelt rammeverk ──
fig, ax = plt.subplots(figsize=(13, 3.2))
ax.axis('off')

bokser = [
    ('SAP-data\n(WERKS 3300)', '#E3F2FD', '#212121'),
    ('ABC-\nanalyse', '#BBDEFB', '#212121'),
    ('XYZ-\nklassifisering', '#90CAF9', '#212121'),
    ('EOQ-\navvik', '#64B5F6', '#212121'),
    ('K-means\nklustering', '#42A5F5', '#212121'),
    ('Regelmotor\nHVFS-regler', '#1E88E5', 'white'),
    ('HVFS-\nanbefaling', '#1565C0', 'white'),
]

bw = 0.11
mellom = 0.015
x0 = 0.025
y0 = 0.20
bh = 0.60

for i, (tekst, farge, tc) in enumerate(bokser):
    x = x0 + i * (bw + mellom)
    ax.add_patch(plt.Rectangle((x, y0), bw, bh,
                                transform=ax.transAxes, facecolor=farge,
                                ec='#90A4AE', linewidth=0.8, zorder=2, clip_on=False))
    ax.text(x + bw/2, y0 + bh/2, tekst, transform=ax.transAxes,
            ha='center', va='center', fontsize=8.5, color=tc,
            fontweight='bold', zorder=3)
    if i < len(bokser) - 1:
        xp = x + bw
        ax.annotate('', xy=(xp + mellom, y0 + bh/2),
                    xytext=(xp, y0 + bh/2),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#455A64', lw=1.5))

ax.set_title('Konseptuelt rammeverk - fra SAP-data til HVFS-anbefaling', fontsize=10, pad=12)
plt.tight_layout()
plt.savefig('plots/00_Konseptuelt_Rammeverk.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figur 0 - Konseptuelt rammeverk lagret")

# ── Figur 1: Lagerstruktur ──
fig, ax = plt.subplots(figsize=(10, 5))
ax.axis('off')
ax.set_xlim(0, 1); ax.set_ylim(0, 1)

def boks(ax, x, y, w, h, tekst, farge='#BBDEFB', tc='#212121', fs=9):
    ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=farge, ec='#90A4AE', lw=1, zorder=2))
    ax.text(x+w/2, y+h/2, tekst, ha='center', va='center',
            fontsize=fs, color=tc, fontweight='bold', zorder=3)

def pil(ax, x1, y1, x2, y2, etikett=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=1.5))
    if etikett:
        ax.text((x1+x2)/2+0.01, (y1+y2)/2+0.02, etikett,
                ha='center', fontsize=7, color='#455A64')

boks(ax, 0.35, 0.72, 0.30, 0.14, 'HVFS\nHelse Vest Forsyningssentral', '#1565C0', 'white', 10)
boks(ax, 0.35, 0.40, 0.30, 0.14, 'Helse Bergen\nWERKS 3300 / LGORT 3001', '#42A5F5', 'white', 9)
boks(ax, 0.02, 0.40, 0.24, 0.14, 'HUS\n(eksempel)', '#BBDEFB', '#212121', 8)
boks(ax, 0.74, 0.40, 0.24, 0.14, 'Stavanger\n(eksempel)', '#BBDEFB', '#212121', 8)
boks(ax, 0.18, 0.10, 0.22, 0.12, 'Seksjon/post\nHelse Bergen', '#E3F2FD', '#212121', 8)
boks(ax, 0.60, 0.10, 0.22, 0.12, 'Seksjon/post\nHelse Bergen', '#E3F2FD', '#212121', 8)

pil(ax, 0.50, 0.72, 0.50, 0.54, 'Sentralleveranse')
pil(ax, 0.14, 0.54, 0.14, 0.40, '')
pil(ax, 0.86, 0.54, 0.86, 0.40, '')
pil(ax, 0.50, 0.40, 0.29, 0.22, '')
pil(ax, 0.50, 0.40, 0.71, 0.22, '')
pil(ax, 0.50, 0.72, 0.14, 0.54, '')
pil(ax, 0.50, 0.72, 0.86, 0.54, '')

ax.set_title('Lagerstruktur - Helse Vest forsyningskjede (forenklet)', fontsize=11, pad=10)
plt.tight_layout()
plt.savefig('plots/00_Lagerstruktur.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figur 1 - Lagerstruktur lagret")

# ── Figur 2: Analysepipeline ──
fig, ax = plt.subplots(figsize=(13, 3.8))
ax.axis('off')

steg = [
    ('SAP S/4HANA\n14 tabeller', '#E3F2FD', '#212121'),
    ('Cleaning\nD-01-D-08', '#BBDEFB', '#212121'),
    ('MASTERFILE\n709 artikler', '#90CAF9', '#212121'),
    ('ABC / XYZ\nEOQ', '#64B5F6', '#212121'),
    ('K-means\nK = 3', '#42A5F5', '#212121'),
    ('Regelmotor\n8 regler', '#1E88E5', 'white'),
    ('HVFS-\nanbefaling\n145 art.', '#1565C0', 'white'),
]

bw = 0.118; mellom = 0.013; x0 = 0.022; y0 = 0.18; bh = 0.64

for i, (tekst, farge, tc) in enumerate(steg):
    x = x0 + i * (bw + mellom)
    ax.add_patch(plt.Rectangle((x, y0), bw, bh,
                                transform=ax.transAxes, facecolor=farge,
                                ec='#90A4AE', lw=0.8, zorder=2, clip_on=False))
    ax.text(x+bw/2, y0+bh/2, tekst, transform=ax.transAxes,
            ha='center', va='center', fontsize=8, color=tc,
            fontweight='bold', zorder=3)
    if i < len(steg)-1:
        xp = x + bw
        ax.annotate('', xy=(xp+mellom, y0+bh/2), xytext=(xp, y0+bh/2),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#455A64', lw=1.5))

ax.set_title('Analysepipeline: fra SAP-radata til HVFS-anbefaling', fontsize=10, pad=12)
plt.tight_layout()
plt.savefig('plots/00_Analysepipeline.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figur 2 - Analysepipeline lagret")

print("\nAlle konseptuelle figurer generert!")
