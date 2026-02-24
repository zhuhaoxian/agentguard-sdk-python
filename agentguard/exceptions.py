"""Custom exceptions for AgentGuard SDK"""


class AgentGuardError(Exception):
    """Base exception for AgentGuard SDK"""
    pass


class ConfigurationError(AgentGuardError):
    """Configuration error"""
    pass


class WebhookError(AgentGuardError):
    """Webhook related error"""
    pass


class ApprovalError(AgentGuardError):
    """Approval related error"""
    pass


class ApprovalTimeoutError(ApprovalError):
    """Approval timeout error"""
    pass


class ApprovalRejectedError(ApprovalError):
    """Approval rejected error"""
    pass
