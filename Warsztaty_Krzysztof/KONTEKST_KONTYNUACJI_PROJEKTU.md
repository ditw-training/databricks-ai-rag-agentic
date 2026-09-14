# Kontekst kontynuacji projektu Databricks

Ten plik jest przekazaniem kontekstu dla kolejnego agenta AI. Zawiera aktualny stan projektu, decyzje, konfigurację Databricks, historię problemów i preferencje użytkownika. Należy go przeczytać przed zmianą materiałów.

## 1. Cel projektu i układ katalogów

Projekt składa się z dwóch ukończonych modułów oraz rozpoczynanego trzeciego modułu szkoleniowego Databricks.

| Moduł | Inspiracja kursowa | Cel |
| --- | --- | --- |
| rag_agent | Building Retrieval Agents On Databricks | Pełny przepływ RAG: dokumenty PDF, parsowanie, chunking, AI Search, agent i Knowledge Assistant. |
| single_agent_app | Building Single-Agent Applications on Databricks | Agent korzystający z tabeli Delta i funkcji Unity Catalog, z MLflow tracingiem, tagami i rejestracją modelu. |
| genai_eval_and_monitor | Generative AI Application Evaluation and Governance | Rozpoznawanie, licencjonowanie i import danych Marketplace jako podstawa dalszych ćwiczeń z ewaluacji i governance. |

Najważniejsze artefakty w katalogu głównym:

- rag_agent/ — pierwszy moduł wraz z dokumentami, ilustracjami, notebookami, instrukcją i raportem.
- single_agent_app/ — drugi moduł wraz z danymi CSV, notebookami, instrukcją i raportem.
- genai_eval_and_monitor/ — rozpoczęty trzeci moduł; zawiera notebook eksploracji danych Marketplace.
- sprawozdanie_modulow_rag_agent_i_single_agent_app.pdf — aktualne zbiorcze sprawozdanie z obu modułów.
- scripts/generate_combined_modules_report.mjs — odtwarzalny generator zbiorczego raportu PDF.
- INSTRUKCJE_Z_PROMPTOW.md — wcześniejszy zapis pierwotnych wymagań dla modułu parsowania. W części narzędzi konsolowych może wyglądać na źle zakodowany; ten plik jest nowszym przekazaniem stanu.

## 2. Preferencje użytkownika i standard pracy

- Rozmowa, raporty i instrukcje dla użytkownika mają być po polsku. Kod, komentarze i docstringi w notebookach mają być po angielsku.
- Instrukcje Databricks muszą opisywać aktualne UI i dokładnie wskazywać, co kliknąć.
- Nie sugerować tworzenia compute przed Catalog i Volume. W Free Edition użytkownik wybiera Serverless w notebooku.
- Notebooky mają używać stałych ścieżek i nazw zasobów. Widgety są niepożądane.
- Jeśli brakuje istotnej informacji, należy pytać zamiast wymyślać konfigurację lub dane.
- Nie usuwać istniejących artefaktów ani nie nadpisywać zmian niezwiązanych z zadaniem.
- Materiały szkoleniowe mogą być fikcyjne, ale muszą być wyraźnie oznaczone jako testowe.
- Po zmianie generatora PDF należy wygenerować plik i sprawdzić liczbę stron. Po zmianie notebooka należy sprawdzić jego format, zależności i kolejność komórek.

## 3. Moduł rag_agent

### Zawartość lokalna

