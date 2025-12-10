# Authentication & Integration Management - Technical Specification

## 🎯 Overview
This document details the authentication layer and integration credential management system that allows users to configure all API keys and credentials through the web UI instead of manually editing configuration files.

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         Frontend UI                              │
│  - Login/Signup Pages                                            │
│  - Integration Setup Wizard                                      │
│  - Settings → Integrations Management                            │
└────────────────────┬─────────────────────────────────────────────┘
                     │ HTTPS (JWT Bearer Token)
┌────────────────────▼─────────────────────────────────────────────┐
│                    Authentication API                            │
│  - User Registration & Login                                     │
│  - JWT Token Issuance & Refresh                                  │
│  - Session Management                                            │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│               Integration Management API                         │
│  - CRUD Operations for Integrations                              │
│  - Credential Encryption/Decryption                              │
│  - Connection Testing                                            │
│  - Status Monitoring                                             │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│                  Credential Vault Service                        │
│  - AES-256 Encryption                                            │
│  - Secure Key Management                                         │
│  - Audit Logging                                                 │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│                     Database Layer                               │
│  - User & Organization Data                                      │
│  - Encrypted Credentials                                         │
│  - Audit Logs                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### Users & Organizations

```sql
-- Organizations (multi-tenant support)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL for OAuth-only users
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'developer', -- 'super_admin', 'org_admin', 'team_lead', 'developer', 'viewer'
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_role CHECK (role IN ('super_admin', 'org_admin', 'team_lead', 'developer', 'viewer'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org ON users(organization_id);

-- OAuth Connections
CREATE TABLE oauth_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google', 'github', 'microsoft'
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(provider, provider_user_id)
);

-- Session Management (for token revocation)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(refresh_token_hash);
```

### Integrations & Credentials

```sql
-- Integration Types (catalog)
CREATE TABLE integration_types (
    id VARCHAR(50) PRIMARY KEY, -- 'argocd', 'github', 'slack', etc.
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'ci_cd', 'source_control', 'communication', 'monitoring'
    logo_url TEXT,
    documentation_url TEXT,
    config_schema JSONB, -- JSON Schema for config validation
    credential_schema JSONB, -- JSON Schema for credential validation
    is_active BOOLEAN DEFAULT TRUE
);

-- Organization-level Integrations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    integration_type_id VARCHAR(50) REFERENCES integration_types(id),
    name VARCHAR(255) NOT NULL, -- User-friendly name, e.g., "Production ArgoCD"
    description TEXT,
    config JSONB DEFAULT '{}', -- Non-sensitive config (URLs, namespaces, etc.)
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'active', 'error', 'disabled'
    error_message TEXT,
    last_sync_at TIMESTAMP,
    next_sync_at TIMESTAMP,
    sync_interval INTEGER DEFAULT 300, -- seconds
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_status CHECK (status IN ('pending', 'active', 'error', 'disabled'))
);

CREATE INDEX idx_integrations_org ON integrations(organization_id);
CREATE INDEX idx_integrations_type ON integrations(integration_type_id);
CREATE INDEX idx_integrations_status ON integrations(status);

-- Encrypted Credentials
CREATE TABLE integration_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES integrations(id) ON DELETE CASCADE,
    credential_type VARCHAR(50) NOT NULL, -- 'api_token', 'oauth', 'basic_auth', 'ssh_key'
    encrypted_data BYTEA NOT NULL, -- AES-256 encrypted JSON
    encryption_key_version VARCHAR(50) DEFAULT 'v1', -- For key rotation
    metadata JSONB DEFAULT '{}', -- Non-sensitive metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP, -- For tokens that expire
    last_used_at TIMESTAMP,
    
    UNIQUE(integration_id, credential_type)
);

CREATE INDEX idx_credentials_integration ON integration_credentials(integration_id);

-- Personal User Integrations (optional feature)
CREATE TABLE user_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    integration_type_id VARCHAR(50) REFERENCES integration_types(id),
    name VARCHAR(255) NOT NULL,
    encrypted_credentials BYTEA NOT NULL,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Integration Activity Logs
CREATE TABLE integration_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES integrations(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL, -- 'connection_test', 'sync_started', 'sync_completed', 'error'
    status VARCHAR(20) NOT NULL, -- 'success', 'failure', 'warning'
    message TEXT,
    metadata JSONB DEFAULT '{}',
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_integration_logs_integration ON integration_logs(integration_id);
CREATE INDEX idx_integration_logs_created ON integration_logs(created_at);
```

### Audit & Security

