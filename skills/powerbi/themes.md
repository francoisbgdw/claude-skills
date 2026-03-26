# Power BI Theme Authoring Reference

## Theme JSON Schema

A Power BI theme is a `.json` file. The only required property is `name`; everything else is optional and falls back to defaults.

Microsoft publishes an official JSON Schema (Draft 7) for IDE validation:
- Schema: `https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.141.json`
- Community templates: `https://github.com/MattRudy/PowerBI-ThemeTemplates`

### Top-Level Properties

```json
{
  "name": "My Theme",
  "dataColors": ["#004578", "#0078D4", "#00BCF2", "#41D3BD", "#EF6950", "#FFB900"],
  "background": "#FFFFFF",
  "foreground": "#252423",
  "tableAccent": "#0078D4",
  "maximum": "#0078D4",
  "center": "#D7D2CB",
  "minimum": "#EF6950",
  "good": "#41D3BD",
  "neutral": "#D7D2CB",
  "bad": "#EF6950"
}
```

| Property | Purpose |
|----------|---------|
| `name` | Theme identifier (**required**) |
| `dataColors` | Array of hex colors for chart series (5-7 recommended). PBI auto-generates more when exhausted |
| `background` | Default page/visual background |
| `foreground` | Default text/foreground color |
| `tableAccent` | Accent color for tables, matrices, KPI visuals |
| `maximum` / `center` / `minimum` | Divergent color scales (gauges, conditional formatting) |
| `good` / `neutral` / `bad` | Semantic status colors (KPI, conditional formatting) |

### Structural Colors (UI Hierarchy)

Six levels control the visual hierarchy of non-data UI elements:

```json
{
  "firstLevelElements": "#252423",
  "secondLevelElements": "#605E5C",
  "thirdLevelElements": "#C8C6C4",
  "fourthLevelElements": "#E1DFDD",
  "background": "#FFFFFF",
  "secondaryBackground": "#F3F2F1",
  "tableAccent": "#0078D4"
}
```

| Level | Controls |
|-------|----------|
| `firstLevelElements` | Primary foreground — titles, axis labels, data labels, slicer headers, card values |
| `secondLevelElements` | Secondary text — subtitles, lighter labels |
| `thirdLevelElements` | Gridlines, borders, minor accents |
| `fourthLevelElements` | Dimmed/disabled elements |
| `background` | Page and container backgrounds |
| `secondaryBackground` | Alternate backgrounds (e.g., filter pane, tooltip) |

### Text Classes

Four text classes control typography across all visuals:

```json
{
  "textClasses": {
    "title": {
      "fontFamily": "Segoe UI Semibold",
      "fontSize": 18,
      "color": "#252423"
    },
    "header": {
      "fontFamily": "Segoe UI Semibold",
      "fontSize": 14,
      "color": "#252423"
    },
    "label": {
      "fontFamily": "Segoe UI",
      "fontSize": 12,
      "color": "#605E5C"
    },
    "callout": {
      "fontFamily": "Segoe UI Light",
      "fontSize": 32,
      "color": "#252423"
    }
  }
}
```

| Class | Used For |
|-------|----------|
| `title` | Axis titles, chart titles |
| `header` | Key influencer headers |
| `label` | Table/matrix values, axis tick labels |
| `callout` | Card data labels, KPI indicators, gauge callouts |

### Visual Styles (visualStyles)

The most powerful section. Pattern: `visualStyles > [visualType or "*"] > [stylePreset or "*"] > [cardName] > [array of property objects]`.

The `"*"` wildcard applies to all visuals (first key) or the default style (second key). Specific visual names override the wildcard.

```json
{
  "visualStyles": {
    "*": {
      "*": {
        "general": [{ "responsive": true, "keepLayerOrder": true }],
        "background": [{
          "show": true,
          "color": { "solid": { "color": "#FFFFFF" } },
          "transparency": 0
        }],
        "border": [{
          "show": true,
          "color": { "solid": { "color": "#E1DFDD" } },
          "radius": 8
        }],
        "dropShadow": [{
          "show": true,
          "color": { "solid": { "color": "#000000" } },
          "position": "outer",
          "preset": "bottomRight",
          "transparency": 85
        }],
        "padding": [{ "top": 8, "bottom": 8, "left": 8, "right": 8 }],
        "title": [{
          "show": true,
          "fontColor": { "solid": { "color": "#252423" } },
          "fontSize": 14,
          "fontFamily": "Segoe UI Semibold",
          "alignment": "left"
        }],
        "visualHeader": [{
          "show": true,
          "background": { "solid": { "color": "transparent" } }
        }]
      }
    },
    "barChart": {
      "*": {
        "legend": [{ "show": true, "position": "Top", "fontSize": 11 }],
        "categoryAxis": [{ "fontSize": 11, "gridlineShow": false }],
        "valueAxis": [{ "fontSize": 11, "gridlineShow": true }],
        "labels": [{ "show": false, "fontSize": 11 }]
      }
    }
  }
}
```

