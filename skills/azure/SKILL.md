---
name: azure
description: Azure resource management for data engineering — storage, Data Factory, Synapse, Key Vault, Entra, resource groups, cost analysis. Use when managing Azure infrastructure, querying resources, or troubleshooting deployments.
allowed-tools: Bash(az *), Read, Grep
---

# Azure Resource Management for Data Engineering

You have full access to the `az` CLI. The user is authenticated via `az login`.

## Current context

- Active subscription: !`az account show --query "{name:name, id:id, tenant:tenantId}" -o tsv 2>/dev/null || echo "not logged in — run: az login"`

## Safety rules

- **ALWAYS confirm with the user before any delete, stop, or destructive operation**
- **ALWAYS show the resource name/id and subscription before modifying resources**
- **Flag production resources** — if a resource name contains "prod", "prd", or "production", warn the user explicitly
- Prefer `--output table` for human-readable output, `--output json` for programmatic use

## Circuit breaker

For bulk or iterative operations (e.g., tagging multiple resources, scaling pools, deleting old resources), apply self-regulation from [shared safety patterns](../_shared/safety.md):

- Track a mental risk score starting at 0%
- Each operation on a production resource: +15% risk
- Each operation touching more than 5 resources: +5% risk
- Any operation that fails or is reverted: +15% risk
- Touching resources outside the original scope: +20% risk
- **Risk > 20%**: Stop and confirm with the user before continuing
- **Hard cap**: Never execute more than 50 resource modifications without a user checkpoint
- For bulk deletes: always list all resources first, show the count, and require explicit confirmation

## Subscription & account management

```bash
# List subscriptions
az account list --output table

# Switch subscription
az account set --subscription "<name-or-id>"

# Show current context
az account show
```

## Resource groups

```bash
# List resource groups
az group list --output table

# List resources in a group
az resource list --resource-group <rg-name> --output table

# Create resource group
az group create --name <rg-name> --location <region>

# Tag a resource group
az group update --name <rg-name> --tags environment=dev project=data-platform

# Delete resource group (DESTRUCTIVE — always confirm)
az group delete --name <rg-name> --yes --no-wait
```

## Storage accounts

```bash
# List storage accounts
az storage account list --output table

# List containers
az storage container list --account-name <account> --output table

# List blobs in a container
az storage blob list --account-name <account> --container-name <container> --output table

# Upload a file
az storage blob upload --account-name <account> --container-name <container> --file <local-path> --name <blob-name>

# Download a file
az storage blob download --account-name <account> --container-name <container> --name <blob-name> --file <local-path>

# Generate SAS token (24-hour expiry)
az storage container generate-sas --account-name <account> --name <container> --permissions rl --expiry $(date -u -d "+24 hours" +%Y-%m-%dT%H:%MZ) --output tsv
```

## Key Vault

```bash
# List key vaults
az keyvault list --output table

# List secrets
az keyvault secret list --vault-name <vault> --output table

# Get a secret value
az keyvault secret show --vault-name <vault> --name <secret-name> --query value -o tsv

# Set a secret
az keyvault secret set --vault-name <vault> --name <secret-name> --value "<value>"

# List certificates
az keyvault certificate list --vault-name <vault> --output table
```

**Security note**: Never log or display secret values in output unless the user explicitly requests it. Prefer showing metadata only.

## Data Factory

```bash
# List data factories
az datafactory list --resource-group <rg-name> --output table

# List pipelines
az datafactory pipeline list --resource-group <rg-name> --factory-name <factory> --output table

# Trigger a pipeline run
az datafactory pipeline create-run --resource-group <rg-name> --factory-name <factory> --name <pipeline-name>

# View pipeline run status
az datafactory pipeline-run show --resource-group <rg-name> --factory-name <factory> --run-id <run-id>

# List recent pipeline runs
az datafactory pipeline-run query-by-factory --resource-group <rg-name> --factory-name <factory> --last-updated-after <datetime> --last-updated-before <datetime>

# View triggers
az datafactory trigger list --resource-group <rg-name> --factory-name <factory> --output table
```

## Synapse Analytics

```bash
# List Synapse workspaces
az synapse workspace list --output table

# List SQL pools
az synapse sql pool list --workspace-name <ws> --resource-group <rg> --output table

# Pause a SQL pool (cost saving)
az synapse sql pool pause --name <pool> --workspace-name <ws> --resource-group <rg>

# Resume a SQL pool
az synapse sql pool resume --name <pool> --workspace-name <ws> --resource-group <rg>

# List Spark pools
az synapse spark pool list --workspace-name <ws> --resource-group <rg> --output table
```

## Entra ID (Azure AD)

```bash
# List app registrations
az ad app list --display-name <search-term> --output table

# Create an app registration
az ad app create --display-name <name>

# List service principals
az ad sp list --display-name <search-term> --output table

# Create a service principal with role
az ad sp create-for-rbac --name <name> --role Contributor --scopes /subscriptions/<sub-id>/resourceGroups/<rg>

# List role assignments
az role assignment list --resource-group <rg-name> --output table
```

## Cost management

```bash
# View current month costs by resource group
az consumption usage list --start-date <YYYY-MM-01> --end-date <YYYY-MM-DD> --query "[].{Resource:instanceName, Cost:pretaxCost, Currency:currency}" --output table

# View budgets
az consumption budget list --output table
```

## Diagnostics & troubleshooting

```bash
# View activity log (last 24h)
az monitor activity-log list --offset 24h --output table

# View resource health
az resource show --ids <resource-id> --output json

# Check resource locks
az lock list --resource-group <rg-name> --output table
```

## Optional: Azure MCP Server

For richer integration with 200+ tools across 40+ Azure services, install the Azure MCP Server:
- Repository: `microsoft/mcp`
- Provides: resource listing, pricing, log queries, diagnostics, provisioning
- Setup: See https://github.com/microsoft/mcp

The Azure Skills Plugin can also be installed: `/plugin install azure-skills@skills`
