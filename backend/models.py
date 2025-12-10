"""Database models for DevOps Command Center."""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.database import Base


def generate_uuid():
    """Generate UUID as string."""
    return str(uuid.uuid4())


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="created_by_user", foreign_keys="Integration.created_by")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TaskStatus(enum.Enum):
    """Task status enum."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(enum.Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskSource(enum.Enum):
    """Task source enum."""
    MANUAL = "manual"
    SLACK = "slack"
    ARGOCD = "argocd"
    GITHUB = "github"
    JIRA = "jira"


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    source = Column(SQLEnum(TaskSource), default=TaskSource.MANUAL, nullable=False)
    source_id = Column(String(255))  # External reference ID
    source_url = Column(String(500))  # Link back to source
    ai_priority_score = Column(Integer, default=5)  # 1-10 AI-calculated priority
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "source": self.source.value if self.source else None,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "ai_priority_score": self.ai_priority_score,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class IntegrationStatus(enum.Enum):
    """Integration status enum."""
    PENDING = "pending"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class Integration(Base):
    """Integration model."""
    __tablename__ = "integrations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    type = Column(String(50), nullable=False)  # 'slack', 'argocd', 'github', etc.
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING)
    config = Column(Text)  # JSON string for non-sensitive config
    error_message = Column(Text)
    last_sync_at = Column(DateTime)
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User", back_populates="integrations", foreign_keys=[created_by])
    credentials = relationship("IntegrationCredential", back_populates="integration", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        import json
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "config": json.loads(self.config) if self.config else {},
            "error_message": self.error_message,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class IntegrationCredential(Base):
    """Integration credentials (encrypted)."""
    __tablename__ = "integration_credentials"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    integration_id = Column(String(36), ForeignKey("integrations.id"), nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    integration = relationship("Integration", back_populates="credentials")


class NotificationType(enum.Enum):
    """Notification type enum."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class Notification(Base):
    """Notification model."""
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"))
    type = Column(SQLEnum(NotificationType), default=NotificationType.INFO)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "type": self.type.value if self.type else None,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MCPStatus(enum.Enum):
    """MCP server status enum."""
    PENDING = "pending"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class MCPServer(Base):
    """MCP Server model for managing multiple MCP connections."""
    __tablename__ = "mcp_servers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    server_type = Column(String(50), nullable=False)  # 'argocd', 'github', 'custom', etc.
    status = Column(SQLEnum(MCPStatus), default=MCPStatus.PENDING)
    config = Column(Text)  # JSON string for MCP configuration
    error_message = Column(Text)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    credentials = relationship("MCPCredential", back_populates="mcp_server", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "server_type": self.server_type,
            "status": self.status.value if self.status else None,
            "config": json.loads(self.config) if self.config else {},
            "error_message": self.error_message,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MCPCredential(Base):
    """MCP server credentials (encrypted)."""
    __tablename__ = "mcp_credentials"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    mcp_server_id = Column(String(36), ForeignKey("mcp_servers.id"), nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mcp_server = relationship("MCPServer", back_populates="credentials")