- documents/ zawiera 10 anglojęzycznych, fikcyjnych artykułów PDF o robotyce, każdy po 3 strony.
- Tematy: everyday robotics, robot senses, motion and actuators, mobile robots, collaborative robots, warehouse/logistics robotics, robotics and AI, robot arms, safety and ethics oraz future robotics.
- Każdy PDF zawiera mockowy tekst edukacyjny, nagłówki, tabelę, wykres z fikcyjnymi danymi, ilustrację i podpis. Dokumenty służą testowaniu parsowania, nie przekazywaniu faktycznej wiedzy technicznej.
- assets/illustrations/ zawiera 10 unikalnych ilustracji w ciepłej, akwarelowej estetyce animacyjnej. Ilustracja 07_robotics_and_ai.png jest używana jako tło raportów.
- scripts/generate_robotics_pdfs.mjs odtwarza PDF-y, a scripts/validate_robotics_assets.mjs waliduje ich strukturę.
- README.md zawiera instrukcję dla Databricks Free Edition.
- sprawozdanie_modulu_rag_agent.pdf jest wcześniejszym raportem modułowym.

### Stała konfiguracja Databricks

~~~
catalog = "workspace"
schema = "default"

source_documents_path = "/Volumes/workspace/default/robotics_files"
python_rendered_pages_path = "/Volumes/workspace/default/robotics_files/parsed_pages/python"
sql_rendered_pages_path = "/Volumes/workspace/default/robotics_files/parsed_pages/sql"

parsed_delta_table = "workspace.default.robotics_parsed_documents"
chunked_delta_table = "workspace.default.robotics_document_chunks"
docs_table = "workspace.default.docs_chunked"

ai_search_endpoint = "robotics_ai_search_endpoint"
ai_search_index = "workspace.default.robotics_document_chunks_index"
embedding_model_endpoint = "databricks-gte-large-en"
~~~

Użytkownik ma katalog workspace, a nie workshop. Nie zmieniać tych nazw na widgety ani inny katalog domyślny.

### Notebooki i kolejność

1. 01_parse_robotics_documents.py
   - Czyta PDF-y binarnie z Volume.
   - Parsuje je przez Python i pyspark.sql.functions.ai_parse_document.
   - Parsuje je oddzielnie w SQL przez ai_parse_document.
   - Wyświetla metadane obu wyników i renderuje jeden wynik przez lokalny includes/document_renderer.py.
   - Zapisuje wyłącznie wynik parsowania Pythonowego do workspace.default.robotics_parsed_documents.
   - Parser korzysta ze schema version 2.0, imageOutputPath oraz opisów figur.
   - Nie wolno ponownie wprowadzić niezbindowanego parametru :source_documents_path w SQL. Wcześniej powodował błąd UNBOUND_SQL_PARAMETER; ścieżka musi być poprawnym literałem SQL albo wartością przygotowaną wcześniej przez Python.

2. 02_chunking.py
   - Czyta wynik Delta z notebooka 01.
   - Czyści JSON do Markdown przez LLM databricks-gpt-oss-20b. Zachowuje nagłówki, tabele i podpisy, a strony oddziela przez == page ==.
   - Tworzy też wariant prostego tekstu bez semantyki z tym samym separatorem.
   - Dzieli tekst przez RecursiveCharacterTextSplitter z chunk_size=2000 i chunk_overlap=200.
   - Zapisuje wynik do workspace.default.robotics_document_chunks.

3. 03_vector_search.py
   - Tworzy workspace.default.docs_chunked z tabeli chunków, jeśli tabela nie istnieje, i włącza Change Data Feed.
   - Tworzy embedding pytania przez mlflow.deployments.get_deploy_client("databricks") oraz databricks-gte-large-en.
   - Korzysta z Databricks SDK i AI Search, aby utworzyć endpoint oraz Delta Sync index z managed embeddings.
   - Wykonuje semantic/query, hybrid, full-text oraz filtrowane wyszukiwanie po realnej ścieżce dokumentu.
   - Zawiera ostatni blok rerankingu przez DatabricksReranker.

4. 04_building_and_logging.py
   - Zawiera instrukcje AI Playground.
   - Włącza mlflow.langchain.autolog().
   - Tworzy agenta LangChain z AI Search, testuje go i opisuje przegląd trace'a.
   - Tworzy obok notebooka agent.py oraz agent_config.yaml.
   - Loguje agenta do MLflow i rejestruje workspace.default.robotics_rag_agent w Unity Catalog.

