# 01_parsing — dokładna instrukcja dla Databricks Free Edition

Ten moduł ma być wykonany w tej kolejności:

1. **Catalog** — tworzenie miejsca na pliki.
2. **Upload** — wgranie 10 PDF-ów.
3. **Workspace** — import dwóch notebooków.
4. **Notebook** — dopiero tutaj wybór Serverless i uruchomienie komórek.

Nie twórz klastra ani compute w osobnej stronie **Compute**. W Databricks Free Edition korzystasz z Serverless wybieranego wewnątrz otwartego notebooka.

## Co przygotować lokalnie

Otwórz katalog `01_parsing` na swoim komputerze. Do Databricks będą potrzebne tylko:

- wszystkie 10 plików z `documents/`,
- `notebooks/01_parse_robotics_documents.py`,
- `notebooks/includes/document_renderer.py`.

Nie wgrywaj plików z `assets/` ani `scripts/` do Databricks — służą tylko do lokalnego odtworzenia materiałów.

## Krok 1 — wejdź do workspace

1. Zaloguj się do [Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition).
2. Po otwarciu workspace spójrz na lewy pasek nawigacji.
3. Kliknij **Catalog**. Otworzy się Catalog Explorer.

## Krok 2 — utwórz Volume na PDF-y

Volume to katalog na pliki. Nie jest to tabela i nie wymaga tworzenia compute.

1. W Catalog Explorer rozwiń katalog `workspace`.
2. Wybierz schema `default`.
3. Po otwarciu strony schema kliknij w prawym górnym rogu **Create** > **Volume**.
4. W polu **Name** wpisz `robotics_files`.
5. Wybierz **Managed volume**. Nie wybieraj External volume.
6. Kliknij **Create**.
7. Otworzy się strona nowego Volume. Jej pełna ścieżka ma być dokładnie:

   ```text
   /Volumes/workspace/default/robotics_files
   ```

Jeśli nie widzisz `workspace.default` albo przycisk **Create > Volume** jest niedostępny, przerwij konfigurację i sprawdź, czy jesteś we właściwym workspace kursowym lub masz uprawnienie `CREATE VOLUME`.

## Krok 3 — wgraj PDF-y do Volume

Nadal będąc na stronie `robotics_files` w Catalog Explorer:

1. Kliknij **Upload to this volume**.
2. W oknie **Upload files**, w sekcji **Files**, kliknij **browse**.
3. Przejdź do lokalnego katalogu `01_parsing/documents/`.
4. Zaznacz wszystkie 10 plików PDF i zatwierdź wybór.
5. W sekcji **Destination volume** upewnij się, że wybrany jest `robotics_files`.
6. Kliknij **Upload**.
7. Poczekaj, aż na stronie Volume pojawi się 10 plików `.pdf`. Kliknij jeden plik, aby sprawdzić, czy otwiera się podgląd.

Wgrywaj PDF-y bezpośrednio do głównego katalogu Volume — nie twórz folderu `documents`.

## Krok 4 — utwórz foldery w Workspace i zaimportuj notebooki

1. Kliknij w lewym pasku **Workspace**.
2. Otwórz swój folder użytkownika (zwykle **Users** > Twój adres e-mail).
3. Kliknij **Create** > **Folder**, wpisz `robotics_parsing` i kliknij **Create**.
4. Wejdź do `robotics_parsing`, kliknij **Create** > **Folder**, wpisz `includes` i kliknij **Create**.
5. Wejdź do folderu `includes`. Kliknij menu z trzema kropkami (**⋮**) dla bieżącego folderu i wybierz **Import**.
6. Kliknij **browse**, wybierz lokalny plik `01_parsing/notebooks/includes/document_renderer.py`, a następnie kliknij **Import**.
7. Wróć o poziom wyżej do `robotics_parsing`. Ponownie wybierz **⋮** > **Import**.
8. Wybierz lokalny plik `01_parsing/notebooks/01_parse_robotics_documents.py` i kliknij **Import**.

Końcowy układ w Workspace ma wyglądać tak:

```text
Users / <Twój użytkownik> / robotics_parsing /
├── 01_parse_robotics_documents
└── includes /
    └── document_renderer
```

Ten układ jest konieczny, ponieważ główny notebook uruchamia renderer przez `%run ./includes/document_renderer`.

## Krok 5 — otwórz notebook i wybierz Serverless

1. W Workspace kliknij `01_parse_robotics_documents`.
2. W prawym górnym rogu edytora notebooka kliknij listę **Connect** lub listę compute (jej nazwa może zależeć od szerokości okna).
3. Wybierz **Serverless**.
4. Nie konfiguruj żadnych dodatkowych parametrów klastra. W Free Edition Serverless uruchamia się automatycznie przy pierwszej komórce z kodem.

## Krok 6 — uruchom stałą konfigurację notebooka

Nie ma widgetów ani pól do uzupełniania. W notebooku są już na stałe wpisane poniższe wartości:

| Zmienna | Wartość |
| --- | --- |
| `source_documents_path` | `/Volumes/workspace/default/robotics_files` |
| `python_rendered_pages_path` | `/Volumes/workspace/default/robotics_files/parsed_pages/python` |
| `sql_rendered_pages_path` | `/Volumes/workspace/default/robotics_files/parsed_pages/sql` |
| `parsed_delta_table` | `workspace.default.robotics_parsed_documents` |

Uruchom komórkę **0. Configuration** (ikona ▶ po lewej stronie komórki). Powinna tylko wypisać te cztery wartości.

## Krok 7 — uruchom ćwiczenie

Uruchamiaj następne komórki **po kolei**, pojedynczo:

1. **Renderer helper** — ładuje lokalną funkcję `render_ai_parse_output`.
2. **1. Parse documents with Python** — czeka na wynik. Powinieneś zobaczyć 10 wierszy z nazwami plików.
3. **2. Parse documents with SQL** — ponownie parsuje te same pliki, ale przez SQL. Powinieneś zobaczyć 10 wierszy.
4. **3. Save parsed output to a Delta table** — tworzy automatycznie tabelę Delta `workspace.default.robotics_parsed_documents` przy pierwszym uruchomieniu i zapisuje do niej wyłącznie 10 wyników parsera Python. Ponowne uruchomienie tej komórki nadpisuje wyłącznie tę tabelę świeżym wynikiem.
5. **4. Display parsed-document metadata** — pokazuje 20 wierszy: 10 z parsera Python i 10 z parsera SQL. Dla każdego PDF `page_count` powinno wynosić `3`.
6. **5. Visualize one Python-parsed document** — pokazuje strony pierwszego PDF-a; kolorowe ramki oznaczają elementy rozpoznane przez parser. Najedź kursorem na ramkę, aby zobaczyć jej typ i treść, albo rozwiń wpis pod stroną.

Nie twórz ręcznie żadnej Delta table w Catalog Explorer. Notebook `01` utworzy `workspace.default.robotics_parsed_documents`, a notebook `02` utworzy `workspace.default.robotics_document_chunks` przy pierwszym uruchomieniu swoich ostatnich komórek zapisu. Musisz jedynie mieć uprawnienia `USE CATALOG`, `USE SCHEMA` i `CREATE TABLE` w `workspace.default`.

Po udanym uruchomieniu w Catalog Explorer, w `robotics_files`, pojawi się katalog `parsed_pages` z obrazami renderowanymi przez parser. Nie musisz go tworzyć ręcznie.

## Gdy coś nie działa

