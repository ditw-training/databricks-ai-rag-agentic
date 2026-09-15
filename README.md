# SQLDay Lite: „Od pytania do agenta” (Databricks)

Materiały całodniowego warsztatu (09:00–18:00) o budowie prostego agenta AI na Databricks: AI Playground, tool calling na funkcjach Unity Catalog, RAG z AI Search, Genie Agent i kontrola dostępu, agent end-to-end oraz MCP.

| Katalog | Zawartość |
|---|---|
| [`workshop/`](workshop/README.md) | **warsztat**: setup, laby uczestnika, rozwiązania (`demo/`), dema wzorca Krzysztofa (`pattern/`), capstone i Canvas (`transfer/`), dane, dokumentacja, testy |
| [`infra/azure_trial/`](infra/azure_trial/README.md) | Terraform: workspace prowadzącego Azure Databricks Trial (Premium, 14 dni) + ADLS Gen2 i katalog Unity Catalog |
| `Docs/` | agenda i prezentacja |
| `Warsztaty_Mariusz/` | archiwum: notebooki źródłowe WS1–WS4 i Zadania (oś fabularna TechRetail) |
| `Warsztaty_Krzysztof/` | źródło dem wzorca (`rag_agent`, `single_agent_app`), testy na Free Edition (sprawozdanie), dalsza droga: ewaluacja i monitoring |

## Start

- **Uczestnik:** [`workshop/README.md`](workshop/README.md): prework, plan dnia, tryby awaryjne.
- **Prowadzący (Krzysztof i Mariusz):** [`workshop/docs/koncepcja_dnia.md`](workshop/docs/koncepcja_dnia.md), [`workshop/docs/trainer_guide.md`](workshop/docs/trainer_guide.md), potem `workshop/00_setup/01_trainer_prepare_premium`.

## Praca nad materiałami

- `workshop/demo/` to **źródło prawdy**. `workshop/labs/` jest generowane: `python workshop/scripts/generate_labs.py`. Nie edytuj labów ręcznie.
- Komórka z `metadata.tags = ["solution"]` dostaje w labie treść `metadata.exercise_source`, a komórka `trainer_only` staje się notatką „Demo prowadzącego”.
- Każda komórka kanoniczna zaczyna się markerem `source:` (`WSx[i]`, `slide N`, `PRZ[i]`, `K:ścieżka`, `new`). Mapę generuje `python workshop/scripts/build_cell_mapping.py` → `workshop/docs/cell_mapping.md`.
- Notebooki nie podają minut: tempo ustalają prowadzący, a orientacyjny plan jest tylko w `workshop/docs/schedule.md`. Lint odrzuca `N min` i `**Czas:**` w notebookach.
- Kontrola: `python workshop/scripts/check_notebooks.py` i `pytest -q workshop/tests`.
- Wszystko, czego nie da się sprawdzić lokalnie, trafia na listę w `workshop/docs/rehearsal_log.md` i jest potwierdzane na workspace.
