"""Integration management service."""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json

from backend.models import Integration, IntegrationCredential, IntegrationStatus
from backend.database import get_db
from backend.services.credential_vault import vault


class IntegrationService:
    """Service for managing integrations."""
    
    @staticmethod
    def create_integration(
        user_id: str,
        type: str,
        name: str,
        description: str = None,
        config: Dict[str, Any] = None,
        credentials: Dict[str, Any] = None
    ) -> str:
        """
        Create a new integration.
        
        Returns:
            integration_id: The ID of the created integration
        """
        with get_db() as db:
            # Create integration
            integration = Integration(
                type=type,
                name=name,
                description=description,
                config=json.dumps(config or {}),
                created_by=user_id,
                status=IntegrationStatus.PENDING
            )
            
            db.add(integration)
            db.flush()
            db.refresh(integration)
            
            # Get the ID before leaving the session
            integration_id = integration.id
            
            # Encrypt and store credentials if provided
            if credentials:
                encrypted = vault.encrypt_credentials(credentials)
                credential = IntegrationCredential(
                    integration_id=integration_id,
                    encrypted_data=encrypted
                )
                db.add(credential)
                db.flush()
            
            # Return the ID, not the object
            return integration_id
    
    @staticmethod
    def get_integration(integration_id: str) -> Optional[Dict[str, Any]]:
        """Get integration by ID."""
        with get_db() as db:
            integration = db.query(Integration).filter(Integration.id == integration_id).first()
            
            if not integration:
                return None
            
            # Convert to dict inside the session
            return integration.to_dict()
    
    @staticmethod
    def get_user_integrations(user_id: str, type: str = None) -> List[Dict[str, Any]]:
        """Get integrations for a user."""
        with get_db() as db:
            query = db.query(Integration).filter(Integration.created_by == user_id)
            
            if type:
                query = query.filter(Integration.type == type)
            
            integrations = query.order_by(Integration.created_at.desc()).all()
            
            # Convert to dicts inside the session
            return [integration.to_dict() for integration in integrations]
    
    @staticmethod
    def get_integration_credentials(integration_id: str) -> Optional[Dict[str, Any]]:
        """Get decrypted credentials for an integration."""
        with get_db() as db:
            credential = db.query(IntegrationCredential).filter(
                IntegrationCredential.integration_id == integration_id
            ).first()
            
            if not credential:
                return None
            
            return vault.decrypt_credentials(credential.encrypted_data)
    
    @staticmethod
    def update_integration(
        integration_id: str,
        name: str = None,
        description: str = None,
        config: Dict[str, Any] = None,
        credentials: Dict[str, Any] = None,
        status: str = None,
        error_message: str = None
    ) -> Optional[Integration]:
        """Update an integration."""
        with get_db() as db:
            integration = db.query(Integration).filter(Integration.id == integration_id).first()
            
            if not integration:
                return None
            
            if name is not None:
                integration.name = name
            if description is not None:
                integration.description = description
            if config is not None:
                integration.config = json.dumps(config)
            if status is not None:
                integration.status = IntegrationStatus[status.upper()]
            if error_message is not None:
                integration.error_message = error_message
            
            # Update credentials if provided
            if credentials:
                # Delete old credential
                db.query(IntegrationCredential).filter(
                    IntegrationCredential.integration_id == integration_id
                ).delete()
                
                # Create new credential
                encrypted = vault.encrypt_credentials(credentials)
                credential = IntegrationCredential(
                    integration_id=integration_id,
                    encrypted_data=encrypted
                )
                db.add(credential)
            
            integration.updated_at = datetime.utcnow()
            db.flush()
            db.refresh(integration)
            
            return integration
    
    @staticmethod
    def delete_integration(integration_id: str) -> bool:
        """Delete an integration."""
        with get_db() as db:
            integration = db.query(Integration).filter(Integration.id == integration_id).first()
            
            if not integration:
                return False
            
            # Credentials will be deleted via cascade
            db.delete(integration)
            return True
    
    @staticmethod
    def test_connection(integration_id: str) -> Tuple[bool, str]:
        """
        Test integration connection.
        
        Returns:
            (success, message)
        """
        integration = IntegrationService.get_integration(integration_id)
        if not integration:
            return False, "Integration not found"
        
        credentials = IntegrationService.get_integration_credentials(integration_id)
        if not credentials:
            return False, "No credentials found"
        
        # Import integration testers
        try:
            integration_type = integration['type']
            # integration['config'] is already a dict from to_dict()
            integration_config = integration['config']
            
            if integration_type == "slack":
                from backend.integrations.slack_integration import test_slack_connection
                return test_slack_connection(integration_config, credentials)
            
            elif integration_type == "argocd":
                from backend.integrations.argocd_integration import test_argocd_connection
                return test_argocd_connection(integration_config, credentials)
            
            elif integration_type == "jira":
                from backend.integrations.jira_integration import test_jira_connection
                return test_jira_connection(integration_config, credentials)
            
            elif integration_type == "github":
                from backend.integrations.github_integration import test_github_connection
                return test_github_connection(integration_config, credentials)
            
            else:
                return False, f"Integration type '{integration_type}' not supported yet"
        
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

