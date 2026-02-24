"""
Basic usage example for AgentGuard Python SDK

This example shows how to use AgentGuardOpenAI to make LLM API calls
through AgentGuard for governance and monitoring.
"""

from agentguard import AgentGuardOpenAI

# Initialize AgentGuard OpenAI client
client = AgentGuardOpenAI(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx"  # Replace with your AgentGuard API key
)

# Use standard OpenAI API - all requests go through AgentGuard
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is AgentGuard?"}
    ]
)

print(response.choices[0].message.content)

# All features work as expected
# - Cost tracking
# - Request logging
# - Policy enforcement
# - Approval workflows (if configured)
