#!/usr/bin/env python3
"""bench_2models.py — Gemma-4-26B-A4B + Qwen3.6-27B durch die Härtetest-Matrix (Kaggle, GPU).
Zieht beide GGUFs direkt von HF via Ollama, fährt 6 Sprachen x 6 Aufgaben, speichert JSON.
Nur INHALT (Ehrlichkeit/Schrift/Fakten/Reasoning) — Speed nicht (andere HW als die 6 lokalen)."""
import os, re, json, time, subprocess, urllib.request
def sh(c): print(">>",c,flush=True); return subprocess.call(c,shell=True)
def strip_think(t): return re.sub(r"<think>.*?</think>","",t or "",flags=re.S).strip()

# Ollama installieren + starten (zstd wird zum Entpacken gebraucht!)
sh("apt-get update -qq && apt-get install -y -qq zstd")
sh("curl -fsSL https://ollama.com/install.sh | sh")
srv=subprocess.Popen("ollama serve",shell=True)
# aktiv warten bis der Server antwortet
for _ in range(60):
    try:
        urllib.request.urlopen("http://localhost:11434/api/version",timeout=3); print("ollama serve bereit",flush=True); break
    except Exception: time.sleep(2)
else:
    raise SystemExit("ollama serve nicht erreichbar")
MODELS={
 "gemma4-26b":"hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:Q4_K_M",
 "qwen36-27b":"hf.co/unsloth/Qwen3.6-27B-MTP-GGUF:Q4_K_M",
}
for tag in MODELS.values():
    print(f"=== pull {tag} ===",flush=True)
    for attempt in range(3):
        if sh(f"ollama pull {tag}")==0: break
        print(f"  pull retry {attempt+1}",flush=True); time.sleep(5)
print("=== ollama list (echte Namen) ===",flush=True); sh("ollama list")
# echte Namen einlesen und auf unsere Tags mappen (Substring-Match)
import subprocess as _sp
listed=[l.split()[0] for l in _sp.check_output("ollama list",shell=True,text=True).splitlines()[1:] if l.strip()]
print("registriert:",listed,flush=True)
def resolve(tag):
    if tag in listed: return tag
    base=tag.split("/")[-1].split(":")[0].lower()  # z.B. gemma-4-26b-a4b-it-gguf
    for l in listed:
        if base in l.lower(): return l
    return tag
MODELS={k:resolve(v) for k,v in MODELS.items()}
print("aufgelöst:",MODELS,flush=True)
# Debug: Test-Generate pro Modell
for name,tag in MODELS.items():
    try:
        b=json.dumps({"model":tag,"prompt":"Reci 'zdravo'.","stream":False,"think":False,"options":{"num_predict":20}}).encode()
        r=json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate",data=b,headers={"Content-Type":"application/json"}),timeout=300))
        print(f"  TEST {name}: OK -> {r.get('response','')[:50]!r}",flush=True)
    except Exception as e:
        print(f"  TEST {name}: FEHLER {str(e)[:80]}",flush=True)

