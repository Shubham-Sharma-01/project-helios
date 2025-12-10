"""Migration script to add MCP tables to the database."""

from backend.database import engine, Base
from backend.models import MCPServer, MCPCredential


def migrate():
    """Create MCP tables."""
    print("Creating MCP tables...")
    
    # Create tables
    Base.metadata.create_all(bind=engine, tables=[
        MCPServer.__table__,
        MCPCredential.__table__
    ])
    
    print("✅ MCP tables created successfully!")


if __name__ == "__main__":
    migrate()

