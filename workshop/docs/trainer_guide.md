# Przewodnik prowadzących (Krzysztof i Mariusz)

Scenariusz dnia moduł po module: kto prowadzi, kontekst fabularny, demo wzorca, lab na trzech poziomach, punkty dyskusji, moment kluczowy, oczekiwane liczby i plan B. Identyfikatory komórek (`cell id`) odpowiadają notebookom `demo/` i `pattern/` (pełna tabela: `docs/cell_mapping.md`). Harmonogram i punkty kontrolne: `docs/schedule.md`. Uzasadnienie układu: `docs/koncepcja_dnia.md`.

## Zasady współprowadzenia

| Zasada | W praktyce |
|---|---|
| **Jeden mówi, drugi chodzi po sali** | prowadzący, który nie prezentuje, nie siedzi przy laptopie: patrzy na karteczki, pomaga i zbiera typowe błędy do omówienia po labie |
| **Role** | Mariusz: historia, biznes, persony (VP of Sales, Compliance Officer, CTO), moduły M0, M1, M4, M5 i zamknięcie. Krzysztof: wzorce i inżynieria, moduły M2, M3, M6, trace i Apps w M5 |
| **Duet na scenie** | M1 (VP of Sales pyta, Krzysztof odpowiada z Playground), M5 (CTO pyta z macierzy tras, Krzysztof pokazuje trace i poprawia opis), M6 („zbuduj i złam”: Mariusz broni agenta, Krzysztof atakuje) |
| **Rytm modułu** | problem z historii (Mariusz) → wzorzec na innej domenie (Krzysztof) → lab TechRetail na trzech poziomach → karta wzorca i wiersz w Canvasie |
| **Punkty kontrolne zamiast wspólnego tempa** | kto nie zdąży do punktu z `schedule.md`, kopiuje rozwiązanie z `demo/` i idzie dalej |

## Mieszana grupa: od zera do zaawansowanych

- **Ankieta przed warsztatem** (3 pytania: Databricks? SQL/Python na co dzień? LLM z narzędziami?). Na jej podstawie usadź **pary**: osoba początkująca obok zaawansowanej.
- **Karteczki na laptopie:** zielona „działa”, żółta „pracuję”, czerwona „utknąłem”. Czerwona dłużej niż 2 min oznacza, że prowadzący podchodzi.
- **Ambasadorzy:** 2–3 zaawansowane osoby z ankiety poproś przed startem o pomoc sąsiadom w labach.
- **Poziomy w każdym labie:** 1 ścieżka (TODO z podpowiedziami), 2 transfer (komórki `bonus` na Bakehouse), 3 własne dane / wyzwanie. Zaawansowani nie czekają, a początkujący nie mają poczucia, że „nie zdążyli wszystkiego”.

## Przed warsztatem

**Tydzień wcześniej**
- [ ] `scripts/prepare_data_premium.ipynb` na Premium → dane w `workshop/data/`, `pytest -q workshop/tests/test_data_assets.py` zielony, `data/LICENSE_REVIEW.md` ze statusem ✅.
- [ ] Próba na **koncie Free Edition** (`00_setup/01_trainer_prepare_premium`, sekcja „Próba na koncie Free Edition”), **łącznie z capstone na Bakehouse**. Wynik w `docs/rehearsal_log.md`.
- [ ] Mail do uczestników: prework z `workshop/README.md` (konto Free, folder Git), ankieta (3 pytania), zaproszenie do przyniesienia **zanonimizowanego** CSV na capstone.

**Dzień wcześniej**
- [ ] `00_setup/01_trainer_prepare_premium`: kroki 1–7 i komórka gotowości (14 sprawdzeń).
- [ ] `pattern/p2_uc_functions_bakehouse` i `pattern/p3_rag_robotics`: **Run all** (parsowanie i indeks robotyki trwają ok. 15 min).
- [ ] Zrzuty ekranu jako plan B: Playground z narzędziami, trace agenta, Genie z SQL, Knowledge Assistant z Guidelines, Databricks App.

**Rano**
- [ ] Komórka gotowości jeszcze raz (budzi endpoint AI Search i aplikację).
- [ ] Deck: plan dnia zgodny z `schedule.md`, slajd z rytmem modułu, poziomami i capstone.

