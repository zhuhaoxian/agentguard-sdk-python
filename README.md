# AgentGuard Python SDK

Python SDK for integrating with AgentGuard - AI Agent governance and monitoring platform.

## Features

- ✅ **Zero Code Changes** - Drop-in replacement for OpenAI client
- ✅ **Unified Client** - One client for all features (LLM + Approvals)
- ✅ **Transparent Proxy** - All requests routed through AgentGuard
- ✅ **Integrated Approval Management** - Built-in approval status query and submission
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
from agentguard_zhx import AgentGuardOpenAI

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

### Approval Status Query

Query approval status using integrated approval management:

```python
from agentguard_zhx import AgentGuardOpenAI

# One client for everything
client = AgentGuardOpenAI(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx"
)

# LLM calls
response = client.chat.completions.create(...)

# Approval management (integrated)
status = client.approvals.get_status("approval_id")

if status.is_approved:
    print("Approved:", status.execution_result)
elif status.is_rejected:
    print("Rejected:", status.remark)

# Submit approval reason
client.approvals.submit_reason("approval_id", "Need to delete test data")
```

### Environment Variables

```python
# Set environment variables
export AGENTGUARD_URL="http://localhost:8080"
export AGENTGUARD_API_KEY="ag_xxx"

# Use without explicit configuration
from agentguard_zhx import AgentGuardOpenAI

client = AgentGuardOpenAI()  # Loads from environment
```

### Business API Interception

```python
from agentguard_zhx import enable_agentguard
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
from agentguard_zhx import AgentGuardConfig, AgentGuardOpenAI

config = AgentGuardConfig(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx"
)

client = AgentGuardOpenAI(config=config)
```

## Examples

See the `examples/` directory for more examples:

- `basic_usage.py` - Basic OpenAI integration
- `approval_polling.py` - Query approval status
- `business_api.py` - Business API interception

## API Reference

### AgentGuardOpenAI

Drop-in replacement for OpenAI client with integrated approval management.

**Parameters:**
- `agentguard_url` (str): AgentGuard server URL
- `agent_api_key` (str): AgentGuard API key
- `config` (AgentGuardConfig, optional): Configuration object

**Integrated Approval Management:**

Access via `client.approvals`:
- `get_status(approval_id)` - Query approval status by ID
- `submit_reason(approval_id, reason)` - Submit approval reason/justification

**Returns:** `ApprovalStatusResponse` with:
- `status` - ApprovalStatus enum (PENDING/APPROVED/REJECTED/EXPIRED)
- `execution_result` - Result if approved and executed
- `remark` - Rejection reason if rejected
- `is_pending`, `is_approved`, `is_rejected`, `is_expired` - Helper properties

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

- Documentation: https://github.com/zhuhaoxian/agentguard-sdk-python/blob/main/README.md
- Issues: https://github.com/zhuhaoxian/agentguard-sdk-python/issues
- Email: zhx_stack@163.com
