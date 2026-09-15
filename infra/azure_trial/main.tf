resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  name         = "${var.prefix}-${random_string.suffix.result}"
  storage_name = "${var.prefix}uc${random_string.suffix.result}"
  uc_container = "unity-catalog"
  uc_root_url  = "abfss://${local.uc_container}@${azurerm_storage_account.uc.name}.dfs.core.windows.net/"
}

resource "azurerm_resource_group" "this" {
  name     = "rg-${local.name}"
  location = var.location
  tags     = var.tags
}

# --- Azure Databricks workspace: Trial = Premium features with free DBUs for 14 days ---

resource "azurerm_databricks_workspace" "this" {
  name                        = "dbw-${local.name}"
  resource_group_name         = azurerm_resource_group.this.name
  location                    = azurerm_resource_group.this.location
  sku                         = "trial"
  managed_resource_group_name = "rg-${local.name}-managed"
  tags                        = var.tags
}

# --- ADLS Gen2 as managed storage for the workshop catalog ---

resource "azurerm_storage_account" "uc" {
  name                            = local.storage_name
  resource_group_name             = azurerm_resource_group.this.name
  location                        = azurerm_resource_group.this.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  account_kind                    = "StorageV2"
  is_hns_enabled                  = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true
  tags                            = var.tags
}

resource "azurerm_storage_container" "uc" {
  name                  = local.uc_container
  storage_account_id    = azurerm_storage_account.uc.id
  container_access_type = "private"
}

resource "azurerm_databricks_access_connector" "uc" {
  name                = "dbac-${local.name}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}

# Read/write data, plus the roles Databricks needs to set up file events on its own.
resource "azurerm_role_assignment" "uc_blob" {
  scope                = azurerm_storage_account.uc.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.uc.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uc_queue" {
  scope                = azurerm_storage_account.uc.id
  role_definition_name = "Storage Queue Data Contributor"
  principal_id         = azurerm_databricks_access_connector.uc.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uc_account" {
  scope                = azurerm_storage_account.uc.id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azurerm_databricks_access_connector.uc.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uc_eventgrid" {
  scope                = azurerm_resource_group.this.id
  role_definition_name = "EventGrid EventSubscription Contributor"
  principal_id         = azurerm_databricks_access_connector.uc.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

# Entra ID role assignments take a moment to propagate; without the wait the
# storage credential validation fails on the first apply.
resource "time_sleep" "rbac_propagation" {
  create_duration = "90s"

  depends_on = [
    azurerm_role_assignment.uc_blob,
    azurerm_role_assignment.uc_queue,
    azurerm_role_assignment.uc_account,
    azurerm_role_assignment.uc_eventgrid,
  ]
}

# --- Cost guard: trial DBUs are free, Azure resources and usage after day 14 are not ---

resource "azurerm_consumption_budget_resource_group" "this" {
  count = var.budget_amount > 0 && length(var.budget_emails) > 0 ? 1 : 0

  name              = "budget-${local.name}"
  resource_group_id = azurerm_resource_group.this.id
  amount            = var.budget_amount
  time_grain        = "Monthly"

  time_period {
    start_date = formatdate("YYYY-MM-01'T'00:00:00Z", plantimestamp())
  }

  notification {
    threshold      = 50
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = var.budget_emails
  }

  notification {
    threshold      = 80
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = var.budget_emails
  }

  notification {
    threshold      = 100
    operator       = "GreaterThan"
    threshold_type = "Forecasted"
    contact_emails = var.budget_emails
  }

  lifecycle {
    ignore_changes = [time_period]
  }
}
