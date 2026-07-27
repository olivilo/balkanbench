🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Odprti benchmark za *razumevanje* jezikov Balkana in Jugov Nitrate Evrope — ne za hitrost.**

Večina benchmarkov za LLM meri učinkovitost in veščine, ki so osredotočene na angleščino. **BalkanBench meri nekaj
drugega:** ali model zares *razume* te jezike — dvosmisljivost, homonime, pisavo, dialekte,
kulturo — in ali je **pošten** (prizna, česar ne ve), namesto da izmišlja dejstva.

> Glavni primer: **„Горе горе горе горе него доле."** — štirikrat *gore*, štiri pomeni:
> *zgoraj · gozdovi/gore · [oni] gorijo · slabše.* → "Zgoraj zgoraj, gozdovi gorijo slabše kot spodaj."
> Model, ki to razreši, je jezik *razumel*, ne le prevedel.

Izvede **13 osi × 12 jezikov = 156 determinističnih testov** na model. Brez API ključev, brez LLM-sodnika —
točkovanje temelji na pisavi/ključni besedi/številki, zato ga lahko kdorkoli ponovi.

---

## 12 jezikov
Srbski (sr), hrvaški (hr), bosanski (bs), makedonski (mk), slovenščina (sl), albanski (sq),
črnogorski (cnr), bulgarski (bg), grški (el), turški (tr), romunski (ro), madarščina (hu).

Zavedanje pisave je vgrajeno: **Azbuka** (kirilica ≠ "le kirilica"), Latinica in grščina so
preverjene za vsak odgovor — model, ki odgovori v makedonskem jeziku z latinsko pisavo, izgubi točko za pisavo.

## 13 osi (kaj se preveri)

| Os | Kaj meri |
|---|---|
| **FACT** | Resnično znanje o zgodovini, kulturi in geografiji Balkana |
| **HALLU** | Izmišljena oseba/delo/dogodek → ali **prizna "ne vem"**, namesto da fabricira? |
| **DETAIL** | Resen subjekt + izmišljen podrobnost → ali opozori na negotovost? |
| **GRADED** | Stopnjevana poštenost: pokaže delno znanje (resen subjekt) **in** zavrne izmišljeno podrobnost |
| **TEACH** | Poučevanje/razlaganje teme **v ciljnem jeziku** |
| **REASON** | Vsakdajev rozum in dedukcija |
| **LOGIC** | Kratek matematika/logika — je končni rezultat pravilen? |
| **LOGIC2** | Drugi logični element (robustnost) |
| **ANALYSIS** | Daljša analiza — pravilen rezultat **in** vidna pot korak za korakom |
| **INSTRUCT** | Sledenje oblikovanju / omejitvam navodil |
| **LONGFORM** | Koherenten dolg besedilo, v jeziku |
| **SEARCH** | Uporaba orodij: ko ni prepričan, ali **pokliče `web_search`**? |
| **TOOLBASE** | Razlikovanje orodij: za osnovno znanje odgovori **neposredno** (ne kliče orodja) |

Vsak odgovor je preverjen tudi za **izpis v jeziku / pravilni pisavi** — razmišljanje in odgovarjanje
v ciljnem jeziku, ne pa preko angleščine.

## Kako deluje točkovanje (deterministično)
Vsaka os uporablja fiksno preverjanje — brez subjektivnega ocenjevanja:
- `name` / `num` — pravilen dejstvo/številka se pojavi v odgovoru
- `idk` — marker poštenosti (*"ne vem / ne morem potrditi"*, glede jezika) se pojavi
- `graded` — resen subjekt **in** marker poštenosti se pojavita hkrati
- `script` / `lang` — izpis je v pričakovani pisavi in jeziku
- `calc` / `calc_long` — končna številka se ujema (dolga oblika zahteva tudi vmesne korake)
- `search` — model je sprožil orodje `web_search`; `notool` — je odgovoril brez njega

Skupaj: **/156**. Popolnoma ponovljivo.

---

## Hitri začetek — preizkusite svoj model

BalkanBench komunicira z vsakim modelom, ki ga streže **[Ollama](https://ollama.com)**.

```bash
# 1) Serve your model(s) with Ollama
ollama pull olivilo/zora          # or your own model, e.g. ollama pull gemma2:9b

# 2) Run the benchmark (Ollama endpoint defaults to localhost:11434)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Izpis: **tabela rezultatov po osi** za vsak model, `/156`, pluss podrobnosti za vsak odgovor.
Primerite poljubni model — vaš fine-tune, osnovni model, konkurenta — na istih 156 nalogah.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

Za sam okvir ni potrebnega GPU — Ollama poganja model, benchmark pa le točkuje.

---

## Referenčni rezultati (Zora v1.11, 8B)
Zora vodi na področju in premaga modele, ki so 3–4× večji:

| Model | Velikost | Rezultat |
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
> Model za Balkan mora razumeti te jezike **od znotraj** — njihove dvojne
> pomene, dialekte, pisave in kulturo — ter biti **pošten** glede svojih omejitev. Hitrost je sekundarna.
> **Razumevanje šteje.**

Odprto, ponovljivo, izvorno preverjeno. Prispevki so dobrodošli.
Avtor: **Sovasoft** ([ai.in.rs](https://ai.in.rs)) z **Akademija Ljiljana**.