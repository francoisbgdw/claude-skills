# Power BI Frontend Development Reference

## Power BI Embedded (JavaScript SDK)

### Packages

| Package | Purpose |
|---------|---------|
| `powerbi-client` | Core embedding SDK (reports, dashboards, tiles, Q&A) |
| `powerbi-models` | TypeScript interfaces and config schemas |
| `powerbi-report-authoring` | Programmatic visual creation/editing in embedded sessions |
| `powerbi-client-react` | React `<PowerBIEmbed>` component |
| `powerbi-client-angular` | Angular module with directive |

### Embedding Workflow

1. Server authenticates to Entra ID (service principal or user identity)
2. Server calls Power BI REST API to get embed URL and generate an embed token
3. Browser receives `accessToken`, `embedUrl`, `id` and calls `powerbi.embed(container, config)`

### Embed Token Generation (REST API)

```bash
# Generate embed token for a report
az rest --method POST \
  --url "https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/reports/{reportId}/GenerateToken" \
  --body '{"accessLevel": "View"}'

# Generate embed token for multiple items
az rest --method POST \
  --url "https://api.powerbi.com/v1.0/myorg/GenerateToken" \
  --body '{
    "datasets": [{"id": "{datasetId}"}],
    "reports": [{"id": "{reportId}", "allowEdit": true}],
    "targetWorkspaces": [{"id": "{workspaceId}"}]
  }'
```

### Report Embed Configuration

```javascript
import * as pbi from 'powerbi-client';

const config = {
  type: 'report',
  id: reportId,
  embedUrl: embedUrl,
  accessToken: token,
  tokenType: pbi.models.TokenType.Embed,    // Embed (for customers) or Aad (for org)
  permissions: pbi.models.Permissions.All,
  viewMode: pbi.models.ViewMode.View,        // View or Edit
  settings: {
    panes: {
      filters: { visible: false },
      pageNavigation: { visible: true, position: pbi.models.PageNavigationPosition.Left }
    },
    bars: { actionBar: { visible: false }, statusBar: { visible: false } },
    background: pbi.models.BackgroundType.Transparent,
    localeSettings: { language: "en-us" },
    personalizeVisuals: { enabled: true }
  },
  theme: { themeJson: myThemeObject },       // Apply theme at load
  filters: [],                               // Report-level filters
  pageName: "ReportSection1"                 // Initial page
};

const container = document.getElementById('report-container');
const report = powerbi.embed(container, config);
```

### Phased Embedding (Faster Load)

```javascript
// Phase 1: Pre-initialize iframe early
powerbi.bootstrap(container, { type: 'report' });

// Phase 2: Embed with full config when token arrives
const report = powerbi.embed(container, fullConfig);
```

### Event Handling

```javascript
report.on('loaded', () => console.log('Report loaded'));
report.on('rendered', () => console.log('All visuals rendered'));
report.on('error', (event) => console.error(event.detail));
report.on('dataSelected', (event) => {
  const { dataPoints, filters } = event.detail;
  // React to user data selections
});
report.on('pageChanged', (event) => {
  const newPage = event.detail.newPage;
});
report.on('buttonClicked', (event) => {
  const { id, title } = event.detail;
});
```

**Key events**: `loaded`, `rendered`, `error`, `dataSelected`, `pageChanged`, `buttonClicked`, `commandTriggered`, `bookmarkApplied`, `filtersApplied`, `saved`, `saveAsTriggered`, `visualClicked`, `visualRendered` (opt-in), `selectionChanged`, `dataHyperlinkClicked`.

### Runtime Theme Switching

```javascript
// Apply a theme dynamically
await report.applyTheme({ themeJson: darkThemeObject });

// Reset to the report's original theme
await report.resetTheme();
```

### Other Embeddable Types

```javascript
// Dashboard
const dashConfig = { type: 'dashboard', id: dashId, embedUrl, accessToken, tokenType,
  pageView: 'fitToWidth' /* fitToWidth | oneColumn | actualSize */ };

// Single visual from a report
const visualConfig = { type: 'visual', id: reportId, embedUrl, accessToken, tokenType,
  pageName: 'ReportSection1', visualName: 'a1b2c3d4' };

// Q&A
const qaConfig = { type: 'qna', embedUrl, accessToken, tokenType,
  datasetIds: [datasetId], question: 'total sales by region' };
```

### React Integration

```jsx
import { PowerBIEmbed } from 'powerbi-client-react';

function ReportView({ config }) {
  return (
    <PowerBIEmbed
      embedConfig={config}
      cssClassName="report-container"
      eventHandlers={new Map([
        ['loaded', () => console.log('Loaded')],
        ['rendered', () => console.log('Rendered')],
        ['error', (e) => console.error(e.detail)]
      ])}
      getEmbeddedComponent={(component) => { /* store ref */ }}
    />
  );
}
```

