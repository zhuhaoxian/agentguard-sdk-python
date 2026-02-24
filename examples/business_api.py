"""
Business API interception example

This example shows how to intercept business API calls using the requests library.
"""

from agentguard import enable_agentguard
import requests

# Enable AgentGuard interception for specific API patterns
enable_agentguard(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx",
    intercept_patterns=[
        r"https://api\.example\.com/.*",  # Intercept example.com API
        r"https://internal\.company\.com/.*"  # Intercept internal API
    ]
)

# Now all matching requests will go through AgentGuard
# AgentGuard will:
# - Log the request
# - Apply policies
# - Track costs (if applicable)
# - Require approval for high-risk operations

# Example: Call business API
response = requests.post(
    "https://api.example.com/users",
    json={
        "name": "John Doe",
        "email": "john@example.com"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Example: Call internal API
response = requests.get("https://internal.company.com/data")
print(f"Data: {response.json()}")
