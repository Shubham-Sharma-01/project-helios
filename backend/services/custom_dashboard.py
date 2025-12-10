"""
Custom Dashboard Service - Personalized insights.

Provides personalized dashboards with:
- Custom widgets
- Real-time metrics
- Trend analysis
- Personalized views
- Interactive visualizations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.services.task_service import TaskService
from backend.services.integration_service import IntegrationService
from backend.services.predictive_analytics import predictive_analytics
from backend.services.smart_recommendations import smart_recommendations


class CustomDashboardService:
    """
    Personalized dashboard generator.
    
    Creates custom dashboards with:
    - User-specific widgets
    - Real-time data
    - Predictive insights
    - Trend visualizations
    - Actionable metrics
    """
    
    def __init__(self):
        self.integration_service = IntegrationService()
    
    def generate_dashboard(self, user_id: str, dashboard_type: str = "overview") -> Dict[str, Any]:
        """
        Generate a custom dashboard for user.
        
        Args:
            user_id: User ID
            dashboard_type: Type of dashboard (overview, detailed, executive)
            
        Returns:
            Complete dashboard data
        """
        if dashboard_type == "overview":
            return self._generate_overview_dashboard(user_id)
        elif dashboard_type == "detailed":
            return self._generate_detailed_dashboard(user_id)
        elif dashboard_type == "executive":
            return self._generate_executive_dashboard(user_id)
        else:
            return self._generate_overview_dashboard(user_id)
    
    def _generate_overview_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Generate overview dashboard."""
        # Get data
        tasks = TaskService.get_user_tasks(user_id) or []
        integrations = self.integration_service.get_user_integrations(user_id) or []
        recommendations = smart_recommendations.get_recommendations(user_id)
        
        # Calculate metrics
        metrics = self._calculate_metrics(tasks, integrations)
        
        # Build widgets
        widgets = [
            self._build_task_summary_widget(tasks),
            self._build_priority_distribution_widget(tasks),
            self._build_progress_widget(tasks),
            self._build_integration_status_widget(integrations),
            self._build_recommendations_widget(recommendations),
            self._build_quick_stats_widget(metrics)
        ]
        
        return {
            "dashboard_type": "overview",
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "widgets": widgets,
            "metrics": metrics,
            "refresh_interval": 60  # seconds
        }
    
    def _generate_detailed_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Generate detailed analytics dashboard."""
        tasks = TaskService.get_user_tasks(user_id) or []
        
        # Get predictive analytics
        analytics = predictive_analytics.analyze_patterns(user_id)
        
        widgets = [
            self._build_task_summary_widget(tasks),
            self._build_trend_analysis_widget(tasks),
            self._build_bottleneck_widget(analytics.get("bottleneck_detection", {})),
            self._build_capacity_widget(analytics.get("capacity_forecast", {})),
            self._build_risk_assessment_widget(analytics.get("risk_assessment", {})),
            self._build_completion_forecast_widget(analytics.get("completion_prediction", {}))
        ]
        
        return {
            "dashboard_type": "detailed",
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "widgets": widgets,
            "analytics": analytics,
            "refresh_interval": 300  # 5 minutes
        }
    
    def _generate_executive_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Generate executive summary dashboard."""
        tasks = TaskService.get_user_tasks(user_id) or []
        integrations = self.integration_service.get_user_integrations(user_id) or []
        
        # High-level metrics
        summary = {
            "total_tasks": len(tasks),
            "active_tasks": len([t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS']]),
            "completion_rate": self._calculate_completion_rate(tasks),
            "urgent_items": len([t for t in tasks if t.get('priority') == 'URGENT']),
            "health_score": self._calculate_health_score(tasks, integrations)
        }
        
        widgets = [
            self._build_kpi_widget(summary),
            self._build_health_score_widget(summary["health_score"]),
            self._build_executive_summary_widget(tasks),
            self._build_alerts_widget(tasks, integrations)
        ]
        
        return {
            "dashboard_type": "executive",
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "summary": summary,
            "widgets": widgets,
            "refresh_interval": 600  # 10 minutes
        }
    
    def _build_task_summary_widget(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Build task summary widget."""
        by_status = {
            "TODO": len([t for t in tasks if t.get('status') == 'TODO']),
            "IN_PROGRESS": len([t for t in tasks if t.get('status') == 'IN_PROGRESS']),
            "DONE": len([t for t in tasks if t.get('status') == 'DONE']),
            "BLOCKED": len([t for t in tasks if t.get('status') == 'BLOCKED'])
        }
        
        return {
            "id": "task_summary",
            "title": "📋 Task Summary",
            "type": "summary",
            "data": {
                "total": len(tasks),
                "by_status": by_status
            },
            "visualization": "bar_chart"
        }
    
    def _build_priority_distribution_widget(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Build priority distribution widget."""
        by_priority = {
            "URGENT": len([t for t in tasks if t.get('priority') == 'URGENT']),
            "HIGH": len([t for t in tasks if t.get('priority') == 'HIGH']),
            "MEDIUM": len([t for t in tasks if t.get('priority') == 'MEDIUM']),
            "LOW": len([t for t in tasks if t.get('priority') == 'LOW'])
        }
        
        return {
            "id": "priority_distribution",
            "title": "🎯 Priority Distribution",
            "type": "distribution",
            "data": by_priority,
            "visualization": "pie_chart"
        }
    
    def _build_progress_widget(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Build progress widget."""
        total = len(tasks)
        done = len([t for t in tasks if t.get('status') == 'DONE'])
        progress = (done / total * 100) if total > 0 else 0
        
        return {
            "id": "progress",
            "title": "📈 Overall Progress",
            "type": "progress",
            "data": {
                "completed": done,
                "total": total,
                "percentage": round(progress, 1)
            },
            "visualization": "progress_bar"
        }
    
    def _build_integration_status_widget(self, integrations: List[Dict]) -> Dict[str, Any]:
        """Build integration status widget."""
        status_count = {
            "ACTIVE": len([i for i in integrations if i.get('status') == 'ACTIVE']),
            "ERROR": len([i for i in integrations if i.get('status') == 'ERROR']),
            "PENDING": len([i for i in integrations if i.get('status') == 'PENDING'])
        }
        
        return {
            "id": "integration_status",
            "title": "🔗 Integration Status",
            "type": "status",
            "data": {
                "total": len(integrations),
                "by_status": status_count
            },
            "visualization": "status_indicator"
        }
    
    def _build_recommendations_widget(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Build recommendations widget."""
        return {
            "id": "recommendations",
            "title": "💡 Smart Recommendations",
            "type": "list",
            "data": {
                "recommendations": [r["message"] for r in recommendations[:5]],
                "count": len(recommendations)
            },
            "visualization": "list"
        }
    
    def _build_quick_stats_widget(self, metrics: Dict) -> Dict[str, Any]:
        """Build quick stats widget."""
        return {
            "id": "quick_stats",
            "title": "⚡ Quick Stats",
            "type": "stats",
            "data": metrics,
            "visualization": "cards"
        }
    
    def _build_trend_analysis_widget(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Build trend analysis widget."""
        # Simple trend: tasks created vs completed over time
        return {
            "id": "trend_analysis",
            "title": "📊 Trend Analysis",
            "type": "trend",
            "data": {
                "message": "Task creation and completion trends",
                "note": "Historical data would show patterns over time"
            },
            "visualization": "line_chart"
        }
    
    def _build_bottleneck_widget(self, bottleneck_data: Dict) -> Dict[str, Any]:
        """Build bottleneck detection widget."""
        return {
            "id": "bottlenecks",
            "title": "🚧 Bottleneck Detection",
            "type": "alert",
            "data": bottleneck_data,
            "visualization": "alert_list"
        }
    
    def _build_capacity_widget(self, capacity_data: Dict) -> Dict[str, Any]:
        """Build capacity forecast widget."""
        return {
            "id": "capacity",
            "title": "📊 Capacity Forecast",
            "type": "gauge",
            "data": capacity_data,
            "visualization": "gauge"
        }
    
    def _build_risk_assessment_widget(self, risk_data: Dict) -> Dict[str, Any]:
        """Build risk assessment widget."""
        return {
            "id": "risk_assessment",
            "title": "⚠️ Risk Assessment",
            "type": "alert",
            "data": risk_data,
            "visualization": "risk_matrix"
        }
    
    def _build_completion_forecast_widget(self, forecast_data: Dict) -> Dict[str, Any]:
        """Build completion forecast widget."""
        return {
            "id": "completion_forecast",
            "title": "🎯 Completion Forecast",
            "type": "prediction",
            "data": forecast_data,
            "visualization": "forecast_chart"
        }
    
    def _build_kpi_widget(self, summary: Dict) -> Dict[str, Any]:
        """Build KPI widget for executive dashboard."""
        return {
            "id": "kpis",
            "title": "📊 Key Performance Indicators",
            "type": "kpi",
            "data": {
                "metrics": [
                    {"label": "Total Tasks", "value": summary["total_tasks"], "icon": "📋"},
                    {"label": "Active Tasks", "value": summary["active_tasks"], "icon": "🔄"},
                    {"label": "Completion Rate", "value": f"{summary['completion_rate']}%", "icon": "✅"},
                    {"label": "Urgent Items", "value": summary["urgent_items"], "icon": "🔴"}
                ]
            },
            "visualization": "kpi_cards"
        }
    
    def _build_health_score_widget(self, health_score: int) -> Dict[str, Any]:
        """Build health score widget."""
        status = "excellent" if health_score >= 80 else "good" if health_score >= 60 else "needs_attention"
        
        return {
            "id": "health_score",
            "title": "💚 System Health Score",
            "type": "score",
            "data": {
                "score": health_score,
                "status": status,
                "max": 100
            },
            "visualization": "radial_gauge"
        }
    
    def _build_executive_summary_widget(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Build executive summary widget."""
        urgent = len([t for t in tasks if t.get('priority') == 'URGENT'])
        blocked = len([t for t in tasks if t.get('status') == 'BLOCKED'])
        
        summary_points = []
        if urgent > 0:
            summary_points.append(f"🔴 {urgent} urgent task(s) require immediate attention")
        if blocked > 0:
            summary_points.append(f"🚧 {blocked} task(s) are blocked")
        if not summary_points:
            summary_points.append("✅ All systems operational")
        
        return {
            "id": "executive_summary",
            "title": "📝 Executive Summary",
            "type": "text",
            "data": {
                "summary": summary_points
            },
            "visualization": "bullet_list"
        }
    
    def _build_alerts_widget(self, tasks: List[Dict], integrations: List[Dict]) -> Dict[str, Any]:
        """Build alerts widget."""
        alerts = []
        
        # Task alerts
        urgent = [t for t in tasks if t.get('priority') == 'URGENT' and t.get('status') != 'DONE']
        if urgent:
            alerts.append({
                "level": "high",
                "message": f"{len(urgent)} urgent task(s) pending"
            })
        
        # Integration alerts
        failed = [i for i in integrations if i.get('status') == 'ERROR']
        if failed:
            alerts.append({
                "level": "medium",
                "message": f"{len(failed)} integration(s) have errors"
            })
        
        return {
            "id": "alerts",
            "title": "🚨 Active Alerts",
            "type": "alerts",
            "data": {
                "alerts": alerts if alerts else [{"level": "info", "message": "No active alerts"}],
                "count": len(alerts)
            },
            "visualization": "alert_badges"
        }
    
    def _calculate_metrics(self, tasks: List[Dict], integrations: List[Dict]) -> Dict[str, Any]:
        """Calculate dashboard metrics."""
        total = len(tasks)
        done = len([t for t in tasks if t.get('status') == 'DONE'])
        active = len([t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS']])
        
        return {
            "total_tasks": total,
            "completed_tasks": done,
            "active_tasks": active,
            "completion_rate": round((done / total * 100) if total > 0 else 0, 1),
            "total_integrations": len(integrations),
            "active_integrations": len([i for i in integrations if i.get('status') == 'ACTIVE'])
        }
    
    def _calculate_completion_rate(self, tasks: List[Dict]) -> float:
        """Calculate task completion rate."""
        total = len(tasks)
        done = len([t for t in tasks if t.get('status') == 'DONE'])
        return round((done / total * 100) if total > 0 else 0, 1)
    
    def _calculate_health_score(self, tasks: List[Dict], integrations: List[Dict]) -> int:
        """Calculate overall health score (0-100)."""
        score = 100
        
        # Deduct for urgent tasks
        urgent = len([t for t in tasks if t.get('priority') == 'URGENT' and t.get('status') != 'DONE'])
        score -= min(urgent * 10, 40)
        
        # Deduct for blocked tasks
        blocked = len([t for t in tasks if t.get('status') == 'BLOCKED'])
        score -= min(blocked * 5, 20)
        
        # Deduct for failed integrations
        failed = len([i for i in integrations if i.get('status') == 'ERROR'])
        score -= min(failed * 10, 30)
        
        return max(score, 0)
    
    def get_widget_data(self, user_id: str, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific widget."""
        dashboard = self.generate_dashboard(user_id, "overview")
        
        for widget in dashboard.get("widgets", []):
            if widget["id"] == widget_id:
                return widget
        
        return None


# Global instance
custom_dashboard = CustomDashboardService()

