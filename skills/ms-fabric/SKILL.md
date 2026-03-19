---
name: ms-fabric
description: Microsoft Fabric workspace and data platform management — lakehouses, warehouses, semantic models, pipelines, notebooks. Use when working with Fabric workspaces, querying data, managing items, or deploying Fabric artifacts.
allowed-tools: Bash(python *), Bash(az rest *), Bash(pip *), Read, Write, Grep, Glob
---

# Microsoft Fabric Management

Fabric has no dedicated CLI. Use the Fabric REST API via `az rest` or Python SDKs. The user authenticates via `az login`.

## Current context

- Azure account: !`az account show --query "{name:name, id:id}" -o tsv 2>/dev/null || echo "not logged in — run: az login"`

## Safety rules & circuit breaker

- **ALWAYS confirm before deleting workspaces, items, or triggering deployments**
- **Flag production workspaces** — if a workspace name contains "prod", "prd", or "production", warn explicitly
- **Show workspace name and item ID before any modification**

For bulk or iterative operations (refreshing multiple models, deploying across workspaces, deleting items), apply self-regulation from [shared safety patterns](../_shared/safety.md):

- Track a mental risk score starting at 0%
- Each operation on a production workspace: +15% risk
- Each failed refresh or deployment: +15% risk
- Operations outside the originally-specified workspace: +20% risk
- **Risk > 20%**: Stop and confirm with the user
- **Hard cap**: Never execute more than 50 API calls in a modification loop without a user checkpoint

## REST API via az rest

The Fabric REST API base URL is `https://api.fabric.microsoft.com/v1`.

### Workspaces

```bash
# List all workspaces
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces"

# Get a specific workspace
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>"

# List items in a workspace
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/items"

# Filter items by type (Lakehouse, Warehouse, SemanticModel, Notebook, DataPipeline, etc.)
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/items?type=Lakehouse"
```

### Lakehouses

```bash
# List lakehouses in a workspace
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/lakehouses"

# List tables in a lakehouse
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/lakehouses/<lakehouse-id>/tables"

# Load a file into a table
az rest --method POST --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/lakehouses/<lakehouse-id>/tables/<table-name>/load" --body '{"relativePath": "Files/data.csv", "pathType": "File", "mode": "Overwrite"}'
```

### Semantic models

```bash
# List semantic models
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/semanticModels"

# Trigger refresh
az rest --method POST --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/semanticModels/<model-id>/refresh"

# Get refresh history
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/semanticModels/<model-id>/refreshes"
```

### Pipelines (Data Pipelines)

```bash
# List pipelines
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/items?type=DataPipeline"

# Run a pipeline (via item job)
az rest --method POST --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/items/<pipeline-id>/jobs/instances?jobType=Pipeline"

# Get job instances
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/items/<item-id>/jobs/instances"
```

### Notebooks

```bash
# List notebooks
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/items?type=Notebook"

# Get notebook definition
az rest --method POST --url "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/items/<notebook-id>/getDefinition"
```

For a full API reference, see [api-reference.md](api-reference.md).

## Python SDK: microsoft-fabric-api

```bash
pip install microsoft-fabric-api
```

```python
from microsoft.fabric import FabricClient
from azure.identity import DefaultAzureCredential

client = FabricClient(credential=DefaultAzureCredential())

# List workspaces
workspaces = client.workspaces.list()
for ws in workspaces:
    print(f"{ws.display_name} ({ws.id})")

# List items in a workspace
items = client.items.list(workspace_id="<workspace-id>")
for item in items:
    print(f"{item.type}: {item.display_name}")
```

## Python SDK: semantic-link (sempy)

For querying semantic models and running DAX. Best used in Fabric notebooks or local environments with `az login`.

```bash
pip install semantic-link semantic-link-labs
```

```python
import sempy.fabric as fabric

# List datasets in a workspace
datasets = fabric.list_datasets(workspace="<workspace-name>")

# Read a table from a semantic model
df = fabric.read_table(
    dataset="<dataset-name>",
    table="<table-name>",
    workspace="<workspace-name>"
)

# Run a DAX query
result = fabric.evaluate_dax(
    dataset="<dataset-name>",
    dax_string='EVALUATE SUMMARIZECOLUMNS(\'Date\'[Year], "Total Sales", [Total Sales])',
    workspace="<workspace-name>"
)
```

## CI/CD with fabric-cicd

```bash
pip install fabric-cicd
```

The `fabric-cicd` tool is officially supported by Microsoft for deploying Fabric items across workspaces (dev -> test -> prod).

```python
from fabric_cicd import FabricWorkspace, publish_all_items

# Connect to source workspace
ws = FabricWorkspace(
    workspace_id="<workspace-id>",
    repository_directory="<local-path>",
    item_type_in_scope=["Notebook", "DataPipeline", "Lakehouse"]
)

# Deploy items
publish_all_items(workspace=ws)
```

## Helper scripts

For reusable Python helpers, see [scripts/fabric_helpers.py](scripts/fabric_helpers.py).

## Optional: Fabric MCP Server

For richer integration via GraphQL:
- Requires: GraphQL API enabled in Fabric workspace, Service Principal auth
- Repository: `microsoft/fabric-samples` (MCP server)
- Setup: Enable GraphQL introspection (requires Workspace Admin), configure Service Principal in `.env`
- See: https://blog.fabric.microsoft.com/en-us/blog/connecting-ai-agents-to-microsoft-fabric-with-graphql-and-the-model-context-protocol-mcp
