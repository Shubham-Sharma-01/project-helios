"""
MCPAgentService - AI Agent powered by mcp-use SDK
Supports both Anthropic Claude and Local Ollama models.
"""
from typing import Dict, Any, Optional
import os
import asyncio
from mcp_use.agents import MCPAgent
from mcp_use.client import MCPClient
from langchain_core.messages import HumanMessage

class MCPAgentService:
    """
    AI Agent Service using mcp-use SDK with LangChain.
    
    This service provides:
    1. Multi-step reasoning with Claude or Ollama
    2. Access to MCP tools (ArgoCD, etc.)
    3. Memory for conversation context
    4. Pretty-printed tool execution
    """
    
    def __init__(self):
        # Check for AI provider preference
        self.ai_provider = os.getenv('AI_PROVIDER', 'ollama').lower()  # Default to Ollama
        
        # Anthropic settings
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        
        # Ollama settings  
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b-instruct-q4_K_M')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        self.enabled = False
        self.agent = None
        self.mcp_client = None
        
        # Initialize based on provider
        if self.ai_provider == 'anthropic':
            if not self.api_key:
                print("⚠️  AI Provider set to 'anthropic' but ANTHROPIC_API_KEY not found")
                print("    Falling back to Ollama...")
                self.ai_provider = 'ollama'
            else:
                self.enabled = True
        
        if self.ai_provider == 'ollama':
            self.enabled = True  # Ollama is always available locally
        
        if not self.enabled:
            print("⚠️  No AI provider available")
            return
        
        try:
            self._initialize_agent()
        except Exception as e:
            print(f"❌ Failed to initialize AI Agent: {e}")
            self.enabled = False
    
    def _initialize_agent(self):
        """Initialize the MCPAgent with LangChain LLM (Claude or Ollama) and MCP tools."""
        print(f"🔄 Initializing AI Agent with {self.ai_provider.upper()}...")
        
        # Step 1: Configure MCP Client
        config = {
            "servers": {
                "argocd-mcp": {
                    "connector": {
                        "type": "http",
                        "url": os.getenv("ARGOCD_MCP_URL", "http://localhost:3000/argocd-mcp")
                    }
                }
            }
        }
        
        self.mcp_client = MCPClient(config=config)
        
        # Step 2: Initialize LLM based on provider
        if self.ai_provider == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(
                model=self.model,
                api_key=self.api_key,
                temperature=0.7,
                max_tokens=4096
            )
            print(f"   Using Claude: {self.model}")
        else:  # ollama
            from langchain_ollama import ChatOllama
            llm = ChatOllama(
                model=self.ollama_model,
                base_url=self.ollama_base_url,
                temperature=0.7,
                num_predict=4096  # Max tokens for Ollama
            )
            print(f"   Using Ollama: {self.ollama_model}")
            print(f"   Ollama server: {self.ollama_base_url}")
        
        # Step 3: Create MCPAgent with system prompt
        system_prompt = """You are an expert DevOps AI assistant with access to real-time ArgoCD data via MCP tools.

Your capabilities:
- 🔍 Check ArgoCD application health and sync status
- 🔄 Trigger deployments and syncs
- 📊 Analyze deployment trends and issues
- 💡 Provide actionable DevOps insights
- 🎯 Help troubleshoot deployment problems

Guidelines:
1. Always use MCP tools to get LIVE data when asked about ArgoCD
2. Be concise and actionable - users want quick answers
3. If an app is unhealthy, suggest specific remediation steps
4. Use emojis to make responses more engaging
5. When syncing apps, confirm the action was successful

Example interactions:
- "Show ArgoCD status" → Use list_applications tool
- "What's broken?" → Check health status and explain issues
- "Sync my-app" → Use sync_application tool and confirm

Remember: You have real-time access to ArgoCD. Use it!"""
        
        self.agent = MCPAgent(
            llm=llm,
            client=self.mcp_client,
            verbose=True,  # Show tool execution
            pretty_print=True,  # Pretty print responses
            memory_enabled=True,  # Remember conversation context
            system_prompt=system_prompt
        )
        
        print("✅ AI Agent initialized successfully!")
        print(f"   Provider: {self.ai_provider.upper()}")
        print(f"   Model: {self.ollama_model if self.ai_provider == 'ollama' else self.model}")
        print(f"   MCP Tools: ArgoCD")
        print(f"   Memory: Enabled")
        print(f"   Cost: {'FREE (Local)' if self.ai_provider == 'ollama' else 'Paid API'}")
    
    async def run_agent_query(self, query: str) -> str:
        """
        Run a query through the AI Agent.
        
        The agent will:
        1. Understand the user's intent
        2. Decide which MCP tools to use
        3. Execute tools in the right order
        4. Reason about the results
        5. Provide a helpful response
        
        Args:
            query: User's natural language question
            
        Returns:
            AI's response as a string
        """
        if not self.enabled or not self.agent:
            return f"⚠️ AI Agent is not enabled. Using {self.ai_provider} - please check configuration."
        
        try:
            print(f"🤖 Agent Query ({self.ai_provider.upper()}): {query}")
            
            # Run the agent - it will automatically use MCP tools as needed
            response = await self.agent.run(query)
            
            # Extract the text response
            if hasattr(response, 'content') and response.content:
                if isinstance(response.content, list):
                    # Multiple content blocks (text + tool results)
                    text_parts = [
                        block.text if hasattr(block, 'text') else str(block)
                        for block in response.content
                        if hasattr(block, 'text')
                    ]
                    return '\n'.join(text_parts) if text_parts else str(response.content[0])
                else:
                    return str(response.content)
            else:
                return str(response)
                
        except Exception as e:
            error_msg = f"❌ AI Agent error ({self.ai_provider}): {str(e)}"
            print(error_msg)
            return error_msg
    
    async def quick_action(self, action_name: str, params: Dict[str, Any] = None) -> str:
        """
        Execute a quick action via the AI Agent.
        
        Quick actions are pre-defined shortcuts like:
        - "argocd_status" → Get all app statuses
        - "sync_app" → Sync a specific app
        - "health_check" → Check overall health
        
        Args:
            action_name: Name of the action
            params: Optional parameters for the action
            
        Returns:
            AI's response
        """
        if not self.enabled or not self.agent:
            return "⚠️ AI Agent is not enabled."
        
        params = params or {}
        
        # Map action names to natural language queries
        action_queries = {
            "argocd_status": "Show me the status of all ArgoCD applications",
            "health_check": "What applications need my attention? Check ArgoCD health",
            "sync_app": f"Sync the ArgoCD application named {params.get('app_name', 'unknown')}",
            "deployment_summary": "Summarize recent deployments and their status",
        }
        
        query = action_queries.get(action_name, f"Perform action: {action_name} with params: {params}")
        
        return await self.run_agent_query(query)
    
    def reset_memory(self):
        """Clear the agent's conversation memory."""
        if self.agent:
            # Note: mcp-use MCPAgent uses LangGraph memory
            # Memory reset depends on the MCPAgent implementation
            print("💭 Agent memory reset (if supported)")
    
    async def close(self):
        """Close the MCP client and clean up resources."""
        if self.mcp_client:
            try:
                await self.mcp_client.close_all_sessions()
                print("✅ MCP Agent sessions closed")
            except Exception as e:
                print(f"Error closing MCP Agent: {e}")


# Global singleton instance
mcp_agent_service = MCPAgentService()


# Example usage (for testing)
async def _test_agent():
    """Test the agent locally."""
    if not mcp_agent_service.enabled:
        print("❌ Agent not enabled. Set ANTHROPIC_API_KEY in .env")
        return
    
    test_queries = [
        "Show me my ArgoCD applications",
        "What applications are unhealthy?",
        "What should I focus on today?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🧪 Test Query: {query}")
        print('='*60)
        response = await mcp_agent_service.run_agent_query(query)
        print(f"\n🤖 Response:\n{response}\n")


if __name__ == "__main__":
    # Run test
    asyncio.run(_test_agent())
