# Przegląd licencji danych warsztatu

Pliki w `workshop/data/` powstały z datasetu Databricks Marketplace (`scripts/prepare_data_premium.ipynb`), zostały spseudonimizowane i są przeznaczone do publikacji w repozytorium warsztatu. Zanim zacommitujesz dane, uzupełnij tabelę na podstawie **żywego** listingu. Licencja może się zmienić, więc przy każdym ponownym eksporcie przejrzyj ją jeszcze raz.

**Status:** ✅ zaakceptowane 2026-09-15. Redystrybucja danych pochodnych dozwolona na CC BY 4.0 z przypisaniem autorstwa (`data/NOTICE.md`).

| Pole | Wartość z listingu |
|---|---|
| Dokładny tytuł produktu | Simulated Retail Customer Data („This dataset represents customer and sales data for a fictional retail company.”) |
| Dostawca | Databricks (provider `ea1e69ff-0127-4c94-bf39-e841fe1d19d2`, share `dbacademy_dataset_retail`, kategoria EDUCATION) |
| Identyfikator lub URL listingu | `a82597f6-5ada-49d5-b934-d6c9dece16a1` |
| Nazwa lub URL licencji | Creative Commons Attribution 4.0 (https://creativecommons.org/licenses/by/4.0/) + Databricks Marketplace Consumer Terms (https://cms.databricks.com/sites/default/files/2023-01/marketplace-consumer-terms_0.pdf) |
| Data przeglądu | 2026-09-15 (odczyt listingu przez API) |
| Kto przeglądał | Krzysztof Burejza (decyzja); treść listingu i Consumer Terms przeanalizowane z Claude Code |
| Dozwolony cel użycia | listing: szkolenia Databricks Academy („Get Started with Databricks for Data Analysis”); CC BY 4.0 nie ogranicza celu |
| Użycie komercyjne (płatny warsztat) | dozwolone: CC BY 4.0; Consumer Terms (rev. 17.01.2023) nie dodają ograniczeń dla produktów |
| **Redystrybucja danych pochodnych** (publiczne repo, uczestnicy) | dozwolona: CC BY 4.0 (adaptacje też), z przypisaniem autorstwa i wskazaniem zmian. Consumer Terms: „Databricks does not grant you any rights to any Products. Your rights to use any Products would be granted by the Data Provider”, więc obowiązuje licencja dostawcy; brak klauzul o zakazie redystrybucji |
| Wymagane przypisanie autorstwa | tak: „Simulated Retail Customer Data, Databricks, CC BY 4.0; zmodyfikowane: agregacja RFM, pseudonimizacja, raporty PDF i chunki” |
| Obowiązki dotyczące danych osobowych | dataset symulowany; dodatkowo pseudonimizacja `customer_name`, `tax_id`, `lat`, `lon` |
| Zakres zaakceptowanego udostępnienia | `databricks_simulated_retail_customer_data.v01`: `customers`, `sales`, `sales_orders` |

## Decyzja

- [x] Redystrybucja pochodnej dozwolona: commit `workshop/data/` do repo, z `data/NOTICE.md`.
- [ ] Redystrybucja niedozwolona: dane zostają poza repo. Uczestnicy dostają je z Volume udostępnionego przez prowadzącego albo z Marketplace (`00_setup` wymaga wtedy zmiany).

Wzorzec przeglądu: `Warsztaty_Krzysztof/genai_eval_and_monitor/notebooks/10_exploring_datasets.py`.
