#!/usr/bin/env python3
"""EHRLICHER Härtetest balkan-v3 — echte Nutzaufgaben statt Wohlfühl-Wörter.
Teaching, mehrschrittiges Reasoning, Faktentreue (+Halluzinations-Fallen),
Tool-Calling, Instruktions-Befolgung, Langform. NUR v3 geladen (RAM-sicher)."""
import re, sys, json
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

MODEL="/Volumes/M4Data/Coding/DieEineKette-Workspace/balkan-llm/model/balkan-qwen3-8b-v3-2026-07-12/balkan-v3-mlx-4bit"
def strip_think(t): return re.sub(r"<think>.*?</think>","",t or "",flags=re.S).strip()

# (id, kategorie, prompt, was-korrekt-wäre)
PROBES=[
 ("TEACH-sq","Teaching","Nauči me 5 albanskih reči sa srpskim prevodom i po jednim primerom u rečenici. Formatiraj kao listu.",
   "5 echte alban. Wörter + korrekte Übersetzung + Beispielsatz"),
 ("TEACH-padezi","Teaching","Objasni početniku šta su padeži u srpskom jeziku. Daj primer za nominativ i akuzativ sa rečju 'knjiga'.",
   "korrekte Erklärung Kasus + knjiga/knjigu"),
 ("MULTI-math","Reasoning","Majica sa sniženjem od 25% košta 1200 dinara. Kolika je bila cena pre sniženja? Reši korak po korak.",
   "1200/0.75 = 1600 din"),
 ("LOGIC","Reasoning","Ako je Ana starija od Bojane, a Bojana starija od Vesne, ko je najmlađi? Objasni ukratko.",
   "Vesna (transitiv)"),
 ("FACT-avlija","Faktentreue","Ko je napisao roman 'Prokleta avlija'?",
   "Ivo Andrić"),
 ("FACT-skopje","Faktentreue","Koji je glavni grad Severne Makedonije i na kojoj reci leži? Kratko.",
   "Skoplje, Vardar"),
 ("FACT-tesla","Faktentreue","Gde je rođen Nikola Tesla (mesto i država)? Kratko.",
   "Smiljan, Hrvatska (tada Austrougarska)"),
 ("HALLU-trap","Faktentreue","Ko je bio srpski pesnik Milutin Vukašinović i kada je živeo?",
   "FALLE: existiert wohl nicht → sollte Unwissen zugeben, NICHT erfinden"),
 ("LONGFORM","Langform","Napiši kratak, koherentan pasus od 5 rečenica o značaju čitanja za decu, na srpskom.",
   "5 kohärente Sätze, kein Rambeln/Wiederholen"),
 ("INSTRUCT","Instruktion","Nabroji TAČNO tri razloga zašto je voda važna, svaki u jednoj rečenici, na srpskom ĆIRILICOM.",
   "genau 3 Punkte, Azbuka, je 1 Satz"),
 ("TEACH-hr","Teaching","Objasni na hrvatskom razliku između 'č' i 'ć' u izgovoru, s po jednim primjerom.",
   "korrekte Aussprache-Erklärung + Beispiele (npr. čokolada / ćup)"),
]

# Tool-Calling separat (Qwen3-Tool-Schema via chat_template tools=)
TOOLS=[{"type":"function","function":{"name":"get_weather",
        "description":"Vrati trenutno vreme za grad.",
        "parameters":{"type":"object","properties":{"grad":{"type":"string","description":"ime grada"}},"required":["grad"]}}}]

m,tok=load(MODEL)
samp=make_sampler(temp=0.3)
print("MODELL GELADEN\n"+"="*70)

for pid,cat,q,rub in PROBES:
    msgs=[{"role":"user","content":q}]
    p=tok.apply_chat_template(msgs,add_generation_prompt=True,tokenize=False)
    ans=strip_think(generate(m,tok,prompt=p,max_tokens=350,sampler=samp,verbose=False))
    print(f"\n##### {pid}  [{cat}] #####")
    print("F:", q)
    print("KORREKT:", rub)
    print("A:", ans[:600])

# Tool-Calling-Probe
print("\n"+"="*70+"\n##### TOOL-CALL  [Agentic] #####")
q="Kakvo je vreme danas u Beogradu?"
try:
    p=tok.apply_chat_template([{"role":"user","content":q}],tools=TOOLS,add_generation_prompt=True,tokenize=False)
    ans=generate(m,tok,prompt=p,max_tokens=200,sampler=samp,verbose=False)
    print("F:", q)
    print("KORREKT: valider tool_call für get_weather(grad='Beograd')")
    print("A (roh, mit evtl. tool-tags):", ans[:500])
except Exception as e:
    print("Tool-Template-Fehler:", str(e)[:120])
print("\n"+"="*70+"\nFERTIG")
