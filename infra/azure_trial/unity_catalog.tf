# New Azure workspaces are attached to the regional Unity Catalog metastore
# automatically, and workspace admins may create credentials, locations and catalogs.
data "databricks_current_metastore" "this" {
  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_storage_credential" "uc" {
  name    = "${var.prefix}_adls_credential"
  comment = "SQLDay workshop: access connector ${azurerm_databricks_access_connector.uc.name}"

  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.uc.id
  }

  isolation_mode = "ISOLATION_MODE_ISOLATED"
  force_destroy  = true

  depends_on = [time_sleep.rbac_propagation, data.databricks_current_metastore.this]
}

resource "databricks_external_location" "uc" {
  name               = "${var.prefix}_adls_root"
  url                = local.uc_root_url
  credential_name    = databricks_storage_credential.uc.name
  comment            = "SQLDay workshop: managed storage for catalog ${var.catalog_name}"
  isolation_mode     = "ISOLATION_MODE_ISOLATED"
  enable_file_events = true
  force_destroy      = true

  # Databricks creates and manages the storage queue in this resource group.
  file_event_queue {
    managed_aqs {
      resource_group  = azurerm_resource_group.this.name
      subscription_id = var.subscription_id
    }
  }

  depends_on = [azurerm_storage_container.uc]
}

# Managed tables, volumes, AI Search sources, inference tables and MLflow traces in
# Unity Catalog all land on ADLS instead of the workspace default storage.
resource "databricks_catalog" "workshop" {
  name           = var.catalog_name
  storage_root   = "${local.uc_root_url}${var.catalog_name}"
  comment        = "SQLDay Lite: Od pytania do agenta (trainer workspace)"
  isolation_mode = "ISOLATED"
  force_destroy  = true

  properties = {
    purpose = "workshop"
  }

  depends_on = [databricks_external_location.uc]
}

# A catalog created through the API has no `default` schema, and the notebooks use it.
resource "databricks_schema" "default" {
  catalog_name  = databricks_catalog.workshop.name
  name          = "default"
  comment       = "SQLDay workshop objects"
  force_destroy = true
}

# --- Co-trainers ---

data "databricks_group" "admins" {
  display_name = "admins"
  depends_on   = [azurerm_databricks_workspace.this]
}

resource "databricks_user" "trainer" {
  for_each  = toset(var.trainer_emails)
  user_name = each.value
}

resource "databricks_group_member" "trainer_admin" {
  for_each  = databricks_user.trainer
  group_id  = data.databricks_group.admins.id
  member_id = each.value.id
}

resource "databricks_grants" "catalog" {
  count   = length(var.trainer_emails) > 0 ? 1 : 0
  catalog = databricks_catalog.workshop.name

  dynamic "grant" {
    for_each = toset(var.trainer_emails)
    content {
      principal  = grant.value
      privileges = ["ALL_PRIVILEGES"]
    }
  }

  depends_on = [databricks_user.trainer]
}
