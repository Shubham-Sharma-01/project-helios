#!/bin/bash
# Setup script to enable AI features

echo "🤖 DevOps Command Center - AI Setup"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    touch .env
fi

# Check if API key is already set
if grep -q "ANTHROPIC_API_KEY=" .env; then
    echo "✅ ANTHROPIC_API_KEY already exists in .env"
    echo ""
    echo "Current value:"
    grep "ANTHROPIC_API_KEY=" .env | sed 's/ANTHROPIC_API_KEY=sk-ant-api03-.*/ANTHROPIC_API_KEY=sk-ant-api03-***hidden***/'
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping update."
        exit 0
    fi
fi

echo ""
echo "📝 To get your Anthropic API key:"
echo "   1. Visit: https://console.anthropic.com/"
echo "   2. Sign up or log in"
echo "   3. Navigate to 'API Keys'"
echo "   4. Click 'Create Key' and copy it"
echo ""
read -p "Enter your Anthropic API key (sk-ant-api03-...): " api_key

# Validate key format
if [[ ! $api_key =~ ^sk-ant-api ]]; then
    echo "❌ Invalid key format. Key should start with 'sk-ant-api'"
    exit 1
fi

# Update or add the key
if grep -q "ANTHROPIC_API_KEY=" .env; then
    # Update existing
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$api_key/" .env
    else
        # Linux
        sed -i "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$api_key/" .env
    fi
    echo "✅ Updated ANTHROPIC_API_KEY in .env"
else
    # Add new
    echo "" >> .env
    echo "# Anthropic API Key for AI Features" >> .env
    echo "ANTHROPIC_API_KEY=$api_key" >> .env
    echo "✅ Added ANTHROPIC_API_KEY to .env"
fi

echo ""
echo "🚀 AI features enabled! Restart the app to use them."
echo ""
echo "Run: python app.py"