```sql
-- Security Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    action VARCHAR(100) NOT NULL, -- 'login', 'logout', 'integration_created', 'credential_accessed'
    resource_type VARCHAR(50), -- 'user', 'integration', 'credential', 'task'
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(20) DEFAULT 'success', -- 'success', 'failure', 'blocked'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_org ON audit_logs(organization_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- Failed Login Attempts (for rate limiting & security)
CREATE TABLE failed_login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255),
    ip_address INET NOT NULL,
    attempted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_failed_login_ip ON failed_login_attempts(ip_address);
CREATE INDEX idx_failed_login_email ON failed_login_attempts(email);
```

---

## 🔐 Encryption Implementation

### Credential Vault Service

```python
# services/credential_vault.py

import os
import json
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

class CredentialVault:
    """Secure credential encryption and decryption service."""
    
    def __init__(self):
        # Master key from environment (NEVER commit to repo)
        self.master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if not self.master_key:
            raise ValueError("ENCRYPTION_MASTER_KEY not set in environment")
        
        # Derive encryption key from master key
        self._cipher = self._initialize_cipher()
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize Fernet cipher with derived key."""
        # Use PBKDF2 to derive a proper encryption key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'devops-command-center-salt',  # In production, use random salt per credential
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
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
        # Decrypt
        decrypted = self._cipher.decrypt(encrypted_data)
        
        # Parse JSON
        credentials = json.loads(decrypted.decode())
        
        return credentials
    
    def rotate_encryption(self, old_encrypted: bytes, old_key: str, new_key: str) -> bytes:
        """
        Re-encrypt data with new key (for key rotation).
        
        Args:
            old_encrypted: Data encrypted with old key
            old_key: Old encryption key
            new_key: New encryption key
            
        Returns:
            Data encrypted with new key
        """
        # Decrypt with old key
        old_cipher = Fernet(old_key.encode())
        decrypted = old_cipher.decrypt(old_encrypted)
        
        # Re-encrypt with new key
        new_cipher = Fernet(new_key.encode())
        new_encrypted = new_cipher.encrypt(decrypted)
        
        return new_encrypted


# Example usage
vault = CredentialVault()

# Encrypt
argocd_creds = {
    "server_url": "https://argocd.example.com",
    "auth_token": "your-secret-token",
    "tls_verify": True
}
encrypted = vault.encrypt_credentials(argocd_creds)

# Store in database
# integration_credentials.encrypted_data = encrypted

# Later, retrieve and decrypt
decrypted = vault.decrypt_credentials(encrypted)
# Use decrypted credentials for API calls
```

### Environment Variables Setup

```bash
# .env (NEVER commit this file)

# Generate a secure master key (run once):
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

ENCRYPTION_MASTER_KEY=your-generated-key-here

# Alternative: Use a passphrase (converted to key)
# ENCRYPTION_PASSPHRASE=your-secure-passphrase-here
```

---

## 🌐 API Endpoints

### Authentication Endpoints

```python
# Authentication API

POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh-token
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
POST   /api/v1/auth/verify-email
GET    /api/v1/auth/me
PATCH  /api/v1/auth/me
POST   /api/v1/auth/change-password

# OAuth
GET    /api/v1/auth/oauth/{provider}/authorize
GET    /api/v1/auth/oauth/{provider}/callback
POST   /api/v1/auth/oauth/{provider}/disconnect
```

#### Example: User Registration

**Request:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "organization_name": "Acme Corp" // Optional: create new org
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "org_admin",
      "organization": {
        "id": "uuid",
        "name": "Acme Corp",
        "slug": "acme-corp"
      }
    },
    "tokens": {
      "access_token": "eyJhbGc...",
      "refresh_token": "eyJhbGc...",
      "expires_in": 3600
    }
  }
}
```

#### Example: Login

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "org_admin",
      "organization_id": "uuid"
    },
    "tokens": {
      "access_token": "eyJhbGc...",
      "refresh_token": "eyJhbGc...",
      "expires_in": 3600
    }
  }
}
```

### Integration Management Endpoints

```python
# Integration API

GET    /api/v1/integrations                    # List all integrations
POST   /api/v1/integrations                    # Create new integration
GET    /api/v1/integrations/{id}               # Get integration details
PATCH  /api/v1/integrations/{id}               # Update integration
DELETE /api/v1/integrations/{id}               # Delete integration
POST   /api/v1/integrations/{id}/test          # Test connection
POST   /api/v1/integrations/{id}/sync          # Trigger sync
GET    /api/v1/integrations/{id}/logs          # Get integration logs
PATCH  /api/v1/integrations/{id}/credentials   # Update credentials
POST   /api/v1/integrations/{id}/enable        # Enable integration
POST   /api/v1/integrations/{id}/disable       # Disable integration

# Integration Types
GET    /api/v1/integration-types               # List available types
GET    /api/v1/integration-types/{type_id}     # Get type details & schema
```

#### Example: Create Integration

