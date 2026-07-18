#!/usr/bin/env python3
"""matrix_ollama.py — Härtetest-Matrix über ALLE Modelle via Ollama.
6 Sprachen x 6 Aufgabentypen (FACT, HALLU, TEACH, REASON, INSTRUCT, LONGFORM).
Automatische Bewertung der harten Achsen: FACT (Name da?), HALLU (Ehrlichkeit),
REASON (richtige Zahl?), SCRIPT (richtige Schrift?), LANG (in-Sprache geblieben?).
Ausgabe: results_matrix/<modell>.json + matrix_scores.md (Heatmap-Tabelle).
"""
import os, re, json, argparse, urllib.request, pathlib, collections
BASE=pathlib.Path(__file__).parent
OUT=BASE/"results_matrix"; OUT.mkdir(exist_ok=True)
CYR=re.compile(r"[Ѐ-ӿ]"); LAT=re.compile(r"[A-Za-zČčĆćŽžŠšĐđ]")
def strip_think(t): return re.sub(r"<think>.*?</think>","",t or "",flags=re.S).strip()

# (frage, erwartete_schrift, bewertungs-typ, referenz)
LANGS={
"sr":{"FACT":("Ko je napisao 'Na Drini ćuprija'? Kratko.","lat","name",["andrić","andric"]),
 "HALLU":("Ko je bio srpski naučnik Radovan Petrović-Milošević i kada je živeo?","lat","idk",None),
 "TEACH":("Objasni detetu šta je fotosinteza, u tačno 3 rečenice.","lat","lang",None),
 "REASON":("Voz putuje 60 km/h. Koliko pređe za 2.5 sata? Reši korak po korak.","lat","num",["150"]),
 "INSTRUCT":("Nabroji TAČNO tri reke u Srbiji, ćirilicom, svaku u jednoj reči.","azb","script",None),
 "LONGFORM":("Napiši 4 koherentne rečenice o Beogradu.","lat","lang",None)},
"hr":{"FACT":("Tko je napisao roman 'Povratak Filipa Latinovicza'? Kratko.","lat","name",["krleža","krleza"]),
 "HALLU":("Tko je bio hrvatski pjesnik Tomislav Berišić-Kralj i kada je živio?","lat","idk",None),
 "TEACH":("Objasni djetetu što je gravitacija, u točno 3 rečenice.","lat","lang",None),
 "REASON":("Kruh košta 8 kuna. Koliko koštaju 3 kruha? Objasni.","lat","num",["24"]),
 "INSTRUCT":("Nabroji TOČNO tri hrvatska grada, svaki u jednoj rečenici.","lat","lang",None),
 "LONGFORM":("Napiši 4 koherentne rečenice o Zagrebu.","lat","lang",None)},
"bs":{"FACT":("Ko je napisao roman 'Derviš i smrt'? Kratko.","lat","name",["selimović","selimovic","meša","mesa"]),
 "HALLU":("Ko je bio bosanski pisac Alija Hodžić-Muratović i kada je živio?","lat","idk",None),
 "TEACH":("Objasni djetetu šta je kiša, u tačno 3 rečenice.","lat","lang",None),
 "REASON":("Imaš 12 jabuka i podijeliš ih na 4 osobe. Koliko svako dobije? Objasni.","lat","num",["3"]),
 "INSTRUCT":("Nabroji TAČNO tri grada u Bosni i Hercegovini, svaki u jednoj rečenici.","lat","lang",None),
 "LONGFORM":("Napiši 4 koherentne rečenice o Sarajevu.","lat","lang",None)},
"mk":{"FACT":("Кој го напиша романот 'Пиреј'? Кратко.","azb","name",["андреевски"]),
 "HALLU":("Кој беше македонскиот поет Стеван Ристовски-Кочо и кога живееше?","azb","idk",None),
 "TEACH":("Објасни му на дете што е Сонцето, во точно 3 реченици.","azb","lang",None),
 "REASON":("Едно јаболко чини 10 денари. Колку чинат 5 јаболка? Објасни чекор по чекор.","azb","num",["50"]),
 "INSTRUCT":("Наброј ТОЧНО три града во Македонија, секој во една реченица.","azb","script",None),
 "LONGFORM":("Напиши 4 кохерентни реченици за Скопје.","azb","lang",None)},
"sl":{"FACT":("Kdo je napisal povest 'Martin Krpan'? Na kratko.","lat","name",["levstik"]),
 "HALLU":("Kdo je bil slovenski pesnik Janez Pregelj-Kovač in kdaj je živel?","lat","idk",None),
 "TEACH":("Otroku razloži, kaj je dež, v točno 3 stavkih.","lat","lang",None),
 "REASON":("Ura dela stane 20 evrov. Koliko stanejo 3 ure? Pojasni.","lat","num",["60"]),
 "INSTRUCT":("Naštej TOČNO tri slovenska mesta, vsako v enem stavku.","lat","lang",None),
 "LONGFORM":("Napiši 4 koherentne stavke o Ljubljani.","lat","lang",None)},
"sq":{"FACT":("Kush e shkroi romanin 'Gjenerali i ushtrisë së vdekur'? Shkurt.","lat","name",["kadare"]),
 "HALLU":("Kush ishte poeti shqiptar Gjon Prendushi-Marku dhe kur jetoi?","lat","idk",None),
 "TEACH":("Shpjegoji një fëmije çfarë është shiu, në saktësisht 3 fjali.","lat","lang",None),
 "REASON":("Një libër kushton 5 euro. Sa kushtojnë 4 libra? Shpjego.","lat","num",["20"]),
 "INSTRUCT":("Rendit SAKTËSISHT tre qytete të Shqipërisë, secili në një fjali.","lat","lang",None),
 "LONGFORM":("Shkruaj 4 fjali koherente për Tiranën.","lat","lang",None)},
}
ORDER=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
# Ablehnungs-Marker (Ehrlichkeit) über die Balkansprachen
IDK=["ne postoji","ne mogu","nisam siguran","nema podataka","ne znam","ne raspolažem",
 "nemam podataka","ne obstaja","ne poznam","nisem prepričan","nimam podatkov","ne najdem",
 "nuk ekziston","nuk kam","nuk jam i sigurt","nuk gjej","nuk njoh","не постои","не знам",
 "немам податоци","не сум сигурен","не располагам","izmišljen","ne odgovara stvarnoj",
 "verujem da se greši","ne mogu da potvrdim","ne mogu potvrditi","greška","fiktiv"]

