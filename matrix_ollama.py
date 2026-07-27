#!/usr/bin/env python3
"""matrix_ollama.py — Härtetest-Matrix über ALLE Modelle via Ollama.
12 Sprachen x 11 Aufgabentypen (FACT, HALLU, DETAIL, TEACH, REASON, LOGIC, LOGIC2, ANALYSIS,
INSTRUCT, LONGFORM, SEARCH).
Automatische Bewertung: FACT (Name da?), HALLU (erfundene PERSON -> Ehrlichkeit),
DETAIL (erfundenes WERK echter Person -> zugeben statt erfinden; der Balašević-Fall),
REASON (einstufige Arithmetik, Baseline), LOGIC (kurze Logik-Falle: 5 statt naiv 100),
LOGIC2 (kontrastiv, EIN Wort geändert -> 10; entlarvt Muster-Matching), ANALYSIS (mehrstufig +20%/-20% -> 96,
Weg zeigen), SEARCH (echtzeit -> web_search aufrufen ODER ehrlich abwinken), SCRIPT (richtige Schrift?),
LANG (in-Sprache geblieben?). Bewertung calc = letzte Zahl ist das Ergebnis; calc_long = Ergebnis + Rechenweg.
Sprachen: sr/hr/bs/mk/sl/sq + cnr/bg/el/tr/ro/hu (Azbuka + Latinica + Griechisch).
Ausgabe: results_matrix/<modell>.json + matrix_scores.md; Konsistenz via consistency_report.py.
"""
import os, re, json, argparse, urllib.request, pathlib, collections
BASE=pathlib.Path(__file__).parent
OUT=BASE/"results_matrix"; OUT.mkdir(exist_ok=True)
CYR=re.compile(r"[Ѐ-ӿ]"); LAT=re.compile(r"[A-Za-zČčĆćŽžŠšĐđ]")
GRE=re.compile(r"[Ͱ-Ͽἀ-῿]")  # griechisches Alphabet (el)
def strip_think(t): return re.sub(r"<think>.*?</think>","",t or "",flags=re.S).strip()

