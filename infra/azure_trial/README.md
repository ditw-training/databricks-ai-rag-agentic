# Workspace prowadzącego: Azure Databricks Trial + ADLS Gen2

Terraform stawia workspace **Premium** do przygotowania i pokazu warsztatu (`workshop/00_setup/01_trainer_prepare_premium`, `pattern/`, dema Knowledge Assistant, Databricks Apps, MCP). Uczestnicy dalej pracują na Free Edition.

## Co powstaje

| Zasób | Po co |
|---|---|
| Resource group `rg-<prefix>-<suffix>` | wszystko w jednej grupie, `terraform destroy` sprząta całość |
| Workspace Azure Databricks, SKU **`trial`** | funkcje Premium i darmowe DBU przez 14 dni |
| Storage account ADLS Gen2 (HNS) + kontener `unity-catalog` | managed storage katalogu warsztatu |
| Access Connector for Azure Databricks (managed identity) | dostęp Unity Catalog do ADLS bez kluczy i sekretów |
| Role: Storage Blob Data Contributor, Storage Queue Data Contributor, Storage Account Contributor, EventGrid EventSubscription Contributor | odczyt i zapis danych oraz file events konfigurowane przez Databricks |
| Storage credential, external location (izolowane do tego workspace) | połączenie Unity Catalog z ADLS |
| Katalog **`workspace`** z `storage_root` na ADLS | notebooki warsztatu mają `CATALOG = "workspace"`, więc działają bez zmian; na ADLS trafiają też inference tables i trace'y MLflow w Unity Catalog, których nie da się włączyć na default storage |
| Opcjonalnie: współprowadzący jako admini, budżet z alertami e-mail | — |

**Region:** domyślnie `northeurope`. Według tabel „Features with limited regional availability” (stan 09.2026) `northeurope` i `germanywestcentral` mają wszystko, czego używa warsztat, bez routingu między geografiami: `databricks-meta-llama-3-3-70b-instruct`, `databricks-gte-large-en`, AI Search, Knowledge Assistant, Databricks Apps, serwery MCP i `ai_parse_document` v2. **Nie wybieraj** `polandcentral`: nie ma tam Model Serving ani AI Search.

## Wymagania

1. Terraform ≥ 1.9, Azure CLI, Databricks CLI.
2. `az login` do tenanta subskrypcji, potem wybór subskrypcji:

   ```bash
   az account list -o table        # Microsoft MCT / MCT_VSE
   az account set --subscription "Microsoft MCT"
   ```

3. Rola **Owner** (albo Contributor + User Access Administrator) na subskrypcji: Terraform nadaje role managed identity.
4. **Limit wydatków.** Trial Databricks nie działa na subskrypcji typu Azure Free Trial. Dla kont z kredytem dokumentacja każe przejść na pay-as-you-go i zdjąć spending limit. Subskrypcje z miesięczną kwotą (Visual Studio / MCT) mają taki limit, więc jeśli `apply` zatrzyma się na workspace, zdejmij limit albo użyj drugiej subskrypcji.
5. Konto Microsoft (np. outlook.com) jako pierwszy admin: przy pierwszym wejściu do konsoli konta (`accounts.azuredatabricks.net`) musisz być Global Administrator tenanta. Workspace i katalog działają bez tego, konsola konta nie.

## Uruchomienie

```bash
cd infra/azure_trial
cp terraform.tfvars.example terraform.tfvars   # uzupełnij subscription_id
terraform init
terraform plan -out tfplan
terraform apply tfplan
```

Tworzenie workspace'u zajmuje kilka minut. Po `apply`:

```bash
terraform output -raw databrickscfg_profile >> ~/.databrickscfg
python smoke_test.py --profile mct
```

`smoke_test.py` sprawdza tożsamość, katalog na ADLS, oba modele, odpowiedź czatu, zapis tabeli zarządzanej na ADLS, `samples.bakehouse`, `ai_query`, API AI Search i Apps oraz zarządzany serwer MCP. Zakłada i od razu usuwa jedną małą tabelę.

**Kilka kont w Azure CLI.** Provider Databricks pobiera token dla tenanta workspace'u i bierze **domyślne** konto `az`. Jeśli domyślna subskrypcja należy do innego tenanta, dostaniesz `AADSTS50020 ... does not exist in tenant`. Wtedy albo ustaw domyślną subskrypcję (`az account set --subscription "MCT_VSE"`), albo podaj token Entra ID tylko na czas uruchomienia:

```bash
export DATABRICKS_TOKEN=$(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d \
  --subscription "<subscription_id>" --query accessToken -o tsv)   # ważny ok. 1 h
export DATABRICKS_HOST=$(terraform output -raw workspace_url)       # dla smoke_test.py bez --profile
```

Jeśli pierwszy `apply` zakończy się błędem na zasobach `databricks_*` (np. metastore jeszcze nie przypięty do nowego workspace'u), uruchom `terraform apply` ponownie. Zasoby Azure już istnieją, więc drugi przebieg tworzy tylko obiekty Unity Catalog.

## Po `apply`: kroki ręczne

| Krok | Gdzie | Dlaczego ręcznie |
|---|---|---|
| Import repozytorium jako folder Git | Workspace → Create → Git folder | wymaga Twojego połączenia z GitHub |
| Włączenie podglądów: managed MCP servers, Agent Bricks (Knowledge Assistant), ewentualnie AI Search reranker | Settings → Previews | podglądy włącza admin w UI |
| Marketplace: „Simulated Retail Customer Data” | Marketplace → Get instant access | źródło dla `workshop/scripts/prepare_data_premium` |
| Grupy `all_states_analysts`, `compliance_officers`, `payments_team` (opcjonalnie, M4 z dwiema tożsamościami) | konsola konta → User management | `is_account_group_member` sprawdza grupy **konta**, a to wymaga account admina |
| `01_trainer_prepare_premium` → Run all | notebook | tworzy endpoint AI Search, indeksy i funkcje |

## Koszty i koniec triala

- Trial pokrywa **DBU** przez 14 dni. Storage account, ruch sieciowy i ewentualne VM klasycznych klastrów są rozliczane w subskrypcji od pierwszego dnia (dla warsztatu to grosze: wszystko jest serverless).
- **Po 14 dniach workspace przechodzi na płatne DBU Premium.** Jeśli nie jest potrzebny, zrób `terraform destroy`. Zapisz datę `apply` w kalendarzu.
- Endpoint AI Search nalicza koszt także bez zapytań. Po próbie uruchom `workshop/00_setup/02_trainer_teardown` albo `terraform destroy`.
- Ustaw `budget_emails`, żeby dostać alert przy 50% i 80% budżetu oraz przy prognozie 100%.

## Sprzątanie

```bash
terraform destroy
```

Katalog, external location i credential mają `force_destroy = true`, więc usuwane są razem z danymi. Managed resource group workspace'u Azure usuwa sama.
