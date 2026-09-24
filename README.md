# Od pytania do agenta: warsztat Databricks (SQLDay Lite)

Całodniowy warsztat (08:30–17:30), na którym budujesz agenta AI na Databricks: od rozmowy z modelem w AI Playground, przez narzędzia w Unity Catalog, RAG na raportach PDF i dane tabelaryczne w Genie, do agenta, który sam wybiera źródło odpowiedzi i jest dostępny przez MCP. Na koniec dnia przenosisz ten sam wzorzec na inne dane.

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
| M5+ | transfer wzorca | mini-agent na danych Bakehouse albo Airbnb |
| M6 | MCP i bezpieczeństwo | narzędzia przez zarządzane serwery MCP, warstwy obrony, least privilege |

**Cel dnia:** agent na danych innych niż TechRetail i jego macierz 3 tras, z co najmniej dwiema trasami zgodnymi.

## Dla kogo

Od początkujących do zaawansowanych. Każdy lab ma trzy poziomy: **ścieżkę** z podpowiedziami, **transfer** na drugą domenę i **wyzwanie** dla tych, którzy skończą wcześniej. Przydaje się podstawowa znajomość SQL i Pythona. Nie jest potrzebne doświadczenie z Databricks ani z LLM.

**Wymagania:** laptop z przeglądarką i konto **Databricks Free Edition**. Nic więcej — wszystkie dane są w repozytorium.

## Jak zacząć

