"""AgentGuard Tools Helper

Provides tool definitions and function mappings for LLM function calling.
This allows business code to easily integrate AgentGuard approval tools.
"""

from typing import Dict, Any, Callable, List
import json


class AgentGuardTools:
    """Helper class for AgentGuard tool definitions and function mappings"""

    def __init__(self, agentguard_client):
        """
        Initialize with an AgentGuardOpenAI client instance.

        Args:
            agentguard_client: An instance of AgentGuardOpenAI
        """
        self.client = agentguard_client

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get AgentGuard tool definitions for LLM function calling.

        Returns:
            List of tool definitions in OpenAI function calling format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "submit_approval_reason",
                    "description": "提交审批申请理由。当需要执行高风险操作被 AgentGuard 拦截时，使用此工具提交申请理由。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "approval_id": {
                                "type": "string",
                                "description": "审批请求ID（从拦截消息中获取）"
                            },
                            "reason": {
                                "type": "string",
                                "description": "申请理由，需要详细说明为什么需要执行此操作"
                            }
                        },
                        "required": ["approval_id", "reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_approval_status",
                    "description": "查询审批状态。当用户告知审批已通过时，使用此工具查询审批结果并获取执行结果。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "approval_id": {
                                "type": "string",
                                "description": "审批请求ID"
                            }
                        },
                        "required": ["approval_id"]
                    }
                }
            }
        ]

    def get_function_map(self) -> Dict[str, Callable]:
        """
        Get function mapping for AgentGuard tools.

        Returns:
            Dictionary mapping function names to callable functions
        """
        return {
            "submit_approval_reason": self._submit_approval_reason_wrapper,
            "check_approval_status": self._check_approval_status_wrapper
        }

    def _submit_approval_reason_wrapper(self, approval_id: str, reason: str) -> Dict[str, Any]:
        """
        Wrapper for submit_reason that formats the response for LLM consumption.

        Args:
            approval_id: Approval request ID
            reason: Approval reason

        Returns:
            Formatted result dictionary
        """
        try:
            result = self.client.approvals.submit_reason(approval_id, reason)
            return {
                "success": True,
                "message": "审批理由已提交，等待审批人员审核",
                "approval_id": approval_id,
                "reason": reason
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"提交审批理由失败: {str(e)}"
            }

    def _check_approval_status_wrapper(self, approval_id: str) -> Dict[str, Any]:
        """
        Wrapper for get_status that formats the response for LLM consumption.

        Args:
            approval_id: Approval request ID

        Returns:
            Formatted result dictionary with status and execution result
        """
        try:
            status_response = self.client.approvals.get_status(approval_id)

            if status_response.is_approved:
                if status_response.execution_result:
                    # Extract content from execution result
                    content = self._extract_content_from_result(status_response.execution_result)
                    return {
                        "status": "approved",
                        "execution_status": "success",
                        "message": "审批通过，执行成功",
                        "content": content,
                        "executionResult": status_response.execution_result
                    }
                else:
                    return {
                        "status": "approved",
                        "execution_status": "pending",
                        "message": "审批通过，正在执行中，请稍后再次查询"
                    }

            elif status_response.is_rejected:
                return {
                    "status": "rejected",
                    "message": f"审批被拒绝: {status_response.remark}"
                }

            elif status_response.is_expired:
                return {
                    "status": "expired",
                    "message": "审批请求已过期"
                }

            elif status_response.is_pending:
                return {
                    "status": "pending",
                    "message": "审批仍在等待中，请稍后再查询"
                }

            else:
                return {
                    "status": "error",
                    "message": f"未知审批状态: {status_response.status}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"查询审批状态失败: {str(e)}"
            }

    def _extract_content_from_result(self, execution_result: Any) -> str:
        """
        Extract content from execution result.

        Args:
            execution_result: Execution result (may be full LLM response)

        Returns:
            Extracted text content
        """
        # Handle different formats of execution results
        if isinstance(execution_result, dict):
            # OpenAI format: {"choices": [{"message": {"content": "..."}}]}
            if "choices" in execution_result:
                choices = execution_result.get("choices", [])
                if choices and len(choices) > 0:
                    message = choices[0].get("message", {})
                    return message.get("content", "")

            # Simplified format: {"content": "..."}
            if "content" in execution_result:
                return execution_result.get("content", "")

            # Other formats: try to convert to JSON string
            return json.dumps(execution_result, ensure_ascii=False, indent=2)

        # If it's a string, return directly
        return str(execution_result)
