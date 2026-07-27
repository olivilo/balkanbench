#!/usr/bin/env python3
"""BalkanBench-Auswertung: manuelle muttersprachliche Bewertung (0/0.5/1) je Fall/Modell,
+ Sprach-/Schrift-Disziplin + Verbosität → Grafiken für die Doku."""
import json, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE="/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench"
OUT=os.path.join(BASE,"results","charts"); os.makedirs(OUT, exist_ok=True)
MODELS=["v3","Yugo","Euro"]
COL={"v3":"#2e7d32","Yugo":"#c62828","Euro":"#1565c0"}
NAME={"v3":"Balkan-v3 (unser)","Yugo":"YugoGPT-7B-Instruct","Euro":"EuroLLM-9B-Instruct"}

# Fall -> (Kategorie, Score je Modell) aus muttersprachlicher Lektüre
CASES={
 "gore-4":     ("Homonym",     {"v3":.5,"Yugo":.5,"Euro":.25}),
 "grad":       ("Homonym",     {"v3":.5,"Yugo":.5,"Euro":.25}),
 "kosa":       ("Homonym",     {"v3":.5,"Yugo":.25,"Euro":.5}),
 "para":       ("Homonym",     {"v3":.5,"Yugo":.25,"Euro":.5}),
 "mk-homonym": ("Homonym",     {"v3":.75,"Yugo":.25,"Euro":0}),
 "ek-ijek":    ("Dialekt",     {"v3":1,"Yugo":.75,"Euro":.25}),
 "sl-dvojina": ("Dialekt",     {"v3":.5,"Yugo":0,"Euro":1}),
 "sq-def":     ("Dialekt",     {"v3":.5,"Yugo":0,"Euro":0}),
 "bkms-lex":   ("Sprachtrenn.",{"v3":1,"Yugo":0,"Euro":0}),
 "bread-3":    ("Sprachtrenn.",{"v3":1,"Yugo":.25,"Euro":0}),
 "false-obraz":("Sprachtrenn.",{"v3":.75,"Yugo":.5,"Euro":.25}),
 "translit":   ("Schrift",     {"v3":.75,"Yugo":0,"Euro":0}),
 "azbuka-answer":("Schrift",   {"v3":1,"Yugo":0,"Euro":.5}),
 "cnr-sz":     ("Schrift",     {"v3":.5,"Yugo":1,"Euro":.5}),
 "proverb-vuk":("Kultur",      {"v3":1,"Yugo":1,"Euro":1}),
 "slava":      ("Kultur",      {"v3":.5,"Yugo":.75,"Euro":.75}),
 "idiom-mk":   ("Kultur",      {"v3":1,"Yugo":.75,"Euro":.5}),
 "reason-inlang":("Reasoning", {"v3":.75,"Yugo":.75,"Euro":.5}),
}
# Sprach-/Schrift-Disziplin: verlangte Schrift/Sprache eingehalten? (1=ja)
DISC={
 "azbuka-answer":{"v3":1,"Yugo":0,"Euro":.5},  # Euro azb aber bulgarisch
 "translit":     {"v3":1,"Yugo":0,"Euro":0},
 "mk-homonym":   {"v3":1,"Yugo":0,"Euro":0},    # Euro→Bulgarisch
 "idiom-mk":     {"v3":1,"Yugo":0,"Euro":0},    # verlangt MK
 "reason-inlang":{"v3":0,"Yugo":0,"Euro":0},    # verlangte ćirilica: keiner
 "sq-def":       {"v3":1,"Yugo":0,"Euro":0},    # bleibt Albanisch
 "sl-dvojina":   {"v3":1,"Yugo":0,"Euro":1},
}

# Verbosität (ø Antwortlänge) direkt aus Ergebnisdateien
files={"v3":"balkan-v3-bench_latest.jsonl","Yugo":"yugogpt-bench_latest.jsonl","Euro":"eurollm-bench_latest.jsonl"}
avglen={}
for k,f in files.items():
    rows=json.load(open(os.path.join(BASE,"results",f)))
    ls=[len(r.get("answer","")) for r in rows if "answer" in r]
    avglen[k]=sum(ls)/len(ls)

