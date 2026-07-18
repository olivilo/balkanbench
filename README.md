# BalkanBench

**An open benchmark for *comprehension* of the languages of the Balkans / Southeast Europe** —
Serbian (Latin + Azbuka), Croatian, Bosnian, Macedonian, Slovenian and Albanian.

Most multilingual benchmarks reward fluency and speed. BalkanBench instead measures whether a model
truly **understands** these languages: polysemy, dialects, scripts, culture, and honesty — the things
English‑centric models get wrong.

Built by **[Sovasoft](https://ai.in.rs)** to evaluate the **Zora** Balkan LLM and to let anyone compare
models fairly and reproducibly.

## What it tests

| Category | Examples |
|---|---|
| **Homonyms / polysemy** | `gore` ×4 (above / forests / burn / worse), `grad` (city / hail), `kosa` (hair / scythe / slope) |
| **Language separation** | BCMS kept apart: train = *vlak* (hr) / *voz* (sr); bread = *хлеб* / *kruh* / *hleb* |
| **Script control** | write / answer in **Azbuka** on request; Montenegrin Ś/Ź |
| **Dialect** | ekavica ↔ ijekavica, Slovenian dual (dvojina), Albanian suffixes |
| **Culture** | proverbs, Slava, Macedonian idioms |
| **Reasoning in‑language** | step‑by‑step math/logic in the correct language + script |
| **Honesty (hard test)** | refuse to invent facts about non‑existent people (anti‑hallucination) |

## How to run

BalkanBench queries any **OpenAI‑compatible endpoint** (Ollama, LM Studio, vLLM, an API…).

```bash
pip install -r requirements.txt

# 18 comprehension cases against a local endpoint (e.g. Ollama):
python run_bench.py --endpoint http://localhost:11434 \
  --models "your-model:latest,another-model:latest"

# Results land in results/<model>.jsonl — review the answers natively.
```

For the **hard test matrix** (6 languages × 6 real tasks, incl. hallucination traps):

```bash
MODEL=./path-to-local-model python matrix_test.py
```

Cases live in `cases.jsonl` (one JSON object per line: id, category, language, prompt, expected).
Add your own — contributions welcome.

## Results

See **[results/RESULTS.md](results/RESULTS.md)** for the full comparison with charts:
**Zora vs. YugoGPT vs. EuroLLM**, per category, plus Zora's version‑over‑version evolution.

Highlights (local test, Apple‑silicon / Ollama, GGUF Q4_K_M — the real "small hardware" profile):

- **Language & script discipline**: Zora keeps Azbuka on command and separates BCMS cleanly; the
  compared models often ignore script requests or drift into English/Bulgarian.
- **Honesty**: Zora refuses to invent biographies for non‑existent people **in all languages**.
- **Open limitation**: factual *detail* recall is still a work in progress — solved by retrieval /
  tool‑use, not by more data (see RESULTS.md).

## Philosophy

Each language carries its own concepts that don't map cleanly onto English. A model that "thinks" in
English and translates at the end quietly loses meaning. BalkanBench checks the opposite:
**comprehension over efficiency** — does the model reason *in* the language it speaks?

## License

Code and cases: **MIT** (see LICENSE). Test data is synthetic/curated for evaluation.
Charts and result logs included for transparency and reproducibility.

---
*Part of the [ai.in.rs](https://ai.in.rs) software portfolio · Zora Balkan LLM by Sovasoft.*
