🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Një benchmark i hapur për *kuptimin* e gjuhëve të Ballkanit dhe Evropës Juglindore — jo për shpejtësinë.**

Shumica e benchmark-eve të LLM masin efikasitetin dhe aftësitë e qendruara në anglisht. **BalkanBench mat diçka tjetër:** nëse një model vërtet i *kupton* këto gjuhë — ambiguitetin, homonimet, shkrimin, dialektin, kulturën — dhe nëse është **i ndershëm** (pranon atë që nuk di) në vend që të shpikë fakte.

> Shembulli kryesor: **„Горе горе горе горе него доле."** — katër herë *gore*, katër kuptime:
> *lart · pyje/male · [ata] digjen · më keq.* → "Lart, pyjet digjen më keq se poshtë."
> Një model që e zgjidh këtë e ka *kuptuar* gjuhën, jo thjesht e ka përkthyer atë.

Ai ekzekuton **13 akse × 12 gjuhë = 156 teste deterministike** për model. Pa çelësa API, pa LLM-judge — vlerësimi bazohet në skript/fjalë kyçe/numër, kështu që kushdo mund ta riprodhojë atë.

---

## 12 gjuhët
Serbisht (sr), Kroatisht (hr), Bosnisht (bs), Maqedonisht (mk), Sllovene (sl), Shqip (sq),
Malazezisht (cnr), Bullgarisht (bg), Greqisht (el), Turqisht (tr), Rumanisht (ro), Hungarisht (hu).

Njohja e shkrimit është e integruar: **Azbuka** (Kirilice ≠ "thjesht Kirilice"), Latinica dhe Greqishti kontrollohen për çdo përgjigje — një model që përgjigjet në Maqedonisht me shkrim latin humbet pikën e shkrimit.

## 13 akset (çfarë testohet)

| Aksi | Çfarë mat |
|---|---|
| **FACT** | Njohuri reale të historisë, kulturës dhe gjeografisë së Ballkanit |
| **HALLU** | Person/vepër/ngjarje e shpikur → a **pranon "nuk e di"** në vend që të fabrikojë? |
| **DETAIL** | Entitet real + një detaj i fabrikuar → a e sinjalizon pasigurinë? |
| **GRADED** | Ndershmëri e graduar: tregon njohuri të pjesshme (entitetin real) **dhe** refuzon detajin e shpikur |
| **TEACH** | Mësimi/shpjegimi i një teme **në gjuhën e synuar** |
| **REASON** | Arsyetim dhe inferencë e përditshme |
| **LOGIC** | Matematikë/logjikë e shkurtër — a është rezultati përfundimtar i saktë? |
| **LOGIC2** | Një element i dytë logjik (robustësia) |
| **ANALYSIS** | Analizë më e gjatë — rezultat i saktë **dhe** një rrugë e dukshme hap pas hapi |
| **INSTRUCT** | Ndjekja e kufizimeve të formatimit / udhëzimeve |
| **LONGFORM** | Tekst koherent i gjatë, në gjuhën përkatëse |
| **SEARCH** | Përdorimi i mjeteve: kur është i pasigurt, a **thërret `web_search`**? |
| **TOOLBASE** | Diskriminimi i mjeteve: për njohuri bazike, përgjigjet **direkt** (nuk thërret një mjet) |

Çdo përgjigje kontrollohet gjithashtu për output-in **në gjuhën përkatëse / shkrimin e saktë** — të menduarit dhe përgjigjja në gjuhën e synuar, pa kaluar përmes anglishtes.

## Si funksionon vlerësimi (deterministik)
Çdo aks përdor një kontroll të fiksuar — pa gjykime subjektive:
- `name` / `num` — fakti/numri i saktë shfaqet në përgjigje
- `idk` — një shenjë ndershmërie (*"nuk e di / nuk mund të konfirmoj"*, sipas gjuhës) shfaqet
- `graded` — entiteti real **dhe** një shenjë ndershmërie shfaqen të dyja
- `script` / `lang` — output-i është në shkrimin dhe gjuhën e pritshme
- `calc` / `calc_long` — numri përfundimtar përputhet (forma e gjatë kërkon gjithashtu hapa ndërmjetës)
- `search` — modeli aktivizoi mjetin `web_search`; `notool` — u përgjigj pa një të tillë

Totali: **/156**. Plotësisht i riprodhueshëm.

---

## Fillimi i shpejtë — testoni modelin tuaj

BalkanBench komunikon me çdo model që shërbehet nga **[Ollama](https://ollama.com)**.

```bash
# 1) Shërbeni modelin tuaj me Ollama
ollama pull olivilo/zora          # ose modeli juaj, p.sh. ollama pull gemma2:9b

# 2) Ekzekutoni benchmark-un (endpoint-i i Ollama është localhost:11434 secara default)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Output-i: një **tabelë pikësh për aks** për çdo model, `/156`, plus detaje për çdo përgjigje.
Krahasoni çdo model — fine-tune-in tuaj, një model bazë, një konkurent — në të njëjtat 156 detyra.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

Nuk kërkohet GPU për vetë strukturën e testimit — Ollama ekzekuton modelin, benchmark-u thjesht vlerëson.

---

## Rezultatet e referencës (Zora v1.11, 8B)
Zora udhëheq fushën, duke mposhtur modele 3–4 herë më të mëdha:

| Model | Madhësia | Pikët |
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

Modeli: **[huggingface.co/sovasoft/zora-v1.11](https://huggingface.co/sovasoft/zora-v1.11)**

## Filozofia
> Një model për Ballkanin duhet t'i kuptojë këto gjuhë **nga brenda** — kuptimet e tyre të dyfishta, dialektet, shkrimet dhe kulturën — dhe të jetë **i ndershëm** për kufizimet e tij. Shpejtësia është dytësore.
> **Kuptimi është ajo që vlen.**

I hapur, i riprodhueshëm, i kontrolluar nativisht në kryq. Kontributet janë të mirëkohruara.
Nga **Sovasoft** ([ai.in.rs](https://ai.in.rs)) me **Akademija Ljiljana**.