| Kim jesteś | Zacznij tu |
|---|---|
| **Uczestnik** | [Przewodnik uczestnika z osią czasu](documents/scripts/przewodnik_uczestnika.md), potem [`workshop/README.md`](workshop/README.md) |
| **Prowadzący** | [Podręcznik prowadzącego](documents/prowadzacy/Podrecznik_prowadzacego.pdf) — jedyny dokument na dzień warsztatu → [harmonogram](documents/scripts/schedule.md) → `workshop/00_setup/01_trainer_prepare_premium` |
| **Workspace prowadzącego (Azure)** | `infra/azure_trial/` (lokalnie, poza repozytorium): Terraform dla Azure Databricks Trial z ADLS Gen2 i Unity Catalog |
| **Autor materiałów** | sekcja [Praca nad materiałami](#praca-nad-materiałami) |

## Plan dnia

| Godzina | Moduł | Notebook uczestnika |
|---|---|---|
| 08:30 | M0 · Start, setup, Canvas agenta | `workshop/00_setup/00_setup` |
| 09:15 | M1 · Agentic AI i AI Playground | `workshop/labs/m1_agentic_ai_playground` |
| 10:25 | M2 · Tool calling: funkcje Unity Catalog | `workshop/labs/m2_tool_calling` |
| 12:35 | M3 · RAG i AI Search | `workshop/labs/m3_rag_ai_search` |
| 14:10 | M4 · SQL, Genie Agent, kontrola dostępu | `workshop/labs/m4_sql_genie_governance` |
| 15:10 | M5 · Agent end-to-end | `workshop/labs/m5_end_to_end_agent` |
| 16:15 | M5+ · Przenieś wzorzec (capstone w parach) | `workshop/labs/m5b_transfer_capstone` |
| 16:55 | M6 · MCP, bezpieczeństwo, dalszy rozwój | `workshop/labs/m6_mcp_security_next_steps` |

Przerwy, prowadzący przy modułach i punkty kontrolne: [`documents/scripts/schedule.md`](documents/scripts/schedule.md).

## Struktura repozytorium

| Katalog | Zawartość |
|---|---|
| [`workshop/00_setup/`](workshop/00_setup) | setup uczestnika, przygotowanie i sprzątanie workspace'u prowadzącego |
| [`workshop/labs/`](workshop/labs) | **notebooki uczestnika** z zadaniami `TODO` (generowane z `demo/`) |
| [`workshop/demo/`](workshop/demo) | rozwiązania i dema prowadzących (źródło prawdy) |
| [`workshop/pattern/`](workshop/pattern) | dema wzorca: funkcje UC na Bakehouse, RAG na robotyce |
| [`workshop/transfer/`](workshop/transfer) | Canvas agenta: specyfikacja uzupełniana przez cały dzień |
| [`workshop/data/`](workshop/data) | dane syntetyczne i spseudonimizowane, raporty PDF, fragmenty z embeddingami, zbiór zapasowy |
| [`workshop/scripts/`](workshop/scripts) | `generate_labs.py` (laby z `demo/`) i `check_notebooks.py` (lint notebooków) |
| [`workshop/tests/`](workshop/tests) | testy statyczne materiału: lint, parzystość demo–laby, spójność wspólnej konfiguracji |
| [`documents/scripts/`](documents/scripts) | źródła .md: przewodniki, harmonogram, podręczniki, cheat sheet Free vs Premium, dziennik prób |
| [`documents/uczestnik/`](documents/uczestnik) | materiały wydawane sali: podręcznik uczestnika (PDF) i agenda |
| [`documents/prowadzacy/`](documents/prowadzacy) | materiały wyłącznie dla prowadzących: podręcznik z narracją, recenzje agendy, analizy |
| [`documents/screens/`](documents/screens) · [`documents/assets/`](documents/assets) | zrzuty z workspace i grafiki slajdów |
| [`documents/brand/`](documents/brand) | pipeline PDF w identyfikacji SQLDay Lite: `build_pdf.py`, arkusz druku, logo |
| `documents/filmy/` (tylko lokalnie, poza gitem) | nagrania z warsztatu (~76 MB), trafiają na Dysk |
| `infra/` (tylko lokalnie, poza gitem) | Terraform i `smoke_test.py` dla workspace'u prowadzącego — zawiera identyfikatory subskrypcji |
| `.archive/` (tylko lokalnie, poza gitem) | poprzednia wersja `workshop/` z `scripts/` i `tests/`, stare `infra/azure_trial` i `Docs/`, materiały źródłowe `Warsztaty_Mariusz/` i `Warsztaty_Krzysztof/` |

## Stan materiałów (23.09.2026)

| Obszar | Stan |
|---|---|
| Notebooki na workspace **Premium** (Azure trial, z folderu Git) | ✅ M5, M3 i M5+ przejechane jako joby 23.09: M5 trasy 5/6, capstone 4/4 |
| Notebooki na **Free Edition** | ✅ te same trzy przejechane 23.09: M5 trasy 5/6, capstone 3/4 |
| Framework agenta | ✅ `create_agent` (LangChain 1.x) w M5, M5+, `retail_agent.py` i supervisorze; `AgentExecutor` wycofany, lint go blokuje |
| Dane warsztatu | ✅ wygenerowane, zwalidowane, licencja przejrzana |
| Deck | ✅ 106 slajdów, aneks z dokumentacją best practices |
| `predict_stream()` w `retail_agent.py` | ⏳ napisane, **nieuruchomione** — żaden notebook go nie woła, sprawdzi się dopiero w czacie Apps albo Playground |
| Przejście ścieżki uczestnika przez człowieka | ⏳ joby sprawdzają, że kod nie pada; nie sprawdzają, czy lab da się przejść |

Trasy 5/6 to wynik oczekiwany: na Llamie 3.3 trasa `r3_both` nie wychodzi, bo model wykonuje jedno narzędzie na turę. Szczegóły, dowody i lista otwartych punktów: [`documents/scripts/rehearsal_log.md`](documents/scripts/rehearsal_log.md).

## Dane i licencje

- **TechRetail Corp:** pochodna zbioru *Simulated Retail Customer Data* (Databricks Marketplace), licencja [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Zmiany wobec źródła: agregacja RFM do `gold_customer_360`, pseudonimizacja `customer_name` i `tax_id`, zaokrąglone `lat` i `lon`, wygenerowane raporty PDF wraz z ich fragmentami i embeddingami.
- **Bakehouse:** katalog przykładów `samples.bakehouse`, dostępny w każdym workspace Databricks.
- **Airbnb San Francisco** (zbiór zapasowy): [Inside Airbnb](https://insideairbnb.com/), licencja [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), `workshop/data/practice/`. Zmiany wobec źródła: usunięte kolumny `host_name`, `latitude` i `longitude`.
- Wszystkie dane są syntetyczne albo publiczne. Na Free Edition wgrywamy wyłącznie dane publiczne lub zanonimizowane.

## Praca nad materiałami

- Od 19.09.2026 główną wersją jest „Warsztaty nowa wersja” (commit `b8902af` w repo `kannulkaa/Warsztaty-Databricks`): bez opcji własnych danych uczestnika; najtrudniejsza ścieżka w labach to „C · Wyzwanie”. Poprzednia wersja i narzędzia są w `.archive/`.
- `workshop/demo/` to **źródło prawdy**; `workshop/labs/` jest **generowane** i nie edytuje się go ręcznie. Po zmianie w demo uruchom w tej kolejności:
  ```bash
  python3 workshop/scripts/generate_labs.py     # przepisz laby z demo
  python3 workshop/scripts/check_notebooks.py   # lint: ma wypisać "0 finding(s)"
  .venv/bin/python -m pytest workshop/tests -q  # testy statyczne materiału
  ```
- Komórka z `metadata.tags = ["solution"]` dostaje w labie treść `metadata.exercise_source`, a komórka `trainer_only` staje się notatką „Demo prowadzącego”.
- Każda komórka kanoniczna ma w metadanych pole `source_ref` z pochodzeniem (`WSx[i]`, `slide N`, `PRZ[i]`, `K:ścieżka`, `new`). Nie ma go w treści komórki, więc uczestnik go nie widzi. Mapa komórek (`cell_mapping.md`) jest w archiwum prowadzących, poza repozytorium.
- Notebooki nie podają minut: tempo ustalają prowadzący, a orientacyjny plan jest tylko w dokumentacji.
- Notebooki mają przypięte środowisko serverless **6** (Databricks Connect 19.1, Python 3.12) w metadanych.
- Kontrola na workspace: `infra/azure_trial/smoke_test.py` (lokalnie) i regresja opisana w dzienniku prób.
- Wszystko, czego nie da się sprawdzić lokalnie, trafia na listę w `documents/scripts/rehearsal_log.md` i jest potwierdzane na workspace.
