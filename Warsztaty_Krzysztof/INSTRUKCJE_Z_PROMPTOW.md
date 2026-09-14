# Instrukcje z promptów — moduł Databricks „01_parsing”

Tworzysz moduł kursu Databricks. Wygeneruj mi 10 artykułów na temat robotyki w formacie PDF. Mają mieć po 2–3 strony, dobrze jakby posiadały też jakieś nagłówki, tabele, wykresy oraz obrazki. Obrazki mogą być w ciepłej, akwarelowej estetyce animacyjnej.

Następnie wygeneruj notebook Databricks, który:

1. najpierw wykona parsing za pomocą Pythona i polecenia `ai_parse_document`,
2. następnie wykona parsing za pomocą SQL,
3. następnie wyświetli metadane sparsowanych dokumentów,
4. następnie wyświetli wizualizację dokumentu za pomocą `DocumentRenderer` i `render_ai_parse_output`.
5. dodatkowo zapisze tylko output sparsowany przez Python do Delta table.

Każdy poszczególny etap ma być osobnym blokiem w notebooku, a funkcje w kodzie mają posiadać komentarze po angielsku wyjaśniające, co robią.

Do tego wygeneruj instrukcję, jak użyć tych rzeczy w darmowym środowisku Databricks. Instrukcja ma być w prostym pliku Markdown w języku polskim.

Wygenerowane rzeczy umieść w folderze o nazwie `01_parsing`. Jeżeli czegoś nie wiesz, zapytaj zamiast zakładać fakty.

Przykładowy tutorial tego typu:

https://customer-academy.databricks.com/learn/courses/2706/building-retrieval-agents-on-databricks/lessons/50348/demo-parse-documents-to-structured-data

## Doprecyzowanie zawartości modułu

Utworzyć `01_parsing/` z:

- `documents/` — 10 anglojęzycznych, fikcyjnych PDF-ów o robotyce, każdy dokładnie 3 strony.
- `assets/illustrations/` — 10 ilustracji w ciepłej, akwarelowej estetyce animacyjnej.
- `scripts/generate_robotics_pdfs.mjs` — odtwarzalny generator PDF-ów.
- `notebooks/01_parse_robotics_documents.py` — importowalny notebook Databricks.
- `notebooks/includes/document_renderer.py` — lokalny, samowystarczalny `DocumentRenderer` z `render_ai_parse_output`.
- `README.md` — prosta instrukcja po polsku dla Databricks Free Edition.

### Dokumenty PDF

- Tematy: everyday robotics, robot senses, motion and actuators, mobile robots, robot arms, collaborative robots, robots in logistics, robots and AI, safety and ethics, future robotics.
- Każdy PDF zawiera tytuł, sekcje i śródtytuły, opisowy tekst, tabelę porównawczą, wykres z fikcyjnymi danymi edukacyjnymi, ilustrację oraz podpisy rysunków.
- Ilustracje będą unikalne i utrzymane w uzgodnionej estetyce ręcznie malowanej akwareli; bez kopiowania stylu konkretnego studia.
- Dokumenty zostaną wyraźnie oznaczone jako „fictional course sample”, aby nie sugerowały prawdziwych danych technicznych.

### Notebook Databricks

Notebook w formacie źródłowym `.py` będzie miał komórkę konfiguracji i osobne komórki dla wymaganych etapów:

1. Konfiguracja ścieżki do PDF-ów w Unity Catalog Volume oraz dwóch katalogów wyjściowych na renderowane strony.
2. Parsowanie Pythonem: `pyspark.sql.functions.ai_parse_document` na binarnej kolumnie `content`; wynik w tymczasowym widoku `parsed_python_docs`.
3. Parsowanie SQL: osobna komórka `%sql` wywołująca `ai_parse_document(content, map(...))`; wynik w `parsed_sql_docs`.
4. Metadane: widok obu wyników z `metadata`, `error_status`, liczbą stron i liczbą elementów.
5. Wizualizacja: konwersja jednego wyniku `VARIANT` przez `to_json()`, a następnie `render_ai_parse_output(...)`.
6. Zapis wyłącznie Pythonowego outputu do tabeli Delta jako osobny segment notebooka.

Parser będzie przypinał wersję schematu `2.0`, zapisywał obrazy stron przez `imageOutputPath` oraz generował opisy figur. Renderer pokaże render strony z kolorowymi ramkami `bbox`, legendą typów elementów i treścią po najechaniu kursorem. Wszystkie komentarze i docstringi w kodzie będą po angielsku.

### Instrukcja i walidacja

