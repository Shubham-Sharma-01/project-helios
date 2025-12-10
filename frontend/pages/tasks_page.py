"""Tasks management page."""

import flet as ft
from backend.services.task_service import TaskService
from backend.services.notification_service import NotificationService
from backend.services.integration_service import IntegrationService
from backend.services.jira_sync_service import JiraSyncService
from frontend.components.sidebar import Sidebar
from frontend.components.topbar import Topbar


class TasksPage(ft.View):
    """Tasks management page."""
    
    def __init__(self, page: ft.Page, app_state):
        self.page = page
        self.app_state = app_state
        
        # Get tasks
        self.tasks = TaskService.get_user_tasks(app_state.get_user_id())
        
        # Get notifications
        unread_count = NotificationService.get_unread_count(app_state.get_user_id())
        
        # Filter controls
        self.filter_status = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("all", "All Status"),
                ft.dropdown.Option("todo", "To Do"),
                ft.dropdown.Option("in_progress", "In Progress"),
                ft.dropdown.Option("done", "Done")
            ],
            value="all",
            width=150,
            on_change=lambda _: self.refresh_tasks()
        )
        
        self.filter_priority = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option("all", "All Priorities"),
                ft.dropdown.Option("urgent", "Urgent"),
                ft.dropdown.Option("high", "High"),
                ft.dropdown.Option("medium", "Medium"),
                ft.dropdown.Option("low", "Low")
            ],
            value="all",
            width=150,
            on_change=lambda _: self.refresh_tasks()
        )
        
        # Task list container
        self.task_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.render_tasks()
        
        # Main content
        content = ft.Container(
            content=ft.Column(
                [
                    Topbar(page, app_state, "My Tasks", unread_count),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Tasks", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Container(expand=True),
                                        self.filter_status,
                                        self.filter_priority,
                                        ft.ElevatedButton(
                                            "➕ New Task",
                                            on_click=lambda _: self.show_new_task_dialog()
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Container(height=20),
                                self.task_list
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
            route="/tasks",
            controls=[
                ft.Row(
                    [
                        Sidebar(page, app_state, selected="tasks"),
                        content
                    ],
                    spacing=0,
                    expand=True
                )
            ],
            padding=0
        )
    
    def render_tasks(self):
        """Render task list."""
        self.task_list.controls.clear()
        
        if not self.tasks:
            self.task_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.INBOX, size=64, color=ft.colors.GREY_400),
                            ft.Text("No tasks yet", size=20, color=ft.colors.GREY_400),
                            ft.Text("Create your first task to get started!", size=14, color=ft.colors.GREY_400)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    padding=60,
                    alignment=ft.alignment.center
                )
            )
        else:
            for task in self.tasks:
                self.task_list.controls.append(self.create_task_card(task))
    
    def create_task_card(self, task):
        """Create a task card."""
        # task is already a dict
        task_dict = task
        
        priority_colors = {
            'urgent': ft.colors.RED_400,
            'high': ft.colors.ORANGE_400,
            'medium': ft.colors.BLUE_400,
            'low': ft.colors.GREEN_400
        }
        
        status_icons = {
            'todo': ft.icons.CIRCLE_OUTLINED,
            'in_progress': ft.icons.TIMELAPSE,
            'done': ft.icons.CHECK_CIRCLE,
            'blocked': ft.icons.BLOCK
        }
        
        source_icons = {
            'slack': "💬",
            'argocd': "🔷",
            'github': "🐙",
            'manual': "✏️"
        }
        
        # Checkbox for quick status toggle
        checkbox = ft.Checkbox(
            value=task_dict['status'] == 'done',
            on_change=lambda e, tid=task_dict['id']: self.toggle_task_status(tid, e.control.value)
        )
        
        # Actions
        actions = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.EDIT,
                    tooltip="Edit",
                    on_click=lambda _, tid=task_dict['id']: self.edit_task(tid)
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="Delete",
                    on_click=lambda _, tid=task_dict['id']: self.delete_task(tid)
                )
            ],
            spacing=0
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        checkbox,
                        ft.Column(
                            [
                                ft.Text(task_dict['title'], weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(
                                    task_dict['description'] or "",
                                    size=13,
                                    color=ft.colors.GREY_400,
                                    max_lines=2
                                ),
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Text(
                                                task_dict['priority'].upper(),
                                                size=11,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.colors.WHITE
                                            ),
                                            bgcolor=priority_colors.get(task_dict['priority'], ft.colors.GREY),
                                            border_radius=10,
                                            padding=ft.padding.symmetric(horizontal=10, vertical=3)
                                        ),
                                        ft.Text(
                                            f"{source_icons.get(task_dict['source'], '📝')} {task_dict['source'].title()}",
                                            size=12,
                                            color=ft.colors.GREY_400
                                        ),
                                        ft.Text(
                                            task_dict['created_at'][:10] if task_dict['created_at'] else "",
                                            size=12,
                                            color=ft.colors.GREY_400
                                        )
                                    ],
                                    spacing=10
                                )
                            ],
                            spacing=8,
                            expand=True
                        ),
                        actions
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=20
            )
        )
    
    def sync_from_jira(self):
        """Sync tasks from Jira."""
        # Find Jira integration
        jira_integrations = IntegrationService.get_user_integrations(
            self.app_state.get_user_id(),
            type='jira'
        )
        
        if not jira_integrations:
            # Show snackbar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("⚠️ No Jira integration found. Add one in Settings first."),
                bgcolor=ft.colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        jira_integration = jira_integrations[0]
        
        if jira_integration.get('status') != 'active':
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("⚠️ Jira integration is not active. Check credentials in Settings."),
                bgcolor=ft.colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Show progress
        self.page.splash = ft.ProgressBar()
        self.page.update()
        
        # Sync issues
        created, updated, message = JiraSyncService.sync_jira_issues_to_tasks(
            self.app_state.get_user_id(),
            jira_integration['id']
        )
        
        # Hide progress
        self.page.splash = None
        
        # Refresh task list
        self.refresh_tasks()
        
        # Show result
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"✅ {message}"),
            bgcolor=ft.colors.GREEN if created > 0 or updated > 0 else ft.colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_new_task_dialog(self):
        """Show dialog to create new task."""
        title_field = ft.TextField(label="Title *", autofocus=True, width=500)
        description_field = ft.TextField(label="Description", multiline=True, min_lines=3, max_lines=5, width=500)
        priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option("low", "Low"),
                ft.dropdown.Option("medium", "Medium"),
                ft.dropdown.Option("high", "High"),
                ft.dropdown.Option("urgent", "Urgent")
            ],
            value="medium",
            width=200
        )
        
        def save_task(e):
            if not title_field.value:
                title_field.error_text = "Title is required"
                self.page.update()
                return
            
            TaskService.create_task(
                user_id=self.app_state.get_user_id(),
                title=title_field.value,
                description=description_field.value,
                priority=priority_dropdown.value
            )
            
            self.page.dialog.open = False
            self.refresh_tasks()
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Create New Task"),
            content=ft.Column(
                [
                    title_field,
                    description_field,
                    priority_dropdown
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Create", on_click=save_task)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def edit_task(self, task_id: str):
        """Edit a task."""
        task = TaskService.get_task(task_id)
        if not task:
            return
        
        # task is already a dict
        task_dict = task
        
        title_field = ft.TextField(label="Title *", value=task_dict['title'], autofocus=True, width=500)
        description_field = ft.TextField(
            label="Description",
            value=task_dict['description'] or "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=500
        )
        priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option("low", "Low"),
                ft.dropdown.Option("medium", "Medium"),
                ft.dropdown.Option("high", "High"),
                ft.dropdown.Option("urgent", "Urgent")
            ],
            value=task_dict['priority'],
            width=200
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("todo", "To Do"),
                ft.dropdown.Option("in_progress", "In Progress"),
                ft.dropdown.Option("done", "Done"),
                ft.dropdown.Option("blocked", "Blocked")
            ],
            value=task_dict['status'],
            width=200
        )
        
        def save_changes(e):
            TaskService.update_task(
                task_id=task_id,
                title=title_field.value,
                description=description_field.value,
                priority=priority_dropdown.value,
                status=status_dropdown.value
            )
            
            self.page.dialog.open = False
            self.refresh_tasks()
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Task"),
            content=ft.Column(
                [
                    title_field,
                    description_field,
                    ft.Row([priority_dropdown, status_dropdown], spacing=10)
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Save", on_click=save_changes)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_task(self, task_id: str):
        """Delete a task."""
        def confirm_delete(e):
            TaskService.delete_task(task_id)
            self.page.dialog.open = False
            self.refresh_tasks()
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Delete Task"),
            content=ft.Text("Are you sure you want to delete this task?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Delete", on_click=confirm_delete, bgcolor=ft.colors.RED)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def toggle_task_status(self, task_id: str, is_done: bool):
        """Toggle task completion status."""
        TaskService.update_task(
            task_id=task_id,
            status="done" if is_done else "todo"
        )
        self.refresh_tasks()
    
    def refresh_tasks(self):
        """Refresh task list with filters."""
        status_filter = None if self.filter_status.value == "all" else self.filter_status.value
        priority_filter = None if self.filter_priority.value == "all" else self.filter_priority.value
        
        self.tasks = TaskService.get_user_tasks(
            self.app_state.get_user_id(),
            status=status_filter,
            priority=priority_filter
        )
        
        self.render_tasks()
        self.page.update()
    
    def close_dialog(self):
        """Close the dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