5. 05_building_assistant.py
   - Wyświetla metadane PDF-ów z /Volumes/workspace/default/robotics_files.
   - Zawiera instrukcje UI utworzenia Knowledge Assistant ze źródłem Files in a Volume.
   - Zawiera gotowe teksty angielskie: nazwę, opis, opis źródła, instrukcje i testowy prompt.
   - Zawiera instrukcje Examples / Guidelines na fikcyjnym przykładzie robota Kratos.

### Doświadczenia i ograniczenia modułu RAG

- Tabele Delta tworzą się automatycznie przy pierwszym zapisie notebooków. Nie trzeba tworzyć ich ręcznie, ale wymagane są uprawnienia USE CATALOG, USE SCHEMA, CREATE TABLE oraz odczyt/zapis Volume.
- vs_endpoint_1 z kursu to zarządzany endpoint AI Search, wcześniej nazywany Vector Search. Nie jest tabelą ani endpointem modelu. W aktualnym UI jest w Compute → AI Search.
- Użytkownik utworzył endpoint robotics_ai_search_endpoint ręcznie w UI. Ma mieć status READY albo ONLINE.
- Po utworzeniu indeksu Delta Sync występował stan PROVISIONING_ENDPOINT. Należy poczekać kilka minut na provisioning. Jeśli indeks ma status ONLINE, lecz poprzedni blok synchronizacji zwrócił błąd "index is not ready", należy uruchomić blok lub notebook jeszcze raz.
- Reranking z notebooka 03 nie zadziałał: feature był włączony, ale konfiguracja workspace blokowała dostęp do modelu rerankera. Wymaga to konfiguracji administratora workspace lub wsparcia Databricks. W bieżącej Free Edition należy traktować reranking jako niedostępny.
- Knowledge Assistant nie jest dostępny w bieżącej Databricks Free Edition. Notebook 05 zawiera instrukcje, ale etap UI Test your agent nie został potwierdzony. Synchronizacja materiałów z Volume nie powiodła się; możliwy jest limit Free Edition, ograniczenie usługi lub problem workspace, ale przyczyna nie została definitywnie potwierdzona.
- Dostępność modeli była zmienna. databricks-gpt-oss-120b i modele GPT miały problemy lub timeout. Notebook 04 ma obecnie databricks-meta-llama-3-3-70b-instruct. Inkling przez krótki czas działał w Playground, lecz później przestał być dostępny.

## 4. Moduł single_agent_app

### Zawartość lokalna i dane

- data/sf_airbnb_listings.csv jest darmowym snapshotem ofert Airbnb z San Francisco, używanym jako dane testowe.
- README wskazuje źródło: publiczne repozytorium San-Francisco-AirBnB-Analysis na licencji MIT, z danymi opartymi na Inside Airbnb. README podaje też opcjonalne nowsze źródło Inside Airbnb.
- Dane należy wgrać do managed Volume workspace.default.sf_airbnb_data pod ścieżką:

~~~
/Volumes/workspace/default/sf_airbnb_data/sf_airbnb_listings.csv
~~~

- Notebook 06 tworzy lub nadpisuje tabelę Delta:

~~~
workspace.default.sf_airbnb_listings
~~~

### Notebooki i kolejność

1. 06_building_uc_functions.py
   - Instaluje unitycatalog-ai[databricks] i dopiero potem restartuje Python.
   - Definicje obiektów oraz konfiguracja znajdują się po restarcie, aby nie trzeba było uruchamiać komórki drugi raz.
   - Czyta CSV i bezpiecznie przetwarza kolumnę price przy użyciu try_cast, aby wartości takie jak Private room nie powodowały błędu CAST_INVALID_INPUT.
   - Tworzy tabelę Delta oraz funkcję SQL do średniej ceny.
   - Tworzy i testuje funkcje Unity Catalog, w tym Pythonową funkcję formatującą dane oferty dla agenta.
   - Python UDF w Unity Catalog nie może bezpośrednio czytać Delta table przez spark.sql. Odczyt po listing_id realizuje funkcja SQL, a Python UDF formatuje przekazane pola.

