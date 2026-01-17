
import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UCPDiscovery:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(follow_redirects=True)

    def fetch_manifest(self) -> Dict[str, Any]:
        """Fetches the UCP manifest from the .well-known endpoint."""
        url = urljoin(self.base_url, "/.well-known/ucp")
        logger.info(f"Fetching manifest from: {url}")
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch manifest: {e}")
            sys.exit(1)

    def parse_capabilities(self, manifest: Dict[str, Any]) -> List[str]:
        """Parses capabilities to identify Authority, Service, and Capability."""
        capabilities_list = []
        ucp_section = manifest.get("ucp", {})
        
        # 1. Parse declared capabilities in 'capabilities' list if present
        raw_caps = ucp_section.get("capabilities", [])
        
        for cap in raw_caps:
            name = cap.get("name", "")
            if name:
                capabilities_list.append(name)
            
        return capabilities_list

    def identify_protocol(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Identifies if the store uses MCP or REST, and returns endpoint/schema."""
        services = manifest.get("ucp", {}).get("services", {})
        
        protocol_info = {}
        
        for svc_name, svc_data in services.items():
            # Check for MCP
            if "mcp" in svc_data:
                protocol_info[svc_name] = {
                    "type": "MCP",
                    "endpoint": svc_data["mcp"].get("endpoint"),
                    "schema": svc_data["mcp"].get("schema")
                }
            elif "rest" in svc_data:  # Hypothetical standard, or just absence of mcp
                 protocol_info[svc_name] = {
                    "type": "REST",
                     # ... extract rest details if they existed
                }
            else:
                 protocol_info[svc_name] = {
                    "type": "Unknown",
                    "data": svc_data
                }
        return protocol_info

    def get_payment_info(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts payment handlers."""
        payment_section = manifest.get("payment", {})
        handlers = payment_section.get("handlers", [])
        
        return {
            "handlers": handlers,
        }


