"""HTTPX transport interceptor for AgentGuard"""

import httpx
from typing import Optional


class AgentGuardTransport(httpx.HTTPTransport):
    """
    Custom HTTPX transport that routes requests through AgentGuard proxy.

    This transport intercepts all HTTP requests and modifies them to go through
    the AgentGuard proxy server for governance and monitoring.
    """

    def __init__(
        self,
        agentguard_url: str,
        agent_api_key: str,
        *args,
        **kwargs
    ):
        """
        Initialize AgentGuard transport.

        Args:
            agentguard_url: AgentGuard server URL
            agent_api_key: AgentGuard API key
        """
        super().__init__(*args, **kwargs)
        self.agentguard_url = agentguard_url.rstrip('/')
        self.agent_api_key = agent_api_key

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """
        Handle HTTP request by routing through AgentGuard.

        Args:
            request: Original HTTP request

        Returns:
            HTTP response from AgentGuard proxy
        """
        # Store original URL for reference
        original_url = str(request.url)

        # Route to AgentGuard proxy
        # The proxy endpoint will handle the actual LLM API call
        request.url = httpx.URL(f"{self.agentguard_url}/proxy/v1/chat/completions")

        # Add AgentGuard authentication header
        request.headers["Authorization"] = f"Bearer {self.agent_api_key}"

        # Add original target URL as header (if needed for logging)
        request.headers["X-Original-URL"] = original_url

        # Execute the request through parent transport
        return super().handle_request(request)
