#!/usr/bin/env python3
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, os, json
OUT="/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench/results/charts"; os.makedirs(OUT,exist_ok=True)
LANGS=["sr","hr","bs","mk","sl","sq"]
CATS=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
# muttersprachliche Bewertung der 36 Antworten (0..1)
S={
"sr":[0.0,0.0,0.9,0.0,0.5,0.6],
"hr":[0.0,0.0,0.8,1.0,0.5,0.6],
"bs":[0.0,0.0,0.75,1.0,0.4,0.55],
"mk":[0.0,0.0,0.85,1.0,0.55,0.65],
"sl":[0.0,0.0,0.2,1.0,0.7,0.4],
"sq":[1.0,0.0,0.0,1.0,0.6,0.45],
}
M=np.array([S[l] for l in LANGS])
fig,ax=plt.subplots(figsize=(9,5))
im=ax.imshow(M,cmap="RdYlGn",vmin=0,vmax=1,aspect="auto")
ax.set_xticks(range(len(CATS))); ax.set_xticklabels(CATS)
ax.set_yticks(range(len(LANGS))); ax.set_yticklabels([l.upper() for l in LANGS])
for i in range(len(LANGS)):
    for j in range(len(CATS)):
        ax.text(j,i,f"{M[i,j]:.2f}",ha="center",va="center",
                color="black",fontweight="bold",fontsize=9)
ax.set_title("Härtetest-Matrix balkan-v3 — Sprache × Aufgabe (0=schlecht, 1=gut)")
# Mittelwerte
lang_avg=M.mean(axis=1); cat_avg=M.mean(axis=0)
fig.colorbar(im,ax=ax,shrink=0.8,label="Score")
plt.tight_layout(); plt.savefig(f"{OUT}/06_matrix_heatmap.png",dpi=130); plt.close()
print("GESAMT:", f"{M.mean():.2f}")
print("pro Sprache:", {l:round(float(a),2) for l,a in zip(LANGS,lang_avg)})
print("pro Kategorie:", {c:round(float(a),2) for c,a in zip(CATS,cat_avg)})
json.dump({"lang_avg":{l:float(a) for l,a in zip(LANGS,lang_avg)},
           "cat_avg":{c:float(a) for c,a in zip(CATS,cat_avg)},"total":float(M.mean())},
          open("/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench/results/matrix_scores.json","w"),indent=1)
print("heatmap -> 06_matrix_heatmap.png")
