# Dziennik prób (dry-run)

Każde uruchomienie w chmurze dopisuj na górze tabeli. Wszystko, co notebooki zakładają o platformie, a czego nie da się sprawdzić lokalnie, jest na liście „Do potwierdzenia”. Po potwierdzeniu przenieś punkt do „Potwierdzone” z datą i dowodem.

## Uruchomienia

| Data | Workspace | Notebook | Wynik | Czas | Uwagi |
|---|---|---|---|---|---|
| 2026-09-15 | trial Premium | `demo/m3_rag_ai_search` (paczki po 8) | ✅ | ok. 3 min | cały moduł z bonusem Bakehouse; wcześniej 3× ❌ na bonusie (429 przy paczce 20 opinii) |
| 2026-09-15 | trial Premium | `demo/m6_mcp_security_next_steps` (łatka pętli w komórce) | ✅ | 2,5 min | `call_tool(get_customer_profile, 173920)`; agent MCP z 3 serwerami (funkcje, AI Search, Genie) |
| 2026-09-15 | trial Premium | `demo/m6_mcp_security_next_steps` | ⚠️ | 3 min | job zielony, ale komórka labu złapała `asyncio.run() cannot be called from a running event loop` i pokazała mylące „serwer MCP niedostępny” |
| 2026-09-15 | trial Premium | `demo/m5b_transfer_capstone` (Bakehouse) | ✅ | 1,5 min | funkcja `capstone_franchise_sales`, narzędzie tekstowe na opiniach, trasy 2/3 (próg karty wyjściowej) |
| 2026-09-15 | trial Premium | `demo/m5_end_to_end_agent` | ✅ | 5 min | trasy 5/6, bez PII 6/6; sędzia `retail_policy` 0,83, `no_pii_leak` 1,0; `retail_customer_agent` v1 → `@champion`, wczytany model odpowiada 1038.72 USD; App nie istnieje (krok UI) |
| 2026-09-15 | trial Premium | `demo/m4_sql_genie_governance` | ✅ | 3 min | 4/4 wartości oczekiwane; row filter i maska nałożone i zdjęte (28 813, `tax_id` bez maski); Genie przez SDK: VIP **9 494** vs 9 541 |
| 2026-09-15 | trial Premium | `demo/m1_agentic_ai_playground` | ✅ | 2,5 min | model bez narzędzi zmyśla procenty mimo promptu (materiał do porównania w M5); jailbreak „powieść” odrzucony z alternatywą |
| 2026-09-15 | trial Premium | Genie Agent i Knowledge Assistant przez API | ✅ | — | Genie `Retail Customer Intelligence Assistant` (`databricks genie create-space`, `serialized_space` v2); KA `Retail Customer Knowledge Assistant` na Volume `retail_docs` (`databricks knowledge-assistants`), ACTIVE, endpoint `ka-b604f219-endpoint`, cytuje raporty |
| 2026-09-15 | trial Premium | `00_setup/01_trainer_prepare_premium` (po poprawkach) | ✅ 10/14 | 2 min | brakuje tylko kroków UI i prowadzącego: Genie Agent, Knowledge Assistant, `@champion`, Databricks App |
| 2026-09-15 | trial Premium | `pattern/p3_rag_robotics` (po poprawce) | ✅ | 2 min | parsowanie z cache, 30 fragmentów, indeks gotowy; `FULL_TEXT` pokazany jako „niedostępny” |
| 2026-09-15 | trial Premium | `pattern/p3_rag_robotics` | ❌ | 25 min | indeks robotyki powstał; zapytanie `FULL_TEXT`: „Full Text is not yet enabled for this workspace” (podgląd) |
| 2026-09-15 | trial Premium | `00_setup/01_trainer_prepare_premium` | ✅ 7/14 | 13 min | indeks `retail_rag_chunks_index` ok. 12 min do ONLINE; błędy w kodzie: `SHOW USER FUNCTIONS`, MCP `asyncio.run` |
| 2026-09-15 | trial Premium | `demo/m2_tool_calling`, `pattern/p2_uc_functions_bakehouse` | ✅ ✅ | 2,5 / 2,5 min | model wybrał `get_revenue_summary(3, 'NY')`; funkcje Bakehouse zwracają podsumowania; klient X 4205 bez zamówień → zmiana reguły |
| 2026-09-15 | trial Premium | `00_setup/00_setup` | ✅ 6/6 | 2,5 min | preflight: SQL 9 541 VIP, 57 chunków, Llama, tracing, endpoint AI Search ONLINE, Bakehouse 3 333 / 204 |
| 2026-09-15 | trial Premium `infra/azure_trial` (northeurope) | `scripts/prepare_data_premium` (job, serverless env 5) | ✅ | 5,5 min | przebieg 4; eksport 16 plików, 1,7 MB; embeddingi 15 s |
| 2026-09-15 | jw. | jw. (poprawka `attrs`) | ❌ | 17 min | `REQUEST_LIMIT_EXCEEDED` na `databricks-gte-large-en`; `mlflow.deployments` ponawiał po cichu do timeoutu SDK |
| 2026-09-15 | jw. | jw. (env 5 wymuszony w jobie) | ❌ | 2 min | `PlanMetrics is not JSON serializable` przy `to_parquet` po `toPandas()` |
| 2026-09-15 | jw. | jw. (import `.ipynb` bez metadanych) | ❌ | 4 min | środowisko serverless 1 (Python 3.10); ten sam błąd `PlanMetrics` |
| 2026-09-15 | jw. | `infra/azure_trial/smoke_test.py` | ✅ 12/12 | — | modele, tabela na ADLS, `samples.bakehouse`, `ai_query`, AI Search API, Apps API, MCP |

