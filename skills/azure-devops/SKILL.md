---
name: azure-devops
description: Azure DevOps automation — pipelines, work items, repos, PRs, wiki. Use when managing DevOps pipelines, tracking work items, or working with Azure Repos.
allowed-tools: Bash(az devops *), Bash(az pipelines *), Bash(az boards *), Bash(az repos *), Bash(az artifacts *), Read, Grep
---

# Azure DevOps Automation

You have access to the `az devops` CLI extension. The user is authenticated via `az login`.

## Current context

- DevOps configuration: !`az devops configure --list 2>/dev/null || echo "not configured — run: az devops configure --defaults organization=https://dev.azure.com/ORG project=PROJECT"`

## Setup

If not configured, set defaults first:
```bash
# Install the devops extension if needed
az extension add --name azure-devops

# Configure defaults
az devops configure --defaults organization=https://dev.azure.com/<ORG> project=<PROJECT>

# Verify
az devops configure --list
```

## Pipelines

### View & monitor
```bash
# List pipeline definitions
az pipelines list --output table

# List recent runs
az pipelines runs list --output table

# Show a specific run
az pipelines runs show --id <run-id> --output table

# View run logs (for debugging failures)
az pipelines runs artifact list --run-id <run-id>
```

### Trigger & manage
```bash
# Queue a pipeline run
az pipelines run --name <pipeline-name>

# Queue with parameters
az pipelines run --name <pipeline-name> --parameters "key1=value1" "key2=value2"

# Queue on a specific branch
az pipelines run --name <pipeline-name> --branch <branch-name>

# List pipeline variables
az pipelines variable list --pipeline-name <pipeline-name> --output table

# Update a pipeline variable
az pipelines variable update --pipeline-name <pipeline-name> --name <var-name> --value <new-value>
```

## Work items

### Query & view
```bash
# List work items assigned to me
az boards work-item query --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.AssignedTo] = @Me AND [System.State] <> 'Closed' ORDER BY [System.ChangedDate] DESC"

# Show a specific work item
az boards work-item show --id <id> --output table

# View work item with all fields
az boards work-item show --id <id> --output json
```

### Create & update
```bash
# Create a work item (Bug)
az boards work-item create --type "Bug" --title "Bug title" --description "Description" --assigned-to "<email>"

# Create a work item (User Story / Task)
az boards work-item create --type "User Story" --title "Story title" --area "<area-path>" --iteration "<iteration-path>"

# Update work item state
az boards work-item update --id <id> --state "Active"

# Add a comment
az boards work-item update --id <id> --discussion "Comment text"

# Link work item to PR
az boards work-item relation add --id <work-item-id> --relation-type "ArtifactLink" --target-id <pr-id>
```

### Common WIQL queries

For more WIQL patterns, see [examples.md](examples.md).

```sql
-- Active bugs in current sprint
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
FROM WorkItems
WHERE [System.WorkItemType] = 'Bug'
  AND [System.State] = 'Active'
  AND [System.IterationPath] UNDER @CurrentIteration
ORDER BY [Microsoft.VSTS.Common.Priority]

-- Recently updated items
SELECT [System.Id], [System.Title], [System.ChangedDate]
FROM WorkItems
WHERE [System.ChangedDate] >= @Today - 7
ORDER BY [System.ChangedDate] DESC
```

## Repositories (Azure Repos)

```bash
# List repos
az repos list --output table

# Create a pull request
az repos pr create --title "PR title" --description "Description" --source-branch <source> --target-branch <target>

# List open PRs
az repos pr list --status active --output table

# View PR details
az repos pr show --id <pr-id>

# Approve a PR
az repos pr set-vote --id <pr-id> --vote approve

# List branch policies
az repos policy list --output table
```

## Wiki

```bash
# List wikis
az devops wiki list --output table

# Show a wiki page
az devops wiki page show --wiki <wiki-name> --path "<page-path>"

# Create/update a wiki page
az devops wiki page update --wiki <wiki-name> --path "<page-path>" --file-path <local-file> --version <etag>
```

## Artifacts

```bash
# List feeds
az artifacts feed list --output table

# List packages in a feed
az artifacts package list --feed <feed-name> --output table
```

## Optional: Azure DevOps MCP Server

For richer integration, install the official Azure DevOps MCP server:
```bash
npx -y @azure-devops/mcp <organization-url>
```

Domains available: `core`, `work`, `work-items`, `search`, `test-plans`, `repositories`, `wiki`, `pipelines`, `advanced-security`

Filter tools by domain: `npx -y @azure-devops/mcp <org-url> -d pipelines -d work-items`
