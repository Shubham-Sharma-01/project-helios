"""
GitHub AI Handler - Natural language interface to GitHub.

Enables AI to understand and execute GitHub operations via chat.
"""
from typing import Dict, Any, List, Optional, Tuple
from backend.services.github_integration import GitHubIntegrationService
import re


class GitHubAIHandler:
    """
    AI-friendly GitHub operations handler.
    
    Translates natural language queries into GitHub API calls.
    """
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.github = GitHubIntegrationService(user_id=user_id)
        self.default_owner = None  # Can be set by user
        self.default_repo = None
    
    def handle_query(self, query: str) -> Tuple[bool, str]:
        """
        Handle natural language GitHub query.
        
        Args:
            query: Natural language query
            
        Returns:
            (success, formatted_response)
        """
        if not self.github.is_available():
            return False, "⚠️ GitHub integration not configured. Add GITHUB_TOKEN to .env file."
        
        query_lower = query.lower()
        
        # List repositories
        if any(phrase in query_lower for phrase in ['list repos', 'show repos', 'my repositories', 'what repos']):
            return self._list_repositories(query)
        
        # Pull requests
        elif any(phrase in query_lower for phrase in ['pull requests', 'prs', 'show prs', 'list prs']):
            return self._list_pull_requests(query)
        
        # Issues
        elif any(phrase in query_lower for phrase in ['issues', 'show issues', 'list issues', 'bugs']):
            return self._list_issues(query)
        
        # Create issue
        elif any(phrase in query_lower for phrase in ['create issue', 'new issue', 'add issue', 'report bug']):
            return self._create_issue(query)
        
        # Commits
        elif any(phrase in query_lower for phrase in ['commits', 'show commits', 'recent commits', 'commit history']):
            return self._list_commits(query)
        
        # Branches
        elif any(phrase in query_lower for phrase in ['branches', 'show branches', 'list branches']):
            return self._list_branches(query)
        
        # Repository stats
        elif any(phrase in query_lower for phrase in ['repo stats', 'repository statistics', 'repo info']):
            return self._get_repo_stats(query)
        
        # Code search
        elif any(phrase in query_lower for phrase in ['search code', 'find code', 'search in repo']):
            return True, "🔍 Code search coming soon! For now, use GitHub.com/owner/repo to search."
        
        # General GitHub help
        else:
            return self._github_help()
    
    def _list_repositories(self, query: str) -> Tuple[bool, str]:
        """List repositories."""
        # Try to extract org/user from query
        org_match = re.search(r'(?:for|from|in|org|organization)\s+(\w+)', query.lower())
        org = org_match.group(1) if org_match else None
        
        result = self.github.list_repositories(org=org)
        
        if not result.get("success"):
            return False, f"❌ {result.get('error', 'Failed to fetch repositories')}"
        
        repos = result["repositories"]
        
        if not repos:
            return True, "No repositories found."
        
        response = f"**📚 GitHub Repositories ({result['count']} total):**\n\n"
        
        for i, repo in enumerate(repos[:10], 1):  # Show top 10
            visibility = "🔒 Private" if repo["private"] else "🔓 Public"
            response += f"{i}. **{repo['name']}** {visibility}\n"
            response += f"   Language: {repo['language']} | ⭐ {repo['stars']} stars | 🔀 {repo['forks']} forks\n"
            if repo['description']:
                response += f"   {repo['description'][:100]}\n"
            response += f"   📂 {repo['full_name']}\n\n"
        
        if len(repos) > 10:
            response += f"_...and {len(repos) - 10} more repositories_\n"
        
        return True, response
    
    def _list_pull_requests(self, query: str) -> Tuple[bool, str]:
        """List pull requests."""
        # Extract repo from query
        owner, repo = self._extract_repo_from_query(query)
        
        if not owner or not repo:
            return False, "❌ Please specify repository: e.g., 'show PRs for owner/repo'"
        
        # Check state (open, closed, all)
        state = "open"
        if "closed" in query.lower():
            state = "closed"
        elif "all" in query.lower():
            state = "all"
        
        result = self.github.list_pull_requests(owner, repo, state)
        
        if not result.get("success"):
            return False, f"❌ {result.get('error', 'Failed to fetch PRs')}"
        
        prs = result["pull_requests"]
        
        if not prs:
            return True, f"No {state} pull requests found for {owner}/{repo}"
        
        response = f"**🔀 Pull Requests for {owner}/{repo} ({state}):**\n\n"
        
        for pr in prs[:10]:
            status_emoji = "🟢" if pr["state"] == "open" else "🔴"
            response += f"{status_emoji} **PR #{pr['number']}: {pr['title']}**\n"
            response += f"   By: {pr['author']} | {pr['head_branch']} → {pr['base_branch']}\n"
            if pr['labels']:
                response += f"   Labels: {', '.join(pr['labels'])}\n"
            response += f"   🔗 {pr['url']}\n\n"
        
        return True, response
    
    def _list_issues(self, query: str) -> Tuple[bool, str]:
        """List issues."""
        owner, repo = self._extract_repo_from_query(query)
        
        if not owner or not repo:
            return False, "❌ Please specify repository: e.g., 'show issues for owner/repo'"
        
        state = "open"
        if "closed" in query.lower():
            state = "closed"
        
        result = self.github.list_issues(owner, repo, state)
        
        if not result.get("success"):
            return False, f"❌ {result.get('error', 'Failed to fetch issues')}"
        
        issues = result["issues"]
        
        if not issues:
            return True, f"No {state} issues found for {owner}/{repo}"
        
        response = f"**🐛 Issues for {owner}/{repo} ({state}):**\n\n"
        
        for issue in issues[:10]:
            response += f"**Issue #{issue['number']}: {issue['title']}**\n"
            response += f"   By: {issue['author']} | 💬 {issue['comments']} comments\n"
            if issue['labels']:
                response += f"   Labels: {', '.join(issue['labels'])}\n"
            response += f"   🔗 {issue['url']}\n\n"
        
        return True, response
    
    def _create_issue(self, query: str) -> Tuple[bool, str]:
        """Create a GitHub issue from natural language."""
        # Extract repo
        owner, repo = self._extract_repo_from_query(query)
        
        if not owner or not repo:
            return False, "❌ Please specify repository: e.g., 'create issue in owner/repo: title here'"
        
        # Extract title
        title_match = re.search(r'(?:create issue|new issue|add issue)(?:\s+in\s+[\w/-]+)?[:\s]+(.+)', query, re.IGNORECASE)
        
        if not title_match:
            return False, "❌ Please provide issue title: e.g., 'create issue: Fix login bug'"
        
        title = title_match.group(1).strip()
        
        result = self.github.create_issue(owner, repo, title)
        
        if not result.get("success"):
            return False, f"❌ {result.get('error', 'Failed to create issue')}"
        
        issue = result["issue"]
        
        response = f"✅ **GitHub Issue Created!**\n\n"
        response += f"**Issue #{issue['number']}:** {issue['title']}\n"
        response += f"**Repository:** {owner}/{repo}\n"
        response += f"**URL:** {issue['url']}\n"
        
        return True, response
    
    def _list_commits(self, query: str) -> Tuple[bool, str]:
        """List recent commits."""
        owner, repo = self._extract_repo_from_query(query)
        
        if not owner or not repo:
            return False, "❌ Please specify repository: e.g., 'show commits for owner/repo'"
        
        # Extract limit
        limit_match = re.search(r'(\d+)\s+commits', query.lower())
        limit = int(limit_match.group(1)) if limit_match else 10
        limit = min(limit, 20)  # Max 20
        
        result = self.github.list_commits(owner, repo, limit=limit)
        
        if not result.get("success"):
            return False, f"❌ {result.get('error', 'Failed to fetch commits')}"
        
        commits = result["commits"]
        
        if not commits:
            return True, f"No commits found for {owner}/{repo}"
        
        response = f"**📝 Recent Commits for {owner}/{repo}:**\n\n"
        
        for commit in commits:
            response += f"• `{commit['sha']}` - {commit['message']}\n"
            response += f"  By: {commit['author']} | {self._format_date(commit['date'])}\n\n"
        
        return True, response
    
    def _list_branches(self, query: str) -> Tuple[bool, str]:
        """List branches."""
        owner, repo = self._extract_repo_from_query(query)
        
        if not owner or not repo:
            return False, "❌ Please specify repository: e.g., 'show branches for owner/repo'"
        
        result = self.github.list_branches(owner, repo)
        
        if not result.get("success"):
            return False, f"❌ {result.get('error', 'Failed to fetch branches')}"
        
        branches = result["branches"]
        
        if not branches:
            return True, f"No branches found for {owner}/{repo}"
        
        response = f"**🌿 Branches for {owner}/{repo}:**\n\n"
        
        for branch in branches:
            protected = "🔒" if branch["protected"] else ""
            response += f"• **{branch['name']}** {protected}\n"
            response += f"  Last commit: `{branch['commit_sha']}`\n"
        
        return True, response
    
    def _get_repo_stats(self, query: str) -> Tuple[bool, str]:
        """Get repository statistics."""
        owner, repo = self._extract_repo_from_query(query)
        
        if not owner or not repo:
            return False, "❌ Please specify repository: e.g., 'repo stats for owner/repo'"
        
        result = self.github.get_repository_stats(owner, repo)
        
        if not result.get("success"):
            return False, f"❌ {result.get('error', 'Failed to fetch stats')}"
        
        stats = result["stats"]
        
        response = f"**📊 Repository Statistics: {stats['repository']}**\n\n"
        response += f"**Engagement:**\n"
        response += f"• ⭐ Stars: {stats['stars']}\n"
        response += f"• 🔀 Forks: {stats['forks']}\n"
        response += f"• 👀 Watchers: {stats['watchers']}\n"
        response += f"• 🐛 Open Issues: {stats['open_issues']}\n\n"
        
        if stats.get("top_contributors"):
            response += f"**Top Contributors:**\n"
            for contrib in stats["top_contributors"]:
                response += f"• {contrib['username']}: {contrib['contributions']} contributions\n"
            response += "\n"
        
        if stats.get("languages"):
            response += f"**Languages:** {', '.join(list(stats['languages'].keys())[:5])}\n\n"
        
        response += f"**Dates:**\n"
        response += f"• Created: {self._format_date(stats['created'])}\n"
        response += f"• Updated: {self._format_date(stats['last_updated'])}\n"
        
        return True, response
    
    def _github_help(self) -> Tuple[bool, str]:
        """Provide GitHub help."""
        response = """**🐙 GitHub Integration Help**

**Available Commands:**

**Repositories:**
• "List my repos"
• "Show repos for organization_name"
• "Repository stats for owner/repo"

**Pull Requests:**
• "Show PRs for owner/repo"
• "List open PRs for owner/repo"
• "Show closed PRs for owner/repo"

**Issues:**
• "Show issues for owner/repo"
• "List bugs for owner/repo"
• "Create issue in owner/repo: Bug title here"

**Commits:**
• "Show commits for owner/repo"
• "Show last 20 commits for owner/repo"

**Branches:**
• "List branches for owner/repo"
• "Show branches for owner/repo"

**Examples:**
• "Show PRs for facebook/react"
• "List repos for microsoft"
• "Create issue in myorg/myrepo: Fix login bug"
• "Show commits for torvalds/linux"

💡 Tip: Replace owner/repo with your actual GitHub repository!
"""
        return True, response
    
    def _extract_repo_from_query(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract owner/repo from query."""
        # Pattern 1: explicit "owner/repo" format
        repo_match = re.search(r'(?:for|in|from)\s+([\w-]+)/([\w-]+)', query)
        if repo_match:
            return repo_match.group(1), repo_match.group(2)
        
        # Pattern 2: Just "owner/repo" somewhere in query
        repo_match = re.search(r'\b([\w-]+)/([\w-]+)\b', query)
        if repo_match:
            return repo_match.group(1), repo_match.group(2)
        
        # Pattern 3: GitHub URL
        url_match = re.search(r'github\.com/([\w-]+)/([\w-]+)', query)
        if url_match:
            return url_match.group(1), url_match.group(2)
        
        # Fallback to defaults if set
        if self.default_owner and self.default_repo:
            return self.default_owner, self.default_repo
        
        return None, None
    
    def _format_date(self, date_str: str) -> str:
        """Format ISO date to human-readable."""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            delta = now - dt
            
            if delta.days == 0:
                if delta.seconds < 3600:
                    return f"{delta.seconds // 60} minutes ago"
                else:
                    return f"{delta.seconds // 3600} hours ago"
            elif delta.days == 1:
                return "yesterday"
            elif delta.days < 7:
                return f"{delta.days} days ago"
            else:
                return dt.strftime("%Y-%m-%d")
        except:
            return date_str
    
    def set_default_repository(self, owner: str, repo: str):
        """Set default repository for queries."""
        self.default_owner = owner
        self.default_repo = repo
        print(f"✅ Default repository set to: {owner}/{repo}")

