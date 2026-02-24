"""Webhook server for receiving AgentGuard approval notifications"""

import hmac
import hashlib
import threading
from typing import Dict, Callable, Optional
from flask import Flask, request, jsonify


class WebhookServer:
    """
    Lightweight webhook server for receiving AgentGuard notifications.

    This server runs in a background thread and handles incoming webhook
    requests from AgentGuard, particularly for approval status changes.

    Example:
        >>> from agentguard import WebhookServer
        >>> import threading
        >>>
        >>> # Create and start webhook server
        >>> webhook_server = WebhookServer(port=5000, secret="your-secret")
        >>> webhook_thread = threading.Thread(
        ...     target=webhook_server.start,
        ...     daemon=True
        ... )
        >>> webhook_thread.start()
        >>>
        >>> # Register callback for approval
        >>> def on_approval(data):
        ...     print(f"Approval status: {data['status']}")
        >>>
        >>> webhook_server.register_callback("approval-123", on_approval)
    """

    def __init__(
        self,
        port: int = 5000,
        secret: Optional[str] = None,
        host: str = "0.0.0.0"
    ):
        """
        Initialize webhook server.

        Args:
            port: Port to listen on
            secret: Secret for HMAC signature verification
            host: Host to bind to
        """
        self.port = port
        self.secret = secret
        self.host = host
        self.app = Flask(__name__)
        self.approval_callbacks: Dict[str, Callable] = {}
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/agentguard/webhook', methods=['POST'])
        def handle_webhook():
            """Handle incoming webhook requests"""
            try:
                # Verify signature if secret is configured
                if self.secret:
                    signature = request.headers.get('X-AgentGuard-Signature', '')
                    payload = request.get_data()

                    if not self._verify_signature(payload, signature):
                        return jsonify({'error': 'Invalid signature'}), 401

                # Parse webhook data
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'Invalid JSON'}), 400

                # Extract approval ID
                approval_id = data.get('approvalId') or data.get('approval_id')
                if not approval_id:
                    return jsonify({'error': 'Missing approval ID'}), 400

                # Trigger callback if registered
                if approval_id in self.approval_callbacks:
                    callback = self.approval_callbacks[approval_id]
                    try:
                        callback(data)
                    except Exception as e:
                        print(f"Error in webhook callback: {e}")
                    finally:
                        # Remove callback after execution
                        del self.approval_callbacks[approval_id]

                return jsonify({'received': True}), 200

            except Exception as e:
                print(f"Error handling webhook: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({'status': 'ok'}), 200

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify HMAC signature.

        Args:
            payload: Request payload
            signature: Signature from header

        Returns:
            True if signature is valid
        """
        if not self.secret:
            return True

        try:
            # Remove 'sha256=' prefix if present
            if signature.startswith('sha256='):
                signature = signature[7:]

            # Calculate expected signature
            expected = hmac.new(
                self.secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            # Compare signatures
            return hmac.compare_digest(expected, signature)

        except Exception as e:
            print(f"Error verifying signature: {e}")
            return False

    def register_callback(self, approval_id: str, callback: Callable) -> None:
        """
        Register callback for approval notification.

        Args:
            approval_id: Approval request ID
            callback: Function to call when webhook is received
        """
        self.approval_callbacks[approval_id] = callback

    def unregister_callback(self, approval_id: str) -> None:
        """
        Unregister callback for approval.

        Args:
            approval_id: Approval request ID
        """
        if approval_id in self.approval_callbacks:
            del self.approval_callbacks[approval_id]

    def start(self) -> None:
        """
        Start the webhook server.

        This method blocks until the server is stopped.
        Run it in a separate thread for non-blocking operation.
        """
        print(f"Starting webhook server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, threaded=True)

    def wait_for_approval(
        self,
        approval_id: str,
        timeout: int = 300
    ) -> Optional[Dict]:
        """
        Wait for approval webhook with timeout.

        Args:
            approval_id: Approval request ID
            timeout: Timeout in seconds

        Returns:
            Webhook data or None if timeout
        """
        result = {}
        event = threading.Event()

        def callback(data):
            nonlocal result
            result = data
            event.set()

        self.register_callback(approval_id, callback)

        # Wait for event with timeout
        event.wait(timeout=timeout)

        # Clean up if timeout
        if not event.is_set():
            self.unregister_callback(approval_id)
            return None

        return result
