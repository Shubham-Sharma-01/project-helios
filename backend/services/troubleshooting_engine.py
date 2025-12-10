"""
Interactive Troubleshooting Engine - AI-guided debugging.

This service provides step-by-step guided troubleshooting for:
- Application errors
- Performance issues
- Integration problems
- System failures
- Configuration issues
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class TroubleshootingEngine:
    """
    AI-powered interactive troubleshooting system.
    
    Provides guided debugging workflows:
    - Diagnose problems interactively
    - Suggest solutions step-by-step
    - Execute fixes automatically
    - Learn from past issues
    """
    
    def __init__(self):
        self.active_sessions = {}  # Store ongoing troubleshooting sessions
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> Dict[str, Dict]:
        """Build troubleshooting knowledge base."""
        return {
            "slow_performance": {
                "symptoms": ["slow", "performance", "lag", "timeout", "delayed"],
                "diagnosis_steps": [
                    "Check CPU and memory usage",
                    "Analyze database query performance",
                    "Review recent code changes",
                    "Check external API response times",
                    "Examine application logs for errors"
                ],
                "common_causes": [
                    {"cause": "Slow database queries", "fix": "Add indexes, optimize queries"},
                    {"cause": "Memory leak", "fix": "Restart service, investigate memory usage"},
                    {"cause": "External API timeout", "fix": "Implement caching, add retry logic"},
                    {"cause": "CPU bottleneck", "fix": "Scale horizontally, optimize code"}
                ],
                "quick_fixes": [
                    "Restart the service",
                    "Clear application cache",
                    "Check recent deployments for issues"
                ]
            },
            "connection_error": {
                "symptoms": ["connection", "refused", "timeout", "unreachable", "network"],
                "diagnosis_steps": [
                    "Verify service is running",
                    "Check network connectivity",
                    "Verify firewall rules",
                    "Check DNS resolution",
                    "Review service logs"
                ],
                "common_causes": [
                    {"cause": "Service down", "fix": "Restart the service"},
                    {"cause": "Firewall blocking", "fix": "Update security group/firewall rules"},
                    {"cause": "DNS misconfiguration", "fix": "Verify DNS records"},
                    {"cause": "Wrong endpoint", "fix": "Check configuration files"}
                ],
                "quick_fixes": [
                    "Restart the service",
                    "Check service health endpoint",
                    "Verify environment variables"
                ]
            },
            "authentication_failed": {
                "symptoms": ["authentication", "unauthorized", "401", "403", "forbidden", "access denied"],
                "diagnosis_steps": [
                    "Verify credentials are correct",
                    "Check token expiration",
                    "Review permission settings",
                    "Check authentication service status",
                    "Examine auth logs"
                ],
                "common_causes": [
                    {"cause": "Expired token", "fix": "Refresh authentication token"},
                    {"cause": "Invalid credentials", "fix": "Update credentials in vault"},
                    {"cause": "Missing permissions", "fix": "Grant required permissions"},
                    {"cause": "Auth service down", "fix": "Check authentication service"}
                ],
                "quick_fixes": [
                    "Regenerate API keys",
                    "Clear auth cache",
                    "Check credential vault"
                ]
            },
            "deployment_failed": {
                "symptoms": ["deployment", "failed", "rollback", "build", "ci/cd"],
                "diagnosis_steps": [
                    "Check build logs",
                    "Verify tests are passing",
                    "Check resource availability",
                    "Review deployment configuration",
                    "Verify image/artifact exists"
                ],
                "common_causes": [
                    {"cause": "Test failures", "fix": "Fix failing tests"},
                    {"cause": "Missing environment variables", "fix": "Add missing config"},
                    {"cause": "Resource constraints", "fix": "Increase resources"},
                    {"cause": "Image not found", "fix": "Verify build/push succeeded"}
                ],
                "quick_fixes": [
                    "Retry deployment",
                    "Rollback to previous version",
                    "Check CI/CD pipeline logs"
                ]
            },
            "high_error_rate": {
                "symptoms": ["errors", "500", "crashes", "exceptions", "failing"],
                "diagnosis_steps": [
                    "Check error logs for patterns",
                    "Identify error frequency and timing",
                    "Check recent changes/deployments",
                    "Review monitoring dashboards",
                    "Check dependency health"
                ],
                "common_causes": [
                    {"cause": "Recent bad deployment", "fix": "Rollback deployment"},
                    {"cause": "Dependency failure", "fix": "Check external services"},
                    {"cause": "Resource exhaustion", "fix": "Scale up resources"},
                    {"cause": "Bug in code", "fix": "Deploy hotfix"}
                ],
                "quick_fixes": [
                    "Rollback to last known good version",
                    "Restart affected services",
                    "Enable circuit breakers"
                ]
            }
        }
    
    def start_troubleshooting(self, user_id: str, problem_description: str) -> Dict[str, Any]:
        """
        Start an interactive troubleshooting session.
        
        Returns initial diagnosis and next steps.
        """
        session_id = f"{user_id}_{datetime.now().timestamp()}"
        
        # Analyze problem description
        problem_type = self._identify_problem_type(problem_description)
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "problem_description": problem_description,
            "problem_type": problem_type,
            "current_step": 0,
            "steps_completed": [],
            "findings": [],
            "started_at": datetime.now().isoformat()
        }
        
        self.active_sessions[session_id] = session
        
        # Get initial guidance
        guidance = self._get_initial_guidance(problem_type, problem_description)
        
        return {
            "session_id": session_id,
            "problem_type": problem_type,
            "guidance": guidance,
            "next_steps": self._get_next_steps(session)
        }
    
    def _identify_problem_type(self, description: str) -> str:
        """Identify the type of problem based on description."""
        description_lower = description.lower()
        
        # Check each problem type
        for problem_type, info in self.knowledge_base.items():
            symptoms = info["symptoms"]
            if any(symptom in description_lower for symptom in symptoms):
                return problem_type
        
        return "unknown"
    
    def _get_initial_guidance(self, problem_type: str, description: str) -> Dict[str, Any]:
        """Get initial troubleshooting guidance."""
        if problem_type == "unknown":
            return {
                "message": "I'll help you troubleshoot this issue. Let's start by gathering information.",
                "questions": [
                    "When did this issue start?",
                    "Has anything changed recently (deployments, config, etc.)?",
                    "Is this affecting all users or specific ones?",
                    "What error messages are you seeing?"
                ]
            }
        
        kb = self.knowledge_base[problem_type]
        
        return {
            "message": f"I've identified this as a **{problem_type.replace('_', ' ').title()}** issue.",
            "diagnosis_plan": kb["diagnosis_steps"],
            "quick_checks": kb["quick_fixes"],
            "common_causes": [cause["cause"] for cause in kb["common_causes"][:3]]
        }
    
    def _get_next_steps(self, session: Dict) -> List[str]:
        """Get next troubleshooting steps."""
        problem_type = session["problem_type"]
        
        if problem_type == "unknown":
            return [
                "Provide more details about the problem",
                "Share any error messages or logs",
                "Describe when the issue occurs"
            ]
        
        kb = self.knowledge_base.get(problem_type, {})
        steps = kb.get("diagnosis_steps", [])
        
        current_step = session["current_step"]
        if current_step < len(steps):
            return [steps[current_step]]
        
        return ["Review findings and apply recommended fixes"]
    
    def execute_diagnostic(self, session_id: str, step: str, result: str) -> Dict[str, Any]:
        """
        Execute a diagnostic step and record results.
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Record the finding
        session["steps_completed"].append(step)
        session["findings"].append({
            "step": step,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        session["current_step"] += 1
        
        # Analyze findings and provide recommendations
        recommendations = self._analyze_findings(session)
        
        return {
            "session_id": session_id,
            "step_completed": step,
            "findings_so_far": len(session["findings"]),
            "recommendations": recommendations,
            "next_steps": self._get_next_steps(session),
            "can_resolve": len(recommendations) > 0
        }
    
    def _analyze_findings(self, session: Dict) -> List[Dict[str, Any]]:
        """Analyze troubleshooting findings and provide recommendations."""
        problem_type = session["problem_type"]
        findings = session["findings"]
        
        if not findings:
            return []
        
        recommendations = []
        
        if problem_type in self.knowledge_base:
            kb = self.knowledge_base[problem_type]
            
            # Match findings to common causes
            for cause_info in kb["common_causes"]:
                recommendations.append({
                    "cause": cause_info["cause"],
                    "fix": cause_info["fix"],
                    "confidence": "medium",
                    "automated": False
                })
        
        return recommendations[:3]  # Top 3 recommendations
    
    def get_quick_diagnosis(self, problem_description: str) -> Dict[str, Any]:
        """
        Get quick diagnosis without starting full troubleshooting session.
        
        Useful for simple problems that can be diagnosed immediately.
        """
        problem_type = self._identify_problem_type(problem_description)
        
        if problem_type == "unknown":
            return {
                "diagnosis": "Unable to automatically diagnose",
                "suggestion": "Start interactive troubleshooting for guided assistance",
                "quick_actions": [
                    "Check application logs",
                    "Verify all services are running",
                    "Review recent changes"
                ]
            }
        
        kb = self.knowledge_base[problem_type]
        
        return {
            "diagnosis": f"Likely {problem_type.replace('_', ' ').title()} issue",
            "quick_fixes": kb["quick_fixes"],
            "common_causes": [c["cause"] for c in kb["common_causes"]],
            "next_steps": kb["diagnosis_steps"][:3]
        }
    
    def suggest_solution(self, problem: str, context: Dict[str, Any]) -> str:
        """
        AI-powered solution suggestion.
        
        Called by the main AI agent to provide troubleshooting guidance.
        """
        diagnosis = self.get_quick_diagnosis(problem)
        
        # Format for AI
        response = f"**Troubleshooting Analysis:**\n\n"
        response += f"**Diagnosis:** {diagnosis['diagnosis']}\n\n"
        
        if 'quick_fixes' in diagnosis:
            response += "**Quick Fixes to Try:**\n"
            for i, fix in enumerate(diagnosis['quick_fixes'], 1):
                response += f"{i}. {fix}\n"
            response += "\n"
        
        if 'common_causes' in diagnosis:
            response += "**Common Causes:**\n"
            for cause in diagnosis['common_causes']:
                response += f"• {cause}\n"
            response += "\n"
        
        response += "💡 Want guided troubleshooting? Say **'Start troubleshooting'** for step-by-step assistance."
        
        return response


# Global instance
troubleshooting_engine = TroubleshootingEngine()

