# DevOps Command Center - Setup Guide for macOS

Complete guide to set up and run the DevOps Command Center on your Mac.

---

## 📋 Prerequisites

### Required Software
1. **Python 3.9 or higher**
2. **pip** (Python package manager)
3. **Git** (optional, for cloning)

### Check if you have Python installed:
```bash
python3 --version
# Should show: Python 3.9.x or higher
```

### If Python is not installed:
```bash
# Install using Homebrew (recommended)
brew install python3

# Or download from https://www.python.org/downloads/
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Navigate to Project Directory
```bash
cd ~/garage-week-project
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your terminal prompt should now show (venv)
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Flet (Desktop UI framework)
- SQLAlchemy (Database)
- bcrypt, PyJWT, cryptography (Security)
- requests (HTTP client)
- anthropic (AI - optional)
- slack-sdk (Slack integration - optional)

**Installation time:** ~2-3 minutes

### Step 4: Set Up Environment Variables (Optional)
```bash
# Copy example env file
cp .env.example .env

# Edit .env file (optional for basic usage)
nano .env
```

**For MVP, you can skip this step!** The app will generate default values.

### Step 5: Run the Application
```bash
python app.py
```

**That's it!** The app will:
1. Create the database automatically
2. Open a desktop window
3. Show the login screen

---

## 📝 First Run

### Creating Your Account
1. Click "Sign up" on the login screen
2. Enter:
   - Email: `your@email.com`
   - Password: (choose a password)
   - Full Name: (optional)
3. Click "Sign Up"
4. Now sign in with your credentials

### Dashboard
- View task statistics
- See AI insights
- Check integration status

### Creating Your First Task
1. Go to "My Tasks" in the sidebar
2. Click "➕ New Task"
3. Fill in:
   - Title: e.g., "Test the app"
   - Description: (optional)
   - Priority: Medium, High, or Urgent
4. Click "Create"

---

## 🔐 Configuration (Optional)

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required for production (optional for testing)
SECRET_KEY=your-random-secret-key-here
ENCRYPTION_MASTER_KEY=your-encryption-key-here

# Optional: AI Features (Anthropic Claude)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Optional: Slack Integration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite:///devops_command_center.db
```

### Generating Secure Keys

```bash
# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔗 Adding Integrations

### Slack Integration

**Prerequisites:**
1. Slack workspace admin access
2. Create a Slack App at https://api.slack.com/apps

**Steps:**
1. Create new Slack app
2. Enable Socket Mode
3. Add Bot Token Scopes:
   - `channels:history`
   - `chat:write`
   - `im:history`
   - `users:read`
4. Install app to workspace
5. Copy tokens:
   - Bot User OAuth Token (starts with `xoxb-`)
   - App-Level Token (starts with `xapp-`)

**In the App:**
1. Go to Settings
2. Click "➕ Add Integration"
3. Select "Slack"
4. Fill in:
   - Name: "My Workspace"
   - Bot Token: `xoxb-...`
   - App Token: `xapp-...`
5. Click "Save & Test"

### ArgoCD Integration

**Prerequisites:**
1. ArgoCD instance URL
2. API token with read access

**Getting ArgoCD Token:**
```bash
# Login to ArgoCD CLI
argocd login <ARGOCD_SERVER>

# Create token
argocd account generate-token --account <USERNAME>
```

**In the App:**
1. Go to Settings
2. Click "➕ Add Integration"
3. Select "ArgoCD"
4. Fill in:
   - Name: "Production ArgoCD"
   - Server URL: `https://argocd.example.com`
   - API Token: (your token)
5. Click "Save & Test"

### AI Features (Claude)

**Get API Key:**
1. Go to https://console.anthropic.com/
2. Create account or sign in
3. Generate API key
4. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

**Features Enabled:**
- Task prioritization
- Daily summaries
- Natural language queries

---

## 📱 Using the App

### Navigation
- **Dashboard**: Overview of all tasks and integrations
- **My Tasks**: Create, edit, and manage tasks
- **Settings**: Add and manage integrations

### Task Management

**Create Task:**
1. My Tasks → "➕ New Task"
2. Enter title, description, priority
3. Click "Create"

**Edit Task:**
1. Click "Edit" icon on task card
2. Update fields
3. Click "Save"

**Delete Task:**
1. Click "Delete" icon on task card
2. Confirm deletion

