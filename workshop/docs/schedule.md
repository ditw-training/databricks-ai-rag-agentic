# Harmonogram dnia: „Od pytania do agenta”

09:00–18:00 · **430 min materiału** · 110 min przerw · prowadzą **Krzysztof i Mariusz** · stan na 2026-09-14

Rytm każdego modułu: **problem z historii → wzorzec na innej domenie → zrób z nami (TechRetail, poziomy 1–3) → karta wzorca**. Koncepcja: `docs/koncepcja_dnia.md`.

| Godzina | Blok | Min | Prowadzi | Prezentacja / demo / lab | Demo wzorca | Notebook uczestnika |
|---|---|---|---|---|---|---|
| 09:00 | **M0** Otwarcie, fabuła, setup, Canvas | 45 | Mariusz; Krzysztof: setup | 20 / 5 / 20 | — | `00_setup/00_setup` + `transfer/canvas_agenta.md` |
| 09:45 | **M1** Agentic AI i AI Playground | 55 | duet: Mariusz (VP of Sales) + Krzysztof (Playground) | 10 / 10 / 35 | ten sam prompt na Bakehouse (UI) | `labs/m1_agentic_ai_playground` |
| 10:40 | przerwa | 15 | | | | |
| 10:55 | **M2** Tool calling, funkcje UC | 70 | Krzysztof | 10 / 10 / 50 | `pattern/p2_uc_functions_bakehouse` | `labs/m2_tool_calling` |
| 12:05 | lunch | 60 | obaj sprawdzają endpointy AI Search uczestników | | | |
| 13:05 | **M3** RAG i AI Search | 80 | Krzysztof | 10 / 15 / 55 | `pattern/p3_rag_robotics` | `labs/m3_rag_ai_search` |
| 14:25 | przerwa | 15 | | | | |
| 14:40 | **M4** SQL, Genie Agent, kontrola dostępu | 50 | Mariusz | 10 / 10 / 30 | Genie i maska na TechRetail | `labs/m4_sql_genie_governance` |
| 15:30 | przerwa | 10 | | | | |
| 15:40 | **M5** Agent end-to-end | 60 | duet: Mariusz (CTO) + Krzysztof (trace, Apps) | 10 / 10+5 / 35 | finał historii TechRetail | `labs/m5_end_to_end_agent` |
| 16:40 | przerwa | 10 | | | | |
| 16:50 | **M5+** Przenieś wzorzec (capstone, w parach) | 40 | obaj po sali | 0 / 0 / 40 | — | `labs/m5b_transfer_capstone` |
| 17:30 | **M6** MCP, bezpieczeństwo, zamknięcie | 30 | Krzysztof (MCP, „zbuduj i złam”); Mariusz (zamknięcie) | 15 / 10 / 5 | funkcje z capstone jako narzędzia MCP | `labs/m6_mcp_security_next_steps` |
| 18:00 | koniec | | | | | |

**Suma materiału:** 45 + 55 + 70 + 80 + 50 + 60 + 40 + 30 = **430 min**. **Przerwy:** 15 + 60 + 15 + 10 + 10 = **110 min**.

## Punkty kontrolne (dla prowadzącego chodzącego po sali)

| Godzina | Każdy uczestnik ma | Kto nie ma |
|---|---|---|
| 09:40 | ✅ w preflight `00_setup`, Canvas z domeną i 5 pytaniami | para z sąsiadem, prowadzący pomaga przy setupie |
| 12:00 | 3 funkcje UC i test payloadem | kopiuje komórki z `demo/m2`, idzie dalej |
| 14:20 | `custom_rag` z cytatami (AI Search albo tryb offline) | kopiuje `m3-custom-rag` z `demo/` |
| 15:25 | **zdjęty** filtr i maska (`m4-cleanup` ✅) | obowiązkowo, zanim zacznie M5 |
| 16:35 | macierz tras w M5 (dowolny wynik) | kopiuje `m5-build-agent` z `demo/` |
| 17:25 | karta wyjściowa: macierz 3 tras na nowych danych | wychodzi z Bakehouse z `demo/m5b` i jedną własną zmianą |

## Zależności między modułami

```
00_setup ──► M1 (m1_baseline_answers) ───────────────────────────────────────────► M5 (porównanie, opcja)
   ├─► M2 (3 funkcje UC) ─────────────────────────────► M5 (agent) ─► M6 (serwer MCP funkcji)
   ├─► M3 (indeks AI Search) ─────────────────────────► M5 (search_retail_reports)
   ├─► M4 (Genie Agent; filtr i maska ZDJĘTE) ─────────► M5 (28 813 wierszy)
   └─► samples.bakehouse ─► poziomy 2 w M1–M4 ─► M5+ capstone (capstone_*) ─► M6 (te funkcje przez MCP)
```

## Gdzie odzyskać czas

| Opóźnienie | Co pominąć bez utraty ciągłości | Zysk |
|---|---|---|
| M0: wolny start Serverless | komórki `optional` (`ai_query`, Time Travel) | 3 min |
| M1 | ablacja w kodzie (`optional`), bonus drugiego modelu | 5 min |
| M2 | tool calling „ręcznie” (`optional`, poziom 2) | 10 min |
| M3: endpoint nie jest `ONLINE` | parsowanie, embedding, reranker (`optional`); Playground po przerwie | 10 min |
| M4 | SDK Genie (`optional`), Genie jako Tool w Playground | 7 min |
| M5 | sędzia LLM i porównanie z M1 (`optional`) | 8 min |
| M5+ | pokaz tylko 2 par zamiast 3 | 3 min |

> Deck (`Docs/Od pytania do agenta - SQLDay Lite.pptx`) ma jeszcze układ z jednym prowadzącym i bez capstone: slajd 2 (plan dnia), slajdy H1–H6 i slajd 10 (Zadania). Wymaga aktualizacji.
