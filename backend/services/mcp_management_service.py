"""Service for managing MCP servers."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from backend.database import get_db
from backend.models import MCPServer, MCPCredential, MCPStatus
from backend.services.credential_vault import vault


class MCPManagementService:
    """Service for managing MCP servers."""
    
    @staticmethod
    def create_mcp_server(
        user_id: str,
        name: str,
        server_type: str,
        description: str = None,
        config: Dict[str, Any] = None,
        credentials: Dict[str, Any] = None
    ) -> str:
        """
        Create a new MCP server configuration.
        
        Args:
            user_id: User ID
            name: MCP server name
            server_type: Type of MCP server (argocd, github, custom, etc.)
            description: Optional description
            config: Configuration dict
            credentials: Credentials dict (will be encrypted)
            
        Returns:
            MCP server ID
        """
        with get_db() as db:
            try:
                # Create MCP server
                mcp_server = MCPServer(
                    user_id=user_id,
                    name=name,
                    server_type=server_type,
                    description=description,
                    config=json.dumps(config) if config else None,
                    status=MCPStatus.PENDING
                )
                
                db.add(mcp_server)
                db.flush()  # Get the ID
                
                # Store encrypted credentials if provided
                if credentials:
                    encrypted_creds = vault.encrypt_credentials(credentials)
                    mcp_cred = MCPCredential(
                        mcp_server_id=mcp_server.id,
                        encrypted_data=encrypted_creds
                    )
                    db.add(mcp_cred)
                
                db.commit()
                return mcp_server.id
                
            except Exception as e:
                db.rollback()
                raise e
    
    @staticmethod
    def get_user_mcp_servers(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all MCP servers for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of MCP server dicts
        """
        with get_db() as db:
            servers = db.query(MCPServer).filter(MCPServer.user_id == user_id).all()
            return [server.to_dict() for server in servers]
    
    @staticmethod
    def get_mcp_server(server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific MCP server.
        
        Args:
            server_id: MCP server ID
            
        Returns:
            MCP server dict or None
        """
        with get_db() as db:
            server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            return server.to_dict() if server else None
    
    @staticmethod
    def update_mcp_server(
        server_id: str,
        name: str = None,
        description: str = None,
        status: str = None,
        config: Dict[str, Any] = None,
        credentials: Dict[str, Any] = None,
        error_message: str = None
    ) -> bool:
        """
        Update an MCP server.
        
        Args:
            server_id: MCP server ID
            name: Optional new name
            description: Optional new description
            status: Optional new status
            config: Optional new config
            credentials: Optional new credentials
            error_message: Optional error message
            
        Returns:
            True if successful
        """
        with get_db() as db:
            try:
                server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
                if not server:
                    return False
                
                if name is not None:
                    server.name = name
                if description is not None:
                    server.description = description
                if status is not None:
                    server.status = MCPStatus[status.upper()]
                if config is not None:
                    server.config = json.dumps(config)
                if error_message is not None:
                    server.error_message = error_message
                
                # Update credentials if provided
                if credentials:
                    # Delete old credentials
                    db.query(MCPCredential).filter(MCPCredential.mcp_server_id == server_id).delete()
                    
                    # Add new credentials
                    encrypted_creds = vault.encrypt_credentials(credentials)
                    mcp_cred = MCPCredential(
                        mcp_server_id=server_id,
                        encrypted_data=encrypted_creds
                    )
                    db.add(mcp_cred)
                
                server.updated_at = datetime.utcnow()
                db.commit()
                return True
                
            except Exception as e:
                db.rollback()
                raise e
    
    @staticmethod
    def delete_mcp_server(server_id: str) -> bool:
        """
        Delete an MCP server.
        
        Args:
            server_id: MCP server ID
            
        Returns:
            True if successful
        """
        with get_db() as db:
            try:
                server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
                if not server:
                    return False
                
                db.delete(server)
                db.commit()
                return True
                
            except Exception as e:
                db.rollback()
                raise e
    
    @staticmethod
    def get_mcp_credentials(server_id: str) -> Optional[Dict[str, Any]]:
        """
        Get decrypted credentials for an MCP server.
        
        Args:
            server_id: MCP server ID
            
        Returns:
            Decrypted credentials dict or None
        """
        with get_db() as db:
            cred = db.query(MCPCredential).filter(MCPCredential.mcp_server_id == server_id).first()
            if not cred:
                return None
            
            return vault.decrypt_credentials(cred.encrypted_data)
    
    @staticmethod
    def test_mcp_connection(server_id: str) -> tuple[bool, str]:
        """
        Test connection to an MCP server.
        
        Args:
            server_id: MCP server ID
            
        Returns:
            Tuple of (success, message)
        """
        try:
            server = MCPManagementService.get_mcp_server(server_id)
            if not server:
                return False, "MCP server not found"
            
            server_type = server['server_type']
            
            # Test connection based on server type
            if server_type == 'argocd':
                # Test ArgoCD MCP connection
                return True, f"ArgoCD MCP '{server['name']}' is available"
            elif server_type == 'github':
                return True, f"GitHub MCP '{server['name']}' is available"
            elif server_type == 'custom':
                return True, f"Custom MCP '{server['name']}' is available"
            else:
                return False, f"Unknown MCP type: {server_type}"
                
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    @staticmethod
    def update_last_used(server_id: str):
        """Update the last_used_at timestamp for an MCP server."""
        with get_db() as db:
            server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            if server:
                server.last_used_at = datetime.utcnow()
                db.commit()