- `README.md` opisze: utworzenie konta Free Edition, managed volume, upload katalogu `documents/`, import obu notebooków, ustawienie widgetów ścieżek oraz kolejność uruchamiania.
- Instrukcja poda wymagania i diagnostykę: serverless environment version 3+, dostępność funkcji w regionie oraz uprawnienia do odczytu/zapisu Volume. Jeśli `ai_parse_document` nie jest dostępne w danym workspace Free Edition, wymagane dwa etapy parsowania nie będą mogły zostać wykonane — instrukcja wskaże użycie bezpłatnego triala jako jedyną zgodną ścieżkę, bez zastępowania funkcji innym parserem.
- Walidacja artefaktów: 10 poprawnych plików PDF, po 3 strony każdy; obecność tekstu, tabeli, wykresu i ilustracji w każdym; poprawny import notebooka oraz statyczna kontrola kolejności komórek i ścieżek.
- Test końcowy w Databricks: oba parsowania zwracają rekordy, metadane są widoczne, a renderer pokazuje stronę z nakładkami.

### Założenia

- PDF-y są materiałem testowym do parsowania, a nie źródłem wiedzy specjalistycznej.
- Ścieżki Volume nie będą zaszyte w kodzie; użytkownik poda je w widgetach notebooka.
- `ai_parse_document` przyjmuje PDF jako dane binarne, zwraca `VARIANT`, a wersja 2.0 udostępnia strony, elementy, metadane i współrzędne ramek; `imageOutputPath` zapisuje renderowane strony.
- Free Edition jest środowiskiem serverless z limitami użycia, a część funkcji może być ograniczona.

## Późniejsze doprecyzowanie instrukcji Databricks

Instrukcja ma być jasna, oparta na najnowszej wersji Databricks i wskazywać dokładnie, co oraz gdzie kliknąć.

Nie należy kazać tworzyć compute przed utworzeniem i przygotowaniem Catalog/Volume. Prawidłowa kolejność instrukcji to:

1. **Catalog** — utworzenie lub wybór schema i utworzenie managed Volume.
2. **Upload** — wgranie 10 PDF-ów do Volume przez interfejs Catalog Explorer.
3. **Workspace** — utworzenie folderów oraz import głównego notebooka i renderera z zachowaniem ścieżki względnej `includes/document_renderer`.
4. **Notebook** — otwarcie głównego notebooka i wybór **Serverless** z listy **Connect** lub compute w prawym górnym rogu notebooka.
5. **Widgets** — ustawienie ścieżek Volume i uruchomienie komórek od góry do dołu.

Instrukcja ma opisywać aktualne elementy UI, między innymi:

- **Catalog** → wybór schema → **Create** → **Volume** → **Managed volume** → **Create**;
- strona Volume → **Upload to this volume** → **browse** → wybór wszystkich 10 PDF-ów → **Upload**;
- **Workspace** → **Create** → **Folder** → menu **⋮** folderu → **Import**;
- notebook → **Connect** / lista compute → **Serverless**.

## Stała konfiguracja ścieżek i tabel

Nie używaj widgetów do wpisywania ścieżek przy każdym uruchomieniu. W notebookach wpisz na stałe:

- `source_documents_path = "/Volumes/workspace/default/robotics_files"`
- `python_rendered_pages_path = "/Volumes/workspace/default/robotics_files/parsed_pages/python"`
- `sql_rendered_pages_path = "/Volumes/workspace/default/robotics_files/parsed_pages/sql"`
- `parsed_delta_table = "workspace.default.robotics_parsed_documents"`
- `chunked_delta_table = "workspace.default.robotics_document_chunks"`

Tabele Delta mają zostać utworzone automatycznie przez notebooki przy pierwszym zapisie. Nie należy tworzyć ich ręcznie; wymagane są jedynie uprawnienia `USE CATALOG`, `USE SCHEMA` i `CREATE TABLE` w `workspace.default`.

## Kontynuacja: notebook `02_chunking`

Przygotuj kolejny notebook będący kontynuacją parsingu. Ma mieć nazwę `02_chunking`. Załóż, że poprzedni notebook został wykonany. Wykonaj tylko potrzebną konfigurację, tylko jeśli jest potrzebna. Nowy notebook ma zawierać następujące sekcje:

1. Wczytanie wcześniej sparsowanych danych w formacie JSON.
2. Oczyszczanie danych za pomocą LLM do postaci Markdown:
   - jako endpoint użyj `databricks-gpt-oss-20b`;
   - napisz `prompt_prefix` w języku angielskim, w którym AI wciela się w pomocnego asystenta, który weźmie JSON i przekonwertuje dane w czysty i czytelny Markdown;
   - do oddzielenia stron użyj `== page ==`;
   - zachowaj nagłówki, tabele, podpisy i wszystkie potrzebne struktury;
   - output nie może zawierać JSON-a ani żadnych bloków kodu.
3. Oczyszczenie sparsowanego JSON-a do pojedynczego stringa w postaci tekstowej. Do oddzielenia stron użyj `== page ==`. Ten wariant nie może używać pozostałej semantyki.
4. Wykonaj chunking tekstu z punktu 3 za pomocą funkcji `RecursiveCharacterTextSplitter` z biblioteki LangChain:
   - `chunk_size=2000`;
   - `chunk_overlap=200`;
   - zachowaj separatory `== page ==`.
5. Zapis danych po chunkingu do Delta table.