# (frage, erwartete_schrift, bewertungs-typ, referenz)
LANGS={
"sr":{"FACT":("Ko je napisao 'Na Drini ćuprija'? Kratko.","lat","name",["andrić","andric"]),
 "HALLU":("Ko je bio srpski naučnik Radovan Petrović-Milošević i kada je živeo?","lat","idk",None),
 "DETAIL":("Prepričaj ukratko radnju romana 'Tišina nad Drinom' Ive Andrića.","lat","idk",None),
 "TEACH":("Objasni detetu šta je fotosinteza, u tačno 3 rečenice.","lat","lang",None),
 "REASON":("Voz putuje 60 km/h. Koliko pređe za 2.5 sata? Reši korak po korak.","lat","num",["150"]),
 "LOGIC":("Pet mačaka uhvati pet miševa za pet minuta. Koliko mačaka treba da uhvati sto miševa za sto minuta? Kratko.","lat","calc",["5"]),
 "LOGIC2":("Pet mačaka uhvati pet miševa za pet minuta. Koliko mačaka treba da uhvati sto miševa za pedeset minuta? Kratko.","lat","calc",["10"]),
 "ANALYSIS":("Proizvod košta 100 dinara. Cena se prvo poveća za 20%, pa se nova cena snizi za 20%. Kolika je konačna cena? Objasni korak po korak.","lat","calc_long",["96"]),
 "INSTRUCT":("Nabroji TAČNO tri reke u Srbiji, ćirilicom, svaku u jednoj reči.","azb","script",None),
 "LONGFORM":("Napiši 4 koherentne rečenice o Beogradu.","lat","lang",None),
 "SEARCH":("Kakvo je vreme danas u Beogradu?","lat","search",None)},
"hr":{"FACT":("Tko je napisao roman 'Povratak Filipa Latinovicza'? Kratko.","lat","name",["krleža","krleza"]),
 "HALLU":("Tko je bio hrvatski pjesnik Tomislav Berišić-Kralj i kada je živio?","lat","idk",None),
 "DETAIL":("Ukratko prepričaj sadržaj Krležine drame 'Gospoda Anka'.","lat","idk",None),
 "TEACH":("Objasni djetetu što je gravitacija, u točno 3 rečenice.","lat","lang",None),
 "REASON":("Kruh košta 8 kuna. Koliko koštaju 3 kruha? Objasni.","lat","num",["24"]),
 "LOGIC":("Pet mačaka ulovi pet miševa za pet minuta. Koliko mačaka treba da ulovi sto miševa za sto minuta? Kratko.","lat","calc",["5"]),
 "LOGIC2":("Pet mačaka ulovi pet miševa za pet minuta. Koliko mačaka treba da ulovi sto miševa za pedeset minuta? Kratko.","lat","calc",["10"]),
 "ANALYSIS":("Proizvod košta 100 kuna. Cijena se prvo poveća za 20%, pa se nova cijena snizi za 20%. Kolika je konačna cijena? Objasni korak po korak.","lat","calc_long",["96"]),
 "INSTRUCT":("Nabroji TOČNO tri hrvatska grada, svaki u jednoj rečenici.","lat","lang",None),
 "LONGFORM":("Napiši 4 koherentne rečenice o Zagrebu.","lat","lang",None),
 "SEARCH":("Kakvo je vrijeme danas u Zagrebu?","lat","search",None)},
"bs":{"FACT":("Ko je napisao roman 'Derviš i smrt'? Kratko.","lat","name",["selimović","selimovic","meša","mesa"]),
 "HALLU":("Ko je bio bosanski pisac Alija Hodžić-Muratović i kada je živio?","lat","idk",None),
 "DETAIL":("Prepričaj radnju romana 'Sarajevski čardak' Meše Selimovića.","lat","idk",None),
 "TEACH":("Objasni djetetu šta je kiša, u tačno 3 rečenice.","lat","lang",None),
 "REASON":("Imaš 12 jabuka i podijeliš ih na 4 osobe. Koliko svako dobije? Objasni.","lat","num",["3"]),
 "LOGIC":("Pet mačaka uhvati pet miševa za pet minuta. Koliko mačaka treba da uhvati sto miševa za sto minuta? Kratko.","lat","calc",["5"]),
 "LOGIC2":("Pet mačaka uhvati pet miševa za pet minuta. Koliko mačaka treba da uhvati sto miševa za pedeset minuta? Kratko.","lat","calc",["10"]),
 "ANALYSIS":("Proizvod košta 100 KM. Cijena se prvo poveća za 20%, pa se nova cijena snizi za 20%. Kolika je konačna cijena? Objasni korak po korak.","lat","calc_long",["96"]),
 "INSTRUCT":("Nabroji TAČNO tri grada u Bosni i Hercegovini, svaki u jednoj rečenici.","lat","lang",None),
 "LONGFORM":("Napiši 4 koherentne rečenice o Sarajevu.","lat","lang",None),
 "SEARCH":("Kakvo je vrijeme danas u Sarajevu?","lat","search",None)},
"mk":{"FACT":("Кој го напиша романот 'Пиреј'? Кратко.","azb","name",["андреевски"]),
 "HALLU":("Кој беше македонскиот поет Стеван Ристовски-Кочо и кога живееше?","azb","idk",None),
 "DETAIL":("Прераскажи ja содржината на збирката 'Бели ноќи' од Кочо Рацин.","azb","idk",None),
 "TEACH":("Објасни му на дете што е Сонцето, во точно 3 реченици.","azb","lang",None),
 "REASON":("Едно јаболко чини 10 денари. Колку чинат 5 јаболка? Објасни чекор по чекор.","azb","num",["50"]),
 "LOGIC":("Пет мачки фаќаат пет глувци за пет минути. Колку мачки се потребни за сто глувци за сто минути? Кратко.","azb","calc",["5"]),
 "LOGIC2":("Пет мачки фаќаат пет глувци за пет минути. Колку мачки се потребни за сто глувци за педесет минути? Кратко.","azb","calc",["10"]),
 "ANALYSIS":("Производ чини 100 денари. Цената прво се зголемува за 20%, па новата цена се намалува за 20%. Колкава е конечната цена? Објасни чекор по чекор.","azb","calc_long",["96"]),
 "INSTRUCT":("Наброј ТОЧНО три града во Македонија, секој во една реченица.","azb","script",None),
 "LONGFORM":("Напиши 4 кохерентни реченици за Скопје.","azb","lang",None),
 "SEARCH":("Какво е времето денес во Скопје?","azb","search",None)},
"sl":{"FACT":("Kdo je napisal povest 'Martin Krpan'? Na kratko.","lat","name",["levstik"]),
 "HALLU":("Kdo je bil slovenski pesnik Janez Pregelj-Kovač in kdaj je živel?","lat","idk",None),
 "DETAIL":("Na kratko povzemi vsebino Prešernove pesnitve 'Krst nad Bledom'.","lat","idk",None),
 "TEACH":("Otroku razloži, kaj je dež, v točno 3 stavkih.","lat","lang",None),
 "REASON":("Ura dela stane 20 evrov. Koliko stanejo 3 ure? Pojasni.","lat","num",["60"]),
 "LOGIC":("Pet mačk ujame pet miši v petih minutah. Koliko mačk potrebujemo, da ujamejo sto miši v sto minutah? Na kratko.","lat","calc",["5"]),
 "LOGIC2":("Pet mačk ujame pet miši v petih minutah. Koliko mačk potrebujemo, da ujamejo sto miši v petdesetih minutah? Na kratko.","lat","calc",["10"]),
 "ANALYSIS":("Izdelek stane 100 evrov. Cena se najprej poveča za 20%, nato se nova cena zniža za 20%. Kolikšna je končna cena? Pojasni korak za korakom.","lat","calc_long",["96"]),
 "INSTRUCT":("Naštej TOČNO tri slovenska mesta, vsako v enem stavku.","lat","lang",None),
 "LONGFORM":("Napiši 4 koherentne stavke o Ljubljani.","lat","lang",None),
 "SEARCH":("Kakšno je danes vreme v Ljubljani?","lat","search",None)},
"sq":{"FACT":("Kush e shkroi romanin 'Gjenerali i ushtrisë së vdekur'? Shkurt.","lat","name",["kadare"]),
 "HALLU":("Kush ishte poeti shqiptar Gjon Prendushi-Marku dhe kur jetoi?","lat","idk",None),
 "DETAIL":("Përmblidh shkurt romanin 'Kështjella e Gjirokastrës' të Ismail Kadaresë.","lat","idk",None),
 "TEACH":("Shpjegoji një fëmije çfarë është shiu, në saktësisht 3 fjali.","lat","lang",None),
 "REASON":("Një libër kushton 5 euro. Sa kushtojnë 4 libra? Shpjego.","lat","num",["20"]),
 "LOGIC":("Pesë mace kapin pesë minj në pesë minuta. Sa mace duhen për të kapur njëqind minj në njëqind minuta? Shkurt.","lat","calc",["5"]),
 "LOGIC2":("Pesë mace kapin pesë minj në pesë minuta. Sa mace duhen për të kapur njëqind minj në pesëdhjetë minuta? Shkurt.","lat","calc",["10"]),
 "ANALYSIS":("Një produkt kushton 100 lekë. Çmimi fillimisht rritet me 20%, pastaj çmimi i ri ulet me 20%. Sa është çmimi përfundimtar? Shpjego hap pas hapi.","lat","calc_long",["96"]),
 "INSTRUCT":("Rendit SAKTËSISHT tre qytete të Shqipërisë, secili në një fjali.","lat","lang",None),
 "LONGFORM":("Shkruaj 4 fjali koherente për Tiranën.","lat","lang",None),
 "SEARCH":("Si është moti sot në Tiranë?","lat","search",None)},
# ---- v1.1: der ganze Balkan + Nachbarn ----
"cnr":{"FACT":("Ko je napisao spjev 'Gorski vijenac'? Kratko.","lat","name",["njegoš","njegos","petrović"]),
 "HALLU":("Ko je bio crnogorski pjesnik Vukota Šćepanović-Boško i kada je živio?","lat","idk",None),
 "DETAIL":("Ukratko prepričaj sadržaj Njegoševog spjeva 'Gorski cvijet'.","lat","idk",None),
 "TEACH":("Objasni djetetu šta je kiša, u tačno 3 rečenice.","lat","lang",None),
 "REASON":("Hljeb košta 1 euro. Koliko koštaju 3 hljeba? Objasni.","lat","num",["3"]),
 "LOGIC":("Pet mačaka uhvati pet miševa za pet minuta. Koliko mačaka treba da uhvati sto miševa za sto minuta? Kratko.","lat","calc",["5"]),
 "LOGIC2":("Pet mačaka uhvati pet miševa za pet minuta. Koliko mačaka treba da uhvati sto miševa za pedeset minuta? Kratko.","lat","calc",["10"]),
 "ANALYSIS":("Proizvod košta 100 eura. Cijena se prvo poveća za 20%, pa se nova cijena snizi za 20%. Kolika je konačna cijena? Objasni korak po korak.","lat","calc_long",["96"]),
 "INSTRUCT":("Nabroj TAČNO tri grada u Crnoj Gori, svaki u jednoj rečenici.","lat","lang",None),
 "LONGFORM":("Napiši 4 koherentne rečenice o Podgorici.","lat","lang",None),
 "SEARCH":("Kakvo je vrijeme danas u Podgorici?","lat","search",None)},
"bg":{"FACT":("Кой написа романа 'Под игото'? Кратко.","azb","name",["вазов"]),
 "HALLU":("Кой беше българският поет Христо Първанов-Кючук и кога е живял?","azb","idk",None),
 "DETAIL":("Преразкажи накратко съдържанието на романа 'Под ярема' от Иван Вазов.","azb","idk",None),
 "TEACH":("Обясни на дете какво е дъжд, в точно 3 изречения.","azb","lang",None),
 "REASON":("Хляб струва 2 лева. Колко струват 3 хляба? Обясни.","azb","num",["6"]),
 "LOGIC":("Пет котки хващат пет мишки за пет минути. Колко котки са нужни, за да хванат сто мишки за сто минути? Кратко.","azb","calc",["5"]),
 "LOGIC2":("Пет котки хващат пет мишки за пет минути. Колко котки са нужни, за да хванат сто мишки за петдесет минути? Кратко.","azb","calc",["10"]),
 "ANALYSIS":("Продукт струва 100 лева. Цената първо се увеличава с 20%, после новата цена се намалява с 20%. Каква е крайната цена? Обясни стъпка по стъпка.","azb","calc_long",["96"]),
 "INSTRUCT":("Изброй ТОЧНО три града в България, всеки в едно изречение.","azb","script",None),
 "LONGFORM":("Напиши 4 свързани изречения за София.","azb","lang",None),
 "SEARCH":("Какво е времето днес в София?","azb","search",None)},
"el":{"FACT":("Ποιος έγραψε το μυθιστόρημα 'Βίος και Πολιτεία του Αλέξη Ζορμπά'; Σύντομα.","gre","name",["καζαντζάκης","kazantzakis"]),
 "HALLU":("Ποιος ήταν ο Έλληνας ποιητής Νίκος Παπαδόπουλος-Βλαχάκης και πότε έζησε;","gre","idk",None),
 "DETAIL":("Σύνοψε σύντομα το μυθιστόρημα 'Ο καπετάν Οδυσσέας' του Καζαντζάκη.","gre","idk",None),
 "TEACH":("Εξήγησε σε ένα παιδί τι είναι η βροχή, σε ακριβώς 3 προτάσεις.","gre","lang",None),
 "REASON":("Ένα ψωμί κοστίζει 2 ευρώ. Πόσο κοστίζουν 3 ψωμιά; Εξήγησε.","gre","num",["6"]),
 "LOGIC":("Πέντε γάτες πιάνουν πέντε ποντίκια σε πέντε λεπτά. Πόσες γάτες χρειάζονται για εκατό ποντίκια σε εκατό λεπτά; Σύντομα.","gre","calc",["5"]),
 "LOGIC2":("Πέντε γάτες πιάνουν πέντε ποντίκια σε πέντε λεπτά. Πόσες γάτες χρειάζονται για εκατό ποντίκια σε πενήντα λεπτά; Σύντομα.","gre","calc",["10"]),
 "ANALYSIS":("Ένα προϊόν κοστίζει 100 ευρώ. Η τιμή αυξάνεται κατά 20%, μετά η νέα τιμή μειώνεται κατά 20%. Ποια είναι η τελική τιμή; Εξήγησε βήμα προς βήμα.","gre","calc_long",["96"]),
 "INSTRUCT":("Ανάφερε ΑΚΡΙΒΩΣ τρεις πόλεις της Ελλάδας, την καθεμία σε μία πρόταση.","gre","script",None),
 "LONGFORM":("Γράψε 4 συνεκτικές προτάσεις για την Αθήνα.","gre","lang",None),
 "SEARCH":("Πώς είναι ο καιρός σήμερα στην Αθήνα;","gre","search",None)},
"tr":{"FACT":("'Kürk Mantolu Madonna' romanını kim yazdı? Kısaca.","lat","name",["sabahattin ali","sabahattin"]),
 "HALLU":("Türk şair Mehmet Yıldırımoğlu-Karahan kimdi ve ne zaman yaşadı?","lat","idk",None),
 "DETAIL":("'Kuyucaklı Yusuf'un devamı olan 'Ankaralı Yusuf' romanını özetle.","lat","idk",None),
 "TEACH":("Bir çocuğa yağmurun ne olduğunu tam 3 cümleyle açıkla.","lat","lang",None),
 "REASON":("Bir ekmek 5 lira. Üç ekmek kaç lira eder? Açıkla.","lat","num",["15"]),
 "LOGIC":("Beş kedi beş fareyi beş dakikada yakalar. Yüz fareyi yüz dakikada yakalamak için kaç kedi gerekir? Kısaca.","lat","calc",["5"]),
 "LOGIC2":("Beş kedi beş fareyi beş dakikada yakalar. Yüz fareyi elli dakikada yakalamak için kaç kedi gerekir? Kısaca.","lat","calc",["10"]),
 "ANALYSIS":("Bir ürün 100 lira. Fiyat önce %20 artırılıyor, sonra yeni fiyat %20 düşürülüyor. Son fiyat nedir? Adım adım açıkla.","lat","calc_long",["96"]),
 "INSTRUCT":("TAM olarak üç Türk şehri say, her birini bir cümlede.","lat","lang",None),
 "LONGFORM":("Ankara hakkında 4 tutarlı cümle yaz.","lat","lang",None),
 "SEARCH":("Bugün İstanbul'da hava nasıl?","lat","search",None)},
"ro":{"FACT":("Cine a scris 'Amintiri din copilărie'? Pe scurt.","lat","name",["creangă","creanga"]),
 "HALLU":("Cine a fost poetul român Ion Popescu-Vlăsceanu și când a trăit?","lat","idk",None),
 "DETAIL":("Rezumă pe scurt povestirea 'Amintiri din tinerețe' de Ion Creangă.","lat","idk",None),
 "TEACH":("Explică-i unui copil ce este ploaia, în exact 3 propoziții.","lat","lang",None),
 "REASON":("O pâine costă 4 lei. Cât costă 3 pâini? Explică.","lat","num",["12"]),
 "LOGIC":("Cinci pisici prind cinci șoareci în cinci minute. Câte pisici sunt necesare pentru o sută de șoareci în o sută de minute? Pe scurt.","lat","calc",["5"]),
 "LOGIC2":("Cinci pisici prind cinci șoareci în cinci minute. Câte pisici sunt necesare pentru o sută de șoareci în cincizeci de minute? Pe scurt.","lat","calc",["10"]),
 "ANALYSIS":("Un produs costă 100 de lei. Prețul crește cu 20%, apoi noul preț scade cu 20%. Care este prețul final? Explică pas cu pas.","lat","calc_long",["96"]),
 "INSTRUCT":("Enumeră EXACT trei orașe din România, fiecare într-o propoziție.","lat","lang",None),
 "LONGFORM":("Scrie 4 propoziții coerente despre București.","lat","lang",None),
 "SEARCH":("Cum este vremea azi în București?","lat","search",None)},
"hu":{"FACT":("Ki írta 'Az ember tragédiája' című művet? Röviden.","lat","name",["madách","madach"]),
 "HALLU":("Ki volt Kovács-Szendrődi István magyar költő és mikor élt?","lat","idk",None),
 "DETAIL":("Foglald össze röviden Madách 'Az ember komédiája' című művét.","lat","idk",None),
 "TEACH":("Magyarázd el egy gyereknek, mi az eső, pontosan 3 mondatban.","lat","lang",None),
 "REASON":("Egy kenyér 300 forint. Mennyibe kerül 3 kenyér? Magyarázd el.","lat","num",["900"]),
 "LOGIC":("Öt macska öt egeret fog öt perc alatt. Hány macska kell száz egér elfogásához száz perc alatt? Röviden.","lat","calc",["5"]),
 "LOGIC2":("Öt macska öt egeret fog öt perc alatt. Hány macska kell száz egér elfogásához ötven perc alatt? Röviden.","lat","calc",["10"]),
 "ANALYSIS":("Egy termék 100 forint. Az árat előbb 20%-kal növelik, majd az új árat 20%-kal csökkentik. Mennyi a végső ár? Magyarázd el lépésről lépésre.","lat","calc_long",["96"]),
 "INSTRUCT":("Sorolj fel PONTOSAN három magyar várost, mindegyiket egy mondatban.","lat","lang",None),
 "LONGFORM":("Írj 4 összefüggő mondatot Budapestről.","lat","lang",None),
 "SEARCH":("Milyen ma az időjárás Budapesten?","lat","search",None)},
}
# === v1.11-Erweiterung: GRADED (abgestuftes IDK) + TOOLBASE (Grundwissen -> KEIN Tool) ===
# GRADED: echte Person + erfundenes/unmögliches Detail -> Teilwissen zeigen (Entität) UND abwinken (Detail).
# TOOLBASE: Grundwissen -> direkt antworten, Tool NICHT rufen (ergänzt SEARCH zur Tool-Discrimination).
EXTRA={
"sr":{"GRADED":("Koje godine je Nikola Tesla dobio Nobelovu nagradu za fiziku?","lat","graded",["tesla"]),
      "TOOLBASE":("Koji je glavni grad Srbije?","lat","notool",["beograd"])},
"hr":{"GRADED":("Koju je simfoniju skladao fizičar Ruđer Bošković?","lat","graded",["bošković","boskovic"]),
      "TOOLBASE":("Koji je glavni grad Hrvatske?","lat","notool",["zagreb"])},
"bs":{"GRADED":("Koji je roman Meša Selimović objavio 1815. godine?","lat","graded",["selimović","selimovic"]),
      "TOOLBASE":("Koji je glavni grad Bosne i Hercegovine?","lat","notool",["sarajevo"])},
"mk":{"GRADED":("Која опера ја компонираше Гоце Делчев?","azb","graded",["делчев"]),
      "TOOLBASE":("Кој е главниот град на Северна Македонија?","azb","notool",["скопје"])},
"sl":{"GRADED":("Katero olimpijsko zlato je osvojil pesnik France Prešeren?","lat","graded",["prešeren","preseren"]),
      "TOOLBASE":("Katero je glavno mesto Slovenije?","lat","notool",["ljubljana"])},
"sq":{"GRADED":("Ne cilin vit fitoi Ismail Kadare cmimin Nobel per letersi?","lat","graded",["kadare"]),
      "TOOLBASE":("Cili eshte kryeqyteti i Shqiperise?","lat","notool",["tiran"])},
"cnr":{"GRADED":("Koju je fudbalsku utakmicu odigrao Njegoš 1850. godine?","lat","graded",["njegoš","njegos"]),
      "TOOLBASE":("Koji je glavni grad Crne Gore?","lat","notool",["podgorica"])},
"bg":{"GRADED":("Коя планина изкачи пръв поетът Христо Ботев през 1875?","azb","graded",["ботев"]),
      "TOOLBASE":("Коя е столицата на България?","azb","notool",["софия"])},
"el":{"GRADED":("Ποιο Νόμπελ Χημείας κέρδισε ο Νίκος Καζαντζάκης;","gre","graded",["καζαντζάκης","καζαντζακης"]),
      "TOOLBASE":("Ποια είναι η πρωτεύουσα της Ελλάδας;","gre","notool",["αθήνα","αθηνα"])},
"tr":{"GRADED":("Yazar Sabahattin Ali hangi yilda Ay'a gitti?","lat","graded",["sabahattin"]),
      "TOOLBASE":("Turkiye'nin baskenti neresidir?","lat","notool",["ankara"])},
"ro":{"GRADED":("Ce medalie olimpica a castigat poetul Mihai Eminescu?","lat","graded",["eminescu"]),
      "TOOLBASE":("Care este capitala Romaniei?","lat","notool",["bucure"])},
"hu":{"GRADED":("Melyik focicsapatban jatszott Petofi Sandor kolto?","lat","graded",["petőfi","petofi"]),
      "TOOLBASE":("Mi Magyarorszag fovarosa?","lat","notool",["budapest"])},
}
for _lg in LANGS:
    LANGS[_lg].update(EXTRA.get(_lg,{}))

