import { useState } from "react";

const COLORS = {
  bg: "#0a0e1a",
  card: "#111827",
  border: "#1f2937",
  red: "#ef4444",
  blue: "#3b82f6",
  green: "#22c55e",
  yellow: "#f59e0b",
  purple: "#a855f7",
  cyan: "#06b6d4",
  text: "#f1f5f9",
  muted: "#94a3b8",
  dim: "#475569",
};

const steps = [
  {
    id: 1,
    label: "SAP KILDEDATA",
    subtitle: "SE16H uttrekk – 15 filer",
    color: "#3b82f6",
    groups: [
      {
        title: "🗂 Masterdata",
        color: "#1d4ed8",
        tables: [
          { name: "MARD", desc: "Artikkelunivers LGORT 3000", rows: "~1 000" },
          { name: "MDMA", desc: "ABC/XYZ (ZZABC, ZZXYZ)", rows: "~1 000" },
          { name: "MARA", desc: "Materialtype, varegruppe", rows: "~1 000" },
          { name: "MAKT", desc: "Materialebeskrivelse", rows: "~1 000" },
          { name: "MARC", desc: "MRP-parametere, MTVFP", rows: "~1 000" },
          { name: "MBEW", desc: "Pris, PEINH, VPRSV", rows: "~1 000" },
        ],
      },
      {
        title: "🔴 Forbruk UT fra lager",
        color: "#b91c1c",
        tables: [
          { name: "MSEG 2024", desc: "BWART=201+647, LGORT=3000", rows: "~135 000" },
          { name: "MSEG 2025", desc: "BWART=201+647, LGORT=3000", rows: "~135 000" },
        ],
      },
      {
        title: "🔵 Innkjøp INN til lager",
        color: "#1e40af",
        tables: [
          { name: "EKKO", desc: "BSART=ZNB, EKGRP=3000+300", rows: "13 154" },
          { name: "EKPO", desc: "LGORT=3000, LOEKZ=blank", rows: "8 240" },
          { name: "EKBE", desc: "BEWTP=E, BWART=101", rows: "9 004" },
        ],
      },
      {
        title: "📋 Leveringstider",
        color: "#0e7490",
        tables: [
          { name: "EINA", desc: "MATNR → INFNR", rows: "–" },
          { name: "EINE", desc: "WEBAZ leveringstid", rows: "–" },
          { name: "T023T", desc: "Varegruppenavn", rows: "–" },
        ],
      },
    ],
  },
  {
    id: 2,
    label: "DATAVASK",
    subtitle: "Python – pandas",
    color: "#f59e0b",
    checks: [
      { icon: "🔗", text: "Koble alle tabeller på MATNR" },
      { icon: "💰", text: "PEINH-korreksjon: pris = STPRS ÷ PEINH" },
      { icon: "📅", text: "Aggreger MSEG per MATNR per måned (24 mnd)" },
      { icon: "📦", text: "Netto EKBE: sum(S) − sum(H) per MATNR" },
      { icon: "🚫", text: "Ekskluder: pris=0, nullforbruk, feil MTART" },
      { icon: "📊", text: "Rapporter MDMA-dekningsgrad (ZZXYZ blank?)" },
    ],
  },
  {
    id: 3,
    label: "ANALYSE",
    subtitle: "4 klassifiseringsmoduler",
    color: "#a855f7",
    modules: [
      {
        name: "ABC-analyse",
        color: "#7c3aed",
        input: "EKPO.NETWR",
        logic: "Kumulativ innkjøpsverdi",
        output: "A (80%) · B (15%) · C (5%)",
      },
      {
        name: "XYZ-klassifisering",
        color: "#dc2626",
        input: "MSEG aggregert/mnd",
        logic: "CV = σ/μ over 24 måneder",
        output: "X (<0.5) · Y (0.5–1.0) · Z (>1.0)",
      },
      {
        name: "EOQ-avvik",
        color: "#0891b2",
        input: "MSEG (D) + MBEW (H) + S=750kr",
        logic: "Wilson EOQ vs faktisk ordrefrekvens",
        output: "Avvik i % · Høy/Lav kostnad",
      },
      {
        name: "K-means klynge",
        color: "#059669",
        input: "Verdi + CV + ordrefrekvens",
        logic: "Normalisert · Elbow-metode K=2–8",
        output: "Klynge 1–K med profil",
      },
    ],
  },
  {
    id: 4,
    label: "REGELMOTOR",
    subtitle: "HVFS-anbefaling per artikkel",
    color: "#22c55e",
    rules: [
      { cond: "A-artikkel + X/Y + lavt EOQ-avvik", result: "✅ Overfør til HVFS", color: "#16a34a" },
      { cond: "C-artikkel + Z + høyt EOQ-avvik", result: "🏠 Behold lokalt", color: "#b45309" },
      { cond: "Alle andre kombinasjoner", result: "🔍 Nærmere vurdering", color: "#1d4ed8" },
    ],
  },
  {
    id: 5,
    label: "SLUTTRESULTAT",
    subtitle: "Output til rapport og Excel",
    color: "#06b6d4",
    outputs: [
      { icon: "📋", title: "Artikkelklassifisering", desc: "~800–1200 artikler med ABC, XYZ, klynge og anbefaling" },
      { icon: "📊", title: "Pareto-diagram", desc: "ABC-fordeling med kumulativ verdi" },
      { icon: "🔷", title: "ABC/XYZ-matrise", desc: "9-felts matrise med antall artikler per kombinasjon" },
      { icon: "🫧", title: "Klyngeplot", desc: "K-means visualisering normaliserte variabler" },
      { icon: "💵", title: "Besparelsesestimering", desc: "Kr/år ved HVFS-overføring · Best/base/worst case" },
      { icon: "✅", title: "XYZ-validering", desc: "Samsvar MDMA.ZZXYZ vs beregnet XYZ fra MSEG" },
    ],
  },
];

