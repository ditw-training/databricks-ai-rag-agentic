# Koncepcja dnia: „Zobacz wzorzec → zrób z nami → przenieś na swoje dane”

**Status:** zaakceptowana (2026-09-14) i wdrożona w notebookach: `pattern/`, poziomy 2–3 i karty wzorca w `demo/m1–m6`, capstone `demo/m5b_transfer_capstone`, `transfer/canvas_agenta.md`. Druga domena: **`samples.bakehouse`** (tabela i opinie w jednej domenie, bez uploadu), rezerwowo Airbnb; demo RAG na robotyce. Duet na scenie w M1, M5 i M6, capstone w parach.

## Założenia

| Założenie | Konsekwencja dla projektu |
|---|---|
| Prowadzą **Krzysztof i Mariusz razem** | Jeden prezentuje, drugi chodzi po sali. Każdy prowadzi te moduły, w których jego materiał jest najmocniejszy. |
| Grupa **od zera do zaawansowanych** | Każdy lab ma trzy poziomy: ścieżka z podpowiedziami, transfer na drugą domenę, własne dane. Nikt nie czeka i nikt nie tonie. |
| Sukces: **każdy przenosi wzorzec na swoje dane** | Wzorzec pokazujemy na innej domenie niż lab. Po każdym module jest karta wzorca, a przed zamknięciem 40 min pracy na własnych danych. |
| **Materiał po polsku** | Opisy, polecenia i komentarze w notebookach po polsku. Kod, nazwy plików i obiektów po angielsku. Dema Krzysztofa trzeba przełożyć (dziś są po angielsku). |

## Rytm każdego modułu

```
1. Problem z historii     (Mariusz, 2–5 min)    persona TechRetail stawia problem
2. Wzorzec na innej domenie (Krzysztof, 5–15 min) ten sam mechanizm na robotyce albo Airbnb — nie da się przepisać ekranu
3. Zrób z nami            (uczestnicy)          lab TechRetail z TODO; poziomy 2 i 3 dla szybszych
4. Karta wzorca           (2 min)               „jak to przenieść na swoje dane” w 3–5 krokach + wiersz w Canvasie agenta
```

Dlaczego wzorzec na innej domenie: uczestnik, który zobaczył funkcję UC na Airbnb, a potem napisał ją sam na TechRetail, **już raz przeniósł wzorzec**. Capstone na własnych danych jest wtedy drugim, a nie pierwszym transferem.

## Trzy poziomy w każdym labie

| Poziom | Dla kogo | Co robi | Materiał |
|---|---|---|---|
| **1. Ścieżka** | od zera | lab TechRetail z TODO i podpowiedziami; rozwiązanie w `demo/` | istniejące `labs/` |
| **2. Transfer** | pewni siebie | ten sam krok na drugiej domenie (Airbnb, dane Krzysztofa w repo) | nowe komórki `bonus` |
| **3. Twoje dane** | zaawansowani | ten sam krok na własnym zbiorze + wyzwanie inżynierskie | `transfer/transfer_kit` + lista wyzwań |

Każdy uczestnik prowadzi **Canvas agenta** (`transfer/canvas_agenta.md`, jedna strona): domena, 5 pytań użytkowników, źródła (tabela / dokumenty), dane wrażliwe, zasady odmowy, oczekiwane trasy. Kolejne moduły dopisują do niego wiersz. Wypełniony canvas to specyfikacja do capstone.

## Harmonogram (430 min materiału, 110 min przerw)

