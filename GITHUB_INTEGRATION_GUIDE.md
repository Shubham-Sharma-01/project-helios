# 🐙 GitHub Integration Guide

## Welcome to AI-Powered GitHub Control!

Your AI agent can now interact with GitHub repositories, pull requests, issues, and more - all through natural language!

---

## 🚀 Quick Setup (2 Easy Steps!)

### Step 1: Get GitHub Personal Access Token

1. **Go to GitHub Settings:**
   - **Direct link:** https://github.com/settings/tokens
   - Or navigate: GitHub → Settings → (scroll down) Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token (Classic):**
   - Click "Generate new token (classic)"
   - Give it a descriptive name: "DevOps Command Center"
   - Select scopes (permissions):
     - ✅ `repo` (Full control of private repositories)
       - Includes: status, deployment, public_repo, invite, security_events
     - ✅ `read:org` (Read org data - optional if you want to access org repos)
     - ✅ `read:user` (Read user data)
   - **Expiration:** Choose based on your security policy (30/60/90 days or No expiration)
   - Click "Generate token" at the bottom

3. **Copy the Token:**
   - ⚠️ **IMPORTANT:** Copy the token immediately! You won't be able to see it again.
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Add Integration in Your App

**No need to edit files!** Add it through the UI:

1. **Open your app**
2. **Go to:** Settings (⚙️ icon in sidebar)
3. **Click:** "Add Integration" button
4. **Select:** Type → "GitHub"
5. **Fill in:**
   - **Name:** "My GitHub" (or any name you want)
   - **Organization/Username:** (optional) Your GitHub username or org
   - **Personal Access Token:** Paste the token you copied
6. **Click:** "Save & Test"
7. **You should see:** ✅ "Connected to GitHub as [your name]"

### Step 3: Test It!

Go to **MCP AI** page and try:

```
"List my GitHub repos"
"Show PRs for owner/repo"
```

**That's it!** 🎉 No `.env` files, no restarts needed!

---

## 🎯 What You Can Do

### 📚 Repository Management

**List Repositories:**
```
"Show my GitHub repos"
"List repos for facebook"
"Show repositories for microsoft"
```

**Repository Stats:**
```
"Show repo stats for owner/repo"
"Get info about facebook/react"
"Repository statistics for torvalds/linux"
```

**Example Response:**
```
📊 Repository Statistics: facebook/react

Engagement:
• ⭐ Stars: 223,567
• 🔀 Forks: 45,892
• 👀 Watchers: 6,789
• 🐛 Open Issues: 892

Top Contributors:
• user1: 1,234 contributions
• user2: 891 contributions

Languages: JavaScript, TypeScript, CSS, HTML
```

---

### 🔀 Pull Request Operations

**List PRs:**
```
"Show PRs for owner/repo"
"List open PRs for myorg/myrepo"
"Show closed PRs for owner/repo"
"What pull requests are open in owner/repo?"
```

**Example Response:**
```
🔀 Pull Requests for owner/repo (open):

🟢 PR #123: Add new authentication feature
   By: john-doe | feature/auth → main
   Labels: enhancement, security
   🔗 https://github.com/owner/repo/pull/123

🟢 PR #122: Fix memory leak in API
   By: jane-smith | bugfix/memory-leak → main
   Labels: bug, critical
   🔗 https://github.com/owner/repo/pull/122
```

---

### 🐛 Issue Management

**List Issues:**
```
"Show issues for owner/repo"
"List bugs for myorg/myrepo"
"What issues are open in owner/repo?"
```

**Create Issues:**
```
"Create issue in owner/repo: Fix login bug"
"Add issue to myorg/myrepo: Add dark mode"
"Report bug in owner/repo: API returns 500"
```

**Example Response:**
```
✅ GitHub Issue Created!

Issue #456: Fix login bug
Repository: owner/repo
URL: https://github.com/owner/repo/issues/456
```

---

### 📝 Commit History

**List Commits:**
```
"Show commits for owner/repo"
"Show last 20 commits for myorg/myrepo"
"Recent commits for facebook/react"
```

