"""AgentGuard OpenAI client wrapper"""

from typing import Optional
import httpx
from openai import OpenAI

from .config import AgentGuardConfig
from .interceptors.httpx_interceptor import AgentGuardTransport


class AgentGuardOpenAI(OpenAI):
    """
    AgentGuard wrapper for OpenAI client.

    This class extends the OpenAI client to route all requests through AgentGuard
    for governance, monitoring, and cost tracking.

    Example:
        >>> from agentguard import AgentGuardOpenAI
        >>>
        >>> client = AgentGuardOpenAI(
        ...     agentguard_url="http://localhost:8080",
        ...     agent_api_key="ag_xxx"
        ... )
        >>>
        >>> response = client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
    """

    def __init__(
        self,
        agentguard_url: Optional[str] = None,
        agent_api_key: Optional[str] = None,
        config: Optional[AgentGuardConfig] = None,
        **kwargs
    ):
        """
        Initialize AgentGuard OpenAI client.

        Args:
            agentguard_url: AgentGuard server URL
            agent_api_key: AgentGuard API key
            config: AgentGuardConfig object (alternative to individual params)
            **kwargs: Additional arguments passed to OpenAI client
        """
        # Load configuration
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

        # Create custom HTTP client with AgentGuard transport
        http_client = httpx.Client(
            transport=AgentGuardTransport(
                agentguard_url=self.config.agentguard_url,
                agent_api_key=self.config.agent_api_key
            )
        )

        # Initialize OpenAI client with custom settings
        super().__init__(
            api_key=self.config.agent_api_key,
            base_url=f"{self.config.agentguard_url}/proxy/v1",
            http_client=http_client,
            **kwargs
        )
