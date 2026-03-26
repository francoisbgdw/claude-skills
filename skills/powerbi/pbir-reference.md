# PBIR & PBIP Format Reference

## Overview

**PBIR** (Power BI Enhanced Report Format) decomposes reports into individual JSON files — one per visual, page, and bookmark. **PBIP** (Power BI Project) is the project-level container that pairs a PBIR report with a TMDL semantic model. Together they enable git-friendly, code-first Power BI development.

### Format Timeline

| Milestone | Date |
|-----------|------|
| PBIR preview in Developer Mode | 2024 |
| Default for new reports in Power BI Service | January 2026 |
| Default for new reports in Power BI Desktop | March 2026 |
| Auto-conversion of existing reports on edit+save | January 2026+ |
| GA (only supported format) | Planned Q3 2026 |

### Format Comparison

| Format | Extension | Report Storage | Model Storage | Git-Friendly |
|--------|-----------|----------------|---------------|-------------|
| PBIX | `.pbix` | Binary zip | Binary zip | No |
| PBIP + PBIR-Legacy | `.pbip` | Single `report.json` | `model.bim` (TMSL) | Partial |
| PBIP + PBIR + TMDL | `.pbip` | Folder of JSON files | Folder of `.tmdl` files | Yes |

---

## PBIP Project Structure

```
MyProject/
├── MyProject.pbip                     # Project entry point
├── .gitignore                         # Auto-generated
│
├── MyProject.Report/
│   ├── .platform                      # Fabric platform config
│   ├── definition.pbir                # Points to PBIR definition folder
│   ├── .pbi/
│   │   ├── localSettings.json         # Local-only (gitignored)
│   │   └── cache.abf                  # Local cache (gitignored)
│   ├── definition/                    # PBIR report definition
│   │   ├── version.json
│   │   ├── report.json
│   │   ├── reportExtensions.json
│   │   ├── pages/
│   │   │   ├── pages.json             # Page ordering, active page
│   │   │   ├── ReportSection1/
│   │   │   │   ├── page.json
│   │   │   │   └── visuals/
│   │   │   │       ├── a1b2c3d4/
│   │   │   │       │   └── visual.json
│   │   │   │       └── e5f6g7h8/
│   │   │   │           └── visual.json
│   │   │   └── ReportSection2/
│   │   │       ├── page.json
│   │   │       └── visuals/...
│   │   └── bookmarks/
│   │       ├── bookmarks.json
│   │       └── Bookmark1.bookmark.json
│   └── StaticResources/
│       └── SharedResources/
│           └── BaseThemes/
│               └── CY24SU11.json      # Theme file
│
├── MyProject.SemanticModel/
│   ├── .platform
│   ├── definition.pbism               # Semantic model pointer
│   ├── .pbi/
│   │   ├── localSettings.json
│   │   └── cache.abf
│   └── definition/                    # TMDL definition
│       ├── database.tmdl
│       ├── model.tmdl
│       ├── relationships.tmdl
│       ├── expression.tmdl
│       ├── tables/
│       │   ├── Sales.tmdl
│       │   ├── Products.tmdl
│       │   └── Date.tmdl
│       ├── roles/
│       │   └── Reader.tmdl
│       └── cultures/
│           └── en-US.tmdl
```

---

## Key PBIR Files

### definition.pbir (Entry Point)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
  "version": "4.0",
  "datasetReference": {
    "byPath": { "path": "../Sales.Dataset" }
  }
}
```

Semantic model reference types:
- `byPath` — relative path to dataset folder (opens dataset in edit mode)
- `byConnection` — connection string to a Fabric workspace model (live connect)

### report.json (Report-Level Settings)

Contains report-level filters, theme reference, formatting defaults, and configuration. Located at `definition/report.json`.

### page.json (Page Definition)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json",
  "name": "ReportSection1",
  "displayName": "Sales Overview",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280,
  "filters": [],
  "background": {
    "color": { "solid": { "color": "#FFFFFF" } },
    "transparency": 0
  }
}
```

### visual.json (Visual Definition)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "a1b2c3d4",
  "position": {
    "x": 50,
    "y": 100,
    "width": 400,
    "height": 300,
    "z": 1000,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "barChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [{
            "field": {
              "Column": {
                "Property": "ProductCategory",
                "Expression": { "SourceRef": { "Entity": "Products" } }
              }
            }
          }]
        },
        "Y": {
          "projections": [{
            "field": {
              "Measure": {
                "Property": "TotalSales",
                "Expression": { "SourceRef": { "Entity": "Sales" } }
              }
            }
          }]
        }
      }
    },
    "objects": {
      "legend": [{
        "properties": {
          "show": { "expr": { "Literal": { "Value": "true" } } }
        }
      }]
    }
  },
  "filters": [],
  "annotations": []
}
```

### Annotations

Custom name-value pairs on reports, pages, and visuals — ignored by Power BI Desktop but usable by external scripts:

```json
{
  "annotations": [
    { "name": "owner", "value": "data-team" },
    { "name": "review-status", "value": "approved" }
  ]
}
```

---

## TMDL (Semantic Model Files)

Each table, role, and culture gets its own `.tmdl` file. Example `tables/Sales.tmdl`:

```
table Sales
    lineageTag: a1b2c3d4-...

    measure 'Total Sales' =
        SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])
        formatString: $#,##0.00
        lineageTag: e5f6g7h8-...

    column OrderDate
        dataType: dateTime
        lineageTag: ...
        sourceColumn: OrderDate

    column Quantity
        dataType: int64
        lineageTag: ...
        sourceColumn: Quantity

    partition Sales = m
        mode: import
        source
            let
                Source = Sql.Database("server.database.windows.net", "AdventureWorks"),
                Sales = Source{[Schema="dbo",Item="Sales"]}[Data]
            in
                Sales