**Example Response:**
```
📝 Recent Commits for owner/repo:

• a1b2c3d - Add user authentication endpoint
  By: john-doe | 2 hours ago

• e4f5g6h - Fix database migration bug
  By: jane-smith | 5 hours ago

• i7j8k9l - Update dependencies
  By: admin | 1 day ago
```

---

### 🌿 Branch Management

**List Branches:**
```
"Show branches for owner/repo"
"List branches for myorg/myrepo"
"What branches exist in owner/repo?"
```

**Example Response:**
```
🌿 Branches for owner/repo:

• main 🔒
  Last commit: a1b2c3d

• develop
  Last commit: e4f5g6h

• feature/new-api
  Last commit: i7j8k9l
```

---

## 💡 Pro Tips

### 1. **Set Default Repository**
If you mostly work on one repo, you can ask the AI to remember it:
```
"Set default repository to owner/repo"
```

Then you can just ask:
```
"Show PRs"  (instead of "Show PRs for owner/repo")
```

### 2. **Combine with Tasks**
```
"Create a task to review PR #123 in owner/repo"
→ Creates task AND shows PR details
```

### 3. **Quick Status Checks**
```
"Give me GitHub status for owner/repo"
→ Shows PRs, issues, recent commits all at once
```

### 4. **Natural Language**
The AI understands variations:
- "What's happening in my repos?"
- "Show me pull requests that need review"
- "Any bugs reported in owner/repo?"

---

## 🔐 Security Best Practices

### Token Security:
1. ✅ **Never commit `.env` file** - It's in .gitignore
2. ✅ **Use limited scopes** - Only grant necessary permissions
3. ✅ **Set expiration** - Rotate tokens regularly
4. ✅ **Revoke if exposed** - Immediately revoke compromised tokens
5. ✅ **Use classic tokens** - Fine-grained tokens coming soon

### Permissions Needed:
- **Minimum:** `public_repo` (for public repos only)
- **Recommended:** `repo` (for private repos)
- **Optional:** `read:org` (for organization repos)

### Token Revocation:
If you need to revoke the token:
- Go to: https://github.com/settings/tokens
- Find your token
- Click "Delete" or "Revoke"

---

## 🎬 Complete Usage Examples

### Morning Check-In:
```
You: "Show my repos and what PRs are open"

AI: 📚 Your GitHub Repositories:
    1. my-api (Python) - ⭐ 45 stars
    2. frontend-app (TypeScript) - ⭐ 23 stars
    
    🔀 Open Pull Requests:
    • my-api: PR #12 - Add authentication
    • frontend-app: PR #8 - Fix responsive layout
    
    💡 You have 2 PRs waiting for review!
```

### Code Review Workflow:
```
You: "Show PRs for myorg/backend-api"

AI: [Lists all open PRs]

You: "Create a task to review PR #45"

AI: ✅ Task created: Review PR #45
    🔗 Link: https://github.com/myorg/backend-api/pull/45
```

### Bug Reporting:
```
You: "Create issue in myorg/app: Users can't login on mobile"

AI: ✅ GitHub Issue Created!
    Issue #789: Users can't login on mobile
    Repository: myorg/app
    URL: https://github.com/myorg/app/issues/789
    
    💡 Would you like me to create a task to track this issue?
```

### Release Planning:
```
You: "Show commits for myorg/api from last week"

AI: [Shows commit history]

You: "Based on these commits, recommend what to include in next release"

AI: [AI analyzes commits and suggests release notes]
```

---

## 🔥 Advanced Features

### Multi-Repo Operations:
```
"Show PRs for all my repositories"
"What issues are open across my projects?"
"Which repos need attention?"
```

### Smart Filters:
```
"Show critical bugs in owner/repo"
"List PRs with label 'security'"
"Find issues created this week"
```

### Integration with Tasks:
```
"Create tasks for all open PRs in owner/repo"
"Track issue #123 as a task"
"Show my GitHub tasks"
```

---

## 🆘 Troubleshooting

