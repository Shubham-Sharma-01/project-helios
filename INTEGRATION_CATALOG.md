# Integration Catalog - Supported MCP Servers

This document defines all available integrations, their configuration schemas, and how to set them up through the UI.

---

## 🔷 ArgoCD

### Description
Monitor and manage ArgoCD applications, deployments, and sync status.

### Category
CI/CD, GitOps

### Capabilities
- List all applications
- View application details and health
- Monitor sync status
- View deployment logs
- Trigger manual syncs
- View application events
- Auto-create tasks for failed syncs

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "server_url": {
      "type": "string",
      "title": "ArgoCD Server URL",
      "description": "Full URL to your ArgoCD server (e.g., https://argocd.example.com)",
      "required": true,
      "format": "uri"
    },
    "namespace": {
      "type": "string",
      "title": "ArgoCD Namespace",
      "description": "Kubernetes namespace where ArgoCD is installed",
      "default": "argocd",
      "required": false
    },
    "tls_verify": {
      "type": "boolean",
      "title": "Verify TLS Certificate",
      "description": "Verify SSL/TLS certificates (disable for self-signed certs)",
      "default": true,
      "required": false
    },
    "sync_interval": {
      "type": "integer",
      "title": "Sync Interval (seconds)",
      "description": "How often to sync application status",
      "default": 300,
      "minimum": 60,
      "required": false
    },
    "monitor_namespaces": {
      "type": "array",
      "title": "Monitor Specific Namespaces",
      "description": "Only monitor applications in these namespaces (leave empty for all)",
      "items": {"type": "string"},
      "required": false
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "credential_type": {
      "type": "string",
      "enum": ["api_token", "username_password"],
      "default": "api_token",
      "title": "Authentication Method"
    },
    "auth_token": {
      "type": "string",
      "title": "API Token",
      "description": "ArgoCD API authentication token",
      "required": true,
      "sensitive": true,
      "show_if": {"credential_type": "api_token"}
    },
    "username": {
      "type": "string",
      "title": "Username",
      "required": false,
      "show_if": {"credential_type": "username_password"}
    },
    "password": {
      "type": "string",
      "title": "Password",
      "format": "password",
      "required": false,
      "sensitive": true,
      "show_if": {"credential_type": "username_password"}
    }
  }
}
```

### Setup Instructions

1. Login to your ArgoCD instance
2. Navigate to Settings → Accounts → {your-account}
3. Click "Generate New Token"
4. Give it a name (e.g., "DevOps Command Center")
5. Copy the generated token
6. Paste it in the "API Token" field

### Notification Settings

- **Sync Failed**: Create urgent task when application sync fails
- **Health Degraded**: Alert when application health is degraded
- **New Application**: Notify when new application is detected
- **Out of Sync**: Alert when application drift is detected

---

## 🐙 GitHub

### Description
Track pull requests, issues, code reviews, and repository activity.

### Category
Source Control, Code Review

### Capabilities
- List repositories
- Track pull requests
- Monitor code review requests
- View issues assigned to you
- Track repository activity
- Auto-create tasks for PR reviews
- Monitor CI/CD status

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "organization": {
      "type": "string",
      "title": "GitHub Organization",
      "description": "Your GitHub organization or username",
      "required": false
    },
    "repositories": {
      "type": "array",
      "title": "Repositories to Monitor",
      "description": "Specific repos to track (leave empty for all accessible repos)",
      "items": {"type": "string"},
      "required": false
    },
    "track_prs": {
      "type": "boolean",
      "title": "Track Pull Requests",
      "default": true
    },
    "track_issues": {
      "type": "boolean",
      "title": "Track Issues",
      "default": true
    },
    "track_reviews": {
      "type": "boolean",
      "title": "Track Review Requests",
      "default": true
    },
    "sync_interval": {
      "type": "integer",
      "title": "Sync Interval (seconds)",
      "default": 300,
      "minimum": 60
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "credential_type": {
      "type": "string",
      "enum": ["personal_access_token", "oauth"],
      "default": "personal_access_token"
    },
    "access_token": {
      "type": "string",
      "title": "Personal Access Token",
      "description": "GitHub Personal Access Token with repo access",
      "required": true,
      "sensitive": true,
      "show_if": {"credential_type": "personal_access_token"}
    }
  }
}
```

### Setup Instructions

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy the generated token
5. Paste it in the "Access Token" field

---

## 📢 Slack

### Description
Track mentions, create tasks from messages, send notifications and status updates.