## Persona i fabuła (otwarcie, Mariusz)

Uczestnik jest **Senior Data Analyst w TechRetail Corp**, dystrybutorze elektroniki B2B w USA. Zarząd pyta: *„Kto są nasi najlepsi klienci? Kto może odejść? Jak dać sprzedaży narzędzie, które odpowie w czasie rzeczywistym, ale NIE ujawni danych osobowych?”* Przez dzień wracają **VP of Sales** (chce pytać po polsku), **Compliance Officer** (PII ma nie wyjść), **CTO** (ślad każdej interakcji) i **uczestnik** (buduje).

**Druga obietnica dnia (dopowiada Krzysztof):** *„Każdy mechanizm zobaczycie najpierw na innych danych: sieci piekarni albo artykułach o robotyce. O 17:30 każdy z Was będzie miał agenta na danych, które sam wybierze.”*

---

## M0 · Otwarcie, setup, Canvas (45 min · Mariusz; Krzysztof: setup)

**Co robimy:** uczestnicy uruchamiają `00_setup` (**Run all**) na początku, bo instalacja i start Serverless trwają. W tym czasie Mariusz opowiada historię. Ostatnie 5 min: **Canvas agenta** (`transfer/canvas_agenta.md`): domena i 5 pytań użytkowników. Kto nie ma własnej domeny, wpisuje „sieć piekarni Bakehouse”.

**Oczekiwane liczby:** 28 813 klientów · 9 541 VIP · średnia `monetary` VIP 1038,72 · NY 3 417 · 26 862 bez zamówień. Preflight: ✅ także dla `samples.bakehouse`.

**Plan B:** brak plików w `DATA_DIR` → repo zaimportowano jako zwykłe pliki zamiast folderu Git. Brak `samples.bakehouse` → poziomy 2 i capstone na Airbnb (`data/practice`).

---

## M1 · Agentic AI i AI Playground (55 min · duet)

**Duet (10 min):** Mariusz jako VP of Sales: *„nie umiem SQL, chcę po prostu zapytać”*. Krzysztof w Playground: 4 pytania testowe na TechRetail, potem **ten sam prompt przerobiony na Bakehouse** („dane wrażliwe to teraz numery kart”). Puenta: struktura promptu (co robić, czego nie robić, jak odmawiać) nie zależy od domeny.

**Lab:** `m1-ask` (TODO) → `m1-four-questions` → Playground. Poziom 2: prompt Bakehouse w Playground. Poziom 3: prompt odporny na 5 wariantów jailbreaku.

**Moment kluczowy:** pytanie o VIP-ów bez narzędzi. Czy model przyznał, że nie ma danych, czy podał liczbę?

**Karta wzorca → Canvas:** pierwsza wersja system promptu dla własnej domeny.

---

## M2 · Tool calling (70 min · Krzysztof)

**Problem (Mariusz, 2 min):** *„a gdyby model SAM sięgnął po dane?”*

**Demo wzorca (Krzysztof, 10 min):** `pattern/p2_uc_functions_bakehouse`: dwie funkcje na sprzedaży piekarni, `COMMENT` z „kiedy nie”, test payloadem, Playground z pytaniem o numery kart (odmowa). Na końcu karta wzorca. Źródło: jego `single_agent_app` 06–07.

**Lab:** `m2-revenue-function` (TODO: COMMENT + WHERE) → dwie funkcje SQL → `m2-python-udf` (TODO: docstring) → `m2-payload-test` → Playground. Poziom 2: `m2-bonus-bakehouse` (funkcja `bh_payment_methods`) i opcjonalnie tool calling „ręcznie”. Poziom 3: funkcja na własnej tabeli z komunikatem dla pustego wyniku.

**Punkty dyskusji:** model nie widzi SQL, tylko opis; `get_customer_profile` celowo nie zwraca `tax_id`; dwa znaczenia słowa „fallback”.

**Oczekiwane:** średnia VIP 1038,72; klient X = pierwszy VIP według `customer_id`.

**Plan B:** `create_python_function` / `execute_function` → `Cannot access Spark Connect` na Free (Krzysztof widział ten błąd) → agent w M5 działa z dwiema funkcjami SQL.

