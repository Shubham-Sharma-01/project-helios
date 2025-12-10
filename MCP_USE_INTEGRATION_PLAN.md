# 🚀 Integrating mcp-use into DevOps Command Center

## Overview

This document outlines how to integrate the **mcp-use** Python SDK to replace our current subprocess-based MCP implementation with a proper, production-ready solution.

**Source:** [mcp-use GitHub Repository](https://github.com/mcp-use/mcp-use)

---

## 🎯 Benefits of Integration

### Current Issues (Subprocess Approach)
- ❌ Subprocess calls are fragile and slow
- ❌ Manual JSON parsing prone to errors
- ❌ No proper error handling
- ❌ Can't use AI agents with multi-step reasoning
- ❌ No streaming support
- ❌ Hardcoded mock data as fallback

### With mcp-use SDK
- ✅ Native Python SDK with type safety
- ✅ Automatic MCP server discovery
- ✅ Built-in AI agents with tool access
- ✅ Real-time streaming responses
- ✅ Proper error handling & retries
- ✅ Multi-server support out of the box
- ✅ Built-in observability (Langfuse)

---

## 📦 Installation

Add to `requirements.txt`:

```txt
# MCP Framework
mcp_use>=1.5.0
```

Then install:

```bash
pip install mcp_use
```

---

## 🔧 Integration Steps

### Step 1: Replace MCPIntegrationHelper

**Current:** `backend/services/mcp_integration_helper.py` (subprocess-based)  
**New:** Use `mcp_use` client

#### New Implementation:

```python
"""MCP Integration using mcp-use SDK."""

from mcp_use import MCPClient
from typing import Dict, Any, List, Optional
import os


class MCPIntegrationHelper:
    """
    Enhanced MCP helper using mcp-use SDK.
    Replaces subprocess calls with proper Python SDK.
    """
    
    def __init__(self):
        """Initialize MCP client with configured servers."""
        self.client = None
        self.sessions = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MCP client with ArgoCD and other servers."""
        try:
            # Configure MCP servers
            # This reads from ~/.cursor/mcp.json or custom config
            config = {
                "mcpServers": {
                    "argocd-mcp": {
                        "command": "npx",
                        "args": ["-y", "argocd-mcp"],
                        "env": {
                            "ARGOCD_SERVER": os.getenv("ARGOCD_SERVER", "localhost:8080"),
                            "ARGOCD_TOKEN": os.getenv("ARGOCD_TOKEN", ""),
                        },
                    },
                    # Add more MCP servers as needed
                },
            }
            
            self.client = MCPClient(config)
            print("✅ MCP Client initialized with mcp-use SDK")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize MCP client: {e}")
            self.client = None
    
    async def connect_servers(self):
        """Connect to all configured MCP servers."""
        if self.client:
            try:
                await self.client.createAllSessions()
                print("✅ All MCP sessions created")
            except Exception as e:
                print(f"⚠️  Failed to create MCP sessions: {e}")
    
    def is_argocd_available(self) -> bool:
        """Check if ArgoCD MCP session is available."""
        return self.client is not None and "argocd-mcp" in self.sessions
    
    async def get_argocd_applications(self) -> Optional[Dict[str, Any]]:
        """
        Get all ArgoCD applications via MCP using mcp-use SDK.
        
        Returns:
            Dictionary with applications data or None
        """
        if not self.client:
            return self._fallback_data()
        
        try:
            session = self.client.getSession("argocd-mcp")
            if not session:
                return self._fallback_data()
            
            # Call the MCP tool to list applications
            result = await session.callTool(
                "list_applications",
                {"limit": 100}
            )
            
            # Parse response
            if result and result.content:
                apps_data = result.content[0].text
                return {
                    "available": True,
                    "source": "mcp",
                    "applications": self._parse_apps(apps_data)
                }
            
            return self._fallback_data()
            
        except Exception as e:
            print(f"Error fetching ArgoCD apps via MCP: {e}")
            return self._fallback_data()
    
    async def get_application_details(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed application information."""
        if not self.client:
            return None
        
        try:
            session = self.client.getSession("argocd-mcp")
            if not session:
                return None
            
            result = await session.callTool(
                "get_application",
                {"applicationName": app_name}
            )
            
            if result and result.content:
                return {
                    "available": True,
                    "source": "mcp",
                    "details": result.content[0].text
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching app details: {e}")
            return None
    
    async def sync_application(self, app_name: str) -> Dict[str, Any]:
        """Trigger sync for an ArgoCD application."""
        if not self.client:
            return {"success": False, "message": "MCP client not available"}
        
        try:
            session = self.client.getSession("argocd-mcp")
            if not session:
                return {"success": False, "message": "ArgoCD session not found"}
            
            result = await session.callTool(
                "sync_application",
                {"applicationName": app_name}
            )
            
            return {
                "success": True,
                "message": f"Sync triggered for {app_name}",
                "result": result.content[0].text if result else None
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def _parse_apps(self, apps_data: str) -> List[Dict[str, Any]]:
        """Parse applications data from MCP response."""
        # Implementation depends on actual MCP response format
        import json
        try:
            return json.loads(apps_data)
        except:
            return []
    
    def _fallback_data(self) -> Dict[str, Any]:
        """Fallback data when MCP is unavailable."""
        return {
            "available": False,
            "source": "fallback",
            "applications": [
                {
                    "name": "argo-workflows",
                    "health": "Unknown",
                    "sync_status": "Unknown",
                    "namespace": "argo",
                }
            ]
        }
    
    async def close(self):
        """Close all MCP sessions."""
        if self.client:
            await self.client.closeAllSessions()
            print("✅ MCP sessions closed")


# Global instance
mcp_helper = MCPIntegrationHelper()
```

---

### Step 2: Create AI Agent Service

The real power of mcp-use is the **AI Agent** capability. Let's create a new service:

```python
"""AI Agent service using mcp-use for multi-step reasoning."""

from mcp_use import Agent
from typing import Dict, Any, List, Optional
import os


class MCPAgentService:
    """
    AI Agent that can use MCP tools for multi-step DevOps tasks.
    Example: "Check ArgoCD health and suggest fixes"
    """
    
    def __init__(self):
        """Initialize AI agent with MCP access."""
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Create agent with MCP tool access."""
        try:
            # Configure MCP servers (same as MCPIntegrationHelper)
            mcp_config = {
                "mcpServers": {
                    "argocd-mcp": {
                        "command": "npx",
                        "args": ["-y", "argocd-mcp"],
                        "env": {
                            "ARGOCD_SERVER": os.getenv("ARGOCD_SERVER"),
                            "ARGOCD_TOKEN": os.getenv("ARGOCD_TOKEN"),
                        },
                    },
                },
            }
            
            # Create agent with Claude
            self.agent = Agent(
                name="DevOps Assistant",
                model="claude-3-5-sonnet-20241022",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                mcp_config=mcp_config,
                instructions="""You are a DevOps AI assistant with access to ArgoCD via MCP.
                
You can:
- List ArgoCD applications
- Check application health and sync status
- Trigger application syncs
- Analyze deployment issues
- Provide actionable recommendations

Always use the MCP tools to get real-time data before answering."""
            )
            
            print("✅ AI Agent initialized with MCP access")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize AI agent: {e}")
            self.agent = None
    
    async def query(self, user_query: str, context: Optional[Dict] = None) -> str:
        """
        Send a query to the AI agent.
        The agent will use MCP tools as needed to answer.
        
        Args:
            user_query: User's question
            context: Additional context (active integrations, etc.)
            
        Returns:
            AI agent's response
        """
        if not self.agent:
            return "⚠️ AI Agent not available. Please set ANTHROPIC_API_KEY."
        
        try:
            # Add context to the query
            enhanced_query = user_query
            if context:
                enhanced_query += f"\n\nContext: {context}"
            
            # Agent will automatically use MCP tools if needed
            response = await self.agent.run(enhanced_query)
            
            return response.get("output", "No response")
            
        except Exception as e:
            print(f"Agent query error: {e}")
            return f"Error: {str(e)}"
    
    async def stream_query(self, user_query: str, context: Optional[Dict] = None):
        """Stream agent responses in real-time."""
        if not self.agent:
            yield "⚠️ AI Agent not available"
            return
        
        try:
            enhanced_query = user_query
            if context:
                enhanced_query += f"\n\nContext: {context}"
            
            # Stream responses
            async for chunk in self.agent.stream(enhanced_query):
                yield chunk.get("output", "")
                
        except Exception as e:
            yield f"Error: {str(e)}"


# Global instance
mcp_agent = MCPAgentService()
```

---

### Step 3: Update MCP Page to Use Agent

Replace the current AI chat logic in `frontend/pages/mcp_page.py`:

```python
# In mcp_page.py, replace get_ai_response method:

async def get_ai_response_async(self, query: str):
    """Get AI response using mcp-use agent."""
    from backend.services.mcp_agent_service import mcp_agent
    
    # Build context
    context = {
        "active_integrations": [
            i["integration_type"] 
            for i in self.integration_service.get_user_integrations(self.user_id)
            if i.get("is_active")
        ],
        "mcp_servers": [
            s["server_type"] 
            for s in self.mcp_service.get_user_mcp_servers(self.user_id)
            if s.get("status") == "active"
        ]
    }
    
    # Use agent (will automatically call MCP tools if needed)
    response = await mcp_agent.query(query, context)
    return response

def get_ai_response(self, query: str):
    """Wrapper to run async agent query."""
    import asyncio
    
    try:
        # Run async query
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.get_ai_response_async(query))
        loop.close()
        
        return response
        
    except Exception as e:
        return f"Error: {str(e)}"
```

---

## 🎯 Key Improvements

### 1. **Real MCP Tool Access**
- Agent can actually call `list_applications`, `sync_application`, etc.
- No more mock data or subprocess hacks

### 2. **Multi-Step Reasoning**
User: "Check if any apps are unhealthy and fix them"

Agent will:
1. Call `list_applications` tool
2. Analyze health status
3. Call `sync_application` for broken apps
4. Report results

### 3. **Streaming Responses**
```python
async for chunk in mcp_agent.stream_query(query):
    # Update UI in real-time
    self.add_message_chunk(chunk)
```

### 4. **Better Error Handling**
- Automatic retries
- Proper timeout management
- Graceful fallbacks

---

## 📋 Migration Checklist

- [ ] Install `mcp_use` package
- [ ] Replace `MCPIntegrationHelper` with new implementation
- [ ] Create `MCPAgentService`
- [ ] Update `mcp_page.py` to use agent
- [ ] Update `argocd_mcp_service.py` to use new helper
- [ ] Add async support to Flet app (if needed)
- [ ] Test with real ArgoCD connection
- [ ] Remove old subprocess code
- [ ] Update documentation

---

## 🧪 Testing

```python
# Test the new integration
import asyncio
from backend.services.mcp_integration_helper import mcp_helper
from backend.services.mcp_agent_service import mcp_agent

async def test():
    # Test MCP client
    await mcp_helper.connect_servers()
    apps = await mcp_helper.get_argocd_applications()
    print(f"Found {len(apps['applications'])} applications")
    
    # Test AI agent
    response = await mcp_agent.query(
        "What's the health status of my ArgoCD applications?"
    )
    print(response)
    
    await mcp_helper.close()

asyncio.run(test())
```

---

## 📚 Additional Features

### Multi-Server Support
```python
mcp_config = {
    "mcpServers": {
        "argocd-mcp": {...},
        "github-mcp": {...},
        "k8s-mcp": {...},
    }
}
```

### Tool Access Control
```python
agent = Agent(
    ...,
    allowed_tools=["list_applications", "get_application"],  # Restrict tools
)
```

### Observability (Langfuse)
```python
agent = Agent(
    ...,
    langfuse_enabled=True,
    langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
)
```

---

## 🔗 Resources

- **GitHub:** https://github.com/mcp-use/mcp-use
- **PyPI:** https://pypi.org/project/mcp_use/
- **Python Docs:** https://github.com/mcp-use/mcp-use/tree/main/libraries/python/docs
- **Examples:** https://github.com/mcp-use/mcp-use/tree/main/libraries/python/examples

---

## 💡 Next Steps

1. **Install mcp-use:** `pip install mcp_use`
2. **Test locally** with your ArgoCD setup
3. **Migrate gradually** (keep fallback during transition)
4. **Add more MCP servers** (GitHub, K8s, Datadog, etc.)
5. **Enable streaming** for better UX

Ready to proceed with integration?

