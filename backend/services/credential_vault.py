"""Credential vault service for secure encryption/decryption."""

import os
import json
from typing import Dict, Any
from cryptography.fernet import Fernet
import base64


class CredentialVault:
    """Secure credential encryption and decryption service."""
    
    def __init__(self):
        # Get or generate master key
        master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if not master_key:
            # Generate a key for development
            master_key = Fernet.generate_key().decode()
            print(f"⚠️  Generated new encryption key: {master_key}")
            print("⚠️  Set ENCRYPTION_MASTER_KEY in .env for production!")
        
        # Ensure it's properly formatted
        if isinstance(master_key, str):
            master_key = master_key.encode()
        
        try:
            self._cipher = Fernet(master_key)
        except Exception as e:
            # If key is invalid, generate a new one
            print(f"⚠️  Invalid encryption key: {e}")
            new_key = Fernet.generate_key()
            self._cipher = Fernet(new_key)
            print(f"⚠️  Generated new key: {new_key.decode()}")
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> bytes:
        """
        Encrypt credentials dictionary.
        
        Args:
            credentials: Dictionary of credential data
            
        Returns:
            Encrypted bytes
        """
        # Convert to JSON string
        json_str = json.dumps(credentials)
        
        # Encrypt
        encrypted = self._cipher.encrypt(json_str.encode())
        
        return encrypted
    
    def decrypt_credentials(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Decrypt credentials.
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted credentials dictionary
        """
        try:
            # Decrypt
            decrypted = self._cipher.decrypt(encrypted_data)
            
            # Parse JSON
            credentials = json.loads(decrypted.decode())
            
            return credentials
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return {}


# Global vault instance
vault = CredentialVault()

