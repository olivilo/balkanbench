#!/usr/bin/env python3
"""make_charts_en.py — English charts, 8 models, honest size-class framing.
§1 release matrix (8 models) + §2 3-way deep-dive + §3 evolution."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE="/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench"
OUT=os.path.join(BASE,"results","charts"); os.makedirs(OUT,exist_ok=True)
ZC="#E8830C"; BIG="#4A90D9"; GREY="#9AA5B1"   # Zora orange · big-generalists blue · Balkan-dedicated grey

sc=json.load(open(os.path.join(BASE,"results_matrix","scores.json")))
# name (with size) + class: zora / big (26-27B generalist) / dedicated (Balkan)
META={
 "zora_v1":("Zora v1 (8B)","zora"),
 "gemma4-26b":("Gemma-4 (26B)","big"),
 "qwen36-27b":("Qwen3.6 (27B)","big"),
 "salamandra":("Salamandra (7B)","ded"),
 "bggpt":("BgGPT (4B)","ded"),
 "eurollm-bench":("EuroLLM (9B)","ded"),
 "aya-expanse":("Aya Expanse (8B)","ded"),
 "yugogpt-bench":("YugoGPT (7B)","ded"),
}
COLC={"zora":ZC,"big":BIG,"ded":GREY}
ORDER=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
AX_EN={"FACT":"Facts","HALLU":"Honesty","TEACH":"Teaching","REASON":"Reasoning",
 "INSTRUCT":"Instruction","LONGFORM":"Long-form","SCRIPT":"Script"}
models=sorted(sc,key=lambda m:sum(sc[m][k][0] for k in ORDER),reverse=True)
def tot(m): return sum(sc[m][k][0] for k in ORDER)
def nm(m): return META[m][0]
def col(m): return COLC[META[m][1]]

# 1) overall — horizontal, size in labels, class colors
fig,ax=plt.subplots(figsize=(8.6,5))
vals=[tot(m) for m in models]
bars=ax.barh([nm(m) for m in models][::-1], vals[::-1], color=[col(m) for m in models][::-1])
ax.set_xlim(0,37); ax.set_xlabel("Total points (max. 36)")
ax.set_title("BalkanBench — overall (6 languages × 6 tasks)", fontweight="bold")
for b,v in zip(bars,vals[::-1]): ax.text(v+0.4,b.get_y()+b.get_height()/2,str(v),va="center",fontweight="bold")
# legend
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=ZC,label="Zora (8B)"),Patch(color=BIG,label="general-purpose 26–27B"),
 Patch(color=GREY,label="dedicated Balkan models")],loc="lower right",fontsize=8,framealpha=.9)
ax.text(0.0,-0.14,"Zora (8B) matches 3× larger generalists and leads its own class — comprehension over size.",
 transform=ax.transAxes,fontsize=8.5,style="italic",color="#555")
ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); plt.savefig(f"{OUT}/01_gesamt.png",dpi=130); plt.close()

# 2) honesty
fig,ax=plt.subplots(figsize=(9,4.7))
hv=[sc[m]["HALLU"][0] for m in models]
bars=ax.bar([nm(m) for m in models],hv,color=[col(m) for m in models])
ax.set_ylim(0,6.6); ax.set_ylabel("Honest refusals (max. 6)")
ax.set_title("Honesty: refusing invented people instead of fabricating biographies", fontweight="bold")
for b,v in zip(bars,hv): ax.text(b.get_x()+b.get_width()/2,v+0.1,str(v),ha="center",fontweight="bold")
ax.text(0.5,-0.30,"Zora (8B) ties the 26B model at 6/6; every dedicated Balkan model scores 0/6.",
 transform=ax.transAxes,ha="center",fontsize=9,style="italic",color="#555")
ax.spines[["top","right"]].set_visible(False); plt.xticks(rotation=20,ha="right"); plt.tight_layout(); plt.savefig(f"{OUT}/02_ehrlichkeit.png",dpi=130); plt.close()

# 3) heatmap 8×7
cols_ax=ORDER+["SCRIPT"]
M=np.array([[sc[m][k][0]/sc[m][k][1] for k in cols_ax] for m in models])
fig,ax=plt.subplots(figsize=(8.8,5.2))
im=ax.imshow(M,cmap="YlOrBr",vmin=0,vmax=1,aspect="auto")
ax.set_xticks(range(len(cols_ax))); ax.set_xticklabels([AX_EN[k] for k in cols_ax])
ax.set_yticks(range(len(models))); ax.set_yticklabels([nm(m) for m in models])
for i in range(len(models)):
    for j in range(len(cols_ax)):
        v=sc[models[i]][cols_ax[j]]
        ax.text(j,i,f"{v[0]}/{v[1]}",ha="center",va="center",color="white" if M[i,j]>0.6 else "#333",fontsize=8,fontweight="bold")
ax.set_title("BalkanBench — capabilities per model (share correct)", fontweight="bold")
plt.colorbar(im,fraction=0.025,pad=0.02); plt.tight_layout(); plt.savefig(f"{OUT}/03_heatmap.png",dpi=130); plt.close()

# 4) speed — only the 6 locally-tested models (same hardware); footnote about the 2 cloud ones
SPEED={"Zora v1":(19.6,19.6),"YugoGPT":(22.6,23.0),"EuroLLM":(17.8,18.5),
 "Aya Expanse":(19.4,19.3),"BgGPT":(36.6,36.8),"Salamandra":(16.1,16.1)}
labels=list(SPEED); lat=[SPEED[l][0] for l in labels]; azb=[SPEED[l][1] for l in labels]
x=np.arange(len(labels)); w=0.38
fig,ax=plt.subplots(figsize=(8.6,4.6))
ax.bar(x-w/2,lat,w,label="Latin",color="#4A90D9")
ax.bar(x+w/2,azb,w,label="Azbuka (Cyrillic)",color=ZC)
ax.set_xticks(x); ax.set_xticklabels(labels,rotation=15); ax.set_ylabel("Tokens / second")
ax.set_title("Speed per script — no Azbuka penalty for Zora", fontweight="bold")
ax.text(0.5,-0.26,"Same Mac hardware, one model at a time. (Gemma-26B / Qwen-27B were run on cloud GPU → not speed-comparable.)",
 transform=ax.transAxes,ha="center",fontsize=8,style="italic",color="#666")
ax.legend(); ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); plt.savefig(f"{OUT}/04_speed.png",dpi=130); plt.close()

# ===== §2 3-way deep-dive (unchanged, English) =====
MODELS=["v3","Yugo","Euro"]; NAME3={"v3":"Zora","Yugo":"YugoGPT-7B","Euro":"EuroLLM-9B"}
COL3={"v3":ZC,"Yugo":GREY,"Euro":"#c7cdd4"}
CASES={"gore-4":("Homonym",{"v3":.5,"Yugo":.5,"Euro":.25}),"grad":("Homonym",{"v3":.5,"Yugo":.5,"Euro":.25}),
 "kosa":("Homonym",{"v3":.5,"Yugo":.25,"Euro":.5}),"para":("Homonym",{"v3":.5,"Yugo":.25,"Euro":.5}),
 "mk-homonym":("Homonym",{"v3":.75,"Yugo":.25,"Euro":0}),"ek-ijek":("Dialect",{"v3":1,"Yugo":.75,"Euro":.25}),
 "sl-dvojina":("Dialect",{"v3":.5,"Yugo":0,"Euro":1}),"sq-def":("Dialect",{"v3":.5,"Yugo":0,"Euro":0}),
 "bkms-lex":("Lang.sep.",{"v3":1,"Yugo":0,"Euro":0}),"bread-3":("Lang.sep.",{"v3":1,"Yugo":.25,"Euro":0}),
 "false-obraz":("Lang.sep.",{"v3":.75,"Yugo":.5,"Euro":.25}),"translit":("Script",{"v3":.75,"Yugo":0,"Euro":0}),
 "azbuka-answer":("Script",{"v3":1,"Yugo":0,"Euro":.5}),"cnr-sz":("Script",{"v3":.5,"Yugo":1,"Euro":.5}),
 "proverb-vuk":("Culture",{"v3":1,"Yugo":1,"Euro":1}),"slava":("Culture",{"v3":.5,"Yugo":.75,"Euro":.75}),
 "idiom-mk":("Culture",{"v3":1,"Yugo":.75,"Euro":.5}),"reason-inlang":("Reasoning",{"v3":.75,"Yugo":.75,"Euro":.5})}
DISC={"azbuka-answer":{"v3":1,"Yugo":0,"Euro":.5},"translit":{"v3":1,"Yugo":0,"Euro":0},
 "mk-homonym":{"v3":1,"Yugo":0,"Euro":0},"idiom-mk":{"v3":1,"Yugo":0,"Euro":0},
 "reason-inlang":{"v3":0,"Yugo":0,"Euro":0},"sq-def":{"v3":1,"Yugo":0,"Euro":0},"sl-dvojina":{"v3":1,"Yugo":0,"Euro":1}}
files={"v3":"balkan-v3-bench_latest.jsonl","Yugo":"yugogpt-bench_latest.jsonl","Euro":"eurollm-bench_latest.jsonl"}
avglen={}
for k,f in files.items():
    rows=json.load(open(os.path.join(BASE,"results",f))); ls=[len(r.get("answer","")) for r in rows if "answer" in r]
    avglen[k]=sum(ls)/len(ls)
cats=sorted(set(c for c,_ in CASES.values()))
percat={m:{c:[] for c in cats} for m in MODELS}
for cid,(cat,scv) in CASES.items():
    for m in MODELS: percat[m][cat].append(scv[m])
percat_avg={m:{c:sum(percat[m][c])/len(percat[m][c]) for c in cats} for m in MODELS}
disc={m:sum(DISC[c][m] for c in DISC) for m in MODELS}; NDISC=len(DISC)
fig,ax=plt.subplots(figsize=(9,4.6)); x=np.arange(len(cats)); w=0.26
for i,m in enumerate(MODELS): ax.bar(x+(i-1)*w,[percat_avg[m][c] for c in cats],w,label=NAME3[m],color=COL3[m])
ax.set_xticks(x); ax.set_xticklabels(cats); ax.set_ylim(0,1.05); ax.set_ylabel("avg. score (0–1)")
ax.set_title("BalkanBench — competence per category (3-way deep-dive)", fontweight="bold")
ax.legend(fontsize=8); ax.grid(axis="y",alpha=.3); plt.tight_layout(); plt.savefig(f"{OUT}/02_kategorien.png",dpi=130); plt.close()
fig,ax=plt.subplots(figsize=(7,4.2)); vals=[disc[m] for m in MODELS]
bars=ax.bar([NAME3[m] for m in MODELS],vals,color=[COL3[m] for m in MODELS])
ax.set_ylabel(f"kept (max {NDISC})"); ax.set_ylim(0,NDISC+0.5)
ax.set_title("Language & script discipline\n(correct Azbuka/language on command)", fontweight="bold")
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+0.1,f"{v:.1f}/{NDISC}",ha="center",fontweight="bold")
plt.tight_layout(); plt.savefig(f"{OUT}/03_disziplin.png",dpi=130); plt.close()
fig,ax=plt.subplots(figsize=(7,4.2)); vals=[avglen[m] for m in MODELS]
bars=ax.bar([NAME3[m] for m in MODELS],vals,color=[COL3[m] for m in MODELS])
ax.set_ylabel("avg. answer length (chars)")
ax.set_title("Conciseness / stopping behaviour\n(shorter = better for local, low-RAM use)", fontweight="bold")
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+30,f"{v:.0f}",ha="center",fontweight="bold")
plt.tight_layout(); plt.savefig(f"{OUT}/04_verbositaet.png",dpi=130); plt.close()

# ===== §3 evolution =====
EV={"Honesty":[0.0,1.0,0.85,1.0],"Facts":[0.17,0.30,0.30,0.33],"Reasoning":[0.83,0.85,0.90,0.83],
 "Teaching":[0.58,0.70,0.65,1.0],"Language/script":[0.90,0.88,0.85,1.0]}
vers=["v3","v4","v5","v6"]
fig,ax=plt.subplots(figsize=(8,4.6))
for lab,ys in EV.items(): ax.plot(vers,ys,marker="o",linewidth=2,label=lab)
ax.set_ylim(0,1.08); ax.set_ylabel("score (0–1)")
ax.set_title("Zora's evolution across versions (v3 → v6)", fontweight="bold")
ax.legend(fontsize=8,ncol=2); ax.grid(alpha=.3)
ax.annotate("honesty breakthrough (v4)",xy=("v4",1.0),xytext=("v4",0.55),fontsize=8,ha="center",arrowprops=dict(arrowstyle="->",color="#888"))
plt.tight_layout(); plt.savefig(f"{OUT}/07_evolution.png",dpi=130); plt.close()
print("EN charts (8 models) written to", OUT)