---

## Report Authoring SDK

Extension of `powerbi-client` for programmatic report editing. Requires edit mode and is available after the `rendered` event.

### Visual CRUD

```javascript
// Create a visual on the current page
const { visual } = await page.createVisual('barChart',
  { x: 20, y: 35, width: 600, height: 400 },  // layout (optional)
  false                                          // autoFocus
);

// Delete a visual
await page.deleteVisual(visual.name);

// Clone a visual
await visual.clone();

// Change visual type
await visual.changeType('pieChart');
```

**Available visual types**: `actionButton`, `areaChart`, `barChart`, `basicShape`, `card`, `clusteredBarChart`, `clusteredColumnChart`, `columnChart`, `donutChart`, `filledMap`, `funnel`, `gauge`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `image`, `kpi`, `lineChart`, `lineClusteredColumnComboChart`, `lineStackedColumnComboChart`, `map`, `multiRowCard`, `pieChart`, `pivotTable`, `ribbonChart`, `scatterChart`, `slicer`, `stackedAreaChart`, `tableEx`, `textbox`, `treemap`, `waterfallChart`.

### Data Binding

```javascript
// Add a data field to a visual's data role
await visual.addDataField('category', {
  column: { property: 'ProductCategory', expression: { sourceRef: { entity: 'Products' } } }
});

// Remove a data field
await visual.removeDataField('measure', 0);

// Get current data fields
const fields = await visual.getDataFields('category');
```

### Visual Properties

```javascript
// Set a property
await visual.setProperty('legend', { show: true, position: 'Top' });

// Get available properties
const props = await visual.getProperties();

// Reset to default
await visual.resetProperty('legend');
```

### Page Operations

```javascript
await report.addPage('NewPage');
await report.deletePage('pageName');
await page.setDisplayName('Sales Dashboard');
```

### Use Cases

- ISV wizard-based report builders for end users
- Chatbot-driven visual creation from natural language
- Self-service analytics dashboards
- Batch layout modifications

---

## Custom Visuals SDK

### Setup

```bash
npm install -g powerbi-visuals-tools
pbiviz new myVisual
cd myVisual
pbiviz start    # Dev server with hot reload
pbiviz package  # Produces .pbiviz for import/publishing
```

### Project Structure

```
myVisual/
├── assets/icon.png              # 20x20 PNG
├── src/
│   ├── visual.ts                # Main visual class (IVisual)
│   └── settings.ts              # Visual properties interface
├── style/visual.less            # Stylesheet
├── capabilities.json            # Data roles, data view mappings, properties
├── pbiviz.json                  # Visual metadata (name, GUID, version, apiVersion)
├── package.json
└── tsconfig.json
```

### IVisual Lifecycle

```typescript
class MyVisual implements IVisual {
  // Called once when the visual is instantiated
  constructor(options: VisualConstructorOptions) {
    // options.element — HTMLElement to render into
    // options.host — IVisualHost services
  }

  // Called on every data/view change (data refresh, resize, filter, etc.)
  public update(options: VisualUpdateOptions): void {
    // options.dataViews — data from the model
    // options.viewport — { width, height }
    // options.type — Data | Resize | ViewMode | Style
  }

  // Called when the format pane opens
  public getFormattingModel(): FormattingModel {
    // Return formatting cards and slices
  }

  // Called on unload (rare — iframe removal is usually faster)
  public destroy(): void { }
}
```

### IVisualHost Services

The `host` object provides Power BI platform services:

| Service | Purpose |
|---------|---------|
| `createSelectionIdBuilder()` | Build selection IDs for data point interactivity |
| `createSelectionManager()` | Manage cross-visual selections and highlights |
| `colorPalette` | Theme-aware colors for data points |
| `tooltipService` | Show/hide tooltips |
| `createLocalizationManager()` | Internationalization |
| `storageService` / `storageV2Service` | Persist data locally (up to 100KB) |
| `applyJsonFilter()` | Apply filters programmatically |
| `fetchMoreData()` | Request beyond the default 1,000 row limit |
| `launchUrl()` | Open URL in new tab |
| `downloadService` | Trigger file downloads |
| `acquireAADTokenService` | Get Entra ID tokens for external APIs |
| `openModalDialog()` | Display modal dialogs |
| `persistProperties()` | Save settings with the visual definition |
| `eventService` | Signal rendering lifecycle events |

### capabilities.json

Defines the visual's data contract:

