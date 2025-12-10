"""Notification service."""

from typing import List, Optional
from datetime import datetime

from backend.models import Notification, NotificationType
from backend.database import get_db


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    def create_notification(
        user_id: str,
        title: str,
        message: str = None,
        type: str = "info",
        task_id: str = None
    ) -> Notification:
        """Create a new notification."""
        with get_db() as db:
            type_enum = NotificationType[type.upper()] if type else NotificationType.INFO
            
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type_enum,
                task_id=task_id
            )
            
            db.add(notification)
            db.flush()
            db.refresh(notification)
            
            return notification
    
    @staticmethod
    def get_user_notifications(user_id: str, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user."""
        with get_db() as db:
            query = db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            return query.order_by(Notification.created_at.desc()).all()
    
    @staticmethod
    def mark_as_read(notification_id: str) -> bool:
        """Mark notification as read."""
        with get_db() as db:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            
            if not notification:
                return False
            
            notification.is_read = True
            db.flush()
            
            return True
    
    @staticmethod
    def mark_all_as_read(user_id: str) -> int:
        """Mark all notifications as read for a user."""
        with get_db() as db:
            count = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).update({"is_read": True})
            
            db.flush()
            
            return count
    
    @staticmethod
    def get_unread_count(user_id: str) -> int:
        """Get count of unread notifications."""
        with get_db() as db:
            return db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).count()

