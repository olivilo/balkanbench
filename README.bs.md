🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Otvoreni benchmark za *razumijevanje* jezika Balkana i jugoistočne Evrope — ne za brzinu.**

Većina LLM benchmarkova mjeri efikasnost i vještine usmjerene na engleski jezik. **BalkanBench mjeri nešto drugo:** da li model zaista *razumije* ove jezike — dvosmislenost, homonime, pismo, dijalekte, kulturu — i da li je **iskren** (priznaje ono što ne zna) umjesto da izmišlja činjenice.

> Flagship example: **„Горе горе горе горе него доле."** — četiri puta *gore*, četiri značenja:
> *gore (odgore) · gore (šume/planine) · gore (gore/palje se) · gore (gore/lošije).* → "Up above, the forests burn worse than below."
> Model koji ovo riješi je *razumio* jezik, a ne samo ga preveo.

Pokreće **13 osa × 12 jezika = 156 determinističkih testova** po modelu. Bez API ključeva, bez LLM-sudije — bodovanje se zasniva na pismu/ključnoj riječi/broju, tako da ga svako može reprodukovati.

---

## 12 jezika
srpski (sr), hrvatski (hr), bosanski (bs), makedonski (mk), slovenački (sl), albanski (sq),
crnogorski (cnr), bugarski (bg), grčki (el), turski (tr), rumunski (ro), mađarski (hu).

Svijest o pismu je ugrađena: **Azbuka** (ćirilica ≠ "samo ćirilica"), Latinica i grčko pismo se
provjeravaju po odgovoru — model koji odgovara na makedonskom jeziku koristeći latinicu gubi bod za pismo.

## 13 osa (šta se testira)

| Osa | Šta mjeri |
|---|---|
| **FACT** | Stvarno znanje o balkanskoj historiji, kulturi, geografiji |
| **HALLU** | Izmišljena osoba/djelo/događaj → da li **priznaje "ne znam"** umjesto da fabricira? |
| **DETAIL** | Stvarni entitet + izmišljen detalj → da li signalizira nesigurnost? |
| **GRADED** | Gradirana iskrenost: pokazuje djelimično znanje (stvarni entitet) **i** odbija izmišljeni detalj |
| **TEACH** | Podučavanje/objašnjavanje teme **na ciljanom jeziku** |
| **REASON** | Svakodnevno zaključivanje i inferencija |
| **LOGIC** | Kratka matematika/logika — da li je konačni rezultat tačan? |
| **LOGIC2** | Druga stavka logike (robustnost) |
| **ANALYSIS** | Duža analiza — tačan rezultat **i** vidljiv put korak-po-korak |
| **INSTRUCT** | Praćenje ograničenja formatiranja / instrukcija |
| **LONGFORM** | Koherentan tekst dugog oblika, na jeziku |
| **SEARCH** | Korištenje alata: kada nije siguran, da li **poziva `web_search`**? |
| **TOOLBASE** | Diskriminacija alata: za osnovno znanje, odgovara **direktno** (ne poziva alat) |

Svaki odgovor se također provjerava za **izlaz na jeziku / u ispravnom pismu** — razmišljanje i odgovaranje na ciljanom jeziku, bez prebacivanja preko engleskog.

## Kako funkcioniše bodovanje (deterministički)
Svaka osa koristi fiksnu provjeru — bez subjektivnog prosuđivanja:
- `name` / `num` — tačna činjenica/broj se pojavljuje u odgovoru
- `idk` — marker iskrenosti (*"ne znam / ne mogu potvrditi"*, zavisno od jezika) se pojavljuje
- `graded` — stvarni entitet **i** marker iskrenosti se oba pojavljuju
- `script` / `lang` — izlaz je u očekivanom pismu i jeziku
- `calc` / `calc_long` — konačni broj se podudara (dugi oblik zahtijeva i međukorake)
- `search` — model je aktivirao `web_search` alat; `notool` — odgovorio je bez njega

Ukupno: **/156**. Potpuno reprodukovljivo.

---

## Brzi start — testirajte vlastiti model

BalkanBench komunicira sa bilo kojim modelom koji poslužuje **[Ollama](https://ollama.com)**.

```bash
# 1) Serve your model(s) with Ollama
ollama pull olivilo/zora          # or your own model, e.g. ollama pull gemma2:9b

# 2) Run the benchmark (Ollama endpoint defaults to localhost:11434)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Izlaz: **tabela bodova po osi** za svaki model, `/156`, plus detalji po odgovoru.
Uporedite bilo koji model — vaš fine-tune, bazni model, konkurenta — na istih 156 zadataka.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

GPU nije potreban za sam harness — Ollama pokreće model, benchmark samo boduje.

---

## Referentni rezultati (Zora v1.11, 8B)
Zora predvodi polje, pobjeđujući modele 3–4× svoje veličine:

| Model | Veličina | Bodovi |
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

## Filozofija
> Model za Balkan mora razumjeti ove jezike **iznutra** — njihova dvostruka
> značenja, dijalekte, pisma i kulturu — i biti **iskren** u vezi svojih ograničenja. Brzina je sekundarna.
> **Razumijevanje je ono što se računa.**

Otvoreno, reprodukovljivo, izvorno međusobno provjereno. Kontribucije su dobrodošle.
Od strane **Sovasoft** ([ai.in.rs](https://ai.in.rs)) uz **Akademija Ljiljana**.