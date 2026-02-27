"""AgentGuard OpenAI client wrapper"""

from typing import Optional
import httpx
from openai import OpenAI

from .config import AgentGuardConfig
from .interceptors.httpx_interceptor import AgentGuardTransport
from .approvals import ApprovalClient


class AgentGuardOpenAI(OpenAI):
    """
    AgentGuard wrapper for OpenAI client with integrated approval management.

    This class extends the OpenAI client to route all requests through AgentGuard
    for governance, monitoring, and cost tracking. It also provides integrated
    approval management via the `approvals` property.

    Example:
        >>> from agentguard import AgentGuardOpenAI
        >>>
        >>> client = AgentGuardOpenAI(
        ...     agentguard_url="http://localhost:8080",
        ...     agent_api_key="ag_xxx"
        ... )
        >>>
        >>> # Use exactly like OpenAI client
        >>> response = client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
        >>>
        >>> # Access integrated approval management
        >>> status = client.approvals.get_status("approval_id")
        >>> client.approvals.submit_reason("approval_id", "reason")
    """

    def __init__(
        self,
        agentguard_url: Optional[str] = None,
        agent_api_key: Optional[str] = None,
        config: Optional[AgentGuardConfig] = None,
        timeout: float = 600.0,  # 默认 600 秒，与 OpenAI SDK 保持一致
        **kwargs
    ):
        """
        Initialize AgentGuard OpenAI client.

        Args:
            agentguard_url: AgentGuard server URL
            agent_api_key: AgentGuard API key
            config: AgentGuardConfig object (alternative to individual params)
            timeout: Request timeout in seconds (default: 600s, same as OpenAI SDK)
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

        # Create custom HTTP client with AgentGuard transport and timeout
        # 使用与 OpenAI SDK 相同的超时配置：
        # - connect: 5s (连接超时)
        # - read: 600s (读取超时，适用于流式传输)
        # - write: 600s (写入超时)
        # - pool: 600s (连接池超时)
        timeout_config = httpx.Timeout(
            connect=5.0,
            read=timeout,
            write=timeout,
            pool=timeout
        )

        http_client = httpx.Client(
            transport=AgentGuardTransport(
                agentguard_url=self.config.agentguard_url,
                agent_api_key=self.config.agent_api_key,
                timeout=timeout  # 传递超时参数到 transport
            ),
            timeout=timeout_config  # 使用详细的超时配置
        )

        # Initialize OpenAI client with custom settings
        super().__init__(
            api_key=self.config.agent_api_key,
            base_url=f"{self.config.agentguard_url}/proxy/v1",
            http_client=http_client,
            **kwargs
        )

        # Initialize integrated approval client
        self._approvals = ApprovalClient(config=self.config)

        # Initialize tools helper for automatic tool merging
        from .tools import AgentGuardTools
        self._tools_helper = AgentGuardTools(self)

    @property
    def approvals(self) -> ApprovalClient:
        """
        Access approval management functionality.

        Returns:
            ApprovalClient instance for managing approvals

        Example:
            >>> client = AgentGuardOpenAI(...)
            >>> # Query approval status
            >>> status = client.approvals.get_status("approval_id")
            >>> if status.is_approved:
            ...     print("Approved:", status.execution_result)
            >>>
            >>> # Submit approval reason
            >>> client.approvals.submit_reason("approval_id", "Need to delete test data")
        """
        return self._approvals

    def merge_tools(self, business_tools: list) -> list:
        """
        Merge business tools with AgentGuard approval tools.

        This is a convenience method that automatically adds AgentGuard's
        approval management tools to your business tools list.

        Args:
            business_tools: List of business tool definitions

        Returns:
            Merged list of tools (business + AgentGuard approval tools)

        Example:
            >>> client = AgentGuardOpenAI(...)
            >>>
            >>> # Define your business tools
            >>> business_tools = [
            ...     {
            ...         "type": "function",
            ...         "function": {
            ...             "name": "get_weather",
            ...             "description": "Get weather info",
            ...             "parameters": {...}
            ...         }
            ...     }
            ... ]
            >>>
            >>> # Automatically merge with AgentGuard tools
            >>> all_tools = client.merge_tools(business_tools)
            >>>
            >>> # Use in chat completion
            >>> response = client.chat.completions.create(
            ...     model="gpt-4",
            ...     messages=[...],
            ...     tools=all_tools  # Includes approval tools automatically
            ... )
        """
        return business_tools + self._tools_helper.get_tool_definitions()

    def get_function_map(self, business_functions: dict) -> dict:
        """
        Merge business functions with AgentGuard approval functions.

        This is a convenience method that automatically adds AgentGuard's
        approval management functions to your business functions dictionary.

        Args:
            business_functions: Dictionary of business function implementations

        Returns:
            Merged dictionary of functions (business + AgentGuard approval functions)

        Example:
            >>> client = AgentGuardOpenAI(...)
            >>>
            >>> # Define your business functions
            >>> business_functions = {
            ...     "get_weather": get_weather_func,
            ...     "send_email": send_email_func
            ... }
            >>>
            >>> # Automatically merge with AgentGuard functions
            >>> all_functions = client.get_function_map(business_functions)
            >>>
            >>> # Execute tool calls
            >>> for tool_call in message.tool_calls:
            ...     func = all_functions[tool_call.function.name]
            ...     result = func(**args)
        """
        return {
            **business_functions,
            **self._tools_helper.get_function_map()
        }
