# `genai_deploy_and_monitor_v2` — wariant offline

Ten moduł jest testowym, samodzielnym odpowiednikiem części kursu dotyczącej batch inference, wdrażania modelu i monitoringu. Cel dydaktyczny pozostaje ten sam: przygotowanie danych, zapis modelu w MLflow i Unity Catalog, wykonanie predykcji, zapis logów oraz analiza metryk.

Nie jest to jednak wdrożenie produkcyjnego endpointu. W szczególności moduł **nie tworzy** Model Serving endpointu, AI Gateway, AI Search, tokenów, secret scope ani nie wymaga Databricks CLI lub działań poza interfejsem Databricks.

## Co zastępuje ten wariant

| Oryginalna funkcja | Wariant offline |
| --- | --- |
| Model Serving endpoint | Model PyFunc ładowany lokalnie z Unity Catalog |
| AI Gateway inference table | Tabela Delta z własnymi logami żądań i odpowiedzi |
| Capture ruchu online | Powtarzalny mikro-batch zapisujący logi |
| Time Series monitor | Tabele profilu i driftu oraz wykresy w notebooku |

Z tego powodu nie można nim sprawdzić routingu traffic, stanu endpointu, automatycznego AI Gateway capture ani prawdziwego monitoringu ruchu online. Można natomiast przećwiczyć pozostały przepływ bez ograniczeń związanych z endpointami Free Edition.

## Wymagania

- Databricks Free Edition lub inny workspace z Serverless i Unity Catalog.
- Uprawnienia do tworzenia tabel Delta i modelu w `workspace.default`. Do rejestracji modelu potrzebne jest `CREATE MODEL`; do ustawienia aliasu `@champion` — własność modelu; do jego użycia — `EXECUTE`.
- Dostęp internetowy środowiska do publicznego Hugging Face. Pierwsze uruchomienie pobiera próbkę XSum, `t5-small` oraz modele metryk; może potrwać kilka minut.

Nie potrzebujesz endpointu, tokenu, sekretu ani własnego komputera poza przeglądarką.

## Uruchomienie

1. W Databricks otwórz **Workspace** i zaimportuj trzy pliki z folderu `notebooks/` jako notebooki źródłowe Python.
2. Uruchom notebook `15_offline_batch_inference` od góry do dołu. Tworzy on dane XSum, pobiera jednorazowo model do tymczasowego dysku Serverless, zapisuje samowystarczalny model `workspace.default.xsum_t5_small_summarizer_v2` oraz tworzy batch predykcji.
3. Uruchom `16_local_model_workflow`. Ładuje on wersję `@champion` z Unity Catalog i zapisuje lokalne logi do `workspace.default.offline_inference_payload_v2`.
4. Uruchom `17_offline_monitoring`. Notebook przetworzy nowe logi i utworzy tabele przetworzonych wyników, profilu pięciominutowego oraz driftu.

Wszystkie notebooki używają stałego katalogu `workspace` i schematu `default`. Pierwsze komórki sprawdzają, czy poprzednie dane już istnieją; ponowne uruchomienie nie powinno ponownie pobierać XSum ani duplikować logów.

## Tabele tworzone przez moduł

- `workspace.default.xsum_summaries_v2`
- `workspace.default.xsum_t5_batch_predictions_v2`
- `workspace.default.offline_inference_payload_v2`
- `workspace.default.offline_processed_inference_v2`
- `workspace.default.offline_inference_profile_5m_v2`
- `workspace.default.offline_inference_drift_5m_v2`

Pierwszy notebook pobiera aktualny snapshot `google-t5/t5-small` oraz wariant CPU biblioteki PyTorch, ponieważ Serverless może nie mieć silnika do uruchamiania modeli. Pobieranie używa tymczasowego dysku `/local_disk0`, z wyłączonym Hugging Face Xet/CAS. Po pierwszym poprawnym uruchomieniu model znajduje się jako artefakt MLflow w Unity Catalog; kolejne uruchomienia 15 wykorzystują alias `@champion` zamiast ponownie pobierać model z Hugging Face. Jeśli pierwsze pobranie nadal nie powiedzie się, przyczyną jest dostęp bieżącej sesji Serverless do publicznego Hub, a nie endpoint Databricks.

## Zgodność z aktualnym Free Edition

Moduł korzysta wyłącznie z notebooków Serverless, Delta, Unity Catalog i MLflow. Nie tworzy endpointów, AI Gateway, AI Search, sekretów ani nie wymaga CLI. Databricks Free Edition działa wyłącznie na Serverless i nie gwarantuje dostępności zewnętrznych usług, dlatego publiczny Hugging Face pozostaje jedyną zależnością spoza workspace. Rejestr modeli Unity Catalog, aliasy modeli oraz ładowanie `models:/...@champion` są obsługiwane przez aktualny MLflow 3.

Źródła: [Free Edition limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations), [Unity Catalog model lifecycle](https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle), [MLflow PythonModel](https://mlflow.org/docs/latest/ml/model/python_model/), [Hugging Face environment variables](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables).
