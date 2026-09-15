# Mapowanie komórek: notebooki warsztatu → materiał źródłowy

Wygenerowano automatycznie (2026-09-15) przez `workshop/scripts/build_cell_mapping.py` z markerów `source:`.
Indeksy `WSx[i]` są 0-based (jak w pliku .ipynb); prezentacja i Przewodnik Mariusza liczą komórki od 1 (dodaj 1).

## `workshop/00_setup/00_setup.ipynb` — M0 · Start: dane TechRetail w Twoim workspace

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `setup-intro` | markdown | M0 · Start: dane TechRetail w Twoim workspace | `new + PRZ[1]` | adapted |
| 2 | `setup-pip` | code |  | `?` | adapted |
| 3 | `setup-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `setup-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `setup-paths` | code | import os | `new` | new |
| 6 | `setup-gold-intro` | markdown | 1. Tabela Gold: `gold_customer_360` | `WS1[15]` | adapted |
| 7 | `setup-gold` | code | import pandas as pd | `new + WS1[16]` | adapted |
| 8 | `setup-explore-segments` | code | SELECT | `WS1[5]` | adapted |
| 9 | `setup-explore-states` | code | SELECT state, COUNT(*) AS klienci, ROUND(AVG(monetary), 2) AS avg_mone | `WS1[6]` | adapted |
| 10 | `setup-ai-query` | code | display(spark.sql(f""" | `WS1[11]` | adapted / optional |
| 11 | `setup-history` | code | DESCRIBE HISTORY workspace.default.gold_customer_360 | `WS1[17]` | adapted / optional |
| 12 | `setup-docs-intro` | markdown | 2. Raporty PDF w Volume | `WS3[3]` | adapted |
| 13 | `setup-docs` | code | import shutil | `WS3[7]` | adapted |
| 14 | `setup-chunks-intro` | markdown | 3. Fragmenty raportów: `retail_rag_chunks` | `WS3[13]` | adapted |
| 15 | `setup-chunks` | code | chunks_pdf = pd.read_parquet(DATA_DIR / "checkpoints" / "retail_rag_ch | `WS3[16]` | adapted |
| 16 | `setup-search-intro` | markdown | 4. Endpoint AI Search (dawniej Vector Search) | `WS3[8]` | adapted |
| 17 | `setup-search-endpoint` | code | from databricks.ai_search.client import AISearchClient | `new` | new |
| 18 | `setup-preflight-intro` | markdown | 5. Preflight | `new` | new |
| 19 | `setup-preflight` | code | import mlflow | `new` | new |
| 20 | `setup-lab` | markdown | Lab: poznaj dane, zanim zapytasz o nie model | `new` | new |
| 21 | `setup-summary` | markdown | Podsumowanie | `new` | new |

## `workshop/00_setup/01_trainer_prepare_premium.ipynb` — Przygotowanie prowadzącego: workspace Premium w dniu warsztatu

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `prep-intro` | markdown | Przygotowanie prowadzącego: workspace Premium w dniu warsztatu | `new + PRZ[19]` | adapted |
| 2 | `prep-pip` | code |  | `?` | adapted |
| 3 | `prep-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `prep-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `prep-context` | code | import os | `new` | new |
| 6 | `prep-step1` | markdown | 1. Dane jak u uczestników | `new` | new |
| 7 | `prep-verify-data` | code | expected = {GOLD_TABLE: 28_813, CHUNKS_TABLE: None} | `new` | new |
| 8 | `prep-step2` | markdown | 2. AI Search: endpoint i indeks do skutku | `WS3[19]` | adapted |
| 9 | `prep-search` | code | from databricks.ai_search.client import AISearchClient | `WS3[19] + new` | adapted |
| 10 | `prep-steps3-6` | markdown | 3–6. Funkcje, Genie, Knowledge Assistant, agent i aplikacja | `new + PRZ[19]` | adapted |
| 11 | `prep-readiness` | code | import mlflow | `new + PRZ[19]` | adapted |
| 12 | `prep-free-dry-run` | markdown | Próba na koncie Free Edition (raz przed warsztatem) | `new` | new |

## `workshop/00_setup/02_trainer_teardown.ipynb` — Sprzątanie po warsztacie (prowadzący)

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `teardown-intro` | markdown | Sprzątanie po warsztacie (prowadzący) | `new` | new |
| 2 | `teardown-pip` | code |  | `?` | adapted |
| 3 | `teardown-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `teardown-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `teardown-plan` | code | from databricks.ai_search.client import AISearchClient | `new + WS4[35]` | adapted |
| 6 | `teardown-costs` | markdown | Koszt dnia (dzień po warsztacie) | `new` | new |
| 7 | `teardown-billing` | code | SELECT usage_date, billing_origin_product, ROUND(SUM(usage_quantity),  | `new` | new / optional |

## `workshop/demo/m1_agentic_ai_playground.ipynb` — M1 · Agentic AI i AI Playground

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `m1-intro` | markdown | M1 · Agentic AI i AI Playground | `new + slide 13–14` | adapted |
| 2 | `m1-pip` | code |  | `?` | adapted |
| 3 | `m1-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `m1-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `m1-concepts` | markdown | 1. Chatbot, RAG, agent: trzy różne rzeczy | `slide 6 + slide 15 + slide 16 + slide 18` | adapted |
| 6 | `m1-prompt` | markdown | 2. System prompt: pierwsza i najtańsza warstwa zasad | `WS2[4] + WS2[5]` | adapted |
| 7 | `m1-ask` | code | import time | `WS2[6]` | adapted / lab |
| 8 | `m1-four-intro` | markdown | 3. Cztery pytania testowe, cztery oczekiwania | `slide 21 + WS2[2] + WS2[3]` | adapted |
| 9 | `m1-four-questions` | code | import pandas as pd | `slide 21 + WS2[7]` | adapted |
| 10 | `m1-ablation-intro` | markdown | Ablacja: usuń jedno zdanie i patrz, co się zmienia | `slide 22` | adapted / optional |
| 11 | `m1-ablation` | code | ALTERNATIVE_SENTENCE = "Gdy odmawiasz, zaproponuj legalną alternatywę  | `slide 22` | adapted / lab / optional |
| 12 | `m1-safety-intro` | markdown | (opcjonalnie) Filtr bezpieczeństwa platformy | `WS2[8] + K:Warsztaty_Krzysztof/sprawozdanie_zbiorcze_v3.pdf` | adapted / optional |
| 13 | `m1-safety-filter` | code | try: | `WS2[9]` | adapted / optional |
| 14 | `m1-playground-lab` | markdown | 4. Lab w AI Playground: pierwszy prototyp bez kodu | `slide 22 + WS2[4]` | adapted |
| 15 | `m1-print-prompt` | code | print(SYSTEM_PROMPT) | `new` | new |
| 16 | `m1-levels` | markdown | Poziomy 2 i 3: kiedy skończysz ścieżkę | `new` | new |
| 17 | `m1-card` | markdown | Karta wzorca: system prompt dla nowej domeny | `new + slide 18` | adapted |
| 18 | `m1-summary` | markdown | Podsumowanie | `new + slide 18` | adapted |

## `workshop/demo/m2_tool_calling.ipynb` — M2 · Tool calling: model wywołuje Twoje funkcje

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `m2-intro` | markdown | M2 · Tool calling: model wywołuje Twoje funkcje | `new + slide 23–24` | adapted |
| 2 | `m2-pip` | code |  | `?` | adapted |
| 3 | `m2-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `m2-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `m2-context` | code | import json | `new + WS4[3] + WS4[9]` | adapted |
| 6 | `m2-tool-anatomy` | markdown | Czym jest narzędzie dla modelu | `slide 25 + slide 27 + slide 28` | adapted |
| 7 | `m2-revenue-intro` | markdown | 1. Pierwsze narzędzie: `get_revenue_summary` | `WS1[19]` | adapted |
| 8 | `m2-revenue-function` | code | CREATE OR REPLACE FUNCTION workspace.default.get_revenue_summary( | `WS1[20]` | adapted / lab |
| 9 | `m2-tool-calling-intro` | markdown | 2. Tool calling „ręcznie”: cztery kroki | `WS1[19] + slide 27` | adapted / optional |
| 10 | `m2-tool-calling` | code | tools = [{ | `WS1[21]` | adapted / lab / optional |
| 11 | `m2-three-tools-intro` | markdown | 3. Trzy narzędzia agenta | `WS4[5] + slide 28` | adapted |
| 12 | `m2-avg-value-function` | code | CREATE OR REPLACE FUNCTION workspace.default.get_average_customer_valu | `WS4[6]` | adapted |
| 13 | `m2-profile-function` | code | CREATE OR REPLACE FUNCTION workspace.default.get_customer_profile( | `WS4[7]` | adapted |
| 14 | `m2-python-udf-intro` | markdown | Funkcja Python w Unity Catalog | `WS4[5]` | adapted |
| 15 | `m2-python-udf` | code | from unitycatalog.ai.core.databricks import DatabricksFunctionClient | `WS4[8]` | adapted / lab |
| 16 | `m2-payload-intro` | markdown | 4. Test surowym payloadem: unit test narzędzia | `WS4[9] + slide 29` | adapted |
| 17 | `m2-payload-test` | code | import re | `WS4[9]` | adapted |
| 18 | `m2-describe-function` | code | display(spark.sql(f"DESCRIBE FUNCTION EXTENDED {PROFILE_FUNCTION}")) | `slide 29` | adapted / optional |
| 19 | `m2-playground-lab` | markdown | 5. Lab w AI Playground: funkcje jako Tools | `WS4[10] + slide 31` | adapted |
| 20 | `m2-fallback` | markdown | Fallback: co robi dobry agent, gdy nic nie pasuje | `slide 30` | adapted |
| 21 | `m2-levels` | markdown | Poziomy 2 i 3: kiedy skończysz ścieżkę | `new` | new |
| 22 | `m2-bonus-bakehouse` | code | CREATE OR REPLACE FUNCTION workspace.default.bh_payment_methods( | `new + K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py` | adapted / lab / poziom 2 |
| 23 | `m2-card` | markdown | Karta wzorca: narzędzie tabelaryczne | `new + slide 28` | adapted |
| 24 | `m2-summary` | markdown | Podsumowanie | `new` | new |

## `workshop/demo/m3_rag_ai_search.ipynb` — M3 · RAG jako narzędzie: raporty, chunking, AI Search

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `m3-intro` | markdown | M3 · RAG jako narzędzie: raporty, chunking, AI Search | `new + slide 32–33 + slide 38` | adapted |
| 2 | `m3-pip` | code |  | `?` | adapted |
| 3 | `m3-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `m3-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `m3-context` | code | import os | `new` | new |
| 6 | `m3-parse-intro` | markdown | 1. Od PDF do tekstu: `ai_parse_document` | `WS3[3] + WS3[8]` | adapted / optional |
| 7 | `m3-parse` | code | if RUN_PARSE: | `WS3[9]` | adapted / lab / optional |
| 8 | `m3-parse-metadata` | code | if "parsed_json" not in spark.table(DOCS_TABLE).columns: | `WS3[11]` | adapted / optional |
| 9 | `m3-render-page` | code | import base64 | `WS3[12] + K:Warsztaty_Krzysztof/rag_agent/notebooks/includes/document_renderer.py` | adapted / optional |
| 10 | `m3-chunking-intro` | markdown | 2. Chunking: dlaczego nie cały dokument | `WS3[13]` | adapted |
| 11 | `m3-plain-text` | code | import html as _html | `WS3[14]` | adapted |
| 12 | `m3-chunking-lab` | markdown |  | `WS3[13] + slide 37` | adapted |
| 13 | `m3-chunking` | code | from langchain_text_splitters import RecursiveCharacterTextSplitter | `WS3[16]` | adapted / lab |
| 14 | `m3-embedding-intro` | markdown | 3. Embedding: tekst zamieniony na 1024 liczby | `WS3[17] + slide 36` | adapted / optional |
| 15 | `m3-embedding` | code | import mlflow.deployments | `WS3[18]` | adapted / lab / optional |
| 16 | `m3-search-intro` | markdown | 4. Indeks AI Search (dawniej Vector Search) | `WS3[8] + slide 39` | adapted |
| 17 | `m3-search-index` | code | from databricks.ai_search.client import AISearchClient | `WS3[19]` | adapted |
| 18 | `m3-retrievers` | code | import re | `WS3[20] + WS3[18]` | adapted |
| 19 | `m3-rag-intro` | markdown | RAG z cytatami: szukaj, doklej, odpowiedz | `slide 40 + WS3[20]` | adapted |
| 20 | `m3-custom-rag` | code | def custom_rag(question: str, k: int = 3, query_type: str = "ANN") ->  | `WS3[20]` | adapted / lab |
| 21 | `m3-six-questions` | code | test_questions = [ | `WS3[20]` | adapted |
| 22 | `m3-modes-intro` | markdown | 5. Trzy tryby wyszukiwania i filtr | `WS3[21] + slide 39` | adapted |
| 23 | `m3-search-modes` | code | question = "Które segmenty mają wysoki promo_ratio i co to oznacza dla | `WS3[22]` | adapted |
| 24 | `m3-reranker` | code | if not SEARCH_READY: | `WS3[24]` | adapted / optional |
| 25 | `m3-playground-lab` | markdown | 6. Lab w AI Playground: indeks jako Tool | `WS3[25]` | adapted |
| 26 | `m3-chain-intro` | markdown | Ten sam RAG jako łańcuch LangChain, ze śladem w MLflow | `WS3[26]` | adapted |
| 27 | `m3-chain` | code | import mlflow | `WS3[27]` | adapted |
| 28 | `m3-ka` | markdown | Demo prowadzącego: Knowledge Assistant (Agent Bricks) | `WS3[29] + K:Warsztaty_Krzysztof/rag_agent/notebooks/05_building_assistant.py` | adapted / trainer_only |
| 29 | `m3-ka-query` | code | KA_ENDPOINT = ""  # nazwa endpointu z karty Knowledge Assistant, np. k | `WS3[33]` | adapted / trainer_only |
| 30 | `m3-levels` | markdown | Poziomy 2 i 3: kiedy skończysz ścieżkę | `new + K:Warsztaty_Krzysztof/rag_agent/notebooks/03_vector_search.py` | adapted |
| 31 | `m3-bonus-bakehouse` | code | reviews = (spark.table("samples.bakehouse.media_customer_reviews") | `new + WS3[18] + WS3[20]` | adapted / lab / poziom 2 |
| 32 | `m3-card` | markdown | Karta wzorca: dokumenty jako narzędzie | `new + slide 38 + K:Warsztaty_Krzysztof/rag_agent/notebooks/02_chunking.py` | adapted |
| 33 | `m3-summary` | markdown | Podsumowanie | `new + WS3[39]` | adapted |

## `workshop/demo/m4_sql_genie_governance.ipynb` — M4 · Dane tabelaryczne: SQL, Genie Agent i kontrola dostępu

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `m4-intro` | markdown | M4 · Dane tabelaryczne: SQL, Genie Agent i kontrola dostępu | `new + slide 42–44` | adapted |
| 2 | `m4-pip` | code |  | `?` | adapted |
| 3 | `m4-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `m4-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `m4-context` | code | import re | `new` | new |
| 6 | `m4-expected-intro` | markdown | 1. Odpowiedź z tabeli: oczekiwane wyniki | `WS2[36] + WS3[20]` | adapted |
| 7 | `m4-expected-values` | code | EXPECTED_SQL = { | `WS3[20] + WS2[37]` | adapted / lab |
| 8 | `m4-function-vs-genie` | markdown | Kiedy funkcja Unity Catalog, a kiedy Genie | `slide 46` | adapted |
| 9 | `m4-genie-lab` | markdown | 2. Lab: Genie Agent nad tabelą Gold | `WS1[37] + slide 45 + slide 48` | adapted |
| 10 | `m4-genie-sdk` | code | def find_genie_space_id(title: str) -> str \| None: | `WS2[39–41]` | adapted / optional |
| 11 | `m4-governance-intro` | markdown | 3. Dostęp do danych w kontrolowany sposób: dwie warstwy | `slide 47 + WS2[17] + WS2[20] + slide 64` | adapted |
| 12 | `m4-grants` | code | SHOW GRANTS ON TABLE workspace.default.gold_customer_360 | `WS2[21]` | adapted |
| 13 | `m4-row-filter-intro` | markdown | Row filter: które wiersze widzi użytkownik | `WS2[24]` | adapted |
| 14 | `m4-row-filter` | code | CREATE OR REPLACE FUNCTION workspace.default.retail_row_filter(state_v | `WS2[25] + WS2[26]` | adapted |
| 15 | `m4-mask-intro` | markdown | Column mask: jakie wartości kolumny widzi użytkownik | `WS2[27]` | adapted |
| 16 | `m4-column-mask` | code | CREATE OR REPLACE FUNCTION workspace.default.mask_tax_id(tax_id_val ST | `WS2[28] + WS2[30]` | adapted / lab |
| 17 | `m4-governance-check` | markdown |  | `slide 47` | adapted |
| 18 | `m4-two-identities` | markdown | Demo prowadzącego: dwie tożsamości na Premium | `WS2[24] + WS2[27]` | adapted / trainer_only |
| 19 | `m4-cleanup-intro` | markdown | 4. Obowiązkowo przed M5: zdejmij filtr i maskę | `WS2[31]` | adapted |
| 20 | `m4-cleanup` | code | for statement in [ | `WS2[32] + new` | adapted |
| 21 | `m4-genie-baseline` | code | import json | `WS3[36] + WS2[42]` | adapted / trainer_only |
| 22 | `m4-genie-tool-lab` | markdown | (jeśli zostanie czas) Genie Agent jako Tool w Playground | `slide 48` | adapted |
| 23 | `m4-levels` | markdown | Poziomy 2 i 3: kiedy skończysz ścieżkę | `new` | new |
| 24 | `m4-bonus-bakehouse` | code | BH_TABLE = f"{CATALOG}.{SCHEMA}.bh_transactions" | `new + WS2[28]` | adapted / lab / poziom 2 |
| 25 | `m4-card` | markdown | Karta wzorca: kontrolowany dostęp do danych | `new + slide 47` | adapted |
| 26 | `m4-summary` | markdown | Podsumowanie | `new` | new |

## `workshop/demo/m5_end_to_end_agent.ipynb` — M5 · Agent end-to-end: agent wybiera RAG albo tabelę

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `m5-intro` | markdown | M5 · Agent end-to-end: agent wybiera RAG albo tabelę | `new + slide 49–50` | adapted |
| 2 | `m5-pip` | code |  | `?` | adapted |
| 3 | `m5-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `m5-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `m5-architecture` | markdown | Architektura agenta | `WS4[11] + slide 51` | adapted |
| 6 | `m5-context` | code | import json | `new + WS4[3] + WS4[4]` | adapted |
| 7 | `m5-tracing-intro` | markdown | 1. Tracing przed agentem | `WS4[14] + slide 54` | adapted |
| 8 | `m5-tracing` | code | experiment = mlflow.set_experiment(f"/Users/{USERNAME}/{EXPERIMENT_NAM | `WS4[14]` | adapted |
| 9 | `m5-retrieve-local` | code | import mlflow.deployments | `WS3[18] + new` | adapted |
| 10 | `m5-agent-intro` | markdown | 2. Agent z czterema narzędziami | `WS4[12] + slide 52` | adapted |
| 11 | `m5-build-agent` | code | from databricks_langchain import ChatDatabricks, UCFunctionToolkit, Ve | `WS4[12]` | adapted / lab |
| 12 | `m5-routes-intro` | markdown | 3. Macierz tras: sześć pytań, sześć oczekiwanych tras | `slide 52 + slide 53 + WS4[13]` | adapted |
| 13 | `m5-route-matrix` | code | TAX_ID_PATTERN = re.compile(r"\d{2}-\d{7}") | `WS4[13] + new + K:Warsztaty_Krzysztof/single_agent_app/notebooks/09_tagging.py` | adapted |
| 14 | `m5-trace-reading` | markdown | Jak czytać trace | `slide 54` | adapted |
| 15 | `m5-own-question` | code | my_question = "Które segmenty mają najwyższy promo_ratio i co raporty  | `new` | new / lab |
| 16 | `m5-repair-intro` | markdown | 4. Pętla poprawy: test, ślad, jedna zmiana, test (w parach) | `slide 54` | adapted |
| 17 | `m5-repair` | code | FIXED_SYSTEM_PROMPT = SYSTEM_PROMPT | `new + slide 54` | adapted |
| 18 | `m5-judge-intro` | markdown | (opcjonalnie) Jakość odpowiedzi: sędzia LLM | `slide 53 + WS2[39–41] + K:Warsztaty_Krzysztof/genai_eval_and_monitor/notebooks/14_llm_as_a_judge.py` | adapted / optional |
| 19 | `m5-judge` | code | from mlflow.entities import Feedback | `WS2[42] + K:Warsztaty_Krzysztof/genai_eval_and_monitor/notebooks/14_llm_as_a_judge.py` | adapted / optional |
| 20 | `m5-responses-intro` | markdown | 5. `ResponsesAgent`: standardowy interfejs agenta | `WS4[20] + new` | adapted |
| 21 | `m5-responses-agent` | code | from uuid import uuid4 | `new` | new |
| 22 | `m5-log-register` | code | from importlib.metadata import version as package_version | `WS4[21] + WS4[22] + WS4[23]` | adapted / trainer_only |
| 23 | `m5-apps-demo` | markdown | Demo prowadzącego: agent w Databricks Apps | `WS4[30] + WS4[31] + slide 55` | adapted / trainer_only |
| 24 | `m5-apps-status` | code | APP_NAME = "sqlday-retail-agent" | `WS4[31]` | adapted / trainer_only |
| 25 | `m5-back-to-m1` | markdown | 6. Wróć do czterech pytań z M1 | `slide 21 + slide 55` | adapted / optional |
| 26 | `m5-back-to-m1-compare` | code | FOUR_QUESTIONS = [ | `slide 21 + new` | adapted / optional |
| 27 | `m5-levels` | markdown | Poziomy 2 i 3: kiedy skończysz ścieżkę | `new` | new |
| 28 | `m5-card` | markdown | Karta wzorca: agent, który wybiera trasę | `new + slide 52 + slide 54` | adapted |
| 29 | `m5-summary` | markdown | Podsumowanie | `new` | new |

## `workshop/demo/m5b_transfer_capstone.ipynb` — M5+ · Przenieś wzorzec na swoje dane

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `m5b-intro` | markdown | M5+ · Przenieś wzorzec na swoje dane | `new` | new |
| 2 | `m5b-pip` | code |  | `?` | adapted |
| 3 | `m5b-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `m5b-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `m5b-choose-intro` | markdown | 1. Wybierz dane | `new + slide 47` | adapted |
| 6 | `m5b-choose-data` | code | import os | `new + K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py` | adapted |
| 7 | `m5b-canvas-intro` | markdown | 2. Canvas w kodzie: domena, zasady i trzy trasy | `new + slide 52` | adapted |
| 8 | `m5b-canvas` | code | MY_DOMAIN = "sieć piekarni Bakehouse" | `new + slide 52` | adapted / lab |
| 9 | `m5b-function-intro` | markdown | 3. Funkcja Unity Catalog z COMMENT | `K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py + slide 28` | adapted |
| 10 | `m5b-function` | code | spark.sql(f""" | `K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py + WS4[9]` | adapted / lab |
| 11 | `m5b-text-intro` | markdown | 4. (jeśli masz tekst) Wyszukiwanie w opiniach jako drugie narzędzie | `WS3[20] + slide 34` | adapted |
| 12 | `m5b-text-tool` | code | from langchain_core.tools import StructuredTool | `WS3[20] + WS4[12]` | adapted |
| 13 | `m5b-agent-intro` | markdown | 5. Agent i macierz tras | `WS4[13] + slide 54` | adapted |
| 14 | `m5b-agent` | code | import mlflow | `WS4[12] + WS4[13] + K:Warsztaty_Krzysztof/single_agent_app/notebooks/09_tagging.py` | adapted |
| 15 | `m5b-exit-card` | markdown | 6. Karta wyjściowa i pokaz | `new` | new |
| 16 | `m5b-summary` | markdown | Podsumowanie | `new` | new |

## `workshop/demo/m6_mcp_security_next_steps.ipynb` — M6 · MCP, bezpieczeństwo i dalszy rozwój

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `m6-intro` | markdown | M6 · MCP, bezpieczeństwo i dalszy rozwój | `new + slide 56–57` | adapted |
| 2 | `m6-pip` | code |  | `?` | adapted |
| 3 | `m6-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `m6-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `m6-context` | code | import asyncio | `new + WS4[18]` | adapted |
| 6 | `m6-mcp-intro` | markdown | 1. MCP na Databricks: agent jako klient, narzędzia jako serwery | `slide 58 + slide 59 + WS4[17]` | adapted |
| 7 | `m6-mcp-client` | code | from databricks_mcp import DatabricksMCPClient | `new + WS4[18]` | adapted / lab |
| 8 | `m6-agent-intro` | markdown | 2. Demo: agent z narzędziami z trzech serwerów MCP | `WS4[17] + slide 60` | adapted |
| 9 | `m6-mcp-agent` | code | from databricks_langchain import ChatDatabricks, DatabricksMCPServer,  | `WS4[19]` | adapted |
| 10 | `m6-risks` | markdown | 3. Ryzyka agentów: czym różnią się od ryzyk czatu | `slide 61 + slide 62 + slide 63 + WS2[10] + WS2[13]` | adapted |
| 11 | `m6-least-privilege` | markdown | Least privilege: agent to tożsamość, nie funkcja | `slide 64` | adapted |
| 12 | `m6-free-limits` | markdown | 4. Ograniczenia Free Edition i małych środowisk | `slide 65 + K:Warsztaty_Krzysztof/sprawozdanie_zbiorcze_v3.pdf` | adapted |
| 13 | `m6-next-steps` | markdown | Cykl życia agenta i co dodać przed PoC oraz produkcją | `slide 66 + slide 67 + slide 68 + WS2[47]` | adapted |
| 14 | `m6-closing` | markdown | Co potrafisz po dzisiejszym dniu | `slide 69 + slide 70 + K:Warsztaty_Krzysztof/KONTEKST_KONTYNUACJI_PROJEKTU.md` | adapted |
| 15 | `m6-card` | markdown | Karta wzorca: od prototypu do PoC na Twoich danych | `new + slide 64 + slide 67` | adapted |
| 16 | `m6-summary` | markdown | Podsumowanie | `new` | new |

## `workshop/pattern/p2_uc_functions_bakehouse.ipynb` — Wzorzec M2 · Funkcje Unity Catalog na danych Bakehouse

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `p2-intro` | markdown | Wzorzec M2 · Funkcje Unity Catalog jako narzędzia, na danych Bakehouse | `new + K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py` | adapted |
| 2 | `p2-pip` | code |  | `?` | adapted |
| 3 | `p2-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `p2-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `p2-context` | code | from unitycatalog.ai.core.databricks import DatabricksFunctionClient | `new` | new |
| 6 | `p2-questions` | markdown | 1. Od pytania biznesowego do funkcji | `K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py + slide 28` | adapted |
| 7 | `p2-franchise-function` | code | CREATE OR REPLACE FUNCTION workspace.default.bh_franchise_summary( | `K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py` | adapted |
| 8 | `p2-product-function` | code | CREATE OR REPLACE FUNCTION workspace.default.bh_product_sales( | `K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py` | adapted |
| 9 | `p2-payload-test` | code | client = DatabricksFunctionClient(execution_mode="serverless") | `K:Warsztaty_Krzysztof/single_agent_app/notebooks/07_building_agent.py` | adapted |
| 10 | `p2-playground` | markdown | 2. Te same funkcje w AI Playground | `K:Warsztaty_Krzysztof/single_agent_app/notebooks/06_building_uc_functions.py + slide 31` | adapted |
| 11 | `p2-pattern-card` | markdown | Karta wzorca: narzędzie tabelaryczne dla agenta | `new + slide 28` | adapted |

## `workshop/pattern/p3_rag_robotics.ipynb` — Wzorzec M3 · RAG od PDF do wyszukiwania na raportach o robotyce

| # | cell id | typ | nagłówek / pierwsza linia | źródło | status |
|---|---|---|---|---|---|
| 1 | `p3-intro` | markdown | Wzorzec M3 · RAG od PDF do wyszukiwania, na raportach o robotyce | `new + K:Warsztaty_Krzysztof/rag_agent/notebooks/01_parse_robotics_documents.py` | adapted |
| 2 | `p3-pip` | code |  | `?` | adapted |
| 3 | `p3-restart` | code | dbutils.library.restartPython() | `WS3[2]` | adapted |
| 4 | `p3-config` | code | CATALOG = "workspace" | `new + WS4[3] + WS2[6]` | adapted |
| 5 | `p3-context` | code | import json | `new + K:Warsztaty_Krzysztof/rag_agent/notebooks/01_parse_robotics_documents.py` | adapted |
| 6 | `p3-parse-intro` | markdown | 1. Parsowanie z obrazami stron i opisami wykresów | `K:Warsztaty_Krzysztof/rag_agent/notebooks/01_parse_robotics_documents.py` | adapted |
| 7 | `p3-parse` | code | if spark.catalog.tableExists(ROBOTICS_PARSED): | `K:Warsztaty_Krzysztof/rag_agent/notebooks/01_parse_robotics_documents.py` | adapted |
| 8 | `p3-render` | code | import base64 | `WS3[12] + K:Warsztaty_Krzysztof/rag_agent/notebooks/includes/document_renderer.py` | adapted |
| 9 | `p3-chunk-intro` | markdown | 2. Chunking: ten sam splitter, inne dokumenty, inne parametry | `K:Warsztaty_Krzysztof/rag_agent/notebooks/02_chunking.py + slide 37` | adapted |
| 10 | `p3-chunking` | code | from langchain_text_splitters import RecursiveCharacterTextSplitter | `K:Warsztaty_Krzysztof/rag_agent/notebooks/02_chunking.py` | adapted |
| 11 | `p3-search-intro` | markdown | 3. Indeks i trzy tryby wyszukiwania | `K:Warsztaty_Krzysztof/rag_agent/notebooks/03_vector_search.py` | adapted |
| 12 | `p3-search` | code | from databricks.ai_search.client import AISearchClient | `K:Warsztaty_Krzysztof/rag_agent/notebooks/03_vector_search.py` | adapted |
| 13 | `p3-knowledge-assistant` | markdown | 4. Ten sam RAG bez kodu: Knowledge Assistant z Guidelines | `K:Warsztaty_Krzysztof/rag_agent/notebooks/05_building_assistant.py` | adapted |
| 14 | `p3-pattern-card` | markdown | Karta wzorca: dokumenty jako narzędzie agenta | `new + slide 38` | adapted |