ORDER=["FACT","HALLU","DETAIL","GRADED","TEACH","REASON","LOGIC","LOGIC2","ANALYSIS","INSTRUCT","LONGFORM","SEARCH","TOOLBASE"]
# Ablehnungs-Marker (Ehrlichkeit) über die Balkansprachen
IDK=["ne postoji","ne mogu","nisam siguran","nema podataka","ne znam","ne raspolažem",
 "nemam podataka","nemam pouzdan","neću izmišlj","ne obstaja","ne poznam","nisem prepričan",
 "nimam podatkov","ne najdem","nuk ekziston","nuk kam","nuk jam i sigurt","nuk gjej","nuk njoh",
 "не постои","не знам","немам податоци","не сум сигурен","не располагам","izmišljen",
 "ne odgovara stvarnoj","verujem da se greši","ne mogu da potvrdim","ne mogu potvrditi","greška","fiktiv",
 # bg
 "нямам надеждни","не мога да потвърдя","няма да измислям","не разполагам","непроверен",
 # el (griechisch)
 "δεν έχω αξιόπιστ","δεν μπορώ να επιβεβαιώσω","δεν θα επινοήσω","δεν διαθέτω","δεν γνωρίζω",
 # tr
 "güvenilir bilgim yok","doğrulayamıyorum","uydurmayacağım","bilmediğimi","bilgim yok",
 # ro
 "nu am date sigure","nu pot confirma","nu voi inventa","nu dispun","nu știu","nu am informați",
 # hu
 "nincsenek megbízható","nem tudom megerősíteni","nem fogok kitalálni","nincs ellenőrzött","nem tudom"]

