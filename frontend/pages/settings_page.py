"""Settings page for managing integrations."""

import flet as ft
import json
from backend.services.integration_service import IntegrationService
from backend.services.notification_service import NotificationService
from frontend.components.sidebar import Sidebar
from frontend.components.topbar import Topbar


class SettingsPage(ft.View):
    """Settings page."""
    
    def __init__(self, page: ft.Page, app_state):
        self.page = page
        self.app_state = app_state
        
        # Get integrations
        self.integrations = IntegrationService.get_user_integrations(app_state.get_user_id())
        
        # Get notifications
        unread_count = NotificationService.get_unread_count(app_state.get_user_id())
        
        # Integration list container
        self.integration_list = ft.Column(spacing=15)
        self.render_integrations()
        
        # Main content
        content = ft.Container(
            content=ft.Column(
                [
                    Topbar(page, app_state, "Settings", unread_count),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Integrations", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Container(expand=True),
                                        ft.ElevatedButton(
                                            "➕ Add Integration",
                                            on_click=lambda _: self.show_add_integration_dialog()
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Container(height=20),
                                self.integration_list if self.integrations else ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Icon(ft.icons.EXTENSION, size=64, color=ft.colors.GREY_400),
                                            ft.Text("No integrations yet", size=20, color=ft.colors.GREY_400),
                                            ft.Text("Add your first integration to get started!", size=14, color=ft.colors.GREY_400)
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=10
                                    ),
                                    padding=60,
                                    alignment=ft.alignment.center
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=10
                        ),
                        padding=20,
                        expand=True
                    )
                ],
                spacing=0
            ),
            expand=True
        )
        
        super().__init__(
            route="/settings",
            controls=[
                ft.Row(
                    [
                        Sidebar(page, app_state, selected="settings"),
                        content
                    ],
                    spacing=0,
                    expand=True
                )
            ],
            padding=0
        )
    
    def render_integrations(self):
        """Render integration list."""
        self.integration_list.controls.clear()
        
        for integration in self.integrations:
            self.integration_list.controls.append(self.create_integration_card(integration))
    
    def create_integration_card(self, integration):
        """Create an integration card."""
        # integration is already a dict now
        integration_dict = integration
        
        status_colors = {
            'active': ft.colors.GREEN_400,
            'pending': ft.colors.ORANGE_400,
            'error': ft.colors.RED_400,
            'disabled': ft.colors.GREY_400
        }
        
        type_icons = {
            'slack': "📢 Slack",
            'argocd': "🔷 ArgoCD",
            'github': "🐙 GitHub",
            'jira': "📝 Jira"
        }
        
        status_indicator = ft.Row(
            [
                ft.Icon(
                    ft.icons.CIRCLE,
                    size=12,
                    color=status_colors.get(integration_dict['status'], ft.colors.GREY)
                ),
                ft.Text(integration_dict['status'].title(), size=12)
            ],
            spacing=5
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    type_icons.get(integration_dict['type'], integration_dict['type'].title()),
                                    size=18,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(integration_dict['name'], size=16, weight=ft.FontWeight.W_500),
                                ft.Text(
                                    integration_dict['description'] or "No description",
                                    size=13,
                                    color=ft.colors.GREY_400
                                ),
                                status_indicator
                            ],
                            spacing=5,
                            expand=True
                        ),
                        ft.Column(
                            [
                                ft.ElevatedButton(
                                    "Test Connection",
                                    on_click=lambda _, iid=integration_dict['id']: self.test_connection(iid)
                                ),
                                ft.OutlinedButton(
                                    "Edit",
                                    on_click=lambda _, iid=integration_dict['id']: self.edit_integration(iid)
                                ),
                                ft.OutlinedButton(
                                    "Delete",
                                    on_click=lambda _, iid=integration_dict['id']: self.delete_integration(iid)
                                )
                            ],
                            spacing=10
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=20
            )
        )
    
    def show_add_integration_dialog(self):
        """Show dialog to add new integration."""
        type_dropdown = ft.Dropdown(
            label="Integration Type *",
            options=[
                ft.dropdown.Option("slack", "📢 Slack"),
                ft.dropdown.Option("argocd", "🔷 ArgoCD"),
                ft.dropdown.Option("github", "🐙 GitHub"),
                ft.dropdown.Option("jira", "📝 Jira")
            ],
            width=500,
            on_change=lambda _: self.update_integration_fields()
        )
        
        name_field = ft.TextField(label="Name *", hint_text="e.g., Production ArgoCD", width=500)
        description_field = ft.TextField(label="Description", width=500)
        
        # Type-specific fields container
        specific_fields = ft.Column(spacing=10, width=500)
        
        self.dialog_fields = {
            'type': type_dropdown,
            'name': name_field,
            'description': description_field,
            'specific': specific_fields
        }
        
        def save_integration(e):
            print("💾 Save & Test button clicked")
            
            # Validation
            if not type_dropdown.value:
                print("❌ Integration type not selected")
                self.show_snackbar("⚠️ Please select an integration type", error=True)
                return
            
            if not name_field.value:
                print("❌ Name field is empty")
                self.show_snackbar("⚠️ Please enter a name", error=True)
                return
            
            print(f"✅ Type: {type_dropdown.value}, Name: {name_field.value}")
            
            try:
                # Collect config and credentials based on type
                config = {}
                credentials = {}
                
                print(f"📝 Processing {len(specific_fields.controls)} fields...")
                
                for control in specific_fields.controls:
                    # Skip if not a text field or if data is not set
                    if not hasattr(control, 'data') or control.data is None:
                        print(f"  ⏭️  Skipping control without data: {type(control).__name__}")
                        continue
                    
                    if not hasattr(control, 'value'):
                        print(f"  ⏭️  Skipping control without value: {type(control).__name__}")
                        continue
                    
                    try:
                        field_type, field_name = control.data
                        value = control.value
                        
                        # Skip empty values (but not False for booleans)
                        if value is None or (value == "" and not isinstance(value, bool)):
                            print(f"  ⏭️  Skipping empty field: {field_type}.{field_name}")
                            continue
                        
                        print(f"  - {field_type}.{field_name} = {value if field_type != 'credential' else '***'}")
                        
                        if field_type == 'config':
                            config[field_name] = value
                        elif field_type == 'credential':
                            credentials[field_name] = value
                    except Exception as field_error:
                        print(f"  ❌ Error processing field: {field_error}")
                        continue
                
                # Validate required fields for ArgoCD
                if type_dropdown.value == 'argocd':
                    if not config.get('server_url'):
                        self.show_snackbar("⚠️ Server URL is required", error=True)
                        return
                    if not credentials.get('auth_token'):
                        self.show_snackbar("⚠️ API Token is required", error=True)
                        return
                
                print(f"🚀 Creating integration...")
                
                # Create integration - returns integration_id (not the object)
                integration_id = IntegrationService.create_integration(
                    user_id=self.app_state.get_user_id(),
                    type=type_dropdown.value,
                    name=name_field.value,
                    description=description_field.value,
                    config=config,
                    credentials=credentials
                )
                
                print(f"✅ Integration created: {integration_id}")
                
                # Test connection
                print("🔌 Testing connection...")
                success, message = IntegrationService.test_connection(integration_id)
                
                if success:
                    print(f"✅ Connection test successful: {message}")
                    IntegrationService.update_integration(integration_id, status="active", error_message=None)
                    self.show_snackbar(f"✅ {message}")
                else:
                    print(f"❌ Connection test failed: {message}")
                    IntegrationService.update_integration(integration_id, status="error", error_message=message)
                    self.show_snackbar(f"⚠️ Integration created but test failed: {message}", error=True)
                
                # Close dialog and refresh
                self.page.dialog.open = False
                self.refresh_integrations()
                self.page.update()
                
            except Exception as ex:
                print(f"❌ Error saving integration: {ex}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"❌ Error: {str(ex)}", error=True)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Add Integration"),
            content=ft.Container(
                content=ft.Column(
                    [
                        type_dropdown,
                        name_field,
                        description_field,
                        ft.Divider(),
                        specific_fields
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=600,
                height=500
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Save & Test", on_click=save_integration)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def update_integration_fields(self):
        """Update form fields based on selected integration type."""
        integration_type = self.dialog_fields['type'].value
        specific_fields = self.dialog_fields['specific']
        specific_fields.controls.clear()
        
        if integration_type == 'slack':
            specific_fields.controls.extend([
                ft.Text("Slack Configuration", weight=ft.FontWeight.BOLD),
                self.create_field('config', 'workspace_id', 'Workspace ID', hint="Your Slack workspace ID"),
                ft.Text("Credentials", weight=ft.FontWeight.BOLD),
                self.create_field('credential', 'bot_token', 'Bot Token *', password=True, hint="xoxb-..."),
                self.create_field('credential', 'app_token', 'App Token', password=True, hint="xapp-..."),
            ])
        elif integration_type == 'argocd':
            # Create TLS Verify checkbox
            tls_verify_checkbox = ft.Checkbox(
                label="Verify TLS/SSL certificates",
                value=True,  # Default to True for security
                tooltip="Uncheck for self-signed certificates or localhost"
            )
            tls_verify_checkbox.data = ('config', 'tls_verify')  # Store field info
            
            specific_fields.controls.extend([
                ft.Text("ArgoCD Configuration", weight=ft.FontWeight.BOLD),
                self.create_field('config', 'server_url', 'Server URL *', hint="https://argocd.example.com or https://localhost:8080"),
                self.create_field('config', 'namespace', 'Namespace', hint="argocd", value="argocd"),
                tls_verify_checkbox,
                ft.Text("Credentials", weight=ft.FontWeight.BOLD),
                self.create_field('credential', 'auth_token', 'API Token *', password=True),
            ])
        elif integration_type == 'github':
            specific_fields.controls.extend([
                ft.Text("GitHub Configuration", weight=ft.FontWeight.BOLD),
                self.create_field('config', 'organization', 'Organization/Username'),
                ft.Text("Credentials", weight=ft.FontWeight.BOLD),
                self.create_field('credential', 'access_token', 'Personal Access Token *', password=True),
            ])
        elif integration_type == 'jira':
            specific_fields.controls.extend([
                ft.Text("Jira Configuration", weight=ft.FontWeight.BOLD),
                self.create_field('config', 'server_url', 'Server URL *', hint="https://jira.company.com"),
                self.create_field('config', 'api_version', 'API Version', hint="2 for Jira Server, 3 for Jira Cloud", value="2"),
                ft.Text("Credentials", weight=ft.FontWeight.BOLD),
                ft.Text("Jira Server: username + password | Jira Cloud: email + API token", size=11, italic=True),
                self.create_field('credential', 'username', 'Username/Email *', hint="username or email@company.com"),
                self.create_field('credential', 'password', 'Password/API Token *', password=True),
            ])
        
        self.page.update()
    
    def create_field(self, field_type: str, field_name: str, label: str, password: bool = False, hint: str = None, value: str = None):
        """Create a form field with metadata."""
        field = ft.TextField(
            label=label,
            password=password,
            can_reveal_password=password,
            hint_text=hint,
            value=value,
            width=500
        )
        field.data = (field_type, field_name)
        return field
    
    def test_connection(self, integration_id: str):
        """Test integration connection."""
        success, message = IntegrationService.test_connection(integration_id)
        
        if success:
            IntegrationService.update_integration(integration_id, status="active", error_message=None)
            self.show_snackbar(f"✅ {message}")
        else:
            IntegrationService.update_integration(integration_id, status="error", error_message=message)
            self.show_snackbar(f"❌ {message}", error=True)
        
        self.refresh_integrations()
    
    def edit_integration(self, integration_id: str):
        """Edit integration with full fields."""
        integration = IntegrationService.get_integration(integration_id)
        if not integration:
            return
        
        integration_dict = integration
        integration_type = integration_dict['type']
        
        # Get existing credentials
        existing_credentials = IntegrationService.get_integration_credentials(integration_id)
        
        name_field = ft.TextField(label="Name", value=integration_dict['name'], width=500)
        description_field = ft.TextField(label="Description", value=integration_dict['description'] or "", width=500)
        
        # Type-specific fields container
        specific_fields = ft.Column(spacing=10, width=500)
        
        # Populate fields based on integration type
        config = integration_dict.get('config', {})
        
        if integration_type == 'jira':
            specific_fields.controls.extend([
                ft.Text("Jira Configuration", weight=ft.FontWeight.BOLD),
                self.create_field('config', 'server_url', 'Server URL *', hint="https://jira.company.com", value=config.get('server_url', '')),
                self.create_field('config', 'api_version', 'API Version', hint="2 for Server, 3 for Cloud", value=config.get('api_version', '2')),
                ft.Text("Credentials", weight=ft.FontWeight.BOLD),
                ft.Text("Jira Server: username + password | Jira Cloud: email + API token", size=11, italic=True),
                self.create_field('credential', 'username', 'Username/Email *', hint="username or email", value=existing_credentials.get('username', '') if existing_credentials else ''),
                self.create_field('credential', 'password', 'Password/API Token *', password=True, hint="Leave empty to keep existing"),
            ])
        elif integration_type == 'argocd':
            tls_verify_checkbox = ft.Checkbox(
                label="Verify TLS/SSL certificates",
                value=config.get('tls_verify', True),
                tooltip="Uncheck for self-signed certificates or localhost"
            )
            tls_verify_checkbox.data = ('config', 'tls_verify')
            
            specific_fields.controls.extend([
                ft.Text("ArgoCD Configuration", weight=ft.FontWeight.BOLD),
                self.create_field('config', 'server_url', 'Server URL *', hint="https://argocd.example.com", value=config.get('server_url', '')),
                self.create_field('config', 'namespace', 'Namespace', hint="argocd", value=config.get('namespace', 'argocd')),
                tls_verify_checkbox,
                ft.Text("Credentials", weight=ft.FontWeight.BOLD),
                self.create_field('credential', 'auth_token', 'API Token *', password=True, hint="Leave empty to keep existing"),
            ])
        elif integration_type == 'slack':
            specific_fields.controls.extend([
                ft.Text("Slack Configuration", weight=ft.FontWeight.BOLD),
                self.create_field('config', 'workspace_id', 'Workspace ID', hint="Your Slack workspace ID", value=config.get('workspace_id', '')),
                ft.Text("Credentials", weight=ft.FontWeight.BOLD),
                self.create_field('credential', 'bot_token', 'Bot Token *', password=True, hint="Leave empty to keep existing"),
                self.create_field('credential', 'app_token', 'App Token', password=True, hint="Leave empty to keep existing"),
            ])
        
        def save_changes(e):
            # Collect config and credentials
            config_data = {}
            credentials_data = {}
            
            for control in specific_fields.controls:
                if hasattr(control, 'data') and control.data is not None:
                    if not hasattr(control, 'value'):
                        continue
                    
                    field_type, field_name = control.data
                    value = control.value
                    
                    # Skip empty password fields (keep existing)
                    if field_type == 'credential' and (value is None or value == ""):
                        continue
                    
                    if field_type == 'config':
                        config_data[field_name] = value
                    elif field_type == 'credential':
                        credentials_data[field_name] = value
            
            # Update integration
            IntegrationService.update_integration(
                integration_id=integration_id,
                name=name_field.value,
                description=description_field.value,
                config=config_data if config_data else None,
                credentials=credentials_data if credentials_data else None
            )
            
            self.page.dialog.open = False
            self.refresh_integrations()
            self.show_snackbar("✅ Integration updated! Click 'Test Connection' to verify.")
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit {integration_type.upper()} Integration"),
            content=ft.Column([
                name_field,
                description_field,
                ft.Divider(),
                specific_fields
            ], tight=True, scroll=ft.ScrollMode.AUTO, height=500),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Save", on_click=save_changes)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_integration(self, integration_id: str):
        """Delete integration."""
        def confirm_delete(e):
            IntegrationService.delete_integration(integration_id)
            self.page.dialog.open = False
            self.refresh_integrations()
            self.show_snackbar("Integration deleted successfully!")
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Delete Integration"),
            content=ft.Text("Are you sure? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Delete", on_click=confirm_delete, bgcolor=ft.colors.RED)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def refresh_integrations(self):
        """Refresh integration list."""
        self.integrations = IntegrationService.get_user_integrations(self.app_state.get_user_id())
        self.render_integrations()
        self.page.update()
    
    def close_dialog(self):
        """Close the dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def show_snackbar(self, message: str, error: bool = False):
        """Show a snackbar message."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.RED if error else ft.colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()

