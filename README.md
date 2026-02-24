# AgentGuard Python SDK

Python SDK for integrating with AgentGuard - AI Agent governance and monitoring platform.

## Features

- ✅ **Zero Code Changes** - Drop-in replacement for OpenAI client
- ✅ **Transparent Proxy** - All requests routed through AgentGuard
- ✅ **Webhook Support** - Real-time approval notifications
- ✅ **Business API Interception** - Monitor all API calls
- ✅ **Cost Tracking** - Automatic cost monitoring
- ✅ **Policy Enforcement** - Apply governance policies
- ✅ **Approval Workflows** - Handle high-risk operations

## Installation

```bash
pip install agentguard-zhx
```


## Quick Start

### Basic Usage

```python
from agentguard import AgentGuardOpenAI

# Initialize client
client = AgentGuardOpenAI(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx"
)

# Use standard OpenAI API
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
```

### Environment Variables

```python
# Set environment variables
export AGENTGUARD_URL="http://localhost:8080"
export AGENTGUARD_API_KEY="ag_xxx"

# Use without explicit configuration
from agentguard import AgentGuardOpenAI

client = AgentGuardOpenAI()  # Loads from environment
```

### Webhook Approval

```python
import threading
from agentguard import AgentGuardOpenAI, WebhookServer

# Start webhook server
webhook_server = WebhookServer(port=5000, secret="your-secret")
webhook_thread = threading.Thread(target=webhook_server.start, daemon=True)
webhook_thread.start()

# Use client as normal
client = AgentGuardOpenAI(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx"
)

# Approvals are handled automatically via webhooks
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "High-risk operation"}]
)
```

### Business API Interception

```python
from agentguard import enable_agentguard
import requests

# Enable global interception
enable_agentguard(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx",
    intercept_patterns=[r"https://api\.example\.com/.*"]
)

# All matching requests go through AgentGuard
response = requests.get("https://api.example.com/data")
```

## Configuration

### AgentGuardConfig

```python
from agentguard import AgentGuardConfig, AgentGuardOpenAI

config = AgentGuardConfig(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx",
    webhook_url="http://your-server.com/webhook",
    webhook_secret="your-secret"
)

client = AgentGuardOpenAI(config=config)
```

### WebhookServer Options

```python
from agentguard import WebhookServer

server = WebhookServer(
    port=5000,              # Port to listen on
    secret="your-secret",   # HMAC signature secret
    host="0.0.0.0"         # Host to bind to
)
```

## Examples

See the `examples/` directory for more examples:

- `basic_usage.py` - Basic OpenAI integration
- `webhook_approval.py` - Webhook-based approval handling
- `business_api.py` - Business API interception

## API Reference

### AgentGuardOpenAI

Drop-in replacement for OpenAI client that routes requests through AgentGuard.

**Parameters:**
- `agentguard_url` (str): AgentGuard server URL
- `agent_api_key` (str): AgentGuard API key
- `config` (AgentGuardConfig, optional): Configuration object

### WebhookServer

Lightweight webhook server for receiving approval notifications.

**Methods:**
- `start()` - Start the server (blocking)
- `register_callback(approval_id, callback)` - Register approval callback
- `wait_for_approval(approval_id, timeout)` - Wait for approval with timeout

### enable_agentguard()

Enable global request interception for the requests library.

**Parameters:**
- `agentguard_url` (str): AgentGuard server URL
- `agent_api_key` (str): AgentGuard API key
- `intercept_patterns` (List[str], optional): URL patterns to intercept (regex)

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black agentguard/

# Lint code
ruff check agentguard/
```

## License

MIT License

## Support

- Documentation: https://docs.agentguard.io
- Issues: https://github.com/agentguard/agentguard-sdk-python/issues
- Email: support@agentguard.io
