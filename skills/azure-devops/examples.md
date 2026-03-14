# Azure DevOps Examples

## WIQL Query Patterns

### Bugs by priority
```sql
SELECT [System.Id], [System.Title], [System.State], [Microsoft.VSTS.Common.Priority]
FROM WorkItems
WHERE [System.WorkItemType] = 'Bug'
  AND [System.State] <> 'Closed'
  AND [System.State] <> 'Removed'
ORDER BY [Microsoft.VSTS.Common.Priority] ASC, [System.CreatedDate] DESC
```

### My active work across all types
```sql
SELECT [System.Id], [System.WorkItemType], [System.Title], [System.State], [System.IterationPath]
FROM WorkItems
WHERE [System.AssignedTo] = @Me
  AND [System.State] IN ('New', 'Active', 'In Progress')
ORDER BY [System.WorkItemType], [Microsoft.VSTS.Common.Priority]
```

### Items changed in last N days
```sql
SELECT [System.Id], [System.Title], [System.ChangedBy], [System.ChangedDate]
FROM WorkItems
WHERE [System.TeamProject] = @Project
  AND [System.ChangedDate] >= @Today - 7
ORDER BY [System.ChangedDate] DESC
```

### Unassigned items in current sprint
```sql
SELECT [System.Id], [System.Title], [System.WorkItemType]
FROM WorkItems
WHERE [System.AssignedTo] = ''
  AND [System.IterationPath] UNDER @CurrentIteration
  AND [System.State] <> 'Closed'
```

### Items blocked or has impediment
```sql
SELECT [System.Id], [System.Title], [System.Tags]
FROM WorkItems
WHERE [System.Tags] CONTAINS 'Blocked'
  AND [System.State] <> 'Closed'
```

## Pipeline YAML patterns

### Basic CI pipeline
```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'

  - script: |
      pip install -r requirements.txt
      pytest tests/ --jv test-results.xml
    displayName: 'Run tests'

  - task: PublishTestResults@2
    inputs:
      testResultsFiles: 'test-results.xml'
```

### Pipeline with environment approval
```yaml
stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - script: echo "Building..."

  - stage: Deploy
    dependsOn: Build
    jobs:
      - deployment: DeployJob
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - script: echo "Deploying..."
```

### Parameterized pipeline
```yaml
parameters:
  - name: environment
    displayName: 'Target Environment'
    type: string
    default: 'dev'
    values:
      - dev
      - staging
      - prod

  - name: runTests
    displayName: 'Run Tests'
    type: boolean
    default: true
```
