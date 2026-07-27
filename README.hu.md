🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Egy nyílt benchmark a Balkan és Délkelet-Európa nyelveinek *értéséhez* — nem a sebességért.**

A legtöbb LLM benchmark az efficiency-t és az angol nyelvközpontú készségeket méri. **A BalkanBench valamást mér:** azt, hogy egy modell valóban *érti-e* ezeket a nyelveket — a többértelműségeket, homonimákat, írásmódokat, nyelvjárásokat, kultúrát — és hogy **őszinte-e** (beismeri-e, amit nem tud), ehelyett nem talál ит facts-eket.

> Flagship példa: **„Горе горе горе горе него доле."** — négyszer *gore*, négy jelentés:
> *felül · erdők/hegyek · égnek [gyulladnak] · rosszabb.* → "Felül az erdők rosszabbul égnek, mint alul."
> Egy modell, amely ezt feloldja, *értette* a nyelvet, nem csak lefordította.

Modellenként **13 tengely × 12 nyelv = 156 determinisztikus tesztet** futtat. Nincsenek API kulcsok, nincs LLM-bíró — a pontozás írásmód/kulcsszó/szám alapú, így bárki reprodukálhatja.

---

## A 12 nyelv
Szerb (sr), horvát (hr), bosnyák (bs), macedón (mk), szlovén (sl), albán (sq),
montenegrói (cnr), bolgár (bg), görög (el), török (tr), román (ro), magyar (hu).

Az írásmód-tudat beépítve: az **Azbuka** (cirill ≠ "csak cirill"), a Latinica és a görög írás minden válasznál ellenőrizésre kerül — egy modell, amely macedón nyelven latin betűkkel válaszol, elveszíti az írásmód pontját.

## A 13 tengely (mit tesztelünk)

| Tengely | Mit mér |
|---|---|
| **FACT** | Valódi ismeretek a Balkan történetéről, kultúrájáról, földrajzáról |
| **HALLU** | Kitalált személy/mű/esemény → **beismeri-e azt, hogy "nem tudom"** a fabrikálás helyett? |
| **DETAIL** | Valósi entitás + egy kitalált részlet → jelzi-e a bizonytalanságot? |
| **GRADED** | Fokozatos őszinteség: mutatja a részleges ismereteket (a valósi entitást) **és** elutasítja a kitalált részletet |
| **TEACH** | Egy téma tanítása/magyarázata **a célnyelven** |
| **REASON** | Mindennapi érvelés és következtetés |
| **LOGIC** | Rövid matek/logika — helyes a végeredmény? |
| **LOGIC2** | Egy második logika tétel (robusztusság) |
| **ANALYSIS** | Hosszabb elemzés — helyes eredmény **és** látható lépésről lépésre vezető út |
| **INSTRUCT** | Formázási / utasításbeli korlátok betartása |
| **LONGFORM** | Koherens, hosszú formátumú szöveg, a nyelven belül |
| **SEARCH** | Szövegkezelő eszközök: ha bizonytalan, **hívja-e a `web_search`** függvényt? |
| **TOOLBASE** | Eszközök differenciálása: alapvető ismereteknél válaszoljon **közvetlenül** (ne hívjon eszközt) |

Minden választ ellenőrizzük a **nyelven belüli / helyes írásmódú** kimenetre is — a célnyelven gondolkodva és válaszolva, nem pedig angol nyelven közvetítve.

## Hogyan működik a pontozás (determinisztikus)
Minden tengely egy fix ellenőrzést használ — nincs szubjektív ítélet:
- `name` / `num` — a helyes tény/szám szerepel a válaszban
- `idk` — egy őszinteségi jelző (*"nem tudom / nem tudom megerősíteni"*, nyelvspecifikusan) szerepel
- `graded` — a valósi entitás **és** az őszinteségi jelző mindkettő szerepel
- `script` / `lang` — a kimenet a várt írásmódban és nyelven van
- `calc` / `calc_long` — a végszám egyezik (a hosszú formátumnál köztes lépések is szükségesek)
- `search` — a modell kiváltotta a `web_search` eszközt; `notool` — eszköz nélkül válaszolt

Összesen: **/156**. Teljesen reprodukálható.

---

## Gyorsstart — teszteld saját modelledet

A BalkanBench bármelyik olyan modelllel kommunikál, amelyet az **[Ollama](https://ollama.com)** szolgál.

```bash
# 1) Szolgáld modelleidet Ollama-val
ollama pull olivilo/zora          # vagy saját modelled, pl. ollama pull gemma2:9b

# 2) Futtasd a benchmarkot (az Ollama végpont alapértelmezett értéke localhost:11434)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Kimenet: egy **tengelyenkénti ponttáblázat** minden modellhez, `/156`, valamint válaszonkénti részletek.
Összehasonlítsd bármelyik modellt — saját fine-tune-odat, egy alapmodellt vagy egy versenytársat — ugyanazon a 156 feladaton.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

A futtató környezethez nincs szükség GPU-ra — az Ollama futtatja a modellt, a benchmark csak pontoz.

---

## Referencia eredmények (Zora v1.11, 8B)
A Zora vezeti a mezőnyt, legyőzve a 3–4-szer nagyobb modelleket:

| Modell | Méret | Pontszám |
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

Modell: **[huggingface.co/sovasoft/zora-v1.11](https://huggingface.co/sovasoft/zora-v1.11)**

## Filozófia
> Egy Balkanra szánt modellnek **belülről** kell értenie ezeket a nyelveket — a többértelműségeket, nyelvjárásokat, írásmódokat és kultúrát — és **őszintenek** kell lennie a korlátai suhtában. A sebesség másodlagos.
> **Az értés számít.**

Nyílt, reprodukálható, natívan keresztellenőrzött. A hozzájárulásokat szívesen fogadjuk.
Készítette **Sovasoft** ([ai.in.rs](https://ai.in.rs)) az **Akademija Ljiljana** közreműködésével.