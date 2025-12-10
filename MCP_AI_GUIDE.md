# MCP AI Integration Guide

## Overview

The MCP (Model Context Protocol) AI feature allows you to integrate and interact with multiple MCP servers from a centralized location in your DevOps Command Center. This feature enables you to:

- 🤖 **Manage Multiple MCPs**: Add and configure multiple MCP servers (ArgoCD, GitHub, custom servers)
- 💬 **Chat Interface**: Interact with MCP servers through a conversational interface
- 🔌 **Test Connections**: Verify MCP connectivity before use
- 📊 **Real-time Data**: Query live data from your infrastructure through MCPs

## Features

### 1. MCP Server Management

**Add New MCP Servers:**
- Navigate to "MCP AI" in the sidebar
- Click "+" to add a new MCP server
- Select the type: ArgoCD, GitHub, or Custom
- Configure connection details and credentials
- Test connection to verify

**Supported MCP Types:**
- **ArgoCD MCP**: Query application status, sync operations, resource details
- **GitHub MCP**: Query pull requests, issues, workflows
- **Custom MCP**: Connect to any MCP-compatible server

### 2. Interactive Chat Interface

**How to Use:**
1. Select an active MCP server from the dropdown
2. Type your question or command in the input field
3. Press Enter or click Send
4. View the response from the MCP server

**Example Prompts:**
- "Show me all ArgoCD applications"
- "What is the sync status of app1?"
- "List recent pull requests"
- "Get deployment status for production"

### 3. MCP Server Configuration

**ArgoCD MCP Configuration:**
```
Name: Production ArgoCD
Server URL: https://argocd.example.com
Namespace: argocd
API Token: (your ArgoCD token)
```

**GitHub MCP Configuration:**
```
Name: Company GitHub
Organization: your-org
Access Token: (your GitHub PAT)
```

**Custom MCP Configuration:**
```
Name: Custom Service
Endpoint URL: http://localhost:3000
API Key: (optional)
```

## Architecture

### Database Schema

**MCPServer Table:**
- `id`: Unique server identifier
- `user_id`: Owner of the MCP server
- `name`: Display name
- `server_type`: argocd, github, custom
- `status`: pending, active, error, disabled
- `config`: JSON configuration
- `last_used_at`: Timestamp of last interaction

**MCPCredential Table:**
- `id`: Credential identifier
- `mcp_server_id`: Foreign key to MCPServer
- `encrypted_data`: Encrypted credentials

### Backend Services

**MCPManagementService** (`backend/services/mcp_management_service.py`):
- `create_mcp_server()`: Create new MCP configuration
- `get_user_mcp_servers()`: List all MCPs for a user
- `update_mcp_server()`: Update MCP configuration
- `delete_mcp_server()`: Remove MCP
- `test_mcp_connection()`: Verify connectivity
- `get_mcp_credentials()`: Decrypt credentials for use

### Frontend Components

**MCPAIPage** (`frontend/pages/mcp_page.py`):
- Split-view interface: MCP list (left) + Chat (right)
- Add/Edit/Delete MCP servers
- Interactive chat with selected MCP
- Real-time response display with markdown support

## Usage Examples

### Example 1: Adding ArgoCD MCP

1. Click "MCP AI" in sidebar
2. Click "+" button
3. Fill in details:
   - Type: ArgoCD MCP
   - Name: "Production ArgoCD"
   - Server URL: https://argocd.company.com
   - Namespace: argocd
   - API Token: your-token
4. Click "Save & Test"
5. Wait for connection verification

### Example 2: Querying Applications

1. Select "Production ArgoCD" from dropdown
2. Type: "Show me all applications"
3. Press Enter
4. View application list with health and sync status

### Example 3: GitHub Operations

1. Select "Company GitHub" from dropdown
2. Type: "List recent pull requests"
3. Review PR list with status

## Security

- **Encrypted Credentials**: All sensitive data (tokens, keys) are encrypted at rest using AES-256
- **User Isolation**: Each user can only access their own MCP servers
- **Connection Testing**: Verify credentials before saving
- **Secure Storage**: Credentials stored separately from configuration

## API Integration

The MCP system can be extended to support additional MCP types:

```python
# Example: Adding a new MCP type
from backend.services.mcp_management_service import MCPManagementService

# Create new MCP server
mcp_id = MCPManagementService.create_mcp_server(
    user_id="user-123",
    name="My Custom MCP",
    server_type="custom",
    description="Custom integration",
    config={
        "endpoint_url": "http://localhost:3000",
        "timeout": 30
    },
    credentials={
        "api_key": "your-api-key"
    }
)

# Test connection
success, message = MCPManagementService.test_mcp_connection(mcp_id)
```

## Troubleshooting

### MCP Server Shows "Error" Status

**Possible Causes:**
1. Invalid credentials
2. Server unreachable
3. Network connectivity issues
4. Incorrect endpoint URL

**Solutions:**
- Click "Test" to see specific error message
- Edit MCP and verify all configuration fields
- Check if server is accessible from your network
- Verify API token/key is still valid

### No Response from MCP

**Possible Causes:**
1. MCP server not selected
2. Server is down
3. Query format not recognized

**Solutions:**
- Ensure an active MCP is selected in dropdown
- Click "Test" on the MCP to verify connectivity
- Try simpler queries like "help" or "status"

### Cannot Add New MCP

**Possible Causes:**
1. Required fields missing
2. Duplicate name
3. Invalid URL format

**Solutions:**
- Ensure all required (*) fields are filled
- Use unique names for each MCP
- Use proper URL format (http://... or https://...)

## Best Practices

1. **Descriptive Names**: Use clear names like "Production ArgoCD" instead of "argocd1"
2. **Test Connections**: Always test after adding/editing
3. **Regular Updates**: Rotate API tokens periodically and update MCP credentials
4. **Specific Queries**: Be specific in your prompts for better responses
5. **Monitor Status**: Check MCP status indicators regularly

## Future Enhancements

- [ ] Support for more MCP types (Kubernetes, Jenkins, etc.)
- [ ] Conversation history persistence
- [ ] Batch operations across multiple MCPs
- [ ] MCP response caching
- [ ] Custom prompt templates
- [ ] Integration with AI Service for intelligent responses

## Related Documentation

- [Integration Setup](INTEGRATION_CATALOG.md)
- [Authentication](AUTHENTICATION_SPEC.md)
- [API Documentation](IMPLEMENTATION_GUIDE.md)

## Support

For issues or questions:
1. Check the error message in the MCP status
2. Review the detailed logs in `app_output.log`
3. Verify your MCP server is accessible
4. Ensure your credentials are valid

