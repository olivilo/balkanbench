🌐 [EN](README.md) · [SR](README.sr.md) · [HR](README.hr.md) · [BS](README.bs.md) · [MK](README.mk.md) · [SL](README.sl.md) · [SQ](README.sq.md) · [CNR](README.cnr.md) · [BG](README.bg.md) · [EL](README.el.md) · [TR](README.tr.md) · [RO](README.ro.md) · [HU](README.hu.md)

# BalkanBench 🦉

**Balkan ve Güneydoğu Avrupa dillerini *anlamak* için açık bir benchmark — hız için değil.**

Çoğu LLM benchmark'ı verimliliği ve İngilizce merkezli becerileri ölçer. **BalkanBench başka bir şeyi ölçer:** bir modelin bu dilleri —belirsizlikleri, eş sesli kelimeleri, alfabeyi, lehçeleri, kültürü— gerçekten *anlayıp anlamadığını* ve gerçekler uydurmak yerine **dürüst** olup olmadığını (bilmediğini kabul edip etmediğini).

> Amiral gemisi örnek: **„Горе горе горе горе него доле."** — dört kez *gore*, dört farklı anlam:
> *yukarıda · ormanlar/dağlar · [onlar] yanıyor · daha kötü.* → "Yukarıda, ormanlar aşağıdakinden daha kötü yanıyor."
> Bunu çözen bir model, dili sadece çevirmemiş, *anlamıştır*.

Model başına **13 eksen × 12 dil = 156 deterministik test** çalıştırır. API anahtarları yok, LLM-hakem yok — puanlama alfabe/anahtar kelime/sayı tabanlıdır, böylece herkes sonuçları yeniden üretebilir.

---

## 12 dil
Sırpça (sr), Hırvatça (hr), Boşnakça (bs), Makedonca (mk), Slovence (sl), Arnavutça (sq),
Karadağca (cnr), Bulgarca (bg), Yunanca (el), Türkçe (tr), Romence (ro), Macarca (hu).

Alfabe farkındalığı sisteme dahil edilmiştir: **Azbuka** (Kiril ≠ "sadece Kiril"), Latinica ve Yunanca her cevap için kontrol edilir — Makedonca'ya Latin alfabesiyle cevap veren bir model alfabe puanını kaybeder.

## 13 eksen (neler test ediliyor)

| Eksen | Ne ölçer |
|---|---|
| **FACT** | Balkan tarihi, kültürü ve coğrafyası hakkında gerçek bilgi |
| **HALLU** | Uydurma kişi/eser/olay → uydurmak yerine **"bilmiyorum" demeyi kabul ediyor mu**? |
| **DETAIL** | Gerçek varlık + uydurma bir detay → belirsizliği işaretliyor mu? |
| **GRADED** | Kademeli dürüstlük: kısmi bilgiyi (gerçek varlığı) gösterip uydurma detayı **reddetme** |
| **TEACH** | Bir konuyu **hedef dilde** öğretme/açıklama |
| **REASON** | Günlük akıl yürütme ve çıkarım |
| **LOGIC** | Kısa matematik/mantık — nihai sonuç doğru mu? |
| **LOGIC2** | İkinci bir mantık maddesi (dayanıklılık) |
| **ANALYSIS** | Daha uzun analiz — doğru sonuç **ve** görünür adım adım yol |
| **INSTRUCT** | Biçimlendirme / talimat kısıtlamalarına uyma |
| **LONGFORM** | Dil içinde, tutarlı uzun form metin |
| **SEARCH** | Araç kullanımı: emin olmadığında **`web_search` çağırıyor mu**? |
| **TOOLBASE** | Araç ayrımı: temel bilgiler için **doğrudan** cevap verme (araç çağırma) |

Her cevap ayrıca **dil içi / doğru alfabe** çıktısı için kontrol edilir — İngilizce üzerinden geçiş yapmak yerine, hedef dilde düşünme ve cevaplama.

## Puanlama nasıl çalışır (deterministik)
Her eksen sabit bir kontrol kullanır — öznel değerlendirme yoktur:
- `name` / `num` — doğru gerçek/sayı cevapta görünür
- `idk` — bir dürüstlük belirteci (*"bilmiyorum / onaylayamıyorum"*, dile göre) görünür
- `graded` — hem gerçek varlık **hem de** dürüstlük belirteci görünür
- `script` / `lang` — çıktı beklenen alfabe ve dildedir
- `calc` / `calc_long` — nihai sayı eşleşir (uzun form ara adımlar da gerektirir)
- `search` — model `web_search` aracını tetikledi; `notool` — araç olmadan cevapladı

Toplam: **/156**. Tamamen yeniden üretilebilir.

---

## Hızlı başlangıç — kendi modelinizi test edin

BalkanBench, **[Ollama](https://ollama.com)** tarafından sunulan herhangi bir modelle iletişim kurar.

```bash
# 1) Model(lerinizi) Ollama ile sunun
ollama pull olivilo/zora          # veya kendi modeliniz, örn. ollama pull gemma2:9b

# 2) Benchmark'ı çalıştırın (Ollama uç noktası varsayılan olarak localhost:11434'tür)
python3 matrix_ollama.py --models "olivilo/zora,gemma2:9b,qwen2.5:7b"
```

Çıktı: her model için **eksen başına puan tablosu**, `/156` ve cevap başına detaylar.
Herhangi bir modeli —ince ayar yaptığınız, temel bir model veya bir rakip— aynı 156 görev üzerinde karşılaştırın.

```
===== olivilo/zora =====
FACT 7/12  HALLU 10/12  DETAIL 8/12  GRADED 6/12  TEACH 12/12 ...
>>> olivilo/zora: 84/156
```

Harness'ın kendisi için GPU gerekmez — Ollama modeli çalıştırır, benchmark sadece puanlar.

---

## Referans sonuçlar (Zora v1.11, 8B)
Zora, kendisinden 3–4 kat daha büyük modelleri geride bırakarak alana öncülük ediyor:

| Model | Boyut | Puan |
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

## Felsefe
> Balkanlar için bir model, bu dilleri **içeriden** —çift anlamlarını, lehçelerini, alfabelerini ve kültürünü— anlamalı ve sınırları konusunda **dürüst** olmalıdır. Hız ikincildir.
> **Anlamak önemlidir.**

Açık, yeniden üretilebilir, yerel olarak çapraz kontrollü. Katkılarınız beklenmektedir.
**Sovasoft** ([ai.in.rs](https://ai.in.rs)) ve **Akademija Ljiljana** tarafından hazırlanmıştır.