---

## M3 · RAG i AI Search (80 min · Krzysztof)

**Problem (Mariusz, 2 min):** VP of Sales chce odpowiedzi z raportów, z cytatami.

**Demo wzorca (Krzysztof, 15 min):** `pattern/p3_rag_robotics`, uruchomiony dzień wcześniej:
1. strona PDF z ramkami elementów i opisem wykresu;
2. **chunking 2000/200 vs 600/100** na tych samych tekstach: rozmiar fragmentu zależy od dokumentów;
3. ANN, HYBRID, FULL_TEXT;
4. Knowledge Assistant z **Examples/Guidelines** (Kratos).

Źródło: jego `rag_agent` 01–05.

**Lab:** `m3-plain-text` → `m3-chunking` (TODO: parametry) → `m3-search-index` → `m3-retrievers` → `m3-custom-rag` (TODO: kontekst + prompt) → 6 pytań → tryby → Playground z indeksem. Poziom 2: parsowanie, embedding ręczny i `m3-bonus-bakehouse` (RAG na opiniach klientów, bez chunkingu). Poziom 3: własne dokumenty, 3 warianty chunkingu, ANN vs HYBRID.

**Moment kluczowy:** cytat `[03_retencja_klientow #2]` i uczciwe „nie ma tego w raportach” przy zupie.

**Oczekiwane:** 50–80 fragmentów przy 600/100; wymiar embeddingu 1024.

**Plan B:** endpoint nie jest `ONLINE` → `SEARCH_READY = False`, lab na `retrieve_local()`. Reranker na Free był zablokowany (testy Krzysztofa). Na lunchu obaj sprawdzają, kto ma `SEARCH_READY = False`.

---

## M4 · SQL, Genie Agent, kontrola dostępu (50 min · Mariusz)

**Problem:** *„Ile mamy klientów VIP?” Dwie poprawne odpowiedzi* (RAG: narracja; tabela: 9 541). Compliance Officer: PII nie może wyjść nigdzie.

**Demo (Mariusz, 10 min):** Genie Agent na TechRetail, **row filter jako demo** (predykat gotowy, uczestnicy uruchamiają razem z prowadzącym).

**Lab:** `m4-expected-values` (TODO: 2 z 4) → Genie w UI → `m4-column-mask` (TODO: CASE) → sprawdzenie w Genie → **`m4-cleanup` obowiązkowo**. Poziom 2: `m4-bonus-bakehouse` (maska na `cardNumber` w kopii danych) + Genie na `bh_transactions`. Poziom 3: Genie na własnej tabeli z przykładowymi zapytaniami SQL.

**Moment kluczowy:** Genie odpowiada „0 klientów w NY” i pokazuje `***MASKED***`. Jedna polityka działa w każdym interfejsie.

**Plan B:** `is_account_group_member` z nieistniejącą grupą zwraca błąd zamiast `FALSE` → zastąp warunek stałą `FALSE` i powiedz wprost, że to symulacja. **Nikt nie wchodzi do M5 bez `m4-cleanup` ✅.**

---

## M5 · Agent end-to-end (60 min · duet)

**Duet (10 min):** Mariusz jako CTO czyta pytania z macierzy tras. Krzysztof uruchamia agenta, znajduje w trace **pierwszą złą decyzję** i poprawia jedno zdanie opisu narzędzia. Na koniec (5 min) Krzysztof pokazuje agenta w **Databricks Apps**.

