import re

with open("LOG650_Rapport_FINAL_v10 (1).md", "r", encoding="utf-8") as f:
    content = f.read()

sections = [
    ("Forord", "# Forord", "# Sammendrag"),
    ("Sammendrag", "# Sammendrag", "# Kapittel 1"),
    ("Kap 1", "# Kapittel 1", "# Kapittel 2"),
    ("Kap 2", "# Kapittel 2", "# Kapittel 3"),
    ("Kap 3", "# Kapittel 3", "# Kapittel 4"),
    ("Kap 4", "# Kapittel 4", "# Kapittel 5"),
    ("Kap 5", "# Kapittel 5", "# Kapittel 6"),
    ("Kap 6", "# Kapittel 6", "# Kapittel 7"),
    ("Kap 7", "# Kapittel 7", "# Kapittel 8"),
    ("Kap 8", "# Kapittel 8", "# Kapittel 9"),
    ("Kap 9", "# Kapittel 9", "# Referanseliste"),
    ("Bibliografi", "# Referanseliste", "ZZZENDFLAG"),
]

targets = {
    "Forord": 300, "Sammendrag": 350,
    "Kap 1": 900, "Kap 2": 3600, "Kap 3": 1350,
    "Kap 4": 1800, "Kap 5": 1800, "Kap 6": 2250,
    "Kap 7": 1800, "Kap 8": 2250, "Kap 9": 900,
    "Bibliografi": 900,
}

total = 0
print(f"{'Del':<20} {'Ord':>6} {'Mal':>6} {'Avvik':>8}  Status")
print("-" * 60)

for name, start, end in sections:
    s = content.find(start)
    e = content.find(end, s + len(start)) if end != "ZZZENDFLAG" else len(content)
    if s == -1:
        continue
    text = content[s:e]
    clean = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    clean = re.sub(r"\|[^\n]*\|", "", clean)
    clean = re.sub(r"^\s*[-|:]+\s*$", "", clean, flags=re.MULTILINE)
    clean = re.sub(r"\$\$.*?\$\$", "MATH", clean, flags=re.DOTALL)
    clean = re.sub(r"\$[^$]+\$", "MATH", clean)
    clean = re.sub(r"#+\s", "", clean)
    clean = re.sub(r"[*_~`]", "", clean)
    words = len(clean.split())
    target = targets.get(name, 0)
    total += words
    diff = words - target
    pct = words / target * 100 if target else 0
    if 85 <= pct <= 115:
        status = "OK"
    elif pct < 85:
        status = "KORT"
    else:
        status = "LANGT"
    print(f"{name:<20} {words:>6} {target:>6} {diff:>+8}  {status}")

print("-" * 60)
print(f"{'TOTALT':<20} {total:>6} {18200:>6} {total-18200:>+8}")
