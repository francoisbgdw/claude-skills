---
name: powerbi
description: Power BI report, dataset, and workspace management — refresh datasets, manage reports, deploy content, administer workspaces, embed analytics. Use when working with Power BI Service, managing datasets/reports, triggering refreshes, or automating Power BI administration.
allowed-tools: Bash(az rest *), Bash(python *), Bash(pip *), Read, Write, Grep, Glob
---

# Power BI Management & Automation

Power BI has no dedicated CLI. Use the Power BI REST API via `az rest` or Python. The user authenticates via `az login`.

## Current context

- Azure account: !`az account show --query "{name:name, id:id}" -o tsv 2>/dev/null || echo "not logged in — run: az login"`

## REST API via az rest

The Power BI REST API base URL is `https://api.powerbi.com/v1.0/myorg`.

For workspace-scoped operations, use: `https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}`

### Workspaces (Groups)

```bash
# List all workspaces the user has access to
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups"

# Get a specific workspace
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}"

# Create a workspace
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups?workspaceV2=true" --body '{"name": "New Workspace"}'

# Add a user to a workspace
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/users" --body '{"emailAddress": "user@domain.com", "groupUserAccessRight": "Member"}'
```

### Datasets (Semantic Models)

```bash
# List datasets in a workspace
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets"

# Get dataset details
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}"

# Trigger dataset refresh
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}/refreshes"

# Get refresh history
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}/refreshes"

# Execute a DAX query against a dataset
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}/executeQueries" --body '{
  "queries": [{"query": "EVALUATE SUMMARIZECOLUMNS('\''Date'\''[Year], \"Total Sales\", [Total Sales])"}],
  "serializerSettings": {"includeNulls": true}
}'

# Update dataset parameters
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}/Default.UpdateParameters" --body '{
  "updateDetails": [{"name": "ServerName", "newValue": "newserver.database.windows.net"}]
}'

# Take over a dataset (change owner)
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}/Default.TakeOver"

# Update data source credentials
az rest --method PATCH --url "https://api.powerbi.com/v1.0/myorg/gateways/{gatewayId}/datasources/{datasourceId}" --body '{
  "credentialDetails": {
    "credentialType": "OAuth2",
    "credentials": "{\"credentialData\":\"\"}",
    "encryptedConnection": "Encrypted",
    "encryptionAlgorithm": "None",
    "privacyLevel": "Organizational"
  }
}'
```

### Reports

```bash
# List reports in a workspace
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/reports"

# Get a specific report
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/reports/{reportId}"

# Clone a report to another workspace
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/reports/{reportId}/Clone" --body '{"name": "Cloned Report", "targetWorkspaceId": "{targetWorkspaceId}"}'

# Rebind a report to a different dataset
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/reports/{reportId}/Rebind" --body '{"datasetId": "{newDatasetId}"}'

# Export report (download .pbix)
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/reports/{reportId}/Export" --output-file report.pbix

# Export report to file (PDF, PNG, PPTX)
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/reports/{reportId}/ExportTo" --body '{
  "format": "PDF",
  "powerBIReportConfiguration": {
    "pages": [{"pageName": "ReportSection1"}]
  }
}'
```

### Dashboards

```bash
# List dashboards in a workspace
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/dashboards"

# List tiles on a dashboard
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/dashboards/{dashboardId}/tiles"
```

### Deployment Pipelines

```bash
# List deployment pipelines
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/pipelines"

# Get pipeline stages
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/pipelines/{pipelineId}/stages"

# Deploy content to next stage
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/pipelines/{pipelineId}/deployAll" --body '{
  "sourceStageOrder": 0,
  "options": {"allowOverwriteArtifact": true, "allowCreateArtifact": true}
}'
```

### Admin operations

