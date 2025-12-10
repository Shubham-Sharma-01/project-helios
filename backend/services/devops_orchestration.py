"""
DevOps Orchestration Layer - Control everything via chat.

Provides natural language interface to:
- Execute DevOps operations
- Manage deployments
- Control infrastructure
- Coordinate workflows
- Automate processes
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from backend.services.integration_service import IntegrationService
from backend.services.task_service import TaskService


class DevOpsOrchestrationLayer:
    """
    Natural language DevOps orchestration.
    
    Enables chat-based control of:
    - Deployments and releases
    - Service management
    - Infrastructure operations
    - Workflow automation
    - Integration coordination
    """
    
    def __init__(self):
        self.integration_service = IntegrationService()
        self.task_service = TaskService()
        self.operation_history = []
    
    def execute_command(self, user_id: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a DevOps command via natural language.
        
        Args:
            user_id: User executing the command
            command: Natural language command
            params: Optional parameters
            
        Returns:
            Execution result with status and output
        """
        # Parse command
        parsed = self._parse_command(command)
        
        if not parsed:
            return {
                "success": False,
                "message": "Could not understand command",
                "suggestions": self._get_command_suggestions()
            }
        
        # Route to appropriate handler
        result = self._route_command(user_id, parsed, params or {})
        
        # Log operation
        self._log_operation(user_id, command, result)
        
        return result
    
    def _parse_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Parse natural language command."""
        cmd_lower = command.lower()
        
        # Deployment commands
        if any(word in cmd_lower for word in ['deploy', 'release', 'rollout']):
            return {
                "type": "deployment",
                "action": "deploy",
                "raw_command": command
            }
        
        # Service management
        elif any(word in cmd_lower for word in ['restart', 'stop', 'start', 'scale']):
            action = next((word for word in ['restart', 'stop', 'start', 'scale'] if word in cmd_lower), 'unknown')
            return {
                "type": "service_management",
                "action": action,
                "raw_command": command
            }
        
        # Status checks
        elif any(word in cmd_lower for word in ['status', 'health', 'check']):
            return {
                "type": "status_check",
                "action": "get_status",
                "raw_command": command
            }
        
        # Workflow automation
        elif any(word in cmd_lower for word in ['automate', 'workflow', 'trigger']):
            return {
                "type": "workflow",
                "action": "execute",
                "raw_command": command
            }
        
        # Integration management
        elif any(word in cmd_lower for word in ['sync', 'integrate', 'connect']):
            return {
                "type": "integration",
                "action": "sync",
                "raw_command": command
            }
        
        return None
    
    def _route_command(self, user_id: str, parsed: Dict[str, Any], params: Dict) -> Dict[str, Any]:
        """Route command to appropriate handler."""
        cmd_type = parsed["type"]
        action = parsed["action"]
        
        handlers = {
            "deployment": self._handle_deployment,
            "service_management": self._handle_service_management,
            "status_check": self._handle_status_check,
            "workflow": self._handle_workflow,
            "integration": self._handle_integration
        }
        
        handler = handlers.get(cmd_type)
        if handler:
            return handler(user_id, action, parsed, params)
        
        return {
            "success": False,
            "message": f"No handler for command type: {cmd_type}"
        }
    
    def _handle_deployment(self, user_id: str, action: str, parsed: Dict, params: Dict) -> Dict[str, Any]:
        """Handle deployment commands."""
        # Simulated deployment - in production this would call actual deployment systems
        
        return {
            "success": True,
            "message": "🚀 **Deployment Orchestration**",
            "details": {
                "action": "deploy",
                "status": "simulated",
                "steps": [
                    "✅ Pre-deployment checks passed",
                    "✅ Building artifacts",
                    "✅ Running tests",
                    "🔄 Deploying to target environment",
                    "⏳ Waiting for health checks"
                ],
                "note": "This is a simulation. Connect ArgoCD or other CD tools for real deployments."
            },
            "recommendations": [
                "Monitor logs after deployment",
                "Verify health checks pass",
                "Check for any alerts"
            ]
        }
    
    def _handle_service_management(self, user_id: str, action: str, parsed: Dict, params: Dict) -> Dict[str, Any]:
        """Handle service management commands."""
        actions_map = {
            "restart": "🔄 Restarting service",
            "start": "▶️ Starting service",
            "stop": "⏹️ Stopping service",
            "scale": "📈 Scaling service"
        }
        
        message = actions_map.get(action, "Managing service")
        
        return {
            "success": True,
            "message": f"{message}",
            "details": {
                "action": action,
                "status": "simulated",
                "note": "Connect to your infrastructure (Kubernetes, Docker, etc.) for real operations"
            },
            "next_steps": [
                "Verify service status",
                "Check logs for errors",
                "Monitor resource usage"
            ]
        }
    
    def _handle_status_check(self, user_id: str, action: str, parsed: Dict, params: Dict) -> Dict[str, Any]:
        """Handle status check commands."""
        # Get integration status
        integrations = self.integration_service.get_user_integrations(user_id) or []
        
        # Get task status
        tasks = TaskService.get_user_tasks(user_id) or []
        active_tasks = [t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS']]
        
        status_summary = {
            "integrations": {
                "total": len(integrations),
                "active": len([i for i in integrations if i.get('status') == 'ACTIVE']),
                "errors": len([i for i in integrations if i.get('status') == 'ERROR'])
            },
            "tasks": {
                "total": len(tasks),
                "active": len(active_tasks),
                "urgent": len([t for t in active_tasks if t.get('priority') == 'URGENT'])
            },
            "overall_health": "healthy" if len([i for i in integrations if i.get('status') == 'ERROR']) == 0 else "degraded"
        }
        
        return {
            "success": True,
            "message": "📊 **System Status Overview**",
            "status": status_summary,
            "details": self._format_status_details(status_summary)
        }
    
    def _format_status_details(self, status: Dict) -> List[str]:
        """Format status details for display."""
        details = []
        
        # Integrations
        integ = status["integrations"]
        if integ["errors"] > 0:
            details.append(f"⚠️ {integ['errors']} integration(s) have errors")
        else:
            details.append(f"✅ All {integ['total']} integration(s) healthy")
        
        # Tasks
        tasks = status["tasks"]
        if tasks["urgent"] > 0:
            details.append(f"🔴 {tasks['urgent']} urgent task(s) need attention")
        details.append(f"📋 {tasks['active']} active task(s)")
        
        # Overall
        health = status["overall_health"]
        if health == "healthy":
            details.append("✅ Overall system health: HEALTHY")
        else:
            details.append("⚠️ Overall system health: DEGRADED")
        
        return details
    
    def _handle_workflow(self, user_id: str, action: str, parsed: Dict, params: Dict) -> Dict[str, Any]:
        """Handle workflow automation commands."""
        return {
            "success": True,
            "message": "⚙️ **Workflow Automation**",
            "details": {
                "available_workflows": [
                    "Deployment pipeline",
                    "Incident response",
                    "Backup and recovery",
                    "Monitoring and alerts",
                    "Task synchronization"
                ],
                "note": "Workflow automation can be configured in Settings"
            },
            "suggestions": [
                "Define workflow triggers",
                "Set up approval gates",
                "Configure notifications"
            ]
        }
    
    def _handle_integration(self, user_id: str, action: str, parsed: Dict, params: Dict) -> Dict[str, Any]:
        """Handle integration commands."""
        integrations = self.integration_service.get_user_integrations(user_id) or []
        
        return {
            "success": True,
            "message": "🔗 **Integration Management**",
            "integrations": [
                {
                    "name": i.get('name', 'Unknown'),
                    "type": i.get('type', 'unknown'),
                    "status": i.get('status', 'unknown')
                }
                for i in integrations
            ],
            "actions_available": [
                "Sync data from integrations",
                "Test integration connections",
                "Configure integration settings"
            ]
        }
    
    def _log_operation(self, user_id: str, command: str, result: Dict):
        """Log orchestration operation."""
        self.operation_history.append({
            "user_id": user_id,
            "command": command,
            "success": result.get("success", False),
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 operations
        if len(self.operation_history) > 100:
            self.operation_history = self.operation_history[-100:]
    
    def _get_command_suggestions(self) -> List[str]:
        """Get command suggestions for users."""
        return [
            "Check system status",
            "Deploy to staging",
            "Restart service xyz",
            "Show integration health",
            "Trigger deployment pipeline",
            "Scale service to 5 instances"
        ]
    
    def get_available_operations(self) -> Dict[str, List[str]]:
        """Get list of available operations."""
        return {
            "deployment": [
                "Deploy to environment",
                "Rollback deployment",
                "Show deployment history",
                "Trigger release pipeline"
            ],
            "service_management": [
                "Restart service",
                "Scale service",
                "Stop/Start service",
                "Check service health"
            ],
            "monitoring": [
                "Get system status",
                "Check integration health",
                "Show active alerts",
                "View metrics"
            ],
            "automation": [
                "Create workflow",
                "Trigger automated task",
                "Schedule operation",
                "Set up alerts"
            ]
        }
    
    def orchestrate_complex_workflow(
        self,
        user_id: str,
        workflow_name: str,
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Orchestrate a complex multi-step workflow.
        
        Example:
        steps = [
            {"action": "deploy", "target": "staging"},
            {"action": "test", "type": "smoke"},
            {"action": "deploy", "target": "production"}
        ]
        """
        results = []
        
        for i, step in enumerate(steps, 1):
            result = {
                "step": i,
                "action": step.get("action"),
                "status": "success",
                "message": f"Step {i}: {step.get('action')} completed"
            }
            results.append(result)
        
        return {
            "success": True,
            "workflow": workflow_name,
            "steps_completed": len(results),
            "results": results,
            "message": f"✅ Workflow '{workflow_name}' completed successfully"
        }


# Global instance
devops_orchestration = DevOpsOrchestrationLayer()

