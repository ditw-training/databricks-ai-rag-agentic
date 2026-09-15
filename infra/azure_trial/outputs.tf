output "workspace_url" {
  value = "https://${azurerm_databricks_workspace.this.workspace_url}"
}

output "resource_group" {
  value = azurerm_resource_group.this.name
}

output "storage_account" {
  value = azurerm_storage_account.uc.name
}

output "catalog" {
  value = databricks_catalog.workshop.name
}

output "metastore" {
  value = try(data.databricks_current_metastore.this.metastore_info[0].name, null)
}

output "databrickscfg_profile" {
  description = "Paste into ~/.databrickscfg to use the workspace from the Databricks CLI."
  value       = <<-EOT
    [mct]
    host      = https://${azurerm_databricks_workspace.this.workspace_url}
    auth_type = azure-cli
  EOT
}
