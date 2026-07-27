#!/usr/bin/env python3
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, os, json
OUT="/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench/results/charts"; os.makedirs(OUT,exist_ok=True)
# (id, kategorie, score, kurz-urteil)
R=[
 ("TEACH-sq","Teaching",0.4,"Format gut, 2/5 alban. Wörter falsch (fshehi/leshim)"),
 ("TEACH-padezi","Teaching",0.7,"7 Kasus korrekt, Akkusativ-Beispiel holprig"),
 ("TEACH-hr","Teaching",0.2,"č/ć-Erklärung falsch, 'ćovjek' kein Wort"),
 ("MULTI-math","Reasoning",0.7,"1600 din korrekt, aber KEINE Schritte gezeigt"),
 ("LOGIC","Reasoning",1.0,"Vesna korrekt, klar erklärt"),
 ("FACT-avlija","Faktentreue",0.0,"'Josip Šović' statt Ivo Andrić — halluziniert"),
 ("FACT-skopje","Faktentreue",1.0,"Skopje/Vardar korrekt"),
 ("FACT-tesla","Faktentreue",0.25,"Smiljan ok, aber 'u Srbiji' falsch (=Hrvatska)"),
 ("HALLU-trap","Faktentreue",0.0,"ERFINDET Bio für nicht-existenten Dichter (gefährlich)"),
 ("LONGFORM","Langform",0.8,"5 kohärente Sätze, stoppt, kleine Grammatikslips"),
 ("INSTRUCT","Instruktion",0.9,"genau 3, Azbuka, je 1 Satz — sehr gut"),
 ("TOOL-CALL","Tool/Agentic",1.0,"valider <tool_call> get_weather(Beograd)"),
]
cats={}
for _,c,s,_ in R: cats.setdefault(c,[]).append(s)
catavg={c:sum(v)/len(v) for c,v in cats.items()}
order=["Teaching","Faktentreue","Reasoning","Instruktion","Langform","Tool/Agentic"]
vals=[catavg[c] for c in order]
col=["#c62828" if v<0.5 else ("#f9a825" if v<0.75 else "#2e7d32") for v in vals]
fig,ax=plt.subplots(figsize=(9,4.6))
b=ax.bar(order,vals,color=col)
ax.set_ylim(0,1.05); ax.set_ylabel("ø Score (0–1)")
ax.set_title("Härtetest balkan-v3 — echte Nutzaufgaben (ehrlich)\nrot<0.5  gelb<0.75  grün≥0.75")
for bar,v in zip(b,vals): ax.text(bar.get_x()+bar.get_width()/2,v+0.02,f"{v:.2f}",ha="center",fontweight="bold")
ax.grid(axis="y",alpha=.3); plt.tight_layout(); plt.savefig(f"{OUT}/05_hardtest.png",dpi=130); plt.close()
total=sum(s for _,_,s,_ in R)/len(R)
print(f"GESAMT Härtetest: {total:.2f} / 1.0  ({total*100:.0f}%)")
for c in order: print(f"  {c:14} {catavg[c]:.2f}")
json.dump({"total":total,"catavg":catavg,"rows":[{"id":i,"cat":c,"score":s,"note":n} for i,c,s,n in R]},
          open("/Volumes/M4Data/Coding/DieEineKette-Workspace/balkanbench/results/hardscores.json","w"),ensure_ascii=False,indent=1)
print("chart -> 05_hardtest.png")
