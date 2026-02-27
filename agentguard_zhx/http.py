"""AgentGuard HTTP client for proxying business API calls

This module provides a simple HTTP client that automatically routes all requests
through AgentGuard's business API proxy for governance and monitoring.
"""

import httpx
from typing import Optional, Dict, Any, Union
import json

from .config import AgentGuardConfig


class AgentGuardHTTP:
    """
    HTTP client that routes all requests through AgentGuard business API proxy.

    This client provides a simple interface for making HTTP requests that are
    automatically proxied through AgentGuard for governance, monitoring, and approval.

    Example:
        >>> from agentguard import AgentGuardHTTP
        >>>
        >>> # Initialize client
        >>> http = AgentGuardHTTP(
        ...     agentguard_url="http://localhost:8080",
        ...     agent_api_key="ag_xxx"
        ... )
        >>>
        >>> # Make requests - they're automatically proxied through AgentGuard
        >>> response = http.post(
        ...     "https://api.sendgrid.com/v3/mail/send",
        ...     json={"to": "user@example.com", "subject": "Hello"}
        ... )
        >>>
        >>> # All standard HTTP methods are supported
        >>> response = http.get("https://api.example.com/users")
        >>> response = http.put("https://api.example.com/users/1", json={...})
        >>> response = http.delete("https://api.example.com/users/1")
    """

    def __init__(
        self,
        agentguard_url: Optional[str] = None,
        agent_api_key: Optional[str] = None,
        config: Optional[AgentGuardConfig] = None,
        timeout: float = 30.0
    ):
        """
        Initialize AgentGuard HTTP client.

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
        self.proxy_url = f"{self.config.agentguard_url}/proxy/v1/api"

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request through AgentGuard proxy.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Target URL to call
            headers: Optional request headers
            json: Optional JSON body
            data: Optional raw body data
            params: Optional query parameters

        Returns:
            Response data as dictionary

        Raises:
            Exception: If the request fails
        """
        # Construct proxy request
        proxy_request = {
            "apiKey": self.config.agent_api_key,
            "targetUrl": url,
            "method": method.upper(),
            "headers": headers or {"Content-Type": "application/json"}
        }

        # Add query parameters to URL if provided
        if params:
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            proxy_request["targetUrl"] = f"{url}?{query_string}"

        # Add body if provided
        if json is not None:
            proxy_request["body"] = json
        elif data is not None:
            proxy_request["body"] = data

        # Send request to AgentGuard proxy
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self.proxy_url,
                json=proxy_request
            )
            response.raise_for_status()

            # Parse AgentGuard response
            result = response.json()

            # Check if request was successful
            if result.get("code") == 200 and "data" in result:
                data = result["data"]

                # Check if operation requires approval
                if data.get("status") == "PENDING_APPROVAL":
                    return {
                        "status": "PENDING_APPROVAL",
                        "approvalRequestId": data.get("approvalRequestId"),
                        "message": "This operation requires approval"
                    }

                # Return successful response
                if data.get("status") == "SUCCESS" and "response" in data:
                    return data["response"]

                return data

            # Return error response
            return {
                "error": result.get("message", "Unknown error"),
                "code": result.get("code")
            }

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self.request("PATCH", url, **kwargs)