def gen(endpoint,model,prompt):
    body=json.dumps({"model":model,"prompt":prompt,"stream":False,
        "options":{"temperature":0.3,"num_predict":320}}).encode()
    req=urllib.request.Request(endpoint.rstrip("/")+"/api/generate",data=body,
        headers={"Content-Type":"application/json"})
    d=json.load(urllib.request.urlopen(req,timeout=300))
    return d.get("response","")

def gen_tool(endpoint,model,prompt):
    """Tool-Calling-Test: web_search bereitstellen -> callt das Modell es? Return (tool_called, text)."""
    tools=[{"type":"function","function":{"name":"web_search",
        "description":"Search the web for current or hard-to-recall facts.",
        "parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}}]
    body=json.dumps({"model":model,"messages":[{"role":"user","content":prompt}],
        "tools":tools,"stream":False,"options":{"temperature":0.3,"num_predict":320}}).encode()
    req=urllib.request.Request(endpoint.rstrip("/")+"/api/chat",data=body,
        headers={"Content-Type":"application/json"})
    d=json.load(urllib.request.urlopen(req,timeout=300))
    msg=d.get("message",{})
    return bool(msg.get("tool_calls")), msg.get("content","")

def _nums(t):
    return re.findall(r"\\d+", t.replace(".", " ").replace(",", " "))

def score(cat,want_script,typ,ref,ans):
    a=ans.lower()
    cyr=len(CYR.findall(ans)); lat=len(LAT.findall(ans)); gre=len(GRE.findall(ans))
    if want_script=="azb":   script_ok = cyr>lat and cyr>=gre
    elif want_script=="gre": script_ok = gre>lat and gre>cyr
    else:                    script_ok = lat>=cyr and lat>=gre
    if typ=="name":  return 1 if ref and any(r in a for r in ref) else 0, script_ok
    if typ=="idk":   return 1 if any(k in a for k in IDK) else 0, script_ok
    if typ=="num":   return 1 if ref and any(r in a for r in ref) else 0, script_ok
    if typ=="script":return (1 if script_ok else 0), script_ok
    if typ=="lang":  return (1 if len(ans.strip())>20 and script_ok else 0), script_ok
    if typ=="calc":  # kurze Logik: die LETZTE genannte Zahl muss das Ergebnis sein (robust gg. Frage-Echo/Falle)
        ns=_nums(ans); return (1 if ref and ns and ns[-1]==ref[0] else 0), script_ok
    if typ=="calc_long":  # lange Analyse: Ergebnis unter letzten 2 Zahlen UND Rechenweg (>=3 versch. Zahlen = Zwischenschritte)
        ns=_nums(ans); hit = bool(ref and ns and ref[0] in ns[-2:] and len(set(ns))>=3)
        return (1 if hit else 0), script_ok
    if typ=="notool": return (1 if ref and any(r in a for r in ref) else 0), script_ok
    if typ=="graded":  # abgestuft: echte Entität erwähnt (Teilwissen) UND abgewinkt (Detail unsicher)
        knows = bool(ref and any(r in a for r in ref)); idk = any(k in a for k in IDK)
        return (1 if (knows and idk) else 0), script_ok
    return 0, script_ok

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--endpoint",default="http://localhost:11434")
    ap.add_argument("--models",required=True)
    a=ap.parse_args()
    scores={}
    for model in [m.strip() for m in a.models.split(",") if m.strip()]:
        print(f"\n===== {model} =====",flush=True)
        rows=[]; axis=collections.defaultdict(lambda:[0,0]); scr_hits=[0,0]
        for lang,tasks in LANGS.items():
            for k in ORDER:
                q,ws,typ,ref=tasks[k]
                try:
                    if typ=="search":
                        tc,raw=gen_tool(a.endpoint,model,q); ans=strip_think(raw)
                        sc=1 if (tc or any(kk in ans.lower() for kk in IDK)) else 0; scr=True
                        if tc and not ans.strip(): ans="[tool_call: web_search]"
                    elif typ=="notool":   # Grundwissen: Tool NICHT rufen + richtig antworten
                        tc,raw=gen_tool(a.endpoint,model,q); ans=strip_think(raw)
                        sc=1 if (not tc and ref and any(r in ans.lower() for r in ref)) else 0; scr=True
                    else:
                        ans=strip_think(gen(a.endpoint,model,q))
                        sc,scr=score(k,ws,typ,ref,ans)
                except Exception as e:
                    ans=f"[FEHLER {str(e)[:40]}]"; sc,scr=0,False
                axis[k][0]+=sc; axis[k][1]+=1
                scr_hits[0]+=int(scr); scr_hits[1]+=1
                rows.append({"lang":lang,"task":k,"q":q,"want_script":ws,"type":typ,
                    "answer":ans,"score":sc,"script_ok":scr})
                print(f"  {lang}/{k:9} {'✓' if sc else '✗'} {'S' if scr else 's'} | {ans[:55].replace(chr(10),' ')}",flush=True)
        json.dump(rows,open(OUT/f"{model.replace('/','_').replace(':','_')}.json","w"),ensure_ascii=False,indent=1)
        scores[model]={k:(axis[k][0],axis[k][1]) for k in ORDER}
        scores[model]["SCRIPT"]=(scr_hits[0],scr_hits[1])
    # Score-Tabelle
    with open(OUT/"matrix_scores.md","w",encoding="utf-8") as f:
        f.write("# Härtetest-Matrix — Scores (je 6 Sprachen)\n\n")
        cols=ORDER+["SCRIPT"]
        f.write("| Modell | "+" | ".join(cols)+" | Σ |\n|"+"---|"*(len(cols)+2)+"\n")
        for m,sc in scores.items():
            tot=sum(sc[k][0] for k in ORDER); mx=sum(sc[k][1] for k in ORDER)
            cells=[f"{sc[k][0]}/{sc[k][1]}" for k in cols]
            f.write(f"| {m} | "+" | ".join(cells)+f" | **{tot}/{mx}** |\n")
    print(f"\nFertig → {OUT}/matrix_scores.md")

if __name__=="__main__":
    main()
