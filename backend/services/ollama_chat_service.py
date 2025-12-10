"""
Simple Ollama Chat Service - Direct LLM interaction with action execution.
"""
from typing import List, Dict, Any, Tuple, Optional
import os

class OllamaChatService:
    """Simple chat service using Ollama directly."""
    
    def __init__(self):
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b-instruct-q4_K_M')
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.enabled = True
        self.conversation_history = []
        
        print(f"✅ Ollama Chat Service initialized")
        print(f"   Model: {self.model}")
        print(f"   Server: {self.base_url}")
        print(f"   Cost: FREE (100% Local)")
    
    def chat(self, message: str, context: dict = None, user_id: str = None) -> Tuple[str, Optional[str]]:
        """
        Send a message to Ollama with app context and action execution.
        
        Args:
            message: User's message
            context: Dict with app data (tasks, integrations, etc.)
            user_id: User ID for executing actions
            
        Returns:
            (AI's response, action_result or None)
        """
        if not self.enabled:
            return "⚠️ Ollama service is not available.", None
        
        try:
            import ollama
            import json
            from backend.services.ai_action_handler import AIActionHandler
            
            # Step 1: Check if this is an action request
            action_executed = False
            action_result = None
            
            if user_id:
                action_handler = AIActionHandler(user_id)
                
                # Try to detect and execute action
                is_action, result = action_handler.detect_and_execute_action(message, context or {})
                
                if is_action:
                    action_executed = True
                    action_result = result
                    
                    # If action succeeded, return early with result
                    if result:
                        return result, "action_executed"
            
            # Build enhanced prompt with REAL context
            enhanced_message = message
            
            if context:
                # Add REAL data to the message
                context_info = "\n\n=== REAL-TIME APP DATA (Use ONLY this data, do NOT make up tasks!) ===\n"
                
                if context.get('tasks'):
                    # Handle both old format (list) and new format (dict with 'all_tasks')
                    tasks_data = context['tasks']
                    if isinstance(tasks_data, dict):
                        tasks = tasks_data.get('all_tasks', [])
                    else:
                        tasks = tasks_data
                    
                    if len(tasks) == 0:
                        context_info += "\n📋 **Tasks:** NO TASKS EXIST YET\n"
                        context_info += "   Tell the user they have no tasks and suggest creating one.\n"
                    else:
                        context_info += f"\n📋 **Your Tasks ({len(tasks)} total):**\n"
                        
                        # Group by status
                        todo = [t for t in tasks if t.get('status') == 'TODO']
                        in_progress = [t for t in tasks if t.get('status') == 'IN_PROGRESS']
                        done = [t for t in tasks if t.get('status') == 'DONE']
                        
                        if todo:
                            context_info += f"\n  📝 TO DO ({len(todo)} tasks):\n"
                            for t in todo[:5]:  # Show up to 5
                                task_id_short = t.get('id', 'N/A')[:8] if t.get('id') else 'N/A'
                                context_info += f"    - {t.get('title', 'Untitled')} (Priority: {t.get('priority', 'N/A')}, ID: {task_id_short})\n"
                        
                        if in_progress:
                            context_info += f"\n  🚀 IN PROGRESS ({len(in_progress)} tasks):\n"
                            for t in in_progress[:5]:
                                task_id_short = t.get('id', 'N/A')[:8] if t.get('id') else 'N/A'
                                context_info += f"    - {t.get('title', 'Untitled')} (Priority: {t.get('priority', 'N/A')}, ID: {task_id_short})\n"
                        
                        if done:
                            context_info += f"\n  ✅ DONE ({len(done)} tasks)\n"
                        
                        if not todo and not in_progress and not done:
                            context_info += "   (All tasks are in other statuses)\n"
                else:
                    context_info += "\n📋 **Tasks:** NO TASK DATA AVAILABLE\n"
                
                if context.get('integrations'):
                    # Handle both old format (list) and new format (dict with 'all')
                    integ_data = context['integrations']
                    if isinstance(integ_data, dict):
                        integ = integ_data.get('all', [])
                    else:
                        integ = integ_data
                    
                    if len(integ) == 0:
                        context_info += f"\n🔗 **Integrations:** NONE CONFIGURED\n"
                    else:
                        context_info += f"\n🔗 **Integrations ({len(integ)} configured):**\n"
                        for i in integ:
                            status = "✅ ACTIVE" if i.get('status') == 'ACTIVE' else f"⚠️ {i.get('status', 'UNKNOWN')}"
                            context_info += f"  • {i.get('name', 'Unknown')} ({i.get('type', 'unknown')}): {status}\n"
                else:
                    context_info += f"\n🔗 **Integrations:** NO DATA AVAILABLE\n"
                
                if context.get('user_info'):
                    context_info += f"\n👤 **User:** {context['user_info']}\n"
                
                context_info += "\n=== END OF REAL DATA ===\n"
                context_info += "\n⚠️ IMPORTANT: Use ONLY the data above. Do NOT invent or make up tasks/integrations!\n"
                context_info += "If the user asks about tasks and there are none, tell them clearly that no tasks exist yet.\n\n"
                
                # Prepend context to message
                enhanced_message = context_info + "**User Question:** " + message
            
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": enhanced_message
            })
            
            # Keep only last 6 messages for context (3 exchanges)
            if len(self.conversation_history) > 6:
                self.conversation_history = self.conversation_history[-6:]
            
            # Add system prompt if this is the first message
            messages_to_send = []
            if len(self.conversation_history) == 1:
                messages_to_send.append({
                    "role": "system",
                    "content": """You are an expert DevOps AI assistant integrated into a DevOps Command Center app.

⚠️ CRITICAL RULES:
1. You will receive REAL-TIME data about the user's tasks and integrations
2. Use ONLY the data provided in the context - NEVER make up or hallucinate tasks!
3. If the context says "NO TASKS EXIST", tell the user they have no tasks
4. If the context says "NO INTEGRATIONS", tell them no integrations are configured
5. Do NOT invent task IDs, titles, or details that weren't provided

When answering:
- Be concise and actionable
- Reference ONLY tasks/integrations from the provided context
- Provide DevOps best practices and advice
- Help prioritize and organize work
- Use emojis to make it friendly
- If no data exists, help them get started

🎯 YOUR ADVANCED CAPABILITIES:
- Task Management (create, delete, update, list)
- Predictive Analytics (predict issues, analyze patterns)
- Interactive Troubleshooting (debug problems)
- Smart Recommendations (optimize workflows)
- DevOps Orchestration (control deployments)
- GitHub Integration (repos, PRs, issues, commits)
- Custom Dashboards (generate insights)

Example good responses:
- "You currently have no tasks. Would you like to create your first task?"
- "Based on your 3 tasks, here's what I see: ..." (only if tasks are provided)
- "Let me analyze your workload and predict potential issues..."
- "I can help troubleshoot that problem. What symptoms are you seeing?"

NEVER respond with made-up task IDs or data that wasn't in the context!"""
                })
            
            messages_to_send.extend(self.conversation_history)
            
            # Debug: Print what we're sending to Ollama
            print(f"\n{'='*60}")
            print(f"🤖 Ollama Query")
            print(f"{'='*60}")
            print(f"Model: {self.model}")
            print(f"Messages: {len(messages_to_send)}")
            if context:
                print(f"Context includes:")
                print(f"  - Tasks: {len(context.get('tasks', []))} tasks")
                print(f"  - Integrations: {len(context.get('integrations', []))} integrations")
            print(f"{'='*60}\n")
            
            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=messages_to_send
            )
            
            # Extract response
            ai_message = response['message']['content']
            
            # Add AI response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })
            
            return ai_message, None
        
        except Exception as e:
            error_msg = f"❌ Ollama error: {str(e)}"
            print(error_msg)
            
            # Check if Ollama is running
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                error_response = f"""⚠️ Cannot connect to Ollama server.

**Possible fixes:**
1. Start Ollama: `ollama serve`
2. Check if running: `ollama list`
3. Verify model is pulled: `ollama pull {self.model}`

Error details: {str(e)}"""
                return error_response, None
            
            return error_msg, None
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("💭 Conversation history cleared")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the AI system."""
        return {
            "provider": "Ollama",
            "model": self.model,
            "base_url": self.base_url,
            "cost": "FREE",
            "privacy": "100% Local",
            "enabled": self.enabled
        }


# Global instance
ollama_chat = OllamaChatService()

