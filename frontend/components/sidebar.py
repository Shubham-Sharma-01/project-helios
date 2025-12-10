"""Sidebar navigation component."""

import flet as ft


class Sidebar(ft.Container):
    """Sidebar navigation."""
    
    def __init__(self, page: ft.Page, app_state, selected: str = "dashboard"):
        self.page = page
        self.app_state = app_state
        
        def nav_button(icon, text, route, is_selected):
            """Create a navigation button."""
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(icon, color=ft.colors.WHITE if is_selected else ft.colors.GREY_400),
                        ft.Text(
                            text,
                            color=ft.colors.WHITE if is_selected else ft.colors.GREY_400,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL
                        )
                    ],
                    spacing=15
                ),
                padding=15,
                bgcolor=ft.colors.BLUE_700 if is_selected else None,
                border_radius=10,
                on_click=lambda _: page.go(route),
                ink=True
            )
        
        super().__init__(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text(
                            "🚀 DevOps CC",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=20
                    ),
                    ft.Divider(height=1),
                    ft.Container(height=10),
                    nav_button(ft.icons.DASHBOARD, "Dashboard", "/", selected == "dashboard"),
                    nav_button(ft.icons.CHECK_CIRCLE_OUTLINE, "My Tasks", "/tasks", selected == "tasks"),
                    nav_button(ft.icons.WB_SUNNY, "Helios AI", "/mcp", selected == "mcp"),
                    nav_button(ft.icons.SETTINGS, "Settings", "/settings", selected == "settings"),
                    ft.Container(expand=True),
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.PERSON, size=20),
                                ft.Column(
                                    [
                                        ft.Text(
                                            app_state.get_username(),
                                            size=14,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.TextButton(
                                            "Sign Out",
                                            on_click=lambda _: self.handle_logout()
                                        )
                                    ],
                                    spacing=0
                                )
                            ],
                            spacing=10
                        ),
                        padding=15
                    )
                ],
                spacing=5
            ),
            width=250,
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=10
        )
    
    def handle_logout(self):
        """Handle user logout."""
        self.app_state.clear_auth()
        self.page.go("/login")

