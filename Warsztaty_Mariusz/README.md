# Retail Customer Intelligence — seria 4 warsztatów Databricks


> **Ta wersja** jest przygotowana do uruchomienia na **Databricks Free Edition** (Community / Trial workspace).


Kompletny case study: od surowych danych z Marketplace po zabezpieczonego AI agenta
z chatbotem RAG i aplikacją webową. Wszystko na jednym datasecie klientów B2B
elektroniki użytkowej (28 813 klientów, 4 074 zamówień).

## Wymagania

- Databricks workspace z Unity Catalog (Free Edition wystarczy)
- Serverless compute
- Dostęp do Databricks Marketplace (dataset: `databricks_simulated_retail_customer_data`)
- Model endpoint: `databricks-meta-llama-3-3-70b-instruct`
- Schema `workspace.default` (dostępna domyślnie — nie wymaga tworzenia)

## Struktura warsztatów

```
WS1: BUDOWA              WS2: ZABEZPIECZENIE            WS3: RAG                   WS4: AGENT APP
═════════════════════    ════════════════════════════    ═══════════════════════    ════════════════════════
Marketplace → SQL         Guardrails LLM: przykłady,     PDF docs (fpdf2)            UC Functions (SQL+Py)
↓                          system prompt, safety filter,  ↓                            + test payloadem
 AI Functions               własny guard (S1–S6),         ai_parse_document()         ↓
↓                          AI Gateway (+ secret scope)   ↓                            LangChain Agent + guardrails
Tool Calling (UC Func)    ↓                              Chunking (600/100)         ↓
↓                          Guardrails UC (Row/Col)       ↓                            MLflow Tracing (Workspace/UC)
PySpark → Gold Table -→  ↓                              Vector Search (ANN/hybrid)  ↓
↓                          Ewaluacja (Gold+Genie)        ↓                            MCP Google Drive (Docs/Sheets)
ML + Registry @champion   + benchmark A/B (ROUGE, 1–5)  RAG chain → UC @champion    ↓
↓                          ↓                              ↓                            UC Model @champion
Dashboard + Genie Space   Monitoring danych (Snapshot)   Knowledge Assistant         ↓
                           + monitoring LLM (TimeSeries)  ↓                            Model Serving + inference table
                                                          Porównanie 3 RAGów         ↓ batch ai_query
                                                                                      Databricks App (Gradio)
```

## Notebooki

### WS1 — Od danych do AI (~105 min)

**Plik:** `WS1 Retail Forecasting od danych do AI.ipynb`

Budowa kompletnego pipeline analitycznego:

| Sekcja | Temat | Funkcjonalności Databricks |
| --- | --- | --- |
| 1 | Eksploracja danych z Marketplace | Unity Catalog, SQL w notebooku |
| 2 | Zaawansowana analityka SQL | CTE, Window Functions, LAG, RANK |
| 3 | AI Functions w SQL | `ai_query()`, `ai_classify()` |
| 5b | **Tool Calling** — LLM wywołuje UC Function | OpenAI API, `get_revenue_summary`, parametryzowany SQL |
| 4 | Feature engineering (RFM) | PySpark, JSON parsing, JOIN |
| 5 | Gold Table w Delta Lake | ACID, Time Travel, DESCRIBE HISTORY |
| 6-8 | Model ML + rejestracja | scikit-learn, MLflow, AutoML, Unity Catalog Model Registry |
| 9 | Prognoza przychodów | Random Forest na cechach czasowych |
| 10 | Dashboard + Genie Space | Lakeview API, Genie Spaces API |

**Wynik:** Tabela `workspace.default.gold_customer_360` (28 813 wierszy × 19 kolumn),
model `loyalty_segment_classifier` w UC, dashboard i Genie Space.

---

### WS2 — Guardrails, Ewaluacja, Monitoring (~115 min)

**Plik:** `WS2 Retail Workshop Guardrails Monitoring Ewaluacja.ipynb`

Zabezpieczenie i walidacja tego, co zbudowano w WS1:

| Część | Temat | Kluczowe API |
| --- | --- | --- |
| 1 | Guardrails LLM | System prompt, `enable_safety_filter`, **własny guard (taksonomia S1–S6, wzór Llama Guard)**, **AI Gateway** (+ secret scope, PII block, inference table) |
| 2 | Guardrails danych (UC) | `ROW FILTER`, `COLUMN MASK`, `GRANT/REVOKE` |
| 3 | Ewaluacja + **benchmark A/B** | `mlflow.genai.evaluate()`, scorery: Safety, Guidelines, PII, Correctness; **ROUGE-1, sędzia 1–5 (mean/variance)**, log inferencji |
| 4 | Monitoring jakości + **monitoring LLM** | Lakehouse Monitoring SDK (Snapshot), profil, dryf; **Time Series 5 min**: toxicity, readability, refusal na odpowiedziach |

**Wynik:** Guardrails na `gold_customer_360` (column mask na `tax_id`, row filter na `state`),
ewaluacja Genie Space, monitor z profilem i detekcją dryfu.

---

### WS3 — RAG i Knowledge Assistant (~90 min)

**Plik:** `WS3 Retail Workshop RAG i Knowledge Assistant.ipynb`

Dwa podejścia do RAG — od zera i managed:

| Część | Temat | Narzędzia |
| --- | --- | --- |
| 1 | Generowanie 10 artykułów PDF | `fpdf2`, `matplotlib`, `ai_query()`, UC Volume |
| 2 | Custom RAG z Vector Search | `ai_parse_document()`, **chunking** (600/100), Delta Sync index, `databricks-gte-large-en`, ANN/hybrid/full-text, filtry, reranking |
| 3 | Knowledge Assistant (managed) | Agent Bricks SDK, quality examples |
| 4 | Porównanie i ewaluacja | 3-way: Genie vs Custom RAG vs KA, `mlflow.genai.evaluate()` |
| - | Interaktywny widget | `dbutils.widgets` — odpytuj oba RAG-i z jednego miejsca |

**Wynik:** 10 PDF w UC Volume, Vector Search index, Knowledge Assistant z 9 quality examples,
tabela porównawcza 3 interfejsów AI.

---

### WS4 — Agent App (~120 min)

**Plik:** `WS4 Retail Workshop Agent App.ipynb`

Od UC Functions po produkcyjną aplikację webową:

| Akt | Temat | Kluczowe |
| --- | --- | --- |
| 1 | Konfiguracja + przegląd Gold | `unitycatalog-ai`, `databricks-langchain` |
| 2 | UC Functions (SQL + Python UDF) | `get_average_customer_value`, `get_customer_profile`, `format_customer_for_agent` |
| 3 | Agent + MLflow Tracing | `UCFunctionToolkit`, `ChatDatabricks`, `AgentExecutor`, autolog, trace'y w UC |
| 3b | **MCP Google Drive** | `DatabricksMCPServer`, `DatabricksMultiServerMCPClient`, LangGraph, 13 narzędzi Google (Docs/Sheets/Slides) |
| 4 | Rejestracja modelu w UC | `mlflow.pyfunc.log_model`, `mlflow.register_model` |
| 5 | Wdrożenie jako Databricks App | Model Serving endpoint, Gradio UI, `w.apps.create_and_wait()` |

**Wynik:** Agent zarejestrowany w Unity Catalog, REST API endpoint,
Databricks App z interfejsem Gradio.

---

### Przewodnik

**Plik:** `Przewodnik Scenariusz i Przewodnik.ipynb`

Scenariusz dla prowadzącego z:
- Historią biznesową (persona: analityk w TechRetail Corp)
- Mapą 4 warsztatów z zależnościami
- Szczegółowym planem każdego aktu (kontekst fabularny, co robimy, oczekiwane wyniki)
- Punktami dyskusji i momentami kluczowymi
- Tabelą funkcjonalności Databricks użytych w case study
- Checklistą przygotowania prowadzącego

## Czas trwania

| Warsztat | Czas | Komórki |
| --- | --- | --- |
| WS1: Budowa | ~105 min | 39 |
| WS2: Zabezpieczenie | ~115 min | 71 |
| WS3: RAG | ~90 min | 40 |
| WS4: Agent App | ~120 min | 36 |
| **Razem** | **~7h 10min** | **186** |

## Tabela bazowa

`workspace.default.gold_customer_360` — 28 813 klientów B2B × 19 kolumn:

| Kolumna | Typ | Opis |
| --- | --- | --- |
| `customer_id` | string | Unikalny identyfikator klienta |
| `customer_name` | string | Nazwa firmy (PII) |
| `tax_id` | string | Numer podatkowy (PII, ~67% null) |
| `state`, `city` | string | Lokalizacja |
| `loyalty_segment` | int | 0=Nowi, 1=Rozwijający, 2=Regularni, 3=VIP |
| `recency_days` | double | Dni od ostatniej aktywności |
| `frequency` | double | Częstotliwość transakcji |
| `monetary` | double | Łączna wartość zakupów ($) |
| `num_orders` | long | Liczba zamówień |
| `promo_ratio` | double | Udział zakupów promocyjnych |



## Funkcjonalności Databricks

| Funkcjonalność | Warsztat |
| --- | --- |
| Databricks Marketplace | WS1 |
| Unity Catalog (3-level namespace) | Wszystkie |
| AI Functions (`ai_query`, `ai_classify`) | WS1, WS3 |
| `ai_parse_document()` | WS3 |
| PySpark (JSON parsing, RFM) | WS1 |
| Delta Lake (ACID, Time Travel) | WS1 |
| MLflow (autolog, tracking, registry) | WS1, WS3, WS4 |
| `mlflow.genai.evaluate()` | WS2, WS3 |
| Dashboard SDK (Lakeview) | WS1 |
| Genie Spaces | WS1, WS2, WS3 |
| Row Filter / Column Mask | WS2 |
| Lakehouse Monitoring | WS2 |
| Vector Search | WS3 |
| Knowledge Assistant (Agent Bricks) | WS3 |
| UC Functions (SQL + Python UDF) | WS4 |
| UCFunctionToolkit + LangChain | WS4 |
| MLflow Tracing | WS4 |
| Model Serving | WS4 |
| Databricks Apps (Gradio) | WS4 |
| **Tool Calling** (UC Function + OpenAI API) | WS1 |
| **AI Gateway** (guardrails, PII block, inference table, secret scope) | WS2 |
| **Benchmark A/B** (ROUGE-1, sędzia 1–5 mean/variance) | WS2 |
| **Monitoring odpowiedzi LLM** (Time Series 5 min) | WS2 |
| **Chunking** (RecursiveCharacterTextSplitter 600/100) | WS3 |
| **MCP Google Drive** (Model Context Protocol, 13 narzędzi) | WS4 |

## Licencja

Materiały warsztatowe. Dane syntetyczne z Databricks Marketplace.