# --- Aggregate ---
total={m:sum(v[1][m] for v in CASES.values()) for m in MODELS}
cats=sorted(set(c for c,_ in CASES.values()))
percat={m:{c:[] for c in cats} for m in MODELS}
for cid,(cat,sc) in CASES.items():
    for m in MODELS: percat[m][cat].append(sc[m])
percat_avg={m:{c:(sum(percat[m][c])/len(percat[m][c])) for c in cats} for m in MODELS}
disc={m:sum(DISC[c][m] for c in DISC) for m in MODELS}
NDISC=len(DISC)

# ---------- Chart 1: Gesamt ----------
fig,ax=plt.subplots(figsize=(7,4.2))
vals=[total[m] for m in MODELS]
bars=ax.bar([NAME[m] for m in MODELS],vals,color=[COL[m] for m in MODELS])
ax.set_ylabel("Punkte (max 18)"); ax.set_ylim(0,18)
ax.set_title("BalkanBench — Gesamtscore (18 Fälle, muttersprachlich bewertet)")
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+0.3,f"{v:.2f}",ha="center",fontweight="bold")
plt.tight_layout(); plt.savefig(f"{OUT}/01_gesamt.png",dpi=130); plt.close()

# ---------- Chart 2: pro Kategorie ----------
fig,ax=plt.subplots(figsize=(9,4.6))
x=np.arange(len(cats)); w=0.26
for i,m in enumerate(MODELS):
    ax.bar(x+(i-1)*w,[percat_avg[m][c] for c in cats],w,label=NAME[m],color=COL[m])
ax.set_xticks(x); ax.set_xticklabels(cats); ax.set_ylim(0,1.05)
ax.set_ylabel("ø Score (0–1)"); ax.set_title("BalkanBench — Kompetenz pro Kategorie")
ax.legend(fontsize=8); ax.grid(axis="y",alpha=.3)
plt.tight_layout(); plt.savefig(f"{OUT}/02_kategorien.png",dpi=130); plt.close()

# ---------- Chart 3: Sprach-/Schrift-Disziplin (Flaggschiff) ----------
fig,ax=plt.subplots(figsize=(7,4.2))
vals=[disc[m] for m in MODELS]
bars=ax.bar([NAME[m] for m in MODELS],vals,color=[COL[m] for m in MODELS])
ax.set_ylabel(f"eingehalten (max {NDISC})"); ax.set_ylim(0,NDISC+0.5)
ax.set_title("Sprach- & Schrift-Disziplin\n(Azbuka/Sprache auf Befehl korrekt — das Designziel)")
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+0.1,f"{v:.1f}/{NDISC}",ha="center",fontweight="bold")
plt.tight_layout(); plt.savefig(f"{OUT}/03_disziplin.png",dpi=130); plt.close()

# ---------- Chart 4: Verbosität (Effizienz lokal) ----------
fig,ax=plt.subplots(figsize=(7,4.2))
vals=[avglen[m] for m in MODELS]
bars=ax.bar([NAME[m] for m in MODELS],vals,color=[COL[m] for m in MODELS])
ax.set_ylabel("ø Antwortlänge (Zeichen)")
ax.set_title("Wortknappheit / Stoppverhalten\n(kürzer = besser für lokal + wenig RAM)")
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+30,f"{v:.0f}",ha="center",fontweight="bold")
plt.tight_layout(); plt.savefig(f"{OUT}/04_verbositaet.png",dpi=130); plt.close()

# ---------- Textbilanz ----------
print("GESAMT:", {m:round(total[m],2) for m in MODELS}, "/18")
print("DISZIPLIN:", {m:round(disc[m],1) for m in MODELS}, f"/{NDISC}")
print("ø LÄNGE:", {m:round(avglen[m]) for m in MODELS})
print("KATEGORIEN:")
for c in cats: print(f"  {c:14}", {m:round(percat_avg[m][c],2) for m in MODELS})
# Scores als JSON sichern
json.dump({"total":total,"percat":percat_avg,"disc":disc,"disc_n":NDISC,"avglen":avglen,
           "cases":{k:v[1] for k,v in CASES.items()}},
          open(f"{BASE}/results/scores.json","w"),ensure_ascii=False,indent=1)
print("Charts →", OUT)
