variable "resource_group_name" {
  description = "Name of the Azure resource group"
  default     = "infralog-monitor-rg"
}

variable "location" {
  description = "Azure region to deploy resources"
  default     = "East US"
}

variable "storage_account_name" {
  description = "Name of the Azure storage account (must be globally unique, lowercase, no hyphens)"
  default     = "infraloglogs"
}

variable "container_name" {
  description = "Name of the blob container"
  default     = "infralog-archive"
}

variable "key_vault_name" {
  description = "Name of the Azure Key Vault (must be globally unique)"
  default     = "infralog-kv"
}