export default function Pipeline() {
  const [active, setActive] = useState(null);

  return (
    <div style={{ background: "#0a0e1a", minHeight: "100vh", fontFamily: "Georgia, serif", color: "#f1f5f9", padding: "32px 16px" }}>
      <div style={{ maxWidth: 880, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{ fontSize: 10, letterSpacing: 4, color: "#94a3b8", marginBottom: 8, fontFamily: "monospace" }}>LOG650 · HELSE BERGEN · WERKS 3300 · LGORT 3000</div>
          <h1 style={{ fontSize: 26, fontWeight: "normal", margin: 0, letterSpacing: 1 }}>Datapipeline & Analyseplan</h1>
          <div style={{ width: 60, height: 1, background: "#06b6d4", margin: "12px auto 0" }} />
        </div>

        {steps.map((step, i) => (
          <div key={step.id}>
            <div
              onClick={() => setActive(active === step.id ? null : step.id)}
              style={{ border: `1px solid ${active === step.id ? step.color : "#1f2937"}`, borderRadius: 8, overflow: "hidden", cursor: "pointer", background: "#111827", transition: "border-color 0.2s" }}
            >
              <div style={{ background: step.color + "15", borderBottom: `1px solid ${step.color}40`, padding: "14px 20px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ fontFamily: "monospace", fontSize: 11, color: step.color, background: step.color + "20", padding: "2px 8px", borderRadius: 3, border: `1px solid ${step.color}40` }}>
                    STEG {step.id}
                  </span>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: "bold", letterSpacing: 1 }}>{step.label}</div>
                    <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 1 }}>{step.subtitle}</div>
                  </div>
                </div>
                <span style={{ color: "#475569", fontSize: 16 }}>{active === step.id ? "▲" : "▼"}</span>
              </div>

              {active === step.id && (
                <div style={{ padding: 20 }}>
                  {step.groups && (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(195px, 1fr))", gap: 10 }}>
                      {step.groups.map(g => (
                        <div key={g.title} style={{ border: `1px solid ${g.color}40`, borderRadius: 6, overflow: "hidden" }}>
                          <div style={{ background: g.color + "20", padding: "7px 12px", fontSize: 11, fontWeight: "bold", borderBottom: `1px solid ${g.color}30` }}>{g.title}</div>
                          {g.tables.map(t => (
                            <div key={t.name} style={{ padding: "5px 12px", borderBottom: "1px solid #1f2937", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                              <div>
                                <span style={{ fontFamily: "monospace", fontSize: 11, color: "#06b6d4" }}>{t.name}</span>
                                <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 1 }}>{t.desc}</div>
                              </div>
                              <span style={{ fontFamily: "monospace", fontSize: 10, color: "#475569", whiteSpace: "nowrap", marginLeft: 6 }}>{t.rows}</span>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}

                  {step.checks && (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 8 }}>
                      {step.checks.map((c, i) => (
                        <div key={i} style={{ padding: "10px 14px", background: "#f59e0b10", border: "1px solid #f59e0b30", borderRadius: 6, fontSize: 12 }}>
                          <span style={{ marginRight: 8 }}>{c.icon}</span>{c.text}
                        </div>
                      ))}
                    </div>
                  )}

                  {step.modules && (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(195px, 1fr))", gap: 10 }}>
                      {step.modules.map(m => (
                        <div key={m.name} style={{ border: `1px solid ${m.color}40`, borderRadius: 6, overflow: "hidden" }}>
                          <div style={{ background: m.color + "20", padding: "7px 12px", fontSize: 12, fontWeight: "bold", borderBottom: `1px solid ${m.color}30`, color: m.color }}>{m.name}</div>
                          <div style={{ padding: "10px 12px" }}>
                            <div style={{ marginBottom: 7 }}>
                              <div style={{ fontSize: 9, color: "#475569", marginBottom: 2, letterSpacing: 1 }}>INPUT</div>
                              <div style={{ fontFamily: "monospace", fontSize: 10, color: "#94a3b8" }}>{m.input}</div>
                            </div>
                            <div style={{ marginBottom: 7 }}>
                              <div style={{ fontSize: 9, color: "#475569", marginBottom: 2, letterSpacing: 1 }}>LOGIKK</div>
                              <div style={{ fontSize: 11, color: "#f1f5f9" }}>{m.logic}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: 9, color: "#475569", marginBottom: 2, letterSpacing: 1 }}>OUTPUT</div>
                              <div style={{ fontFamily: "monospace", fontSize: 10, color: m.color }}>{m.output}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {step.rules && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      {step.rules.map((r, i) => (
                        <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", border: `1px solid ${r.color}40`, borderRadius: 6, background: r.color + "08" }}>
                          <div style={{ flex: 1, fontFamily: "monospace", fontSize: 11, color: "#94a3b8" }}>IF {r.cond}</div>
                          <div style={{ fontSize: 13, color: r.color, fontWeight: "bold", whiteSpace: "nowrap" }}>{r.result}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {step.outputs && (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
                      {step.outputs.map((o, i) => (
                        <div key={i} style={{ padding: "12px 16px", border: "1px solid #06b6d430", borderRadius: 6, background: "#06b6d408" }}>
                          <div style={{ fontSize: 22, marginBottom: 6 }}>{o.icon}</div>
                          <div style={{ fontSize: 12, fontWeight: "bold", color: "#06b6d4", marginBottom: 4 }}>{o.title}</div>
                          <div style={{ fontSize: 11, color: "#94a3b8" }}>{o.desc}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {i < steps.length - 1 && (
              <div style={{ display: "flex", justifyContent: "center", padding: "6px 0", position: "relative" }}>
                <div style={{ width: 2, height: 28, background: "linear-gradient(to bottom, #475569, #94a3b8)" }} />
              </div>
            )}
          </div>
        ))}

        <div style={{ textAlign: "center", marginTop: 36, fontSize: 10, color: "#475569", fontFamily: "monospace" }}>
          LOG650 · Thomas Ekrem Jensen · Helse Vest IKT · v1.0 · 2026
        </div>
      </div>
    </div>
  );
}
