#!/usr/bin/env python3
"""bench_gemma.py — Gemma-4-26B-A4B nachziehen (kompatible Quellen probieren)."""
import os, re, json, time, subprocess, urllib.request
def sh(c): print(">>",c,flush=True); return subprocess.call(c,shell=True)
def strip_think(t): return re.sub(r"<think>.*?</think>","",t or "",flags=re.S).strip()
sh("apt-get update -qq && apt-get install -y -qq zstd")
sh("curl -fsSL https://ollama.com/install.sh | sh")
subprocess.Popen("ollama serve",shell=True)
for _ in range(60):
    try: urllib.request.urlopen("http://localhost:11434/api/version",timeout=3); print("serve bereit",flush=True); break
    except Exception: time.sleep(2)

def test_gen(tag):
    try:
        b=json.dumps({"model":tag,"prompt":"Reci 'zdravo'.","stream":False,"think":False,"options":{"num_predict":20}}).encode()
        r=json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate",data=b,headers={"Content-Type":"application/json"}),timeout=300))
        return True, r.get("response","")[:50]
    except Exception as e: return False, str(e)[:80]

CANDIDATES=[
 "hf.co/ggml-org/gemma-4-26B-A4B-it-GGUF:Q4_0",
 "hf.co/google/gemma-4-26B-A4B-it-qat-q4_0-gguf:latest",
]
MODEL=None
for c in CANDIDATES:
    print(f"=== versuche {c} ===",flush=True)
    if sh(f"ollama pull {c}")!=0: print("  pull fehlgeschlagen",flush=True); continue
    ok,msg=test_gen(c); print(f"  test: {ok} -> {msg!r}",flush=True)
    if ok: MODEL=c; break
if not MODEL:
    sh("ollama list"); raise SystemExit("Keine kompatible Gemma-Quelle gefunden")
print(f"=== benchmark mit {MODEL} ===",flush=True)

LANGS={
"sr":{"FACT":"Ko je napisao 'Na Drini ćuprija'? Kratko.","HALLU":"Ko je bio srpski naučnik Radovan Petrović-Milošević i kada je živeo?","TEACH":"Objasni detetu šta je fotosinteza, u tačno 3 rečenice.","REASON":"Voz putuje 60 km/h. Koliko pređe za 2.5 sata? Reši korak po korak.","INSTRUCT":"Nabroji TAČNO tri reke u Srbiji, ćirilicom, svaku u jednoj reči.","LONGFORM":"Napiši 4 koherentne rečenice o Beogradu."},
"hr":{"FACT":"Tko je napisao roman 'Povratak Filipa Latinovicza'? Kratko.","HALLU":"Tko je bio hrvatski pjesnik Tomislav Berišić-Kralj i kada je živio?","TEACH":"Objasni djetetu što je gravitacija, u točno 3 rečenice.","REASON":"Kruh košta 8 kuna. Koliko koštaju 3 kruha? Objasni.","INSTRUCT":"Nabroji TOČNO tri hrvatska grada, svaki u jednoj rečenici.","LONGFORM":"Napiši 4 koherentne rečenice o Zagrebu."},
"bs":{"FACT":"Ko je napisao roman 'Derviš i smrt'? Kratko.","HALLU":"Ko je bio bosanski pisac Alija Hodžić-Muratović i kada je živio?","TEACH":"Objasni djetetu šta je kiša, u tačno 3 rečenice.","REASON":"Imaš 12 jabuka i podijeliš ih na 4 osobe. Koliko svako dobije? Objasni.","INSTRUCT":"Nabroji TAČNO tri grada u Bosni i Hercegovini, svaki u jednoj rečenici.","LONGFORM":"Napiši 4 koherentne rečenice o Sarajevu."},
"mk":{"FACT":"Кој го напиша романот 'Пиреј'? Кратко.","HALLU":"Кој беше македонскиот поет Стеван Ристовски-Кочо и кога живееше?","TEACH":"Објасни му на дете што е Сонцето, во точно 3 реченици.","REASON":"Едно јаболко чини 10 денари. Колку чинат 5 јаболка? Објасни чекор по чекор.","INSTRUCT":"Наброј ТОЧНО три града во Македонија, секој во една реченица.","LONGFORM":"Напиши 4 кохерентни реченици за Скопје."},
"sl":{"FACT":"Kdo je napisal povest 'Martin Krpan'? Na kratko.","HALLU":"Kdo je bil slovenski pesnik Janez Pregelj-Kovač in kdaj je živel?","TEACH":"Otroku razloži, kaj je dež, v točno 3 stavkih.","REASON":"Ura dela stane 20 evrov. Koliko stanejo 3 ure? Pojasni.","INSTRUCT":"Naštej TOČNO tri slovenska mesta, vsako v enem stavku.","LONGFORM":"Napiši 4 koherentne stavke o Ljubljani."},
"sq":{"FACT":"Kush e shkroi romanin 'Gjenerali i ushtrisë së vdekur'? Shkurt.","HALLU":"Kush ishte poeti shqiptar Gjon Prendushi-Marku dhe kur jetoi?","TEACH":"Shpjegoji një fëmije çfarë është shiu, në saktësisht 3 fjali.","REASON":"Një libër kushton 5 euro. Sa kushtojnë 4 libra? Shpjego.","INSTRUCT":"Rendit SAKTËSISHT tre qytete të Shqipërisë, secili në një fjali.","LONGFORM":"Shkruaj 4 fjali koherente për Tiranën."},
}
ORDER=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
def gen(prompt):
    b=json.dumps({"model":MODEL,"prompt":prompt,"stream":False,"think":False,"options":{"temperature":0.3,"num_predict":600}}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate",data=b,headers={"Content-Type":"application/json"}),timeout=600)).get("response","")
os.makedirs("/kaggle/working/results_matrix",exist_ok=True); rows=[]
for lang,tasks in LANGS.items():
    for k in ORDER:
        try: ans=strip_think(gen(tasks[k]))
        except Exception as e: ans=f"[FEHLER {str(e)[:40]}]"
        rows.append({"lang":lang,"task":k,"q":tasks[k],"answer":ans})
        print(f"  {lang}/{k:9} | {ans[:60].replace(chr(10),' ')}",flush=True)
json.dump(rows,open("/kaggle/working/results_matrix/gemma4-26b.json","w"),ensure_ascii=False,indent=1)
print("=== FERTIG ===",flush=True)
