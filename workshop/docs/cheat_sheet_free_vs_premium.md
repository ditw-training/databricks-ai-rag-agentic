# Cheat sheet: Free Edition vs Premium

**Stan na 2026-09-14.** Oznaczenia „07.2026” pochodzą z testów Krzysztofa na Free Edition (`Warsztaty_Krzysztof/sprawozdanie_zbiorcze_v3.pdf`). Uczestnicy pracują na **Databricks Free Edition**, prowadzący pokazuje dema na workspace **Premium**. Funkcje i limity Free Edition zmieniają się, więc w razie wątpliwości sprawdź dokumentację „Free Edition limitations”.

## Co działa gdzie

| Funkcja | Free Edition | Premium | Gdzie w warsztacie | Jak ćwiczyć na Free |
|---|---|---|---|---|
| Serverless notebooks | ✅ tylko Serverless; po przekroczeniu dziennej kwoty wyłączenie do końca dnia | ✅ | wszystkie moduły | uruchamiaj komórki po kolei, nie Run all kilka razy |
| SQL Warehouse | ✅ 1, rozmiar 2X-Small | ✅ | M4 (Genie) | — |
| Foundation Model API (Llama 3.3 70B, gte-large-en) | ✅ z limitami na minutę | ✅ | M1–M6 | `time.sleep` jest już w pętlach |
| AI Playground z narzędziami | ✅ | ✅ | M1, M2, M3, M4 | pełny lab |
| Funkcje Unity Catalog (SQL i Python) | ✅ | ✅ | M2 | pełny lab |
| `ai_parse_document`, `ai_query` | ✅ z limitami (z obrazami stron i opisami wykresów potwierdzone 07.2026) | ✅ | M0, M3 | M3 domyślnie czyta checkpoint (`RUN_PARSE = False`) |
| Reranker AI Search | ❌ zablokowany konfiguracją workspace (07.2026) | ✅ zależnie od regionu | M3 (opcja) | pomiń |
| Katalog przykładów `samples.bakehouse` | ✅ | ✅ | poziomy 2, capstone | pełny lab |
| **AI Search** (dawniej Vector Search) | ✅ **1 endpoint, 1 jednostka** | ✅ | M3, M5, M6 | tryb offline `retrieve_local()`, gdy endpoint nie jest `ONLINE` |
| **Genie Agent** (dawniej Genie Space) | ✅; API ok. 5 pytań na minutę | ✅ | M4 | UI; SDK opcjonalnie |
| Row filter, column mask | ✅ (jedna tożsamość: widzisz wariant „bez uprawnień”) | ✅, dwie tożsamości | M4 | pełny lab |
| MLflow Tracing, eksperymenty | ✅ | ✅ | M3, M5 | pełny lab |
| Agent w notebooku, `ResponsesAgent` lokalnie | ✅ | ✅ | M5 | pełny lab |
| Rejestracja modelu w Unity Catalog, alias `@champion` | ⚠️ możliwa, ale poza czasem labu | ✅ | M5 (demo) | ćwicz po warsztacie |
| **Databricks Apps** | ⚠️ do 3 aplikacji | ✅ | M5 (demo) | po warsztacie: szablon aplikacji agentowej |
| Model Serving własnego agenta | ❌ tworzenie endpointu kończyło się `Failed` (07.2026); dla agentów i tak legacy | ✅ | — | nie ćwiczymy; używaj Databricks Apps |
| Inference tables, trace'y MLflow w Unity Catalog | ❌ w `workspace.default` (default storage); potrzebny katalog z external storage | ✅ | M6 (omówienie) | trace'y w eksperymencie MLflow działają |
| `enable_safety_filter` | ⚠️ zwracał błędy, wypierany przez guardrails na endpoincie | ✅ | M1 (opcja) | komórka pokaże błąd; nie usuwaj kontroli po cichu |
| **Zarządzane serwery MCP** (funkcje, AI Search, Genie) | ⚠️ Public Preview, dostępność zależy od workspace | ✅ | M6 | `TRY_MCP = False` pomija; wzorzec jak w M2 |
| **Knowledge Assistant** (Agent Bricks) | ❌ | ✅ | M3 (demo) | tylko pokaz |
| **Unity Gateway** (dawniej AI Gateway, GA 08.2026) | ❌ na własnym endpoincie | ✅ | M6 (omówienie) | archiwum WS2 §7 |
| Secret scope, tokeny serwisowe | ❌ | ✅ | — | — |
| Lakehouse Monitoring | ❌ | ✅ | M6 (omówienie) | archiwum WS2 Cz. 4 |
| Marketplace | ✅ | ✅ | przygotowanie danych (prowadzący) | niepotrzebne: dane są w repo |

## Nazwy zmienione w 2026

