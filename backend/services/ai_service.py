"""AI prioritization service using Claude or Ollama."""

from typing import List, Dict, Any, Optional
import os
import json


class AIService:
    """Service for AI-powered task prioritization and analysis."""
    
    def __init__(self):
        # Check AI provider
        self.ai_provider = os.getenv('AI_PROVIDER', 'ollama').lower()
        
        # Anthropic settings
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        
        # Ollama settings
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b-instruct-q4_K_M')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Determine if AI is enabled
        if self.ai_provider == 'anthropic':
            self.enabled = bool(self.api_key)
            if not self.enabled:
                print("⚠️  ANTHROPIC_API_KEY not set - falling back to Ollama")
                self.ai_provider = 'ollama'
                self.enabled = True
        else:  # ollama
            self.enabled = True
        
        if not self.enabled:
            print("⚠️  No AI provider available - AI features disabled")
        else:
            print(f"✅ AI Service using: {self.ai_provider.upper()}")
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze and prioritize tasks using AI.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Tasks with AI priority scores
        """
        if not self.enabled:
            # Fallback: simple priority scoring
            return self._fallback_prioritization(tasks)
        
        try:
            if self.ai_provider == 'anthropic':
                return self._prioritize_with_anthropic(tasks)
            else:  # ollama
                return self._prioritize_with_ollama(tasks)
        
        except Exception as e:
            print(f"AI prioritization error: {e}")
            return self._fallback_prioritization(tasks)
    
    def _prioritize_with_anthropic(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize tasks using Anthropic Claude."""
        from anthropic import Anthropic
        
        client = Anthropic(api_key=self.api_key)
        
        # Prepare task summary for AI
        task_summary = []
        for task in tasks:
            task_summary.append({
                'id': task.get('id'),
                'title': task.get('title'),
                'description': task.get('description', '')[:200],  # Limit length
                'source': task.get('source'),
                'priority': task.get('priority'),
                'created_at': task.get('created_at')
            })
        
        prompt = f"""Analyze these tasks and assign an urgency score (1-10) to each. Consider:
- Source (slack mentions = higher urgency)
- Keywords like "urgent", "critical", "down", "production", "error"
- Priority field
- How recent they are

Tasks:
{json.dumps(task_summary, indent=2)}

Respond with JSON array of {{"id": "task-id", "score": 8, "reason": "brief explanation"}}.
Only return the JSON array, no other text."""

        response = client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._process_ai_response(response.content[0].text, tasks)
    
    def _prioritize_with_ollama(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize tasks using local Ollama."""
        import ollama
        
        # Prepare task summary for AI
        task_summary = []
        for task in tasks:
            task_summary.append({
                'id': task.get('id'),
                'title': task.get('title'),
                'description': task.get('description', '')[:200],  # Limit length
                'source': task.get('source'),
                'priority': task.get('priority'),
                'created_at': task.get('created_at')
            })
        
        prompt = f"""Analyze these tasks and assign an urgency score (1-10) to each. Consider:
- Source (slack mentions = higher urgency)
- Keywords like "urgent", "critical", "down", "production", "error"
- Priority field
- How recent they are

Tasks:
{json.dumps(task_summary, indent=2)}

Respond with ONLY a JSON array of {{"id": "task-id", "score": 8, "reason": "brief explanation"}}.
Do not include any other text, just the JSON array."""

        response = ollama.chat(
            model=self.ollama_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._process_ai_response(response['message']['content'], tasks)
    
    def _process_ai_response(self, content: str, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process AI response and apply scores to tasks."""
        # Try to extract JSON from response
        content = content.strip()
        
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        ai_scores = json.loads(content)
        
        # Apply scores to tasks
        score_map = {item['id']: item for item in ai_scores}
        for task in tasks:
            task_id = task.get('id')
            if task_id in score_map:
                task['ai_priority_score'] = score_map[task_id].get('score', 5)
                task['ai_reason'] = score_map[task_id].get('reason', '')
        
        # Sort by AI score
        tasks.sort(key=lambda t: t.get('ai_priority_score', 5), reverse=True)
        
        return tasks
    
    def _fallback_prioritization(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback prioritization without AI."""
        priority_map = {'urgent': 10, 'high': 7, 'medium': 5, 'low': 3}
        source_boost = {'slack': 2, 'argocd': 1, 'manual': 0}
        
        for task in tasks:
            base_score = priority_map.get(task.get('priority', 'medium'), 5)
            source_score = source_boost.get(task.get('source', 'manual'), 0)
            
            # Check for urgent keywords
            title = task.get('title', '').lower()
            keywords = ['urgent', 'critical', 'down', 'error', 'production', 'asap']
            keyword_boost = 2 if any(kw in title for kw in keywords) else 0
            
            task['ai_priority_score'] = min(base_score + source_score + keyword_boost, 10)
        
        # Sort by score
        tasks.sort(key=lambda t: t.get('ai_priority_score', 5), reverse=True)
        
        return tasks
    
    def get_daily_summary(self, tasks: List[Dict[str, Any]]) -> str:
        """Get AI-generated daily summary."""
        if not self.enabled:
            return self._fallback_summary(tasks)
        
        try:
            prompt = f"""Provide a brief daily summary for these tasks:
{json.dumps([{'title': t.get('title'), 'priority': t.get('priority'), 'status': t.get('status')} for t in tasks[:10]], indent=2)}

Keep it short (2-3 sentences), highlighting urgent items and overall workload."""
            
            if self.ai_provider == 'anthropic':
                from anthropic import Anthropic
                client = Anthropic(api_key=self.api_key)
                response = client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            else:  # ollama
                import ollama
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response['message']['content'].strip()
        
        except Exception as e:
            print(f"AI summary error: {e}")
            return self._fallback_summary(tasks)
    
    def _fallback_summary(self, tasks: List[Dict[str, Any]]) -> str:
        """Fallback summary without AI."""
        total = len(tasks)
        urgent = len([t for t in tasks if t.get('priority') == 'urgent'])
        done = len([t for t in tasks if t.get('status') == 'done'])
        
        if urgent > 0:
            return f"⚠️ You have {urgent} urgent task(s) requiring immediate attention. Total: {total} tasks, {done} completed."
        else:
            return f"✅ No urgent items. You have {total} tasks, {done} completed. Good progress!"
    
    def generate_insights(self, prompt: str, mcp_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI insights for a task or ticket.
        
        Args:
            prompt: The prompt to send to AI
            mcp_context: Optional MCP data to include (ArgoCD status, etc.)
        """
        if not self.enabled:
            return self._fallback_insights()
        
        try:
            # Enhance prompt with MCP context if available
            enhanced_prompt = prompt
            if mcp_context and mcp_context.get('available'):
                enhanced_prompt += f"\n\n📊 Real-time Infrastructure Context (via MCP):\n{json.dumps(mcp_context, indent=2)}"
                enhanced_prompt += "\n\nUse this real-time data to provide more accurate recommendations."
            
            if self.ai_provider == 'anthropic':
                from anthropic import Anthropic
                client = Anthropic(api_key=self.api_key)
                response = client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": enhanced_prompt}]
                )
                return response.content[0].text.strip()
            else:  # ollama
                import ollama
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[{"role": "user", "content": enhanced_prompt}]
                )
                return response['message']['content'].strip()
        
        except Exception as e:
            print(f"AI insights error: {e}")
            return self._fallback_insights()
    
    def _fallback_insights(self) -> str:
        """Fallback insights when AI is not available."""
        return """📊 AI Insights (Limited Mode)

AI features are currently unavailable. Set ANTHROPIC_API_KEY in your .env file to enable full AI insights.

💡 General Recommendations:
• Review the priority and status
• Break down complex tasks into smaller steps
• Set clear deadlines and milestones
• Communicate progress with stakeholders

To enable full AI insights, add your Anthropic API key to the .env file."""
    
    def get_item_ai_insights(self, item: Dict[str, Any], item_type: str = "task") -> str:
        """
        Get AI insights for a specific task or Jira ticket when user clicks on it.
        NOW WITH MCP INTEGRATION for real-time ArgoCD context!
        
        Args:
            item: Task or Jira ticket dictionary
            item_type: "task" or "jira_ticket"
            
        Returns:
            AI-generated insights string with live MCP data
        """
        if not self.enabled:
            return self._fallback_insights()
        
        try:
            from anthropic import Anthropic
            from backend.services.mcp_integration_helper import mcp_helper
            
            client = Anthropic(api_key=self.api_key)
            
            # 🔥 NEW: Get live MCP context for this item
            mcp_context = mcp_helper.get_mcp_context_for_item(item)
            
            # Build context-aware prompt with MCP data
            if item_type == "jira_ticket":
                prompt = f"""Analyze this Jira ticket and provide actionable insights:

**Ticket:** {item.get('key', 'Unknown')}
**Summary:** {item.get('summary', 'No summary')}
**Status:** {item.get('status', 'Unknown')}
**Priority:** {item.get('priority', 'Unknown')}
**Type:** {item.get('type', 'Unknown')}
**URL:** {item.get('url', '')}"""

                # 🚀 Add live ArgoCD MCP data if available
                if mcp_context and mcp_context.get('available'):
                    prompt += f"""

📊 **LIVE ArgoCD Status (via MCP):**
"""
                    if mcp_context.get('mentioned_apps'):
                        prompt += "\n**Related Applications Detected:**\n"
                        for app in mcp_context['mentioned_apps']:
                            prompt += f"• {app['name']}: {app['health']}, {app['sync_status']}"
                            if app.get('out_of_sync_resources'):
                                prompt += f" ({app['out_of_sync_resources']} resources need sync)"
                            prompt += f" | Last sync: {app.get('last_sync', 'Unknown')}\n"
                    
                    if mcp_context.get('summary'):
                        summary = mcp_context['summary']
                        prompt += f"""
**Cluster Health Summary:**
• Total Apps: {summary.get('total_apps', 0)}
• Healthy: {summary.get('healthy', 0)} | Degraded: {summary.get('degraded', 0)}
• Synced: {summary.get('synced', 0)} | Out of Sync: {summary.get('out_of_sync', 0)}
"""
                
                prompt += """

Provide:
1. 📊 Quick Status Assessment (consider LIVE ArgoCD data if provided)
2. 💡 Key Actions Needed (3-4 bullet points)
3. ⚠️ Potential Blockers or Risks (check if related apps are healthy/synced)
4. 🎯 Recommended Next Steps (factor in current infrastructure state)

Keep it concise and actionable. If ArgoCD data shows issues, prioritize those!"""

            else:  # task
                prompt = f"""Analyze this task and provide actionable insights:

**Title:** {item.get('title', 'Unknown')}
**Description:** {item.get('description', 'No description')[:300]}
**Status:** {item.get('status', 'Unknown')}
**Priority:** {item.get('priority', 'Unknown')}
**Source:** {item.get('source', 'Manual')}
**Source URL:** {item.get('source_url', 'N/A')}"""

                # 🚀 Add live ArgoCD MCP data if available
                if mcp_context and mcp_context.get('available'):
                    prompt += f"""

📊 **LIVE ArgoCD Status (via MCP):**
"""
                    if mcp_context.get('mentioned_apps'):
                        prompt += "\n**Related Applications Detected:**\n"
                        for app in mcp_context['mentioned_apps']:
                            prompt += f"• {app['name']}: {app['health']}, {app['sync_status']}"
                            if app.get('out_of_sync_resources'):
                                prompt += f" ({app['out_of_sync_resources']} resources need sync)"
                            prompt += f" | Last sync: {app.get('last_sync', 'Unknown')}\n"
                    
                    if mcp_context.get('summary'):
                        summary = mcp_context['summary']
                        prompt += f"""
**Cluster Health Summary:**
• Total Apps: {summary.get('total_apps', 0)}
• Healthy: {summary.get('healthy', 0)} | Degraded: {summary.get('degraded', 0)}
• Synced: {summary.get('synced', 0)} | Out of Sync: {summary.get('out_of_sync', 0)}
"""
                
                prompt += """

Provide:
1. 📊 Quick Status Assessment (consider LIVE ArgoCD data if provided)
2. 💡 Key Actions Needed (3-4 bullet points)
3. ⚠️ Potential Blockers or Risks (check if related apps are healthy/synced)
4. 🎯 Recommended Next Steps (factor in current infrastructure state)

Keep it concise and actionable. Focus on DevOps/Infrastructure context."""
            
            response = client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Add MCP attribution if data was used
            ai_response = response.content[0].text.strip()
            if mcp_context and mcp_context.get('available'):
                ai_response = "🔌 *Enhanced with live ArgoCD MCP data*\n\n" + ai_response
            
            return ai_response
        
        except Exception as e:
            print(f"AI insights error: {e}")
            return self._fallback_insights()


# Global AI service instance
ai_service = AIService()