| Objaw | Co zrobić |
| --- | --- |
| Nie ma **Catalog** w menu | Otwórz pełny workspace Free Edition, nie uproszczony widok Genie. |
| Nie ma **Create > Volume** | Zmień schema lub utwórz własny schema; potrzebne są `USE CATALOG`, `USE SCHEMA` i `CREATE VOLUME`. |
| Upload nie działa | Sprawdź, czy jesteś na stronie Volume i masz `WRITE VOLUME`. |
| Komórka Python nie widzi PDF-ów | Sprawdź, że `source_documents_path` kończy się na nazwie Volume, a PDF-y są bezpośrednio w nim. |
| Zapis do Delta table kończy się błędem uprawnień | Użyj tabeli w schema, w którym masz `USE CATALOG`, `USE SCHEMA` i `CREATE TABLE`; najprościej użyć tego samego catalog i schema co dla Volume. |
| Błąd `ai_parse_document` albo funkcja nie istnieje | Funkcja AI może nie być dostępna w regionie lub aktualnym Free Edition. Nie zastępuj jej innym parserem: ćwiczenie wymaga tej samej funkcji w Pythonie i SQL. W takim przypadku użyj [bezpłatnego triala](https://docs.databricks.com/aws/en/getting-started/free-trial). |
| Renderer nie pokazuje obrazów | Uruchom najpierw komórkę Python. Sprawdź też, czy masz `WRITE VOLUME` dla katalogu `parsed_pages/python`. |

## Dlaczego te kroki są takie

`ai_parse_document` dostaje PDF jako dane binarne z Unity Catalog Volume i zwraca `VARIANT`. Opcja `imageOutputPath` zapisuje obrazy stron, które wykorzystuje renderer. Zobacz aktualną [dokumentację `ai_parse_document`](https://docs.databricks.com/gcp/en/sql/language-manual/functions/ai_parse_document), [tworzenie Volume](https://docs.databricks.com/aws/en/volumes/utility-commands) oraz [upload do Volume](https://docs.databricks.com/aws/en/volumes/unstructured-data-tutorial).

## Lokalne odtworzenie PDF-ów (opcjonalne)

Nie jest potrzebne do pracy w Databricks. Jeżeli chcesz odtworzyć PDF-y lokalnie, w katalogu `01_parsing` uruchom:

```powershell
npm.cmd install
npm.cmd run generate:robotics
npm.cmd run validate:robotics
```

## Kontynuacja — notebook `02_chunking`

Po poprawnym wykonaniu całego notebooka `01_parse_robotics_documents` zaimportuj także `notebooks/02_chunking.py` bezpośrednio do folderu `robotics_parsing` w Workspace (obok notebooka `01`). Otwórz go i wybierz **Serverless** w menu **Connect**.

1. Uruchom komórkę **0. Minimal configuration**. Nie ma w niej widgetów ani pól do wypełnienia.
2. Notebook używa na stałe tabeli źródłowej `workspace.default.robotics_parsed_documents`.
3. Chunky zapisze na stałe do `workspace.default.robotics_document_chunks`; tabela zostanie utworzona automatycznie przez sekcję 5.
4. Uruchom następnie sekcje 1–5 po kolei.

Notebook `02` odczytuje wyłącznie Pythonowy output zapisany wcześniej do Delta table. Tworzy Markdown przez `databricks-gpt-oss-20b`, osobny czysty tekst z separatorami `== page ==`, chunky LangChain oraz tabelę Delta z kolumnami `chunk_id`, `path`, `chunk_position` i `chunk_text`.

Jeżeli sekcja 4 zgłosi `ImportError`, utwórz tymczasową komórkę Python w tym notebooku i uruchom:

```python
%pip install langchain-text-splitters
```

Po instalacji zrestartuj Python, jeśli Databricks o to poprosi, a następnie zacznij notebook `02` ponownie od sekcji 0. To jest jedyna dodatkowa konfiguracja pakietu i jest potrzebna tylko wtedy, gdy biblioteka nie jest już dostępna w środowisku Serverless.

## Kontynuacja — notebook `03_vector_search`

Przed uruchomieniem tego notebooka wykonaj w całości notebooki `01_parse_robotics_documents` oraz `02_chunking`. Nie twórz ręcznie tabeli `docs_chunked` ani indeksu: notebook `03` tworzy je sam. Endpoint AI Search `robotics_ai_search_endpoint` utwórz ręcznie zgodnie z krokiem 3.

### 1. Zaimportuj notebook

1. W lewym pasku kliknij **Workspace** i otwórz wcześniej utworzony folder `robotics_parsing`.
2. Kliknij menu z trzema kropkami (**⋮**) dla folderu `robotics_parsing`, a następnie **Import**.
3. Kliknij **browse**, wybierz lokalny plik `01_parsing/notebooks/03_vector_search.py` i kliknij **Import**.
4. W folderze muszą być teraz trzy notebooki: `01_parse_robotics_documents`, `02_chunking` oraz `03_vector_search`.

### 2. Sprawdź endpoint embeddingów — bez tworzenia go ręcznie

Notebook używa dokładnie endpointu `databricks-gte-large-en` do testowego embeddingu i do tworzenia indeksu z zarządzanymi embeddingami.

1. W lewym pasku kliknij **Serving**.
2. Na górze listy **Endpoints** znajdź `databricks-gte-large-en`.
3. Nie klikaj **Create serving endpoint** i nie próbuj tworzyć endpointu o tej nazwie. Jest to prekonfigurowany endpoint Databricks Foundation Model APIs, dostępny automatycznie tylko w obsługiwanych regionach.
4. Jeśli endpoint jest widoczny, wróć do notebooka. Jeśli nie ma go na liście, ten notebook nie może zostać wykonany w obecnym workspace — nie zastępuj modelu innym endpointem, ponieważ ćwiczenie wymaga tej dokładnej nazwy. Użyj workspace w regionie obsługującym ten model albo bezpłatnego triala Databricks.

### 3. Sprawdź dostępność AI Search

1. W lewym pasku kliknij **Compute**.
2. Otwórz kartę **AI Search**. Jest to obecna nazwa usługi znanej wcześniej jako Vector Search.
3. Kliknij **Create endpoint**.
4. W polu nazwy wpisz dokładnie `robotics_ai_search_endpoint`.
5. Jako typ wybierz **Standard**, a następnie kliknij **Confirm**.
6. Poczekaj, aż endpoint będzie miał status **Ready** lub **Online**. Dopiero wtedy uruchom sekcję 4 notebooka `03`.
7. Jeżeli nie widzisz karty **AI Search**, nie uruchamiaj sekcji tworzenia indeksu. Usługa nie jest dostępna lub nie została udostępniona w tym workspace; jedyną zgodną drogą jest workspace/trial z AI Search, a nie lokalny zamiennik.
8. Free Edition pozwala na jeden endpoint AI Search. Jeżeli masz już endpoint utworzony dla innego ćwiczenia, nie utworzysz drugiego. Usuń poprzedni endpoint tylko wtedy, gdy nie jest już potrzebny, albo uruchom ćwiczenie w innym workspace/trialu.

### 4. Uruchom notebook

1. W **Workspace** otwórz `03_vector_search` i w prawym górnym rogu wybierz **Connect** > **Serverless**.
2. Uruchom komórkę **0. Install required SDK packages**. Instaluje ona `databricks-ai-search` i aktualny `databricks-sdk`.
3. Uruchom następną komórkę restartu Python. Po restarcie kontynuuj od **1. Minimal configuration**; nie zmieniaj wpisanych na stałe wartości `workspace.default`.
4. Uruchom kolejne sekcje po kolei. Sekcja 2 automatycznie tworzy `workspace.default.docs_chunked`, włącza Change Data Feed i pokazuje pięć rekordów. Sekcja 4 tworzy indeks `workspace.default.robotics_document_chunks_index` i uruchamia jego pierwszą inicjalizację.
5. Po utworzeniu indeksu w logach może przez kilka minut pojawiać się `PROVISIONING_ENDPOINT` lub komunikat o oczekiwaniu na `ONLINE`. Jest to normalne przygotowywanie zasobów indeksu; pozostaw komórkę uruchomioną i nie usuwaj indeksu ani endpointu.
6. Gdy indeks uzyska status `ONLINE`, ale wcześniejsze uruchomienie sekcji 4 zakończyło się błędem „index is not ready”, uruchom sekcję 4 jeszcze raz. Następnie uruchom cztery komórki wyszukiwania i komórkę rerankingu.

Do wykonania `03` potrzebujesz uprawnień `USE CATALOG`, `USE SCHEMA`, `CREATE TABLE` i odczytu/zapisu tabel w `workspace.default`, a także prawa do użycia endpointu modelu. Nie twórz wcześniej żadnej Delta table: wcześniejsze notebooki tworzą `robotics_parsed_documents` i `robotics_document_chunks`, a notebook `03` tworzy `docs_chunked`.

Jeżeli komórka embeddingu zgłasza błąd, sprawdź **Serving** i dostępność `databricks-gte-large-en`. Jeżeli tworzenie endpointu lub indeksu zgłasza błąd, sprawdź **Compute** > **AI Search**, limity Free Edition i uprawnienia. Free Edition ma limit jednego endpointu AI Search oraz ograniczenia Model Serving; niektóre modele i funkcje mogą być niedostępne w danym regionie.

## Kontynuacja — notebook `04_building_and_logging`

Nie twórz ręcznie żadnej nowej tabeli, plików agenta, eksperymentu MLflow ani modelu w Unity Catalog. Notebook `04` sam tworzy obok siebie pliki `agent.py` i `agent_config.yaml` w folderze Workspace notebooka, zakłada eksperyment MLflow w Twoim folderze użytkownika oraz rejestruje model `workspace.default.robotics_rag_agent`.

### 1. Warunki przed uruchomieniem

1. Wykonaj notebooki `01`, `02` i `03` do momentu, w którym indeks `workspace.default.robotics_document_chunks_index` ma status **ONLINE**.
2. W lewym pasku kliknij **Serving** i sprawdź, czy na liście endpointów Foundation Model APIs widnieje `databricks-inkling`.
3. Nie twórz ręcznie endpointu o nazwie `databricks-inkling`. Jest to prekonfigurowany endpoint Databricks; jeśli nie jest dostępny w tym workspace lub regionie, notebook nie może wykonać części agentowej. W **AI Playground** wybierz model **Inkling**. W notebooku `ChatDatabricks` używa nazwy endpointu `databricks-inkling`.
4. Upewnij się, że masz w `workspace.default` uprawnienia `USE CATALOG`, `USE SCHEMA`, `CREATE MODEL` oraz dostęp do indeksu AI Search i endpointu modelu.

### 2. Zaimportuj i uruchom notebook

1. W **Workspace** otwórz folder `robotics_parsing`.
2. Z menu z trzema kropkami (**⋮**) folderu wybierz **Import**, wskaż `01_parsing/notebooks/04_building_and_logging.py` i kliknij **Import**.
3. Otwórz `04_building_and_logging`, a następnie wybierz **Connect** > **Serverless**.
4. Uruchom komórkę **0. Install required packages**, a następnie komórkę restartu Python. Po restarcie kontynuuj od **1. Minimal configuration**.
5. Uruchamiaj kolejne sekcje po kolei. Komórka tworzenia plików wymaga, aby notebook był zapisany w folderze Workspace, do którego masz prawo zapisu — po imporcie do własnego folderu `robotics_parsing` nie jest potrzebna żadna dodatkowa konfiguracja.

### 3. Co jest opcjonalne

Sekcja AI Playground jest wyłącznie instrukcją korzystania z interfejsu. Jeśli nie widzisz pozycji **Playground** w lewym menu, możesz ją pominąć: nie blokuje to budowy agenta, trace ani rejestracji modelu.

Nie konfiguruj rerankingu dla notebooka `04`. Agent korzysta z wyszukiwania hybrydowego bez rerankera, ponieważ bieżąca konfiguracja Free Edition blokuje dostęp do modelu rerankera.

Jeżeli rejestracja modelu zwróci błąd uprawnień, nie twórz ręcznie pustego modelu w Catalog Explorer. Poproś o `CREATE MODEL` w `workspace.default` albo użyj schema, w którym to uprawnienie jest dostępne; wtedy trzeba zmienić stałe `catalog` i `schema` w notebooku.
