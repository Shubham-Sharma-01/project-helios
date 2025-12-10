# DevOps Command Center 🚀

An AI-powered productivity platform for DevOps teams that automates manual tasks, tracks work items, integrates with multiple tools via MCP, and provides intelligent notifications and dashboards.

## 🎯 Project Status: ✅ **WORKING PROTOTYPE COMPLETE!**

This is a **garage week project** that solves common DevOps productivity challenges.

## 📋 What's Built

- ✅ **Working Desktop Application** (Flet-based)
- ✅ User authentication with JWT
- ✅ Task management (create, edit, delete, filter)
- ✅ Database (SQLite with SQLAlchemy)
- ✅ Credential encryption (AES-256)
- ✅ Slack integration support
- ✅ ArgoCD integration support
- ✅ AI prioritization (Claude API)
- ✅ Notification system
- ✅ Settings/integration management UI
- ✅ **Complete setup documentation**

## 🚀 **Ready to Run!**

## 📚 Documentation

### 🌟 Start Here
- **[QUICK_START_MAC.md](QUICK_START_MAC.md)** - ⭐ **RUN THE APP (3 min)** - Quick setup for macOS
- **[SETUP_MAC.md](SETUP_MAC.md)** - Complete setup guide with troubleshooting
- **[QUICK_START.md](QUICK_START.md)** - Overview, FAQ, and getting started guide

### Planning Documents
- **[MVP_ROADMAP.md](MVP_ROADMAP.md)** - Day-by-day implementation plan with demo script
- **[PLANNING.md](PLANNING.md)** - Comprehensive architecture, tech stack, and design decisions
- **[UI_DESIGN.md](UI_DESIGN.md)** - Complete UI/UX specification with ASCII wireframes
- **[AUTHENTICATION_SPEC.md](AUTHENTICATION_SPEC.md)** - Auth system, encryption, and API endpoints
- **[INTEGRATION_CATALOG.md](INTEGRATION_CATALOG.md)** - All supported integrations with setup guides

### Technical Files (Draft)
- **[requirements.txt](requirements.txt)** - Python dependencies
- **[config.py](config.py)** - Configuration structure

## 🎨 Core Features

### MVP (Week 1)
1. ✅ **User Authentication** - UI-based credential management (no hardcoded secrets)
2. ✅ **Task Management** - Create, edit, prioritize tasks with smart views
3. ✅ **Slack Integration** - Auto-create tasks from mentions
4. ✅ **ArgoCD Monitoring** - Real-time deployment status
5. ✅ **AI Prioritization** - Claude-powered urgency detection
6. ✅ **Smart Notifications** - In-app, Slack, and desktop alerts
7. ✅ **Integration Management UI** - Add/test/manage integrations via UI

### Future Enhancements
- Team collaboration features
- GitHub & Jira integrations
- Advanced AI (summaries, recommendations)
- Analytics dashboard
- Mobile app

## ✅ Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Frontend** | Streamlit | Fastest MVP, Python-only, looks professional |
| **Database** | SQLite → PostgreSQL | Start simple, migrate for production |
| **Backend** | Flask | Simpler than FastAPI, sufficient for MVP |
| **MVP Integrations** | Slack + ArgoCD | Biggest pain points, both available |
| **Auth** | Email/password + JWT | Simple, no OAuth complexity yet |
| **AI** | Claude (Anthropic) | Best reasoning for prioritization |
| **Deployment** | Local + Docker | Easy demo and team sharing |

## 🏃 How to Run

### ⚠️ **Python Version Requirement**
- **Requires Python 3.11 or 3.12** (Python 3.13 not supported yet)
- If you have Python 3.13, see **[PYTHON313_FIX.md](PYTHON313_FIX.md)** for instructions

### Quick Start (3 minutes)
```bash
# 1. Navigate to project
cd ~/garage-week-project

# 2. Create & activate virtual environment (use 3.12 if available)
python3.12 -m venv venv
# OR: python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

**The app will open automatically!** 🎉

### First Time
1. Click "Sign up" to create account
2. Sign in with your credentials
3. Create your first task
4. (Optional) Add integrations in Settings

📖 **See [QUICK_START_MAC.md](QUICK_START_MAC.md) for detailed guide**

## 🎪 Demo Guide

Planning to demo this? See **[DEMO_GUIDE.md](DEMO_GUIDE.md)** for:
- Demo script (5-7 minutes)
- Key points to emphasize
- Expected questions & answers
- Backup plan if demo fails

## 💡 Quick Start Guide

### For Reviewers
1. Start with **[MVP_ROADMAP.md](MVP_ROADMAP.md)** - Clear week plan
2. Read **[PLANNING.md](PLANNING.md)** - Overall architecture
3. Check **[UI_DESIGN.md](UI_DESIGN.md)** - See what it will look like
4. Review **[AUTHENTICATION_SPEC.md](AUTHENTICATION_SPEC.md)** - Security approach

### For Implementation
```bash
# When ready to start coding, follow MVP_ROADMAP.md day-by-day
# All planning is complete - just execute! 🚀
```

### Questions?
- Architecture? → See PLANNING.md
- UI/UX? → See UI_DESIGN.md  
- Auth/Security? → See AUTHENTICATION_SPEC.md
- Integrations? → See INTEGRATION_CATALOG.md
- Timeline? → See MVP_ROADMAP.md

---

*Garage Week Project - Making DevOps Teams More Productive*

