🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Otvoreni benchmark za *razumijevanje* jezika Balkana i jugoistočne Europe — ne za brzinu.**

Većina LLM benchmarkova mjeri učinkovitost i vještine usmjerene na engleski jezik. **BalkanBench mjeri nešto drugo:** razumije li model uistinu ove jezike — dvosmislenost, homonime, pismo, dijalekte, kulturu — i je li **iskren** (priznaje ono što ne zna) umjesto da izmišlja činjenice.

> Flagship example: **„Горе горе горе горе него доле."** — četiri puta *gore*, četiri značenja:
> *gore · šume/planine · gore [oni] · gore.* → "Gore, šume gore gore nego dolje."
> Model koji ovo riješi *razumio* je jezik, a ne samo ga preveo.

Pokreće **13 osi × 12 jezika = 156 determinističkih testova** po modelu. Bez API ključeva, bez LLM-sudije — bodovanje se temelji na pismu/ključnoj riječi/broju, tako da ga svatko može reproducirati.

---

## 12 jezika
Srpski (sr), hrvatski (hr), bosanski (bs), makedonski (mk), slovenački (sl), albanski (sq),
crnogorski (cnr), bugarski (bg), grčki (el), turski (tr), rumunjski (ro), mađarski (hu).

Svijest o pismu je ugrađena: **Azbuka** (ćirilica ≠ "samo ćirilica"), Latinica i grčko pismo provjeravaju se po odgovoru — model koji odgovara na makedonskom jeziku koristeći latinicu gubi bod za pismo.

## 13 osi (što se testira)

| Os | Što mjeri |
|---|---|
| **FACT** | Stvarno znanje o povijesti, kulturi i geografiji Balkana |
| **HALLU** | Izmišljena osoba/djelo/događaj → priznaje li **"ne znam"** umjesto fabriciranja? |
| **DETAIL** | Stvarni entitet + izmišljen detalj → signalizira li nesigurnost? |
| **GRADED** | Gradirana iskrenost: pokazuje djelomično znanje (stvarni entitet) **i** odbija izmišljeni detalj |
| **TEACH** | Podučivanje/objašnjavanje teme **na ciljanom jeziku** |
| **REASON** | Svakodnevno zaključivanje i inferencija |
| **LOGIC** | Kratka matematika/logika — je li konačni rezultat točan? |
| **LOGIC2** | Druga logika (robustnost) |
| **ANALYSIS** | Duža analiza — točan rezultat **i** vidljiv put korak-po-korak |
| **INSTRUCT** | Praćenje ograničenja formatiranja / instrukcija |
| **LONGFORM** | Koherentan tekst dugog oblika, na jeziku |
| **SEARCH** | Korištenje alata: kada nije siguran, poziva li **`web_search`**? |
| **TOOLBASE** | Diskriminacija alata: za osnovno znanje, odgovara **izravno** (ne poziva alat) |

Svaki odgovor se također provjerava na **izlaz u ciljanom jeziku / točnom pismu** — razmišljanje i odgovaranje na ciljanom jeziku, bez prebacivanja preko engleskog.

## Kako bodovanje funkcionira (deterministički)
Svaka os koristi fiksnu provjeru — bez subjektivnog prosuđivanja:
- `name` / `num` — točna činjenica/broj pojavljuje se u odgovoru
- `idk` — pojavljuje se marker iskrenosti (*"ne znam / ne mogu potvrditi"*, ovisno o jeziku)
- `graded` — pojavljuju se i stvarni entitet **i** marker iskrenosti
- `script` / `lang` — izlaz je u očekivanom pismu i jeziku
- `calc` / `calc_long` — konačni broj se podudara (dugi oblik također zahtijeva međukorake)
- `search` — model je aktivirao alat `web_search`; `notool` — odgovorio je bez njega

Ukupno: **/156**. Potpuno reproducibilno.

---

## Brzi start — testirajte vlastiti model

BalkanBench komunicira sa svakim modelom koji poslužuje **[Ollama](https://ollama.com)**.

```bash
# 1) Poslužite svoj model(e) putem Ollame
ollama pull olivilo/zora          # ili vaš vlastiti model, npr. ollama pull gemma2:9b

# 2) Pokrenite benchmark (Ollama endpoint zadano je localhost:11434)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Izlaz: **tablica bodova po osi** za svaki model, `/156`, plus detalji po odgovoru.
Usporedite bilo koji model — vaš fine-tune, bazni model, konkurent — na istih 156 zadataka.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

GPU nije potreban za samu infrastrukturu — Ollama pokreće model, benchmark samo boduje.

---

## Referentni rezultati (Zora v1.11, 8B)
Zora predvodi polje, nadmašujući modele 3–4× svoje veličine:

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
> značenja, dijalekte, pisma i kulturu — i biti **iskren** oko svojih ograničenja. Brzina je sekundarna.
> **Razumijevanje je presudno.**

Otvoreno, reproducibilno, izvorno međusobno provjereno. Prigovori i doprinosi su dobrodošli.
Od strane **Sovasoft** ([ai.in.rs](https://ai.in.rs)) uz **Akademija Ljiljana**.