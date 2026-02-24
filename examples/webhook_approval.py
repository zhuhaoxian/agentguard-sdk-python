"""
Webhook approval example for AgentGuard Python SDK

This example demonstrates how to handle approval workflows using webhooks.
"""

import threading
from agentguard import AgentGuardOpenAI, WebhookServer

# Start webhook server in background
webhook_server = WebhookServer(
    port=5000,
    secret="your-webhook-secret"  # Should match AgentGuard configuration
)

webhook_thread = threading.Thread(
    target=webhook_server.start,
    daemon=True
)
webhook_thread.start()

print("Webhook server started on port 5000")

# Initialize AgentGuard client
client = AgentGuardOpenAI(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx"
)

# Make a request that requires approval
try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "Delete all user data"}  # High-risk operation
        ]
    )

    # If approval is required, AgentGuard will:
    # 1. Block the request
    # 2. Create an approval request
    # 3. Send webhook notification when approved/rejected
    # 4. Resume or cancel the request

    print(response.choices[0].message.content)

except Exception as e:
    print(f"Request failed or requires approval: {e}")

# Keep the script running to receive webhooks
input("Press Enter to exit...")