**Common visual type names**: `barChart`, `clusteredBarChart`, `clusteredColumnChart`, `lineChart`, `areaChart`, `pieChart`, `donutChart`, `card`, `multiRowCard`, `tableEx`, `pivotTable`, `slicer`, `map`, `filledMap`, `scatterChart`, `treemap`, `waterfallChart`, `funnel`, `gauge`, `kpi`.

**Common card names**: `general`, `background`, `border`, `dropShadow`, `padding`, `title`, `visualHeader`, `legend`, `categoryAxis`, `valueAxis`, `labels`, `dataPoint`.

---

## How to Apply Themes

### Power BI Desktop
- **View > Themes > Browse for themes** — import any `.json` file
- **View > Themes > Customize current theme** — GUI editor, then export to JSON

### Organizational Themes (Admin Portal)
- Tenant admins upload via **Fabric Admin Portal > Tenant settings**
- All users see the theme in the gallery
- No public REST API yet; Semantic Link Labs uses an internal API as a workaround

### Power BI Embedded (JavaScript SDK)
```javascript
const themeJson = { /* theme object */ };
await report.applyTheme({ themeJson: themeJson });

// Reset to default
await report.resetTheme();
```

### Python (Semantic Link Labs in Fabric Notebooks)
```python
import sempy_labs as labs
import json

with open("corporate_theme.json") as f:
    theme = json.load(f)

rpt = labs.get_report("My Report", workspace="My Workspace")
rpt.set_theme(theme_json=theme)
```

### PBIR (Code-First)
Place the theme JSON file at:
```
MyReport.Report/StaticResources/SharedResources/BaseThemes/theme.json
```
Reference it in `definition/report.json`. Commit to source control.

---

## Accessibility Best Practices

### WCAG 2.2 Contrast Requirements
- **Normal text** (< 18pt / < 14pt bold): minimum **4.5:1** contrast ratio
- **Large text** (>= 18pt / >= 14pt bold): minimum **3:1** contrast ratio
- **Non-text UI** (borders, icons, chart elements): minimum **3:1** contrast ratio

### Color Blindness
- Test with simulation tools: Color Oracle, Coblis, or browser DevTools
- Cover deuteranopia (red-green, ~6% of males), protanopia (red-green, ~1%), tritanopia (blue-yellow, rare)
- **Never rely on color alone** — use data labels, patterns, shapes, or annotations alongside color

### Font Sizing
- Never below **12px** for labels
- **14px+** for titles and headers
- Card callout values benefit from **24px+** for readability

### High-Contrast Variant
Provide a high-contrast theme variant. Power BI Embedded supports `contrastMode` in config:
```javascript
{ settings: { contrastMode: models.ContrastMode.HighContrastBlack } }
```

---

## Corporate Branding Mapping

| Brand Element | Theme Property |
|---------------|---------------|
| Primary color | `tableAccent`, first entry in `dataColors` |
| Secondary / tertiary colors | Remaining `dataColors` entries |
| Brand text color | `foreground`, `firstLevelElements` |
| Brand background | `background` |
| Accent for hover/selection | `secondaryBackground` |
| Success / warning / error | `good` / `neutral` / `bad` |

**Tips:**
- Limit palette to **5-7 data colors** derived from brand guidelines
- Use accent colors sparingly — highlight key data points, not everything
- Test against multiple visual types (bar, line, card, table, matrix, slicer, map) before rollout

---

## Starter Templates

### Corporate Light
```json
{
  "name": "Corporate Light",
  "dataColors": ["#0078D4", "#00BCF2", "#41D3BD", "#FFB900", "#EF6950", "#8661C5"],
  "background": "#FFFFFF",
  "foreground": "#252423",
  "tableAccent": "#0078D4",
  "firstLevelElements": "#252423",
  "secondLevelElements": "#605E5C",
  "thirdLevelElements": "#C8C6C4",
  "fourthLevelElements": "#E1DFDD",
  "secondaryBackground": "#F3F2F1",
  "good": "#41D3BD",
  "neutral": "#D7D2CB",
  "bad": "#EF6950",
  "maximum": "#0078D4",
  "center": "#D7D2CB",
  "minimum": "#EF6950",
  "textClasses": {
    "title": { "fontFamily": "Segoe UI Semibold", "fontSize": 16, "color": "#252423" },
    "header": { "fontFamily": "Segoe UI Semibold", "fontSize": 14, "color": "#252423" },
    "label": { "fontFamily": "Segoe UI", "fontSize": 12, "color": "#605E5C" },
    "callout": { "fontFamily": "Segoe UI Light", "fontSize": 28, "color": "#252423" }
  },
  "visualStyles": {
    "*": {
      "*": {
        "background": [{ "show": true, "color": { "solid": { "color": "#FFFFFF" } }, "transparency": 0 }],
        "border": [{ "show": true, "color": { "solid": { "color": "#E1DFDD" } }, "radius": 8 }],
        "dropShadow": [{ "show": true, "color": { "solid": { "color": "#000000" } }, "position": "outer", "preset": "bottomRight", "transparency": 90 }],
        "title": [{ "fontColor": { "solid": { "color": "#252423" } }, "fontSize": 14, "fontFamily": "Segoe UI Semibold" }]
      }
    }
  }
}
```

