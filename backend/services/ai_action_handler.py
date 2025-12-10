"""
AI Action Handler - Execute user commands via AI prompts.
Handles task management, integrations, and app actions.

NOW WITH GAME-CHANGING FEATURES:
- Predictive Analytics
- Interactive Troubleshooting
- Smart Recommendations
- DevOps Orchestration
- Custom Dashboards
"""
from typing import Dict, Any, List, Optional, Tuple
from backend.services.task_service import TaskService
from backend.services.integration_service import IntegrationService
from backend.models import TaskPriority, TaskStatus
import json
import re

# Import game-changing features
from backend.services.predictive_analytics import predictive_analytics
from backend.services.troubleshooting_engine import troubleshooting_engine
from backend.services.smart_recommendations import smart_recommendations
from backend.services.devops_orchestration import devops_orchestration
from backend.services.custom_dashboard import custom_dashboard
from backend.services.github_ai_handler import GitHubAIHandler


class AIActionHandler:
    """
    Handles AI-requested actions in the app.
    
    This service can:
    - Create, update, delete tasks
    - Manage integrations
    - Fetch app data
    - Execute user commands
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.task_service = TaskService()
        self.integration_service = IntegrationService()
        self.github_ai_handler = GitHubAIHandler(user_id=user_id)
    
    def get_full_app_context(self) -> Dict[str, Any]:
        """
        Get comprehensive context about the entire app state.
        
        Returns:
            Complete app context with all user data
        """
        # Get all tasks
        tasks = TaskService.get_user_tasks(self.user_id) or []
        
        # Get task stats
        stats = TaskService.get_task_stats(self.user_id)
        
        # Get all integrations
        integrations = self.integration_service.get_user_integrations(self.user_id) or []
        
        # Build comprehensive context
        context = {
            "tasks": {
                "total": len(tasks),
                "all_tasks": tasks,
                "by_status": {
                    "TODO": [t for t in tasks if t.get('status') == 'TODO'],
                    "IN_PROGRESS": [t for t in tasks if t.get('status') == 'IN_PROGRESS'],
                    "DONE": [t for t in tasks if t.get('status') == 'DONE'],
                    "BLOCKED": [t for t in tasks if t.get('status') == 'BLOCKED']
                },
                "stats": stats
            },
            "integrations": {
                "total": len(integrations),
                "all": integrations,
                "by_type": self._group_by_type(integrations),
                "active": [i for i in integrations if i.get('status') == 'ACTIVE']
            },
            "user_id": self.user_id
        }
        
        return context
    
    def _group_by_type(self, integrations: List[Dict]) -> Dict[str, List[Dict]]:
        """Group integrations by type."""
        grouped = {}
        for integ in integrations:
            int_type = integ.get('type', 'unknown')
            if int_type not in grouped:
                grouped[int_type] = []
            grouped[int_type].append(integ)
        return grouped
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute an AI-requested action.
        
        Args:
            action: Action name (create_task, delete_task, etc.)
            params: Action parameters
            
        Returns:
            (success, message)
        """
        actions = {
            # Task management
            'create_task': self._create_task,
            'delete_task': self._delete_task,
            'update_task': self._update_task,
            'list_tasks': self._list_tasks,
            'get_task_details': self._get_task_details,
            'list_integrations': self._list_integrations,
            'get_stats': self._get_stats,
            
            # 🔥 GAME-CHANGING FEATURES
            'predict_issues': self._predict_issues,
            'troubleshoot': self._troubleshoot_problem,
            'get_recommendations': self._get_smart_recommendations,
            'orchestrate': self._orchestrate_devops,
            'generate_dashboard': self._generate_custom_dashboard,
            'get_insights': self._get_predictive_insights,
            
            # 🐙 GITHUB INTEGRATION
            'github_query': self._handle_github_query,
        }
        
        handler = actions.get(action)
        if not handler:
            return False, f"Unknown action: {action}"
        
        try:
            return handler(params)
        except Exception as e:
            return False, f"Action failed: {str(e)}"
    
    def _create_task(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Create a new task."""
        print(f"\n🔍 DEBUG _create_task: params={params}")
        title = params.get('title')
        description = params.get('description', '')
        priority_param = params.get('priority', 'MEDIUM')
        print(f"🔍 Priority param type: {type(priority_param)}, value: {priority_param}")
        
        if not title:
            return False, "Title is required to create a task"
        
        # Handle priority - could be string or already a TaskPriority enum
        if isinstance(priority_param, TaskPriority):
            priority_enum = priority_param
            priority_str = priority_param.value
        else:
            # It's a string, convert to enum
            priority_str = str(priority_param).upper()
            priority_map = {
                'LOW': TaskPriority.LOW,
                'MEDIUM': TaskPriority.MEDIUM,
                'HIGH': TaskPriority.HIGH,
                'URGENT': TaskPriority.URGENT,
                'CRITICAL': TaskPriority.URGENT
            }
            priority_enum = priority_map.get(priority_str, TaskPriority.MEDIUM)
        
        # Create task
        try:
            print(f"🔍 About to create task with priority_enum: {priority_enum} (type: {type(priority_enum)})")
            task_id = TaskService.create_task(
                user_id=self.user_id,
                title=title,
                description=description,
                priority=priority_enum
            )
            
            # Shorten the task ID for display
            task_id_short = task_id[:8] if len(task_id) > 8 else task_id
            
            print(f"✅ Task created successfully: {task_id}")
            return True, f"✅ **Task Created Successfully!**\n\n📝 **Title:** {title}\n🎯 **Priority:** {priority_str}\n🆔 **ID:** `{task_id_short}...`\n\n✨ Check the **My Tasks** page to see it!"
        except Exception as e:
            print(f"❌ Error creating task: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Failed to create task: {str(e)}"
    
    def _delete_task(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Delete a task."""
        task_id = params.get('task_id')
        
        if not task_id:
            return False, "Task ID is required"
        
        success = TaskService.delete_task(task_id, self.user_id)
        
        if success:
            return True, f"✅ Task deleted successfully! ID: {task_id}"
        else:
            return False, f"❌ Failed to delete task. Task not found or access denied."
    
    def _update_task(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a task."""
        task_id = params.get('task_id')
        
        if not task_id:
            return False, "Task ID is required"
        
        # Build update params
        update_params = {}
        
        if 'title' in params:
            update_params['title'] = params['title']
        
        if 'description' in params:
            update_params['description'] = params['description']
        
        if 'status' in params:
            status_param = params['status']
            if isinstance(status_param, TaskStatus):
                update_params['status'] = status_param
            else:
                status_map = {
                    'TODO': TaskStatus.TODO,
                    'IN_PROGRESS': TaskStatus.IN_PROGRESS,
                    'DONE': TaskStatus.DONE,
                    'BLOCKED': TaskStatus.BLOCKED
                }
                status = str(status_param).upper().replace(' ', '_')
                update_params['status'] = status_map.get(status, TaskStatus.TODO)
        
        if 'priority' in params:
            priority_param = params['priority']
            if isinstance(priority_param, TaskPriority):
                update_params['priority'] = priority_param
            else:
                priority_map = {
                    'LOW': TaskPriority.LOW,
                    'MEDIUM': TaskPriority.MEDIUM,
                    'HIGH': TaskPriority.HIGH,
                    'URGENT': TaskPriority.URGENT
                }
                priority = str(priority_param).upper()
                update_params['priority'] = priority_map.get(priority, TaskPriority.MEDIUM)
        
        # Update task
        task = TaskService.update_task(task_id, self.user_id, **update_params)
        
        if task:
            return True, f"✅ Task updated successfully!\n{json.dumps(update_params, indent=2)}"
        else:
            return False, "❌ Failed to update task. Task not found or access denied."
    
    def _list_tasks(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """List tasks with optional filtering."""
        status_filter = params.get('status')
        priority_filter = params.get('priority')
        
        tasks = TaskService.get_user_tasks(self.user_id) or []
        
        # Apply filters - handle both string and enum types
        if status_filter:
            status_val = str(status_filter).upper() if not isinstance(status_filter, TaskStatus) else status_filter.value
            tasks = [t for t in tasks if t.get('status') == status_val]
        
        if priority_filter:
            priority_val = str(priority_filter).upper() if not isinstance(priority_filter, TaskPriority) else priority_filter.value
            tasks = [t for t in tasks if t.get('priority') == priority_val]
        
        if not tasks:
            return True, "No tasks found matching the criteria."
        
        # Format task list
        result = f"Found {len(tasks)} task(s):\n\n"
        for i, task in enumerate(tasks, 1):
            result += f"{i}. **{task.get('title', 'Untitled')}**\n"
            result += f"   Status: {task.get('status', 'Unknown')}\n"
            result += f"   Priority: {task.get('priority', 'Unknown')}\n"
            result += f"   ID: {task.get('id', 'Unknown')}\n\n"
        
        return True, result
    
    def _get_task_details(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Get detailed information about a specific task."""
        task_id = params.get('task_id')
        
        if not task_id:
            return False, "Task ID is required"
        
        task = TaskService.get_task(task_id, self.user_id)
        
        if not task:
            return False, "Task not found"
        
        result = f"**Task Details:**\n\n"
        result += f"📝 Title: {task.get('title', 'Untitled')}\n"
        result += f"📊 Status: {task.get('status', 'Unknown')}\n"
        result += f"🎯 Priority: {task.get('priority', 'Unknown')}\n"
        result += f"📄 Description: {task.get('description', 'No description')}\n"
        result += f"🔗 Source: {task.get('source', 'Manual')}\n"
        result += f"🆔 ID: {task.get('id', 'Unknown')}\n"
        result += f"📅 Created: {task.get('created_at', 'Unknown')}\n"
        
        return True, result
    
    def _list_integrations(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """List all integrations."""
        integrations = self.integration_service.get_user_integrations(self.user_id) or []
        
        if not integrations:
            return True, "No integrations configured yet."
        
        result = f"**Integrations ({len(integrations)} total):**\n\n"
        
        for i, integ in enumerate(integrations, 1):
            status_icon = {
                'ACTIVE': '✅',
                'ERROR': '❌',
                'PENDING': '⏳',
                'DISABLED': '⚪'
            }.get(integ.get('status', 'UNKNOWN'), '❓')
            
            result += f"{i}. {status_icon} **{integ.get('name', 'Unnamed')}**\n"
            result += f"   Type: {integ.get('type', 'Unknown').upper()}\n"
            result += f"   Status: {integ.get('status', 'Unknown')}\n"
            
            if integ.get('error_message'):
                result += f"   Error: {integ.get('error_message')}\n"
            
            result += f"   ID: {integ.get('id', 'Unknown')}\n\n"
        
        return True, result
    
    def _get_stats(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Get comprehensive app statistics."""
        stats = TaskService.get_task_stats(self.user_id)
        integrations = self.integration_service.get_user_integrations(self.user_id) or []
        
        result = "**📊 Your DevOps Command Center Stats:**\n\n"
        
        # Task stats
        result += f"**Tasks:**\n"
        result += f"  • Total: {stats.get('total', 0)}\n"
        result += f"  • To Do: {stats.get('todo', 0)}\n"
        result += f"  • In Progress: {stats.get('in_progress', 0)}\n"
        result += f"  • Done: {stats.get('done', 0)}\n"
        result += f"  • Blocked: {stats.get('blocked', 0)}\n"
        result += f"  • Urgent: {stats.get('urgent', 0)}\n\n"
        
        # Integration stats
        active = len([i for i in integrations if i.get('status') == 'ACTIVE'])
        error = len([i for i in integrations if i.get('status') == 'ERROR'])
        
        result += f"**Integrations:**\n"
        result += f"  • Total: {len(integrations)}\n"
        result += f"  • Active: {active}\n"
        result += f"  • Errors: {error}\n"
        
        return True, result
    
    # ========== GAME-CHANGING FEATURES ==========
    
    def _predict_issues(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """🧠 Predictive Analytics - Predict potential issues."""
        prediction = predictive_analytics.predict_issue({"user_id": self.user_id})
        
        if not prediction:
            return True, "No predictions available at this time."
        
        return True, prediction["summary"]
    
    def _troubleshoot_problem(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """💬 Interactive Troubleshooting - Guide user through problem solving."""
        problem = params.get('problem', 'general issue')
        
        diagnosis = troubleshooting_engine.get_quick_diagnosis(problem)
        
        return True, troubleshooting_engine.suggest_solution(problem, {"user_id": self.user_id})
    
    def _get_smart_recommendations(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """🎯 Smart Recommendations - Get personalized recommendations."""
        recommendations = smart_recommendations.get_daily_recommendations(self.user_id)
        
        return True, recommendations
    
    def _orchestrate_devops(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """🌐 DevOps Orchestration - Execute DevOps commands."""
        command = params.get('command', '')
        
        result = devops_orchestration.execute_command(self.user_id, command, params)
        
        if not result.get('success'):
            return False, result.get('message', 'Command execution failed')
        
        # Format result
        response = result.get('message', '')
        if 'details' in result:
            details = result['details']
            if isinstance(details, dict):
                response += f"\n\n**Details:**\n"
                for key, value in details.items():
                    if isinstance(value, list):
                        response += f"• {key}:\n"
                        for item in value:
                            response += f"  - {item}\n"
                    else:
                        response += f"• {key}: {value}\n"
        
        return True, response
    
    def _generate_custom_dashboard(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """📊 Custom Dashboard - Generate personalized dashboard."""
        dashboard_type = params.get('type', 'overview')
        
        dashboard = custom_dashboard.generate_dashboard(self.user_id, dashboard_type)
        
        # Format dashboard for text display
        response = f"**📊 {dashboard_type.title()} Dashboard**\n\n"
        response += f"Generated at: {dashboard['generated_at']}\n\n"
        
        # Show key metrics
        if 'metrics' in dashboard:
            metrics = dashboard['metrics']
            response += "**Key Metrics:**\n"
            response += f"• Total Tasks: {metrics.get('total_tasks', 0)}\n"
            response += f"• Completed: {metrics.get('completed_tasks', 0)}\n"
            response += f"• Active: {metrics.get('active_tasks', 0)}\n"
            response += f"• Completion Rate: {metrics.get('completion_rate', 0)}%\n"
        
        response += "\n💡 Tip: Ask for specific widgets like 'show task summary' or 'show progress'"
        
        return True, response
    
    def _get_predictive_insights(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """🔮 Get comprehensive predictive insights."""
        analysis = predictive_analytics.analyze_patterns(self.user_id)
        
        response = "**🔮 Predictive Insights:**\n\n"
        
        # Workload trend
        workload = analysis.get("workload_trend", {})
        response += f"**Workload:** {workload.get('trend', 'Unknown').title()} "
        response += f"({workload.get('completion_rate', 0)}% completion)\n\n"
        
        # Risks
        risks = analysis.get("risk_assessment", {})
        risk_level = risks.get("risk_level", "unknown")
        response += f"**Risk Level:** {risk_level.upper()}\n"
        if risks.get("risks"):
            for risk in risks["risks"][:3]:
                response += f"• {risk['message']}\n"
        response += "\n"
        
        # Recommendations
        if analysis.get("recommendations"):
            response += "**Top Recommendations:**\n"
            for rec in analysis["recommendations"][:3]:
                response += f"• {rec}\n"
        
        return True, response
    
    def _handle_github_query(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """🐙 GitHub Integration - Handle GitHub queries."""
        query = params.get('query', '')
        
        success, response = self.github_ai_handler.handle_query(query)
        
        return success, response
    
    # ========== END GAME-CHANGING FEATURES ==========
    
    def detect_and_execute_action(self, query: str, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Detect if the query is requesting an action and execute it.
        
        Returns:
            (action_detected, result_message)
        """
        query_lower = query.lower()
        
        # Pattern matching for actions
        
        # CREATE TASK - More sophisticated natural language patterns
        create_patterns = [
            # Direct patterns: "create task: xyz" or "create task xyz"
            r"create (?:a |an |new )?(?:task|user)[:\s]+(.+)",
            r"add (?:a |an |new )?(?:task|user)[:\s]+(.+)",
            r"new (?:task|user)[:\s]+(.+)",
            r"make (?:a |an |new )?(?:task|user)[:\s]+(.+)",
            
            # Named patterns: "create task called xyz", "create task named xyz"
            r"create (?:a |an |new )?(?:task|user) (?:called|named) (.+)",
            r"add (?:a |an |new )?(?:task|user) (?:called|named) (.+)",
            
            # "by the name" patterns: "create task by the name xyz"
            r"create (?:a |an |new )?(?:task|user)(?: for me)? by (?:the )?name (.+)",
            r"add (?:a |an |new )?(?:task|user)(?: for me)? by (?:the )?name (.+)",
            
            # "with name" patterns: "create task with name xyz"
            r"create (?:a |an |new )?(?:task|user)(?: for me)? with (?:the )?name (.+)",
            r"add (?:a |an |new )?(?:task|user)(?: for me)? with (?:the )?name (.+)",
        ]
        
        for pattern in create_patterns:
            match = re.search(pattern, query_lower)
            if match:
                # Get the last captured group (the title)
                title = match.group(match.lastindex).strip() if match.lastindex else match.group(1).strip()
                
                # Deep cleaning - remove common filler phrases
                # Remove leading phrases
                title = re.sub(r'^(for me|with (?:the )?name|called|named|by (?:the )?name (?:of )?|titled)\s*', '', title, flags=re.IGNORECASE).strip()
                
                # Remove "for me" anywhere
                title = re.sub(r'\s+for me\b', '', title, flags=re.IGNORECASE).strip()
                
                # Extract priority if mentioned
                priority = 'MEDIUM'
                if 'urgent' in title.lower() or 'critical' in title.lower():
                    priority = 'URGENT'
                elif 'high priority' in title.lower():
                    priority = 'HIGH'
                elif 'low priority' in title.lower():
                    priority = 'LOW'
                
                # Clean title - remove priority keywords
                title = re.sub(r'\s*(urgent|critical|high priority|low priority)\s*', '', title, flags=re.IGNORECASE).strip()
                
                # Remove trailing/leading punctuation and whitespace
                title = title.strip('.,;:!? ')
                
                if not title:
                    return True, "❌ Please provide a task name/title."
                
                print(f"🔥 ACTION DETECTED: Creating task '{title}' with priority '{priority}'")
                success, message = self._create_task({'title': title, 'priority': priority})
                return True, message
        
        # DELETE TASK
        delete_patterns = [
            r"delete (?:the )?task[:\s]+(.+)",
            r"remove (?:the )?task[:\s]+(.+)",
            r"delete task (?:with )?id[:\s]+(.+)",
        ]
        
        for pattern in delete_patterns:
            match = re.search(pattern, query_lower)
            if match:
                # Try to extract task ID or title
                identifier = match.group(1).strip()
                
                # Find task by title or ID
                tasks = TaskService.get_user_tasks(self.user_id) or []
                
                task_to_delete = None
                for task in tasks:
                    if task.get('id') == identifier or task.get('title', '').lower() == identifier:
                        task_to_delete = task
                        break
                
                if task_to_delete:
                    success, message = self._delete_task({'task_id': task_to_delete['id']})
                    return True, message
                else:
                    return True, f"❌ Task '{identifier}' not found. Use exact title or task ID."
        
        # UPDATE TASK STATUS
        status_patterns = [
            r"(?:mark|set|move|change) task (.+?) (?:as|to) (todo|in progress|done|blocked)",
            r"complete (?:the )?task[:\s]+(.+)",
            r"finish (?:the )?task[:\s]+(.+)",
        ]
        
        for pattern in status_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if 'complete' in pattern or 'finish' in pattern:
                    identifier = match.group(1).strip()
                    new_status = 'DONE'
                else:
                    identifier = match.group(1).strip()
                    new_status = match.group(2).strip().upper().replace(' ', '_')
                
                # Find task
                tasks = TaskService.get_user_tasks(self.user_id) or []
                task_to_update = None
                
                for task in tasks:
                    if task.get('id') == identifier or task.get('title', '').lower() == identifier:
                        task_to_update = task
                        break
                
                if task_to_update:
                    success, message = self._update_task({
                        'task_id': task_to_update['id'],
                        'status': new_status
                    })
                    return True, message
                else:
                    return True, f"❌ Task '{identifier}' not found."
        
        # LIST ACTIONS
        if any(phrase in query_lower for phrase in ['list tasks', 'show tasks', 'what tasks', 'my tasks', 'all tasks']):
            success, message = self._list_tasks({})
            return True, message
        
        if any(phrase in query_lower for phrase in ['list integrations', 'show integrations', 'what integrations']):
            success, message = self._list_integrations({})
            return True, message
        
        if any(phrase in query_lower for phrase in ['stats', 'statistics', 'summary', 'overview']):
            success, message = self._get_stats({})
            return True, message
        
        # 🔥 GAME-CHANGING FEATURE DETECTION
        
        # Predictive Analytics
        if any(phrase in query_lower for phrase in ['predict', 'forecast', 'what will happen', 'future issues', 'predict issues']):
            success, message = self._predict_issues({})
            return True, message
        
        # Interactive Troubleshooting
        if any(phrase in query_lower for phrase in ['troubleshoot', 'debug', 'diagnose', 'problem with', 'issue with', 'not working']):
            success, message = self._troubleshoot_problem({'problem': query})
            return True, message
        
        # Smart Recommendations
        if any(phrase in query_lower for phrase in ['recommend', 'suggestions', 'what should i', 'advice', 'guidance', 'daily briefing']):
            success, message = self._get_smart_recommendations({})
            return True, message
        
        # Predictive Insights
        if any(phrase in query_lower for phrase in ['insights', 'analysis', 'patterns', 'trends', 'analytics']):
            success, message = self._get_predictive_insights({})
            return True, message
        
        # Custom Dashboard
        if any(phrase in query_lower for phrase in ['dashboard', 'metrics', 'kpi', 'performance']):
            success, message = self._generate_custom_dashboard({})
            return True, message
        
        # DevOps Orchestration
        if any(phrase in query_lower for phrase in ['deploy', 'orchestrate', 'execute', 'run workflow', 'check status', 'restart service']):
            success, message = self._orchestrate_devops({'command': query})
            return True, message
        
        # 🐙 GitHub Integration
        if any(phrase in query_lower for phrase in [
            'github', 'repo', 'repository', 'pull request', 'pr', 'prs',
            'commits', 'branches', 'issues', 'create issue', 'show commits',
            'list repos', 'show prs', 'show issues'
        ]):
            success, message = self._handle_github_query({'query': query})
            return True, message
        
        # No action detected
        return False, None
    
    def parse_ai_intent(self, query: str, ai_response: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Parse AI response for action intent.
        
        Some queries need AI to decide the action. This parses the AI's
        suggested action from its response.
        
        Returns:
            (has_action, action_dict)
        """
        # Look for action markers in AI response
        if "ACTION:" in ai_response or "EXECUTE:" in ai_response:
            # Extract action from AI response
            # Format: ACTION: create_task(title="...", priority="...")
            action_match = re.search(r"ACTION:\s*(\w+)\((.*?)\)", ai_response)
            
            if action_match:
                action_name = action_match.group(1)
                params_str = action_match.group(2)
                
                # Parse parameters (simple key="value" parsing)
                params = {}
                param_matches = re.findall(r'(\w+)="([^"]*)"', params_str)
                for key, value in param_matches:
                    params[key] = value
                
                return True, {"action": action_name, "params": params}
        
        return False, None


# Convenience function
def create_action_handler(user_id: str) -> AIActionHandler:
    """Create an action handler for a user."""
    return AIActionHandler(user_id)

