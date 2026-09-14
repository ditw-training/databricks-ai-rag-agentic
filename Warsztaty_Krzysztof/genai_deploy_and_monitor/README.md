# Moduł `genai_deploy_and_monitor`

Ten moduł zawiera notebook `15_batch_inference.py`. Buduje on demonstracyjny przepływ: XSum → tabela Delta → pipeline Hugging Face `t5-small` → MLflow → Unity Catalog Model Registry → endpoint Model Serving → batch inference SQL przez `ai_query`.

## Co przygotować przed uruchomieniem

1. Otwórz Databricks i wybierz środowisko Serverless. Notebook używa stałych nazw `workspace.default`, więc konto musi mieć katalog `workspace` i schemat `default`.
2. Upewnij się, że masz uprawnienia `USE CATALOG`, `USE SCHEMA`, `CREATE TABLE`, `CREATE MODEL` oraz możliwość tworzenia wersji modelu i endpointów Model Serving. Do przypisania aliasu `champion` potrzebujesz własności modelu albo odpowiednich uprawnień do jego modyfikacji.
3. Sekcja 1 pobiera próbkę publicznego datasetu `EdinburghNLP/xsum` przez Hugging Face Dataset Viewer API, a sekcja 2 pobiera model `t5-small` z Hugging Face. Środowisko musi mieć dostęp sieciowy do Hugging Face. Notebook celowo nie używa biblioteki `datasets`, aby uniknąć konfliktu jej wersji z patchami runtime Databricks oraz nietrwałego cache w `/tmp`. Token Hugging Face nie jest potrzebny dla tych publicznych zasobów, ale może pomóc przy rate limit.
4. Otwórz notebook w workspace i uruchom komórki kolejno od góry. Pierwsza komórka instalacyjna restartuje Python, dlatego po restarcie przejdź do kolejnej komórki.

Notebook przypina `transformers==4.57.1`. Nie zmieniaj tego ograniczenia na wersję 5.x: w aktualnej gałęzi 5.x zadanie pipeline `summarization`, wymagane w tym ćwiczeniu z T5, nie jest dostępne pod tą historyczną nazwą.

## Endpoint produkcyjny i `ai_query`

Sekcja 7 tworzy endpoint `xsum-t5-small-summarizer-endpoint` dla wersji aktualnie oznaczonej aliasem `@champion`. Tworzenie custom Model Serving endpoint może być niedostępne lub limitowane w Databricks Free Edition. Jeśli tak się stanie, sekcje 1–6 nadal pokazują tworzenie, testowanie i rejestrację modelu, ale sekcja 8 nie może zostać wykonana bez działającego endpointu.

Po utworzeniu endpointu:

1. Wejdź w **Serving** i otwórz `xsum-t5-small-summarizer-endpoint`.
2. Poczekaj na status **Ready**.
3. Kliknij **Query endpoint** i wybierz **Show example**. Sprawdź, czy wejście ma postać zbliżoną do `{"inputs": ["sample text"]}`.
4. Jeśli przykład endpointu używa innego kontraktu wejścia lub wyjścia, dostosuj wyłącznie argumenty `request` i `returnType` w sekcji 8 zgodnie z tym przykładem. Nie zmieniaj tabel źródłowych.
5. Uruchom sekcję 8 na Serverless albo Databricks Runtime 18.2+. `ai_query` nie działa na Pro ani Classic SQL Warehouse.

Po promocji nowej wersji modelu do `@champion` uruchom ponownie sekcję 7 po zaktualizowaniu konfiguracji istniejącego endpointu na numer tej wersji. Alias ułatwia wybór wersji produkcyjnej, ale endpoint custom Model Serving przechowuje konkretny numer wersji.

## Endpoint RAG z notebooka 16

> **Ważne dla tego workspace Free Edition:** nie włączaj opcji **Enable inference tables and telemetry** dla katalogu `workspace` i schema `default`. Ten katalog używa default storage, a telemetryczne tabele OpenTelemetry (`*_otel_spans`, `*_otel_logs`, `*_otel_metrics`) oraz AI Gateway inference tables wymagają katalogu ze skonfigurowanym external storage. Błąd `Unsupported table kind. Tables created in default storage are not supported` potwierdza to ograniczenie. Endpoint bez telemetry może działać; notebook 17 nie może jednak wykonać rzeczywistego monitoringu bez zewnętrznego storage.

