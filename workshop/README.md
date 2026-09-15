# Od pytania do agenta: warsztat Databricks (SQLDay Lite)

Budujesz asystenta AI dla fikcyjnej firmy **TechRetail Corp**: od rozmowy z modelem w AI Playground, przez narzędzia w Unity Catalog, RAG na raportach PDF i dane tabelaryczne w Genie, do agenta, który sam wybiera źródło odpowiedzi. Każdy mechanizm zobaczysz najpierw na **innych danych** (sieć piekarni Bakehouse, artykuły o robotyce), a na koniec dnia **przeniesiesz wzorzec na dane, które sam wybierzesz**.

Prowadzą **Krzysztof i Mariusz**.

## Prework (15 min, przed warsztatem)

1. **Konto Databricks Free Edition:** zarejestruj się na stronie Databricks Free Edition. Wystarczy konto Google, Microsoft albo e-mail.
2. **Import repozytorium jako folder Git:**
   1. W workspace kliknij **Workspace → Home → Create → Git folder**.
   2. Wklej adres repozytorium warsztatu i kliknij **Create Git folder**.
   3. Sprawdź, że widzisz katalog `workshop/` z podkatalogami `00_setup`, `labs`, `demo`, `pattern`, `transfer` i `data`.
3. **Test:** otwórz `workshop/00_setup/00_setup` i uruchom tylko pierwszą komórkę (`%pip install`). Jeśli skończy się bez błędu, jesteś gotowy.
4. **(Opcjonalnie) Twoje dane na koniec dnia:** jeden plik CSV (do kilku tysięcy wierszy), najlepiej z jedną kolumną tekstu (opinie, opisy, notatki). **Tylko dane publiczne albo zanonimizowane:** bez imion i nazwisk, e-maili, telefonów, adresów, numerów dokumentów i kart. Kto nie przyniesie danych, pracuje na gotowym zbiorze Bakehouse.

> Folder musi być **Git folderem**. Zwykły upload plików nie przeniesie danych z `workshop/data/`, a notebooki czytają je ścieżką względną.

## Jak pracujemy

Każdy moduł ma ten sam rytm:

```
problem z historii TechRetail → wzorzec na innych danych (prowadzący) → Ty: lab TechRetail na 3 poziomach → karta wzorca + wiersz w Canvasie
```

| Poziom | Dla kogo | Co robisz |
|---|---|---|
| **1. Ścieżka** | wszyscy | komórki z `ZADANIE` w `labs/` (szukaj `TODO`) |
| **2. Transfer** | kto skończy ścieżkę | komórki `POZIOM 2` na danych Bakehouse |
| **3. Twoje dane** | kto chce więcej | ten sam krok na własnych danych albo wyzwanie z tabeli „Poziomy 2 i 3” |

| Katalog | Co zawiera |
|---|---|
| `00_setup/00_setup` | tabela klientów, raporty PDF, fragmenty raportów, start AI Search, preflight |
| `labs/m1 … m6`, `labs/m5b` | **Twoje notebooki** |
| `demo/` | rozwiązania: zajrzyj, gdy utkniesz na dłużej niż 2 minuty |
| `pattern/` | dema wzorca prowadzącego (Bakehouse, robotyka) |
| `transfer/canvas_agenta.md` | jednostronicowa specyfikacja Twojego agenta, uzupełniana przez cały dzień |
| `docs/cheat_sheet_free_vs_premium.md` | co działa na Free Edition, nazwy zmienione w 2026, co zrobić, gdy coś nie działa |
| `data/` | dane syntetyczne i spseudonimizowane, gotowe fragmenty i embeddingi, zbiór zapasowy Airbnb |

**Zasady:** pracujesz w parze z sąsiadem. Błąd jest normalny, a nie porażką. Czerwona karteczka po 2 minutach utknięcia. Zawsze możesz skopiować rozwiązanie z `demo/`.

## Plan dnia

| Godzina | Moduł | Notebook |
|---|---|---|
| 09:00 | M0 · Otwarcie, setup, Canvas | `00_setup/00_setup` |
| 09:45 | M1 · Agentic AI i AI Playground | `labs/m1_agentic_ai_playground` |
| 10:55 | M2 · Tool calling: funkcje Unity Catalog | `labs/m2_tool_calling` |
| 13:05 | M3 · RAG i AI Search | `labs/m3_rag_ai_search` |
| 14:40 | M4 · SQL, Genie Agent, kontrola dostępu | `labs/m4_sql_genie_governance` |
| 15:40 | M5 · Agent end-to-end | `labs/m5_end_to_end_agent` |
| 16:50 | **M5+ · Przenieś wzorzec na swoje dane** (w parach) | `labs/m5b_transfer_capstone` |
| 17:30 | M6 · MCP, bezpieczeństwo, dalszy rozwój | `labs/m6_mcp_security_next_steps` |

Szczegóły i przerwy: `docs/schedule.md`.

**Cel dnia (karta wyjściowa):** macierz 3 tras Twojego agenta na danych innych niż TechRetail, z co najmniej dwiema trasami zgodnymi.

## Każdy notebook zaczyna się tak samo

1. `%pip install --quiet -r ../requirements.txt` (1–2 min, czytaj wstęp w tym czasie),
2. `dbutils.library.restartPython()`,
3. **komórka konfiguracji**: ta sama we wszystkich notebookach (nazwy tabel, endpointów, `SYSTEM_PROMPT`).

Po każdym restarcie Pythona uruchom ponownie komórkę konfiguracji i kolejne.

## Tryby awaryjne na Free Edition

| Flaga | Gdzie | Domyślnie | Co robi |
|---|---|---|---|
| `RUN_PARSE` | M3 | `False` | `False`: wczytuje sparsowane raporty z `data/checkpoints` zamiast `ai_parse_document` |
| `SEARCH_READY` | M3, M5, M6 | ustawiana automatycznie | `False`: wyszukiwanie w raportach liczone lokalnie (`retrieve_local`) na tych samych embeddingach |
| `DATA_OPTION` | M5+ | `"bakehouse"` | `"airbnb"`: zbiór zapasowy z `data/practice`; `"own"`: Twój CSV z Volume `my_data` |
| `USE_AI_SEARCH` | M5+ | `False` | `True`: indeks AI Search na Twoim tekście zamiast wyszukiwania po słowach kluczowych |
| `TRY_MCP` | M6 | `True` | `False`: pomija wywołania zarządzanych serwerów MCP |

## Po warsztacie

Usuń endpoint AI Search (**Compute → AI Search**), jeśli nie wracasz do labów w najbliższych dniach. Zużywa kwotę Free Edition także bez zapytań. Dalsza droga: tabela w M6 (archiwa `Warsztaty_Mariusz/` i `Warsztaty_Krzysztof/`).

---

*Dane: Databricks Marketplace „Simulated Retail Customer Data”, pochodna spseudonimizowana (`data/LICENSE_REVIEW.md`); `samples.bakehouse` (katalog przykładów Databricks); Airbnb San Francisco (licencja MIT, `data/practice`). Materiał źródłowy: `Warsztaty_Mariusz/` (WS1–WS4, fabuła) i `Warsztaty_Krzysztof/` (wzorce i testy na Free Edition).*
