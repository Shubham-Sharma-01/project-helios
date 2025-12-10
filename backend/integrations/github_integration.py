"""
GitHub Integration Tests and Utilities.

Tests GitHub connection and validates credentials.
"""
from typing import Dict, Any, Tuple
import requests


def test_github_connection(config: Dict[str, Any], credentials: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Test GitHub connection by validating token and fetching user info.
    
    Args:
        config: Integration configuration (organization/username, etc.)
        credentials: Decrypted credentials (access_token)
    
    Returns:
        (success, message)
    """
    # Validate credentials
    token = credentials.get('access_token') or credentials.get('token')
    
    if not token:
        return False, "❌ GitHub token is required"
    
    # Test API connection
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Test 1: Get authenticated user info
        response = requests.get(
            "https://api.github.com/user",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 401:
            return False, "❌ Invalid GitHub token - authentication failed"
        
        if response.status_code == 403:
            error_msg = response.json().get('message', '')
            if 'rate limit' in error_msg.lower():
                return False, "❌ GitHub API rate limit exceeded - wait a moment and try again"
            return False, f"❌ Access denied: {error_msg}"
        
        if response.status_code != 200:
            return False, f"❌ GitHub API error: {response.status_code}"
        
        user_data = response.json()
        username = user_data.get('login')
        name = user_data.get('name', username)
        
        # Test 2: Check token scopes/permissions
        scopes = response.headers.get('X-OAuth-Scopes', '').split(', ')
        
        # Verify we have minimum required permissions
        if not any(scope in scopes for scope in ['repo', 'public_repo']):
            return False, "⚠️ Token lacks required permissions. Please add 'repo' scope."
        
        # Build success message with user info
        success_msg = f"✅ Connected to GitHub as {name} (@{username})\n"
        success_msg += f"🔑 Token has {len([s for s in scopes if s])} permission scopes"
        
        # Add organization info if configured
        org = config.get('organization')
        if org:
            # Verify org access
            org_response = requests.get(
                f"https://api.github.com/orgs/{org}",
                headers=headers,
                timeout=10
            )
            
            if org_response.status_code == 200:
                success_msg += f"\n🏢 Organization '{org}' accessible"
            elif org_response.status_code == 404:
                success_msg += f"\n⚠️ Organization '{org}' not found (but personal repos work)"
            else:
                success_msg += f"\n⚠️ Cannot access organization '{org}'"
        
        # Test 3: Try to list repositories (quick test)
        repos_response = requests.get(
            "https://api.github.com/user/repos",
            headers=headers,
            params={"per_page": 1},
            timeout=10
        )
        
        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            if repos_data:
                success_msg += f"\n📚 Can access repositories"
        
        return True, success_msg
    
    except requests.exceptions.Timeout:
        return False, "❌ Connection timeout - GitHub API not responding"
    
    except requests.exceptions.ConnectionError:
        return False, "❌ Network error - cannot reach GitHub API"
    
    except Exception as e:
        return False, f"❌ Connection test failed: {str(e)}"


def fetch_github_repositories(config: Dict[str, Any], credentials: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Fetch repositories from GitHub.
    
    Args:
        config: Integration configuration
        credentials: Decrypted credentials
    
    Returns:
        (success, data)
    """
    token = credentials.get('access_token') or credentials.get('token')
    
    if not token:
        return False, "GitHub token not found"
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # If organization is specified, get org repos
        org = config.get('organization')
        if org:
            url = f"https://api.github.com/orgs/{org}/repos"
        else:
            url = "https://api.github.com/user/repos"
        
        response = requests.get(
            url,
            headers=headers,
            params={"per_page": 50, "sort": "updated"},
            timeout=15
        )
        
        if response.status_code != 200:
            return False, f"GitHub API error: {response.status_code}"
        
        repos = response.json()
        
        return True, repos
    
    except Exception as e:
        return False, str(e)

