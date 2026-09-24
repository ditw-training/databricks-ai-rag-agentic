# Od pytania do agenta: warsztat Databricks (SQLDay Lite)

Całodniowy warsztat, na którym budujesz agenta AI na Databricks: od rozmowy z modelem w AI Playground, przez narzędzia w Unity Catalog, RAG na raportach PDF i dane tabelaryczne w Genie, aż po agenta, który sam wybiera źródło odpowiedzi i jest dostępny przez MCP. Na koniec przenosisz ten sam wzorzec na inne dane.

Prowadzą **Krzysztof Burejza** i **Mariusz Wiecha**. Materiał jest po polsku, a kod, nazwy plików i obiektów po angielsku.

## Zanim przyjdziesz (15 minut)

1. **Załóż konto Databricks Free Edition.** Wystarczy konto Google, Microsoft albo adres e-mail.
2. **Zaimportuj to repozytorium jako folder Git:** w workspace **Workspace → Home → Create → Git folder**, wklej adres tego repozytorium i kliknij **Create Git folder**.
3. **Sprawdź, że widzisz** katalog `workshop/` z podkatalogami `00_setup`, `labs`, `demo`, `pattern`, `transfer` i `data`.
4. **Zrób test:** otwórz `workshop/00_setup/00_setup` i uruchom samą pierwszą komórkę (`%pip install`). Kończy się bez błędu? Jesteś gotowy.

> Musi to być **folder Git**, nie zwykły import plików. Przy imporcie nie przeniosą się dane z `workshop/data/`, a notebooki czytają je ścieżką względną i przerwą pracę.

Całego notebooka setup (**Run all**) uruchamiasz dopiero na sali, razem z prowadzącym.

Szczegóły przygotowań znajdziesz w [Przed_warsztatem.pdf](documents/uczestnik/Przed_warsztatem.pdf).

## Co zbudujesz

| Moduł | Umiejętność | Efekt |
|---|---|---|
| M0 | przygotowanie danych | tabela klientów, raporty PDF, fragmenty, endpoint AI Search |
| M1 | system prompt, ocena odpowiedzi | punkt odniesienia: co potrafi sam model i gdzie zmyśla |
| M2 | tool calling | trzy funkcje Unity Catalog jako narzędzia agenta, test payloadem |
| M3 | RAG | parsowanie PDF, chunking, embeddingi, AI Search, odpowiedzi z cytatami |
| M4 | dane tabelaryczne i dostęp | Genie Agent, row filter, maska kolumny |
| M5 | agent end-to-end | agent z czterema narzędziami, macierz tras, trace w MLflow |
| M5+ | transfer wzorca | mini-agent na danych Bakehouse albo Airbnb, w parach |
| M6 | MCP i bezpieczeństwo | narzędzia przez zarządzane serwery MCP, warstwy obrony, least privilege |

**Cel dnia:** agent na danych innych niż TechRetail i jego macierz trzech tras, z co najmniej dwiema trasami zgodnymi.

## Dla kogo

Od początkujących do zaawansowanych. Każdy moduł ma trzy poziomy: **ścieżkę A** przechodzisz razem z prowadzącym, **ścieżkę B** robisz samodzielnie na innych danych, a **ścieżka C** czeka na tych, którzy skończą wcześniej.

Przyda się podstawowa znajomość SQL i Pythona. Doświadczenie z Databricks ani z modelami językowymi nie jest potrzebne.

**Czego potrzebujesz:** laptopa z przeglądarką i konta Databricks Free Edition. Wszystkie dane są w tym repozytorium.

## Jak się tu poruszać

| Chcesz | Idź do |
|---|---|
| zacząć pracę | [`workshop/README.md`](workshop/README.md) — jak pracujemy, ścieżki, rytm modułu |
| notebooki z zadaniami | [`workshop/labs/`](workshop/labs) — tu pracujesz przez cały dzień |
| zajrzeć do rozwiązania | [`workshop/demo/`](workshop/demo) — pełne wersje pokazywane przez prowadzącego |
| przeczytać wcześniej | [Podrecznik_uczestnika.pdf](documents/uczestnik/Podrecznik_uczestnika.pdf) |

## Materiały do czytania

Wszystkie w [`documents/uczestnik/`](documents/uczestnik):

| Plik | Co zawiera |
|---|---|
| `Przed_warsztatem.pdf` | przygotowanie konta i importu, lista kontrolna |
| `Podrecznik_uczestnika.pdf` | przewodnik po dniu, moduł po module |
| `Kompendium_uczestnika.pdf` | szersze omówienie pojęć: agenty, RAG, MCP, ocena jakości |
| `Dodatki_uczestnika.pdf` | materiały uzupełniające i ćwiczenia dodatkowe |
| `Dokumentacja_i_linki.pdf` | odnośniki do dokumentacji Databricks i źródeł |

## Struktura repozytorium

| Katalog | Zawartość |
|---|---|
| [`workshop/00_setup/`](workshop/00_setup) | notebook przygotowujący dane w Twoim workspace |
| [`workshop/labs/`](workshop/labs) | **notebooki z zadaniami** — tu pracujesz |
| [`workshop/demo/`](workshop/demo) | pełne wersje z rozwiązaniami |
| [`workshop/pattern/`](workshop/pattern) | karty wzorca: funkcje Unity Catalog na Bakehouse, RAG na robotyce |
| [`workshop/transfer/`](workshop/transfer) | Canvas agenta, uzupełniany przez cały dzień |
| [`workshop/data/`](workshop/data) | dane warsztatu: tabele, raporty PDF, fragmenty z embeddingami |
| [`documents/uczestnik/`](documents/uczestnik) | podręczniki w PDF |

## Dane i licencje

- **TechRetail Corp** — pochodna zbioru *Simulated Retail Customer Data* z Databricks Marketplace, licencja [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Zmiany wobec źródła: agregacja RFM do `gold_customer_360`, pseudonimizacja nazwy klienta i numeru podatkowego, zaokrąglone współrzędne, wygenerowane raporty PDF wraz z fragmentami i embeddingami.
- **Bakehouse** — katalog przykładów `samples.bakehouse`, dostępny w każdym workspace Databricks.
- **Airbnb San Francisco** — [Inside Airbnb](https://insideairbnb.com/), licencja [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Zmiany wobec źródła: usunięte kolumny z nazwą gospodarza i dokładnymi współrzędnymi.

Wszystkie dane są syntetyczne albo publiczne. Na Free Edition wgrywamy wyłącznie dane publiczne lub zanonimizowane.