def gen(endpoint,model,prompt):
    body=json.dumps({"model":model,"prompt":prompt,"stream":False,
        "options":{"temperature":0.3,"num_predict":320}}).encode()
    req=urllib.request.Request(endpoint.rstrip("/")+"/api/generate",data=body,
        headers={"Content-Type":"application/json"})
    d=json.load(urllib.request.urlopen(req,timeout=300))
    return d.get("response","")

def score(cat,want_script,typ,ref,ans):
    a=ans.lower()
    cyr=len(CYR.findall(ans)); lat=len(LAT.findall(ans))
    script_ok = (cyr>lat) if want_script=="azb" else (lat>=cyr)
    if typ=="name":  return 1 if ref and any(r in a for r in ref) else 0, script_ok
    if typ=="idk":   return 1 if any(k in a for k in IDK) else 0, script_ok
    if typ=="num":   return 1 if ref and any(r in a for r in ref) else 0, script_ok
    if typ=="script":return (1 if script_ok else 0), script_ok
    if typ=="lang":  return (1 if len(ans.strip())>20 and script_ok else 0), script_ok
    return 0, script_ok

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--endpoint",default="http://localhost:11434")
    ap.add_argument("--models",required=True)
    a=ap.parse_args()
    scores={}
    for model in [m.strip() for m in a.models.split(",") if m.strip()]:
        print(f"\n===== {model} =====",flush=True)
        rows=[]; axis=collections.defaultdict(lambda:[0,0]); scr_hits=[0,0]
        for lang,tasks in LANGS.items():
            for k in ORDER:
                q,ws,typ,ref=tasks[k]
                try:
                    ans=strip_think(gen(a.endpoint,model,q))
                except Exception as e:
                    ans=f"[FEHLER {str(e)[:40]}]"
                sc,scr=score(k,ws,typ,ref,ans)
                axis[k][0]+=sc; axis[k][1]+=1
                scr_hits[0]+=int(scr); scr_hits[1]+=1
                rows.append({"lang":lang,"task":k,"q":q,"want_script":ws,"type":typ,
                    "answer":ans,"score":sc,"script_ok":scr})
                print(f"  {lang}/{k:9} {'✓' if sc else '✗'} {'S' if scr else 's'} | {ans[:55].replace(chr(10),' ')}",flush=True)
        json.dump(rows,open(OUT/f"{model.replace('/','_').replace(':','_')}.json","w"),ensure_ascii=False,indent=1)
        scores[model]={k:(axis[k][0],axis[k][1]) for k in ORDER}
        scores[model]["SCRIPT"]=(scr_hits[0],scr_hits[1])
    # Score-Tabelle
    with open(OUT/"matrix_scores.md","w",encoding="utf-8") as f:
        f.write("# Härtetest-Matrix — Scores (je 6 Sprachen)\n\n")
        cols=ORDER+["SCRIPT"]
        f.write("| Modell | "+" | ".join(cols)+" | Σ |\n|"+"---|"*(len(cols)+2)+"\n")
        for m,sc in scores.items():
            tot=sum(sc[k][0] for k in ORDER); mx=sum(sc[k][1] for k in ORDER)
            cells=[f"{sc[k][0]}/{sc[k][1]}" for k in cols]
            f.write(f"| {m} | "+" | ".join(cells)+f" | **{tot}/{mx}** |\n")
    print(f"\nFertig → {OUT}/matrix_scores.md")

if __name__=="__main__":
    main()
