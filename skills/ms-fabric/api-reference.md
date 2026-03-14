# Microsoft Fabric REST API Reference

Base URL: `https://api.fabric.microsoft.com/v1`

Authentication: Bearer token via `az login` or Service Principal. When using `az rest`, authentication is handled automatically.

## Core endpoints

### Workspaces
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workspaces` | List all workspaces |
| GET | `/workspaces/{id}` | Get workspace details |
| POST | `/workspaces` | Create workspace |
| PATCH | `/workspaces/{id}` | Update workspace |
| DELETE | `/workspaces/{id}` | Delete workspace |
| GET | `/workspaces/{id}/items` | List items (filter with `?type=`) |

### Item types for filtering
- `Lakehouse`
- `Warehouse`
- `SemanticModel`
- `Notebook`
- `DataPipeline`
- `Report`
- `Dashboard`
- `Dataflow`
- `SparkJobDefinition`
- `MLModel`
- `MLExperiment`

### Lakehouses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workspaces/{wsId}/lakehouses` | List lakehouses |
| GET | `/workspaces/{wsId}/lakehouses/{id}` | Get lakehouse |
| GET | `/workspaces/{wsId}/lakehouses/{id}/tables` | List tables |
| POST | `/workspaces/{wsId}/lakehouses/{id}/tables/{table}/load` | Load data into table |

### Semantic Models
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workspaces/{wsId}/semanticModels` | List models |
| POST | `/workspaces/{wsId}/semanticModels/{id}/refresh` | Trigger refresh |
| GET | `/workspaces/{wsId}/semanticModels/{id}/refreshes` | Refresh history |

### Jobs (Pipelines, Notebooks, etc.)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workspaces/{wsId}/items/{id}/jobs/instances?jobType=Pipeline` | Run a pipeline |
| GET | `/workspaces/{wsId}/items/{id}/jobs/instances` | List job runs |
| GET | `/workspaces/{wsId}/items/{id}/jobs/instances/{jobId}` | Get job status |
| POST | `/workspaces/{wsId}/items/{id}/jobs/instances/{jobId}/cancel` | Cancel a job |

### Item definitions (import/export)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workspaces/{wsId}/items/{id}/getDefinition` | Export item definition |
| POST | `/workspaces/{wsId}/items/{id}/updateDefinition` | Import item definition |

### Capacities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/capacities` | List available capacities |

### Git integration
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workspaces/{wsId}/git/status` | Git sync status |
| POST | `/workspaces/{wsId}/git/commitToGit` | Commit workspace to git |
| POST | `/workspaces/{wsId}/git/updateFromGit` | Pull from git |

## Common response format

```json
{
  "value": [
    {
      "id": "guid",
      "displayName": "Item Name",
      "type": "Lakehouse",
      "workspaceId": "guid"
    }
  ],
  "continuationToken": "token-for-next-page",
  "continuationUri": "url-for-next-page"
}
```

Use `continuationUri` for paginated results.

## Error responses

```json
{
  "errorCode": "ItemNotFound",
  "message": "The requested item was not found.",
  "requestId": "guid"
}
```

Common error codes: `Unauthorized`, `ItemNotFound`, `WorkspaceNotFound`, `CapacityNotActive`, `TooManyRequests` (429 — retry with exponential backoff).
