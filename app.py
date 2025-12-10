"""DevOps Command Center - Main Flet Application."""

import flet as ft
from frontend.pages.login_page import LoginPage
from frontend.pages.dashboard_page import DashboardPage
from frontend.pages.tasks_page import TasksPage
from frontend.pages.settings_page import SettingsPage
from frontend.pages.mcp_page import MCPAIPage
from frontend.state import AppState
from backend.database import init_db

# Local development config
try:
    from config_local import SKIP_LOGIN, DEMO_USER
except ImportError:
    SKIP_LOGIN = False
    DEMO_USER = None


def main(page: ft.Page):
    """Main application entry point."""
    
    # Initialize database
    init_db()
    
    # Page configuration
    page.title = "DevOps Command Center"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1280
    page.window.height = 800
    page.window.min_width = 800
    page.window.min_height = 600
    
    # Initialize app state
    app_state = AppState(page)
    
    # Auto-login for local development
    if SKIP_LOGIN and not app_state.is_authenticated():
        print("🔓 DEV MODE: Auto-login enabled (skipping authentication)")
        # Create or get demo user
        from backend.auth import register_user, create_access_token
        from backend.models import User
        from backend.database import get_db
        
        # Get or create demo user and extract data within the session
        demo_user_dict = None
        demo_user_id = None
        
        with get_db() as db:
            demo_user = db.query(User).filter(User.email == DEMO_USER["email"]).first()
            if not demo_user:
                # Create demo user
                success, demo_user, msg = register_user(
                    email=DEMO_USER["email"],
                    password="demo",
                    full_name=DEMO_USER["full_name"]
                )
                if success:
                    print(f"✅ Created demo user: {DEMO_USER['email']}")
                    # Refresh to get the user from database
                    with get_db() as db2:
                        demo_user = db2.query(User).filter(User.email == DEMO_USER["email"]).first()
                        if demo_user:
                            demo_user_id = demo_user.id
                            demo_user_dict = demo_user.to_dict()
                else:
                    print(f"❌ Failed to create demo user: {msg}")
            else:
                # Extract data while still in session
                demo_user_id = demo_user.id
                demo_user_dict = demo_user.to_dict()
        
        # Now use the extracted data outside the session
        if demo_user_id and demo_user_dict:
            token = create_access_token(demo_user_id)
            app_state.set_auth(token, demo_user_dict)
            print(f"✅ Auto-logged in as: {demo_user_dict['email']}")
    
    # Navigation handler
    def route_change(e):
        """Handle route changes."""
        page.views.clear()
        
        route = page.route
        
        # Login page (no auth required)
        if route == "/login" or not app_state.is_authenticated():
            if SKIP_LOGIN:
                # Skip login, go straight to dashboard
                page.go("/")
                return
            page.views.append(LoginPage(page, app_state))
        
        # Protected routes
        elif app_state.is_authenticated():
            if route == "/":
                page.views.append(DashboardPage(page, app_state))
            elif route == "/tasks":
                page.views.append(TasksPage(page, app_state))
            elif route == "/mcp":
                page.views.append(MCPAIPage(page, app_state))
            elif route == "/settings":
                page.views.append(SettingsPage(page, app_state))
            else:
                page.views.append(DashboardPage(page, app_state))
        
        # Redirect to login if not authenticated
        else:
            page.go("/login")
        
        page.update()
    
    page.on_route_change = route_change
    
    # Start at dashboard if authenticated (or skip login), otherwise login
    if app_state.is_authenticated() or SKIP_LOGIN:
        page.go("/")
    else:
        page.go("/login")


if __name__ == "__main__":
    ft.app(target=main)

