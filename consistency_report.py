#!/usr/bin/env python3
"""consistency_report.py — kontrastive & sprachübergreifende Konsistenz aus den Matrix-Rohdaten.

Liest results_matrix/<modell>.json (Zeilen mit lang/task/score, erzeugt von matrix_ollama.py) und misst
zwei Dinge, die die reine Punktesumme NICHT zeigt:

 (1) KONTRASTIVE PAARE — LOGIC (Antwort 5) vs. LOGIC2 (fast identisch, aber Antwort 10).
     Nur wer BEIDE richtig hat, hat wirklich verstanden; wer LOGIC kann und LOGIC2 nicht, hat vermutlich nur
     das Muster "5" gematcht. Kernidee von BalkanBench: Verständnis > Mustererkennung.

 (2) SPRACH-KONSISTENZ — für jede Logik-Achse: in wie vielen der 12 Sprachen ist die Antwort richtig?
     Gutes Reasoning darf nicht an der Sprache hängen (dieselbe Aufgabe, 12 Sprachen).

Aufruf:  python consistency_report.py        -> results_matrix/consistency.md
"""
import json, glob, pathlib

BASE = pathlib.Path(__file__).parent
MD = BASE / "results_matrix"
REASONING_AXES = ["LOGIC", "LOGIC2", "ANALYSIS"]


def load_models():
    out = {}
    for f in glob.glob(str(MD / "*.json")):
        stem = pathlib.Path(f).stem
        if stem in ("scores", "consistency"):
            continue
        try:
            out[stem] = json.load(open(f, encoding="utf-8"))
        except Exception:
            pass
    return out


def main():
    models = load_models()
    if not models:
        print("Keine results_matrix/<modell>.json gefunden — erst matrix_ollama.py laufen lassen.")
        return

    lines = ["# BalkanBench — Konsistenz-Report", "",
             "Ergänzt die Punktetabelle um zwei Dinge, die Summen verbergen: kontrastives Verständnis",
             "und ob Reasoning über die Sprachen stabil ist.", ""]

    # (1) kontrastive Paare LOGIC vs LOGIC2
    lines += ["## 1. Kontrastive Logik-Paare (LOGIC 5  vs.  LOGIC2 10)", "",
              "Fast identische Fragen, ein Wort geändert. **Beide richtig = verstanden**;",
              "nur LOGIC richtig = wahrscheinlich Muster-Matching auf die Zahl 5.", "",
              "| Modell | beide richtig | nur LOGIC (Muster?) | nur LOGIC2 | keine |",
              "|---|---|---|---|---|"]
    for m, rows in sorted(models.items()):
        by = {(r["lang"], r["task"]): r["score"] for r in rows if "task" in r and "score" in r and "lang" in r}
        if not any(k[1] in ("LOGIC","LOGIC2") for k in by): continue  # Modell ohne Logik-Scores (z.B. cloud-getestet)
        langs = sorted({k[0] for k in by})
        both = only1 = only2 = none = 0
        for lg in langs:
            a = by.get((lg, "LOGIC")); b = by.get((lg, "LOGIC2"))
            if a is None or b is None:
                continue
            if a and b: both += 1
            elif a and not b: only1 += 1
            elif b and not a: only2 += 1
            else: none += 1
        lines.append(f"| {m} | **{both}** | {only1} | {only2} | {none} |")

    # (2) Sprach-Konsistenz je Reasoning-Achse
    lines += ["", "## 2. Sprach-Konsistenz je Achse (richtige Sprachen / 12)", "",
              "Dieselbe Aufgabe in allen 12 Sprachen — gutes Reasoning hängt nicht an der Sprache.", "",
              "| Modell | " + " | ".join(REASONING_AXES) + " |",
              "|---|" + "---|" * len(REASONING_AXES)]
    for m, rows in sorted(models.items()):
        by = {(r["lang"], r["task"]): r["score"] for r in rows if "task" in r and "score" in r and "lang" in r}
        if not any(k[1] in REASONING_AXES for k in by): continue
        langs = sorted({k[0] for k in by})
        cells = []
        for ax in REASONING_AXES:
            hit = sum(1 for lg in langs if by.get((lg, ax)) == 1)
            tot = sum(1 for lg in langs if (lg, ax) in by)
            cells.append(f"{hit}/{tot}")
        lines.append(f"| {m} | " + " | ".join(cells) + " |")

    lines += ["", "*Generiert aus results_matrix/ — Rohantworten liegen dort je Modell.*"]
    (MD / "consistency.md").write_text("\n".join(lines), encoding="utf-8")
    print("✓ results_matrix/consistency.md geschrieben (", len(models), "Modelle )")


if __name__ == "__main__":
    main()
