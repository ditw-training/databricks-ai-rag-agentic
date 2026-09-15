variable "subscription_id" {
  description = "Azure subscription for the trial workspace (az account list -o table)."
  type        = string
}

variable "location" {
  description = "Azure region. northeurope and germanywestcentral serve Llama 3.3 70B, gte-large-en, AI Search, Knowledge Assistant, Apps and MCP without cross-geo routing."
  type        = string
  default     = "northeurope"
}

variable "prefix" {
  description = "Short lowercase prefix for resource names (letters and digits, max 10)."
  type        = string
  default     = "sqldayai"

  validation {
    condition     = can(regex("^[a-z][a-z0-9]{1,9}$", var.prefix))
    error_message = "prefix: lowercase letters and digits, 2-10 characters, starting with a letter."
  }
}

variable "catalog_name" {
  description = "Unity Catalog catalog on ADLS. The workshop notebooks use CATALOG = \"workspace\", so the default keeps them unchanged."
  type        = string
  default     = "workspace"
}

variable "trainer_emails" {
  description = "Co-trainers added as workspace admins with ALL PRIVILEGES on the workshop catalog. The account running terraform is admin already."
  type        = list(string)
  default     = []
}

variable "budget_amount" {
  description = "Monthly cost alert for the resource group, in the subscription currency. 0 disables the budget."
  type        = number
  default     = 50
}

variable "budget_emails" {
  description = "Recipients of budget alerts (50%, 80% actual and 100% forecast)."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags applied to every Azure resource."
  type        = map(string)
  default = {
    project = "sqlday-lite-agentic-ai"
    purpose = "workshop-trial"
  }
}
