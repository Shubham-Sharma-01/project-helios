#!/bin/bash
# Install mcp-use and complete the integration

echo "🚀 Installing mcp-use SDK..."
echo "================================"
echo ""

cd /Users/shubhams1/garage-week-project

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Try normal install first
echo ""
echo "📦 Installing mcp-use package..."
pip install mcp-use

# If that fails due to SSL, try with trusted hosts
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Normal install failed (likely SSL issues)"
    echo "🔄 Trying with trusted hosts..."
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org mcp-use
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ mcp-use installed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Set ANTHROPIC_API_KEY in your .env file"
    echo "   - Get key from: https://console.anthropic.com/"
    echo "   - Add to .env: ANTHROPIC_API_KEY=sk-ant-api03-..."
    echo ""
    echo "2. Configure ArgoCD (if using):"
    echo "   - ARGOCD_SERVER=localhost:8080"
    echo "   - ARGOCD_TOKEN=your-token"
    echo ""
    echo "3. Restart the app:"
    echo "   python app.py"
    echo ""
    echo "4. Test in MCP AI page:"
    echo "   Ask: 'What's the status of my deployments?'"
    echo ""
    echo "📖 For more details, see: MCP_USE_INTEGRATION_COMPLETE.md"
else
    echo ""
    echo "❌ Installation failed!"
    echo ""
    echo "Manual installation:"
    echo "1. Activate venv: source venv/bin/activate"
    echo "2. Install: pip install mcp-use"
    echo ""
    echo "If SSL issues persist:"
    echo "pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org mcp-use"
    exit 1
fi

