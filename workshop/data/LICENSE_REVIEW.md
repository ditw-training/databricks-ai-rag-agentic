# Przegląd licencji danych warsztatu

Pliki w `workshop/data/` powstały z datasetu Databricks Marketplace (`scripts/prepare_data_premium.ipynb`), zostały spseudonimizowane i są przeznaczone do publikacji w repozytorium warsztatu. Zanim zacommitujesz dane, uzupełnij tabelę na podstawie **żywego** listingu. Licencja może się zmienić, więc przy każdym ponownym eksporcie przejrzyj ją jeszcze raz.

**Status:** ⏳ nieprzejrzane. Do czasu zmiany statusu na ✅ pliki danych nie trafiają do commita.

| Pole | Wartość z listingu |
|---|---|
| Dokładny tytuł produktu | Databricks Simulated Retail Customer Data |
| Dostawca | |
| Identyfikator lub URL listingu | |
| Nazwa lub URL licencji | |
| Data przeglądu | |
| Kto przeglądał | |
| Dozwolony cel użycia | |
| Użycie komercyjne (płatny warsztat) | |
| **Redystrybucja danych pochodnych** (publiczne repo, uczestnicy) | |
| Wymagane przypisanie autorstwa | |
| Obowiązki dotyczące danych osobowych | dataset symulowany; dodatkowo pseudonimizacja `customer_name`, `tax_id`, `lat`, `lon` |
| Zakres zaakceptowanego udostępnienia | `databricks_simulated_retail_customer_data.v01`: `customers`, `sales`, `sales_orders` |

## Decyzja

- [ ] Redystrybucja pochodnej dozwolona: commit `workshop/data/` do repo.
- [ ] Redystrybucja niedozwolona: dane zostają poza repo. Uczestnicy dostają je z Volume udostępnionego przez prowadzącego albo z Marketplace (`00_setup` wymaga wtedy zmiany).

Wzorzec przeglądu: `Warsztaty_Krzysztof/genai_eval_and_monitor/notebooks/10_exploring_datasets.py`.
