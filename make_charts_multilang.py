#!/usr/bin/env python3
"""make_charts_multilang.py — Overall + Honesty per language, 8 models, size-class colors."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BASE="/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench"
CH=os.path.join(BASE,"results","charts")
ZC="#E8830C"; BIG="#4A90D9"; GREY="#9AA5B1"
sc=json.load(open(os.path.join(BASE,"results_matrix","scores.json")))
META={"zora_v1":("Zora v1 (8B)","zora"),"gemma4-26b":("Gemma-4 (26B)","big"),
 "qwen36-27b":("Qwen3.6 (27B)","big"),"salamandra":("Salamandra (7B)","ded"),
 "bggpt":("BgGPT (4B)","ded"),"eurollm-bench":("EuroLLM (9B)","ded"),
 "aya-expanse":("Aya Expanse (8B)","ded"),"yugogpt-bench":("YugoGPT (7B)","ded")}
COLC={"zora":ZC,"big":BIG,"ded":GREY}
ORDER=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
models=sorted(sc,key=lambda m:sum(sc[m][k][0] for k in ORDER),reverse=True)
def tot(m): return sum(sc[m][k][0] for k in ORDER)
def nm(m): return META[m][0]
def col(m): return COLC[META[m][1]]

# (overall_title, overall_xlabel, honesty_title, honesty_ylabel, honesty_sub, legend[zora,big,ded])
T={
"sr-lat":("BalkanBench — ukupno (6 jezika × 6 zadataka)","Ukupno poena (maks. 36)",
 "Iskrenost: odbiti izmišljene osobe umesto izmišljanja biografija","Iskrena odbijanja (maks. 6)",
 "Zora (8B) izjednačena s modelom od 26B na 6/6; svi namenski balkanski modeli: 0/6.",
 ("Zora (8B)","opšti 26–27B","namenski balkanski")),
"sr-azb":("БалканБенч — укупно (6 језика × 6 задатака)","Укупно поена (макс. 36)",
 "Искреност: одбити измишљене особе уместо измишљања биографија","Искрена одбијања (макс. 6)",
 "Зора (8Б) изједначена с моделом од 26Б на 6/6; сви наменски балкански модели: 0/6.",
 ("Зора (8Б)","општи 26–27Б","наменски балкански")),
"hr":("BalkanBench — ukupno (6 jezika × 6 zadataka)","Ukupno bodova (maks. 36)",
 "Iskrenost: odbiti izmišljene osobe umjesto izmišljanja biografija","Iskrena odbijanja (maks. 6)",
 "Zora (8B) izjednačena s modelom od 26B na 6/6; svi namjenski balkanski modeli: 0/6.",
 ("Zora (8B)","opći 26–27B","namjenski balkanski")),
"bs":("BalkanBench — ukupno (6 jezika × 6 zadataka)","Ukupno bodova (maks. 36)",
 "Iskrenost: odbiti izmišljene osobe umjesto izmišljanja biografija","Iskrena odbijanja (maks. 6)",
 "Zora (8B) izjednačena s modelom od 26B na 6/6; svi namjenski balkanski modeli: 0/6.",
 ("Zora (8B)","opći 26–27B","namjenski balkanski")),
"mk":("БалканБенч — вкупно (6 јазици × 6 задачи)","Вкупно поени (макс. 36)",
 "Искреност: одбивање измислени лица наместо измислување биографии","Искрени одбивања (макс. 6)",
 "Зора (8Б) изедначена со моделот од 26Б на 6/6; сите наменски балкански модели: 0/6.",
 ("Зора (8Б)","општи 26–27Б","наменски балкански")),
"sl":("BalkanBench — skupno (6 jezikov × 6 nalog)","Skupaj točk (najv. 36)",
 "Iskrenost: zavrniti izmišljene osebe namesto izmišljanja biografij","Iskrene zavrnitve (najv. 6)",
 "Zora (8B) izenačena z modelom 26B pri 6/6; vsi namenski balkanski modeli: 0/6.",
 ("Zora (8B)","splošni 26–27B","namenski balkanski")),
"sq":("BalkanBench — gjithsej (6 gjuhë × 6 detyra)","Pikë gjithsej (maks. 36)",
 "Ndershmëria: refuzimi i personave të trilluar në vend të trillimit të biografive","Refuzime të ndershme (maks. 6)",
 "Zora (8B) baras me modelin 26B në 6/6; të gjitha modelet e dedikuara ballkanike: 0/6.",
 ("Zora (8B)","të përgjithshme 26–27B","të dedikuara ballkanike")),
}
for lang,(ot,ox,ht,hy,hs,leg) in T.items():
    d=os.path.join(CH,lang); os.makedirs(d,exist_ok=True)
    # overall (horizontal, size labels, class colors)
    fig,ax=plt.subplots(figsize=(8.6,5))
    vals=[tot(m) for m in models]
    ax.barh([nm(m) for m in models][::-1], vals[::-1], color=[col(m) for m in models][::-1])
    ax.set_xlim(0,37); ax.set_xlabel(ox); ax.set_title(ot, fontweight="bold")
    for i,v in enumerate(vals[::-1]): ax.text(v+0.4,i,str(v),va="center",fontweight="bold")
    ax.legend(handles=[Patch(color=ZC,label=leg[0]),Patch(color=BIG,label=leg[1]),Patch(color=GREY,label=leg[2])],
     loc="lower right",fontsize=8,framealpha=.9)
    ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); plt.savefig(f"{d}/01_gesamt.png",dpi=130); plt.close()
    # honesty
    fig,ax=plt.subplots(figsize=(9,4.8))
    hv=[sc[m]["HALLU"][0] for m in models]
    ax.bar([nm(m) for m in models],hv,color=[col(m) for m in models])
    ax.set_ylim(0,6.6); ax.set_ylabel(hy); ax.set_title(ht, fontweight="bold", fontsize=10.5)
    for i,v in enumerate(hv): ax.text(i,v+0.1,str(v),ha="center",fontweight="bold")
    ax.text(0.5,-0.34,hs,transform=ax.transAxes,ha="center",fontsize=8,style="italic",color="#555")
    ax.spines[["top","right"]].set_visible(False); plt.xticks(rotation=20,ha="right"); plt.tight_layout(); plt.savefig(f"{d}/02_ehrlichkeit.png",dpi=130); plt.close()
    print("✓",lang)
print("localized 8-model charts →", CH,"/<lang>/")
