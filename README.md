# Od pytania do agenta: warsztat Databricks (SQLDay Lite)

Całodniowy warsztat (09:00–18:00), na którym budujesz agenta AI na Databricks: od rozmowy z modelem w AI Playground, przez narzędzia w Unity Catalog, RAG na raportach PDF i dane tabelaryczne w Genie, do agenta, który sam wybiera źródło odpowiedzi i jest dostępny przez MCP. Na koniec dnia przenosisz ten sam wzorzec na inne dane.

Prowadzą **Krzysztof** i **Mariusz**. Materiał jest po polsku, a kod, nazwy plików i obiektów po angielsku.

## Co zbudujesz

| Moduł | Umiejętność | Efekt |
|---|---|---|
| M0 | przygotowanie danych | tabela klientów, raporty PDF, fragmenty, endpoint AI Search |
| M1 | system prompt, ocena odpowiedzi | punkt odniesienia: co potrafi sam model (i gdzie zmyśla) |
| M2 | tool calling | 3 funkcje Unity Catalog jako narzędzia agenta, test payloadem |
| M3 | RAG | parsowanie PDF, chunking, embeddingi, AI Search, odpowiedzi z cytatami |
| M4 | dane tabelaryczne i dostęp | Genie Agent, row filter, maska kolumny |
| M5 | agent end-to-end | agent z 4 narzędziami, macierz tras, trace w MLflow, `ResponsesAgent` |
| M5+ | transfer wzorca | mini-agent na danych Bakehouse, Airbnb albo własnych |
| M6 | MCP i bezpieczeństwo | narzędzia przez zarządzane serwery MCP, warstwy obrony, least privilege |

**Cel dnia:** agent na danych innych niż TechRetail i jego macierz 3 tras, z co najmniej dwiema trasami zgodnymi.

## Dla kogo

Od początkujących do zaawansowanych. Każdy lab ma trzy poziomy: **ścieżkę** z podpowiedziami, **transfer** na drugą domenę i **własne dane** z wyzwaniem. Przydaje się podstawowa znajomość SQL i Pythona. Nie jest potrzebne doświadczenie z Databricks ani z LLM.

**Wymagania:** laptop z przeglądarką i konto **Databricks Free Edition**. Opcjonalnie zanonimizowany plik CSV na capstone.

## Jak zacząć