### "GitHub integration not configured"
**Solution:** Add `GITHUB_TOKEN` to your `.env` file

### "Failed to fetch repositories"
**Possible causes:**
1. Token expired → Generate new token
2. Wrong token → Verify token is correct
3. Network issue → Check internet connection
4. Rate limit → Wait a few minutes (GitHub limits API calls)

### "Repository not found"
**Solution:** Check:
- Repository name is correct (case-sensitive)
- You have access to the repository
- Repository exists and isn't deleted

### "Permission denied"
**Solution:** Your token needs more scopes:
- Go to https://github.com/settings/tokens
- Edit your token
- Add `repo` scope
- Save and update `.env` file

---

## 📊 What's Included

### Current Features: ✅
- ✅ List repositories
- ✅ Get repository stats
- ✅ List pull requests
- ✅ Get PR details
- ✅ List issues
- ✅ Create issues
- ✅ List commits
- ✅ List branches
- ✅ Natural language parsing

### Coming Soon: 🔜
- 🔜 Create pull requests
- 🔜 Merge PRs
- 🔜 Review code
- 🔜 Create branches
- 🔜 Tag releases
- 🔜 Code search
- 🔜 Workflow triggers
- 🔜 GitHub Actions integration

---

## 🎯 Best Practices

### Daily Workflow:
1. **Morning:** `"Show my repos and open PRs"`
2. **Code Review:** `"List PRs needing review in owner/repo"`
3. **Bug Triage:** `"Show critical issues in owner/repo"`
4. **End of Day:** `"What commits were made today in owner/repo?"`

### Team Collaboration:
- Use GitHub integration to stay updated on team activity
- Create tasks from GitHub issues
- Track PR reviews
- Monitor repository health

### DevOps Integration:
- Link deployments to commits
- Track release progress
- Monitor code quality
- Coordinate releases with tasks

---

## 🎉 Example Conversations

### Repository Discovery:
```
You: "Show my repos"
AI: [Lists your repositories]

You: "Tell me more about myorg/api"
AI: [Shows detailed stats, contributors, languages]

You: "What branches exist?"
AI: [Lists all branches]
```

### PR Review Session:
```
You: "Show open PRs for myorg/backend"
AI: [Lists open PRs]

You: "Show details for PR #45"
AI: [Shows PR details, changes, status]

You: "Create task to review this"
AI: [Creates task with PR link]
```

### Issue Management:
```
You: "What bugs are open in myorg/frontend?"
AI: [Lists open issues]

You: "Create issue: Add dark mode support"
AI: [Creates GitHub issue]

You: "Track this as a high priority task"
AI: [Creates task linked to issue]
```

---

## 🌟 Why This Is Powerful

### Traditional Approach:
1. Open GitHub.com
2. Navigate to repository
3. Click through menus
4. Manually check PRs, issues
5. Copy/paste to task manager

### With AI Integration:
1. **Ask in natural language**
2. **Done!** ✨

**Time saved:** 5-10 minutes per check  
**Convenience:** 10x better  
**Context switching:** Eliminated  

---

## 🚀 Ready to Get Started?

1. **Get your GitHub token** (5 minutes)
2. **Add to `.env` file**
3. **Restart app**
4. **Try:** `"List my GitHub repos"`

**That's it!** 🎉

Your AI agent is now a **GitHub power user**! 🐙✨

---

## 📚 Commands Cheat Sheet

```bash
# Repositories
"List my repos"
"Show repos for <org>"
"Repo stats for <owner>/<repo>"

# Pull Requests
"Show PRs for <owner>/<repo>"
"List open PRs for <owner>/<repo>"
"PR #<number> details"

# Issues
"Show issues for <owner>/<repo>"
"Create issue in <owner>/<repo>: <title>"

# Commits
"Show commits for <owner>/<repo>"
"Last 20 commits for <owner>/<repo>"

# Branches
"List branches for <owner>/<repo>"

# Help
"GitHub help"
"What can I do with GitHub?"
```

---

**Go try it out!** Your AI is now GitHub-enabled! 🚀🐙

