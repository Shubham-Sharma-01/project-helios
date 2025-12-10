"""Jira integration."""

from typing import Dict, Any, Tuple, List
import requests
from requests.auth import HTTPBasicAuth
import base64


def test_jira_connection(config: Dict[str, Any], credentials: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Test Jira connection.
    Supports both Jira Cloud (email + api_token) and Jira Server (username + password).
    
    Returns:
        (success, message)
    """
    try:
        server_url = config.get('server_url')
        
        # Support both Jira Cloud and Jira Server authentication
        username = credentials.get('username') or credentials.get('email')
        password = credentials.get('password') or credentials.get('api_token')
        
        if not server_url:
            return False, "Missing server_url in config"
        
        if not username:
            return False, "Missing username/email in credentials"
        
        if not password:
            return False, "Missing password/api_token in credentials"
        
        # Clean up URL
        server_url = server_url.rstrip('/')
        
        # Detect API version (try v2 first for Jira Server, then v3 for Cloud)
        api_version = config.get('api_version', '2')  # Default to v2 for Jira Server
        
        # Test connection by getting current user info
        response = requests.get(
            f"{server_url}/rest/api/{api_version}/myself",
            auth=HTTPBasicAuth(username, password),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get('displayName', 'Unknown')
            return True, f"Connected successfully as {username}."
        elif response.status_code == 401:
            return False, "Authentication failed. Check your email and API token."
        elif response.status_code == 403:
            return False, "Access denied. Check your permissions."
        else:
            return False, f"Connection failed with status {response.status_code}"
    
    except requests.exceptions.Timeout:
        return False, "Connection timeout. Check server URL."
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach server. Check server URL and network."
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_jira_issues(
    config: Dict[str, Any],
    credentials: Dict[str, Any],
    jql: str = "assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC",
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    Get Jira issues using JQL query.
    
    Args:
        config: Jira configuration
        credentials: Jira credentials
        jql: JQL query string
        max_results: Maximum number of results to return
    
    Returns:
        List of issue dictionaries
    """
    try:
        server_url = config.get('server_url', '').rstrip('/')
        username = credentials.get('username') or credentials.get('email')
        password = credentials.get('password') or credentials.get('api_token')
        api_version = config.get('api_version', '2')
        
        response = requests.get(
            f"{server_url}/rest/api/{api_version}/search",
            auth=HTTPBasicAuth(username, password),
            headers={"Accept": "application/json"},
            params={
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,priority,assignee,created,updated,issuetype"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            issues_data = data.get('issues', [])
            
            # Simplify the response
            issues = []
            for issue_data in issues_data:
                fields = issue_data.get('fields', {})
                
                # Extract assignee info
                assignee = fields.get('assignee', {})
                assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
                
                # Extract status
                status = fields.get('status', {})
                status_name = status.get('name', 'Unknown')
                
                # Extract priority
                priority = fields.get('priority', {})
                priority_name = priority.get('name', 'None')
                
                # Extract issue type
                issue_type = fields.get('issuetype', {})
                issue_type_name = issue_type.get('name', 'Unknown')
                
                issues.append({
                    'key': issue_data.get('key', 'Unknown'),
                    'summary': fields.get('summary', 'No summary'),
                    'status': status_name,
                    'priority': priority_name,
                    'assignee': assignee_name,
                    'type': issue_type_name,
                    'created': fields.get('created', ''),
                    'updated': fields.get('updated', ''),
                    'url': f"{server_url}/browse/{issue_data.get('key', '')}"
                })
            
            return issues
        else:
            print(f"Error getting issues: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"Error getting Jira issues: {e}")
        return []


def get_assigned_issues(config: Dict[str, Any], credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get issues assigned to current user.
    
    Returns:
        List of issue dictionaries
    """
    jql = "assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC, updated DESC"
    return get_jira_issues(config, credentials, jql=jql)


def get_issue_details(
    config: Dict[str, Any],
    credentials: Dict[str, Any],
    issue_key: str
) -> Dict[str, Any]:
    """
    Get detailed information for a specific issue.
    
    Returns:
        Issue details dictionary
    """
    try:
        server_url = config.get('server_url', '').rstrip('/')
        username = credentials.get('username') or credentials.get('email')
        password = credentials.get('password') or credentials.get('api_token')
        api_version = config.get('api_version', '2')
        
        response = requests.get(
            f"{server_url}/rest/api/{api_version}/issue/{issue_key}",
            auth=HTTPBasicAuth(username, password),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    
    except Exception as e:
        print(f"Error getting issue details: {e}")
        return {}


def create_jira_issue(
    config: Dict[str, Any],
    credentials: Dict[str, Any],
    project_key: str,
    summary: str,
    description: str = None,
    issue_type: str = "Task",
    priority: str = "Medium"
) -> Tuple[bool, str]:
    """
    Create a new Jira issue.
    
    Returns:
        (success, message_or_issue_key)
    """
    try:
        server_url = config.get('server_url', '').rstrip('/')
        username = credentials.get('username') or credentials.get('email')
        password = credentials.get('password') or credentials.get('api_token')
        api_version = config.get('api_version', '2')
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }
        }
        
        # Use different description format for API v2 vs v3
        if description:
            if api_version == '2':
                # Jira Server (API v2) uses plain text
                payload["fields"]["description"] = description
            else:
                # Jira Cloud (API v3) uses Atlassian Document Format
                payload["fields"]["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                }
        
        if priority:
            payload["fields"]["priority"] = {"name": priority}
        
        response = requests.post(
            f"{server_url}/rest/api/{api_version}/issue",
            auth=HTTPBasicAuth(username, password),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            issue_key = data.get('key', 'Unknown')
            return True, issue_key
        else:
            error_msg = response.json().get('errorMessages', ['Unknown error'])
            return False, f"Failed to create issue: {error_msg}"
    
    except Exception as e:
        return False, f"Error creating issue: {str(e)}"