2. 07_building_agent.py
   - Na nowo definiuje wszystkie niezbędne obiekty, mimo że notebook 06 był wykonany.
   - Wyświetla pięć rekordów tabeli Airbnb.
   - Tworzy DatabricksFunctionClient, listę funkcji oraz UCFunctionToolkit.
   - Zapisuje JSON konfiguracji agenta w Volume.
   - Buduje agenta LangChain z endpointem databricks-meta-llama-3-3-70b-instruct.
   - Zależności zostały przypięte, aby obejść błędy ExecutionInfo i importu AgentExecutor. AgentExecutor należy importować z langchain_classic.agents, a nie ze starego langchain.agents.

3. 08_mlflow_tracing.py
   - Czyta tabelę, tworzy konfigurację i listę narzędzi.
   - Uruchamia mlflow.langchain.autolog().
   - Pokazuje poprawne lokalizacje eksperymentów Workspace i artefaktów w Volume.
   - Testuje agenta, opisuje kontrolę trace'ów w UI i zawiera przykład własnej lokalizacji trace'ów w Unity Catalog.

4. 09_tagging.py
   - Ponownie ładuje obiekty agenta i wprowadza tagi do trace decoratora.
   - Waliduje długość prompta.
   - Tworzy demo_agent2.py oraz JSON config w Volume, bez oczekiwania na wcześniej istniejący demo_agent.py.
   - Loguje agenta jako MLflow pyfunc, zapisuje model_uri, rejestruje model workspace.default.airbnb_demo_agent w Unity Catalog i ponownie go ładuje.

### Stałe ustawienia i ograniczenia

~~~
catalog = "workspace"
schema = "default"
airbnb_table = "workspace.default.sf_airbnb_listings"
llm_endpoint = "databricks-meta-llama-3-3-70b-instruct"
uc_model_name = "workspace.default.airbnb_demo_agent"
~~~

- Typowe uprawnienia: USE CATALOG, USE SCHEMA, CREATE VOLUME, READ VOLUME, CREATE TABLE, CREATE FUNCTION, EXECUTE oraz CREATE MODEL w workspace.default.
- Moduł i instrukcja są aktualne oraz zweryfikowane na 23.07.2026.
- Z uwagi na prostszy przepływ nie wystąpiły problemy z limitami Databricks Free Edition.
- Jeśli Free Edition zwróci błąd Cannot access Spark Connect przy DatabricksFunctionClient, jest to ograniczenie dostępności usługi w workspace, a nie problem z CSV.

## 5. Rozpoczęty moduł genai_eval_and_monitor

- Folder: genai_eval_and_monitor/.
- Inspiracja: kurs Generative AI Application Evaluation and Governance.
- Pierwszy notebook: notebooks/10_exploring_datasets.py.
- Notebook jest po angielsku i zawiera dwie niezależne sekcje:
  1. znalezienie datasetu Amazon Products od Bright Data, przegląd aktualnych warunków i import;
  2. znalezienie datasetu Personal Income od Rearc, przegląd aktualnych warunków i import.
