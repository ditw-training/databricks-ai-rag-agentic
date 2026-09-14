# Single-agent app — materiały kursowe

Ten folder zawiera materiały do kolejnego modułu po `rag_agent`.

## Dane San Francisco Airbnb

Plik [`data/sf_airbnb_listings.csv`](data/sf_airbnb_listings.csv) jest darmowym snapshotem ofert Airbnb z San Francisco. Zawiera między innymi `id`, nazwę, gospodarza, dzielnicę, typ pokoju, cenę, liczbę opinii i dostępność.

- Materiał lokalny pochodzi z publicznego repozytorium [San-Francisco-AirBnB-Analysis](https://github.com/lrakla/San-Francisco-AirBnB-Analysis), udostępnionego na licencji MIT. Jest to snapshot danych z lat 2019–2020 oparty na danych Inside Airbnb.
- Jeżeli potrzebujesz nowszego pliku, wejdź na [Inside Airbnb — Get the Data](https://insideairbnb.com/get-the-data/), odszukaj **San Francisco** i pobierz **Detailed Listings data** (`listings.csv.gz`). Źródło jest aktualizowane okresowo, dlatego data pliku może się zmieniać.

## Wgranie danych do Databricks

1. W Databricks kliknij **Catalog** > `workspace` > `default`.
2. Kliknij **Create** > **Volume**, wpisz `sf_airbnb_data`, wybierz **Managed volume** i kliknij **Create**.
3. Otwórz nowy Volume i kliknij **Upload to this volume**.
4. Wskaż lokalny plik `single_agent_app/data/sf_airbnb_listings.csv` i kliknij **Upload**.
5. Pełna ścieżka pliku w notebooku będzie następująca:

   ```text
   /Volumes/workspace/default/sf_airbnb_data/sf_airbnb_listings.csv
   ```

6. Zaimportuj `notebooks/06_building_uc_functions.py` do swojego folderu Workspace, połącz go z **Serverless** i uruchamiaj komórki od góry do dołu.
7. Sekcja 2 notebooka sama utworzy lub nadpisze zarządzaną tabelę Delta `workspace.default.sf_airbnb_listings`.

Do pełnego wykonania potrzebujesz uprawnień `USE CATALOG`, `USE SCHEMA`, `CREATE VOLUME`, `READ VOLUME`, `CREATE TABLE`, `CREATE FUNCTION` i `EXECUTE` w `workspace.default`.

## Ważne ograniczenie funkcji Python UC

Python UDF zarejestrowany w Unity Catalog działa w izolowanym środowisku i nie ma dostępu do `spark.sql` ani tabel Delta. Dlatego notebook tworzy funkcję SQL `get_listing_details` do pobierania oferty po `listing_id`, a rejestrowana funkcja Python `format_listing_for_agent` formatuje przekazane pola do czytelnego tekstu dla agenta.

Wykonanie funkcji przez `DatabricksFunctionClient` wymaga serverless generic compute. Jeśli Free Edition zwróci błąd `Cannot access Spark Connect`, ograniczenie dotyczy dostępności tej usługi w workspace, a nie danych CSV.
