terraform {
  required_version = ">= 1.9"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.5"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.132"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.9"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.14"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# The workspace provider is configured from the workspace created in the same run.
# Auth is auto-detected: Azure CLI by default, or an Entra ID token in DATABRICKS_TOKEN
# when the CLI's default account belongs to another tenant (see README).
provider "databricks" {
  host = "https://${azurerm_databricks_workspace.this.workspace_url}"
}
