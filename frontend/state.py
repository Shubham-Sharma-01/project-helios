"""Application state management."""

import flet as ft
from typing import Optional, Dict, Any


class AppState:
    """Global application state."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.token: Optional[str] = None
        self.user: Optional[Dict[str, Any]] = None
        self._load_from_storage()
    
    def _load_from_storage(self):
        """Load auth data from client storage."""
        try:
            self.token = self.page.client_storage.get("auth_token")
            user_data = self.page.client_storage.get("user")
            if user_data:
                import json
                self.user = json.loads(user_data)
        except Exception as e:
            print(f"Error loading from storage: {e}")
            self.token = None
            self.user = None
    
    def set_auth(self, token: str, user: Dict[str, Any]):
        """Set authentication data."""
        import json
        self.token = token
        self.user = user
        
        # Save to client storage
        try:
            self.page.client_storage.set("auth_token", token)
            self.page.client_storage.set("user", json.dumps(user))
        except Exception as e:
            print(f"Error saving to storage: {e}")
    
    def clear_auth(self):
        """Clear authentication data."""
        self.token = None
        self.user = None
        
        try:
            self.page.client_storage.remove("auth_token")
            self.page.client_storage.remove("user")
        except Exception as e:
            print(f"Error clearing storage: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.token is not None and self.user is not None
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID."""
        return self.user.get("id") if self.user else None
    
    def get_username(self) -> str:
        """Get current username."""
        if self.user:
            return self.user.get("full_name") or self.user.get("email", "User")
        return "User"

