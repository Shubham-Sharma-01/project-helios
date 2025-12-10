"""Service for syncing Jira issues to tasks."""

from typing import List, Dict, Any, Tuple
from datetime import datetime

from backend.services.integration_service import IntegrationService
from backend.services.task_service import TaskService
from backend.integrations.jira_integration import get_assigned_issues
from backend.database import get_db
from backend.models import Task, TaskSource


class JiraSyncService:
    """Service for syncing Jira issues to tasks."""
    
    @staticmethod
    def sync_jira_issues_to_tasks(user_id: str, integration_id: str) -> Tuple[int, int, str]:
        """
        Sync Jira issues to tasks for a user.
        
        Returns:
            (created_count, updated_count, message)
        """
        # Get integration
        integration = IntegrationService.get_integration(integration_id)
        if not integration:
            return 0, 0, "Integration not found"
        
        if integration['type'] != 'jira':
            return 0, 0, "Not a Jira integration"
        
        # Get credentials
        credentials = IntegrationService.get_integration_credentials(integration_id)
        if not credentials:
            return 0, 0, "No credentials found"
        
        # Get Jira issues
        try:
            issues = get_assigned_issues(integration['config'], credentials)
            
            if not issues:
                return 0, 0, "No issues found in Jira"
            
            created_count = 0
            updated_count = 0
            
            with get_db() as db:
                for issue in issues:
                    issue_key = issue['key']
                    
                    # Check if task already exists for this Jira issue
                    existing_task = db.query(Task).filter(
                        Task.user_id == user_id,
                        Task.source == TaskSource.JIRA,
                        Task.source_id == issue_key
                    ).first()
                    
                    # Map Jira priority to task priority
                    from backend.models import TaskPriority, TaskStatus
                    
                    priority_map = {
                        'Highest': TaskPriority.URGENT,
                        'High': TaskPriority.HIGH,
                        'Medium': TaskPriority.MEDIUM,
                        'Low': TaskPriority.LOW,
                        'Lowest': TaskPriority.LOW
                    }
                    priority = priority_map.get(issue['priority'], TaskPriority.MEDIUM)
                    
                    # Map Jira status to task status
                    status_map = {
                        'To Do': TaskStatus.TODO,
                        'Open': TaskStatus.TODO,
                        'In Progress': TaskStatus.IN_PROGRESS,
                        'Done': TaskStatus.DONE,
                        'Closed': TaskStatus.DONE,
                        'Resolved': TaskStatus.DONE
                    }
                    status = status_map.get(issue['status'], TaskStatus.TODO)
                    
                    if existing_task:
                        # Update existing task
                        existing_task.title = f"[{issue_key}] {issue['summary']}"
                        existing_task.description = f"Jira Issue: {issue['url']}\nStatus: {issue['status']}\nPriority: {issue['priority']}\nType: {issue['type']}"
                        existing_task.priority = priority
                        existing_task.source_url = issue['url']
                        existing_task.updated_at = datetime.utcnow()
                        
                        # Update status only if not manually completed
                        if existing_task.status != TaskStatus.DONE or status != TaskStatus.DONE:
                            existing_task.status = status
                        
                        updated_count += 1
                    else:
                        # Create new task
                        task = Task(
                            user_id=user_id,
                            title=f"[{issue_key}] {issue['summary']}",
                            description=f"Jira Issue: {issue['url']}\nStatus: {issue['status']}\nPriority: {issue['priority']}\nType: {issue['type']}",
                            priority=priority,
                            source=TaskSource.JIRA,
                            source_id=issue_key,
                            source_url=issue['url'],
                            status=status
                        )
                        db.add(task)
                        created_count += 1
                
                db.commit()
            
            message = f"Synced {len(issues)} Jira issues: {created_count} created, {updated_count} updated"
            return created_count, updated_count, message
            
        except Exception as e:
            return 0, 0, f"Sync failed: {str(e)}"
    
    @staticmethod
    def get_jira_issue_summary(user_id: str, integration_id: str) -> Dict[str, Any]:
        """
        Get summary of Jira issues for dashboard widget.
        
        Returns:
            Dictionary with issue counts by status and priority
        """
        # Get integration
        integration = IntegrationService.get_integration(integration_id)
        if not integration:
            return {"error": "Integration not found"}
        
        # Get credentials
        credentials = IntegrationService.get_integration_credentials(integration_id)
        if not credentials:
            return {"error": "No credentials found"}
        
        try:
            issues = get_assigned_issues(integration['config'], credentials)
            
            if not issues:
                return {
                    "total": 0,
                    "by_status": {},
                    "by_priority": {},
                    "recent_issues": []
                }
            
            # Count by status
            status_counts = {}
            for issue in issues:
                status = issue['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by priority
            priority_counts = {}
            for issue in issues:
                priority = issue['priority']
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Get recent issues (first 5) for widget
            recent_issues = issues[:5]
            
            return {
                "total": len(issues),
                "by_status": status_counts,
                "by_priority": priority_counts,
                "recent_issues": recent_issues,
                "all_issues": issues,  # All issues for priority overview
                "server_url": integration['config'].get('server_url', '')
            }
            
        except Exception as e:
            return {"error": f"Failed to fetch issues: {str(e)}"}

