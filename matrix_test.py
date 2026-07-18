#!/usr/bin/env python3
"""Volle Matrix: 6 Sprachen x 6 reale Aufgabentypen. Nur v3 (RAM-sicher).
Jede Aufgabe in korrekter Sprache/Schrift. Ausgabe -> json + lesbar."""
import re, json
from mlx_lm import load, generate
import os
from mlx_lm.sample_utils import make_sampler
MODEL=os.environ.get("MODEL","./model")  # Pfad zum lokalen MLX/HF-Modell (ENV MODEL=...)
def strip_think(t): return re.sub(r"<think>.*?</think>","",t or "",flags=re.S).strip()

# je Sprache: FACT(bekannt), HALLU(erfundene Person->darf NICHT erfinden), TEACH, REASON, INSTRUCT, LONGFORM
LANGS={
"sr":{"FACT":("Ko je napisao 'Na Drini ćuprija'? Kratko.","Ivo Andrić"),
 "HALLU":("Ko je bio srpski naučnik Radovan Petrović-Milošević i kada je živeo?","FALLE: ne postoji -> priznati neznanje"),
 "TEACH":("Objasni detetu šta je fotosinteza, u tačno 3 rečenice.","3 tačne rečenice"),
 "REASON":("Voz putuje 60 km/h. Koliko pređe za 2.5 sata? Reši korak po korak.","150 km"),
 "INSTRUCT":("Nabroji TAČNO tri reke u Srbiji, ćirilicom, svaku u jednoj reči.","3, azbuka"),
 "LONGFORM":("Napiši 4 koherentne rečenice o Beogradu.","4 rečenice")},
"hr":{"FACT":("Tko je napisao roman 'Povratak Filipa Latinovicza'? Kratko.","Miroslav Krleža"),
 "HALLU":("Tko je bio hrvatski pjesnik Tomislav Berišić-Kralj i kada je živio?","FALLE: ne postoji"),
 "TEACH":("Objasni djetetu što je gravitacija, u točno 3 rečenice.","3 tačne rečenice"),
 "REASON":("Kruh košta 8 kuna. Koliko koštaju 3 kruha? Objasni.","24 kn"),
 "INSTRUCT":("Nabroji TOČNO tri hrvatska grada, svaki u jednoj rečenici.","3"),
 "LONGFORM":("Napiši 4 koherentne rečenice o Zagrebu.","4 rečenice")},
"bs":{"FACT":("Ko je napisao roman 'Derviš i smrt'? Kratko.","Meša Selimović"),
 "HALLU":("Ko je bio bosanski pisac Alija Hodžić-Muratović i kada je živio?","FALLE: ne postoji"),
 "TEACH":("Objasni djetetu šta je kiša, u tačno 3 rečenice.","3 tačne rečenice"),
 "REASON":("Imaš 12 jabuka i podijeliš ih na 4 osobe. Koliko svako dobije? Objasni.","3"),
 "INSTRUCT":("Nabroji TAČNO tri grada u Bosni i Hercegovini, svaki u jednoj rečenici.","3"),
 "LONGFORM":("Napiši 4 koherentne rečenice o Sarajevu.","4 rečenice")},
"mk":{"FACT":("Кој го напиша романот 'Пиреј'? Кратко.","Петре М. Андреевски"),
 "HALLU":("Кој беше македонскиот поет Стеван Ристовски-Кочо и кога живееше?","ЗАМКА: не постои"),
 "TEACH":("Објасни му на дете што е Сонцето, во точно 3 реченици.","3 точни реченици"),
 "REASON":("Едно јаболко чини 10 денари. Колку чинат 5 јаболка? Објасни чекор по чекор.","50 денари"),
 "INSTRUCT":("Наброј ТОЧНО три града во Македонија, секој во една реченица.","3, кирилица"),
 "LONGFORM":("Напиши 4 кохерентни реченици за Скопје.","4 реченици")},
"sl":{"FACT":("Kdo je napisal povest 'Martin Krpan'? Na kratko.","Fran Levstik"),
 "HALLU":("Kdo je bil slovenski pesnik Janez Pregelj-Kovač in kdaj je živel?","PAST: ne obstaja"),
 "TEACH":("Otroku razloži, kaj je dež, v točno 3 stavkih.","3 pravilni stavki"),
 "REASON":("Ura dela stane 20 evrov. Koliko stanejo 3 ure? Pojasni.","60 EUR"),
 "INSTRUCT":("Naštej TOČNO tri slovenska mesta, vsako v enem stavku.","3"),
 "LONGFORM":("Napiši 4 koherentne stavke o Ljubljani.","4 stavki")},
"sq":{"FACT":("Kush e shkroi romanin 'Gjenerali i ushtrisë së vdekur'? Shkurt.","Ismail Kadare"),
 "HALLU":("Kush ishte poeti shqiptar Gjon Prendushi-Marku dhe kur jetoi?","KURTH: nuk ekziston"),
 "TEACH":("Shpjegoji një fëmije çfarë është shiu, në saktësisht 3 fjali.","3 fjali të sakta"),
 "REASON":("Një libër kushton 5 euro. Sa kushtojnë 4 libra? Shpjego.","20 euro"),
 "INSTRUCT":("Rendit SAKTËSISHT tre qytete të Shqipërisë, secili në një fjali.","3"),
 "LONGFORM":("Shkruaj 4 fjali koherente për Tiranën.","4 fjali")},
}
ORDER=["FACT","HALLU","TEACH","REASON","INSTRUCT","LONGFORM"]
m,tok=load(MODEL); samp=make_sampler(temp=0.3)
print("GELADEN\n"+"="*70)
res={}
for lang,tasks in LANGS.items():
    res[lang]={}
    for k in ORDER:
        q,rub=tasks[k]
        p=tok.apply_chat_template([{"role":"user","content":q}],add_generation_prompt=True,tokenize=False)
        a=strip_think(generate(m,tok,prompt=p,max_tokens=300,sampler=samp,verbose=False))
        res[lang][k]={"q":q,"rub":rub,"a":a}
        print(f"\n### {lang.upper()} / {k}  (soll: {rub})")
        print("A:", a[:400].replace("\n"," "))
import os
json.dump(res,open("results/matrix_raw.json","w"),ensure_ascii=False,indent=1)
print("\n"+"="*70+"\nFERTIG_MATRIX")
