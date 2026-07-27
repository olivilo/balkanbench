#!/usr/bin/env python3
"""Ausführlicher Testlauf balkan-v3 (MLX) — Stärken/Schwächen über alle Sprachen,
beide Schriften, Homonyme, Kultur, Reasoning + Englisch-Leck-Kontrolle."""
import re, sys, json
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

MODEL = sys.argv[1] if len(sys.argv) > 1 else \
    "/Volumes/M4Data/Coding/DieEineKette-Workspace/balkan-llm/model/balkan-qwen3-8b-v3-2026-07-12/balkan-v3-mlx-4bit"
CYR = re.compile(r"[Ѐ-ӿ]"); LAT = re.compile(r"[A-Za-z]")
def strip_think(t): return re.sub(r"<think>.*?</think>", "", t or "", flags=re.S).strip()
def script(t):
    c,l=len(CYR.findall(t)),len(LAT.findall(t))
    return "azbuka" if c>l else ("latinica" if l>0 else "—")
EN=set("the and is are of a to in that with for this as be it".split())
def en_leak(t):
    w=re.findall(r"[a-zA-Z]+", t.lower());
    return sum(1 for x in w if x in EN)

PROBES=[
 ("SR-lat/nauka","sr","Objasni ukratko šta je fotosinteza.","latinica"),
 ("SR-azb/istorija","sr","Одговори ћирилицом: Ко је био Никола Тесла и по чему је познат?","azbuka"),
 ("SR-skripta/kontrola","sr","Napiši rečenicu 'Volim svoju zemlju' i latinicom i ćirilicom (azbukom).","-"),
 ("HR/jezik","hr","Objasni na hrvatskom: koja je razlika između 'tko' i 'što'?","latinica"),
 ("BS/kultura","bs","Ukratko na bosanskom: šta je sevdalinka?","latinica"),
 ("MK/nauka","mk","Одговори на македонски: што е гравитација?","azbuka"),
 ("SL/geografija","sl","Na slovenščini: katero je glavno mesto Slovenije in ob kateri reki leži?","latinica"),
 ("SQ/pojmovi","sq","Përgjigju shqip: çfarë është demokracia?","latinica"),
 ("SQ/istorija","sq","Përgjigju shqip: kush ishte Gjergj Kastrioti Skënderbeu?","latinica"),
 ("HOM/gore","sr","Objasni značenje svake reči 'gore' u: 'Gore gore gore gore nego dole.' Prevedi.","-"),
 ("HOM/kosa","sr","Šta sve može da znači reč 'kosa'? Navedi značenja.","-"),
 ("REASON/logika","sr","Ako svi mačke spavaju danju, a Miki je mačka, šta možemo zaključiti? Objasni kratko.","-"),
 ("KULT/knjizevnost","sr","Ko je napisao 'Na Drini ćuprija' i o čemu se radi?","-"),
 ("MATH/racun","hr","Trgovac kupi robu za 80 eura i proda za 100. Koliki je postotak zarade? Objasni.","-"),
]

m,tok=load(MODEL)
samp=make_sampler(temp=0.3)
rows=[]
for tag,lang,q,want in PROBES:
    msgs=[{"role":"user","content":q}]
    p=tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    raw=generate(m,tok,prompt=p,max_tokens=200,sampler=samp,verbose=False)
    ans=strip_think(raw)
    sc=script(ans); leak=en_leak(ans)
    flag=""
    if want in ("latinica","azbuka") and sc!=want: flag=f" ⚠SCHRIFT({sc}≠{want})"
    if leak>=4: flag+=f" ⚠EN-Leck({leak})"
    print(f"\n===== {tag}  [Schrift:{sc}{flag}] =====")
    print(f"F: {q}")
    print(f"A: {ans[:500]}")
    rows.append((tag,sc,leak,flag,ans))

print("\n\n########## KURZBILANZ ##########")
for tag,sc,leak,flag,ans in rows:
    print(f"{tag:22s} schrift={sc:8s} en={leak:2d} {'OK' if not flag else flag}")