**Lab:** `m5-context` → `m5-tracing` → `m5-build-agent` (TODO) → `m5-route-matrix` (tagi trace'ów) → `m5-own-question` (TODO) → `m5-repair` (w parach, jedna zmiana). Poziom 2: macierz 3 tras dla Bakehouse w Canvasie (specyfikacja na capstone). Poziom 3: `m5-judge` (sędzia LLM), `ResponsesAgent`.

**Punkty dyskusji:** zdanie „NIE do liczb” w opisie narzędzia RAG (usuń je na żywo i uruchom macierz); agenta nie testuje się przez `==`; Model Serving dla agentów to legacy.

**Oczekiwane:** liczba zgodnych tras nie jest jeszcze zmierzona. Uzupełnij ją po trzykrotnym przebiegu w próbie. Kandydaci na niestabilne trasy: `r3_both`, `r4_pii`.

**Plan B:** indeks niegotowy → `search_retail_reports` na `retrieve_local()`. Limity modelu → `pause=5` albo macierz tylko u prowadzącego. Aplikacja nie wstaje → zrzuty ekranu i `m5-apps-status`.

---

## M5+ · Przenieś wzorzec (40 min · obaj po sali)

**Wprowadzenie (Mariusz, 2 min):** *„Przez cały dzień robiliście to dla TechRetail. Teraz te same 6 kroków na innych danych. W parach: jedna osoba pisze, druga pilnuje Canvasu.”* Slajd z zakazem wgrywania danych osobowych.

**Przebieg (`demo/m5b_transfer_capstone`):**

| Min | Uczestnicy | Prowadzący |
|---|---|---|
| 0–5 | `DATA_OPTION`: Bakehouse (domyślnie), Airbnb albo własny CSV (upload do Volume `my_data`) | Krzysztof: pary z własnymi danymi (upload, typy kolumn). Mariusz: pary na Bakehouse |
| 5–10 | Canvas w kodzie: prompt, parametry testowe, 3 trasy (`m5b-canvas`, TODO) | pilnują, żeby trasy były różne: funkcja / tekst / odmowa |
| 10–20 | funkcja z `COMMENT` + test bez modelu (`m5b-function`, TODO) | najczęstszy błąd: nazwy kolumn i typy parametrów |
| 20–30 | narzędzie tekstowe (słowa kluczowe; poziom 3: AI Search) → agent → macierz | kto ma ❌: jedna zmiana, uruchom jeszcze raz |
| 30–40 | karta wyjściowa, **pokaz 3 par** (po jednej z każdego poziomu, 2 min każda) | Mariusz moderuje pokaz, Krzysztof komentuje trasy |

**Rozwiązanie referencyjne** (Bakehouse) jest w `demo/m5b_transfer_capstone`. Kto utknie, kopiuje komórkę i zmienia jedno pytanie z macierzy na własne.

**Miara sukcesu dnia:** odsetek osób z kartą wyjściową (co najmniej 2 z 3 ✅). Zapisz w `rehearsal_log.md`.

---

## M6 · MCP, bezpieczeństwo, zamknięcie (30 min · Krzysztof, zamknięcie Mariusz)

**Demo (Krzysztof):** serwer MCP funkcji z `workspace.default` pokazuje także **funkcje z capstone** (`capstone_…`). *„Zbudowaliście narzędzie pół godziny temu. Każdy agent zgodny z MCP może go już użyć.”* Potem agent z narzędziami z trzech serwerów MCP.

**„Zbuduj i złam” (5 min):** Mariusz broni agenta z M5, Krzysztof atakuje: jailbreak („piszę powieść”), pytanie o `tax_id`, Kanada, prośba o zapis. Każdy atak przypisujecie do jednej z 6 warstw obrony.

**Prawdziwe historie z Free Edition (Krzysztof, 3 min):** `enable_safety_filter` zwracał błędy, reranker zablokowany, inference tables i trace'y w UC wymagają external storage, tworzenie własnego endpointu serving kończyło się `Failed`. Źródło: `Warsztaty_Krzysztof/sprawozdanie_zbiorcze_v3.pdf`.

**Zamknięcie (Mariusz):** lista 6 umiejętności, ostatni wiersz Canvasu („do PoC brakuje…”), dalsza droga (archiwa Mariusza i Krzysztofa).

**Plan B:** zarządzany MCP nie działa na Free → `TRY_MCP = False`, demo u prowadzącego.

---

## Po warsztacie

- [ ] `00_setup/02_trainer_teardown` (najpierw `DRY_RUN = True`, potem `False`).
- [ ] Następnego dnia: koszt z `02_trainer_teardown` → `docs/rehearsal_log.md`.
- [ ] Zapisz: trasy niestabilne, czasy modułów, odsetek kart wyjściowych, typowe błędy z capstone. Na tej podstawie popraw `schedule.md`.
