#!/usr/bin/env python3
"""bench_extended.py — Erweiterter BalkanBench: Inhalt + GESCHWINDIGKEIT pro Sprache/Schrift.

Misst über den Ollama-/OpenAI-Endpoint für jedes Modell und jeden Fall:
  - Antwort (für inhaltliche Bewertung)
  - prompt_eval (Preprocessing): Tokens + Dauer  -> Preprocessing-Geschwindigkeit
  - eval (Generierung): Tokens + Dauer           -> Token/s (pro Sprache/Schrift!)
  - Thinking: Länge + Anteil des <think>-Blocks   -> "denkt es zu lang?"

Zusätzliche Inhalts-Kategorien: Synonyme, Homophone, Homographen (Betonung), pro Sprache.
Nutzt Ollama /api/generate (liefert prompt_eval_count/duration, eval_count/duration).

Aufruf:  python3 bench_extended.py --endpoint http://localhost:11434 --models "zora,aya,..."
Ausgabe: results_ext/<modell>.json + results_ext/speed_summary.md
"""
import os, re, json, time, argparse, urllib.request, pathlib, collections
BASE=pathlib.Path(__file__).parent
OUT=BASE/"results_ext"; OUT.mkdir(exist_ok=True)
CYR=re.compile(r"[Ѐ-ӿ]")
def strip_think(t): return re.sub(r"<think>.*?</think>","",t or "",flags=re.S).strip()
def think_part(t):
    m=re.search(r"<think>(.*?)</think>",t or "",flags=re.S)
    return m.group(1).strip() if m else ""

# Testfälle: (id, lang, script, kategorie, prompt) — Inhalt + Speed über Sprachen/Schriften
CASES=[
 # gleiche Aufgabe in mehreren Sprachen/Schriften -> Speed-Vergleich
 ("speed-sr-lat","sr","lat","speed","Objasni u 3 rečenice šta je fotosinteza."),
 ("speed-sr-azb","sr","azb","speed","Објасни у 3 реченице шта је фотосинтеза."),
 ("speed-hr","hr","lat","speed","Objasni u 3 rečenice što je fotosinteza."),
 ("speed-mk","mk","azb","speed","Објасни во 3 реченици што е фотосинтеза."),
 ("speed-sl","sl","lat","speed","Pojasni v 3 stavkih, kaj je fotosinteza."),
 ("speed-sq","sq","lat","speed","Shpjego në 3 fjali çfarë është fotosinteza."),
 # Synonyme
 ("syn-sr","sr","lat","synonym","Navedi tri sinonima za reč „lep“ na srpskom."),
 ("syn-hr","hr","lat","synonym","Navedi tri sinonima za riječ „lijep“ na hrvatskom."),
 ("syn-mk","mk","azb","synonym","Наведи три синоними за зборот „убав“ на македонски."),
 ("syn-sl","sl","lat","synonym","Naštej tri sopomenke za besedo „lep“ v slovenščini."),
 ("syn-sq","sq","lat","synonym","Jep tre sinonime për fjalën „i bukur“ në shqip."),
 # Homophone / gleich klingend, verschieden geschrieben/bedeutet
 ("homf-sr","sr","lat","homophon","Objasni razliku između „s njim“ i „snjim“ i koja je ispravna."),
 ("homf-hr","hr","lat","homophon","Objasni razliku u značenju: „pojedini“ i „po jedini“."),
 # Homographen (Betonung)
 ("homg-sr","sr","lat","homograph","Reč „luk“ ima dva značenja po dužini samoglasnika. Objasni."),
 ("homg-hr","hr","lat","homograph","Riječ „pas“ ima dva značenja ovisno o izgovoru. Objasni."),
 ("homg-mk","mk","azb","homograph","Зборот „лук“ има две значења. Објасни."),
]

def gen_ollama(endpoint, model, prompt):
    body=json.dumps({"model":model,"prompt":prompt,"stream":False,
        "options":{"temperature":0.3,"num_predict":300}}).encode()
    req=urllib.request.Request(endpoint.rstrip("/")+"/api/generate",data=body,
        headers={"Content-Type":"application/json"})
    t0=time.time(); d=json.load(urllib.request.urlopen(req,timeout=300)); wall=time.time()-t0
    return {
        "response": d.get("response",""),
        "prompt_tokens": d.get("prompt_eval_count",0),
        "prompt_ms": d.get("prompt_eval_duration",0)/1e6,
        "eval_tokens": d.get("eval_count",0),
        "eval_ms": d.get("eval_duration",0)/1e6,
        "wall_s": round(wall,2),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--endpoint",default="http://localhost:11434")
    ap.add_argument("--models",required=True)
    a=ap.parse_args()
    summary=[]
    for model in [m.strip() for m in a.models.split(",") if m.strip()]:
        print(f"\n=== {model} ===",flush=True)
        rows=[]
        for cid,lang,scr,cat,prompt in CASES:
            try:
                r=gen_ollama(a.endpoint,model,prompt)
                full=r["response"]; ans=strip_think(full); th=think_part(full)
                tok_s=round(r["eval_tokens"]/(r["eval_ms"]/1000),1) if r["eval_ms"]>0 else 0
                pp_s=round(r["prompt_tokens"]/(r["prompt_ms"]/1000),1) if r["prompt_ms"]>0 else 0
                rows.append({"id":cid,"lang":lang,"script":scr,"cat":cat,"prompt":prompt,
                    "answer":ans,"think_chars":len(th),"answer_chars":len(ans),
                    "tokens_per_sec":tok_s,"preproc_tokens_per_sec":pp_s,
                    "prompt_tokens":r["prompt_tokens"],"eval_tokens":r["eval_tokens"],
                    "prompt_ms":round(r["prompt_ms"]),"eval_ms":round(r["eval_ms"]),"wall_s":r["wall_s"]})
                print(f"  [{cid:12}] {tok_s:5} tok/s | think {len(th):4}z | {ans[:45].replace(chr(10),' ')}")
            except Exception as e:
                rows.append({"id":cid,"error":str(e)[:100]}); print(f"  [{cid}] FEHLER {str(e)[:50]}")
        json.dump(rows,open(OUT/f"{model.replace('/','_').replace(':','_')}.json","w"),ensure_ascii=False,indent=1)
        # Speed-Aggregat pro Schrift
        by_scr=collections.defaultdict(list)
        for r in rows:
            if r.get("cat")=="speed" and r.get("tokens_per_sec"): by_scr[r["script"]].append(r["tokens_per_sec"])
        summary.append((model,{k:round(sum(v)/len(v),1) for k,v in by_scr.items()},
            round(sum(r.get("tokens_per_sec",0) for r in rows if r.get("tokens_per_sec"))/max(1,sum(1 for r in rows if r.get("tokens_per_sec"))),1),
            round(sum(r.get("think_chars",0) for r in rows)/max(1,len(rows)))))
    # Speed-Summary
    with open(OUT/"speed_summary.md","w",encoding="utf-8") as f:
        f.write("# Speed & Thinking — Ergebnisse\n\n")
        f.write("| Modell | tok/s (latinica) | tok/s (azbuka) | tok/s (Ø) | ø think-Zeichen |\n|---|---|---|---|---|\n")
        for m,scr,avg,think in summary:
            f.write(f"| {m} | {scr.get('lat','–')} | {scr.get('azb','–')} | {avg} | {think} |\n")
    print(f"\nFertig → {OUT}/ (je Modell .json + speed_summary.md)")

if __name__=="__main__":
    main()