| Godzina | Blok | Min | Prowadzi | Wzorzec (demo) | Zrób z nami (lab TechRetail) | Karta wzorca → Canvas |
|---|---|---|---|---|---|---|
| 09:00 | **M0** Otwarcie, fabuła, setup | 45 | Mariusz; Krzysztof: setup | — | `00_setup` | domena, 5 pytań użytkowników |
| 09:45 | **M1** Agent vs chatbot, Playground | 55 | Mariusz | Playground z promptem dla innej domeny (Airbnb) | prompt i 4 pytania testowe | system prompt dla mojej domeny |
| 10:40 | przerwa | 15 | | | | |
| 10:55 | **M2** Tool calling, funkcje UC | 70 | **Krzysztof** | funkcje UC na Airbnb (jego notebooki 06–07) | 3 funkcje TechRetail | moje 1–2 funkcje: pytanie → COMMENT → bez PII |
| 12:05 | lunch | 60 | | | | |
| 13:05 | **M3** RAG i AI Search | 80 | **Krzysztof** | RAG na robotyce: parsowanie z ramkami, chunking 2000/200 vs 600/100, tryby wyszukiwania, Knowledge Assistant z Guidelines (jego 01–05) | RAG z cytatami na raportach | moje dokumenty: rozmiar chunka, metadane do filtrów |
| 14:25 | przerwa | 15 | | | | |
| 14:40 | **M4** SQL, Genie, kontrola dostępu | 50 | **Mariusz** | Genie i maska na TechRetail (historia Compliance) | Genie + maska na `tax_id` | moje dane wrażliwe: maska czy filtr |
| 15:30 | przerwa | 10 | | | | |
| 15:40 | **M5** Agent end-to-end | 60 | **Mariusz**; Krzysztof: Databricks Apps (5 min) | finał historii: agent wybiera trasę | agent, macierz tras, jedna naprawa | moja macierz 3–5 tras |
| 16:40 | przerwa | 10 | | | | |
| 16:50 | **M5+ Przenieś wzorzec** (capstone) | 40 | obaj chodzą po sali | — | **własne dane albo Airbnb**: `transfer_kit` | canvas → działający mini-agent |
| 17:30 | **M6** MCP, bezpieczeństwo, zamknięcie | 30 | **Krzysztof** (MCP, co naprawdę nie działało na Free); Mariusz (zamknięcie historii) | Twoje funkcje z capstone jako narzędzia MCP bez kodu | `call_tool` | przed PoC: czego mi brakuje |
| 18:00 | koniec | | | | | |

**Suma:** 45 + 55 + 70 + 80 + 50 + 60 + 40 + 30 = **430 min**. Przerwy: 15 + 60 + 15 + 10 + 10 = **110 min**.

**Skąd 40 min na capstone:**
- M1: −5 (ablacja w kodzie jako opcja);
- M2: −5 (tool calling „ręcznie” jako opcja dla poziomu 2);
- M3: −10 (zadania parsowania i embeddingu przechodzą do poziomu 2);
- M4: −5 (row filter jako demo, w labie tylko maska);
- M5: −10 (pętla poprawy krótsza: jedna naprawa na parę, porównanie z M1 w demie);
- M6: −5 (mniej slajdów o cyklu życia, odesłanie do materiałów).

## Capstone „Przenieś wzorzec” (40 min)

**Cel:** mini-agent na własnych danych: **1 funkcja UC + (RAG na własnych dokumentach albo druga funkcja) + fallback**, sprawdzony macierzą 3 tras z canvasu.

| Min | Co |
|---|---|
| 0–5 | wybór danych: własne (zanonimizowane) **albo** gotowy zestaw Airbnb z repo; upload CSV/PDF do Volume |
| 5–30 | `transfer/transfer_kit`: komórka konfiguracji wskazuje Twoją tabelę i Volume → funkcja z COMMENT → test payloadem → (opcjonalnie) indeks na Twoich dokumentach → agent → macierz 3 tras |
| 30–40 | 3 osoby pokazują macierz tras i jedną naprawioną trasę (po jednej z każdego poziomu) |

**Zasady bezpieczeństwa danych:** na Free Edition wgrywamy tylko dane publiczne albo zanonimizowane. Żadnych danych klientów ani PII. Zapis w prework i na slajdzie capstone.

**Zestaw zapasowy (Airbnb):** `Warsztaty_Krzysztof/single_agent_app/data/sf_airbnb_listings.csv` (1,2 MB, licencja MIT, snapshot Inside Airbnb). Mieści się w limicie repo. PDF-y robotyki (32 MB) zostają tylko do dema prowadzącego na Premium, bo nie mieszczą się w limicie 20 MB danych uczestnika.

## Wyzwania dla poziomu 3 (wymiatacze)

