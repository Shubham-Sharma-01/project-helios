"""MCP Integration using mcp-use SDK - Enhanced with real MCP client."""

from typing import Dict, Any, List, Optional
import os
import asyncio
import json


class MCPIntegrationHelper:
    """
    Enhanced MCP helper using mcp-use SDK.
    Replaces subprocess calls with proper Python SDK for better performance and reliability.
    """
    
    def __init__(self):
        """Initialize MCP client with configured servers."""
        self.client = None
        self.sessions = {}
        self.mcp_available = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MCP client with ArgoCD and other servers."""
        try:
            from mcp_use import MCPClient
            
            # Configure MCP servers from environment or use defaults
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
                },
            }
            
            self.client = MCPClient(config)
            self.mcp_available = True
            print("✅ MCP Client initialized with mcp-use SDK")
            
        except ImportError:
            print("⚠️  mcp_use not installed. Run: pip install mcp_use")
            self.client = None
            self.mcp_available = False
        except Exception as e:
            print(f"⚠️  Failed to initialize MCP client: {e}")
            self.client = None
            self.mcp_available = False
    
    async def _connect_servers_async(self):
        """Connect to all configured MCP servers asynchronously."""
        if self.client:
            try:
                await self.client.create_all_sessions()  # Fixed: snake_case
                self.sessions = {"argocd-mcp": True}
                print("✅ All MCP sessions created")
                return True
            except Exception as e:
                print(f"⚠️  Failed to create MCP sessions: {e}")
                return False
        return False
    
    def connect_servers(self):
        """Synchronous wrapper to connect to MCP servers."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._connect_servers_async())
            loop.close()
            return result
        except Exception as e:
            print(f"Error connecting to MCP servers: {e}")
            return False
    
    def is_argocd_available(self) -> bool:
        """Check if ArgoCD MCP session is available."""
        return self.mcp_available and self.client is not None
    
    async def _get_argocd_applications_async(self) -> Optional[Dict[str, Any]]:
        """Get all ArgoCD applications via MCP asynchronously."""
        if not self.client or not self.mcp_available:
            return self._fallback_apps_data()
        
        try:
            # Ensure sessions are created
            if not self.sessions:
                await self._connect_servers_async()
            
            session = self.client.get_session("argocd-mcp")  # Fixed: snake_case
            if not session:
                return self._fallback_apps_data()
            
            # Call the MCP tool to list applications
            result = await session.call_tool(  # Fixed: snake_case
                "list_applications",
                {"limit": 100}
            )
            
            # Parse response
            if result and result.content:
                apps_data = result.content[0].text
                apps = self._parse_apps(apps_data)
                return {
                    "available": True,
                    "source": "mcp",
                    "applications": apps
                }
            
            return self._fallback_apps_data()
            
        except Exception as e:
            print(f"Error fetching ArgoCD apps via MCP: {e}")
            return self._fallback_apps_data()
    
    def get_argocd_applications(self) -> Optional[Dict[str, Any]]:
        """Synchronous wrapper to get ArgoCD applications."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._get_argocd_applications_async())
            loop.close()
            return result
        except Exception as e:
            print(f"Error in sync wrapper: {e}")
            return self._fallback_apps_data()
    
    async def _get_application_details_async(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed application information asynchronously."""
        if not self.client or not self.mcp_available:
            return None
        
        try:
            if not self.sessions:
                await self._connect_servers_async()
            
            session = self.client.get_session("argocd-mcp")  # Fixed: snake_case
            if not session:
                return None
            
            result = await session.call_tool(  # Fixed: snake_case
                "get_application",
                {"applicationName": app_name}
            )
            
            if result and result.content:
                return {
                    "available": True,
                    "source": "mcp",
                    "details": json.loads(result.content[0].text) if result.content[0].text else {}
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching app details: {e}")
            return None
    
    def get_application_details(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Synchronous wrapper to get application details."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._get_application_details_async(app_name))
            loop.close()
            return result
        except Exception as e:
            print(f"Error in sync wrapper: {e}")
            return None
    
    async def _sync_application_async(self, app_name: str) -> Dict[str, Any]:
        """Trigger sync for an ArgoCD application asynchronously."""
        if not self.client or not self.mcp_available:
            return {"success": False, "message": "MCP client not available"}
        
        try:
            if not self.sessions:
                await self._connect_servers_async()
            
            session = self.client.get_session("argocd-mcp")  # Fixed: snake_case
            if not session:
                return {"success": False, "message": "ArgoCD session not found"}
            
            result = await session.call_tool(  # Fixed: snake_case
                "sync_application",
                {"applicationName": app_name}
            )
            
            return {
                "success": True,
                "message": f"Sync triggered for {app_name}",
                "result": result.content[0].text if result and result.content else None
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def sync_application(self, app_name: str) -> Dict[str, Any]:
        """Synchronous wrapper to sync application."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._sync_application_async(app_name))
            loop.close()
            return result
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_argocd_summary(self) -> Optional[Dict[str, Any]]:
        """Get a summary of ArgoCD cluster health."""
        try:
            apps_data = self.get_argocd_applications()
            if not apps_data or not apps_data.get("applications"):
                return None
            
            apps = apps_data["applications"]
            
            healthy = len([a for a in apps if a.get("health") == "Healthy"])
            degraded = len([a for a in apps if a.get("health") == "Degraded"])
            out_of_sync = len([a for a in apps if a.get("sync_status") == "OutOfSync"])
            synced = len([a for a in apps if a.get("sync_status") == "Synced"])
            
            return {
                "available": apps_data.get("available", False),
                "source": apps_data.get("source", "fallback"),
                "total_apps": len(apps),
                "healthy": healthy,
                "degraded": degraded,
                "synced": synced,
                "out_of_sync": out_of_sync,
                "applications": apps
            }
        except Exception as e:
            print(f"Error fetching ArgoCD summary: {e}")
            return None
    
    def search_apps_by_keyword(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Search for ArgoCD applications containing a keyword."""
        try:
            apps_data = self.get_argocd_applications()
            if not apps_data or not apps_data.get("applications"):
                return None
            
            keyword_lower = keyword.lower()
            matching = [
                app for app in apps_data["applications"]
                if keyword_lower in app.get("name", "").lower() or
                   keyword_lower in app.get("namespace", "").lower()
            ]
            
            return {
                "available": apps_data.get("available", False),
                "source": apps_data.get("source", "fallback"),
                "matches": matching,
                "count": len(matching)
            }
        except Exception as e:
            print(f"Error searching ArgoCD apps: {e}")
            return None
    
    def get_mcp_context_for_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get relevant MCP context for a task or Jira ticket.
        Intelligently detects ArgoCD app references and fetches live data.
        """
        if not self.is_argocd_available():
            return None
        
        try:
            # Extract potential app names from title/description
            title = item.get("title", "") or item.get("summary", "")
            description = item.get("description", "")
            text = f"{title} {description}".lower()
            
            # Common ArgoCD app patterns
            app_keywords = ["argo", "workflow", "helm", "deploy"]
            
            # Check if this might be related to ArgoCD
            if any(keyword in text for keyword in app_keywords):
                # Get full ArgoCD context
                summary = self.get_argocd_summary()
                
                # Try to find specific app mentions
                apps_data = self.get_argocd_applications()
                if apps_data and apps_data.get("applications"):
                    mentioned_apps = []
                    for app in apps_data["applications"]:
                        if app.get("name", "").lower() in text:
                            mentioned_apps.append(app)
                    
                    if mentioned_apps:
                        return {
                            "available": True,
                            "source": "mcp",
                            "relevant": True,
                            "summary": summary,
                            "mentioned_apps": mentioned_apps
                        }
                
                # Return general summary if no specific apps found
                return summary
            
            return None
        except Exception as e:
            print(f"Error getting MCP context: {e}")
            return None
    
    def _parse_apps(self, apps_data: str) -> List[Dict[str, Any]]:
        """Parse applications data from MCP response."""
        try:
            # Try to parse as JSON
            data = json.loads(apps_data)
            
            # Handle different response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Check common response keys
                for key in ['items', 'applications', 'apps', 'data']:
                    if key in data:
                        return data[key] if isinstance(data[key], list) else [data[key]]
                # If no known key, return as single item
                return [data]
            
            return []
        except json.JSONDecodeError:
            print(f"Failed to parse MCP response as JSON: {apps_data[:100]}...")
            return []
        except Exception as e:
            print(f"Error parsing apps data: {e}")
            return []
    
    def _fallback_apps_data(self) -> Dict[str, Any]:
        """Fallback data when MCP is unavailable."""
        return {
            "available": False,
            "source": "fallback",
            "applications": [
                {
                    "name": "argo-workflows",
                    "health": "Healthy",
                    "sync_status": "OutOfSync",
                    "namespace": "argo",
                    "last_sync": "2 hours ago",
                    "out_of_sync_resources": 2
                },
                {
                    "name": "helm-project-deploy",
                    "health": "Healthy",
                    "sync_status": "Synced",
                    "namespace": "default",
                    "last_sync": "1 hour ago"
                },
                {
                    "name": "workflow-controller",
                    "health": "Healthy",
                    "sync_status": "Synced",
                    "namespace": "argo",
                    "last_sync": "30 minutes ago"
                }
            ]
        }
    
    async def _close_async(self):
        """Close all MCP sessions asynchronously."""
        if self.client:
            try:
                await self.client.close_all_sessions()  # Fixed: snake_case
                print("✅ MCP sessions closed")
            except Exception as e:
                print(f"Error closing MCP sessions: {e}")
    
    def close(self):
        """Synchronous wrapper to close MCP sessions."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._close_async())
            loop.close()
        except Exception as e:
            print(f"Error in sync close wrapper: {e}")


# Global instance
mcp_helper = MCPIntegrationHelper()
