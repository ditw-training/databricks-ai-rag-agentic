# Od pytania do agenta: warsztat Databricks (SQLDay Lite)

Budujesz asystenta AI dla fikcyjnej firmy **TechRetail Corp**: od rozmowy z modelem w AI Playground, przez narzędzia w Unity Catalog, RAG na raportach PDF i dane tabelaryczne w Genie, do agenta, który sam wybiera źródło odpowiedzi. Każdy mechanizm robisz najpierw razem z prowadzącym na TechRetail, potem możesz go powtórzyć sam na danych sieci piekarni Bakehouse albo wziąć trudniejsze wyzwanie. Na koniec dnia **przeniesiesz cały wzorzec na nowe dane** — sieć piekarni albo oferty Airbnb — w parach.

Prowadzą **Krzysztof i Mariusz**.

> **Pierwszy raz tutaj?** Zacznij od [przewodnika uczestnika z osią czasu](../documents/scripts/przewodnik_uczestnika.md): co przygotować przed warsztatem, co robisz w każdym module i co masz na koniec.

## Prework (15 min, przed warsztatem)

1. **Konto Databricks Free Edition:** zarejestruj się na stronie Databricks Free Edition. Wystarczy konto Google, Microsoft albo e-mail.
2. **Import repozytorium jako folder Git:**
   1. W workspace kliknij **Workspace → Home → Create → Git folder**.
   2. Wklej adres `https://github.com/ditw-training/databricks-ai-rag-agentic.git` i kliknij **Create Git folder**.
   3. Sprawdź, że widzisz katalog `workshop/` z podkatalogami `00_setup`, `labs`, `demo`, `pattern`, `transfer` i `data`.
3. **Test:** otwórz `workshop/00_setup/00_setup` i uruchom tylko pierwszą komórkę (`%pip install`). Jeśli skończy się bez błędu, jesteś gotowy. Cały notebook (**Run all**) uruchamiasz raz, na sali o 08:30, razem z prowadzącym.

> Folder musi być **Git folderem**. Zwykły upload plików nie przeniesie danych z `workshop/data/`, a notebooki czytają je ścieżką względną.

## Jak pracujemy

Każdy moduł ma ten sam rytm:

```
prezentacja → A · Razem (TechRetail, z prowadzącym) → praca własna: B albo C → karta wzorca + wiersz w Canvasie
```

| Ścieżka | Co robisz | Gdzie w labie |
|---|---|---|
| **A · Razem** | TechRetail razem z prowadzącym; komórki z `ZADANIE` (szukaj `TODO`) | numerowane części notebooka |
| **B · Samodzielnie** | ten sam wzorzec na danych sieci piekarni Bakehouse (`workspace.bakehouse`), już bez prowadzącego | sekcja „B · Samodzielnie: …” |
| **C · Wyzwanie** | trudniejsza wersja problemu; w M2 i M4 na ofertach Airbnb (`workspace.airbnb`) | sekcja „C · Wyzwanie: …” |

Ścieżka A to pełny cel modułu. W czasie pracy własnej kończysz A we własnym tempie albo wybierasz B lub C. Mapa ścieżek na początku każdego notebooka mówi, po czym poznasz, że skończyłeś.

| Katalog | Co zawiera |
|---|---|
| `00_setup/00_setup` | tabela klientów, raporty PDF, fragmenty raportów, dane ścieżek B i C (schematy `bakehouse`, `airbnb`, `governance`), start AI Search, preflight |
| `labs/m1 … m6`, `labs/m5b` | **Twoje notebooki** |
| `demo/` | rozwiązania wszystkich trzech ścieżek: zajrzyj, gdy utkniesz na dłużej niż 2 minuty |
| `pattern/` | przykłady referencyjne na innych danych (funkcje UC na Bakehouse, RAG na robotyce); na sali nie uruchamiamy ich na żywo |
| `transfer/canvas_agenta.md` | jednostronicowa specyfikacja Twojego agenta, uzupełniana przez cały dzień |
| `../documents/scripts/sciaga_pojec.md` | **Kompendium uczestnika**: teoria z diagramami, podsumowanie modułów i ściąga decyzji. [Wersja PDF](../documents/uczestnik/Kompendium_uczestnika.pdf) |
| `../documents/scripts/dokumentacja_i_linki.md` | odsyłacze do oficjalnej dokumentacji, ułożone modułami — dokąd pójść po warsztacie |
| `../documents/scripts/cheat_sheet_free_vs_premium.md` | co działa na Free Edition, nazwy zmienione w 2026, co zrobić, gdy coś nie działa |
| `data/` | dane syntetyczne i spseudonimizowane, gotowe fragmenty i embeddingi, zbiór zapasowy Airbnb |

**Zasady:** pracujesz w parze z sąsiadem. Błąd jest normalny, a nie porażką. Czerwona karteczka po 2 minutach utknięcia. Zawsze możesz skopiować rozwiązanie z `demo/`.

## Plan dnia

| Godzina | Moduł | Notebook |
|---|---|---|
| 08:30 | M0 · Otwarcie, setup, Canvas | `00_setup/00_setup` |
| 09:15 | M1 · Agentic AI i AI Playground | `labs/m1_agentic_ai_playground` |
| 10:25 | M2 · Tool calling: funkcje Unity Catalog | `labs/m2_tool_calling` |
| 12:35 | M3 · RAG i AI Search | `labs/m3_rag_ai_search` |
| 14:10 | M4 · SQL, Genie Agent, kontrola dostępu | `labs/m4_sql_genie_governance` |
| 15:10 | M5 · Agent end-to-end | `labs/m5_end_to_end_agent` |
| 16:15 | **M5+ · Przenieś wzorzec na nowe dane** (w parach) | `labs/m5b_transfer_capstone` |
| 16:55 | M6 · MCP, bezpieczeństwo, dalszy rozwój | `labs/m6_mcp_security_next_steps` |

Szczegóły i przerwy: `../documents/scripts/schedule.md`.

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
| `DATA_OPTION` | M5+ | `"bakehouse"` | `"airbnb"`: oferty z `workspace.airbnb.listings` (C · Wyzwanie, gdy agent piekarni już działa, albo gdy brak `samples.bakehouse`) |
| `USE_AI_SEARCH` | M5+ | `False` | `True`: indeks AI Search na Twoim tekście zamiast wyszukiwania po słowach kluczowych |
| `TRY_MCP` | M6 | `True` | `False`: pomija wywołania zarządzanych serwerów MCP |

## Po warsztacie

Usuń endpoint AI Search (**Compute → AI Search**), jeśli nie wracasz do labów w najbliższych dniach. Zużywa kwotę Free Edition także bez zapytań. Dalsza droga: tabela w M6 (materiały źródłowe prowadzących — poproś prowadzącego, nie ma ich w tym repozytorium).

---

*Dane. **TechRetail**: pochodna zbioru „Simulated Retail Customer Data” (Databricks Marketplace), licencja [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); zmiany wobec źródła to agregacja RFM, pseudonimizacja nazw i identyfikatorów podatkowych oraz zaokrąglenie współrzędnych. **Bakehouse**: `samples.bakehouse`, katalog przykładów Databricks. **Airbnb San Francisco**: [Inside Airbnb](https://insideairbnb.com/), licencja [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); usunięto kolumny `host_name`, `latitude` i `longitude`. Dane są syntetyczne albo publiczne i nie opisują prawdziwych osób. Materiał źródłowy warsztatu jest poza repozytorium, w lokalnym archiwum prowadzącego.*
