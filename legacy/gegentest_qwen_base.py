#!/usr/bin/env python3
"""gegentest_qwen_base.py — Kennt Qwen3-8B-Basis die Fakten, die Zora v1.1 falsch hat?
Stellt FACT + HALLU (12 Sprachen) an qwen/qwen3-8b via LM Studio (localhost:1234).
Beweist, ob unser CPT/SFT das Faktenwissen ZERSTÖRT hat.
"""
import json, urllib.request, sys
import matrix_ollama as M   # LANGS, score, strip_think

ENDPOINT = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen/qwen3-8b"


def ask(q):
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": q + " /no_think"}],
                       "temperature": 0.3, "max_tokens": 320}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=300))
    return M.strip_think(d["choices"][0]["message"]["content"])


fact_ok = hallu_ok = 0
print(f"Modell: {MODEL} (Basis, via LM Studio)\n")
print("Spr | FACT           | HALLU (winkt ab?)")
for lang, tasks in M.LANGS.items():
    # FACT
    q, ws, typ, ref = tasks["FACT"]
    a = ask(q)
    sc_f, _ = M.score("FACT", ws, typ, ref, a)
    fact_ok += sc_f
    # HALLU
    q2, ws2, typ2, ref2 = tasks["HALLU"]
    a2 = ask(q2)
    sc_h, _ = M.score("HALLU", ws2, typ2, ref2, a2)
    hallu_ok += sc_h
    print(f" {lang:3} | {'✓' if sc_f else '✗'} {a[:40].replace(chr(10),' '):40} | {'✓ IDK' if sc_h else '✗ halluziniert'}")

print(f"\n=== QWEN3-8B-BASIS: FACT {fact_ok}/12 | HALLU {hallu_ok}/12 ===")
print(f"=== ZORA v1.1-16bit:   FACT 3/12  | HALLU 1/12  (zum Vergleich) ===")
print("\nWenn Qwen deutlich besser bei FACT -> unser Training hat das Wissen zerstört.")