```bash
# List workspaces (admin scope — requires Power BI Admin role)
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/admin/groups?%24top=100"

# Get workspace info with datasets, reports, etc.
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/admin/workspaces/getInfo" --body '{"workspaces": ["{workspaceId}"]}'

# List capacities
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/capacities"

# Get refresh schedule
az rest --method GET --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}/refreshSchedule"
```

For a full API reference, see [api-reference.md](api-reference.md).

## Python automation

### Using azure-identity + requests (recommended)

```python
from azure.identity import DefaultAzureCredential
import requests

credential = DefaultAzureCredential()
token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")

headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}

# List workspaces
resp = requests.get("https://api.powerbi.com/v1.0/myorg/groups", headers=headers)
workspaces = resp.json()["value"]
for ws in workspaces:
    print(f"{ws['name']} ({ws['id']})")
```

### Using semantic-link (in Fabric notebooks)

```python
import sempy.fabric as fabric

# List datasets
datasets = fabric.list_datasets(workspace="<workspace-name>")

# Execute DAX query
result = fabric.evaluate_dax(
    dataset="<dataset-name>",
    dax_string='EVALUATE ROW("Test", 1 + 1)',
    workspace="<workspace-name>"
)
```

### Using pbipy (community library)

```bash
pip install pbipy
```

```python
from pbipy import PowerBI

pbi = PowerBI(bearer_token)

# List workspaces
workspaces = pbi.groups()

# Get datasets in a workspace
datasets = pbi.datasets(group=workspace)

# Trigger refresh
pbi.refresh_dataset(dataset, group=workspace)
```

## Common automation scenarios

### Bulk dataset refresh
```python
# Refresh all datasets in a workspace
datasets = requests.get(f"{BASE}/groups/{ws_id}/datasets", headers=headers).json()["value"]
for ds in datasets:
    if ds.get("isRefreshable"):
        requests.post(f"{BASE}/groups/{ws_id}/datasets/{ds['id']}/refreshes", headers=headers)
        print(f"Triggered refresh: {ds['name']}")
```

### Monitor refresh status
```python
refreshes = requests.get(
    f"{BASE}/groups/{ws_id}/datasets/{ds_id}/refreshes?$top=1",
    headers=headers
).json()["value"]

latest = refreshes[0]
print(f"Status: {latest['status']}, Start: {latest.get('startTime')}, End: {latest.get('endTime')}")
```

### Content promotion (dev -> test -> prod)
Use deployment pipelines for managed promotion:
```bash
# Deploy from Development (stage 0) to Test (stage 1)
az rest --method POST --url "https://api.powerbi.com/v1.0/myorg/pipelines/{pipelineId}/deployAll" --body '{"sourceStageOrder": 0}'
```

## Relationship with Fabric and DAX skills

- **Fabric skill**: Manages Fabric-specific items (lakehouses, warehouses, notebooks, Fabric pipelines). Power BI datasets/reports in Fabric are also accessible via this skill's REST API.
- **DAX skill**: Focuses on writing and optimizing DAX queries. Use `executeQueries` endpoint from this skill or `evaluate_dax()` from semantic-link to run DAX against Power BI datasets.

## Optional: Power BI MCP Servers

### Power BI Modeling MCP (Microsoft)
Microsoft's `powerbi-modeling-mcp` (announced at Ignite 2025) enables AI agents to interact with semantic models:
- Read model structure, run DAX queries, create/modify measures, manage relationships
- Connects to Power BI Desktop, Fabric workspaces, and PBIP files
- Remote server available for cloud-hosted models

### MCP Engine (Community)
- Repository: `maxanatsko/pbi-desktop-mcp-public`
- Connects to Power BI Desktop locally
- Read model structure, execute DAX, create/modify measures
- Compatible with Claude Desktop, Claude Code CLI, VS Code

### Configuration example
```json
{
  "mcpServers": {
    "powerbi": {
      "command": "npx",
      "args": ["-y", "@anthropic/powerbi-mcp"]
    }
  }
}
```

Note: Verify the exact package name and setup at the MCP server's documentation, as implementations are evolving.
