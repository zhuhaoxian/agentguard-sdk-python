"""Requests library interceptor for AgentGuard"""

import requests
import json
from functools import wraps
from typing import Optional, List, Pattern
import re


# Store original request function
_original_request = requests.request


class RequestsInterceptor:
    """Interceptor for requests library to route through AgentGuard"""

    def __init__(
        self,
        agentguard_url: str,
        agent_api_key: str,
        intercept_patterns: Optional[List[str]] = None
    ):
        """
        Initialize requests interceptor.

        Args:
            agentguard_url: AgentGuard server URL
            agent_api_key: AgentGuard API key
            intercept_patterns: List of URL patterns to intercept (regex)
        """
        self.agentguard_url = agentguard_url.rstrip('/')
        self.agent_api_key = agent_api_key
        self.intercept_patterns = [
            re.compile(pattern) for pattern in (intercept_patterns or [])
        ]

    def should_intercept(self, url: str) -> bool:
        """
        Check if URL should be intercepted.

        Args:
            url: Request URL

        Returns:
            True if URL should be intercepted
        """
        # If no patterns specified, intercept all
        if not self.intercept_patterns:
            return True

        # Check if URL matches any pattern
        return any(pattern.search(url) for pattern in self.intercept_patterns)

    def intercept_request(self, method: str, url: str, **kwargs):
        """
        Intercept and route request through AgentGuard.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Request arguments

        Returns:
            Response from AgentGuard proxy
        """
        if not self.should_intercept(url):
            return _original_request(method, url, **kwargs)

        # Construct proxy request body
        proxy_body = {
            "apiKey": self.agent_api_key,
            "targetUrl": url,
            "method": method.upper(),
            "headers": kwargs.get('headers', {}),
        }

        # Add request body if present
        if 'json' in kwargs:
            proxy_body['body'] = kwargs['json']
        elif 'data' in kwargs:
            try:
                proxy_body['body'] = json.loads(kwargs['data'])
            except (json.JSONDecodeError, TypeError):
                proxy_body['body'] = kwargs['data']

        # Send request to AgentGuard proxy
        return _original_request(
            'POST',
            f"{self.agentguard_url}/proxy/v1/api",
            json=proxy_body,
            headers={'Content-Type': 'application/json'}
        )


# Global interceptor instance
_interceptor: Optional[RequestsInterceptor] = None


def enable_agentguard(
    agentguard_url: str,
    agent_api_key: str,
    intercept_patterns: Optional[List[str]] = None
) -> None:
    """
    Enable global AgentGuard interception for requests library.

    This function monkey-patches the requests.request function to route
    matching requests through AgentGuard proxy.

    Example:
        >>> from agentguard import enable_agentguard
        >>>
        >>> enable_agentguard(
        ...     agentguard_url="http://localhost:8080",
        ...     agent_api_key="ag_xxx",
        ...     intercept_patterns=[r"https://api\.example\.com/.*"]
        ... )
        >>>
        >>> # Now all matching requests will go through AgentGuard
        >>> import requests
        >>> response = requests.get("https://api.example.com/data")

    Args:
        agentguard_url: AgentGuard server URL
        agent_api_key: AgentGuard API key
        intercept_patterns: List of URL patterns to intercept (regex)
    """
    global _interceptor

    _interceptor = RequestsInterceptor(
        agentguard_url=agentguard_url,
        agent_api_key=agent_api_key,
        intercept_patterns=intercept_patterns
    )

    @wraps(_original_request)
    def wrapped_request(method, url, **kwargs):
        return _interceptor.intercept_request(method, url, **kwargs)

    requests.request = wrapped_request


def disable_agentguard() -> None:
    """
    Disable AgentGuard interception and restore original requests behavior.
    """
    global _interceptor
    _interceptor = None
    requests.request = _original_request