## Potwierdzone

| Data | Co | Dowód |
|---|---|---|
| 2026-09-14 | Pakiet `databricks-ai-search` 0.78 istnieje; moduł `databricks.ai_search.client.AISearchClient`; metody `endpoint_exists`, `create_endpoint`, `get_endpoint`, `create_delta_sync_index_and_wait`, `get_index().similarity_search`; `VectorSearchClient` to alias | kod wheela z PyPI |
| 2026-09-14 | `workshop/requirements-prep.txt` rozwiązuje się dla Pythona 3.12 (`uv pip compile`) | lokalnie |
| 2026-09-14 | `unitycatalog-ai[databricks]` 0.4.0 ogranicza `databricks-sdk` do ≤ 0.94 i dociąga `databricks-connect` | `uv pip compile --annotate` |
| 2026-09-14 | **Bez ograniczenia `mcp<2`** resolver wybiera `mcp` 2.2.0 i `import databricks_langchain` kończy się `ImportError: RequestContext` (langchain-mcp-adapters 0.3.1). Z `mcp>=1.20,<2` (1.30.0) wszystkie importy warsztatu działają | czysty venv, Python 3.12 |
| 2026-09-14 | `databricks-langchain` 0.20: klasy `VectorSearchRetrieverTool`, `DatabricksVectorSearch`, `UCFunctionToolkit`, `DatabricksMCPServer`, `DatabricksMultiServerMCPClient` zachowały nazwy; `mlflow.models.resources.DatabricksVectorSearchIndex` bez zmian | introspekcja pakietów |
| 2026-09-14 | `AISearchIndex.similarity_search(columns, query_text, filters, num_results, query_type, reranker)`; reranker: `databricks.ai_search.reranker.DatabricksReranker(columns_to_rerank)`; wynik ma `manifest.columns` i `result.data_array` | introspekcja pakietu |
| 2026-09-14 | `databricks-mcp` 0.9.2: rozpoznawane ścieżki zarządzanych serwerów to `/api/2.0/mcp/functions/{catalog}/{schema}`, `/mcp/vector-search/{catalog}/{schema}`, `/mcp/genie/{id}`, `/mcp/external/{connection}` (ścieżki `/mcp/ai-search/` SDK nie zna) | `databricks_mcp/mcp.py`, `MCP_URL_PATTERNS` |
| 2026-09-14 | LangGraph 1.2: `create_react_agent` oznaczony jako przestarzały → `langchain.agents.create_agent(model, tools, system_prompt=...)` | dekorator `@deprecated` w źródle |
| 2026-09-14 | `unitycatalog-ai` przy docstringu bez `Args:` tylko ostrzega (nie przerywa rejestracji) | `parse_docstring` lokalnie |
| 2026-09-14 | Smoke testy lokalne z atrapą modelu i funkcji: M3 (chunking, `retrieve_local`, RAG z cytatami, tryby wyszukiwania, łańcuch LangChain z trace'em), M5 (`build_agent`, `AgentExecutor.intermediate_steps`, macierz tras, naprawa, `ResponsesAgent` z historią, porównanie z M1), M6 (`create_agent` z asynchronicznymi narzędziami MCP) | skrypty w scratchpadzie sesji; `SMOKE OK` |
| 2026-09-14 | Kod pliku agenta *models from code* (M5, komórka prowadzącego) parsuje się; `mlflow.models.ModelConfig` istnieje w MLflow 3.16 | `ast.parse` |

| 2026-09-15 | Workspace trial: Llama 3.3 70B i gte-large-en `READY`, `ai_query`, `samples.bakehouse` (3333 transakcje), zarządzany serwer MCP `system/ai` (4 narzędzia), API AI Search i Apps | `smoke_test.py` |
| 2026-09-15 | Katalog Marketplace `databricks_simulated_retail_customer_data.v01` (`customers`, `sales`, `sales_orders`); licencja CC BY 4.0 + Marketplace Consumer Terms | API `consumer-listings get`, instalacja w UI |
| 2026-09-15 | Walidacja po pseudonimizacji: 11/11 PASS (28 813, segmenty, NY 3 417, 26 862 bez zamówień, VIP 1038,72) | job `prepare_data_premium` |
| 2026-09-15 | Font DejaVu pobiera się z GitHuba na serverless; 10 PDF = 0,5 MB; `ai_parse_document` 2.0 z obrazami ~2 min; 57 chunków (plan 50–80) | job |
| 2026-09-15 | `databricks fs cp -r dbfs:/Volumes/...` kopiuje eksport; `test_data_assets.py` przechodzi | lokalnie |
| 2026-09-15 | **`.ipynb` zaimportowany bez `environmentMetadata` działa na serverless env 1 (Python 3.10).** Metadane `{"environment_version": "5"}` są honorowane przy imporcie i w jobie (Python 3.12.3); wszystkie notebooki mają je teraz w repo | job próbny `envprobe` |
| 2026-09-15 | **Spark Connect wkłada `PlanMetrics` do `DataFrame.attrs` po `toPandas()`**, a `to_parquet` zapisuje `attrs` jako JSON i pada. Poprawka: `.attrs.clear()`; test pilnuje każdej komórki `toPandas` → `to_parquet` | job |
| 2026-09-15 | **`REQUEST_LIMIT_EXCEEDED` na `databricks-gte-large-en` zależy od rozmiaru paczki, nie od tempa:** paczka 20 opinii Bakehouse (ok. 13 tys. znaków) dostaje 429 natychmiast i przy każdej próbie, paczki 1, 5 i 10 przechodzą w 0,5 s; komunikat mówi mylnie o „QPS rate limit”. Pierwsza porażka `prepare_data_premium` (paczki po 20) miała tę samą przyczynę; `prepare_data_premium` i bonus M3 używają paczek po 8. `mlflow.deployments` (SDK) ponawia 429 po cichu aż do swojego timeoutu. M3, M5 i `prepare_data_premium` używają teraz `get_open_ai_client().with_options(max_retries=4, timeout=30)` (M5, M3) albo jawnego backoffu z komunikatem (prepare); lint zabrania `mlflow.deployments` | job + wywołanie na żywo 0,8 s |
| 2026-09-15 | Katalog utworzony przez API (Terraform) **nie ma schematu `default`**; Terraform zakłada go osobno | `smoke_test.py` |
| 2026-09-15 | Instalacja listingu Marketplace przez API wymaga `accepted_consumer_terms.version`, której dokumentacja nie podaje; akceptacja w UI | `consumer-installations create` → „Consumer Terms Missing” |

| 2026-09-15 | `00_setup` z plików workspace: `DATA_DIR = cwd.parent / "data"`, `pd.read_parquet` z workspace files, `shutil.copy` do Volume, `%pip -r ../requirements.txt` (ok. 50 s) | job `00_setup` |
| 2026-09-15 | **`spark.sql("SHOW USER FUNCTIONS IN catalog.schema")` na serverless → `CROSS_CATALOG_SCHEMA_REFERENCE_NOT_SUPPORTED`.** M5 i sprawdzenie gotowości czytają `information_schema.routines`; lint zabrania wzorca | job `01_trainer` |
| 2026-09-15 | **`DatabricksMCPClient.list_tools()` w notebooku wymaga `nest_asyncio.apply()`** (inaczej `asyncio.run() cannot be called from a running event loop`); z nim serwer funkcji zwraca 7 narzędzi | job `01_trainer` |
| 2026-09-15 | **AI Search `FULL_TEXT` na nowym workspace trial to podgląd wyłączony domyślnie** („Full Text is not yet enabled… previews”); ANN i HYBRID działają. M3 i `p3` pokazują tryb jako niedostępny zamiast przerywać | job `p3` |
| 2026-09-15 | Indeks Delta Sync 57 wierszy: ok. 12 min od utworzenia do `ONLINE` na świeżym endpoincie; drugi indeks (robotyka, 30 wierszy) na tym samym endpoincie | joby `01_trainer`, `p3` |
| 2026-09-15 | Pierwszy VIP według `customer_id` (4205) nie ma zamówień; „klient X” to teraz pierwszy VIP z zamówieniem, miastem i `tax_id` (173920) | job M2 |

| 2026-09-15 | **Genie liczy klientów jako `COUNT(DISTINCT customer_id)`: 9 494 VIP zamiast 9 541**, bo w danych źródłowych 143 klientów ma po dwa wiersze (286). Dane zostają (liczby z decku), przewodnik prowadzącego ma z tego moment dydaktyczny w M4 | job M4 + parquet lokalnie |
| 2026-09-15 | **`nest_asyncio.apply()` musi być w tej samej komórce co `list_tools()` / `call_tool()`**; łatka z wcześniejszej komórki nie działa. Test pilnuje każdej komórki z `list_tools()` | job M6 |
| 2026-09-15 | Genie Agent i Knowledge Assistant da się założyć z CLI (`genie create-space` z `serialized_space` wersja 2; `knowledge-assistants create-knowledge-assistant` + `create-knowledge-source` typu `files`); KA z Volume jest ACTIVE po kilku minutach i cytuje PDF-y oraz obrazy stron | CLI 1.16.1 |
| 2026-09-15 | `databricks serving-endpoints query` obcina odpowiedź agenta KA do pól `id/model/object`; pełna odpowiedź przez `databricks api post /serving-endpoints/<ka>/invocations` | CLI |
| 2026-09-15 | Rejestracja agenta *models from code* w UC z aliasem `@champion` i wczytanie z UC działają na workspace z katalogiem na ADLS | job M5 |

## Potwierdzone przez Krzysztofa na Free Edition (22–28.07.2026)

Źródło: `Warsztaty_Krzysztof/sprawozdanie_zbiorcze_v3.pdf` i `KONTEKST_KONTYNUACJI_PROJEKTU.md`. Inne wersje pakietów niż dziś, więc przy próbie traktuj te punkty jako mocną przesłankę, a nie gwarancję.

| Co | Wynik |
|---|---|
| `ai_parse_document` 2.0 z `imageOutputPath` i `descriptionElementTypes` (Python i SQL), renderer ramek | ✅ działa |
| AI Search: endpoint STANDARD, Delta Sync z managed embeddings, ANN / HYBRID / FULL_TEXT / filtr po ścieżce | ✅ działa; kilka minut `PROVISIONING_ENDPOINT`; `sync()` zaraz po utworzeniu zwraca „index is not ready” |
| Reranker `DatabricksReranker` | ❌ zablokowany konfiguracją workspace |
| Knowledge Assistant | ❌ niepotwierdzony; synchronizacja z Volume nie powiodła się |
| Funkcje UC SQL i Python, `execute_function`, `UCFunctionToolkit` + `AgentExecutor` + Llama 3.3 70B | ✅ działa (możliwy błąd `Cannot access Spark Connect`) |
| `VectorSearchRetrieverTool` + `create_agent`, `mlflow.langchain.log_model(model_type="agent")`, rejestracja w UC | ✅ działa |
| Modele GPT-OSS / GPT | ⚠️ timeouty; Inkling dostępny krótko |
| `enable_safety_filter` | ❌ błędy, traktowany jako przestarzały |
| Custom Model Serving endpoint | ❌ provisioning kończył się `Failed` |
| AI Gateway inference tables i trace'y OTel w `workspace.default` | ❌ `Unsupported table kind`: wymagany katalog z external storage |
| Llama Guard z Marketplace | ❌ brak możliwości utworzenia endpointu |

## Do potwierdzenia

**Dane i `00_setup` (Free)**
- [ ] `%pip install -r ../requirements.txt` działa w folderze Git na Serverless; ile trwa instalacja.
- [ ] `databricks-connect` dociągany przez `unitycatalog-ai[databricks]` nie psuje sesji Spark na Serverless.
- [ ] `os.getcwd()` w notebooku folderu Git wskazuje katalog notebooka (`DATA_DIR = cwd.parent / "data"`).
- [ ] `pd.read_parquet` z plików workspace i `shutil.copy` do `/Volumes/...` działają na Free.
- [ ] Endpoint `databricks-meta-llama-3-3-70b-instruct` jest dostępny na Free i Premium we wrześniu 2026.
- [ ] `ai_query` działa na Free (komórka opcjonalna w M0).
- [ ] Czas od `create_endpoint` do stanu ONLINE na Free; limit jednego endpointu AI Search.
- [ ] `mlflow.start_span` w eksperymencie `/Users/<login>/sqlday_retail_agent` z notebooka w folderze Git.
- [ ] Run-all `00_setup` ≤ 12 min.

**`prepare_data_premium` (Premium)**
- [ ] Licencja: człowiek potwierdza Marketplace Consumer Terms (PDF) i zmienia status w `data/LICENSE_REVIEW.md` na ✅.
- [ ] `w.genie.list_spaces()` / `start_conversation_and_wait` działają dla Genie Agents; klucze metryk `mlflow.genai.evaluate` mają postać `<scorer>/mean` (krok 8, po utworzeniu Genie Agenta w UI).

**Z próby 2026-09-15 (nowe)**
- [ ] Limit zapytań pay-per-token na Free przy 20 osobach: M3 (4 zdania) i M5 (macierz tras, 1 embedding na pytanie) z `max_retries=4` kończą się w rozsądnym czasie albo czytelnym `RateLimitError`.
- [ ] `get_open_ai_client()` jest oznaczony jako przestarzały w nowszym `databricks-sdk` (zalecany `databricks_openai.DatabricksOpenAI`); w przypiętym środowisku (SDK 0.67) działa bez ostrzeżeń. Decyzja przed warsztatem: zostać czy przejść na `databricks-openai`.
- [ ] M3: `gte-large-en` to model angielski; dla polskich zdań parafraza 0,611 vs zupa 0,574 (mały margines). Sprawdzić na 4 zdaniach z labu i ewentualnie dodać zdanie o tym na slajdzie.
- [ ] Środowisko serverless 5 dostępne na Free Edition (metadane notebooków).
- [ ] `FULL_TEXT` na Free Edition (Krzysztof 07.2026: działał) i włączenie podglądu na workspace prowadzącego (Settings → Previews).

**M1**
- [ ] `w.serving_endpoints.get_open_ai_client()` na Free; `extra_body={"enable_safety_filter": True}` akceptowane albo czytelny błąd.
- [ ] Który drugi model do porównania w Playground odpowiada stabilnie na Free (GPT-OSS miały timeouty w 07.2026).
- [ ] 8 wywołań z `sleep(1)` mieści się w limicie FMAPI przy 20 osobach.

**M2**
- [ ] `DatabricksFunctionClient(execution_mode="serverless").create_python_function` i `execute_function` na Free.
- [ ] Llama 3.3 70B przez klienta OpenAI zwraca `tool_calls` dla schematu `tools` (M2 część 2).
- [ ] Playground: menu **Tools → Add tool → Unity Catalog function**; nazwa przycisku **Get code**.

**M3**
- [ ] `ai_parse_document(content, MAP('version', '2.0'))` bez `imageOutputPath` zwraca `document.elements` (RUN_PARSE = True).
- [ ] `AISearchIndex.describe()["status"]["ready"]` i `indexed_row_count` na świeżym indeksie; `index.sync()` na indeksie TRIGGERED.
- [ ] `similarity_search(query_type="FULL_TEXT")` i `filters={"doc_id": ...}` na endpointcie STANDARD; `DatabricksReranker` na Free.
- [ ] `DatabricksVectorSearch(...).as_retriever(search_kwargs={"k": 3, "query_type": "HYBRID"})` na indeksie z managed embeddings.
- [ ] `llm.responses.create(model=<endpoint KA>)` dla Knowledge Assistant (Premium).
- [ ] Playground: typ narzędzia „AI Search index” (albo nadal „Vector Search”).

**M4**
- [ ] `is_account_group_member('<nieistniejąca grupa>')` zwraca `FALSE` (nie błąd) w row filtrze i masce na Free.
- [ ] `ALTER TABLE ... DROP ROW FILTER` / `DROP MASK` bez aktywnego filtra: błąd czy no-op (komórka łapie oba przypadki).
- [ ] Genie Agent: tworzenie w UI na Free; `get_message_attachment_query_result` zwraca `statement_response.result.data_array`; limit pytań na minutę.
- [ ] Genie z aktywną maską pokazuje `***MASKED***` i respektuje row filter.

**M5**
- [ ] `SHOW USER FUNCTIONS IN workspace.default` zwraca kolumnę `function` z pełną nazwą.
- [ ] `UCFunctionToolkit` nazywa narzędzia `workspace__default__<funkcja>`; `VectorSearchRetrieverTool(tool_name="search_retail_reports")` pojawia się w `intermediate_steps` pod tą nazwą.
- [ ] Macierz tras 3× pod rząd: liczba zgodnych tras, trasy niestabilne (uzupełnij `trainer_guide.md`).
- [ ] `mlflow.pyfunc.log_model(python_model=<plik w Volume>, model_config=..., resources=...)` + `@champion` + `load_model(...).predict({"input": [...]})` na Premium.
- [ ] Databricks Apps: nazwa ścieżki **Get code → Create agent app** w Playground; `w.apps.get` zwraca `service_principal_client_id`.

**M6**
- [ ] Zarządzany serwer MCP funkcji UC na Free (Public Preview): `list_tools`, `call_tool`, nazwy narzędzi (sufiks `get_customer_profile`).
- [ ] Serwery `/mcp/vector-search/{catalog}/{schema}` i `/mcp/genie/{id}` na Premium; `DatabricksMultiServerMCPClient.get_tools()` z trzema serwerami.
- [ ] `asyncio.run` w notebooku Serverless (albo ścieżka `nest_asyncio`).
- [ ] `ChatDatabricks` z `langchain.agents.create_agent` i narzędziami MCP (tool calling Llama 3.3 70B).

**Nowy układ dnia (pattern, poziomy, capstone)**
- [ ] `samples.bakehouse` na Free: tabele `sales_transactions`, `sales_franchises`, `media_customer_reviews`; typ `franchiseID` i `cardNumber`.
- [ ] Funkcje SQL UC czytające katalog `samples` (`bh_franchise_summary`, `bh_payment_methods`) tworzą się i wykonują na Free.
- [ ] `CREATE TABLE ... AS SELECT * FROM samples.bakehouse.sales_transactions` + maska na `cardNumber` (typ wykrywany w komórce).
- [ ] `pattern/p3_rag_robotics` na Premium: kopia 32 MB PDF z folderu Git do Volume, parsowanie, drugi indeks na tym samym endpointcie.
- [ ] Capstone na Free w 40 min: opcja Bakehouse end-to-end, opcja Airbnb (`pd.read_csv` → Spark), opcja własny CSV z Volume `my_data`.
- [ ] Liczba indeksów na jednym endpointcie AI Search na Free (retail + capstone).
- [ ] Serwer MCP funkcji pokazuje funkcje `capstone_*` w M6.
- [ ] Odsetek kart wyjściowych w próbie z osobami spoza zespołu.

**Laby i czas**
- [ ] Każde `ZADANIE` wykonalne w podanym czasie przez osobę spoza zespołu.
- [ ] Próba czasowa całego dnia z timerem → korekta `docs/schedule.md`.
- [ ] Koszt dnia na Premium (`system.billing.usage`) po 24 h.
