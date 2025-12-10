"""
Smart Recommendations System - Optimize everything.

Provides intelligent recommendations for:
- Task prioritization
- Workflow optimization
- Best practices
- Performance improvements
- Resource allocation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.services.task_service import TaskService
from backend.services.integration_service import IntegrationService


class SmartRecommendationsSystem:
    """
    AI-powered recommendation engine.
    
    Analyzes user behavior, patterns, and data to provide:
    - Actionable recommendations
    - Optimization suggestions
    - Best practice guidance
    - Personalized insights
    """
    
    def __init__(self):
        self.recommendation_rules = self._build_rules()
    
    def _build_rules(self) -> List[Dict]:
        """Build recommendation rules."""
        return [
            {
                "id": "focus_urgent",
                "condition": lambda ctx: len(ctx.get("urgent_tasks", [])) > 0,
                "recommendation": "🔥 Focus on urgent tasks first - you have {count} urgent task(s) needing immediate attention",
                "priority": "high",
                "action": "prioritize_urgent"
            },
            {
                "id": "reduce_wip",
                "condition": lambda ctx: len(ctx.get("in_progress", [])) > 5,
                "recommendation": "⚠️ Too many tasks in progress ({count}). Complete existing tasks before starting new ones to improve focus.",
                "priority": "medium",
                "action": "reduce_work_in_progress"
            },
            {
                "id": "unblock_tasks",
                "condition": lambda ctx: len(ctx.get("blocked_tasks", [])) > 0,
                "recommendation": "🚧 You have {count} blocked task(s). Unblock these to restore workflow momentum.",
                "priority": "high",
                "action": "unblock_tasks"
            },
            {
                "id": "clear_backlog",
                "condition": lambda ctx: len(ctx.get("todo_tasks", [])) > 20,
                "recommendation": "📋 Large backlog detected ({count} tasks). Consider prioritizing, delegating, or archiving old tasks.",
                "priority": "low",
                "action": "review_backlog"
            },
            {
                "id": "celebrate_progress",
                "condition": lambda ctx: len(ctx.get("done_tasks", [])) > 10,
                "recommendation": "🎉 Great progress! You've completed {count} tasks. Keep up the momentum!",
                "priority": "info",
                "action": "celebrate"
            },
            {
                "id": "balance_workload",
                "condition": lambda ctx: self._check_workload_imbalance(ctx),
                "recommendation": "⚖️ Workload imbalance detected. Consider redistributing tasks for better balance.",
                "priority": "medium",
                "action": "rebalance_workload"
            },
            {
                "id": "add_integrations",
                "condition": lambda ctx: len(ctx.get("integrations", [])) == 0,
                "recommendation": "🔗 No integrations configured. Connect Jira, ArgoCD, or Slack to unlock more features!",
                "priority": "info",
                "action": "setup_integrations"
            },
            {
                "id": "fix_integration_errors",
                "condition": lambda ctx: len(ctx.get("failed_integrations", [])) > 0,
                "recommendation": "❌ {count} integration(s) have errors. Fix them to restore full functionality.",
                "priority": "medium",
                "action": "fix_integrations"
            }
        ]
    
    def _check_workload_imbalance(self, context: Dict) -> bool:
        """Check if workload is imbalanced."""
        urgent = len(context.get("urgent_tasks", []))
        low = len(context.get("low_priority", []))
        
        return urgent > 5 and low > urgent * 2
    
    def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for user.
        
        Returns list of actionable recommendations.
        """
        # Gather context
        context = self._build_context(user_id)
        
        # Apply rules
        recommendations = []
        for rule in self.recommendation_rules:
            if rule["condition"](context):
                rec = {
                    "id": rule["id"],
                    "message": rule["recommendation"].format(
                        count=self._get_count_for_rule(rule["id"], context)
                    ),
                    "priority": rule["priority"],
                    "action": rule["action"],
                    "timestamp": datetime.now().isoformat()
                }
                recommendations.append(rec)
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        return recommendations
    
    def _build_context(self, user_id: str) -> Dict[str, Any]:
        """Build context for recommendation engine."""
        tasks = TaskService.get_user_tasks(user_id) or []
        integrations = IntegrationService().get_user_integrations(user_id) or []
        
        context = {
            "all_tasks": tasks,
            "urgent_tasks": [t for t in tasks if t.get('priority') == 'URGENT' and t.get('status') != 'DONE'],
            "in_progress": [t for t in tasks if t.get('status') == 'IN_PROGRESS'],
            "blocked_tasks": [t for t in tasks if t.get('status') == 'BLOCKED'],
            "todo_tasks": [t for t in tasks if t.get('status') == 'TODO'],
            "done_tasks": [t for t in tasks if t.get('status') == 'DONE'],
            "low_priority": [t for t in tasks if t.get('priority') == 'LOW'],
            "integrations": integrations,
            "failed_integrations": [i for i in integrations if i.get('status') == 'ERROR'],
            "user_id": user_id
        }
        
        return context
    
    def _get_count_for_rule(self, rule_id: str, context: Dict) -> int:
        """Get count value for rule message formatting."""
        count_map = {
            "focus_urgent": len(context.get("urgent_tasks", [])),
            "reduce_wip": len(context.get("in_progress", [])),
            "unblock_tasks": len(context.get("blocked_tasks", [])),
            "clear_backlog": len(context.get("todo_tasks", [])),
            "celebrate_progress": len(context.get("done_tasks", [])),
            "fix_integration_errors": len(context.get("failed_integrations", []))
        }
        return count_map.get(rule_id, 0)
    
    def get_optimization_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """
        Get specific optimization suggestions.
        """
        suggestions = []
        
        # Task management optimizations
        in_progress = context.get("in_progress", [])
        if len(in_progress) > 3:
            suggestions.append("💡 Consider limiting work-in-progress to 3 tasks for better focus")
        
        blocked = context.get("blocked_tasks", [])
        if blocked:
            suggestions.append(f"💡 Resolve {len(blocked)} blocked task(s) to improve flow")
        
        # Priority suggestions
        urgent = context.get("urgent_tasks", [])
        if urgent:
            suggestions.append(f"💡 {len(urgent)} urgent task(s) should be worked on immediately")
        
        # Workflow suggestions
        todo = context.get("todo_tasks", [])
        done = context.get("done_tasks", [])
        
        if len(todo) > len(done) * 3:
            suggestions.append("💡 Backlog growing - consider triaging or delegating tasks")
        
        return suggestions
    
    def recommend_next_task(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Recommend the next task user should work on.
        
        Uses intelligent prioritization based on:
        - Task priority
        - Status
        - Workflow optimization
        """
        tasks = TaskService.get_user_tasks(user_id) or []
        
        # Filter to actionable tasks
        actionable = [t for t in tasks if t.get('status') in ['TODO', 'BLOCKED']]
        
        if not actionable:
            return None
        
        # Prioritize
        # 1. Blocked urgent tasks first
        blocked_urgent = [t for t in actionable if t.get('status') == 'BLOCKED' and t.get('priority') == 'URGENT']
        if blocked_urgent:
            return {
                "task": blocked_urgent[0],
                "reason": "This is a blocked urgent task - unblocking it is critical",
                "action": "unblock"
            }
        
        # 2. Urgent tasks
        urgent = [t for t in actionable if t.get('priority') == 'URGENT' and t.get('status') == 'TODO']
        if urgent:
            return {
                "task": urgent[0],
                "reason": "This urgent task needs immediate attention",
                "action": "start"
            }
        
        # 3. High priority tasks
        high = [t for t in actionable if t.get('priority') == 'HIGH' and t.get('status') == 'TODO']
        if high:
            return {
                "task": high[0],
                "reason": "High priority task ready to be started",
                "action": "start"
            }
        
        # 4. Any TODO task
        todo = [t for t in actionable if t.get('status') == 'TODO']
        if todo:
            return {
                "task": todo[0],
                "reason": "Next task in your backlog",
                "action": "start"
            }
        
        return None
    
    def get_daily_recommendations(self, user_id: str) -> str:
        """
        Get formatted daily recommendations for user.
        
        This is called by the AI to provide daily guidance.
        """
        recommendations = self.get_recommendations(user_id)
        
        if not recommendations:
            return "✅ Everything looks good! No specific recommendations right now."
        
        # Format recommendations
        output = "**🎯 Smart Recommendations:**\n\n"
        
        for rec in recommendations[:5]:  # Top 5
            emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🔵",
                "info": "ℹ️"
            }.get(rec["priority"], "•")
            
            output += f"{emoji} {rec['message']}\n"
        
        # Add next task recommendation
        next_task = self.recommend_next_task(user_id)
        if next_task:
            output += f"\n**📌 Recommended Next Task:**\n"
            output += f"➡️ {next_task['task'].get('title', 'Unnamed task')}\n"
            output += f"   {next_task['reason']}\n"
        
        return output


# Global instance
smart_recommendations = SmartRecommendationsSystem()

