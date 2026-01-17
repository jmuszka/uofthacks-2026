
import argparse
import logging
import json
import sys
from client_path import UCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Test UCP Discovery and Checkout")
    parser.add_argument("--url", required=True, help="Base URL of the UCP Store")
    parser.add_argument("--variant-id", required=True, help="Product Variant ID")
    parser.add_argument("--quantity", type=int, default=1, help="Quantity to purchase")
    args = parser.parse_args()

    print(f"Testing against: {args.url}")
    print(f"Variant: {args.variant_id}, Qty: {args.quantity}")
    
    try:
        client = UCPClient(args.url)
        
        # Step 1: Discovery
        print("\n--- Step 1: Discovery ---")
        try:
            manifest = client.fetch_manifest()
            print("Manifest fetched successfully.")
            
            capabilities = client.parse_capabilities(manifest)
            print(f"Capabilities: {json.dumps(capabilities, indent=2)}")
            
            protocols = client.identify_protocol(manifest)
            print(f"Protocols: {json.dumps(protocols, indent=2)}")
            
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            print("Skipping to Checkout (might fail if discovery failed due to auth)...")

        # Step 2: Checkout
        print("\n--- Step 2: Create Checkout ---")
        try:
            response = client.create_checkout(args.variant_id, args.quantity)
            if "error" in response:
                 print("\n--- Checkout Failed ---")
                 print(json.dumps(response, indent=2))
            else:
                print("\n--- Checkout Created Successfully ---")
                print(json.dumps(response, indent=2))
        except Exception as e:
            logger.error(f"Checkout creation failed: {e}")

    except Exception as e:
        logger.error(f"Client initialization failed: {e}")

if __name__ == "__main__":
    main()
