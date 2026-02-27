"""AgentGuard Approval API client"""

from typing import Optional, Dict, Any
import httpx
from enum import Enum

from .config import AgentGuardConfig
from .exceptions import AgentGuardError


class ApprovalStatus(str, Enum):
    """Approval status enum"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalStatusResponse:
    """Approval status query response"""

    def __init__(self, status: str, execution_result: Optional[Any] = None, remark: Optional[str] = None):
        self.status = ApprovalStatus(status)
        self.execution_result = execution_result
        self.remark = remark

    @property
    def is_pending(self) -> bool:
        """Check if approval is still pending"""
        return self.status == ApprovalStatus.PENDING

    @property
    def is_approved(self) -> bool:
        """Check if approval was approved"""
        return self.status == ApprovalStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        """Check if approval was rejected"""
        return self.status == ApprovalStatus.REJECTED

    @property
    def is_expired(self) -> bool:
        """Check if approval has expired"""
        return self.status == ApprovalStatus.EXPIRED

    def __repr__(self) -> str:
        return f"ApprovalStatusResponse(status={self.status.value})"


class ApprovalClient:
    """
    Client for querying approval status.

    Example:
        >>> from agentguard import ApprovalClient
        >>>
        >>> client = ApprovalClient(
        ...     agentguard_url="http://localhost:8080",
        ...     agent_api_key="ag_xxx"
        ... )
        >>>
        >>> # Query approval status
        >>> status = client.get_status("approval_id_123")
        >>> if status.is_approved:
        ...     print("Approved! Result:", status.execution_result)
        >>> elif status.is_rejected:
        ...     print("Rejected. Reason:", status.remark)
        >>> elif status.is_pending:
        ...     print("Still pending approval...")
    """

    def __init__(
        self,
        agentguard_url: Optional[str] = None,
        agent_api_key: Optional[str] = None,
        config: Optional[AgentGuardConfig] = None,
        timeout: float = 30.0
    ):
        """
        Initialize approval client.

        Args:
            agentguard_url: AgentGuard server URL
            agent_api_key: AgentGuard API key
            config: AgentGuardConfig object (alternative to individual params)
            timeout: Request timeout in seconds
        """
        if config:
            self.config = config
        elif agentguard_url and agent_api_key:
            self.config = AgentGuardConfig(
                agentguard_url=agentguard_url,
                agent_api_key=agent_api_key
            )
        else:
            self.config = AgentGuardConfig.from_env()

        self.config.validate()
        self.timeout = timeout

    def get_status(self, approval_id: str) -> ApprovalStatusResponse:
        """
        Query approval status by ID.

        Args:
            approval_id: The approval ID returned when approval was triggered

        Returns:
            ApprovalStatusResponse with status, execution_result (if approved), or remark (if rejected)

        Raises:
            AgentGuardError: If the request fails
        """
        url = f"{self.config.agentguard_url}/api/v1/approvals/{approval_id}/status"
        headers = {
            "X-Agent-API-Key": self.config.agent_api_key
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

                result = response.json()
                if result.get("code") != 200:
                    raise AgentGuardError(
                        f"Failed to query approval status: {result.get('message', 'Unknown error')}"
                    )

                data = result.get("data", {})
                return ApprovalStatusResponse(
                    status=data.get("status"),
                    execution_result=data.get("executionResult"),
                    remark=data.get("remark")
                )

        except httpx.HTTPStatusError as e:
            raise AgentGuardError(f"HTTP error querying approval status: {e}")
        except httpx.RequestError as e:
            raise AgentGuardError(f"Request error querying approval status: {e}")
        except Exception as e:
            raise AgentGuardError(f"Unexpected error querying approval status: {e}")

    def submit_reason(self, approval_id: str, reason: str) -> Dict[str, Any]:
        """
        Submit approval reason/justification.

        Args:
            approval_id: The approval ID
            reason: The reason/justification for the approval request

        Returns:
            Dict with submission result

        Raises:
            AgentGuardError: If the request fails
        """
        url = f"{self.config.agentguard_url}/api/v1/approvals/{approval_id}/reason"
        headers = {
            "X-Agent-API-Key": self.config.agent_api_key,
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json={"reason": reason})
                response.raise_for_status()

                result = response.json()
                if result.get("code") != 200:
                    raise AgentGuardError(
                        f"Failed to submit approval reason: {result.get('message', 'Unknown error')}"
                    )

                return {
                    "success": True,
                    "message": "Approval reason submitted successfully"
                }

        except httpx.HTTPStatusError as e:
            raise AgentGuardError(f"HTTP error submitting approval reason: {e}")
        except httpx.RequestError as e:
            raise AgentGuardError(f"Request error submitting approval reason: {e}")
        except Exception as e:
            raise AgentGuardError(f"Unexpected error submitting approval reason: {e}")
