# Power BI REST API Reference

Base URL: `https://api.powerbi.com/v1.0/myorg`

Authentication: Bearer token via `az login` (audience: `https://analysis.windows.net/powerbi/api/.default`). When using `az rest`, authentication is handled automatically.

## API Operation Groups

| Group | Description |
|-------|-------------|
| Groups (Workspaces) | Create, list, manage workspaces and members |
| Datasets | Manage datasets, trigger refreshes, execute DAX queries |
| Reports | List, clone, rebind, export reports |
| Dashboards | List dashboards and tiles |
| Dataflows | Manage Power BI dataflows |
| Imports | Import .pbix files into workspaces |
| Pipelines | Deployment pipeline management (dev/test/prod) |
| Gateways | Manage on-premises data gateways and data sources |
| Capacities | Manage Premium/Fabric capacities |
| Apps | Manage Power BI apps |
| Admin | Tenant-wide administration (requires admin role) |
| Embed Token | Generate embed tokens for embedded analytics |
| Push Datasets | Create and push data to real-time datasets |

## Key Endpoints

### Workspaces

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/groups` | List workspaces |
| POST | `/groups?workspaceV2=true` | Create workspace |
| DELETE | `/groups/{id}` | Delete workspace |
| POST | `/groups/{id}/users` | Add user to workspace |
| DELETE | `/groups/{id}/users/{email}` | Remove user |

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/groups/{wsId}/datasets` | List datasets |
| GET | `/groups/{wsId}/datasets/{id}` | Get dataset details |
| DELETE | `/groups/{wsId}/datasets/{id}` | Delete dataset |
| POST | `/groups/{wsId}/datasets/{id}/refreshes` | Trigger refresh |
| GET | `/groups/{wsId}/datasets/{id}/refreshes` | Get refresh history |
| POST | `/groups/{wsId}/datasets/{id}/executeQueries` | Run DAX query |
| GET | `/groups/{wsId}/datasets/{id}/datasources` | List data sources |
| POST | `/groups/{wsId}/datasets/{id}/Default.UpdateParameters` | Update parameters |
| POST | `/groups/{wsId}/datasets/{id}/Default.TakeOver` | Take ownership |
| GET | `/groups/{wsId}/datasets/{id}/refreshSchedule` | Get refresh schedule |
| PATCH | `/groups/{wsId}/datasets/{id}/refreshSchedule` | Update refresh schedule |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/groups/{wsId}/reports` | List reports |
| GET | `/groups/{wsId}/reports/{id}` | Get report details |
| DELETE | `/groups/{wsId}/reports/{id}` | Delete report |
| POST | `/reports/{id}/Clone` | Clone report |
| POST | `/groups/{wsId}/reports/{id}/Rebind` | Rebind to dataset |
| GET | `/groups/{wsId}/reports/{id}/Export` | Download .pbix |
| POST | `/groups/{wsId}/reports/{id}/ExportTo` | Export to PDF/PNG/PPTX |
| GET | `/groups/{wsId}/reports/{id}/pages` | List report pages |

### Dashboards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/groups/{wsId}/dashboards` | List dashboards |
| GET | `/groups/{wsId}/dashboards/{id}/tiles` | List tiles |

### Deployment Pipelines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pipelines` | List pipelines |
| GET | `/pipelines/{id}/stages` | Get pipeline stages |
| POST | `/pipelines/{id}/deployAll` | Deploy to next stage |
| GET | `/pipelines/{id}/operations` | Get deploy operations |

### Imports

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/groups/{wsId}/imports?datasetDisplayName={name}` | Import .pbix file |
| GET | `/groups/{wsId}/imports/{id}` | Get import status |

### Gateways

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gateways` | List gateways |
| GET | `/gateways/{id}/datasources` | List gateway data sources |
| PATCH | `/gateways/{id}/datasources/{dsId}` | Update credentials |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/groups?$top=N` | List all workspaces (admin) |
| POST | `/admin/workspaces/getInfo` | Workspace scan with lineage |
| GET | `/admin/datasets` | List all datasets (admin) |
| GET | `/admin/capacities` | List capacities |

## Execute DAX Queries

Request body format:
```json
{
  "queries": [
    {
      "query": "EVALUATE SUMMARIZECOLUMNS('Table'[Column], \"Measure\", [Measure Name])"
    }
  ],
  "serializerSettings": {
    "includeNulls": true
  }
}
```

Response format:
```json
{
  "results": [
    {
      "tables": [
        {
          "rows": [
            {"Table[Column]": "Value", "[Measure]": 123.45}
          ]
        }
      ]
    }
  ]
}
```

## Import .pbix file

```bash
# Import requires multipart form upload
curl -X POST "https://api.powerbi.com/v1.0/myorg/groups/{wsId}/imports?datasetDisplayName=MyReport&nameConflict=CreateOrOverwrite" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@report.pbix"
```

## Throttling

Power BI uses throttling to maintain performance. When throttled:
- HTTP 429 (Too Many Requests) returned
- `Retry-After` header indicates wait time in seconds
- Implement exponential backoff for automated operations

## Permissions (Scopes)

Key delegated permissions:
- `Dataset.ReadWrite.All` — manage datasets
- `Report.ReadWrite.All` — manage reports
- `Workspace.ReadWrite.All` — manage workspaces
- `Dashboard.ReadWrite.All` — manage dashboards
- `Dataflow.ReadWrite.All` — manage dataflows
- `Pipeline.ReadWrite.All` — manage deployment pipelines
- `Tenant.ReadWrite.All` — admin operations (requires Power BI Admin role)

Service principals do not use scopes — permissions are managed via Power BI admin portal.
