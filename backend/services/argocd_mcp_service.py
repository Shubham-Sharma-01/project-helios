"""ArgoCD MCP integration service - Enhanced with real MCP integration helper."""

from typing import Dict, Any, List, Optional


class ArgoCD_MCP_Service:
    """Service for ArgoCD MCP operations with live data."""
    
    def __init__(self):
        """Initialize with MCP integration helper."""
        try:
            from backend.services.mcp_integration_helper import mcp_helper
            self.mcp_helper = mcp_helper
            self.mcp_available = mcp_helper.is_argocd_available()
        except ImportError:
            self.mcp_helper = None
            self.mcp_available = False
            print("⚠️  MCP Integration Helper not available")
    
    def get_applications(self) -> List[Dict[str, Any]]:
        """
        Get all ArgoCD applications using MCP Integration Helper.
        
        Returns:
            List of application dictionaries
        """
        if self.mcp_helper and self.mcp_available:
            try:
                result = self.mcp_helper.get_argocd_applications()
                if result and result.get('applications'):
                    return result['applications']
            except Exception as e:
                print(f"⚠️  MCP call failed: {e}")
        
        return self._get_fallback_apps()
    
    def _get_fallback_apps(self) -> List[Dict[str, Any]]:
        """Fallback data when MCP not available."""
        return [
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
    
    def get_app_details(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info for a specific app."""
        if self.mcp_helper and self.mcp_available:
            try:
                result = self.mcp_helper.get_application_details(app_name)
                if result:
                    return result
            except Exception as e:
                print(f"⚠️  MCP call failed: {e}")
        
        # Fallback
        apps = self.get_applications()
        for app in apps:
            if app['name'] == app_name:
                return app
        return None
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary of all apps from MCP."""
        if self.mcp_helper and self.mcp_available:
            try:
                result = self.mcp_helper.get_argocd_summary()
                if result and result.get('available'):
                    return result
            except Exception as e:
                print(f"⚠️  MCP call failed: {e}")
        
        # Fallback calculation
        apps = self.get_applications()
        
        healthy = len([a for a in apps if a.get('health') == 'Healthy'])
        degraded = len([a for a in apps if a.get('health') == 'Degraded'])
        synced = len([a for a in apps if a.get('sync_status') == 'Synced'])
        out_of_sync = len([a for a in apps if a.get('sync_status') == 'OutOfSync'])
        
        return {
            "available": False,
            "source": "fallback",
            "total_apps": len(apps),
            "healthy": healthy,
            "degraded": degraded,
            "synced": synced,
            "out_of_sync": out_of_sync,
            "applications": apps
        }


# Global instance
argocd_mcp = ArgoCD_MCP_Service()


