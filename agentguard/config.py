"""Configuration management for AgentGuard SDK"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentGuardConfig:
    """AgentGuard configuration"""

    agentguard_url: str
    agent_api_key: str
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> "AgentGuardConfig":
        """Create configuration from environment variables"""
        return cls(
            agentguard_url=os.getenv("AGENTGUARD_URL", "http://localhost:8080"),
            agent_api_key=os.getenv("AGENTGUARD_API_KEY", ""),
            webhook_url=os.getenv("AGENTGUARD_WEBHOOK_URL"),
            webhook_secret=os.getenv("AGENTGUARD_WEBHOOK_SECRET"),
        )

    def validate(self) -> None:
        """Validate configuration"""
        if not self.agentguard_url:
            raise ValueError("agentguard_url is required")
        if not self.agent_api_key:
            raise ValueError("agent_api_key is required")
