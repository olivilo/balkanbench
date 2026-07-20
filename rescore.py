#!/usr/bin/env python3
"""rescore.py — bewertet ALLE results_matrix/<model>.json robust neu → scores.json + matrix_scores.md.
Achsen: FACT(name), HALLU(Ehrlichkeit/Ablehnung), TEACH/LONGFORM(lang+script), REASON(Zahl),
INSTRUCT(script), SCRIPT(Schrift über alle Antworten)."""
import json, re, glob, collections, os
BASE=os.path.dirname(os.path.abspath(__file__))
CYR=re.compile(r"[Ѐ-ӿ]"); LAT=re.compile(r"[A-Za-zČčĆćŽžŠšĐđ]")
ORDER=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
REF={("sr","FACT"):["andrić","andric"],("hr","FACT"):["krleža","krleza"],
 ("bs","FACT"):["selimović","selimovic","meša","mesa"],("mk","FACT"):["андреевски"],
 ("sl","FACT"):["levstik"],("sq","FACT"):["kadare"],
 ("sr","REASON"):["150"],("hr","REASON"):["24"],("bs","REASON"):["3"],
 ("mk","REASON"):["50"],("sl","REASON"):["60"],("sq","REASON"):["20"]}
IDK=["ne postoji","ne mogu","nisam siguran","nema podataka","ne znam","ne raspolažem","nemam podataka",
 "nemam pouzdan","ne mogu da potvrd","ne mogu potvrd","neću da izmišlj","neću izmišlj","ne obstaja",
 "ne poznam","nisem prepričan","nimam podatk","nimam zanesljiv","ne najdem","si ne bom izmišlj",
 "ne bom izmišlj","nuk ekziston","nuk kam","nuk jam i sigurt","nuk gjej","nuk njoh","nuk mund të konfirm",
 "nuk do të shpik","не постои","не знам","немам податоц","немам сигурни","не сум сигурен","не располагам",
 "не можам да потврд","не ќе измисл","izmišljen","fiktiv","greš","priznati","radije ću priznati",
 "ne odgovara stvarn","nažalost","ne postoji široko","ne postoji poznat","mešali","мешали","zapravo",
 "nije postojao","не постои","nuk ekziston një","ne obstaja","majlico","ni znan","verjetno gre za"]
def want_script(lang,task):
    if lang=="mk": return "azb"
    if (lang,task)==("sr","INSTRUCT"): return "azb"
    return "lat"
def score(lang,task,ans):
    a=ans.lower(); cyr=len(CYR.findall(ans)); lat=len(LAT.findall(ans))
    ws=want_script(lang,task); scr=(cyr>lat) if ws=="azb" else (lat>=cyr)
    if task=="FACT": s=1 if any(r in a for r in REF.get((lang,task),[])) else 0
    elif task=="HALLU": s=1 if any(k in a for k in IDK) else 0
    elif task=="REASON": s=1 if any(r in a for r in REF.get((lang,task),[])) else 0
    elif task=="INSTRUCT": s=1 if scr else 0
    else: s=1 if len(ans.strip())>20 and scr else 0
    return s, scr
rows_out={}
for jf in glob.glob(f"{BASE}/results_matrix/*.json"):
    model=os.path.basename(jf)[:-5]
    if model=="scores": continue
    d=json.load(open(jf))
    if not isinstance(d,list): continue
    axis=collections.defaultdict(lambda:[0,0]); scr=[0,0]
    for r in d:
        s,sc=score(r["lang"],r["task"],r.get("answer",""))
        axis[r["task"]][0]+=s; axis[r["task"]][1]+=1; scr[0]+=int(sc); scr[1]+=1
    rows_out[model]={k:tuple(axis[k]) for k in ORDER}; rows_out[model]["SCRIPT"]=tuple(scr)
def tot(m): return sum(rows_out[m][k][0] for k in ORDER)
order=sorted(rows_out,key=tot,reverse=True)
cols=ORDER+["SCRIPT"]
lines=["# Härtetest-Matrix — Scores (8 Modelle, je 6 Sprachen)\n",
 "| Modell | "+" | ".join(cols)+" | Σ |","|"+"---|"*(len(cols)+2)]
for m in order:
    sc=rows_out[m]; t=tot(m); mx=sum(sc[k][1] for k in ORDER)
    lines.append(f"| {m} | "+" | ".join(f"{sc[k][0]}/{sc[k][1]}" for k in cols)+f" | **{t}/{mx}** |")
open(f"{BASE}/results_matrix/matrix_scores.md","w").write("\n".join(lines)+"\n")
json.dump(rows_out,open(f"{BASE}/results_matrix/scores.json","w"),indent=1)
print("\n".join(lines))
