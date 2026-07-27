#!/usr/bin/env python3
"""
BalkanBench — CLOUD-Runner (in Colab, bandbreiten-schonend).

Statt einen HTTP-Endpoint abzufragen (run_bench.py), lädt dieser Runner HF-Modelle
DIREKT in Colab (4-bit) und beantwortet cases.jsonl in-process. Modelle werden in
Googles Netz nach HF_HOME (= Google Drive) geladen und bleiben gecacht -> NICHTS über
Olivers 50-GB-Heimleitung. Bewertung = dieselbe auto_check-Logik wie run_bench.py.

Vergleichsmodelle (Cloud, Entscheidung 2026-07-10):
  * unser Balkan-LLM v2           (in-memory oder aus LoRA-Dir auf Drive)
  * YugoGPT                       (gordicaleksa/YugoGPT — 7B, Balkan-Basline)
  * EU-Modell EuroLLM-9B-Instruct (utter-project/EuroLLM-9B-Instruct — EU/Horizon)
  (Duolingo: bewusst weggelassen — kein offenes Modell.)

Benutzung in Colab:
  import run_bench_hf as B
  # a) unser v2, das schon im Speicher ist (aus dem Training):
  B.bench_loaded(model, tokenizer, "sovasoft-balkan-v2")
  # b) Baselines frisch laden + benchen (nacheinander, T4-schonend):
  B.load_and_bench("utter-project/EuroLLM-9B-Instruct", "eurollm-9b-it")
  B.load_and_bench("gordicaleksa/YugoGPT", "yugogpt", instruct=False)
  B.write_summary()
"""
import json, pathlib, gc
from run_bench import CASES, auto_check, strip_think   # Wiederverwendung der Bewertung

BASE = pathlib.Path(__file__).parent
RES = BASE / "results"; RES.mkdir(exist_ok=True)
_done = {}


def _generate(model, tokenizer, prompt, instruct=True, max_new_tokens=400):
    import torch
    if instruct:
        msgs = [{"role": "user", "content": prompt}]
        try:
            ids = tokenizer.apply_chat_template(msgs, add_generation_prompt=True,
                                                return_tensors="pt").to(model.device)
        except Exception:
            instruct = False
    if not instruct:
        ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new_tokens, do_sample=True,
                             temperature=0.2, top_p=0.9, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(out[0][ids.shape[1]:], skip_special_tokens=True)


def bench_loaded(model, tokenizer, name, instruct=True):
    """Benchmarkt ein bereits geladenes Modell gegen alle cases; schreibt results/<name>.jsonl."""
    safe = name.replace("/", "_").replace(":", "_")
    rows = []
    print(f"\n=== {name} ===")
    for c in CASES:
        try:
            ans = strip_think(_generate(model, tokenizer, c["prompt"], instruct))
            chk = auto_check(c, ans)
            rows.append({"id": c["id"], "cat": c["cat"], "prompt": c["prompt"],
                         "answer": ans, "expected": c["expected"], "auto": chk})
            print(f"  [{c['id']:14}] {chk}  | {ans[:60].replace(chr(10),' ')}")
        except Exception as e:
            rows.append({"id": c["id"], "error": str(e)[:120]})
            print(f"  [{c['id']}] FEHLER {str(e)[:70]}")
    json.dump(rows, open(RES / f"{safe}.jsonl", "w"), ensure_ascii=False, indent=1)
    _done[name] = f"{safe}.jsonl"


def load_and_bench(model_id, name, instruct=True, max_seq_length=2048):
    """Lädt ein HF-Modell 4-bit (Cache auf Drive), benchmarkt, gibt Speicher wieder frei."""
    import torch
    from unsloth import FastLanguageModel
    print(f"\n### lade {model_id} (4-bit) ...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_id, max_seq_length=max_seq_length, load_in_4bit=True, dtype=None)
    FastLanguageModel.for_inference(model)
    bench_loaded(model, tokenizer, name, instruct)
    del model, tokenizer
    gc.collect(); torch.cuda.empty_cache()


def write_summary():
    with open(RES / "summary.md", "w", encoding="utf-8") as f:
        f.write("# BalkanBench — Ergebnisse (Cloud-Runner)\n\n"
                "Auto-Checks (Schrift/Sprache/Keywords). Tiefes Verständnis: Antworten in "
                "`results/<modell>.jsonl` **muttersprachlich** gegenprüfen (v2 vs Baselines).\n\n")
        for m, fn in _done.items():
            f.write(f"- **{m}** → `results/{fn}`\n")
    print("Summary →", RES / "summary.md")
