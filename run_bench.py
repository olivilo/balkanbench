#!/usr/bin/env python3
"""
BalkanBench-Runner — vergleicht LLMs im *Verständnis* der Balkansprachen.
Fragt beliebige OpenAI-kompatible Endpoints ab (Ollama, LM Studio, API), speichert
Antworten + Auto-Checks (Schrift/Sprache/Keywords). Tiefes Verständnis → LLM-Judge/Mensch.

KEINE Keys in dieser Datei — via ENV BENCH_KEY (Standard 'x' für Ollama).
Aufruf:
  python3 run_bench.py --endpoint http://localhost:11434 --models "sovasoft/balkan,gemma2:9b"
  BENCH_KEY=sk-... python3 run_bench.py --endpoint http://localhost:1234 --models "..."
"""
import os, re, json, argparse, urllib.request, pathlib

BASE = pathlib.Path(__file__).parent
CASES = [json.loads(l) for l in open(BASE / "cases.jsonl", encoding="utf-8")]
RES = BASE / "results"; RES.mkdir(exist_ok=True)
KEY = os.environ.get("BENCH_KEY", "x")
CYR = re.compile(r"[Ѐ-ӿ]"); LAT = re.compile(r"[A-Za-z]")

try:
    from lingua import Language, LanguageDetectorBuilder
    _L = [Language.ENGLISH, Language.SERBIAN, Language.CROATIAN, Language.BOSNIAN,
          Language.SLOVENE, Language.MACEDONIAN, Language.ALBANIAN]
    DET = LanguageDetectorBuilder.from_languages(*_L).build()
    def detect(t):
        r = DET.detect_language_of(t or ""); return r.name.lower()[:2] if r else "?"
except Exception:
    def detect(t): return "?"   # lingua optional

def strip_think(t): return re.sub(r"<think>.*?</think>", "", t or "", flags=re.S).strip()
def is_azbuka(t):
    c, l = len(CYR.findall(t)), len(LAT.findall(t)); return c > l

def auto_check(case, ans):
    chk = case.get("check", ""); notes = []
    if "script_azbuka" in chk: notes.append("azbuka" if is_azbuka(ans) else "NICHT-azbuka")
    if chk.startswith("lang_"):
        want = chk.split("_")[1]; got = detect(ans); notes.append(f"lang={got}{'✓' if got.startswith(want[:2]) else '✗ (Ziel '+want+')'}")
    if chk == "mentions_all_4":
        hits = sum(1 for kw in ["šume","planin","gore","gorе","plamt","loš","komparativ","iznad"] if kw.lower() in ans.lower())
        notes.append(f"schlüsselbegriffe~{hits}")
    if chk.startswith("mentions "):
        kws = chk.split(" ",1)[1].split(","); hit=[k for k in kws if k.lower() in ans.lower()]
        notes.append(f"{len(hit)}/{len(kws)}: {hit}")
    return "; ".join(notes) or "—"

def ask(endpoint, model, prompt):
    body = json.dumps({"model": model, "messages": [{"role":"user","content":prompt}],
                       "temperature":0.2, "max_tokens":700}).encode()
    req = urllib.request.Request(endpoint.rstrip("/") + "/v1/chat/completions", data=body,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY})
    m = json.load(urllib.request.urlopen(req, timeout=180))["choices"][0]["message"]
    return strip_think(m.get("content") or "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://localhost:11434")
    ap.add_argument("--models", required=True, help="kommagetrennt")
    args = ap.parse_args()
    summary = {}
    for model in [m.strip() for m in args.models.split(",") if m.strip()]:
        safe = model.replace("/","_").replace(":","_")
        out = RES / f"{safe}.jsonl"; rows=[]
        print(f"\n=== {model} ===")
        for c in CASES:
            try:
                ans = ask(args.endpoint, model, c["prompt"])
                chk = auto_check(c, ans)
                rows.append({"id":c["id"],"cat":c["cat"],"prompt":c["prompt"],
                             "answer":ans,"expected":c["expected"],"auto":chk})
                print(f"  [{c['id']:14}] {chk}  | {ans[:60].replace(chr(10),' ')}")
            except Exception as e:
                rows.append({"id":c["id"],"error":str(e)[:100]}); print(f"  [{c['id']}] FEHLER {str(e)[:60]}")
        json.dump(rows, open(out,"w"), ensure_ascii=False, indent=1)
        summary[model] = out.name
    # kurze Übersicht
    with open(RES/"summary.md","w",encoding="utf-8") as f:
        f.write("# BalkanBench — Ergebnisse\n\nAuto-Checks (Schrift/Sprache/Keywords). "
                "Tiefes Verständnis: Antworten in results/<modell>.jsonl **muttersprachlich** prüfen.\n\n")
        for m,fn in summary.items(): f.write(f"- **{m}** → `results/{fn}`\n")
    print(f"\nFertig → {RES}/  (summary.md + je Modell eine .jsonl). Antworten muttersprachlich gegenprüfen!")

if __name__ == "__main__":
    main()
