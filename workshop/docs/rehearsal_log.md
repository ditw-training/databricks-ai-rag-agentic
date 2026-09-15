# Dziennik prób (dry-run)

Każde uruchomienie w chmurze dopisuj na górze tabeli. Wszystko, co notebooki zakładają o platformie, a czego nie da się sprawdzić lokalnie, jest na liście „Do potwierdzenia”. Po potwierdzeniu przenieś punkt do „Potwierdzone” z datą i dowodem.

## Uruchomienia

| Data | Workspace | Notebook | Wynik | Czas | Uwagi |
|---|---|---|---|---|---|
| | | | | | |

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
- [ ] Nazwa katalogu Marketplace to `databricks_simulated_retail_customer_data.v01`; licencja pozwala na redystrybucję pochodnej.
- [ ] Walidacja po pseudonimizacji przechodzi (28 813 wierszy, segmenty, NY 3 417, 26 862 bez zamówień, VIP 1038,72).
- [ ] Generator PDF pobiera font DejaVu (dostęp do GitHub z Serverless); 10 PDF razem < 5 MB.
- [ ] `ai_parse_document` w wersji 2.0 zwraca ten sam kształt JSON co w WS3; liczba chunków 50–80.
- [ ] `w.genie.list_spaces()` / `start_conversation_and_wait` działają dla Genie Agents; klucze metryk `mlflow.genai.evaluate` mają postać `<scorer>/mean`.
- [ ] `databricks fs cp -r dbfs:/Volumes/...` kopiuje eksport do repo; cały eksport < 20 MB.

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
