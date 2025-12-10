"""Login page."""

import flet as ft
from backend.auth import register_user, authenticate_user, create_access_token


class LoginPage(ft.View):
    """Login and registration page."""
    
    def __init__(self, page: ft.Page, app_state):
        self.page = page
        self.app_state = app_state
        
        # Input fields
        self.email_field = ft.TextField(
            label="Email",
            hint_text="your@email.com",
            autofocus=True,
            width=400
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=400
        )
        
        self.name_field = ft.TextField(
            label="Full Name (optional)",
            width=400,
            visible=False
        )
        
        self.error_text = ft.Text("", color=ft.colors.RED, size=14)
        self.success_text = ft.Text("", color=ft.colors.GREEN, size=14)
        
        # Mode toggle
        self.is_login_mode = True
        self.mode_text = ft.Text("Don't have an account?")
        self.mode_button = ft.TextButton(
            "Sign up",
            on_click=self.toggle_mode
        )
        
        # Submit button
        self.submit_button = ft.ElevatedButton(
            "Sign In",
            on_click=self.handle_submit,
            width=400
        )
        
        super().__init__(
            route="/login",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=50),
                            ft.Text(
                                "🚀 DevOps Command Center",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                "AI-Powered Productivity Platform",
                                size=16,
                                color=ft.colors.GREY_400,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Container(height=30),
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Sign In",
                                                size=24,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            ft.Container(height=10),
                                            self.email_field,
                                            self.password_field,
                                            self.name_field,
                                            ft.Container(height=10),
                                            self.error_text,
                                            self.success_text,
                                            ft.Container(height=10),
                                            self.submit_button,
                                            ft.Container(height=20),
                                            ft.Row(
                                                [
                                                    self.mode_text,
                                                    self.mode_button
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER
                                            )
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=10
                                    ),
                                    padding=40
                                ),
                                width=500
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    expand=True,
                    alignment=ft.alignment.center
                )
            ]
        )
    
    def toggle_mode(self, e):
        """Toggle between login and signup mode."""
        self.is_login_mode = not self.is_login_mode
        
        if self.is_login_mode:
            self.submit_button.text = "Sign In"
            self.mode_text.value = "Don't have an account?"
            self.mode_button.text = "Sign up"
            self.name_field.visible = False
        else:
            self.submit_button.text = "Sign Up"
            self.mode_text.value = "Already have an account?"
            self.mode_button.text = "Sign in"
            self.name_field.visible = True
        
        self.error_text.value = ""
        self.success_text.value = ""
        self.page.update()
    
    def handle_submit(self, e):
        """Handle login/signup submission."""
        email = self.email_field.value
        password = self.password_field.value
        
        # Clear previous messages
        self.error_text.value = ""
        self.success_text.value = ""
        
        # Validation
        if not email or not password:
            self.error_text.value = "⚠️ Email and password are required"
            self.page.update()
            return
        
        try:
            if self.is_login_mode:
                # Login
                print(f"Attempting login for: {email}")
                success, user, message = authenticate_user(email, password)
                print(f"Login result: success={success}, message={message}")
                
                if success:
                    print(f"Login successful! Creating token...")
                    token = create_access_token(user.id)
                    self.app_state.set_auth(token, user.to_dict())
                    print(f"Navigating to dashboard...")
                    self.page.go("/")
                else:
                    self.error_text.value = f"❌ {message}"
                    print(f"Login failed: {message}")
            else:
                # Register
                name = self.name_field.value
                print(f"Attempting registration for: {email}")
                success, user, message = register_user(email, password, name)
                print(f"Registration result: success={success}, message={message}")
                
                if success:
                    self.success_text.value = "✅ Account created! Please sign in."
                    self.error_text.value = ""
                    # Switch to login mode
                    self.is_login_mode = True
                    self.toggle_mode(None)
                else:
                    self.error_text.value = f"❌ {message}"
        
        except Exception as ex:
            print(f"Exception during submit: {ex}")
            import traceback
            traceback.print_exc()
            self.error_text.value = f"❌ Error: {str(ex)}"
        
        self.page.update()

