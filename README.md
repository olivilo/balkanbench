🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**An open benchmark for *understanding* the languages of the Balkans & Southeast Europe — not speed.**

Most LLM benchmarks measure efficiency and English-centric skills. **BalkanBench measures something
else:** whether a model truly *understands* these languages — ambiguity, homonyms, script, dialect,
culture — and whether it is **honest** (admits what it doesn't know) instead of inventing facts.

> Flagship example: **„Горе горе горе горе него доле."** — four times *gore*, four meanings:
> *up · forests/mountains · [they] burn · worse.* → "Up above, the forests burn worse than below."
> A model that resolves this has *understood* the language, not just translated it.

It runs **13 axes × 12 languages = 156 deterministic tests** per model. No API keys, no LLM-judge —
scoring is script/keyword/number based, so anyone can reproduce it.

---

## The 12 languages
Serbian (sr), Croatian (hr), Bosnian (bs), Macedonian (mk), Slovenian (sl), Albanian (sq),
Montenegrin (cnr), Bulgarian (bg), Greek (el), Turkish (tr), Romanian (ro), Hungarian (hu).

Script awareness is built in: **Azbuka** (Cyrillic ≠ "just Cyrillic"), Latinica, and Greek are
checked per answer — a model answering Macedonian in Latin script loses the script point.

## The 13 axes (what is tested)

| Axis | What it measures |
|---|---|
| **FACT** | Real knowledge of Balkan history, culture, geography |
| **HALLU** | Invented person/work/event → does it **admit "I don't know"** instead of fabricating? |
| **DETAIL** | Real entity + a fabricated detail → does it flag the uncertainty? |
| **GRADED** | Graded honesty: show partial knowledge (the real entity) **and** decline the invented detail |
| **TEACH** | Teaching/explaining a topic **in the target language** |
| **REASON** | Everyday reasoning and inference |
| **LOGIC** | Short math/logic — is the final result correct? |
| **LOGIC2** | A second logic item (robustness) |
| **ANALYSIS** | Longer analysis — correct result **and** a visible step-by-step path |
| **INSTRUCT** | Following formatting / instruction constraints |
| **LONGFORM** | Coherent long-form text, in-language |
| **SEARCH** | Tool use: when unsure, does it **call `web_search`**? |
| **TOOLBASE** | Tool discrimination: for basic knowledge, answer **directly** (do *not* call a tool) |

Every answer is also checked for **in-language / correct-script** output — thinking and answering
in the target language, not pivoting through English.

## How scoring works (deterministic)
Each axis uses a fixed check — no subjective judging:
- `name` / `num` — the correct fact/number appears in the answer
- `idk` — an honesty marker (*"I don't know / can't confirm"*, per language) appears
- `graded` — the real entity **and** an honesty marker both appear
- `script` / `lang` — output is in the expected script and language
- `calc` / `calc_long` — the final number matches (long form also requires intermediate steps)
- `search` — the model triggered the `web_search` tool; `notool` — it answered without one

Total: **/156**. Fully reproducible.

---

## Quickstart — test your own model

BalkanBench talks to any model served by **[Ollama](https://ollama.com)**.

```bash
# 1) Serve your model(s) with Ollama
ollama pull olivilo/zora          # or your own model, e.g. ollama pull gemma2:9b

# 2) Run the benchmark (Ollama endpoint defaults to localhost:11434)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Output: a **per-axis score table** for each model, `/156`, plus per-answer detail.
Compare any model — your fine-tune, a base model, a competitor — on the same 156 tasks.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

No GPU required for the harness itself — Ollama runs the model, the benchmark just scores.

---

## Reference results (Zora v1.11, 8B)
Zora leads the field, beating models 3–4× its size:

| Model | Size | Score |
|---|---|---|
| **Zora v1.11** | **8B** | **84** |
| Gemma-4-31B | 31B | 77 |
| Mistral-24B | 24B | 73 |
| Qwen3.6-30B | 30B | 73 |
| Salamandra | 7B | 66 |
| EuroLLM | 9B | 65 |
| Aya | 8B | 61 |
| BgGPT | 7B | 56 |
| YugoGPT | 7B | 35 |

Model: **[huggingface.co/sovasoft/zora-v1.11](https://huggingface.co/sovasoft/zora-v1.11)**

## Philosophy
> A model for the Balkans must understand these languages **from the inside** — their double
> meanings, dialects, scripts and culture — and be **honest** about its limits. Speed is secondary.
> **Understanding counts.**

Open, reproducible, natively cross-checked. Contributions welcome.
By **Sovasoft** ([ai.in.rs](https://ai.in.rs)) with **Akademija Ljiljana**.
