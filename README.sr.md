🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Otvoreni benchmark za *razumevanje* jezika Balkana i Jugoistočne Evrope — ne za brzinu.**

Većina LLM benchmark-ova meri efikasnost i veštine centrirane oko engleskog jezika. **BalkanBench meri nešto drugo:** da li model zaista *razume* ove jezike — dvosmislenost, homonime, pismo, dijalekte, kulturu — i da li je **iskren** (priznaje ono što ne zna) umesto da izmišlja činjenice.

> Flagship example: **„Горе горе горе горе него доле."** — četiri puta *gore*, četiri značenja:
> *gore (napolju/iznad) · gore (šume/planine) · gore (goreju) · gore (lošije).* → "Up above, the forests burn worse than below."
> Model koji ovo razreši je *razumeo* jezik, a ne samo ga preveo.

Pokreće **13 osa × 12 jezika = 156 determinističkih testova** po modelu. Bez API ključeva, bez LLM-sudije — bodovanje je zasnovano na pismu/ključnoj reči/broju, tako da ga svako može reprodukovati.

---

## 12 jezika
Serbian (sr), Croatian (hr), Bosnian (bs), Macedonian (mk), Slovenian (sl), Albanian (sq),
Montenegrin (cnr), Bulgarian (bg), Greek (el), Turkish (tr), Romanian (ro), Hungarian (hu).

Svest o pismu je ugrađena: **Azbuka** (Ćirilica ≠ "samo ćirilica"), Latinica i grčki se proveravaju po odgovoru — model koji odgovara na makedonskom jeziku koristeći latinicu gubi poen za pismo.

## 13 osa (šta se testira)

| Osa | Šta meri |
|---|---|
| **FACT** | Stvarno znanje o istoriji, kulturi i geografiji Balkana |
| **HALLU** | Izmišljena osoba/delo/događaj → da li **priznaje "ne znam"** umesto da fabricira? |
| **DETAIL** | Stvarni entitet + izmišljen detalj → da li signalizira nesigurnost? |
| **GRADED** | Gradirana iskrenost: pokazuje delimično znanje (stvarni entitet) **i** odbija izmišljeni detalj |
| **TEACH** | Podučavanje/objašnjavanje teme **na ciljnom jeziku** |
| **REASON** | Svakodnevno zaključivanje i inferencija |
| **LOGIC** | Kratka matematika/logika — da li je konačni rezultat tačan? |
| **LOGIC2** | Druga stavka logike (robustnost) |
| **ANALYSIS** | Duža analiza — tačan rezultat **i** vidljiv put korak-po-korak |
| **INSTRUCT** | Praćenje ograničenja formatiranja / instrukcija |
| **LONGFORM** | Koherentan dugački tekst, na jeziku |
| **SEARCH** | Korišćenje alata: kada nije siguran, da li **poziva `web_search`**? |
| **TOOLBASE** | Diskriminacija alata: za osnovno znanje, odgovara **direktno** (ne poziva alat) |

Svaki odgovor se takođe proverava za **izlaz na ciljnom jeziku / ispravnom pismu** — razmišljanje i odgovaranje na ciljnom jeziku, bez prebacivanja preko engleskog.

## Kako funkcioniše bodovanje (deterministički)
Svaka osa koristi fiksnu proveru — bez subjektivnog ocenjivanja:
- `name` / `num` — tačna činjenica/broj se pojavljuje u odgovoru
- `idk` — marker iskrenosti (*"ne znam / ne mogu da potvrdim"*, zavisno od jezika) se pojavljuje
- `graded` — i stvarni entitet **i** marker iskrenosti se pojavljuju
- `script` / `lang` — izlaz je na očekivanom pismu i jeziku
- `calc` / `calc_long` — konačni broj se poklapa (dugački oblik takođe zahteva međukorake)
- `search` — model je aktivirao `web_search` alat; `notool` — odgovorio je bez njega

Ukupno: **/156**. Potpuno reprodukovljivo.

---

## Brzi start — testirajte sopstveni model

BalkanBench komunicira sa bilo kojim modelom koji servisira **[Ollama](https://ollama.com)**.

```bash
# 1) Servirajte vaš model(e) pomoću Ollama
ollama pull olivilo/zora          # ili vaš sopstveni model, npr. ollama pull gemma2:9b

# 2) Pokrenite benchmark (Ollama endpoint podrazumevano je localhost:11434)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Izlaz: **tabela rezultata po osi** za svaki model, `/156`, plus detalji po odgovoru.
Uporedite bilo koji model — vaš fine-tune, bazni model, konkurenta — na istih 156 zadataka.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

GPU nije potreban za sam harness — Ollama pokreće model, benchmark samo boduje.

---

## Referentni rezultati (Zora v1.11, 8B)
Zora predvodi polje, pobedivši modele 3–4× svoje veličine:

| Model | Veličina | Rezultat |
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
> Model za Balkan mora razumeti ove jezike **iznutra** — njihova dvostruka značenja, dijalekte, pisma i kulturu — i biti **iskren** u vezi sa svojim ograničenjima. Brzina je sekundarna.
> **Razumevanje je presudno.**

Otvoreno, reprodukovljivo, izvorno međusobno provereno. Kontribucije su dobrodošle.
Od strane **Sovasoft** ([ai.in.rs](https://ai.in.rs)) uz **Akademija Ljiljana**.