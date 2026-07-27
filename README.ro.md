🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Un benchmark deschis pentru *înțelegerea* limbilor din Balcani și Europa de Sud-Est — nu pentru viteză.**

Majoritatea benchmark-urilor pentru LLM măsoară eficiența și abilitățile centrate pe limba engleză. **BalkanBench măsoară altceva:** dacă un model *înțelege* cu adevărat aceste limbi — ambiguitatea, omonimele, alfabetul, dialectul, cultura — și dacă este **onest** (admite ceea ce nu știe) în loc să inventeze fapte.

> Flagship example: **„Горе горе горе горе него доле."** — patru ori *gore*, patru înțelesuri:
> *sus · păduri/munți · [ele] ard · mai rău.* → "Sus, pădurile ard mai rău decât jos."
> Un model care rezolvă acest lucru a *înțeles* limba, nu doar a tradus-o.

Acesta rulează **13 axe × 12 limbi = 156 de teste deterministe** per model. Fără chei API, fără LLM-judge — scorul se bazează pe script/cuvânt-cheie/număr, astfel încât oricine îl poate reproduce.

---

## Cele 12 limbi
Serbian (sr), Croatian (hr), Bosnian (bs), Macedonian (mk), Slovenian (sl), Albanian (sq),
Montenegrin (cnr), Bulgarian (bg), Greek (el), Turkish (tr), Romanian (ro), Hungarian (hu).

Conștientizarea alfabetului este integrată: **Azbuka** (Chirilic ≠ "doar chirilic"), Latinica și Greca sunt
verificate pentru fiecare răspuns — un model care răspunde în macedoneană cu alfabet latin pierde punctul pentru script.

## Cele 13 axe (ce este testat)

| Axă | Ce măsoară |
|---|---|
| **FACT** | Cunoștințe reale despre istoria, cultura și geografia Balcanilor |
| **HALLU** | Persoană/operă/eveniment inventat → **admite "nu știu"** în loc să fabrice? |
| **DETAIL** | Entitate reală + un detaliu fabricat → semnalează incertitudinea? |
| **GRADED** | Onestitate gradată: arată cunoștințe parțiale (entitatea reală) **și** refuză detaliul inventat |
| **TEACH** | Predarea/explicarea unui subiect **în limba țintă** |
| **REASON** | Raționament și inferență de zi cu zi |
| **LOGIC** | Matematică/logică scurtă — este rezultatul final corect? |
| **LOGIC2** | Un al doilea element de logică (robustețe) |
| **ANALYSIS** | Analiză mai lungă — rezultat corect **și** un parcurs vizibil pas cu pas |
| **INSTRUCT** | Respectarea constrângerilor de formatare / instrucțiuni |
| **LONGFORM** | Text coerent de formă lungă, în limba respectivă |
| **SEARCH** | Utilizarea instrumentelor: când nu este sigur, **apelează `web_search`**? |
| **TOOLBASE** | Discriminarea instrumentelor: pentru cunoștințe de bază, răspunde **direct** (nu apelează un instrument) |

Fiecare răspuns este verificat și pentru output-ul **în limba respectivă / scriptul corect** — gândirea și răspunsul în limba țintă, fără a trece prin engleză.

## Cum funcționează scorul (determinist)
Fiecare axă folosește o verificare fixă — fără judecată subiectivă:
- `name` / `num` — faptul/numărul corect apare în răspuns
- `idk` — un marcator de onestitate (*"nu știu / nu pot confirma"*, per limbă) apare
- `graded` — atât entitatea reală, cât și un marcator de onestitate apar
- `script` / `lang` — output-ul este în scriptul și limba așteptate
- `calc` / `calc_long` — numărul final coincide (forma lungă necesită și pași intermediari)
- `search` — modelul a declanșat instrumentul `web_search`; `notool` — a răspuns fără acesta

Total: **/156**. Complet reproductibil.

---

## Quickstart — testează propriul model

BalkanBench comunică cu orice model servit de **[Ollama](https://ollama.com)**.

```bash
# 1) Serve your model(s) with Ollama
ollama pull olivilo/zora          # or your own model, e.g. ollama pull gemma2:9b

# 2) Run the benchmark (Ollama endpoint defaults to localhost:11434)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Output: un **tabel de scor per axă** pentru fiecare model, `/156`, plus detalii per răspuns.
Compară orice model — fine-tune-ul tău, un model de bază, un competitor — pe aceleași 156 de sarcini.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

Nu este necesar un GPU pentru harness-ul în sine — Ollama rulează modelul, benchmark-ul doar calculează scorul.

---

## Rezultate de referință (Zora v1.11, 8B)
Zora conduce domeniul, depășind modele de 3–4 ori mai mari:

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

## Filosofie
> Un model pentru Balcani trebuie să înțeleagă aceste limbi **din interior** — dublele
> sensuri, dialectele, scripturile și cultura — și să fie **onest** cu privire la limitele sale. Viteza este secundară.
> **Înțelegerea contează.**

Deschis, reproductibil, verificat nativ cross-lingual. Contribuțiile sunt binevenite.
De **Sovasoft** ([ai.in.rs](https://ai.in.rs)) împreună cu **Akademija Ljiljana**.