**Filter Tasks:**
- Use Status dropdown (All, To Do, In Progress, Done)
- Use Priority dropdown (All, Urgent, High, Medium, Low)

### Notifications
- Click bell icon (🔔) in top bar
- See unread notifications
- Click to mark as read
- "Mark All Read" to clear all

---

## 🛠️ Troubleshooting

### App Won't Start

**Problem:** `ModuleNotFoundError`
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** `Permission denied`
```bash
# Solution: Activate virtual environment
source venv/bin/activate
```

### Database Issues

**Problem:** Database locked or corrupted
```bash
# Solution: Delete and recreate database
rm devops_command_center.db
python app.py  # Will recreate automatically
```

### Integration Connection Failures

**Slack:** "Invalid token"
- Verify token starts with `xoxb-`
- Check token hasn't expired
- Ensure bot is installed in workspace

**ArgoCD:** "Connection timeout"
- Verify server URL is correct
- Check network connectivity
- Verify TLS settings

### Performance Issues

**Problem:** App is slow
```bash
# Check Python version (should be 3.9+)
python3 --version

# Reinstall with no cache
pip install --no-cache-dir -r requirements.txt
```

---

## 🔄 Updating the App

### Pull Latest Changes
```bash
# Activate virtual environment
source venv/bin/activate

# Pull updates
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Run app
python app.py
```

---

## 📦 Building Desktop App (Optional)

To create a standalone `.app` for macOS:

```bash
# Install packaging tool
pip install flet

# Build app
flet build macos

# Find app in: build/macos/
```

---

## 🗄️ Database Location

**SQLite Database:** `./devops_command_center.db`

### Backup Database
```bash
# Create backup
cp devops_command_center.db devops_command_center.db.backup

# Restore from backup
cp devops_command_center.db.backup devops_command_center.db
```

### View Database
```bash
# Install SQLite browser
brew install --cask db-browser-for-sqlite

# Open database
open devops_command_center.db
```

---

## 🧪 Development Mode

### Running with Auto-Reload
```bash
# Install watchdog for auto-reload
pip install watchdog

# Run with flet in dev mode
flet run app.py --web  # Web version for debugging
```

### Checking Logs
```bash
# App logs to stdout
python app.py 2>&1 | tee app.log
```

### Resetting Everything
```bash
# Delete database and start fresh
rm devops_command_center.db

# Clear client storage (logout)
# Click "Sign Out" in app, then delete:
rm -rf ~/.flet/
```

---

## 🚀 Next Steps

1. ✅ Create your account
2. ✅ Create a few test tasks
3. ✅ Add a Slack integration (if you have access)
4. ✅ Add an ArgoCD integration (if you have access)
5. ✅ Test AI prioritization (if you added API key)
6. ✅ Explore the dashboard
7. ✅ Share with your team!

---

## 📞 Getting Help

### Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Check installed packages
pip list

# Update a specific package
pip install --upgrade flet

# Run app
python app.py

# Stop app
# Press Cmd+C in terminal
```

### File Structure
```
garage-week-project/
├── app.py                          # Main application entry
├── backend/                        # Backend services
│   ├── auth.py                     # Authentication
│   ├── database.py                 # Database setup
│   ├── models.py                   # Data models
│   ├── services/                   # Business logic
│   │   ├── task_service.py
│   │   ├── integration_service.py
│   │   ├── notification_service.py
│   │   ├── ai_service.py
│   │   └── credential_vault.py
│   └── integrations/               # Integration connectors
│       ├── slack_integration.py
│       └── argocd_integration.py
├── frontend/                       # Frontend UI
│   ├── pages/                      # App pages
│   │   ├── login_page.py
│   │   ├── dashboard_page.py
│   │   ├── tasks_page.py
│   │   └── settings_page.py
│   ├── components/                 # Reusable components
│   │   ├── sidebar.py
│   │   └── topbar.py
│   └── state.py                    # App state management
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (you create this)
└── devops_command_center.db        # SQLite database (auto-created)
```

---

## 🎉 Success!

You should now have a fully functional DevOps Command Center running on your Mac!

**Features Available:**
- ✅ User authentication
- ✅ Task management (CRUD)
- ✅ Priority-based filtering
- ✅ Integration management
- ✅ Slack & ArgoCD support
- ✅ AI prioritization (with API key)
- ✅ Notifications
- ✅ Modern desktop UI

**Next:** Customize with your integrations and start managing your DevOps tasks!

---

*For more detailed documentation, see the planning docs in the project root.*