Jeżeli utworzenie endpointu przez SDK w notebooku 16 przekracza limit czasu, utwórz go w całości w UI Databricks. Nie wymaga to CLI ani działań w Windows.

1. Najpierw wykonaj sekcję 1 notebooka `16_deploying_llm_chain.py`. W **Catalog** → `workspace` → `default` → **Models** sprawdź, że istnieje model `robotics_rag_deployment_chain`.
2. W lewym menu otwórz **Serving** i kliknij **Create serving endpoint**.
3. Nazwij endpoint dokładnie: `robotics-rag-deployment-endpoint`.
4. W części **Served entities** wybierz **My models – Unity Catalog** albo **Custom model**, następnie wybierz model `workspace.default.robotics_rag_deployment_chain` oraz jego najnowszą wersję.
5. Wybierz compute **Small** (CPU) i włącz **Scale to zero**.
6. Rozwiń **Advanced configurations** lub **Environment variables** i dodaj:
   - `DATABRICKS_HOST` = `{{secrets/rag_deployment_secrets/databricks_host}}`
   - `DATABRICKS_TOKEN` = `{{secrets/rag_deployment_secrets/databricks_token}}`
7. Jeżeli formularz tworzenia pokazuje część **AI Gateway**, włącz **Inference tables** i wybierz katalog `workspace`, schema `default` oraz prefix `robotics_rag_inference`. W niektórych wersjach Free Edition tej części nie ma na formularzu — wtedy niczego nie konfiguruj na tym etapie.
8. Kliknij **Create** i poczekaj na status **Ready**. Pierwsze wdrożenie własnego modelu może trwać 10–20 minut. Przy statusie **Failed** otwórz endpoint i sprawdź **Logs** lub **Build logs**.
9. Po statusie **Ready** otwórz endpoint. Jeżeli widzisz **Edit AI Gateway** lub sekcję **AI Gateway**, włącz **Inference tables** tam, ustaw `workspace`, `default` i prefix `robotics_rag_inference`, a następnie kliknij **Update**. Jeżeli tej opcji nadal nie ma, AI Gateway inference tables nie są udostępnione dla tego endpointu lub workspace; endpoint może nadal działać, ale notebook 17 nie będzie miał payload table do monitoringu.
10. Po statusie **Ready** pomiń blok 3 notebooka 16 i uruchom blok 5. Blok 5 sam tworzy klienta SDK, więc nie zależy od wykonanego wdrożenia przez kod.

Tabela AI Gateway powinna pojawić się jako `workspace.default.robotics_rag_inference_payload` po wykonaniu przykładowego zapytania z bloku 5. Jej logi mogą pojawić się z opóźnieniem, dlatego przed uruchomieniem notebooka 17 odczekaj kilka minut i sprawdź ją w **Catalog** → `workspace` → `default` → **Tables**.

## Diagnostyka

- **Błąd podczas pobierania XSum lub modelu** — sprawdź dostęp do Hugging Face, uruchom ponownie komórkę instalacyjną i restart Python. Jeśli API Dataset Viewer zwróci limit zapytań, odczekaj chwilę albo skonfiguruj token Hugging Face zgodnie z polityką organizacji.
- **`Unknown task summarization`** — w środowisku pozostał Transformers 5.x. Uruchom ponownie pierwszą komórkę z `transformers==4.57.1`, wykonaj restart Python i dopiero wtedy uruchom sekcję 2.
- **Brak uprawnień do rejestracji** — sprawdź `USE CATALOG`, `USE SCHEMA`, `CREATE MODEL` i własność modelu w **Catalog** → `workspace` → `default` → **Models**.
- **Endpoint nie staje się Ready** — otwórz go w **Serving** i sprawdź komunikat wdrożenia oraz dostępność Custom Model Serving w regionie i planie workspace.
- **`ai_query` zwraca błąd kontraktu** — użyj **Query endpoint** → **Show example** jako źródła prawidłowego `request` i dopasuj `returnType` w sekcji 8.