```

---

## JSON Schema Validation

Every PBIR file includes a `$schema` URL. All schemas published at:
`https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition`

Enable VS Code IntelliSense by adding to `.vscode/settings.json`:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/definition/report.json"],
      "url": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json"
    },
    {
      "fileMatch": ["**/pages/*/page.json"],
      "url": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.0.0/schema.json"
    },
    {
      "fileMatch": ["**/visuals/*/visual.json"],
      "url": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json"
    }
  ]
}
```

---

## Git Workflow

### Recommended .gitignore

```gitignore
# Auto-generated by PBIP, extend as needed
.pbi/
*.abf
localSettings.json
diagramLayout.json
```

### Branching Strategy

1. Enable Developer Mode in Power BI Desktop
2. Save as `.pbip` (File > Save as > Power BI Project)
3. Init a Git repo in the project folder
4. Each developer works on separate pages/visuals — changes produce diffs in separate files
5. Use PRs for review; merge conflicts are resolvable (individual JSON files, not monolithic blobs)
6. Deploy via Fabric Git Integration or deployment pipelines

### Fabric Git Integration

Connect a Fabric workspace directly to Azure DevOps or GitHub:
- Bidirectional sync between workspace and repo
- Changes in the service can be committed; commits can be synced to the workspace
- Supports branching for dev/test/prod environments

---

## Programmatic Editing Patterns

### Batch-modify visual properties across a report

```python
import json
from pathlib import Path

report_dir = Path("MyProject.Report/definition")

# Update all visuals to use rounded borders
for visual_path in report_dir.glob("pages/*/visuals/*/visual.json"):
    with open(visual_path) as f:
        visual = json.load(f)

    # Add or update border radius in visual objects
    if "visual" in visual and "objects" in visual["visual"]:
        visual["visual"]["objects"].setdefault("border", [{}])
        visual["visual"]["objects"]["border"][0].setdefault("properties", {})
        visual["visual"]["objects"]["border"][0]["properties"]["radius"] = {
            "expr": { "Literal": { "Value": "8" } }
        }

    with open(visual_path, "w") as f:
        json.dump(visual, f, indent=2)
```

### Copy a page between reports

```bash
# Copy page folder from source to target report
cp -r SourceReport.Report/definition/pages/SalesPage \
      TargetReport.Report/definition/pages/SalesPage

# Update pages.json in the target to include the new page
```

### CI/CD validation

```bash
# Validate all PBIR JSON files against their schemas
pip install jsonschema requests

python -c "
import json, jsonschema, requests
from pathlib import Path

for f in Path('.').glob('**/*.json'):
    with open(f) as fh:
        data = json.load(fh)
    schema_url = data.get('\$schema')
    if schema_url and 'developer.microsoft.com' in schema_url:
        schema = requests.get(schema_url).json()
        jsonschema.validate(data, schema)
        print(f'OK: {f}')
"
```

### Apply a theme to a PBIR report

Place the theme file in `StaticResources/SharedResources/BaseThemes/` and reference it in `definition/report.json`.

---

## Size Limits (Service-Enforced)

| Limit | Value |
|-------|-------|
| Max pages per report | 1,000 |
| Max visuals per page | 1,000 |
| Max resource package files | 1,000 |
| Max total resource file size | 300 MB |
| Max total report file size | 300 MB |
| Performance warning threshold | 500+ files |

---

## Naming Conventions

By default, PBIR uses 20-character unique identifiers for folders/files (e.g., `90c2e07d8e84e7d5c026`). These can be renamed to friendlier names using only word characters or hyphens. Use "Copy object name" in Power BI Desktop/Service to identify which file maps to which visual.

---

## External Tool Compatibility

| Tool | Capability |
|------|-----------|
| **Tabular Editor** (2 & 3) | Read/write TMDL files, supports PBIP projects |
| **DAX Studio** | Connects to local PBI Desktop for DAX testing |
| **ALM Toolkit** | Schema comparison between PBIP semantic models |
| **VS Code** | JSON editing with IntelliSense via schema URLs |
| **AI agents (Claude Code)** | Read/modify TMDL and PBIR files programmatically |
