"""Task management service."""

from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.models import Task, TaskStatus, TaskPriority, TaskSource
from backend.database import get_db


class TaskService:
    """Service for managing tasks."""
    
    @staticmethod
    def create_task(
        user_id: str,
        title: str,
        description: str = None,
        priority: str = "medium",
        source: str = "manual",
        source_id: str = None,
        source_url: str = None,
        due_date: datetime = None
    ) -> Task:
        """Create a new task."""
        with get_db() as db:
            # Convert string enums to enum values - handle both string and enum inputs
            if isinstance(priority, TaskPriority):
                priority_enum = priority
            elif priority:
                priority_enum = TaskPriority[str(priority).upper()]
            else:
                priority_enum = TaskPriority.MEDIUM
            
            if isinstance(source, TaskSource):
                source_enum = source
            elif source:
                source_enum = TaskSource[str(source).upper()]
            else:
                source_enum = TaskSource.MANUAL
            
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority_enum,
                source=source_enum,
                source_id=source_id,
                source_url=source_url,
                due_date=due_date
            )
            
            db.add(task)
            db.flush()
            db.refresh(task)
            
            # Return task ID as string (session will close, can't access task.id later)
            task_id = task.id
            return task_id
    
    @staticmethod
    def get_task(task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        with get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            return task.to_dict()
    
    @staticmethod
    def get_user_tasks(
        user_id: str,
        status: str = None,
        priority: str = None,
        source: str = None
    ) -> List[Dict[str, Any]]:
        """Get tasks for a user with optional filters."""
        with get_db() as db:
            query = db.query(Task).filter(Task.user_id == user_id)
            
            if status:
                status_enum = TaskStatus[str(status).upper()] if not isinstance(status, TaskStatus) else status
                query = query.filter(Task.status == status_enum)
            
            if priority:
                priority_enum = TaskPriority[str(priority).upper()] if not isinstance(priority, TaskPriority) else priority
                query = query.filter(Task.priority == priority_enum)
            
            if source:
                source_enum = TaskSource[str(source).upper()] if not isinstance(source, TaskSource) else source
                query = query.filter(Task.source == source_enum)
            
            # Order by priority and creation date
            query = query.order_by(
                Task.priority.desc(),
                Task.created_at.desc()
            )
            
            tasks = query.all()
            return [task.to_dict() for task in tasks]
    
    @staticmethod
    def get_urgent_tasks(user_id: str) -> List[Dict[str, Any]]:
        """Get urgent tasks for a user."""
        with get_db() as db:
            tasks = db.query(Task).filter(
                Task.user_id == user_id,
                Task.status != TaskStatus.DONE,
                Task.priority == TaskPriority.URGENT
            ).order_by(Task.created_at.desc()).all()
            return [task.to_dict() for task in tasks]
    
    @staticmethod
    def update_task(
        task_id: str,
        title: str = None,
        description: str = None,
        status: str = None,
        priority: str = None,
        due_date: datetime = None
    ) -> Optional[Task]:
        """Update a task."""
        with get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return None
            
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                if isinstance(status, TaskStatus):
                    task.status = status
                    if status == TaskStatus.DONE:
                        task.completed_at = datetime.utcnow()
                else:
                    task.status = TaskStatus[str(status).upper()]
                    if str(status).upper() == "DONE":
                        task.completed_at = datetime.utcnow()
            if priority is not None:
                task.priority = TaskPriority[str(priority).upper()] if not isinstance(priority, TaskPriority) else priority
            if due_date is not None:
                task.due_date = due_date
            
            task.updated_at = datetime.utcnow()
            db.flush()
            db.refresh(task)
            
            return task
    
    @staticmethod
    def delete_task(task_id: str) -> bool:
        """Delete a task."""
        with get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return False
            
            db.delete(task)
            return True
    
    @staticmethod
    def get_task_stats(user_id: str) -> Dict[str, int]:
        """Get task statistics for a user."""
        with get_db() as db:
            all_tasks = db.query(Task).filter(Task.user_id == user_id).all()
            
            stats = {
                "total": len(all_tasks),
                "todo": len([t for t in all_tasks if t.status == TaskStatus.TODO]),
                "in_progress": len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
                "done": len([t for t in all_tasks if t.status == TaskStatus.DONE]),
                "urgent": len([t for t in all_tasks if t.priority == TaskPriority.URGENT and t.status != TaskStatus.DONE]),
                "high": len([t for t in all_tasks if t.priority == TaskPriority.HIGH and t.status != TaskStatus.DONE]),
            }
            
            return stats