- Import odbywa się ręcznie przez Marketplace UI, ponieważ użytkownik musi zaakceptować bieżące warunki dostawcy. Notebook nie zgaduje typu licencji ani nie zastępuje importu lokalnym plikiem.
- Import został wykonany w domyślnym środowisku Marketplace. Notebook weryfikuje read-only shared catalogs bright_data_amazon_dataset i rearc_personal_income_fred, a następnie wyświetla po pięć rekordów z tabel datasets.amazon_best_seller_products oraz fred.fred_pi.
- Bright Data ma również w schema datasets tabele amazon_products i amazon_reviews. Jeśli podana nazwa katalogu nie istnieje, notebook zwraca jasny błąd z krokiem Marketplace → My requests → Installed data products → View data.
- Wymagania Marketplace: Unity Catalog i co najmniej USE MARKETPLACE ASSETS; zależnie od konfiguracji mogą być potrzebne CREATE CATALOG, USE PROVIDER lub pomoc administratora Marketplace/metastore.
- Drugi notebook: notebooks/11_guardrails.py. Zawiera przykłady odmowy nielegalnego żądania, celowo pustą odpowiedź w przykładzie z fikcyjnym uzasadnieniem, system prompt ograniczający asystenta do Databricks oraz dwa wywołania Meta Llama 3.3 70B Instruct. Pierwsze używa WorkspaceClient i ChatMessage, a drugie używa klienta OpenAI, base_url kończącego się na /serving-endpoints oraz natywnego Databricks extra_body={"enable_safety_filter": True}. Jeśli endpoint nie obsługuje filtra, notebook nie powinien usuwać go po cichu.
- Trzeci notebook: notebooks/12_implementing_guardrails.py. Zawiera instrukcję instalacji Llama Guard Model z Marketplace i utworzenia endpointu w UI, domyślną nazwę endpointu llama-guard, wspólne stringi legalnego i nielegalnego promptu, krótką oraz rozszerzoną taksonomię kategorii unsafe, payload [INST] oraz zapytania przez mlflow.deployments. Integracja z Meta Llama 3.3 70B Instruct sprawdza prompt jako User przed wywołaniem modelu i odpowiedź jako Agent po wywołaniu. Endpoint Llama Guard może wymagać GPU/provisioned capacity i nie musi być dostępny w Free Edition.
- Czwarty notebook: notebooks/13_benchmark_evaluation.py. Porównuje system streszczania na databricks-meta-llama-3-3-70b-instruct z challengerem databricks-dbrx-instruct. Wymaga pliku /Volumes/workspace/default/genai_eval_data/news-summarization.csv z kolumnami input oraz output. Gotowy plik lokalny znajduje się w genai_eval_and_monitor/data/news-summarization.csv; został utworzony z 302 par article/summary z writer_summaries.json pobranego z repozytorium autora. Generator genai_eval_and_monitor/scripts/prepare_news_summarization_eval_data.mjs pozwala odtworzyć pobranie i konwersję. Używa klasycznego mlflow.evaluate pod aliasem mlflow_evaluate i ROUGE-1, czyli ROUGE-N dla n=1, aby zachować przepływ historycznego kursu. Paper 2301.13848 dotyczy news summarization, a demonstracyjny prompt kursowy dotyczy recenzji produktów spożywczych — nie należy przedstawiać dowolnego CSV z recenzjami jako oryginalnych danych artykułu.

## 6. Raporty PDF

### Raporty modułowe

- rag_agent/sprawozdanie_modulu_rag_agent.pdf — raport 2-stronicowy; weryfikacja 22.07.2026.
- single_agent_app/sprawozdanie_modulu_single_agent_app.pdf — raport 2-stronicowy; weryfikacja 23.07.2026.

### Raport zbiorczy

- Plik: sprawozdanie_modulow_rag_agent_i_single_agent_app.pdf.
- Generator: scripts/generate_combined_modules_report.mjs.
- Raport ma 4 strony A4 i można go odtworzyć poleceniem:

~~~
node scripts\generate_combined_modules_report.mjs
~~~

