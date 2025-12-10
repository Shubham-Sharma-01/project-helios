"""
Ollama Chat Service V2 - TRUE Natural Language Processing
Uses Ollama LLM to understand intent, then executes actions.
"""
from typing import List, Dict, Any, Tuple, Optional
import os
import json
import re


class OllamaChatServiceV2:
    """Chat service that uses Ollama for natural language understanding."""
    
    def __init__(self):
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b-instruct-q4_K_M')
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.enabled = True
        self.conversation_history = []
        
        print(f"✅ Ollama Chat Service V2 initialized (TRUE NLP)")
        print(f"   Model: {self.model}")
        print(f"   Server: {self.base_url}")
    
    def chat(self, message: str, context: dict = None, user_id: str = None) -> Tuple[str, str]:
        """
        Process message using Ollama's natural language understanding.
        
        Flow:
        1. Ollama understands the query naturally
        2. Ollama decides if it needs to call a function
        3. We execute the function
        4. Ollama formats the final response
        """
        if not self.enabled:
            return "⚠️ Ollama service not available.", "error"
        
        try:
            import ollama
            
            # Build system prompt with available functions
            system_prompt = self._build_system_prompt_with_tools(context, user_id)
            
            # First pass: Let Ollama understand the query
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add conversation history
            for msg in self.conversation_history[-4:]:  # Last 2 exchanges
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Current message
            messages.append({"role": "user", "content": message})
            
            print(f"\n🤖 Ollama processing: {message}")
            
            # Get Ollama's response
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            ai_response = response['message']['content']
            
            print(f"🧠 Ollama understood: {ai_response[:100]}...")
            
            # Check if Ollama wants to call a function
            function_call = self._extract_function_call(ai_response)
            
            if function_call:
                print(f"🔧 Function call detected: {function_call['function']}")
                
                # Execute the function
                result = self._execute_function(function_call, user_id, context)
                
                # Send result back to Ollama for formatting
                followup_messages = messages + [
                    {"role": "assistant", "content": ai_response},
                    {"role": "user", "content": f"Function result: {json.dumps(result)}"}
                ]
                
                final_response = ollama.chat(
                    model=self.model,
                    messages=followup_messages
                )
                
                final_answer = final_response['message']['content']
                
                # Update history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": final_answer})
                
                return final_answer, "function_executed"
            
            # No function call, just return Ollama's response
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response, "ai_response"
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ Error: {str(e)}", "error"
    
    def _build_system_prompt_with_tools(self, context: dict, user_id: str) -> str:
        """Build system prompt that tells Ollama about available tools."""
        
        prompt = """You are Helios ☀️, an expert DevOps AI assistant with access to powerful tools and live data.

Your name is Helios - named after the Greek god of the sun, you bring light and clarity to DevOps challenges!

🎯 YOUR CAPABILITIES:

**1. GitHub Operations** (if user has GitHub integrated):
   - list_github_repos() - List user's repositories
   - get_repo_info(owner, repo) - Get repository details
   - list_pull_requests(owner, repo, state) - List PRs
   - list_issues(owner, repo) - List issues
   - list_commits(owner, repo, limit) - List recent commits (includes commit details)
   - list_branches(owner, repo) - List branches
   - get_repo_stats(owner, repo) - Get complete repository statistics
   
   Note: For commit details, use list_commits - it includes all commit info!

**2. Task Management**:
   - create_task(title, description, priority) - Create new task
   - delete_task(task_id) - Delete a task
   - list_tasks(status, priority) - List/filter tasks
   - update_task(task_id, updates) - Update a task

**3. Smart Features**:
   - predict_issues() - Predictive analytics
   - troubleshoot(issue) - Interactive debugging
   - get_recommendations() - Smart suggestions
   - get_dashboard() - Custom metrics

**4. Integration Info**:
   - list_integrations() - Show configured integrations

⚡ HOW TO USE FUNCTIONS:

When you need to call a function, respond with:
FUNCTION_CALL: function_name(param1="value1", param2="value2")

Example:
User: "Show my GitHub repos"
You: "I'll fetch your GitHub repositories. FUNCTION_CALL: list_github_repos()"

User: "Show PRs for facebook/react"
You: "I'll check the pull requests for facebook/react. FUNCTION_CALL: list_pull_requests(owner="facebook", repo="react", state="open")"

User: "Show commits for Shubham-Sharma-01/helm-app-project"
You: "I'll list the commits for that repository. FUNCTION_CALL: list_commits(owner="Shubham-Sharma-01", repo="helm-app-project", limit="10")"

User: "Create a task to fix the bug"
You: "I'll create that task for you. FUNCTION_CALL: create_task(title="Fix the bug", priority="MEDIUM")"

⚠️ IMPORTANT RULES:
1. Use FUNCTION_CALL when you need live data from systems
2. Extract parameters from the user's question intelligently
3. For GitHub queries, parse owner/repo from the user's message
4. If user says "my repos" or "my GitHub", use list_github_repos()
5. Be conversational and explain what you're doing
6. After function executes, I'll give you results to format nicely

"""
        
        # Add current context
        if context:
            prompt += "\n\n📊 CURRENT APP STATE:\n"
            
            if context.get('tasks'):
                tasks = context['tasks']
                if isinstance(tasks, dict):
                    tasks_list = tasks.get('all_tasks', [])
                else:
                    tasks_list = tasks
                
                if tasks_list:
                    prompt += f"\n📋 Tasks: {len(tasks_list)} total"
                    todo = len([t for t in tasks_list if t.get('status') == 'TODO'])
                    in_progress = len([t for t in tasks_list if t.get('status') == 'IN_PROGRESS'])
                    done = len([t for t in tasks_list if t.get('status') == 'DONE'])
                    prompt += f" ({todo} TODO, {in_progress} IN PROGRESS, {done} DONE)"
                else:
                    prompt += "\n📋 Tasks: None yet"
            
            if context.get('integrations'):
                integrations = context['integrations']
                if isinstance(integrations, dict):
                    integ_list = integrations.get('all', [])
                else:
                    integ_list = integrations
                
                if integ_list:
                    prompt += f"\n🔗 Integrations: {len(integ_list)} configured"
                    github = [i for i in integ_list if i.get('type') == 'github' and i.get('status') == 'active']
                    if github:
                        prompt += " (GitHub ✅ ACTIVE)"
                    else:
                        prompt += " (GitHub ❌ not configured)"
                else:
                    prompt += "\n🔗 Integrations: None configured"
        
        prompt += "\n\nBe helpful, concise, and use functions when appropriate!"
        
        return prompt
    
    def _extract_function_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract function call from Ollama's response."""
        
        # Look for FUNCTION_CALL: pattern
        match = re.search(r'FUNCTION_CALL:\s*(\w+)\((.*?)\)', response, re.IGNORECASE)
        
        if not match:
            return None
        
        function_name = match.group(1)
        params_str = match.group(2)
        
        # Parse parameters
        params = {}
        if params_str:
            # Simple parameter parsing (key="value" or key='value')
            param_matches = re.findall(r'(\w+)=["\']([^"\']+)["\']', params_str)
            for key, value in param_matches:
                params[key] = value
        
        return {
            "function": function_name,
            "parameters": params
        }
    
    def _execute_function(self, function_call: Dict[str, Any], user_id: str, context: dict) -> Dict[str, Any]:
        """Execute the requested function."""
        
        function_name = function_call["function"]
        params = function_call["parameters"]
        
        try:
            # GitHub functions
            if function_name == "list_github_repos":
                from backend.services.github_integration import GitHubIntegrationService
                github = GitHubIntegrationService(user_id=user_id)
                
                if not github.is_available():
                    return {
                        "success": False, 
                        "error": "GitHub integration not configured",
                        "message": "Please add GitHub integration in Settings → Integrations. Go to https://github.com/settings/tokens to get a token."
                    }
                
                result = github.list_repositories(
                    user=params.get("user"),
                    org=params.get("org")
                )
                return result
            
            elif function_name == "get_repo_info":
                from backend.services.github_integration import GitHubIntegrationService
                github = GitHubIntegrationService(user_id=user_id)
                result = github.get_repository(
                    owner=params.get("owner"),
                    repo=params.get("repo")
                )
                return result
            
            elif function_name == "list_pull_requests":
                from backend.services.github_integration import GitHubIntegrationService
                github = GitHubIntegrationService(user_id=user_id)
                result = github.list_pull_requests(
                    owner=params.get("owner"),
                    repo=params.get("repo"),
                    state=params.get("state", "open")
                )
                return result
            
            elif function_name == "list_issues":
                from backend.services.github_integration import GitHubIntegrationService
                github = GitHubIntegrationService(user_id=user_id)
                result = github.list_issues(
                    owner=params.get("owner"),
                    repo=params.get("repo")
                )
                return result
            
            elif function_name == "list_commits":
                from backend.services.github_integration import GitHubIntegrationService
                github = GitHubIntegrationService(user_id=user_id)
                
                if not github.is_available():
                    return {
                        "success": False, 
                        "error": "GitHub integration not configured",
                        "message": "Please add GitHub integration in Settings → Integrations"
                    }
                
                result = github.list_commits(
                    owner=params.get("owner"),
                    repo=params.get("repo"),
                    limit=int(params.get("limit", "10"))
                )
                return result
            
            elif function_name == "list_branches":
                from backend.services.github_integration import GitHubIntegrationService
                github = GitHubIntegrationService(user_id=user_id)
                result = github.list_branches(
                    owner=params.get("owner"),
                    repo=params.get("repo")
                )
                return result
            
            elif function_name == "get_repo_stats":
                from backend.services.github_integration import GitHubIntegrationService
                github = GitHubIntegrationService(user_id=user_id)
                result = github.get_repository_stats(
                    owner=params.get("owner"),
                    repo=params.get("repo")
                )
                return result
            
            # Task management functions
            elif function_name == "create_task":
                from backend.services.task_service import TaskService
                from backend.models import TaskPriority
                
                priority_str = params.get("priority", "MEDIUM").upper()
                priority_map = {
                    'LOW': TaskPriority.LOW,
                    'MEDIUM': TaskPriority.MEDIUM,
                    'HIGH': TaskPriority.HIGH,
                    'URGENT': TaskPriority.URGENT
                }
                priority = priority_map.get(priority_str, TaskPriority.MEDIUM)
                
                task_id = TaskService.create_task(
                    user_id=user_id,
                    title=params.get("title"),
                    description=params.get("description", ""),
                    priority=priority
                )
                return {"success": True, "task_id": task_id, "title": params.get("title")}
            
            elif function_name == "list_tasks":
                from backend.services.task_service import TaskService
                tasks = TaskService.get_user_tasks(user_id)
                return {"success": True, "tasks": tasks, "count": len(tasks)}
            
            # Other functions can be added here
            
            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def is_available(self) -> bool:
        """Check if service is available."""
        return self.enabled


# Global instance
ollama_chat_v2 = OllamaChatServiceV2()

