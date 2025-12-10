"""
Predictive Analytics Service - Prevent issues before they happen.

This service analyzes patterns, trends, and historical data to predict:
- Resource exhaustion (disk, memory, CPU)
- Performance degradation
- Potential failures
- Capacity issues
- Bottlenecks
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
from backend.services.task_service import TaskService
from backend.services.integration_service import IntegrationService


class PredictiveAnalyticsService:
    """
    AI-powered predictive analytics for DevOps.
    
    Analyzes historical data and current trends to predict:
    - Future issues before they occur
    - Resource needs and capacity planning
    - Performance bottlenecks
    - Task completion estimates
    """
    
    def __init__(self):
        self.task_service = TaskService()
        self.integration_service = IntegrationService()
    
    def analyze_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze user's work patterns and predict insights.
        
        Returns comprehensive analytics including:
        - Task completion trends
        - Workload predictions
        - Bottleneck identification
        - Risk assessments
        """
        tasks = TaskService.get_user_tasks(user_id) or []
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "workload_trend": self._analyze_workload_trend(tasks),
            "completion_prediction": self._predict_completion_rate(tasks),
            "bottleneck_detection": self._detect_bottlenecks(tasks),
            "risk_assessment": self._assess_risks(tasks),
            "capacity_forecast": self._forecast_capacity(tasks),
            "recommendations": []
        }
        
        # Generate actionable recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_workload_trend(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze workload trends over time."""
        if not tasks:
            return {"status": "no_data", "trend": "stable", "alert": None}
        
        # Group tasks by status
        todo = len([t for t in tasks if t.get('status') == 'TODO'])
        in_progress = len([t for t in tasks if t.get('status') == 'IN_PROGRESS'])
        done = len([t for t in tasks if t.get('status') == 'DONE'])
        blocked = len([t for t in tasks if t.get('status') == 'BLOCKED'])
        
        total = len(tasks)
        completion_rate = (done / total * 100) if total > 0 else 0
        
        # Determine trend
        trend = "stable"
        alert = None
        
        if todo > done * 2:
            trend = "increasing"
            alert = "⚠️ Workload growing faster than completion rate"
        elif done > todo * 2:
            trend = "decreasing"
            alert = "✅ Completing tasks faster than new ones arrive"
        
        if blocked > 0:
            alert = f"🚨 {blocked} blocked task(s) need attention"
        
        return {
            "status": "analyzed",
            "trend": trend,
            "completion_rate": round(completion_rate, 1),
            "task_distribution": {
                "todo": todo,
                "in_progress": in_progress,
                "done": done,
                "blocked": blocked
            },
            "alert": alert
        }
    
    def _predict_completion_rate(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Predict when current workload will be completed."""
        active_tasks = [t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS']]
        
        if not active_tasks:
            return {
                "prediction": "No active tasks",
                "estimated_completion": "N/A",
                "confidence": "high"
            }
        
        # Simple prediction based on task count and priority
        urgent = len([t for t in active_tasks if t.get('priority') == 'URGENT'])
        high = len([t for t in active_tasks if t.get('priority') == 'HIGH'])
        medium = len([t for t in active_tasks if t.get('priority') == 'MEDIUM'])
        low = len([t for t in active_tasks if t.get('priority') == 'LOW'])
        
        # Estimate days (rough heuristic)
        estimated_days = (urgent * 0.5) + (high * 1) + (medium * 2) + (low * 3)
        
        completion_date = datetime.now() + timedelta(days=estimated_days)
        
        return {
            "prediction": f"Estimated {round(estimated_days, 1)} days to complete active tasks",
            "estimated_completion": completion_date.strftime("%Y-%m-%d"),
            "active_task_count": len(active_tasks),
            "confidence": "medium" if len(active_tasks) < 20 else "low"
        }
    
    def _detect_bottlenecks(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Detect bottlenecks in the workflow."""
        bottlenecks = []
        
        # Check for blocked tasks
        blocked = [t for t in tasks if t.get('status') == 'BLOCKED']
        if blocked:
            bottlenecks.append({
                "type": "blocked_tasks",
                "severity": "high",
                "count": len(blocked),
                "description": f"{len(blocked)} blocked task(s) preventing progress",
                "recommendation": "Unblock these tasks immediately to restore workflow"
            })
        
        # Check for too many in-progress tasks
        in_progress = [t for t in tasks if t.get('status') == 'IN_PROGRESS']
        if len(in_progress) > 10:
            bottlenecks.append({
                "type": "context_switching",
                "severity": "medium",
                "count": len(in_progress),
                "description": f"{len(in_progress)} tasks in progress simultaneously",
                "recommendation": "Focus on completing existing tasks before starting new ones"
            })
        
        # Check for old TODO tasks
        old_todos = [t for t in tasks if t.get('status') == 'TODO']
        if len(old_todos) > 20:
            bottlenecks.append({
                "type": "task_backlog",
                "severity": "medium",
                "count": len(old_todos),
                "description": f"{len(old_todos)} tasks in backlog",
                "recommendation": "Review and prioritize backlog, consider delegating"
            })
        
        return {
            "detected": len(bottlenecks) > 0,
            "count": len(bottlenecks),
            "bottlenecks": bottlenecks
        }
    
    def _assess_risks(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Assess risks in current workload."""
        risks = []
        
        urgent_tasks = [t for t in tasks if t.get('priority') == 'URGENT' and t.get('status') != 'DONE']
        if urgent_tasks:
            risks.append({
                "type": "urgent_tasks",
                "level": "high",
                "count": len(urgent_tasks),
                "message": f"{len(urgent_tasks)} urgent task(s) require immediate attention",
                "impact": "High risk of missing critical deadlines"
            })
        
        blocked_urgent = [t for t in tasks if t.get('priority') in ['URGENT', 'HIGH'] and t.get('status') == 'BLOCKED']
        if blocked_urgent:
            risks.append({
                "type": "blocked_critical",
                "level": "critical",
                "count": len(blocked_urgent),
                "message": f"{len(blocked_urgent)} critical task(s) blocked",
                "impact": "Severe risk of project delays"
            })
        
        # Check workload balance
        active = len([t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS']])
        if active > 30:
            risks.append({
                "type": "overload",
                "level": "medium",
                "count": active,
                "message": f"{active} active tasks may lead to burnout",
                "impact": "Risk of decreased productivity and quality"
            })
        
        return {
            "risk_level": "critical" if any(r["level"] == "critical" for r in risks) else "high" if risks else "low",
            "risk_count": len(risks),
            "risks": risks
        }
    
    def _forecast_capacity(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Forecast capacity and resource needs."""
        active = len([t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS']])
        
        # Simple capacity calculation
        capacity_used = min((active / 50) * 100, 100) if active > 0 else 0
        
        status = "healthy"
        recommendation = None
        
        if capacity_used > 80:
            status = "at_capacity"
            recommendation = "Consider delegating tasks or deferring non-critical work"
        elif capacity_used > 60:
            status = "high_utilization"
            recommendation = "Monitor workload closely, avoid taking on new commitments"
        elif capacity_used < 20:
            status = "underutilized"
            recommendation = "Capacity available for new projects"
        
        return {
            "status": status,
            "capacity_used": round(capacity_used, 1),
            "capacity_available": round(100 - capacity_used, 1),
            "recommendation": recommendation
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Workload recommendations
        workload = analysis.get("workload_trend", {})
        if workload.get("alert"):
            recommendations.append(workload["alert"])
        
        # Bottleneck recommendations
        bottlenecks = analysis.get("bottleneck_detection", {})
        for bottleneck in bottlenecks.get("bottlenecks", []):
            recommendations.append(f"🔧 {bottleneck['description']}: {bottleneck['recommendation']}")
        
        # Risk recommendations
        risks = analysis.get("risk_assessment", {})
        for risk in risks.get("risks", []):
            recommendations.append(f"⚠️ {risk['message']}: {risk['impact']}")
        
        # Capacity recommendations
        capacity = analysis.get("capacity_forecast", {})
        if capacity.get("recommendation"):
            recommendations.append(f"📊 {capacity['recommendation']}")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ Everything looks good! Keep up the great work!")
        
        return recommendations[:5]  # Top 5 most important
    
    def predict_issue(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Predict potential issues based on context.
        
        This is called by the AI to get predictive insights.
        """
        user_id = context.get("user_id")
        if not user_id:
            return None
        
        analysis = self.analyze_patterns(user_id)
        
        # Format for AI consumption
        prediction = {
            "has_predictions": True,
            "summary": self._create_summary(analysis),
            "insights": analysis,
            "action_required": analysis["risk_assessment"]["risk_level"] in ["high", "critical"]
        }
        
        return prediction
    
    def _create_summary(self, analysis: Dict[str, Any]) -> str:
        """Create human-readable summary of predictions."""
        lines = []
        
        # Workload
        workload = analysis["workload_trend"]
        lines.append(f"📈 **Workload Trend:** {workload['trend'].title()} ({workload['completion_rate']}% completion rate)")
        
        # Risks
        risks = analysis["risk_assessment"]
        if risks["risk_count"] > 0:
            lines.append(f"⚠️ **Risk Level:** {risks['risk_level'].upper()} ({risks['risk_count']} risk(s) detected)")
        
        # Completion
        completion = analysis["completion_prediction"]
        lines.append(f"🎯 **Prediction:** {completion['prediction']}")
        
        # Top recommendation
        if analysis["recommendations"]:
            lines.append(f"\n💡 **Top Recommendation:** {analysis['recommendations'][0]}")
        
        return "\n".join(lines)


# Global instance
predictive_analytics = PredictiveAnalyticsService()