### Category
Communication, Notifications

### Capabilities
- Track mentions
- Monitor specific channels
- Create tasks from messages
- Send notifications
- Update status in channels
- Thread tracking
- Priority detection with AI

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "workspace_id": {
      "type": "string",
      "title": "Workspace ID",
      "description": "Your Slack workspace ID",
      "required": true
    },
    "track_mentions": {
      "type": "boolean",
      "title": "Track Mentions",
      "description": "Auto-create tasks from mentions",
      "default": true
    },
    "track_channels": {
      "type": "array",
      "title": "Monitor Channels",
      "description": "Specific channels to track (e.g., #incidents, #production)",
      "items": {"type": "string"},
      "required": false
    },
    "priority_keywords": {
      "type": "array",
      "title": "Priority Keywords",
      "description": "Keywords that indicate urgent messages",
      "items": {"type": "string"},
      "default": ["urgent", "critical", "asap", "emergency", "down"],
      "required": false
    },
    "track_threads": {
      "type": "boolean",
      "title": "Track Threads",
      "description": "Monitor threads where you're mentioned",
      "default": true
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "bot_token": {
      "type": "string",
      "title": "Bot User OAuth Token",
      "description": "Starts with xoxb-",
      "required": true,
      "sensitive": true,
      "pattern": "^xoxb-"
    },
    "app_token": {
      "type": "string",
      "title": "App-Level Token",
      "description": "Starts with xapp- (for Socket Mode)",
      "required": true,
      "sensitive": true,
      "pattern": "^xapp-"
    },
    "signing_secret": {
      "type": "string",
      "title": "Signing Secret",
      "description": "For request verification",
      "required": true,
      "sensitive": true
    }
  }
}
```

### Setup Instructions

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Enable Socket Mode
4. Add Bot Token Scopes: `channels:history`, `chat:write`, `im:history`, `users:read`
5. Install app to workspace
6. Copy tokens from OAuth & Permissions page

---

## 📝 Jira

### Description
Sync Jira issues, track project progress, update ticket status.

### Category
Project Management, Issue Tracking

### Capabilities
- List issues assigned to you
- Track sprint progress
- Sync issue status
- Create/update issues
- Link tasks to Jira tickets
- Track story points
- Monitor project health

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "server_url": {
      "type": "string",
      "title": "Jira Server URL",
      "description": "Your Jira instance URL (e.g., https://company.atlassian.net)",
      "required": true,
      "format": "uri"
    },
    "project_keys": {
      "type": "array",
      "title": "Project Keys",
      "description": "Specific projects to track (e.g., PROJ, TEAM)",
      "items": {"type": "string"},
      "required": false
    },
    "track_sprints": {
      "type": "boolean",
      "title": "Track Active Sprints",
      "default": true
    },
    "sync_interval": {
      "type": "integer",
      "title": "Sync Interval (seconds)",
      "default": 300,
      "minimum": 60
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "title": "Email",
      "description": "Your Jira account email",
      "format": "email",
      "required": true
    },
    "api_token": {
      "type": "string",
      "title": "API Token",
      "description": "Jira API token",
      "required": true,
      "sensitive": true
    }
  }
}
```

### Setup Instructions

1. Go to https://id.atlassian.com/manage/api-tokens
2. Click "Create API token"
3. Give it a label
4. Copy the generated token
5. Use your Atlassian account email and the token

---

## ☁️ Kubernetes

### Description
Monitor Kubernetes clusters, pods, deployments, and resources.

### Category
Infrastructure, Container Orchestration

