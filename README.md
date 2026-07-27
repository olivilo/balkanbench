# BalkanBench 🦉

**Ein offener Benchmark für das *Verständnis* der Balkansprachen — nicht für Geschwindigkeit.**

Die meisten LLM-Benchmarks messen Effizienz und englisch-zentrierte Fähigkeiten.
**BalkanBench misst etwas anderes:** ob ein Modell die **Sprachen und Dialekte des Balkans
wirklich durchdringt** — Mehrdeutigkeit, Homonyme, Schrift, dialektale Feinheiten,
kulturelle Nuancen. Weniger „wie schnell", mehr „**hat es wirklich verstanden**".

Beispiel (das Flaggschiff): **„Горе горе горе горе него доле."**
Vier Mal „gore" — vier Bedeutungen: *oben · šume (Wälder/Berge) · gore [brennen] · schlimmer.*
Übersetzt: „Oben brennen die Wälder schlimmer als unten." Ein Modell, das das auflöst,
hat die Sprache verstanden — nicht nur übersetzt.

## Was getestet wird (Kategorien)
| Kategorie | Was |
|---|---|
| **Homonyme/Polysemie** | „gore", „grad" (Stadt/Hagel), „kosa" (Haar/Sense/Hang), „para" (Geld/Dampf) … |
| **Dialekt-Genauigkeit** | ekavica ↔ ijekavica (mleko/mlijeko), regionale Varianten |
| **Schrift-Treue** | Latinica ↔ **Azbuka** (≠ „Kyrillisch"), korrekte Transliteration |
| **Sprach-Trennung (BKMS)** | hleb/kruh, voz/vlak, hiljada/tisuća — richtiges Wort je Sprache |
| **Kultur/Sprichwörter** | Bedeutung regionaler Redewendungen |
| **In-language Reasoning** | denkt & erklärt es *in* der Sprache (statt englisch → übersetzt)? |

## Wer wird verglichen
Unser **`sovasoft/balkan`** gegen:
- **Yugo-/Balkan-LLMs:** YugoGPT, TildeOpen, EuroLLM …
- **Standardmodelle in diesen Sprachen:** Gemma, Mistral, Qwen (Basis) …

## Nutzung
```bash
# Modelle vorher lokal bereitstellen (Ollama) oder API-Endpoint angeben.
python3 run_bench.py --endpoint http://localhost:11434 \
    --models "sovasoft/balkan,gemma2:9b,mistral:7b,gordicaleksa/yugogpt"
# Ergebnisse: results/<modell>.jsonl  +  results/summary.md
```
Auto-Checks (Schrift/Sprache) laufen automatisch; **tiefes Verständnis** (Homonyme, Kultur)
wird per **LLM-Judge** vorbewertet und **menschlich gegengeprüft** (muttersprachlich).

## Philosophie
> Ein Modell für den Balkan muss die Balkansprachen **von innen** verstehen — ihre
> Doppeldeutigkeiten, ihre Dialekte, ihre Schriften, ihre Kultur. Geschwindigkeit ist
> zweitrangig. **Verständnis zählt.**

Offen, reproduzierbar, muttersprachlich gegengeprüft. Beiträge willkommen.
Von **Sovasoft** mit **Akademija Ljiljana**.
