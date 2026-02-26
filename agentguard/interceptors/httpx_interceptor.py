"""HTTPX transport interceptor for AgentGuard"""

import httpx
import json
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
        timeout: float = 600.0,
        *args,
        **kwargs
    ):
        """
        Initialize AgentGuard transport.

        Args:
            agentguard_url: AgentGuard server URL
            agent_api_key: AgentGuard API key
            timeout: Request timeout in seconds (default: 600s, same as OpenAI SDK)
        """
        super().__init__(*args, **kwargs)
        self.agentguard_url = agentguard_url.rstrip('/')
        self.agent_api_key = agent_api_key
        self.timeout = int(timeout)  # 转换为整数（秒）

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """
        Handle HTTP request by routing through AgentGuard.

        Args:
            request: Original HTTP request

        Returns:
            HTTP response from AgentGuard proxy (unwrapped to standard OpenAI format)
        """
        # Store original URL and request for reference
        original_url = str(request.url)
        original_request = request

        # Parse request body and add timeout parameter
        if request.content:
            try:
                body = json.loads(request.content)
                # Add timeout to request body for AgentGuard backend
                body['timeout'] = self.timeout
                # Create new request with updated content
                new_content = json.dumps(body).encode('utf-8')

                # Copy headers, remove Content-Length to avoid conflicts
                new_headers = {}
                for key, value in request.headers.items():
                    if key.lower() != 'content-length':
                        new_headers[key] = value

                # Add/update required headers (keep existing Authorization from OpenAI SDK)
                new_headers["X-Original-URL"] = original_url
                new_headers["Content-Length"] = str(len(new_content))
                new_headers["Content-Type"] = "application/json"

                # Create a new request with updated content and headers
                request = httpx.Request(
                    method=request.method,
                    url=f"{self.agentguard_url}/proxy/v1/chat/completions",
                    headers=new_headers,
                    content=new_content
                )
            except (json.JSONDecodeError, KeyError):
                # If parsing fails, continue without adding timeout
                request.url = httpx.URL(f"{self.agentguard_url}/proxy/v1/chat/completions")
                request.headers["X-Original-URL"] = original_url
        else:
            # No content, just update URL and headers
            request.url = httpx.URL(f"{self.agentguard_url}/proxy/v1/chat/completions")
            request.headers["X-Original-URL"] = original_url

        # Execute the request through parent transport
        response = super().handle_request(request)

        # Unwrap AgentGuard response format to standard OpenAI format
        response = self._unwrap_agentguard_response(response, original_request)

        return response

    def _unwrap_agentguard_response(self, response: httpx.Response, original_request: httpx.Request) -> httpx.Response:
        """
        Unwrap AgentGuard response format to standard OpenAI format.

        AgentGuard wraps responses in: {"code": 200, "data": {"response": {...}}}
        This method extracts the actual OpenAI response from data.response

        For streaming responses (text/event-stream), returns the response as-is
        to preserve streaming behavior.

        Args:
            response: AgentGuard wrapped response
            original_request: Original request object

        Returns:
            Unwrapped response in standard OpenAI format
        """
        try:
            # Check if this is a streaming response
            content_type = response.headers.get('content-type', '').lower()
            if 'text/event-stream' in content_type:
                # For streaming responses, return as-is to preserve streaming
                return response

            # For non-streaming responses, unwrap the AgentGuard format
            # Read response content if not already read
            if not hasattr(response, '_content'):
                response.read()

            # Parse response body
            body = json.loads(response.content)

            # Check if this is an AgentGuard wrapped response
            if isinstance(body, dict) and 'data' in body and 'response' in body['data']:
                # Extract the actual OpenAI response
                actual_response = body['data']['response']

                # Create new response with unwrapped content
                unwrapped_response = httpx.Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    content=json.dumps(actual_response).encode('utf-8')
                )
                # Set the request manually
                unwrapped_response._request = original_request

                return unwrapped_response

            # If not wrapped, return as-is
            return response

        except (json.JSONDecodeError, KeyError, TypeError):
            # If parsing fails, return original response
            return response

