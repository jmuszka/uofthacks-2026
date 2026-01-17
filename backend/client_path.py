
import logging
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from ucp_sdk.models.discovery.profile_schema import UcpDiscoveryProfile

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(follow_redirects=True)

    def fetch_manifest(self) -> UcpDiscoveryProfile:
        """Fetches the UCP manifest from the .well-known endpoint."""
        url = urljoin(self.base_url, "/.well-known/ucp")
        logger.info(f"Fetching manifest from: {url}")
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            # Use SDK to validate/parse response
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
        
        # manifest.ucp is DiscoveryProfile
        # manifest.ucp.capabilities is List[Discovery]
        if manifest.ucp.capabilities:
            for cap in manifest.ucp.capabilities:
                if cap.name:
                    capabilities_list.append(cap.name)
            
        return capabilities_list

    def identify_protocol(self, manifest: UcpDiscoveryProfile) -> Dict[str, Any]:
        """Identifies protocols from the manifest model."""
        protocol_info = {}
        
        # manifest.ucp.services is Services, which is a RootModel[dict[str, UcpService]]
        if manifest.ucp.services:
            for svc_name, svc_data in manifest.ucp.services.root.items():
                # svc_data is UcpService
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
            # PaymentHandlerResponse model to dict, mode='json' converts AnyUrl to str
            handlers = [h.model_dump(mode='json') for h in manifest.payment.handlers]
        
        return {
            "handlers": handlers,
        }
