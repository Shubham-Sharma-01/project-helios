# 🚀 MCP AI - Quick Start Guide

Get started with MCP AI in under 5 minutes!

## ✅ Prerequisites

- DevOps Command Center app running
- User account created and logged in
- At least one MCP server to connect to (ArgoCD, GitHub, or custom)

## 🎯 Step-by-Step Setup

### Step 1: Open MCP AI (10 seconds)

1. Look at the left sidebar
2. Click on **"MCP AI"** (🤖 robot icon)
3. You should see the split-view interface

```
✓ You're in! Now you'll see:
  - Left: MCP Servers list (empty at first)
  - Right: Chat interface
```

### Step 2: Add Your First MCP (2 minutes)

#### For ArgoCD MCP:

1. Click the **"+"** button (top-right of left panel)
2. Select **"🔷 ArgoCD MCP"** from dropdown
3. Fill in:
   ```
   Name: Production ArgoCD
   Description: Main production cluster
   Server URL: https://argocd.yourcompany.com
   Namespace: argocd
   API Token: [paste your ArgoCD token]
   ```
4. Click **"Save & Test"**
5. Wait for ✅ success message

#### For GitHub MCP:

1. Click the **"+"** button
2. Select **"🐙 GitHub MCP"**
3. Fill in:
   ```
   Name: Company GitHub
   Description: Main organization
   Organization: your-org-name
   Access Token: [paste your GitHub PAT]
   ```
4. Click **"Save & Test"**

#### For Custom MCP:

1. Click the **"+"** button
2. Select **"⚙️ Custom MCP"**
3. Fill in:
   ```
   Name: My Custom Server
   Description: Custom integration
   Endpoint URL: http://localhost:3000
   API Key: [optional]
   ```
4. Click **"Save & Test"**

### Step 3: Start Chatting (30 seconds)

1. **Select your MCP** from the dropdown at the top-right
   - Look for: `[Select MCP Server ▼]`
   - Click and choose your newly added MCP

2. **Type your first question** in the input box at the bottom:
   ```
   For ArgoCD: "Show me all applications"
   For GitHub: "List recent pull requests"
   For Custom: "help" or "status"
   ```

3. **Press Enter** or click the **"►"** send button

4. **View the response** in the chat area!

```
You: Show me all applications

🤖 MCP Assistant: 
Applications:
- app1: Healthy, Synced ✓
- app2: Degraded, OutOfSync ⚠
- app3: Healthy, Synced ✓
```

## 💡 Quick Tips

### Tip 1: Multiple MCPs
You can add as many MCP servers as you want! Just keep clicking "+" and adding them.

### Tip 2: Switch Between MCPs
Change MCP server mid-conversation by selecting a different one from the dropdown.

### Tip 3: Test Connections
If an MCP shows ⚠ Error status, click **"Test"** to see what's wrong.

### Tip 4: Edit MCPs
Need to update credentials? Click **"Edit"** on any MCP card (coming soon - currently delete and re-add).

### Tip 5: Quick Send
Press **Enter** in the message box to send (no need to click Send button).

## 🎨 Understanding Status Colors

- 🟢 **Active** - Ready to use, connection verified
- 🟠 **Pending** - Just added, needs testing
- 🔴 **Error** - Connection failed, check settings
- ⚫ **Disabled** - Manually turned off

## 📝 Example Conversations

### Example 1: ArgoCD Application Check
```
You: Show me all applications

🤖: Applications:
- app1: Healthy, Synced
- app2: Degraded, OutOfSync
- app3: Healthy, Synced

Would you like details on any specific application?

You: What's wrong with app2?

🤖: app2 is showing Degraded status...
```

### Example 2: GitHub PRs
```
You: List recent pull requests

🤖: Recent Pull Requests:
#123 - Fix bug in API (Open)
#122 - Update dependencies (Merged)
#121 - Add new feature (Open)

You: Show me details for #123

🤖: PR #123: Fix bug in API
Status: Open
Author: john.doe
Created: 2 days ago
...
```

## 🐛 Common Issues & Solutions

### Issue: "Please select an MCP server first"
**Solution**: Click the dropdown at top-right and select an MCP.

### Issue: MCP shows Error status
**Solutions**:
1. Click **"Test"** to see error message
2. Verify server URL is correct
3. Check if API token is valid
4. Ensure server is reachable from your network

### Issue: No MCPs in dropdown
**Solution**: Add at least one MCP with Active status first.

### Issue: Can't add MCP
**Solutions**:
1. Fill in all required fields (marked with *)
2. Use valid URL format: `https://...` or `http://...`
3. Provide credentials

## 🎓 Next Steps

Once you're comfortable with the basics:

1. **Add more MCPs** - Connect all your infrastructure
2. **Explore different queries** - Each MCP type supports different operations
3. **Monitor regularly** - Use MCP AI for daily infrastructure checks
4. **Integrate workflows** - Make MCP AI part of your DevOps routine

## 📚 Learn More

- **Full Documentation**: See `MCP_AI_GUIDE.md`
- **Visual Guide**: See `MCP_VISUAL_GUIDE.md`
- **Implementation Details**: See `MCP_IMPLEMENTATION_SUMMARY.md`

## ✨ Pro Tips

### Tip 1: Descriptive Names
Use clear, descriptive names for your MCPs:
- ✅ "Production ArgoCD VA6"
- ✅ "GitHub Main Org"
- ❌ "mcp1"
- ❌ "test"

### Tip 2: Test First
Always test MCP connections before relying on them.

### Tip 3: Keep Tokens Fresh
Rotate API tokens regularly and update MCP credentials.

### Tip 4: Use Descriptions
Add descriptions to remember what each MCP is for.

### Tip 5: Organize by Environment
Name MCPs by environment:
- "Production ArgoCD"
- "Staging ArgoCD"
- "Dev ArgoCD"

## 🎉 You're Ready!

That's it! You now have a centralized place to manage and interact with all your MCP servers. Enjoy your new AI assistant! 🤖

---

**Questions?** Check the full guide in `MCP_AI_GUIDE.md`

**Issues?** Review troubleshooting section in the guide

**Want to contribute?** See `MCP_IMPLEMENTATION_SUMMARY.md` for technical details

