"""MCP Server service for managing MCP connections."""

from backend.database import get_db
from backend.models import MCPServer, MCPStatus, MCPCredential
from backend.services.credential_vault import CredentialVault
import json
from datetime import datetime

# Initialize credential vault
vault = CredentialVault()


class MCPService:
    """Service for managing MCP servers."""
    
    @staticmethod
    def create_mcp_server(user_id: str, name: str, server_type: str, 
                         description: str = None, config: dict = None,
                         credentials: dict = None) -> dict:
        """Create a new MCP server configuration."""
        with get_db() as db:
            # Create MCP server
            mcp_server = MCPServer(
                user_id=user_id,
                name=name,
                description=description,
                server_type=server_type,
                config=json.dumps(config) if config else None,
                status=MCPStatus.PENDING
            )
            db.add(mcp_server)
            db.flush()
            
            # Store encrypted credentials if provided
            if credentials:
                encrypted = vault.encrypt_credentials(credentials)
                mcp_cred = MCPCredential(
                    mcp_server_id=mcp_server.id,
                    encrypted_data=encrypted
                )
                db.add(mcp_cred)
            
            db.commit()
            db.refresh(mcp_server)
            
            return mcp_server.to_dict()
    
    @staticmethod
    def get_user_mcp_servers(user_id: str) -> list:
        """Get all MCP servers for a user."""
        with get_db() as db:
            servers = db.query(MCPServer).filter(
                MCPServer.user_id == user_id
            ).order_by(MCPServer.created_at.desc()).all()
            
            return [server.to_dict() for server in servers]
    
    @staticmethod
    def get_mcp_server(server_id: str) -> dict:
        """Get a specific MCP server."""
        with get_db() as db:
            server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            if server:
                return server.to_dict()
            return None
    
    @staticmethod
    def update_mcp_server(server_id: str, **kwargs) -> dict:
        """Update an MCP server."""
        with get_db() as db:
            server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            if not server:
                return None
            
            for key, value in kwargs.items():
                if key == 'config' and isinstance(value, dict):
                    setattr(server, key, json.dumps(value))
                elif hasattr(server, key):
                    setattr(server, key, value)
            
            server.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(server)
            
            return server.to_dict()
    
    @staticmethod
    def delete_mcp_server(server_id: str) -> bool:
        """Delete an MCP server."""
        with get_db() as db:
            server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            if server:
                db.delete(server)
                db.commit()
                return True
            return False
    
    @staticmethod
    def get_mcp_credentials(server_id: str) -> dict:
        """Get decrypted credentials for an MCP server."""
        with get_db() as db:
            credential = db.query(MCPCredential).filter(
                MCPCredential.mcp_server_id == server_id
            ).first()
            
            if credential:
                return vault.decrypt_credentials(credential.encrypted_data)
            return {}
    
    @staticmethod
    def update_mcp_status(server_id: str, status: MCPStatus, error_message: str = None):
        """Update MCP server status."""
        with get_db() as db:
            server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            if server:
                server.status = status
                server.error_message = error_message
                server.updated_at = datetime.utcnow()
                db.commit()
    
    @staticmethod
    def record_mcp_usage(server_id: str):
        """Record last usage time for an MCP server."""
        with get_db() as db:
            server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            if server:
                server.last_used_at = datetime.utcnow()
                db.commit()