```json
{
  "dataRoles": [
    { "name": "category", "kind": "Grouping", "displayName": "Category" },
    { "name": "measure", "kind": "Measure", "displayName": "Value" }
  ],
  "dataViewMappings": [{
    "categorical": {
      "categories": { "for": { "in": "category" } },
      "values": { "select": [{ "bind": { "to": "measure" } }] }
    }
  }],
  "objects": {
    "dataColors": {
      "displayName": "Data Colors",
      "properties": {
        "fill": { "type": { "fill": { "solid": { "color": true } } } }
      }
    }
  },
  "privileges": [
    { "name": "WebAccess", "essential": true, "parameters": ["https://api.example.com"] }
  ]
}
```

### Development Workflow

1. `pbiviz new myVisual` — scaffold project
2. `pbiviz start` — launches dev server; test in Power BI Service using the Developer Visual placeholder
3. Iterate on `src/visual.ts`, `capabilities.json`, and `style/visual.less`
4. `pbiviz package` — generates `.pbiviz` file
5. Import to workspace or publish to AppSource marketplace / organizational store

---

## Paginated Reports (RDL)

### Overview

RDL (Report Definition Language) is an XML schema for paginated, pixel-perfect reports. Used in Power BI paginated reports and SQL Server Reporting Services.

### Key RDL Elements

```xml
<Report xmlns="http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition">
  <ReportParameters>
    <ReportParameter Name="StartDate">
      <DataType>DateTime</DataType>
      <Prompt>Start Date</Prompt>
    </ReportParameter>
  </ReportParameters>

  <DataSources>
    <DataSource Name="AdventureWorks">
      <ConnectionProperties>
        <DataProvider>SQL</DataProvider>
        <ConnectString>Data Source=server;Initial Catalog=db</ConnectString>
      </ConnectionProperties>
    </DataSource>
  </DataSources>

  <DataSets>
    <DataSet Name="SalesData">
      <Query>
        <DataSourceName>AdventureWorks</DataSourceName>
        <CommandText>SELECT * FROM Sales WHERE OrderDate >= @StartDate</CommandText>
      </Query>
      <Fields>
        <Field Name="OrderDate"><DataField>OrderDate</DataField></Field>
        <Field Name="Amount"><DataField>Amount</DataField></Field>
      </Fields>
    </DataSet>
  </DataSets>

  <Body>
    <ReportItems>
      <Tablix Name="SalesTable"><!-- Table definition --></Tablix>
      <Chart Name="SalesChart"><!-- Chart definition --></Chart>
      <Textbox Name="Title"><Paragraphs><Paragraph><TextRuns>
        <TextRun><Value>Sales Report</Value></TextRun>
      </TextRuns></Paragraph></Paragraphs></Textbox>
    </ReportItems>
  </Body>

  <Page>
    <PageWidth>8.5in</PageWidth>
    <PageHeight>11in</PageHeight>
    <PageHeader><Height>1in</Height></PageHeader>
    <PageFooter><Height>0.5in</Height></PageFooter>
  </Page>
</Report>
```

### Publishing RDL to Power BI

```bash
# Import .rdl file via REST API (multipart upload)
curl -X POST \
  "https://api.powerbi.com/v1.0/myorg/groups/{wsId}/imports?datasetDisplayName=MyReport" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@report.rdl"

# Or via az rest
az rest --method POST \
  --url "https://api.powerbi.com/v1.0/myorg/groups/{wsId}/imports?datasetDisplayName=MyReport" \
  --body @report.rdl
```

### RDL Design Tools

- **Power BI Report Builder** — desktop GUI for paginated reports
- **SQL Server Data Tools (SSDT)** — Visual Studio extension
- **Programmatic generation** — build XML with any XML library (Python `lxml`, .NET `XmlTextWriter`, etc.)

---

## Embed Token API Reference

### Single Report Token

| Method | Endpoint | Body |
|--------|----------|------|
| POST | `/groups/{wsId}/reports/{id}/GenerateToken` | `{"accessLevel": "View"}` |

Access levels: `View`, `Edit`, `Create`.

### Multi-Resource Token

| Method | Endpoint |
|--------|----------|
| POST | `/GenerateToken` |

```json
{
  "datasets": [{ "id": "{datasetId}" }],
  "reports": [{ "id": "{reportId}", "allowEdit": true }],
  "targetWorkspaces": [{ "id": "{workspaceId}" }],
  "lifetimeInMinutes": 60,
  "identities": [{
    "username": "user@domain.com",
    "roles": ["Reader"],
    "datasets": ["{datasetId}"]
  }]
}
```

### Token Refresh

Embed tokens expire (default 1 hour, max 24 hours). Refresh before expiry:

```javascript
report.on('tokenExpiring', async () => {
  const newToken = await fetchNewToken();
  await report.setAccessToken(newToken);
});
```
