#!/usr/bin/env python3
"""05_kategorien_alle.png — per-Aufgabentyp, ALLE 8 Modelle (nicht nur der 3-Wege-Deep-dive).
Farbe nach Größenklasse: Zora orange · Generalisten 26-27B blau · dedizierte Balkan grau."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
BASE="/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench"
OUT=os.path.join(BASE,"results","charts"); os.makedirs(OUT,exist_ok=True)
ZC="#E8830C"; BIG="#4A90D9"; GREY="#9AA5B1"
sc=json.load(open(os.path.join(BASE,"results_matrix","scores.json")))
META={"zora_v1":("Zora v1 (8B)","zora"),"gemma4-26b":("Gemma-4 (26B)","big"),
 "qwen36-27b":("Qwen3.6 (27B)","big"),"salamandra":("Salamandra (7B)","ded"),
 "bggpt":("BgGPT (4B)","ded"),"eurollm-bench":("EuroLLM (9B)","ded"),
 "aya-expanse":("Aya Expanse (8B)","ded"),"yugogpt-bench":("YugoGPT (7B)","ded")}
COLC={"zora":ZC,"big":BIG,"ded":GREY}
AX=[("FACT","Facts"),("HALLU","Honesty"),("TEACH","Teaching"),
    ("REASON","Reasoning"),("INSTRUCT","Instruction"),("SCRIPT","Script")]
models=sorted(sc,key=lambda m:sum(sc[m][k][0] for k in ["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]),reverse=True)
names=[META[m][0] for m in models]; cols=[COLC[META[m][1]] for m in models]
fig,axes=plt.subplots(2,3,figsize=(15,8)); axes=axes.flatten()
for i,(key,title) in enumerate(AX):
    ax=axes[i]; vals=[sc[m][key][0] for m in models]; mx=sc[models[0]][key][1]
    ax.barh(names[::-1], vals[::-1], color=cols[::-1])
    ax.set_xlim(0,mx+0.4); ax.set_title(title, fontweight="bold", fontsize=12)
    for j,v in enumerate(vals[::-1]): ax.text(v+0.05,j,str(v),va="center",fontsize=8,fontweight="bold")
    if i%3!=0: ax.set_yticklabels([])
    ax.tick_params(labelsize=8); ax.spines[["top","right"]].set_visible(False)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=ZC,label="Zora (8B)"),Patch(color=BIG,label="general-purpose 26–27B"),
 Patch(color=GREY,label="dedicated Balkan models")],loc="lower center",ncol=3,fontsize=10,bbox_to_anchor=(0.5,-0.02))
fig.suptitle("BalkanBench — per task type, all 8 models (each cell max 6)", fontweight="bold", fontsize=14, y=1.0)
plt.tight_layout(rect=[0,0.03,1,0.98]); plt.savefig(f"{OUT}/05_kategorien_alle.png",dpi=130,bbox_inches="tight"); plt.close()
print("✓ 05_kategorien_alle.png — alle 8 Modelle, 6 Aufgabentypen")