| Dziś | Dawniej | Uwaga |
|---|---|---|
| AI Search | Vector Search | pakiet `databricks-ai-search`, klient `AISearchClient`; klasy LangChain (`VectorSearchRetrieverTool`, `DatabricksVectorSearch`) i ścieżka MCP `/mcp/vector-search/` zachowały starą nazwę |
| Genie Agent | Genie Space | SDK nadal `w.genie.*_space` |
| Unity Gateway | AI Gateway | GA od 04.08.2026 |
| `ResponsesAgent` | `ChatAgent`, `PythonModel` z `predict(DataFrame)` | standardowy interfejs agentów |
| Databricks Apps | Model Serving + `agents.deploy` | rekomendowane wdrożenie agentów |
| `langchain.agents.create_agent(system_prompt=...)` | `langgraph.prebuilt.create_react_agent(state_modifier=...)` | LangChain / LangGraph 1.x |

## Nazwy obiektów warsztatu (`workspace.default`)

| Obiekt | Nazwa | Tworzy |
|---|---|---|
| tabela klientów | `gold_customer_360` (28 813 wierszy, 19 kolumn) | `00_setup` |
| raporty PDF | Volume `retail_docs` (10 plików) | `00_setup` |
| fragmenty raportów | `retail_rag_chunks`; `retail_rag_docs` | `00_setup`; M3 |
| endpoint i indeks AI Search | `retail_rag_search`, `retail_rag_chunks_index` | `00_setup`, M3 |
| funkcje | `get_revenue_summary`, `get_average_customer_value`, `get_customer_profile`, `format_customer_for_agent` | M2 |
| odpowiedzi z M1 | `m1_baseline_answers` | M1 |
| Genie Agent | `Retail Customer Intelligence Assistant` | M4 (UI) |
| eksperyment MLflow | `/Users/<login>/sqlday_retail_agent` | M0, M3, M5 |
| funkcje Bakehouse (poziom 2) | `bh_franchise_summary`, `bh_product_sales` (demo), `bh_payment_methods`, `bh_mask_card`; tabela `bh_transactions` | pattern/p2, M2, M4 |
| capstone | `capstone_table`, `capstone_docs`, funkcja `capstone_…`, opcjonalnie indeks `capstone_docs_index`; Volume `my_data` | M5+ |
| demo robotyki (prowadzący) | Volume `robotics_files`, `robotics_parsed_documents`, `robotics_chunks`, indeks `robotics_chunks_index` | pattern/p3 |

## Gdy coś nie działa

| Objaw | Co zrobić |
|---|---|
| `%pip install` trwa długo albo pada | uruchom komórkę jeszcze raz; zawsze potem `restartPython` i komórkę konfiguracji |
| `NameError` po restarcie | uruchom od komórki konfiguracji w dół |
| `ImportError ... RequestContext` przy `databricks_langchain` | brak ograniczenia `mcp<2`: sprawdź, czy instalujesz z `../requirements.txt` |
| endpoint AI Search `PROVISIONING` | nic nie rób: M3 i M5 przejdą w tryb offline; uruchom M3 ponownie po przerwie |
| `429` / `REQUEST_LIMIT_EXCEEDED` z modelu | odczekaj minutę; nie uruchamiaj macierzy tras kilka razy naraz |
| serverless wyłączony do końca dnia (kwota) | pracuj na ekranie prowadzącego i w Playground; dokończ labs następnego dnia |
| M5: „tabela ma 3 xxx wierszy” | row filter z M4 nadal aktywny: uruchom komórkę sprzątającą z M4 |
| M6: błąd serwera MCP | `TRY_MCP = False`, obejrzyj demo |
| M5+: brak `samples.bakehouse` | `DATA_OPTION = "airbnb"` |
| M5+: błąd typów przy własnym CSV | usuń puste kolumny, sprawdź separator; zacznij od 5–10 kolumn |
| `Cannot access Spark Connect` przy funkcji Python UC | ograniczenie usługi na Free: użyj funkcji SQL |

## Po warsztacie u siebie

1. Usuń endpoint AI Search, jeśli nie wracasz jutro (zużywa kwotę bez zapytań).
2. Rozwiązania wszystkich labów są w `workshop/demo/`.
3. Dalsza droga: `Warsztaty_Mariusz/` WS2 (ewaluacja `mlflow.genai`, własny guard z taksonomią, monitoring) i WS4 (rejestracja, aplikacja). Tamte notebooki używają nazw sprzed 2026, więc tłumacz je według tabeli wyżej.

*Dane TechRetail Corp są syntetyczne (Databricks Marketplace, „Simulated Retail Customer Data”) i dodatkowo spseudonimizowane: `customer_name` = `Customer <id>`, `tax_id` fikcyjne, współrzędne zaokrąglone.*