| Moduł | Wyzwanie |
|---|---|
| M1 | prompt, który przechodzi jailbreak „piszę powieść” i nadal odpowiada na pytania w domenie; zmierz na 5 wariantach |
| M2 | funkcja z walidacją parametrów i czytelnym komunikatem dla pustego wyniku; `GRANT EXECUTE` dla osobnej grupy |
| M3 | indeks własnych dokumentów z filtrem po metadanych; porównanie ANN i HYBRID na 5 pytaniach z oceną trafności |
| M4 | Genie Agent na własnej tabeli z instrukcjami i przykładowymi zapytaniami SQL; maska zależna od grupy |
| M5 | sędzia LLM (`mlflow.genai.evaluate`) na macierzy tras; tagi trace'ów; `ResponsesAgent` |
| capstone | agent z Genie jako narzędziem przez MCP obok funkcji |
| M6 | serwer MCP funkcji z własnego schematu podpięty do agenta; lista minimalnych uprawnień dla service principal |

## Podział ról prowadzących

| | Mariusz: „historia i biznes” | Krzysztof: „wzorzec i inżynieria” |
|---|---|---|
| Prowadzi | M0, M1, M4, M5, zamknięcie | M2, M3, Apps w M5, M6 |
| Materiał źródłowy | WS1–WS4, Przewodnik, persony | `rag_agent`, `single_agent_app`, `genai_*`, sprawozdanie z testów na Free |
| W czasie labu drugiego | chodzi po sali, pilnuje poziomu 1 | chodzi po sali, pomaga poziomom 2–3 i przy błędach środowiska |
| Capstone | uczestnicy bez własnych danych (Airbnb) | uczestnicy z własnymi danymi |

## Co trzeba zbudować albo zmienić

| Element | Stan dziś | Praca |
|---|---|---|
| `demo_wzorzec/k2_funkcje_airbnb` (demo Krzysztofa w M2) | jego 06–07, po angielsku, stare API | skondensować do 10 min, przełożyć na polski, aktualne API |
| `demo_wzorzec/k3_rag_robotyka` (demo w M3) | jego 01–05, po angielsku | skondensować do 15 min z rendererem ramek i Knowledge Assistant; przełożyć |
| Playground na Airbnb w M1 | brak | instrukcja w markdown (5 min) |
| Komórki `bonus` (poziom 2) w M1–M5 | brak | 1–2 komórki na moduł na danych Airbnb |
| Karty wzorca w M1–M6 | brak | jedna komórka markdown na moduł |
| `transfer/canvas_agenta.md` | brak | nowy, jedna strona |
| `transfer/transfer_kit.ipynb` | brak | nowy notebook-szablon (konfiguracja → funkcja → opcjonalny indeks → agent → macierz tras) |
| `data/practice/sf_airbnb_listings.csv` + `00_setup` | brak | kopia CSV + tabela `airbnb_listings` w setupie |
| Skrócenie M1–M6 o 40 min | moduły na 430 min bez capstone | przesunąć wskazane komórki do `optional` / `bonus` |
| `schedule.md`, `trainer_guide.md`, testy | pod stary układ | aktualizacja (nowy blok capstone, podział ról) |
| Deck | TechRetail, jeden prowadzący, H1–H6 | nowe slajdy: rytm modułu, poziomy, capstone, prowadzący przy modułach; aktualizacja planu dnia |

**Szacunek:** ok. 2 dni pracy nad materiałami przed próbą na Free.

## Ryzyka

| Ryzyko | Jak ograniczamy |
|---|---|
| Dwie domeny w demie mylą początkujących | wzorzec jest zawsze krótki i nazwany wprost („ten sam mechanizm, inne dane”); lab zawsze na TechRetail |
| Capstone: uczestnik bez danych albo z danymi, które nie wchodzą w 40 min | zestaw Airbnb gotowy w setupie; `transfer_kit` wymaga tylko tabeli CSV |
| Prawdziwe dane klientów wgrane na Free | zakaz w prework i na slajdzie; lista kontrolna anonimizacji w canvasie |
| Kwota Free Edition wyczerpana przed capstone | capstone nie wymaga AI Search (RAG opcjonalny); ten sam endpoint co w M3 |
| Dema Krzysztofa na robotyce wymagają przygotowania na Premium | krok w `01_trainer_prepare_premium` (import folderu, parsowanie i indeks dzień wcześniej) |
