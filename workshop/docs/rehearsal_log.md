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

**Moduły (przed budową M2–M6)**
- [ ] Nazwy klas retrievera i zasobów po zmianie nazwy (`databricks-langchain` 0.20, `mlflow.models.resources`).
- [ ] Managed MCP (`/api/2.0/mcp/functions|ai-search|genie/...`) na Free Edition.
- [ ] Reranker w `databricks-ai-search` na Free.
