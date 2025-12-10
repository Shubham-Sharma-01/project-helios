# Configuration Guide

## Environment Variables

Create a `.env` file in the project root with the following variables:

### Required Settings

```bash
# Database
DATABASE_URL=sqlite:///./devops_command_center.db

# Security & Encryption
ENCRYPTION_MASTER_KEY=your-32-character-encryption-key-here
JWT_SECRET=your-jwt-secret-key-here
```

### AI Configuration

Choose your AI provider:

```bash
# AI Provider (choose one)
AI_PROVIDER=ollama  # Recommended: Free, local, private

# For Ollama (100% Free - Recommended!)
OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
OLLAMA_BASE_URL=http://localhost:11434

# OR for Anthropic Claude (requires API key)
# AI_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Optional Integrations

#### Slack (Future Feature)

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_NOTIFICATIONS_CHANNEL=#devops
```

**What Slack Integration Will Do:**
- 📢 Send deployment notifications to channels
- 🚨 Alert team about urgent tasks
- 🤖 Respond to slash commands (`/devops status`)
- 📝 Create tasks from @mentions

**Setup Steps (when ready):**
1. Go to https://api.slack.com/apps
2. Create a new Slack app
3. Add Bot Token Scopes:
   - `chat:write` - Send messages
   - `channels:read` - List channels
   - `commands` - Slash commands (optional)
   - `app_mentions:read` - Listen for @mentions (optional)
4. Install app to workspace
5. Copy Bot Token and Signing Secret to `.env`

#### Jira

```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your-jira-api-token
```

#### ArgoCD

```bash
ARGOCD_URL=https://argocd.your-company.com
ARGOCD_TOKEN=your-argocd-token
```

#### MCP Servers

```bash
ARGOCD_MCP_URL=http://localhost:3000/argocd-mcp
```

---

## AI Capabilities

Your AI assistant can:

### 📋 Task Management
- **Create tasks:** "Create a task: Deploy new API to production"
- **Delete tasks:** "Delete task test"
- **Update tasks:** "Mark task test as done"
- **List tasks:** "Show me all my tasks"
- **Get details:** "Tell me about my tasks"

### 📊 App Insights
- **Statistics:** "Show me my stats"
- **Integration status:** "List my integrations"
- **App overview:** "What's the current state of my app?"

### 🤖 Smart Understanding
- Understands natural language
- Knows all your tasks and integrations
- Provides DevOps advice
- Learns from conversation context

---

## Quick Start

1. **Install Ollama** (for free local AI):
   ```bash
   brew install ollama
   ollama pull llama3.1
   ollama serve
   ```

2. **Configure `.env`**:
   ```bash
   AI_PROVIDER=ollama
   OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
   ```

3. **Run the app**:
   ```bash
   python app.py
   ```

4. **Try AI commands**:
   - "Create a task: Test new feature"
   - "Show me all tasks"
   - "What's my app status?"

---

## Future Enhancements

### Slack Integration
When you add Slack credentials, you'll be able to:
- Get notified about deployments in Slack
- Create tasks from Slack mentions
- Use `/devops` slash commands
- Get AI responses in Slack threads

### More AI Actions
Coming soon:
- Trigger ArgoCD deployments via chat
- Get AI recommendations for task prioritization
- Natural language queries for logs
- Smart alerts and anomaly detection

---

## Troubleshooting

### Ollama Not Working?
```bash
# Check if Ollama is running
ps aux | grep ollama

# List available models
ollama list

# Pull a model
ollama pull llama3.1

# Start Ollama server
ollama serve
```

### AI Not Understanding Commands?
The AI uses pattern matching for actions like:
- "create task: ..."
- "delete task ..."
- "show tasks"
- "list integrations"

Be explicit with commands for best results!

---

## Security Notes

- **Never commit `.env` file** - It contains secrets!
- **Use strong encryption keys** - Generate with: `openssl rand -hex 32`
- **Rotate API tokens** - Especially if exposed
- **Use Ollama for privacy** - No data leaves your machine

---

For more help, check the README.md or open an issue!

