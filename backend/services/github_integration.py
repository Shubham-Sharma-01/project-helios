"""
GitHub Integration Service - Complete GitHub control via AI.

Provides natural language interface to:
- Repository management
- Pull requests
- Issues
- Commits and branches
- Code reviews
- Release management
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import os
import requests
from backend.database import get_db
from backend.models import Integration, IntegrationStatus


class GitHubIntegrationService:
    """
    Natural language GitHub integration.
    
    Enables chat-based control of:
    - Repositories
    - Pull Requests
    - Issues
    - Commits
    - Branches
    - Code reviews
    """
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.api_key = None
        self.base_url = "https://api.github.com"
        self.enabled = False
        self.headers = {}
        self._load_credentials()
    
    def _load_credentials(self):
        """Load GitHub credentials from database or environment."""
        # First, try to load from database if user_id is provided
        if self.user_id:
            try:
                from backend.services.integration_service import IntegrationService
                integration_service = IntegrationService()
                integrations = integration_service.get_user_integrations(self.user_id)
                
                # Find GitHub integration (active or error - we'll try to use it anyway)
                github_integrations = [i for i in integrations if i.get('type') == 'github' and i.get('status') in ['active', 'error']]
                
                if github_integrations:
                    github_int = github_integrations[0]
                    # Get decrypted credentials
                    creds = integration_service.get_integration_credentials(github_int['id'])
                    token = creds.get('access_token') or creds.get('token') if creds else None
                    if token:
                        self.api_key = token
                        self.enabled = True
                        self.headers = {
                            "Authorization": f"Bearer {self.api_key}",
                            "Accept": "application/vnd.github.v3+json",
                            "X-GitHub-Api-Version": "2022-11-28"
                        }
                        print(f"✅ GitHub integration loaded from database for user {self.user_id}")
                        return
            except Exception as e:
                print(f"⚠️  Failed to load GitHub credentials from database: {e}")
        
        # Fallback to environment variable
        self.api_key = os.getenv('GITHUB_TOKEN')
        if self.api_key:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            print("✅ GitHub integration loaded from environment")
        else:
            print("⚠️  GitHub integration disabled (no token found in database or environment)")
    
    def is_available(self) -> bool:
        """Check if GitHub integration is available."""
        return self.enabled
    
    # ========== REPOSITORY OPERATIONS ==========
    
    def list_repositories(self, user: Optional[str] = None, org: Optional[str] = None) -> Dict[str, Any]:
        """
        List repositories for user or organization.
        
        Args:
            user: GitHub username
            org: GitHub organization name
            
        Returns:
            Repository list with metadata
        """
        if not self.enabled:
            return self._disabled_response()
        
        try:
            if org:
                url = f"{self.base_url}/orgs/{org}/repos"
            elif user:
                url = f"{self.base_url}/users/{user}/repos"
            else:
                url = f"{self.base_url}/user/repos"
            
            response = requests.get(url, headers=self.headers, params={"per_page": 20, "sort": "updated"})
            
            if response.status_code != 200:
                return {"success": False, "error": f"GitHub API error: {response.status_code}"}
            
            repos = response.json()
            
            formatted_repos = []
            for repo in repos:
                formatted_repos.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description", "No description"),
                    "language": repo.get("language", "Unknown"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "open_issues": repo.get("open_issues_count", 0),
                    "updated_at": repo.get("updated_at"),
                    "url": repo["html_url"],
                    "private": repo.get("private", False)
                })
            
            return {
                "success": True,
                "repositories": formatted_repos,
                "count": len(formatted_repos)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed information about a repository."""
        if not self.enabled:
            return self._disabled_response()
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Repository not found: {owner}/{repo}"}
            
            data = response.json()
            
            return {
                "success": True,
                "repository": {
                    "name": data["name"],
                    "full_name": data["full_name"],
                    "description": data.get("description", "No description"),
                    "language": data.get("language", "Unknown"),
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "watchers": data.get("watchers_count", 0),
                    "open_issues": data.get("open_issues_count", 0),
                    "size": data.get("size", 0),
                    "default_branch": data.get("default_branch", "main"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "url": data["html_url"],
                    "private": data.get("private", False),
                    "topics": data.get("topics", [])
                }
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== PULL REQUEST OPERATIONS ==========
    
    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """
        List pull requests for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
        """
        if not self.enabled:
            return self._disabled_response()
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            response = requests.get(url, headers=self.headers, params={"state": state, "per_page": 20})
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch PRs: {response.status_code}"}
            
            prs = response.json()
            
            formatted_prs = []
            for pr in prs:
                formatted_prs.append({
                    "number": pr["number"],
                    "title": pr["title"],
                    "state": pr["state"],
                    "author": pr["user"]["login"],
                    "created_at": pr["created_at"],
                    "updated_at": pr["updated_at"],
                    "mergeable_state": pr.get("mergeable_state", "unknown"),
                    "labels": [label["name"] for label in pr.get("labels", [])],
                    "url": pr["html_url"],
                    "head_branch": pr["head"]["ref"],
                    "base_branch": pr["base"]["ref"]
                })
            
            return {
                "success": True,
                "pull_requests": formatted_prs,
                "count": len(formatted_prs),
                "state": state
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get detailed information about a specific pull request."""
        if not self.enabled:
            return self._disabled_response()
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {"success": False, "error": f"PR #{pr_number} not found"}
            
            pr = response.json()
            
            return {
                "success": True,
                "pull_request": {
                    "number": pr["number"],
                    "title": pr["title"],
                    "description": pr.get("body", "No description"),
                    "state": pr["state"],
                    "author": pr["user"]["login"],
                    "created_at": pr["created_at"],
                    "updated_at": pr["updated_at"],
                    "merged": pr.get("merged", False),
                    "mergeable": pr.get("mergeable", None),
                    "additions": pr.get("additions", 0),
                    "deletions": pr.get("deletions", 0),
                    "changed_files": pr.get("changed_files", 0),
                    "commits": pr.get("commits", 0),
                    "url": pr["html_url"],
                    "head_branch": pr["head"]["ref"],
                    "base_branch": pr["base"]["ref"]
                }
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== ISSUE OPERATIONS ==========
    
    def list_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List issues for a repository."""
        if not self.enabled:
            return self._disabled_response()
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            response = requests.get(url, headers=self.headers, params={"state": state, "per_page": 20})
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch issues: {response.status_code}"}
            
            issues = response.json()
            
            # Filter out PRs (GitHub API returns both issues and PRs)
            filtered_issues = [issue for issue in issues if "pull_request" not in issue]
            
            formatted_issues = []
            for issue in filtered_issues:
                formatted_issues.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "author": issue["user"]["login"],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                    "labels": [label["name"] for label in issue.get("labels", [])],
                    "comments": issue.get("comments", 0),
                    "url": issue["html_url"]
                })
            
            return {
                "success": True,
                "issues": formatted_issues,
                "count": len(formatted_issues),
                "state": state
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_issue(self, owner: str, repo: str, title: str, body: Optional[str] = None, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new issue."""
        if not self.enabled:
            return self._disabled_response()
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            
            data = {
                "title": title,
                "body": body or "",
            }
            
            if labels:
                data["labels"] = labels
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code != 201:
                return {"success": False, "error": f"Failed to create issue: {response.status_code}"}
            
            issue = response.json()
            
            return {
                "success": True,
                "issue": {
                    "number": issue["number"],
                    "title": issue["title"],
                    "url": issue["html_url"],
                    "state": issue["state"]
                },
                "message": f"✅ Issue #{issue['number']} created successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== COMMIT OPERATIONS ==========
    
    def list_commits(self, owner: str, repo: str, branch: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """List recent commits."""
        if not self.enabled:
            return self._disabled_response()
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {"per_page": limit}
            
            if branch:
                params["sha"] = branch
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch commits: {response.status_code}"}
            
            commits = response.json()
            
            formatted_commits = []
            for commit in commits:
                formatted_commits.append({
                    "sha": commit["sha"][:7],
                    "full_sha": commit["sha"],
                    "message": commit["commit"]["message"].split("\n")[0],  # First line only
                    "author": commit["commit"]["author"]["name"],
                    "date": commit["commit"]["author"]["date"],
                    "url": commit["html_url"]
                })
            
            return {
                "success": True,
                "commits": formatted_commits,
                "count": len(formatted_commits),
                "branch": branch or "default"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== BRANCH OPERATIONS ==========
    
    def list_branches(self, owner: str, repo: str) -> Dict[str, Any]:
        """List repository branches."""
        if not self.enabled:
            return self._disabled_response()
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/branches"
            response = requests.get(url, headers=self.headers, params={"per_page": 20})
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch branches: {response.status_code}"}
            
            branches = response.json()
            
            formatted_branches = []
            for branch in branches:
                formatted_branches.append({
                    "name": branch["name"],
                    "protected": branch.get("protected", False),
                    "commit_sha": branch["commit"]["sha"][:7]
                })
            
            return {
                "success": True,
                "branches": formatted_branches,
                "count": len(formatted_branches)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== CODE STATISTICS ==========
    
    def get_repository_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get comprehensive repository statistics."""
        if not self.enabled:
            return self._disabled_response()
        
        try:
            # Get repo info
            repo_info = self.get_repository(owner, repo)
            if not repo_info.get("success"):
                return repo_info
            
            # Get contributors
            url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            contributors_response = requests.get(url, headers=self.headers, params={"per_page": 5})
            
            top_contributors = []
            if contributors_response.status_code == 200:
                contributors = contributors_response.json()
                top_contributors = [
                    {"username": c["login"], "contributions": c["contributions"]}
                    for c in contributors[:5]
                ]
            
            # Get languages
            url = f"{self.base_url}/repos/{owner}/{repo}/languages"
            languages_response = requests.get(url, headers=self.headers)
            
            languages = {}
            if languages_response.status_code == 200:
                languages = languages_response.json()
            
            repo_data = repo_info["repository"]
            
            return {
                "success": True,
                "stats": {
                    "repository": repo_data["full_name"],
                    "stars": repo_data["stars"],
                    "forks": repo_data["forks"],
                    "watchers": repo_data["watchers"],
                    "open_issues": repo_data["open_issues"],
                    "size_kb": repo_data["size"],
                    "languages": languages,
                    "top_contributors": top_contributors,
                    "created": repo_data["created_at"],
                    "last_updated": repo_data["updated_at"]
                }
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== HELPER METHODS ==========
    
    def _disabled_response(self) -> Dict[str, Any]:
        """Return response when GitHub integration is disabled."""
        return {
            "success": False,
            "error": "GitHub integration not configured",
            "message": "Add GitHub integration in Settings → Integrations to enable GitHub features"
        }
    
    def parse_repo_url(self, url_or_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse GitHub repository from URL or owner/repo format.
        
        Examples:
            - "https://github.com/owner/repo" -> ("owner", "repo")
            - "owner/repo" -> ("owner", "repo")
            - "repo" -> (None, "repo")
        """
        # Remove trailing .git if present
        url_or_name = url_or_name.rstrip("/").replace(".git", "")
        
        # Handle full GitHub URL
        if "github.com" in url_or_name:
            parts = url_or_name.split("github.com/")[-1].split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
        
        # Handle owner/repo format
        if "/" in url_or_name:
            parts = url_or_name.split("/")
            if len(parts) == 2:
                return parts[0], parts[1]
        
        # Just repo name
        return None, url_or_name


# Global instance
github_integration = GitHubIntegrationService()