### Capabilities
- List clusters
- Monitor pod status
- View deployment health
- Track resource usage
- View logs
- Auto-create alerts for pod failures
- Monitor namespaces

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "cluster_name": {
      "type": "string",
      "title": "Cluster Name",
      "description": "Friendly name for this cluster",
      "required": true
    },
    "api_server_url": {
      "type": "string",
      "title": "API Server URL",
      "description": "Kubernetes API server URL",
      "required": true,
      "format": "uri"
    },
    "namespaces": {
      "type": "array",
      "title": "Monitor Namespaces",
      "description": "Specific namespaces to track (empty = all)",
      "items": {"type": "string"},
      "required": false
    },
    "sync_interval": {
      "type": "integer",
      "title": "Sync Interval (seconds)",
      "default": 60,
      "minimum": 30
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "credential_type": {
      "type": "string",
      "enum": ["bearer_token", "kubeconfig", "service_account"],
      "default": "bearer_token"
    },
    "bearer_token": {
      "type": "string",
      "title": "Bearer Token",
      "required": false,
      "sensitive": true,
      "show_if": {"credential_type": "bearer_token"}
    },
    "kubeconfig": {
      "type": "string",
      "title": "Kubeconfig File Content",
      "format": "textarea",
      "required": false,
      "sensitive": true,
      "show_if": {"credential_type": "kubeconfig"}
    },
    "ca_cert": {
      "type": "string",
      "title": "CA Certificate",
      "format": "textarea",
      "required": false,
      "sensitive": true
    }
  }
}
```

---

## 📊 Datadog

### Description
Monitor metrics, alerts, and infrastructure health from Datadog.

### Category
Monitoring, Observability

### Capabilities
- Track active alerts
- Monitor metrics
- View dashboards
- Create tasks from alerts
- Track incident status
- SLO monitoring

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "site": {
      "type": "string",
      "title": "Datadog Site",
      "enum": ["datadoghq.com", "us3.datadoghq.com", "us5.datadoghq.com", "datadoghq.eu", "ddog-gov.com"],
      "default": "datadoghq.com",
      "required": true
    },
    "track_monitors": {
      "type": "boolean",
      "title": "Track Monitors",
      "default": true
    },
    "alert_priority_threshold": {
      "type": "string",
      "title": "Alert Priority Threshold",
      "enum": ["P1", "P2", "P3", "P4", "P5"],
      "default": "P3",
      "description": "Only create tasks for alerts at or above this priority"
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "api_key": {
      "type": "string",
      "title": "API Key",
      "required": true,
      "sensitive": true
    },
    "app_key": {
      "type": "string",
      "title": "Application Key",
      "required": true,
      "sensitive": true
    }
  }
}
```

---

## 🔔 PagerDuty

### Description
Track incidents, on-call schedules, and alerts from PagerDuty.

### Category
Incident Management, On-Call

### Capabilities
- List active incidents
- Track on-call schedule
- Auto-create tasks from incidents
- Update incident status
- View incident timeline
- Acknowledge/resolve incidents

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "account_subdomain": {
      "type": "string",
      "title": "Account Subdomain",
      "description": "Your PagerDuty subdomain (e.g., 'company' from company.pagerduty.com)",
      "required": true
    },
    "track_all_incidents": {
      "type": "boolean",
      "title": "Track All Team Incidents",
      "description": "Track all incidents (not just assigned to you)",
      "default": false
    },
    "auto_create_tasks": {
      "type": "boolean",
      "title": "Auto-Create Tasks for Incidents",
      "default": true
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "api_token": {
      "type": "string",
      "title": "API Token",
      "description": "PagerDuty API token with read/write access",
      "required": true,
      "sensitive": true
    },
    "user_email": {
      "type": "string",
      "title": "Your PagerDuty Email",
      "format": "email",
      "required": true
    }
  }
}
```

---

## 📈 Grafana

### Description
Monitor Grafana dashboards, alerts, and metrics.

### Category
Monitoring, Visualization

### Capabilities
- List dashboards
- Track alerts
- View dashboard snapshots
- Create tasks from alerts
- Monitor panel metrics

### Configuration Schema

```json
{
  "type": "object",
  "properties": {
    "server_url": {
      "type": "string",
      "title": "Grafana Server URL",
      "description": "Your Grafana instance URL",
      "required": true,
      "format": "uri"
    },
    "dashboards": {
      "type": "array",
      "title": "Monitor Specific Dashboards",
      "description": "Dashboard UIDs to track (empty = all)",
      "items": {"type": "string"},
      "required": false
    }
  }
}
```

### Credential Schema

```json
{
  "type": "object",
  "properties": {
    "credential_type": {
      "type": "string",
      "enum": ["api_key", "service_account"],
      "default": "api_key"
    },
    "api_key": {
      "type": "string",
      "title": "API Key",
      "required": true,
      "sensitive": true
    }
  }
}
```

---

## 🔧 Future Integrations

### Planned
- **GitLab**: CI/CD and code management
- **Jenkins**: CI/CD pipeline monitoring
- **Terraform Cloud**: Infrastructure as Code
- **AWS**: Cloud resource monitoring
- **Azure DevOps**: Project management and CI/CD
- **Sentry**: Error tracking
- **New Relic**: APM monitoring
- **Prometheus**: Metrics and alerting

### Community Requests
Submit integration requests via GitHub issues or the settings page!

---

*This catalog will be updated as new integrations are added.*

