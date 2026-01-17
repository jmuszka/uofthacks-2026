import logging
import sys
import uuid
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
import json
import httpx
import base64
from dotenv import load_dotenv

from ucp_sdk.models.discovery.profile_schema import UcpDiscoveryProfile
from ucp_sdk.models.schemas.shopping import checkout_create_req
from ucp_sdk.models.schemas.shopping import payment_create_req
from ucp_sdk.models.schemas.shopping.types import buyer
from ucp_sdk.models.schemas.shopping.types import item_create_req
from ucp_sdk.models.schemas.shopping.types import line_item_create_req

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(follow_redirects=True)
        self.access_token = self.fetch_access_token()

    def fetch_access_token(self) -> str:
        """Fetches a Bearer token from Shopify using client credentials."""
        client_id = os.getenv("SHOPIFY_CLIENT_ID")
        client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            logger.error("SHOPIFY_CLIENT_ID or SHOPIFY_CLIENT_SECRET not found in environment.")
            sys.exit(1)

        url = "https://api.shopify.com/auth/access_token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            logger.info("Fetching access token from Shopify...")
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            token_data = response.json()
            return token_data["access_token"]
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch access token: {e}")
            if e.response:
                logger.error(f"Response Body: {e.response.text}")
            sys.exit(1)
        except KeyError:
            logger.error("Access token not found in response.")
            sys.exit(1)

    def _get_headers(self) -> Dict[str, str]:
        """Generate necessary headers for UCP requests."""
        return {
            "UCP-Agent": 'profile="https://danielkaminsky05.github.io/ucpagent/ucp.json", key-id="key-1"',
            "Authorization": f"Bearer {self.access_token}",
            "idempotency-key": str(uuid.uuid4()),
            "request-id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }

    def fetch_manifest(self) -> UcpDiscoveryProfile:
        """Fetches the UCP manifest from the .well-known endpoint."""
        url = urljoin(self.base_url, "/.well-known/ucp")
        logger.info(f"Fetching manifest from: {url}")
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return UcpDiscoveryProfile.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch manifest: {e}")
            sys.exit(1)
        except Exception as e:
             logger.error(f"Failed to parse manifest: {e}")
             sys.exit(1)

    def parse_capabilities(self, manifest: UcpDiscoveryProfile) -> List[str]:
        """Parses capabilities from the manifest model."""
        capabilities_list = []
        if manifest.ucp.capabilities:
            for cap in manifest.ucp.capabilities:
                if cap.name:
                    capabilities_list.append(cap.name)
        return capabilities_list

    def identify_protocol(self, manifest: UcpDiscoveryProfile) -> Dict[str, Any]:
        """Identifies protocols from the manifest model."""
        protocol_info = {}
        if manifest.ucp.services:
            for svc_name, svc_data in manifest.ucp.services.root.items():
                if svc_data.mcp:
                    protocol_info[svc_name] = {
                        "type": "MCP",
                        "endpoint": str(svc_data.mcp.endpoint) if svc_data.mcp.endpoint else None,
                        "schema": str(svc_data.mcp.schema_) if svc_data.mcp.schema_ else None
                    }
                elif svc_data.rest:
                     protocol_info[svc_name] = {
                        "type": "REST",
                        "endpoint": str(svc_data.rest.endpoint) if svc_data.rest.endpoint else None,
                        "schema": str(svc_data.rest.schema_) if svc_data.rest.schema_ else None
                    }
                else:
                     protocol_info[svc_name] = {
                        "type": "Unknown",
                    }
        return protocol_info

    def get_payment_info(self, manifest: UcpDiscoveryProfile) -> Dict[str, Any]:
        """Extracts payment handlers from the manifest model."""
        handlers = []
        if manifest.payment and manifest.payment.handlers:
            handlers = [h.model_dump(mode='json') for h in manifest.payment.handlers]
        return {
            "handlers": handlers,
        }

    def create_checkout(self, variant_id: str, quantity: int) -> Dict[str, Any]:
        """Creates a checkout session via MCP JSON-RPC."""
        # Endpoint found via discovery: /api/ucp/mcp
        url = urljoin(self.base_url, "/api/ucp/mcp")
        logger.info(f"Creating checkout at: {url}")
        
        # 1. Create Line Items
        item = item_create_req.ItemCreateRequest(id=variant_id)
        line_item = line_item_create_req.LineItemCreateRequest(
            quantity=quantity,
            item=item
        )

        # 2. Create Payment
        payment = payment_create_req.PaymentCreateRequest()

        # 3. Create Buyer
        buyer_info = buyer.Buyer(email="buyer@example.com")

        # 4. Create Checkout Request Payload (Inner Arguments)
        checkout_req = checkout_create_req.CheckoutCreateRequest(
            currency="USD",
            line_items=[line_item],
            payment=payment,
            buyer=buyer_info,
            _meta={
                "ucp": {
                    "profile": "https://danielkaminsky05.github.io/ucpagent/ucp.json"
                }
            }
        )
        
        args_payload = checkout_req.model_dump(mode='json', exclude_none=True)
        if "_meta" not in args_payload:
             args_payload["_meta"] = {
                "ucp": {
                    "profile": "https://danielkaminsky05.github.io/ucpagent/ucp.json"
                }
            }

        # 5. Wrap in JSON-RPC for MCP
        json_rpc_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "create_checkout",
                "arguments": args_payload
            }
        }

        try:
            # Add authentication/identification headers
            headers = self._get_headers()
            response = self.client.post(url, json=json_rpc_payload, headers=headers)
            response.raise_for_status()
            logger.info("JSON-RPC request sent successfully.")
            
            # Check for JSON-RPC error
            resp_json = response.json()
            if "error" in resp_json:
                logger.error(f"JSON-RPC Error: {resp_json['error']}")
                return resp_json
            
            return resp_json
        except httpx.HTTPError as e:
            logger.error(f"Failed to create checkout: {e}")
            if e.response:
                logger.error(f"Response Body: {e.response.text}")
            sys.exit(1)
