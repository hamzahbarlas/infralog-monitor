# ── Resource Group ───────────────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# ── Storage Account ──────────────────────────────────────────
resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    project     = "infralog-monitor"
    environment = "dev"
  }
}

# ── Blob Container ───────────────────────────────────────────
resource "azurerm_storage_container" "main" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# ── Key Vault ────────────────────────────────────────────────
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                = var.key_vault_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get",
      "Set",
      "List",
      "Delete",
      "Purge"
    ]
  }

  tags = {
    project     = "infralog-monitor"
    environment = "dev"
  }
}

# ── Store SendGrid Key in Key Vault ──────────────────────────
resource "azurerm_key_vault_secret" "sendgrid_key" {
  name         = "sendgrid-api-key"
  value        = "placeholder-replace-after-deploy"
  key_vault_id = azurerm_key_vault.main.id
}