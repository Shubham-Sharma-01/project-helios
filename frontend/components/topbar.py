"""Top navigation bar component."""

import flet as ft


class Topbar(ft.Container):
    """Top navigation bar."""
    
    def __init__(self, page: ft.Page, app_state, title: str, unread_count: int = 0):
        self.page = page
        self.app_state = app_state
        
        # Notification badge
        badge = None
        if unread_count > 0:
            badge = ft.Container(
                content=ft.Text(str(unread_count), size=10, color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                right=0,
                top=0
            )
        
        notification_button = ft.Stack(
            [
                ft.IconButton(
                    icon=ft.icons.NOTIFICATIONS_OUTLINED,
                    on_click=lambda _: self.show_notifications()
                ),
                badge if badge else ft.Container()
            ]
        )
        
        super().__init__(
            content=ft.Row(
                [
                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    notification_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=20
        )
    
    def show_notifications(self):
        """Show notifications dialog."""
        from backend.services.notification_service import NotificationService
        
        notifications = NotificationService.get_user_notifications(
            self.app_state.get_user_id(),
            unread_only=True
        )
        
        notification_items = []
        for notification in notifications[:10]:
            notif_dict = notification.to_dict()
            notification_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.CIRCLE, size=12, color=ft.colors.BLUE),
                    title=ft.Text(notif_dict['title']),
                    subtitle=ft.Text(notif_dict['message']) if notif_dict.get('message') else None,
                    on_click=lambda e, nid=notif_dict['id']: self.mark_as_read(nid)
                )
            )
        
        if not notification_items:
            notification_items.append(
                ft.Container(
                    content=ft.Text("No new notifications", color=ft.colors.GREY_400),
                    padding=20
                )
            )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Notifications"),
            content=ft.Container(
                content=ft.Column(notification_items, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=300
            ),
            actions=[
                ft.TextButton("Mark All Read", on_click=lambda _: self.mark_all_read()),
                ft.TextButton("Close", on_click=lambda _: self.close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def mark_as_read(self, notification_id: str):
        """Mark notification as read."""
        from backend.services.notification_service import NotificationService
        NotificationService.mark_as_read(notification_id)
        self.close_dialog()
        self.page.update()
    
    def mark_all_read(self):
        """Mark all notifications as read."""
        from backend.services.notification_service import NotificationService
        NotificationService.mark_all_as_read(self.app_state.get_user_id())
        self.close_dialog()
        self.page.update()
    
    def close_dialog(self):
        """Close the dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