### Corporate Dark
```json
{
  "name": "Corporate Dark",
  "dataColors": ["#00BCF2", "#41D3BD", "#FFB900", "#EF6950", "#8661C5", "#E3008C"],
  "background": "#1B1A19",
  "foreground": "#FFFFFF",
  "tableAccent": "#00BCF2",
  "firstLevelElements": "#FFFFFF",
  "secondLevelElements": "#D2D0CE",
  "thirdLevelElements": "#484644",
  "fourthLevelElements": "#323130",
  "secondaryBackground": "#252423",
  "good": "#41D3BD",
  "neutral": "#D2D0CE",
  "bad": "#EF6950",
  "maximum": "#00BCF2",
  "center": "#484644",
  "minimum": "#EF6950",
  "textClasses": {
    "title": { "fontFamily": "Segoe UI Semibold", "fontSize": 16, "color": "#FFFFFF" },
    "header": { "fontFamily": "Segoe UI Semibold", "fontSize": 14, "color": "#FFFFFF" },
    "label": { "fontFamily": "Segoe UI", "fontSize": 12, "color": "#D2D0CE" },
    "callout": { "fontFamily": "Segoe UI Light", "fontSize": 28, "color": "#FFFFFF" }
  },
  "visualStyles": {
    "*": {
      "*": {
        "background": [{ "show": true, "color": { "solid": { "color": "#252423" } }, "transparency": 0 }],
        "border": [{ "show": true, "color": { "solid": { "color": "#484644" } }, "radius": 6 }],
        "dropShadow": [{ "show": false }],
        "title": [{ "fontColor": { "solid": { "color": "#FFFFFF" } }, "fontSize": 14, "fontFamily": "Segoe UI Semibold" }]
      }
    }
  }
}
```

### High-Contrast Accessible
```json
{
  "name": "High Contrast Accessible",
  "dataColors": ["#0066CC", "#CC6600", "#009933", "#CC0000", "#6600CC", "#007777"],
  "background": "#FFFFFF",
  "foreground": "#000000",
  "tableAccent": "#0066CC",
  "firstLevelElements": "#000000",
  "secondLevelElements": "#333333",
  "thirdLevelElements": "#666666",
  "fourthLevelElements": "#999999",
  "secondaryBackground": "#F0F0F0",
  "good": "#009933",
  "neutral": "#666666",
  "bad": "#CC0000",
  "maximum": "#0066CC",
  "center": "#666666",
  "minimum": "#CC0000",
  "textClasses": {
    "title": { "fontFamily": "Segoe UI Bold", "fontSize": 18, "color": "#000000" },
    "header": { "fontFamily": "Segoe UI Semibold", "fontSize": 15, "color": "#000000" },
    "label": { "fontFamily": "Segoe UI", "fontSize": 13, "color": "#333333" },
    "callout": { "fontFamily": "Segoe UI Semibold", "fontSize": 30, "color": "#000000" }
  },
  "visualStyles": {
    "*": {
      "*": {
        "background": [{ "show": true, "color": { "solid": { "color": "#FFFFFF" } }, "transparency": 0 }],
        "border": [{ "show": true, "color": { "solid": { "color": "#000000" } }, "radius": 4 }],
        "dropShadow": [{ "show": false }],
        "title": [{ "fontColor": { "solid": { "color": "#000000" } }, "fontSize": 16, "fontFamily": "Segoe UI Bold" }]
      }
    }
  }
}
```

---

## Dark/Light Mode Toggle Pattern

Build a theme toggle in Power BI using **bookmarks + buttons** (no DAX required):

1. Create two bookmarks: "Light Mode" and "Dark Mode"
2. Each bookmark captures the applied theme and page background
3. Add toggle buttons bound to each bookmark
4. In Power BI Embedded, toggle programmatically:

```javascript
// Switch to dark mode
await report.applyTheme({ themeJson: darkTheme });

// Switch to light mode
await report.applyTheme({ themeJson: lightTheme });
```

---

## Theme Validation

Use the Microsoft JSON schema for real-time validation in VS Code:

```json
{
  "$schema": "https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.141.json",
  "name": "My Theme",
  "dataColors": ["#0078D4"]
}
```

Add to VS Code `settings.json` for automatic validation of all theme files:
```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/powerbi-theme*.json", "**/pbi-theme*.json"],
      "url": "https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.141.json"
    }
  ]
}
```