| Kim jesteś | Zacznij tu |
|---|---|
| **Uczestnik** | [Przewodnik uczestnika z osią czasu](workshop/docs/przewodnik_uczestnika.md), potem [`workshop/README.md`](workshop/README.md) |
| **Prowadzący** | [Koncepcja dnia](workshop/docs/koncepcja_dnia.md) → [przewodnik prowadzącego](workshop/docs/trainer_guide.md) → [harmonogram](workshop/docs/schedule.md) → `workshop/00_setup/01_trainer_prepare_premium` |
| **Workspace prowadzącego (Azure)** | [`infra/azure_trial/`](infra/azure_trial/README.md): Terraform dla Azure Databricks Trial z ADLS Gen2 i Unity Catalog |
| **Autor materiałów** | sekcja [Praca nad materiałami](#praca-nad-materiałami) |

## Plan dnia

| Godzina | Moduł | Notebook uczestnika |
|---|---|---|
| 09:00 | M0 · Start, setup, Canvas agenta | `workshop/00_setup/00_setup` |
| 09:45 | M1 · Agentic AI i AI Playground | `workshop/labs/m1_agentic_ai_playground` |
| 10:55 | M2 · Tool calling: funkcje Unity Catalog | `workshop/labs/m2_tool_calling` |
| 13:05 | M3 · RAG i AI Search | `workshop/labs/m3_rag_ai_search` |
| 14:40 | M4 · SQL, Genie Agent, kontrola dostępu | `workshop/labs/m4_sql_genie_governance` |
| 15:40 | M5 · Agent end-to-end | `workshop/labs/m5_end_to_end_agent` |
| 16:50 | M5+ · Przenieś wzorzec (capstone w parach) | `workshop/labs/m5b_transfer_capstone` |
| 17:30 | M6 · MCP, bezpieczeństwo, dalszy rozwój | `workshop/labs/m6_mcp_security_next_steps` |

Przerwy, prowadzący przy modułach i punkty kontrolne: [`workshop/docs/schedule.md`](workshop/docs/schedule.md).

## Struktura repozytorium

| Katalog | Zawartość |
|---|---|
| [`workshop/00_setup/`](workshop/00_setup) | setup uczestnika, przygotowanie i sprzątanie workspace'u prowadzącego |
| [`workshop/labs/`](workshop/labs) | **notebooki uczestnika** z zadaniami `TODO` (generowane z `demo/`) |
| [`workshop/demo/`](workshop/demo) | rozwiązania i dema prowadzących (źródło prawdy) |
| [`workshop/pattern/`](workshop/pattern) | dema wzorca: funkcje UC na Bakehouse, RAG na robotyce |
| [`workshop/transfer/`](workshop/transfer) | Canvas agenta: specyfikacja uzupełniana przez cały dzień |
| [`workshop/data/`](workshop/data) | dane syntetyczne i spseudonimizowane, raporty PDF, fragmenty z embeddingami, zbiór zapasowy |
| [`workshop/docs/`](workshop/docs) | przewodniki, harmonogram, koncepcja dnia, cheat sheet Free vs Premium, dziennik prób |
| [`workshop/scripts/`](workshop/scripts), [`workshop/tests/`](workshop/tests) | przygotowanie danych, generator labów, lint i testy |
| [`infra/azure_trial/`](infra/azure_trial) | Terraform i `smoke_test.py` dla workspace'u prowadzącego |
| `Docs/` | agenda i prezentacja |
| `Warsztaty_Mariusz/`, `Warsztaty_Krzysztof/` | archiwa materiałów źródłowych prowadzących |

## Stan materiałów (15.09.2026)

| Obszar | Stan |
|---|---|
| Notebooki z rozwiązaniami na workspace **Premium** (Azure trial, z folderu Git) | ✅ regresja 11/11, bez błędów w komórkach |
| Dane warsztatu | ✅ wygenerowane, zwalidowane, licencja przejrzana |
| Ścieżka uczestnika na **Free Edition** | ⏳ do przejścia na świeżym koncie |
| Deck | ⏳ do aktualizacji pod układ dnia z capstone |

Szczegóły, dowody i lista otwartych punktów: [`workshop/docs/rehearsal_log.md`](workshop/docs/rehearsal_log.md).

## Dane i licencje

- **TechRetail Corp:** pochodna zbioru *Simulated Retail Customer Data* (Databricks Marketplace, CC BY 4.0), spseudonimizowana; przypisanie autorstwa i lista zmian w [`workshop/data/NOTICE.md`](workshop/data/NOTICE.md), przegląd w [`LICENSE_REVIEW.md`](workshop/data/LICENSE_REVIEW.md).
- **Bakehouse:** katalog przykładów `samples.bakehouse`, dostępny w każdym workspace Databricks.
- **Airbnb San Francisco** (zbiór zapasowy): licencja MIT, `workshop/data/practice/`.
- Wszystkie dane są syntetyczne albo publiczne. Na Free Edition wgrywamy wyłącznie dane publiczne lub zanonimizowane.

## Praca nad materiałami

- `workshop/demo/` to **źródło prawdy**. `workshop/labs/` jest generowane: `python workshop/scripts/generate_labs.py`. Nie edytuj labów ręcznie.
- Komórka z `metadata.tags = ["solution"]` dostaje w labie treść `metadata.exercise_source`, a komórka `trainer_only` staje się notatką „Demo prowadzącego”.
- Każda komórka kanoniczna zaczyna się markerem `source:` (`WSx[i]`, `slide N`, `PRZ[i]`, `K:ścieżka`, `new`). Mapę generuje `python workshop/scripts/build_cell_mapping.py` → `workshop/docs/cell_mapping.md`.
- Notebooki nie podają minut: tempo ustalają prowadzący, a orientacyjny plan jest tylko w dokumentacji. Lint odrzuca `N min` i `**Czas:**` w notebookach.
- Notebooki mają przypięte środowisko serverless 5 (Python 3.12) w metadanych.
- Kontrola lokalna: `python workshop/scripts/check_notebooks.py` i `pytest -q workshop/tests`. Kontrola na workspace: `infra/azure_trial/smoke_test.py` i regresja opisana w dzienniku prób.
- Wszystko, czego nie da się sprawdzić lokalnie, trafia na listę w `workshop/docs/rehearsal_log.md` i jest potwierdzane na workspace.