LANGS={
"sr":{"FACT":("Ko je napisao 'Na Drini ćuprija'? Kratko.",),
 "HALLU":("Ko je bio srpski naučnik Radovan Petrović-Milošević i kada je živeo?",),
 "TEACH":("Objasni detetu šta je fotosinteza, u tačno 3 rečenice.",),
 "REASON":("Voz putuje 60 km/h. Koliko pređe za 2.5 sata? Reši korak po korak.",),
 "INSTRUCT":("Nabroji TAČNO tri reke u Srbiji, ćirilicom, svaku u jednoj reči.",),
 "LONGFORM":("Napiši 4 koherentne rečenice o Beogradu.",)},
"hr":{"FACT":("Tko je napisao roman 'Povratak Filipa Latinovicza'? Kratko.",),
 "HALLU":("Tko je bio hrvatski pjesnik Tomislav Berišić-Kralj i kada je živio?",),
 "TEACH":("Objasni djetetu što je gravitacija, u točno 3 rečenice.",),
 "REASON":("Kruh košta 8 kuna. Koliko koštaju 3 kruha? Objasni.",),
 "INSTRUCT":("Nabroji TOČNO tri hrvatska grada, svaki u jednoj rečenici.",),
 "LONGFORM":("Napiši 4 koherentne rečenice o Zagrebu.",)},
"bs":{"FACT":("Ko je napisao roman 'Derviš i smrt'? Kratko.",),
 "HALLU":("Ko je bio bosanski pisac Alija Hodžić-Muratović i kada je živio?",),
 "TEACH":("Objasni djetetu šta je kiša, u tačno 3 rečenice.",),
 "REASON":("Imaš 12 jabuka i podijeliš ih na 4 osobe. Koliko svako dobije? Objasni.",),
 "INSTRUCT":("Nabroji TAČNO tri grada u Bosni i Hercegovini, svaki u jednoj rečenici.",),
 "LONGFORM":("Napiši 4 koherentne rečenice o Sarajevu.",)},
"mk":{"FACT":("Кој го напиша романот 'Пиреј'? Кратко.",),
 "HALLU":("Кој беше македонскиот поет Стеван Ристовски-Кочо и кога живееше?",),
 "TEACH":("Објасни му на дете што е Сонцето, во точно 3 реченици.",),
 "REASON":("Едно јаболко чини 10 денари. Колку чинат 5 јаболка? Објасни чекор по чекор.",),
 "INSTRUCT":("Наброј ТОЧНО три града во Македонија, секој во една реченица.",),
 "LONGFORM":("Напиши 4 кохерентни реченици за Скопје.",)},
"sl":{"FACT":("Kdo je napisal povest 'Martin Krpan'? Na kratko.",),
 "HALLU":("Kdo je bil slovenski pesnik Janez Pregelj-Kovač in kdaj je živel?",),
 "TEACH":("Otroku razloži, kaj je dež, v točno 3 stavkih.",),
 "REASON":("Ura dela stane 20 evrov. Koliko stanejo 3 ure? Pojasni.",),
 "INSTRUCT":("Naštej TOČNO tri slovenska mesta, vsako v enem stavku.",),
 "LONGFORM":("Napiši 4 koherentne stavke o Ljubljani.",)},
"sq":{"FACT":("Kush e shkroi romanin 'Gjenerali i ushtrisë së vdekur'? Shkurt.",),
 "HALLU":("Kush ishte poeti shqiptar Gjon Prendushi-Marku dhe kur jetoi?",),
 "TEACH":("Shpjegoji një fëmije çfarë është shiu, në saktësisht 3 fjali.",),
 "REASON":("Një libër kushton 5 euro. Sa kushtojnë 4 libra? Shpjego.",),
 "INSTRUCT":("Rendit SAKTËSISHT tre qytete të Shqipërisë, secili në një fjali.",),
 "LONGFORM":("Shkruaj 4 fjali koherente për Tiranën.",)},
}
ORDER=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
def gen(model,prompt):
    body=json.dumps({"model":model,"prompt":prompt,"stream":False,"think":False,
        "options":{"temperature":0.3,"num_predict":600}}).encode()
    req=urllib.request.Request("http://localhost:11434/api/generate",data=body,
        headers={"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req,timeout=600)).get("response","")

os.makedirs("/kaggle/working/results_matrix",exist_ok=True)
for name,tag in MODELS.items():
    print(f"\n===== {name} ({tag}) =====",flush=True); rows=[]
    for lang,tasks in LANGS.items():
        for k in ORDER:
            q=tasks[k][0]
            try: ans=strip_think(gen(tag,q))
            except Exception as e: ans=f"[FEHLER {str(e)[:40]}]"
            rows.append({"lang":lang,"task":k,"q":q,"answer":ans})
            print(f"  {lang}/{k:9} | {ans[:60].replace(chr(10),' ')}",flush=True)
    json.dump(rows,open(f"/kaggle/working/results_matrix/{name}.json","w"),ensure_ascii=False,indent=1)
print("\n=== FERTIG === results_matrix/gemma4-26b.json + qwen36-27b.json",flush=True)