- Generator korzysta z pdfkit i pdf-lib z rag_agent/node_modules, osadza C:\Windows\Fonts\segoeui.ttf oraz C:\Windows\Fonts\segoeuib.ttf i używa rag_agent/assets/illustrations/07_robotics_and_ai.png jako pełnostronicowego tła przyciętego metodą cover.
- Styl raportu: półprzezroczyste białe panele, neutralne szarości (#4B5563 dla tekstu, #374151 dla nagłówków, #6B7280 dla tekstu pomocniczego) oraz stonowany szaroniebieski dla akcentów.
- Ostatnie korekty raportu:
  - single_agent_app jest inspirowany kursem Building Single-Agent Applications on Databricks;
  - w sekcji materiałów są odtwarzalne artykuły PDF, nie artefakty PDF;
  - ograniczenia modeli wskazują krótkotrwałą dostępność Inklinga, późniejszy brak Inklinga, timeouty GPT i użycie Meta Llama 3.3 70B Instruct;
  - ocena materiałów jest rozdzielona: pierwszy kurs był praktyczny i dobrze tłumaczył decyzje, drugi był mniej przystępny i przeładowany buzzwordami oraz nazwami własnymi.

## 7. Stan weryfikacji i granice twierdzeń

- Nie wolno twierdzić, że usługi niedostępne w bieżącej Free Edition zostały przetestowane. Dotyczy to szczególnie Knowledge Assistant i rerankingu.
- Notebooki oraz instrukcje rag_agent były weryfikowane na 22.07.2026, a single_agent_app na 23.07.2026.
- Generator zbiorczego raportu został uruchomiony lokalnie po ostatnich zmianach i sprawdza liczbę stron przez pdf-lib.
- Przy aktualizacji notebooka należy zmieniać raport tylko wtedy, gdy zmienia się opisany przepływ, stan weryfikacji albo ograniczenie.

## 9. Aktualizacja modułu genai_eval_and_monitor — 24.07.2026

- `notebooks/13_benchmark_evaluation.py`: nieistniejący endpoint `databricks-dbrx-instruct` zastąpiono aktualnym `databricks-gpt-oss-20b`. Baseline pozostaje `databricks-meta-llama-3-3-70b-instruct`; run challengera ma nazwę `news_summarization_challenger_gpt_oss_20b`. GPT-OSS może zwrócić wiadomość jako listę części `content`, więc obie funkcje streszczające używają `extract_response_text(...)`, która normalizuje string oraz listę części do zwykłego tekstu.
- Dodano `notebooks/14_llm_as_a_judge.py`. Definiuje `query_chatbot_system` na endpointcie Meta Llama 3.3 70B Instruct oraz klasyczną metrykę MLflow `professionalism` z `EvaluationExample` i skalą od 1 do 5. Model sędziego jest przekazany jako `endpoints:/databricks-meta-llama-3-3-70b-instruct`; agregacje to `mean` oraz `variance`.
- Notebook 14 uruchamia trzy przykładowe prompty (casual, neutral, formal), zapisuje wynik do eksperymentu `/Shared/genai_eval_and_monitor_llm_as_judge` i wyjaśnia w komórce Markdown, gdzie w UI odczytać metryki zbiorcze oraz wyniki per-row. Kończy się listą praktyk LLM-as-a-judge.

## 10. Raporty genai_eval_and_monitor — 24.07.2026

- Dodano `genai_eval_and_monitor/scripts/generate_module_report.mjs` oraz wygenerowany nim dwustronicowy PDF `genai_eval_and_monitor/sprawozdanie_modulu_genai_eval_and_monitor.pdf`.
- Raport opisuje dataset `news-summarization.csv` (302 pary tekst–referencyjne streszczenie), cztery notebooki wykonawcze 11–14 i instrukcyjny notebook 10. Zaznacza, że pełny etap notebooka 12 jest zablokowany, ponieważ Free Edition nie pozwala utworzyć endpointu Llama Guard.
- Zaktualizowano `scripts/generate_combined_modules_report.mjs` i istniejący PDF `sprawozdanie_modulow_rag_agent_i_single_agent_app.pdf`. Raport ma teraz 5 stron i obejmuje trzy moduły, z osobną stroną dla `genai_eval_and_monitor`; generator weryfikuje liczbę stron przez pdf-lib.
- Oba generatory używają tej samej ilustracji tła robotyki, krojów Segoe UI i neutralnej palety szarości.

## 11. Rozpoczęty moduł genai_deploy_and_monitor — 27.07.2026

- Folder `genai_deploy_and_monitor/` zawiera notebook `notebooks/15_batch_inference.py` i polską instrukcję `README.md`.
- Notebook tworzy `workspace.default.xsum_summaries` z próbką 100 rekordów publicznego datasetu `EdinburghNLP/xsum`, buduje pipeline Hugging Face `t5-small`, loguje go z `infer_signature` i `model_config`, testuje jako pyfunc, rejestruje go jako `workspace.default.xsum_t5_small_summarizer` oraz przypisuje alias `@champion`.
- Następnie notebook tworzy custom Model Serving endpoint `xsum-t5-small-summarizer-endpoint` dla rozwiązanego numeru wersji `@champion` i wykonuje SQL batch inference przez `ai_query`, zapisując wynik do `workspace.default.xsum_t5_batch_predictions`.
- `README.md` opisuje wymagania Hugging Face, Unity Catalog, Model Serving oraz Serverless/DBR 18.2+ dla `ai_query`. Custom Model Serving może nie być dostępny albo być limitowany w Free Edition; bez endpointu sekcja 8 nie zadziała, ale sekcje 1–6 pozostają użyteczne.
- Aktualizacja notebooka 15: sekcja 1 nie używa już `datasets.load_dataset`, ponieważ w Databricks runtime wystąpił konflikt `datasets`/`huggingface_hub` (`HfFileSystem.find() got multiple values for maxdepth`) oraz warning o cache w `/tmp`. Pobieranie próbki XSum odbywa się teraz przez publiczne API `https://datasets-server.huggingface.co/rows`; `datasets` usunięto z zależności, więc cache w `/tmp` nie jest tworzony.

- Dodano `genai_deploy_and_monitor/notebooks/16_deploying_llm_chain.py`: prosty LangChain RAG chain nad istniejącym indeksem `workspace.default.robotics_document_chunks_index`, logowanie i rejestracja w Unity Catalog oraz tworzenie/aktualizacja endpointu `robotics-rag-deployment-endpoint`. Notebook zawiera sekret scope, `WorkspaceClient`, scale-to-zero, environment variables, legacy auto-capture inference tables, alternatywną metodę UI, inferencję przez SDK i MLflow Deployments oraz instrukcję UI dla tabel inference.
- Dodano `genai_deploy_and_monitor/notebooks/17_online_monitoring.py`: przetwarza rzeczywistą tabelę `workspace.default.robotics_rag_inference_payload`, rozpakowuje payloady, oblicza toxicity, perplexity i readability w trybie incremental streaming i zapisuje `workspace.default.robotics_rag_processed_inference`. Tworzy lub weryfikuje monitor Time Series z pięciominutową granularnością przez aktualne API `WorkspaceClient.data_quality`, czeka na refresh oraz pokazuje profile i drift metric tables. Notebook wymaga włączonej AI Gateway inference table dla endpointu 16.

## 8. Instrukcja dla kolejnego agenta

1. Najpierw przeczytaj właściwy README.md i notebook, którego dotyczy zgłoszenie.
2. Zachowaj stałe nazwy workspace.default oraz ścieżki Volume opisane w tym pliku.
3. Przy problemach z Databricks sprawdzaj kolejno: dostępność usługi, status endpointu lub indeksu, uprawnienia Unity Catalog, wersje pakietów i dostępność endpointu modelu.
4. Nie zastępuj wymaganej usługi Databricks lokalnym odpowiednikiem, jeśli użytkownik oczekuje konkretnej funkcji kursowej, np. AI Search lub ai_parse_document.
5. Jeżeli modyfikujesz raport PDF, edytuj generator, uruchom go i zachowaj neutralny styl typograficzny.
