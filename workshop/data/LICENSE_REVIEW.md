# Przegląd licencji danych warsztatu

Pliki w `workshop/data/` powstały z datasetu Databricks Marketplace (`scripts/prepare_data_premium.ipynb`), zostały spseudonimizowane i są przeznaczone do publikacji w repozytorium warsztatu. Zanim zacommitujesz dane, uzupełnij tabelę na podstawie **żywego** listingu. Licencja może się zmienić, więc przy każdym ponownym eksporcie przejrzyj ją jeszcze raz.

**Status:** ⏳ pola uzupełnione z API Marketplace (2026-09-15), czeka na potwierdzenie człowieka. Do czasu zmiany statusu na ✅ pliki danych nie trafiają do commita.

| Pole | Wartość z listingu |
|---|---|
| Dokładny tytuł produktu | Simulated Retail Customer Data („This dataset represents customer and sales data for a fictional retail company.”) |
| Dostawca | Databricks (provider `ea1e69ff-0127-4c94-bf39-e841fe1d19d2`, share `dbacademy_dataset_retail`, kategoria EDUCATION) |
| Identyfikator lub URL listingu | `a82597f6-5ada-49d5-b934-d6c9dece16a1` |
| Nazwa lub URL licencji | Creative Commons Attribution 4.0 (https://creativecommons.org/licenses/by/4.0/) + Databricks Marketplace Consumer Terms (https://cms.databricks.com/sites/default/files/2023-01/marketplace-consumer-terms_0.pdf) |
| Data przeglądu | 2026-09-15 (odczyt listingu przez API) |
| Kto przeglądał | _do uzupełnienia_ |
| Dozwolony cel użycia | listing: szkolenia Databricks Academy („Get Started with Databricks for Data Analysis”); CC BY 4.0 nie ogranicza celu |
| Użycie komercyjne (płatny warsztat) | CC BY 4.0: dozwolone; do potwierdzenia w Consumer Terms (PDF) |
| **Redystrybucja danych pochodnych** (publiczne repo, uczestnicy) | CC BY 4.0: dozwolona (adaptacje też), pod warunkiem przypisania autorstwa i wskazania zmian; do potwierdzenia w Consumer Terms (PDF) |
| Wymagane przypisanie autorstwa | tak: „Simulated Retail Customer Data, Databricks, CC BY 4.0; zmodyfikowane: agregacja RFM, pseudonimizacja, raporty PDF i chunki” |
| Obowiązki dotyczące danych osobowych | dataset symulowany; dodatkowo pseudonimizacja `customer_name`, `tax_id`, `lat`, `lon` |
| Zakres zaakceptowanego udostępnienia | `databricks_simulated_retail_customer_data.v01`: `customers`, `sales`, `sales_orders` |

## Decyzja

- [ ] Redystrybucja pochodnej dozwolona: commit `workshop/data/` do repo.
- [ ] Redystrybucja niedozwolona: dane zostają poza repo. Uczestnicy dostają je z Volume udostępnionego przez prowadzącego albo z Marketplace (`00_setup` wymaga wtedy zmiany).

Wzorzec przeglądu: `Warsztaty_Krzysztof/genai_eval_and_monitor/notebooks/10_exploring_datasets.py`.
