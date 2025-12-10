"""ArgoCD integration."""

from typing import Dict, Any, Tuple, List
import requests


def test_argocd_connection(config: Dict[str, Any], credentials: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Test ArgoCD connection.
    
    Returns:
        (success, message)
    """
    try:
        server_url = config.get('server_url')
        auth_token = credentials.get('auth_token')
        tls_verify = config.get('tls_verify', True)
        
        if not server_url:
            return False, "Missing server_url in config"
        
        if not auth_token:
            return False, "Missing auth_token in credentials"
        
        # Clean up URL
        server_url = server_url.rstrip('/')
        
        # Test connection
        response = requests.get(
            f"{server_url}/api/v1/applications",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10,
            verify=tls_verify
        )
        
        if response.status_code == 200:
            apps = response.json()
            app_count = len(apps.get('items', []))
            return True, f"Connected successfully. Found {app_count} applications."
        elif response.status_code == 401:
            return False, "Authentication failed. Check your token."
        else:
            return False, f"Connection failed with status {response.status_code}"
    
    except requests.exceptions.Timeout:
        return False, "Connection timeout. Check server URL."
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach server. Check server URL and network."
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_argocd_applications(config: Dict[str, Any], credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get ArgoCD applications.
    
    Returns:
        List of application dictionaries
    """
    try:
        server_url = config.get('server_url', '').rstrip('/')
        auth_token = credentials.get('auth_token')
        tls_verify = config.get('tls_verify', True)
        
        response = requests.get(
            f"{server_url}/api/v1/applications",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10,
            verify=tls_verify
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            # Simplify the response
            apps = []
            for item in items:
                metadata = item.get('metadata', {})
                status = item.get('status', {})
                spec = item.get('spec', {})
                
                apps.append({
                    'name': metadata.get('name', 'Unknown'),
                    'namespace': metadata.get('namespace', 'default'),
                    'health': status.get('health', {}).get('status', 'Unknown'),
                    'sync': status.get('sync', {}).get('status', 'Unknown'),
                    'project': spec.get('project', 'default'),
                    'server': spec.get('destination', {}).get('server', ''),
                    'repo': spec.get('source', {}).get('repoURL', ''),
                })
            
            return apps
        else:
            print(f"Error getting applications: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"Error getting ArgoCD applications: {e}")
        return []


def get_application_status(
    config: Dict[str, Any],
    credentials: Dict[str, Any],
    app_name: str
) -> Dict[str, Any]:
    """
    Get detailed status for a specific application.
    
    Returns:
        Application status dictionary
    """
    try:
        server_url = config.get('server_url', '').rstrip('/')
        auth_token = credentials.get('auth_token')
        tls_verify = config.get('tls_verify', True)
        
        response = requests.get(
            f"{server_url}/api/v1/applications/{app_name}",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10,
            verify=tls_verify
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    
    except Exception as e:
        print(f"Error getting application status: {e}")
        return {}