**Request:**
```http
POST /api/v1/integrations
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "integration_type_id": "argocd",
  "name": "Production ArgoCD",
  "description": "ArgoCD instance for production deployments",
  "config": {
    "server_url": "https://argocd.example.com",
    "namespace": "argocd",
    "tls_verify": true,
    "sync_interval": 300
  },
  "credentials": {
    "credential_type": "api_token",
    "auth_token": "your-secret-token-here"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "integration": {
      "id": "uuid",
      "integration_type_id": "argocd",
      "name": "Production ArgoCD",
      "description": "ArgoCD instance for production deployments",
      "config": {
        "server_url": "https://argocd.example.com",
        "namespace": "argocd",
        "tls_verify": true,
        "sync_interval": 300
      },
      "status": "pending",
      "created_at": "2024-11-24T10:00:00Z",
      "created_by": {
        "id": "uuid",
        "full_name": "John Doe"
      }
    }
  },
  "message": "Integration created successfully. Testing connection..."
}
```

#### Example: Test Connection

**Request:**
```http
POST /api/v1/integrations/{integration_id}/test
Authorization: Bearer {access_token}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "status": "active",
    "message": "Connection successful",
    "details": {
      "server_version": "v2.8.0",
      "applications_count": 15,
      "response_time_ms": 245
    }
  }
}
```

**Response (Failure):**
```json
{
  "success": false,
  "error": {
    "code": "CONNECTION_FAILED",
    "message": "Failed to connect to ArgoCD server",
    "details": {
      "reason": "Invalid authentication token",
      "status_code": 401
    }
  }
}
```

#### Example: List Integrations

**Request:**
```http
GET /api/v1/integrations?status=active&type=argocd
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "integrations": [
      {
        "id": "uuid-1",
        "integration_type_id": "argocd",
        "name": "Production ArgoCD",
        "status": "active",
        "config": {
          "server_url": "https://argocd.example.com"
        },
        "last_sync_at": "2024-11-24T10:30:00Z",
        "created_at": "2024-11-20T09:00:00Z"
      },
      {
        "id": "uuid-2",
        "integration_type_id": "argocd",
        "name": "Staging ArgoCD",
        "status": "active",
        "config": {
          "server_url": "https://argocd-staging.example.com"
        },
        "last_sync_at": "2024-11-24T10:28:00Z",
        "created_at": "2024-11-21T14:30:00Z"
      }
    ],
    "pagination": {
      "total": 2,
      "page": 1,
      "per_page": 20
    }
  }
}
```

---

## 🔄 Integration Management Workflows

### Workflow 1: Add New Integration

```
1. User clicks "Add Integration" in Settings
   ↓
2. Frontend shows integration type selector
   ↓
3. User selects integration type (e.g., ArgoCD)
   ↓
4. Frontend fetches integration schema
   GET /api/v1/integration-types/argocd
   ↓
5. Frontend renders dynamic form based on schema
   ↓
6. User fills in:
   - Server URL
   - Auth token
   - Configuration options
   ↓
7. User clicks "Test Connection"
   POST /api/v1/integrations (with test=true)
   ↓
8. Backend:
   - Encrypts credentials
   - Tests connection
   - Returns result
   ↓
9. If successful:
   - Backend saves integration
   - Backend creates background sync job
   - Frontend shows success message
   - Frontend redirects to integration details
   ↓
10. If failed:
    - Backend returns error details
    - Frontend shows error message
    - User can retry or edit config
```

### Workflow 2: Edit Integration Credentials

```
1. User goes to Settings → Integrations
   ↓
2. User clicks "Edit" on an integration
   ↓
3. Frontend shows edit form (credentials are masked)
   ↓
4. User updates credentials (e.g., new API token)
   ↓
5. User clicks "Save & Test"
   PATCH /api/v1/integrations/{id}/credentials
   ↓
6. Backend:
   - Decrypts old credentials (for audit)
   - Encrypts new credentials
   - Tests connection with new credentials
   - If successful: saves and marks integration as active
   - If failed: keeps old credentials, returns error
   ↓
7. Frontend shows result
   ↓
8. Audit log created:
   "User {name} updated credentials for {integration}"
```

### Workflow 3: Integration Health Monitoring

```
Background Job (runs every 5 minutes):

1. Fetch all active integrations
   ↓
2. For each integration:
   - Decrypt credentials
   - Make health check API call
   - Record response time and status
   ↓
3. If health check fails:
   - Update integration status to 'error'
   - Log error details
   - Create notification for org admins
   - Retry with exponential backoff
   ↓
4. If health check succeeds:
   - Update integration status to 'active'
   - Update last_sync_at timestamp
   - Clear any previous error messages
```

---

## 🧪 Testing Integration Connections

### Connection Test Service

