"""Helios AI Page - AI-powered DevOps assistant with MCP integration."""

import flet as ft
from backend.services.integration_service import IntegrationService
from backend.services.task_service import TaskService
from backend.services.ollama_chat_service_v2 import ollama_chat_v2
from backend.services.mcp_service import MCPService
from backend.models import MCPStatus
from frontend.components.sidebar import Sidebar
from frontend.components.topbar import Topbar
import asyncio


class MCPAIPage(ft.View):
    """Helios AI - Your intelligent DevOps assistant with natural language interface."""
    
    def __init__(self, page: ft.Page, app_state):
        self.page = page
        self.app_state = app_state
        self.integration_service = IntegrationService()
        self.ollama_chat = ollama_chat_v2  # Simple Ollama chat
        self.mcp_service = MCPService()
        
        # Chat history - persist in app_state
        if not hasattr(self.app_state, 'mcp_chat_messages'):
            self.app_state.mcp_chat_messages = []
        self.chat_messages = self.app_state.mcp_chat_messages
        
        self.chat_container = ft.ListView(
            spacing=10,
            padding=20,
            auto_scroll=True,
            expand=True
        )
        
        # Selected MCP server
        self.selected_mcp_server = None
        self.mcp_dropdown = None
        
        # Build the main content
        main_content = self.build_main_content()
        
        # Initialize the View with sidebar and content
        super().__init__(
            route="/mcp",
            controls=[
                ft.Row(
                    [
                        Sidebar(page, app_state, selected="mcp"),
                        ft.VerticalDivider(width=1),
                        ft.Column(
                            [
                                Topbar(page, "Helios AI Assistant", 0),
                                main_content
                            ],
                            expand=True,
                            spacing=0
                        )
                    ],
                    spacing=0,
                    expand=True
                )
            ]
        )
    
    def build_main_content(self):
        """Build the main content area."""
        user_id = self.app_state.user.get("id")
        
        # Get MCP servers
        mcp_servers = self.mcp_service.get_user_mcp_servers(user_id)
        active_mcps = [s for s in mcp_servers if s.get("status") == "active"]
        
        # Get integrations for context
        integrations = self.integration_service.get_user_integrations(user_id)
        active_integrations = [i for i in integrations if i.get("is_active", False)]
        
        # MCP server selector
        mcp_options = []
        for mcp in active_mcps:
            mcp_options.append(
                ft.dropdown.Option(
                    key=str(mcp["id"]),
                    text=f"{mcp['server_type'].upper()} - {mcp['name']}"
                )
            )
        
        self.mcp_dropdown = ft.Dropdown(
            label="Select MCP Server",
            options=mcp_options,
            width=300,
            on_change=self.on_mcp_selected
        )
        
        # Message input
        self.message_input = ft.TextField(
            hint_text="Ask AI about your DevOps environment or use MCP tools...",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            on_submit=self.send_message
        )
        
        send_button = ft.IconButton(
            icon=ft.icons.SEND,
            tooltip="Send message",
            on_click=self.send_message
        )
        
        # Quick actions
        quick_actions = ft.Row(
            [
                ft.ElevatedButton(
                    "📊 ArgoCD Status",
                    on_click=lambda _: self.quick_query("Show me the status of all ArgoCD applications"),
                    disabled=not any(i.get("integration_type") == "argocd" for i in active_integrations)
                ),
                ft.ElevatedButton(
                    "🎫 Jira Summary",
                    on_click=lambda _: self.quick_query("Summarize my Jira tickets and highlight what needs attention"),
                    disabled=not any(i.get("integration_type") == "jira" for i in active_integrations)
                ),
                ft.ElevatedButton(
                    "🔍 Smart Insights",
                    on_click=lambda _: self.quick_query("Analyze all my data and provide actionable insights"),
                ),
            ],
            wrap=True,
            spacing=10
        )
        
        # MCP Server management section
        mcp_servers_display = self.build_mcp_servers_section(mcp_servers)
        
        # Main content
        content = ft.Column(
            [
                # Header with tabs
                ft.Container(
                           content=ft.Row(
                               [
                                   ft.Icon(ft.icons.WB_SUNNY, size=32, color=ft.colors.ORANGE_400),
                                   ft.Text("Helios AI Assistant", size=24, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.OutlinedButton(
                                "🗑️ Clear Chat",
                                icon=ft.icons.DELETE_OUTLINE,
                                on_click=self.clear_chat_history,
                                tooltip="Clear conversation history"
                            ),
                            ft.ElevatedButton(
                                "➕ Add MCP Server",
                                icon=ft.icons.ADD,
                                on_click=self.show_add_mcp_dialog,
                                bgcolor=ft.colors.PURPLE_700
                            )
                        ]
                    ),
                    padding=20
                ),
                
                # Info card
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "🤖 AI-Powered DevOps Assistant with MCP Integration",
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Chat with AI about your DevOps environment, or connect MCP servers for advanced automation. "
                            "MCP (Model Context Protocol) enables AI to interact with your tools directly.",
                            size=12,
                            color=ft.colors.GREY_400
                        ),
                    ]),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.PURPLE_400),
                    border=ft.border.all(1, ft.colors.PURPLE_400),
                    border_radius=8,
                    padding=15,
                    margin=ft.margin.symmetric(horizontal=20)
                ),
                
                # MCP Servers Section
                mcp_servers_display,
                
                ft.Divider(height=1),
                
                # MCP server selector
                ft.Container(
                    content=ft.Row([
                        ft.Text("🔌 Active MCP:", size=14, weight=ft.FontWeight.BOLD),
                        self.mcp_dropdown if mcp_options else ft.Text(
                            "No active MCP servers. Add one above!",
                            color=ft.colors.ORANGE_400
                        )
                    ]),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10)
                ),
                
                # Quick actions
                ft.Container(
                    content=ft.Column([
                        ft.Text("⚡ Quick Actions:", size=14, weight=ft.FontWeight.BOLD),
                        quick_actions
                    ]),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10)
                ),
                
                ft.Divider(height=1),
                
                # Chat area
                ft.Container(
                    content=self.chat_container,
                    expand=True,
                    bgcolor=ft.colors.with_opacity(0.02, ft.colors.WHITE),
                    border_radius=8,
                    margin=ft.margin.symmetric(horizontal=20),
                ),
                
                # Input area
                ft.Container(
                    content=ft.Row(
                        [self.message_input, send_button],
                        spacing=10
                    ),
                    padding=20
                ),
            ],
            expand=True,
            spacing=0
        )
        
        # 🔥 Restore chat history or add welcome message
        if len(self.chat_messages) > 0:
            # Restore existing chat
            print(f"📝 Restoring {len(self.chat_messages)} chat messages from history...")
            for msg in self.chat_messages:
                self.chat_container.controls.append(msg)
        else:
            # Add initial welcome message only if no history
            if not active_integrations and not active_mcps:
                self.add_system_message(
                    "⚠️ No active integrations or MCP servers. Add them to get started!"
                )
            else:
                messages = []
                if active_integrations:
                    messages.append(f"✅ {len(active_integrations)} integration(s) connected")
                if active_mcps:
                    messages.append(f"✅ {len(active_mcps)} MCP server(s) active")
                self.add_system_message(f"☀️ Hello! I'm Helios, your AI DevOps assistant. " + " | ".join(messages) + ". Ask me anything! I can create tasks, show stats, manage GitHub, and more!")
        
        return content
    
    def build_mcp_servers_section(self, mcp_servers):
        """Build the MCP servers display section."""
        if not mcp_servers:
            return ft.Container(
                content=ft.Text(
                    "No MCP servers configured. Click 'Add MCP Server' to get started!",
                    size=12,
                    color=ft.colors.GREY_400
                ),
                padding=20
            )
        
        server_cards = []
        for server in mcp_servers:
            status_color = {
                "active": ft.colors.GREEN_400,
                "pending": ft.colors.ORANGE_400,
                "error": ft.colors.RED_400,
                "disabled": ft.colors.GREY_400
            }.get(server.get("status"), ft.colors.GREY_400)
            
            server_card = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.CLOUD, color=status_color, size=24),
                        ft.Column(
                            [
                                ft.Text(server["name"], weight=ft.FontWeight.BOLD, size=14),
                                ft.Text(
                                    f"{server['server_type'].upper()} • {server['status']}",
                                    size=12,
                                    color=ft.colors.GREY_400
                                )
                            ],
                            spacing=2,
                            expand=True
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            icon_color=ft.colors.RED_400,
                            tooltip="Delete MCP Server",
                            on_click=lambda _, s=server: self.delete_mcp_server(s["id"])
                        )
                    ],
                    spacing=10
                ),
                bgcolor=ft.colors.with_opacity(0.05, ft.colors.SURFACE_VARIANT),
                border_radius=8,
                padding=15,
                width=300
            )
            server_cards.append(server_card)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("🖥️ MCP Servers:", size=14, weight=ft.FontWeight.BOLD),
                ft.Row(server_cards, wrap=True, spacing=10)
            ]),
            padding=ft.padding.symmetric(horizontal=20, vertical=10)
        )
    
    def show_add_mcp_dialog(self, e):
        """Show dialog to add a new MCP server."""
        name_field = ft.TextField(label="Server Name", hint_text="e.g., Production ArgoCD", autofocus=True)
        type_field = ft.Dropdown(
            label="Server Type",
            options=[
                ft.dropdown.Option("argocd", "ArgoCD MCP"),
                ft.dropdown.Option("github", "GitHub MCP"),
                ft.dropdown.Option("notion", "Notion MCP"),
                ft.dropdown.Option("custom", "Custom MCP")
            ],
            value="argocd"
        )
        description_field = ft.TextField(
            label="Description (optional)",
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        endpoint_field = ft.TextField(
            label="MCP Endpoint URL",
            hint_text="e.g., http://localhost:3000"
        )
        
        def save_mcp_server(e):
            if not name_field.value or not endpoint_field.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please fill in required fields!"),
                    bgcolor=ft.colors.RED_400
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Create MCP server
            user_id = self.app_state.user.get("id")
            config = {"endpoint": endpoint_field.value}
            
            try:
                mcp_server = self.mcp_service.create_mcp_server(
                    user_id=user_id,
                    name=name_field.value,
                    server_type=type_field.value,
                    description=description_field.value,
                    config=config
                )
                
                # Update status to active (in production, you'd test connection first)
                self.mcp_service.update_mcp_status(mcp_server["id"], MCPStatus.ACTIVE)
                
                dialog.open = False
                self.page.update()
                
                # Reload the page
                self.page.go("/mcp")
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ MCP Server '{name_field.value}' added successfully!"),
                    bgcolor=ft.colors.GREEN_400
                )
                self.page.snack_bar.open = True
                self.page.update()
                
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error: {str(ex)}"),
                    bgcolor=ft.colors.RED_400
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Add MCP Server"),
            content=ft.Column(
                [
                    name_field,
                    type_field,
                    description_field,
                    endpoint_field,
                    ft.Container(
                        content=ft.Text(
                            "💡 MCP servers enable AI to interact with your tools directly. "
                            "Make sure the MCP endpoint is accessible.",
                            size=11,
                            color=ft.colors.GREY_400
                        ),
                        padding=10,
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.BLUE_400),
                        border_radius=5
                    )
                ],
                tight=True,
                spacing=15,
                width=500
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Add Server", on_click=save_mcp_server, bgcolor=ft.colors.PURPLE_700)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_mcp_server(self, server_id: str):
        """Delete an MCP server."""
        if self.mcp_service.delete_mcp_server(server_id):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ MCP Server deleted successfully!"),
                bgcolor=ft.colors.GREEN_400
            )
            self.page.snack_bar.open = True
            self.page.go("/mcp")  # Reload
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Failed to delete MCP server"),
                bgcolor=ft.colors.RED_400
            )
            self.page.snack_bar.open = True
        self.page.update()
    
    def on_mcp_selected(self, e):
        """Handle MCP server selection."""
        if e.control.value:
            self.selected_mcp_server = e.control.value
            server = self.mcp_service.get_mcp_server(self.selected_mcp_server)
            if server:
                self.add_system_message(
                    f"🔌 Connected to MCP: {server['server_type'].upper()} - {server['name']}"
                )
                # Record usage
                self.mcp_service.record_mcp_usage(self.selected_mcp_server)
    
    def add_message(self, content: str, is_user: bool = True):
        """Add a message to the chat."""
        message = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.icons.PERSON if is_user else ft.icons.SMART_TOY,
                        size=20,
                        color=ft.colors.BLUE_400 if is_user else ft.colors.PURPLE_400
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "You" if is_user else "AI Assistant",
                                weight=ft.FontWeight.BOLD,
                                size=12
                            ),
                            ft.Text(content, selectable=True, size=14)
                        ],
                        spacing=5,
                        expand=True
                    )
                ],
                spacing=10
            ),
            bgcolor=ft.colors.with_opacity(
                0.05, ft.colors.BLUE_400 if is_user else ft.colors.PURPLE_400
            ),
            border_radius=8,
            padding=15,
            margin=ft.margin.only(
                left=50 if is_user else 0,
                right=0 if is_user else 50
            )
        )
        self.chat_messages.append(message)
        self.chat_container.controls.append(message)
        self.page.update()
    
    def add_system_message(self, content: str):
        """Add a system message to the chat."""
        message = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.INFO_OUTLINE, size=20, color=ft.colors.AMBER_400),
                    ft.Text(content, size=12, color=ft.colors.GREY_400, expand=True)
                ],
                spacing=10
            ),
            padding=10,
            margin=ft.margin.symmetric(horizontal=50)
        )
        self.chat_messages.append(message)
        self.chat_container.controls.append(message)
        self.page.update()
    
    def add_action_result(self, content: str):
        """Add an action result message (highlighted)."""
        message = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.BOLT, size=24, color=ft.colors.GREEN_400),
                    ft.Markdown(
                        content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        on_tap_link=lambda e: self.page.launch_url(e.data),
                        expand=True
                    )
                ],
                spacing=10
            ),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.GREEN_400),
            border=ft.border.all(2, ft.colors.GREEN_400),
            border_radius=8,
            padding=15,
            margin=ft.margin.only(right=50)
        )
        self.chat_messages.append(message)
        self.chat_container.controls.append(message)
        self.page.update()
    
    def clear_chat_history(self, e):
        """Clear the chat history."""
        # Clear UI
        self.chat_container.controls.clear()
        
        # Clear stored messages
        self.chat_messages.clear()
        if hasattr(self.app_state, 'mcp_chat_messages'):
            self.app_state.mcp_chat_messages.clear()
        
        # Clear Ollama conversation history
        self.ollama_chat.conversation_history.clear()
        
        # Add welcome message
        self.add_system_message("🔄 Chat history cleared! I'm Helios ☀️, ready to help with your DevOps tasks!")
        
        # Update UI
        self.page.update()
        
        # Show confirmation
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("✅ Chat history cleared successfully!"),
            bgcolor=ft.colors.GREEN_400
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def quick_query(self, query: str):
        """Execute a quick query."""
        self.message_input.value = query
        self.send_message(None)
    
    def send_message(self, e):
        """Send a message and get AI response."""
        message = self.message_input.value.strip()
        if not message:
            return
        
        # Add user message
        self.add_message(message, is_user=True)
        self.message_input.value = ""
        self.page.update()
        
        # Get AI response
        self.get_ai_response(message)
    
    def get_ai_response(self, query: str):
        """Get AI response using Ollama with full app context!"""
        user_id = self.app_state.user.get("id")
        
        # Show loading
        loading_message = ft.Container(
            content=ft.Row(
                [
                    ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ft.Text("🤖 Ollama is thinking...", size=12, color=ft.colors.GREY_400)
                ],
                spacing=10
            ),
            padding=10,
            margin=ft.margin.symmetric(horizontal=50)
        )
        self.chat_container.controls.append(loading_message)
        self.page.update()
        
        try:
            # 🔥 Get comprehensive app context using action handler
            from backend.services.ai_action_handler import AIActionHandler
            
            action_handler = AIActionHandler(user_id)
            context = action_handler.get_full_app_context()
            
            # Debug: Print what we're passing
            print(f"\n🔍 Passing context to AI:")
            print(f"   Tasks: {context['tasks']['total']} items")
            print(f"     - TODO: {len(context['tasks']['by_status']['TODO'])}")
            print(f"     - IN_PROGRESS: {len(context['tasks']['by_status']['IN_PROGRESS'])}")
            print(f"     - DONE: {len(context['tasks']['by_status']['DONE'])}")
            print(f"   Integrations: {context['integrations']['total']} items")
            print(f"   User ID: {user_id}")
            print()
            
            # Call Ollama with context and user_id
            response, action_type = self.ollama_chat.chat(query, context=context, user_id=user_id)
            
            # Remove loading
            self.chat_container.controls.remove(loading_message)
            
            # Add AI response - highlight if it's an action
            if action_type == "action_executed":
                self.add_action_result(response)
                
                # 🔥 NEW: Trigger app refresh if task was created/updated/deleted
                if any(word in query.lower() for word in ['create', 'delete', 'update', 'mark', 'complete', 'finish']):
                    print("✅ Task action detected - refreshing app state...")
                    
                    # Add helpful tip
                    self.add_system_message("💡 Tip: Go to the Dashboard or Tasks page to see your updated tasks!")
                    
                    # Show snackbar notification
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("✅ Task modified! Check Dashboard to see changes."),
                        bgcolor=ft.colors.GREEN_400,
                        action="Go to Dashboard",
                        action_color=ft.colors.WHITE,
                        on_action=lambda _: self.page.go("/dashboard")
                    )
                    self.page.snack_bar.open = True
            else:
                self.add_message(response, is_user=False)
            
        except Exception as e:
            # Remove loading
            if loading_message in self.chat_container.controls:
                self.chat_container.controls.remove(loading_message)
            
            # Show detailed error
            error_msg = f"❌ **Ollama Error**\n\n{str(e)}\n\n"
            error_msg += "**Quick Fixes:**\n"
            error_msg += "• Ollama running? Check: `ps aux | grep ollama`\n"
            error_msg += "• Model available? Run: `ollama list`\n"
            error_msg += f"• Pull model: `ollama pull llama3.1`\n"
            error_msg += f"• Restart Ollama: `ollama serve`"
            
            self.add_message(error_msg, is_user=False)
        
        self.page.update()
