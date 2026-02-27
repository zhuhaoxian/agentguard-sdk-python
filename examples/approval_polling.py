"""
Example: Query approval status

This demonstrates the approval flow:
1. Agent sends request → triggers approval
2. Returns approval ID to Agent
3. Agent tells user about approval and provides ID
4. User approves on AgentGuard platform
5. Agent queries approval status when needed (by approval ID)
6. Gets approval result and continues execution
"""

from agentguard_zhx import ApprovalClient

# Initialize approval client
approval_client = ApprovalClient(
    agentguard_url="http://localhost:8080",
    agent_api_key="your_agent_api_key"
)


def check_approval_status(approval_id: str):
    """
    Query approval status by ID.

    Args:
        approval_id: The approval ID returned when approval was triggered
    """
    print(f"Querying approval status for ID: {approval_id}")

    # Query approval status
    status = approval_client.get_status(approval_id)

    # Check status and handle accordingly
    if status.is_approved:
        print("✅ Approval granted!")
        if status.execution_result:
            print(f"Execution result: {status.execution_result}")
            return status.execution_result
        return None

    elif status.is_rejected:
        print(f"❌ Approval rejected. Reason: {status.remark}")
        return None

    elif status.is_expired:
        print("⏰ Approval expired")
        return None

    elif status.is_pending:
        print("⏳ Approval is still pending")
        return None


if __name__ == "__main__":
    # Example: Query approval status
    approval_id = "your_approval_id_here"
    result = check_approval_status(approval_id)