```python
# services/integration_tester.py

from typing import Dict, Any, Tuple
import requests
from .credential_vault import CredentialVault

class IntegrationTester:
    """Test integration connections."""
    
    def __init__(self, vault: CredentialVault):
        self.vault = vault
    
    def test_argocd(self, config: Dict, credentials: Dict) -> Tuple[bool, str, Dict]:
        """
        Test ArgoCD connection.
        
        Returns:
            (success, message, details)
        """
        try:
            server_url = config['server_url']
            auth_token = credentials['auth_token']
            
            # Make API call to ArgoCD
            response = requests.get(
                f"{server_url}/api/v1/applications",
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=10,
                verify=config.get('tls_verify', True)
            )
            
            if response.status_code == 200:
                apps = response.json()
                return (
                    True,
                    "Connection successful",
                    {
                        "applications_count": len(apps.get('items', [])),
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
                )
            else:
                return (
                    False,
                    f"Connection failed with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
        
        except requests.exceptions.Timeout:
            return (False, "Connection timeout", {"timeout": 10})
        except requests.exceptions.ConnectionError:
            return (False, "Cannot reach server", {"server_url": server_url})
        except Exception as e:
            return (False, f"Unexpected error: {str(e)}", {})
    
    def test_github(self, config: Dict, credentials: Dict) -> Tuple[bool, str, Dict]:
        """Test GitHub connection."""
        try:
            token = credentials['access_token']
            
            response = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                return (
                    True,
                    "Connection successful",
                    {
                        "username": user['login'],
                        "name": user.get('name'),
                        "rate_limit_remaining": response.headers.get('X-RateLimit-Remaining')
                    }
                )
            else:
                return (False, f"Authentication failed: {response.status_code}", {})
        
        except Exception as e:
            return (False, f"Error: {str(e)}", {})
    
    def test_slack(self, config: Dict, credentials: Dict) -> Tuple[bool, str, Dict]:
        """Test Slack connection."""
        try:
            bot_token = credentials['bot_token']
            
            response = requests.post(
                "https://slack.com/api/auth.test",
                headers={"Authorization": f"Bearer {bot_token}"},
                timeout=10
            )
            
            data = response.json()
            
            if data.get('ok'):
                return (
                    True,
                    "Connection successful",
                    {
                        "team": data.get('team'),
                        "user": data.get('user'),
                        "bot_id": data.get('bot_id')
                    }
                )
            else:
                return (False, f"Slack API error: {data.get('error')}", {})
        
        except Exception as e:
            return (False, f"Error: {str(e)}", {})
    
    def test_integration(self, integration_type: str, config: Dict, credentials: Dict) -> Tuple[bool, str, Dict]:
        """Route to appropriate test function."""
        testers = {
            'argocd': self.test_argocd,
            'github': self.test_github,
            'slack': self.test_slack,
            # Add more as needed
        }
        
        tester = testers.get(integration_type)
        if not tester:
            return (False, f"No tester available for {integration_type}", {})
        
        return tester(config, credentials)
```

---

## 🎨 Frontend Integration Forms

### Dynamic Form Generation

```typescript
// frontend/src/components/IntegrationForm.tsx

interface IntegrationSchema {
  type: string;
  name: string;
  config_schema: {
    properties: {
      [key: string]: {
        type: string;
        title: string;
        description?: string;
        required?: boolean;
        default?: any;
      };
    };
  };
  credential_schema: {
    // Similar structure
  };
}

// Fetch schema from API
const schema = await fetch(`/api/v1/integration-types/${type}`);

// Render form dynamically
<Form>
  {Object.entries(schema.config_schema.properties).map(([key, field]) => (
    <FormField key={key}>
      <Label>{field.title}</Label>
      <Input
        type={field.type}
        name={key}
        required={field.required}
        placeholder={field.description}
        defaultValue={field.default}
      />
    </FormField>
  ))}
  
  <Button onClick={handleTestConnection}>Test Connection</Button>
  <Button onClick={handleSave}>Save Integration</Button>
</Form>
```

---

## 🔒 Security Checklist

- [ ] All credentials encrypted at rest (AES-256)
- [ ] Master encryption key stored securely (env var, not in code)
- [ ] JWT tokens use strong secrets
- [ ] Passwords hashed with bcrypt (12+ rounds)
- [ ] HTTPS only (no HTTP allowed)
- [ ] CORS properly configured
- [ ] CSRF protection enabled
- [ ] Rate limiting on auth endpoints
- [ ] Failed login tracking & lockout
- [ ] Audit logs for all security events
- [ ] No credentials in logs or error messages
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection (escape user input)
- [ ] Secure session management
- [ ] Token revocation on logout
- [ ] Regular security audits

---

*This specification provides a complete authentication and credential management system for the DevOps Command Center.*

