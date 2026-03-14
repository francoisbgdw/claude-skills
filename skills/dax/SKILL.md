---
name: dax
description: DAX query authoring, testing, and optimization for Power BI and Microsoft Fabric semantic models. Use when writing DAX measures, debugging calculations, querying semantic models, or optimizing DAX performance.
allowed-tools: Bash(python *), Read, Write, Grep
---

# DAX Query Authoring & Optimization

Write, test, and optimize DAX queries for Power BI and Microsoft Fabric semantic models.

## Running DAX queries

### Via Python semantic-link (recommended)

```bash
pip install semantic-link semantic-link-labs
```

```python
import sempy.fabric as fabric

# Run a DAX query against a semantic model
result = fabric.evaluate_dax(
    dataset="<semantic-model-name>",
    dax_string="""
    EVALUATE
    SUMMARIZECOLUMNS(
        'Date'[Year],
        'Date'[Month],
        "Total Sales", [Total Sales],
        "Order Count", [Order Count]
    )
    """,
    workspace="<workspace-name>"
)
print(result)
```

**Note**: `evaluate_dax()` does not auto-refresh the semantic model. Refresh first if needed:
```python
fabric.refresh_dataset(dataset="<name>", workspace="<workspace>")
```

### Via REST API

```bash
az rest --method POST \
  --url "https://api.powerbi.com/v1.0/myorg/groups/<workspace-id>/datasets/<dataset-id>/executeQueries" \
  --body '{"queries": [{"query": "EVALUATE ROW(\"Test\", 1)"}]}'
```

## DAX authoring guidelines

### Measures vs calculated columns
- **Measures**: Evaluated at query time, use for aggregations. Always preferred.
- **Calculated columns**: Evaluated at refresh time, stored in model. Use only when you need row-level values for slicing/filtering.

### Variable pattern (always use VAR)
```dax
Total Profit =
VAR _Revenue = [Total Revenue]
VAR _Cost = [Total Cost]
RETURN
    _Revenue - _Cost
```

### CALCULATE pattern
```dax
-- Apply a filter context modification
Online Sales =
CALCULATE(
    [Total Sales],
    'Channel'[Channel] = "Online"
)

-- Remove filters
All Product Sales =
CALCULATE(
    [Total Sales],
    REMOVEFILTERS('Product')
)
```

### Iterator vs aggregator
```dax
-- GOOD: Aggregator (single scan)
Total Sales = SUM('Sales'[Amount])

-- USE WHEN NEEDED: Iterator (row-by-row, then aggregate)
Weighted Avg Price =
DIVIDE(
    SUMX('Sales', 'Sales'[Quantity] * 'Sales'[UnitPrice]),
    SUM('Sales'[Quantity])
)
```

For a comprehensive pattern library, see [dax-patterns.md](dax-patterns.md).

## Performance optimization

### Prefer SUMMARIZECOLUMNS over ADDCOLUMNS + SUMMARIZE
```dax
-- GOOD: Engine-optimized
EVALUATE
SUMMARIZECOLUMNS(
    'Product'[Category],
    "Total", [Total Sales]
)

-- AVOID: Less efficient
EVALUATE
ADDCOLUMNS(
    SUMMARIZE('Sales', 'Product'[Category]),
    "Total", [Total Sales]
)
```

### Avoid repeated measure calls
```dax
-- BAD: Evaluates [Total Sales] twice
Margin % = DIVIDE([Total Sales] - [Total Cost], [Total Sales])

-- GOOD: Evaluate once with VAR
Margin % =
VAR _Sales = [Total Sales]
RETURN
    DIVIDE(_Sales - [Total Cost], _Sales)
```

### Filter columns, not tables
```dax
-- GOOD: Column filter
CALCULATE([Total Sales], 'Date'[Year] = 2024)

-- AVOID: Table filter (creates a full table scan)
CALCULATE([Total Sales], FILTER('Date', 'Date'[Year] = 2024))
```

### Use KEEPFILTERS when appropriate
```dax
-- Intersects with existing filter context instead of replacing
Category Sales =
CALCULATE(
    [Total Sales],
    KEEPFILTERS('Product'[Category] = "Electronics")
)
```

## Common anti-patterns to avoid

1. **Circular dependencies**: Measure A references Measure B which references Measure A
2. **FILTER on large tables**: Use column filters in CALCULATE instead
3. **Nested iterators**: SUMX inside SUMX creates O(n^2) complexity
4. **DISTINCTCOUNT on high-cardinality columns**: Consider approximate alternatives
5. **Context transition without CALCULATE**: Referencing a measure inside an iterator without CALCULATE

## Debugging DAX

### Test with EVALUATE
```dax
-- Quick test of a measure
EVALUATE ROW("Result", [My Measure])

-- Test with filter context
EVALUATE
CALCULATETABLE(
    ROW("Result", [My Measure]),
    'Date'[Year] = 2024
)
```

### Inspect filter context
```dax
Debug Filters =
VAR _Filters = CONCATENATEX(
    FILTERS('Product'[Category]),
    'Product'[Category],
    ", "
)
RETURN "Filters: " & _Filters
```

### INFO functions for model metadata
```dax
EVALUATE INFO.TABLES()
EVALUATE INFO.COLUMNS()
EVALUATE INFO.MEASURES()
EVALUATE INFO.RELATIONSHIPS()
```
