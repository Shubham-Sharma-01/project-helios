# Enable AI Features - Quick Guide

## 🤖 What AI Features Will Be Enabled?

Once you add your Anthropic API key, you'll unlock:

✅ **AI-Powered Task Prioritization** - Intelligent urgency scoring based on keywords, source, and context  
✅ **Smart Daily Summaries** - AI-generated overview of your workload  
✅ **Context-Aware Insights** - Click any task/Jira ticket to get AI recommendations  
✅ **MCP-Enhanced Analysis** - AI incorporates live ArgoCD data from MCP servers  
✅ **AI Chat Interface** - Conversational DevOps assistant with full context awareness  

---

## 📋 Setup Instructions

### Option 1: Use the Setup Script (Easiest)

```bash
cd /Users/shubhams1/garage-week-project
./setup_ai.sh
```

The script will guide you through the process interactively.

### Option 2: Manual Setup

1. **Get your API key:**
   - Go to https://console.anthropic.com/
   - Sign up or log in
   - Navigate to **API Keys**
   - Click **Create Key**
   - Copy the key (format: `sk-ant-api03-...`)

2. **Edit your `.env` file:**
   ```bash
   cd /Users/shubhams1/garage-week-project
   nano .env  # or use your preferred editor
   ```

3. **Add this line:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

4. **Save and close** (Ctrl+X, then Y if using nano)

5. **Restart the app:**
   ```bash
   pkill -9 -f "python app.py"
   sleep 2
   source venv/bin/activate
   python app.py
   ```

---

## ✅ Verify AI is Enabled

After restarting, you should see in the console:
```
✅ AI Service enabled with model: claude-3-5-sonnet-20241022
```

Instead of:
```
⚠️  ANTHROPIC_API_KEY not set - AI features disabled
```

In the app:
- Go to **MCP AI** page
- The warning message should be gone
- You can now chat with the AI assistant!
- Click on any task/ticket in the dashboard to get AI insights

---

## 💰 API Usage & Costs

**Model:** Claude 3.5 Sonnet (20241022)
- **Input:** $3 per million tokens
- **Output:** $15 per million tokens

**Typical usage per day (light use):**
- ~10 AI insights: ~$0.05
- ~20 chat messages: ~$0.10
- Task prioritization: ~$0.02
- **Total:** ~$0.17/day or **~$5/month**

💡 **Tip:** Anthropic gives new users **$5 free credit** to get started!

---

## 🔒 Security

- Your API key is stored in `.env` (already in `.gitignore`)
- Never commit `.env` to Git
- The key is only used to call Anthropic's API
- No data is stored on Anthropic's servers beyond the API call

---

## ❓ Troubleshooting

### "AI features are disabled" message persists
1. Check `.env` has the correct format: `ANTHROPIC_API_KEY=sk-ant-...`
2. No spaces around the `=` sign
3. No quotes around the key
4. Restart the app completely

### "Invalid API key" error
1. Verify the key starts with `sk-ant-api03-`
2. Check for typos when copying
3. Ensure the key is active in your Anthropic console
4. Generate a new key if needed

### App won't start after adding key
```bash
# Check for syntax errors in .env
cat .env | grep ANTHROPIC

# Verify the key format
echo $ANTHROPIC_API_KEY  # Should print your key after: source venv/bin/activate
```

---

## 🚀 Next Steps

Once AI is enabled:

1. **Try the AI Chat** - Go to "MCP AI" page and ask DevOps questions
2. **Get Task Insights** - Click any task in the dashboard to get AI recommendations
3. **Enable ArgoCD MCP** - Add an MCP server to get live infrastructure data in AI responses
4. **Connect Jira** - AI will provide insights on your tickets too!

---

**Ready to enable AI? Run the setup script:**
```bash
./setup_ai.sh
```

