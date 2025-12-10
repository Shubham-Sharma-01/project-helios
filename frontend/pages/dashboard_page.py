"""Dashboard page."""

import flet as ft
from backend.services.task_service import TaskService
from backend.services.integration_service import IntegrationService
from backend.services.ai_service import ai_service
from backend.services.notification_service import NotificationService
from backend.services.jira_sync_service import JiraSyncService
from backend.services.argocd_mcp_service import argocd_mcp
from frontend.components.sidebar import Sidebar
from frontend.components.topbar import Topbar


class DashboardPage(ft.View):
    """Main dashboard page."""
    
    def __init__(self, page: ft.Page, app_state):
        self.page = page
        self.app_state = app_state
        
        # Get stats
        stats = TaskService.get_task_stats(app_state.get_user_id())
        tasks = TaskService.get_user_tasks(app_state.get_user_id())
        
        # Get AI summary (tasks is already a list of dicts)
        ai_summary = ai_service.get_daily_summary(tasks) if tasks else "No tasks yet. Create your first task!"
        
        # Get integrations
        integrations = IntegrationService.get_user_integrations(app_state.get_user_id())
        
        # Get unread notifications
        unread_count = NotificationService.get_unread_count(app_state.get_user_id())
        
        # Stat cards
        stat_cards = ft.Row(
            [
                self.create_stat_card("🚨 Urgent", stats.get('urgent', 0), ft.colors.RED_400),
                self.create_stat_card("✅ To Do", stats.get('todo', 0), ft.colors.BLUE_400),
                self.create_stat_card("🎯 In Progress", stats.get('in_progress', 0), ft.colors.ORANGE_400),
                self.create_stat_card("📊 Total", stats.get('total', 0), ft.colors.GREEN_400),
            ],
            spacing=20,
            wrap=True
        )
        
        # AI Insights card
        ai_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.PSYCHOLOGY, color=ft.colors.PURPLE_400),
                                ft.Text("AI Insights", size=18, weight=ft.FontWeight.BOLD)
                            ]
                        ),
                        ft.Text(ai_summary, size=14)
                    ],
                    spacing=10
                ),
                padding=20
            )
        )
        
        # Recent tasks
        recent_tasks = ft.Column(
            [
                ft.Text("Recent Activity", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=10)
            ]
        )
        
        for task in tasks[:5]:
            recent_tasks.controls.append(self.create_task_card(task))
        
        if not tasks:
            recent_tasks.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No tasks yet. Go to Tasks page to create one!",
                        size=14,
                        color=ft.colors.GREY_400,
                        text_align=ft.TextAlign.CENTER
                    ),
                    padding=40
                )
            )
        
        # Integrations status
        integration_cards = ft.Row(spacing=15, wrap=True)
        
        if integrations:
            for integration in integrations:
                integration_cards.controls.append(self.create_integration_card(integration))
        else:
            integration_cards.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("No integrations yet", weight=ft.FontWeight.BOLD),
                                ft.Text("Go to Settings to add integrations", size=12, color=ft.colors.GREY_400),
                                ft.ElevatedButton(
                                    "Add Integration",
                                    on_click=lambda _: page.go("/settings")
                                )
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        padding=20,
                        width=200
                    )
                )
            )
        
        # Jira widget (if Jira integration exists)
        jira_widget = self.create_jira_widget()
        
        # Get combined Jira & Tasks view
        combined_view = self.create_combined_priority_view()
        
        # Build main content sections
        main_sections = [
            stat_cards,
            ft.Container(height=20),
            ai_card,
            ft.Container(height=30),
        ]
        
        # Add combined priority view if available
        if combined_view:
            main_sections.extend([
                ft.Text("📊 Priority Overview", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Your Jira tickets and tasks organized by priority", size=12, color=ft.colors.GREY_400),
                ft.Container(height=15),
                combined_view,
                ft.Container(height=30),
            ])
        else:
            main_sections.extend([
                recent_tasks,
                ft.Container(height=30),
            ])
        
        # Add Jira widget if available (compact version)
        if jira_widget:
            main_sections.extend([
                ft.Text("📋 Jira Summary", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                jira_widget,
                ft.Container(height=30),
            ])
        
        # Add ArgoCD MCP widget
        argocd_widget_mcp = self.create_argocd_mcp_widget()
        if argocd_widget_mcp:
            main_sections.extend([
                ft.Text("🔷 ArgoCD Status (Live via MCP)", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Real-time application health powered by AI", size=12, color=ft.colors.GREY_400),
                ft.Container(height=10),
                argocd_widget_mcp,
                ft.Container(height=30),
            ])
        
        # Add integrations section
        main_sections.extend([
            ft.Text("Integrations", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            integration_cards
        ])
        
        # Main content
        content = ft.Container(
            content=ft.Column(
                [
                    Topbar(page, app_state, "Dashboard", unread_count),
                    ft.Container(
                        content=ft.Column(
                            main_sections,
                            scroll=ft.ScrollMode.AUTO,
                            spacing=0
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
            route="/",
            controls=[
                ft.Row(
                    [
                        Sidebar(page, app_state, selected="dashboard"),
                        content
                    ],
                    spacing=0,
                    expand=True
                )
            ],
            padding=0
        )
    
    def create_stat_card(self, title: str, value: int, color):
        """Create a stat card."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                        ft.Text(str(value), size=32, weight=ft.FontWeight.BOLD, color=color)
                    ],
                    spacing=5
                ),
                padding=20,
                width=200
            )
        )
    
    def create_task_card(self, task):
        """Create a task preview card."""
        priority_colors = {
            'urgent': ft.colors.RED_400,
            'high': ft.colors.ORANGE_400,
            'medium': ft.colors.BLUE_400,
            'low': ft.colors.GREEN_400
        }
        
        source_icons = {
            'slack': "💬",
            'argocd': "🔷",
            'github': "🐙",
            'manual': "✏️"
        }
        
        # task is already a dict
        task_dict = task
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(task_dict['title'], weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    content=ft.Text(
                                        task_dict['priority'].upper(),
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.WHITE
                                    ),
                                    bgcolor=priority_colors.get(task_dict['priority'], ft.colors.GREY),
                                    border_radius=10,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=4)
                                )
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Text(
                                    f"{source_icons.get(task_dict['source'], '📝')} {task_dict['source'].title()}",
                                    size=12,
                                    color=ft.colors.GREY_400
                                ),
                                ft.Text("|", size=12, color=ft.colors.GREY_400),
                                ft.Text(
                                    task_dict['created_at'][:10] if task_dict['created_at'] else "Today",
                                    size=12,
                                    color=ft.colors.GREY_400
                                )
                            ]
                        )
                    ],
                    spacing=8
                ),
                padding=15
            )
        )
    
    def create_integration_card(self, integration):
        """Create integration status card."""
        # integration is already a dict now
        integration_dict = integration
        
        status_colors = {
            'active': ft.colors.GREEN_400,
            'pending': ft.colors.ORANGE_400,
            'error': ft.colors.RED_400,
            'disabled': ft.colors.GREY_400
        }
        
        type_icons = {
            'slack': "📢",
            'argocd': "🔷",
            'github': "🐙",
            'jira': "📝"
        }
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    type_icons.get(integration_dict['type'], "🔧"),
                                    size=24
                                ),
                                ft.Icon(
                                    ft.icons.CIRCLE,
                                    size=12,
                                    color=status_colors.get(integration_dict['status'], ft.colors.GREY)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(integration_dict['name'], weight=ft.FontWeight.BOLD),
                        ft.Text(
                            integration_dict['status'].title(),
                            size=12,
                            color=ft.colors.GREY_400
                        )
                    ],
                    spacing=8
                ),
                padding=15,
                width=150
            )
        )
    
    def create_jira_widget(self):
        """Create Jira issues widget."""
        # Find active Jira integration
        integrations = IntegrationService.get_user_integrations(self.app_state.get_user_id(), type='jira')
        
        if not integrations:
            return None
        
        jira_integration = integrations[0]  # Use first Jira integration
        
        # Check if integration is active
        if jira_integration.get('status') != 'active':
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Jira Integration", weight=ft.FontWeight.BOLD),
                            ft.Text("Integration not active. Check credentials in Settings.", size=12, color=ft.colors.ORANGE_400),
                            ft.ElevatedButton("Go to Settings", on_click=lambda _: self.page.go("/settings"))
                        ],
                        spacing=10
                    ),
                    padding=20
                )
            )
        
        # Get Jira issue summary
        jira_summary = JiraSyncService.get_jira_issue_summary(
            self.app_state.get_user_id(),
            jira_integration['id']
        )
        
        if 'error' in jira_summary:
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Jira Issues", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Error: {jira_summary['error']}", size=12, color=ft.colors.RED_400)
                        ],
                        spacing=10
                    ),
                    padding=20
                )
            )
        
        total = jira_summary.get('total', 0)
        by_status = jira_summary.get('by_status', {})
        by_priority = jira_summary.get('by_priority', {})
        recent_issues = jira_summary.get('recent_issues', [])
        
        # Status summary
        status_chips = ft.Row(spacing=10, wrap=True)
        for status, count in list(by_status.items())[:4]:
            status_chips.controls.append(
                ft.Container(
                    content=ft.Text(f"{status}: {count}", size=12),
                    bgcolor=ft.colors.BLUE_900,
                    padding=ft.padding.symmetric(8, 4),
                    border_radius=5
                )
            )
        
        # Priority summary
        priority_emojis = {
            'Highest': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢',
            'Lowest': '⚪'
        }
        
        priority_row = ft.Row(spacing=10)
        for priority in ['Highest', 'High', 'Medium', 'Low']:
            count = by_priority.get(priority, 0)
            if count > 0:
                priority_row.controls.append(
                    ft.Text(f"{priority_emojis.get(priority, '⚪')} {count}", size=12)
                )
        
        # Recent issues list
        issues_list = ft.Column(spacing=8)
        for issue in recent_issues[:3]:
            issue_row = ft.Row(
                [
                    ft.Text(
                        issue['key'],
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_400
                    ),
                    ft.Text(
                        issue['summary'][:50] + ('...' if len(issue['summary']) > 50 else ''),
                        size=12,
                        expand=True
                    )
                ],
                spacing=10
            )
            issues_list.controls.append(issue_row)
        
        # Refresh dashboard without syncing
        def refresh_dashboard():
            """Refresh dashboard to show latest Jira data."""
            self.page.splash = ft.ProgressBar()
            self.page.update()
            
            # Just reload the dashboard (Jira data refreshed automatically)
            self.page.splash = None
            self.page.views.clear()
            self.page.views.append(DashboardPage(self.page, self.app_state))
            self.page.update()
        
        # Sync button (imports Jira issues as tasks)
        def sync_jira(e):
            self.page.splash = ft.ProgressBar()
            self.page.update()
            
            created, updated, message = JiraSyncService.sync_jira_issues_to_tasks(
                self.app_state.get_user_id(),
                jira_integration['id']
            )
            
            self.page.splash = None
            
            # Show snackbar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.GREEN if created > 0 or updated > 0 else ft.colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Force full dashboard reload
            self.page.views.clear()
            self.page.views.append(DashboardPage(self.page, self.app_state))
            self.page.update()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(f"📋 {total} Assigned Issues", size=16, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "🔄 Refresh",
                                            on_click=lambda e: refresh_dashboard(),
                                            height=35,
                                            bgcolor=ft.colors.BLUE_700
                                        ),
                                        ft.ElevatedButton(
                                            "📥 Import to Tasks",
                                            on_click=sync_jira,
                                            height=35,
                                            bgcolor=ft.colors.GREEN_700
                                        )
                                    ],
                                    spacing=10
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(),
                        ft.Text("By Status:", size=12, weight=ft.FontWeight.BOLD),
                        status_chips,
                        ft.Container(height=10),
                        ft.Text("By Priority:", size=12, weight=ft.FontWeight.BOLD),
                        priority_row,
                        ft.Divider(),
                        ft.Text("Recent Issues:", size=12, weight=ft.FontWeight.BOLD),
                        issues_list if recent_issues else ft.Text("No issues found", size=12, color=ft.colors.GREY_400),
                    ],
                    spacing=10
                ),
                padding=20,
                width=700
            )
        )
    
    def create_combined_priority_view(self):
        """Create combined view of Jira issues and tasks by priority."""
        # Get Jira issues
        jira_integrations = IntegrationService.get_user_integrations(self.app_state.get_user_id(), type='jira')
        jira_issues = []
        
        if jira_integrations and jira_integrations[0].get('status') == 'active':
            jira_summary = JiraSyncService.get_jira_issue_summary(
                self.app_state.get_user_id(),
                jira_integrations[0]['id']
            )
            if 'error' not in jira_summary:
                # Use all_issues for priority overview (not just recent 5)
                jira_issues = jira_summary.get('all_issues', [])
        
        # Get tasks
        tasks = TaskService.get_user_tasks(self.app_state.get_user_id())
        
        if not jira_issues and not tasks:
            return None
        
        # Organize by status categories
        urgent_items = []
        todo_items = []
        in_progress_items = []
        
        # Process Jira issues
        for issue in jira_issues:
            item = {
                'type': 'jira',
                'key': issue['key'],
                'title': f"[{issue['key']}] {issue['summary']}",
                'priority': issue['priority'],
                'status': issue['status'],
                'url': issue.get('url', ''),
                'raw_data': issue
            }
            
            # Categorize by priority and status
            if issue['priority'] in ['Highest', 'High']:
                urgent_items.append(item)
            elif issue['status'] in ['To Do', 'Open', 'Backlog']:
                todo_items.append(item)
            elif issue['status'] in ['In Progress', 'In Review']:
                in_progress_items.append(item)
        
        # Process Tasks
        for task in tasks:
            if task['status'] == 'done':
                continue  # Skip completed tasks
            
            item = {
                'type': 'task',
                'key': task['id'],
                'title': task['title'],
                'priority': task['priority'],
                'status': task['status'],
                'description': task.get('description', ''),
                'raw_data': task
            }
            
            # Categorize by priority and status
            if task['priority'] == 'urgent':
                urgent_items.append(item)
            elif task['status'] == 'todo':
                todo_items.append(item)
            elif task['status'] == 'in_progress':
                in_progress_items.append(item)
        
        # Create columns
        urgent_col = self.create_priority_column("🚨 Urgent", urgent_items, ft.colors.RED_900)
        todo_col = self.create_priority_column("📝 To Do", todo_items, ft.colors.BLUE_900)
        in_progress_col = self.create_priority_column("🔄 In Progress", in_progress_items, ft.colors.ORANGE_900)
        
        return ft.Row(
            [urgent_col, todo_col, in_progress_col],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def create_priority_column(self, title: str, items: list, color):
        """Create a priority column with items."""
        item_cards = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=400)
        
        for item in items[:10]:  # Show max 10 items per column
            item_cards.controls.append(self.create_item_card(item))
        
        if not items:
            item_cards.controls.append(
                ft.Container(
                    content=ft.Text("No items", size=12, color=ft.colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    padding=20
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Container(
                                    content=ft.Text(str(len(items)), size=14, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.colors.WHITE24,
                                    padding=ft.padding.symmetric(8, 4),
                                    border_radius=10
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        bgcolor=color,
                        padding=15,
                        border_radius=ft.border_radius.only(top_left=10, top_right=10)
                    ),
                    ft.Container(
                        content=item_cards,
                        padding=10,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                        expand=True
                    )
                ],
                spacing=0
            ),
            width=350,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10
        )
    
    def create_item_card(self, item: dict):
        """Create a card for a Jira issue or task."""
        # Priority emoji
        priority_map = {
            'urgent': '🔴',
            'Highest': '🔴',
            'high': '🟠',
            'High': '🟠',
            'medium': '🟡',
            'Medium': '🟡',
            'low': '🟢',
            'Low': '🟢',
            'Lowest': '⚪'
        }
        
        priority_emoji = priority_map.get(item['priority'], '⚪')
        
        # Type indicator
        type_emoji = '🎫' if item['type'] == 'jira' else '✅'
        type_text = 'Jira' if item['type'] == 'jira' else 'Task'
        
        # Truncate title
        title = item['title']
        if len(title) > 60:
            title = title[:60] + '...'
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(priority_emoji, size=16),
                                ft.Text(type_emoji, size=14),
                                ft.Container(
                                    content=ft.Text(type_text, size=10),
                                    bgcolor=ft.colors.BLUE_700 if item['type'] == 'jira' else ft.colors.GREEN_700,
                                    padding=ft.padding.symmetric(6, 3),
                                    border_radius=5
                                )
                            ],
                            spacing=8
                        ),
                        ft.Text(
                            title,
                            size=13,
                            weight=ft.FontWeight.W_500,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.PSYCHOLOGY, size=14, color=ft.colors.PURPLE_400),
                                    ft.Text("AI Insights", size=11, color=ft.colors.PURPLE_400)
                                ],
                                spacing=5
                            ),
                            on_click=lambda e, itm=item: self.show_ai_insights(itm)
                        )
                    ],
                    spacing=8
                ),
                padding=12,
                ink=True,
                on_click=lambda e, itm=item: self.show_ai_insights(itm)
            )
        )
    
    def show_ai_insights(self, item: dict):
        """Show AI insights dialog for an item."""
        # Generate AI insights
        self.page.splash = ft.ProgressBar()
        self.page.update()
        
        # Check if we can get MCP context
        mcp_context = None
        from backend.services.mcp_service import mcp_service
        
        # Try to get ArgoCD context if this relates to infrastructure
        if mcp_service.check_mcp_argocd_available():
            # Check if ticket mentions ArgoCD apps
            title_lower = item['title'].lower()
            if any(keyword in title_lower for keyword in ['deploy', 'argocd', 'k8s', 'kubernetes', 'helm', 'pod', 'service']):
                mcp_context = mcp_service.get_argocd_apps_summary()
        
        if item['type'] == 'jira':
            prompt = f"""Analyze this Jira ticket and provide insights:

Title: {item['title']}
Priority: {item['priority']}
Status: {item['status']}

Provide:
1. What this ticket is about (brief summary)
2. Why it might be important
3. Recommended next steps
4. Estimated complexity (High/Medium/Low)
"""
        else:
            prompt = f"""Analyze this task and provide insights:

Title: {item['title']}
Priority: {item['priority']}
Status: {item['status']}
Description: {item.get('description', 'No description')}

Provide:
1. What this task involves (brief summary)
2. Why it's important
3. Recommended approach
4. Estimated time needed
"""
        
        # Get AI insights with MCP context
        insights = ai_service.generate_insights(prompt, mcp_context)
        
        self.page.splash = None
        
        # Show dialog
        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.icons.PSYCHOLOGY, color=ft.colors.PURPLE_400),
                    ft.Text("AI Insights", weight=ft.FontWeight.BOLD)
                ],
                spacing=10
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(item['title'], size=14, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text(insights, size=13, selectable=True),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                ft.Text(f"Type: {'🎫 Jira' if item['type'] == 'jira' else '✅ Task'}", size=11),
                                ft.Text(f"Priority: {item['priority']}", size=11),
                                ft.Text(f"Status: {item['status']}", size=11),
                            ],
                            spacing=15
                        )
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=600,
                height=400
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self.close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        """Close dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def create_argocd_mcp_widget(self):
        """Create ArgoCD widget powered by MCP with live data."""
        try:
            # Get real-time data from ArgoCD via MCP
            health_summary = argocd_mcp.get_health_summary()
            apps = health_summary.get('applications', [])
            
            if not apps:
                return None
            
            # Create app cards
            app_cards = ft.Row(spacing=15, wrap=True)
            
            for app in apps:
                # Health color
                health_color = ft.colors.GREEN_400 if app.get('health') == 'Healthy' else ft.colors.RED_400
                
                # Sync indicator
                sync_status = app.get('sync_status', app.get('sync', 'Unknown'))
                sync_emoji = "🟢" if sync_status == 'Synced' else "🔴"
                
                # AI Analysis button
                def show_ai_analysis(e, app_data=app):
                    self.show_argocd_ai_analysis(app_data)
                
                app_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.icons.APPS, color=ft.colors.BLUE_400),
                                        ft.Text(app['name'], size=14, weight=ft.FontWeight.BOLD)
                                    ],
                                    spacing=8
                                ),
                                ft.Divider(height=5),
                                ft.Row(
                                    [
                                        ft.Icon(ft.icons.FAVORITE, size=14, color=health_color),
                                        ft.Text(app.get('health', 'Unknown'), size=12)
                                    ],
                                    spacing=5
                                ),
                                ft.Row(
                                    [
                                        ft.Text(sync_emoji, size=14),
                                        ft.Text(sync_status, size=12)
                                    ],
                                    spacing=5
                                ),
                                ft.Container(height=5),
                                ft.ElevatedButton(
                                    "🤖 AI Analysis",
                                    on_click=show_ai_analysis,
                                    bgcolor=ft.colors.PURPLE_700,
                                    height=30,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=5),
                                    )
                                )
                            ],
                            spacing=8
                        ),
                        padding=15,
                        width=200
                    )
                )
                app_cards.controls.append(app_card)
            
            # Summary stats
            summary_row = ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(str(health_summary.get('total_apps', 0)), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400),
                                ft.Text("Total Apps", size=12)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2
                        ),
                        padding=10,
                        bgcolor=ft.colors.BLUE_900,
                        border_radius=8
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(str(health_summary.get('healthy', 0)), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
                                ft.Text("Healthy", size=12)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2
                        ),
                        padding=10,
                        bgcolor=ft.colors.GREEN_900,
                        border_radius=8
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(str(health_summary.get('out_of_sync', 0)), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_400),
                                ft.Text("Out of Sync", size=12)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2
                        ),
                        padding=10,
                        bgcolor=ft.colors.ORANGE_900,
                        border_radius=8
                    )
                ],
                spacing=15
            )
            
            return ft.Column(
                [
                    summary_row,
                    ft.Container(height=15),
                    app_cards
                ],
                spacing=10
            )
            
        except Exception as e:
            print(f"ArgoCD MCP widget error: {e}")
            return None
    
    def show_argocd_ai_analysis(self, app_data: dict):
        """Show AI analysis for an ArgoCD app."""
        self.page.splash = ft.ProgressBar()
        self.page.update()
        
        # Get MCP context
        mcp_context = argocd_mcp.get_health_summary()
        
        # Create prompt for AI
        prompt = f"""Analyze this ArgoCD application and provide insights:

Application: {app_data['name']}
Health: {app_data['health']}
Sync Status: {app_data['sync']}
Namespace: {app_data['namespace']}

Provide:
1. Current status assessment
2. Potential issues (if any)
3. Recommended actions
4. Best practices for this deployment
"""
        
        # Get AI insights with full MCP context
        insights = ai_service.generate_insights(prompt, mcp_context)
        
        self.page.splash = None
        
        # Show dialog
        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.icons.PSYCHOLOGY, color=ft.colors.PURPLE_400),
                    ft.Text(f"AI Analysis: {app_data['name']}", weight=ft.FontWeight.BOLD)
                ],
                spacing=10
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.HEALTH_AND_SAFETY, size=16, color=ft.colors.GREEN_400 if app_data['health'] == 'Healthy' else ft.colors.RED_400),
                                ft.Text(f"Health: {app_data['health']}", size=12),
                                ft.Text(f"Sync: {app_data['sync']}", size=12, color=ft.colors.BLUE_400)
                            ],
                            spacing=10
                        ),
                        ft.Divider(),
                        ft.Text(insights, size=13, selectable=True),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Text("💡 Powered by ArgoCD MCP + AI", size=10, italic=True, color=ft.colors.GREY_400),
                            bgcolor=ft.colors.PURPLE_900,
                            padding=8,
                            border_radius=5
                        )
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=600,
                height=400
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self.close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

