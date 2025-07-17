#!/usr/bin/env python3
"""
Download the Weave Service API OpenAPI specification.

This script fetches the OpenAPI spec from the Weave service and saves it
in a format that Mintlify can directly consume, eliminating the need for
custom processing.
"""

import json
import requests
import sys
from pathlib import Path


def download_openapi_spec():
    """Download the OpenAPI spec from Weave service."""
    url = "https://trace.wandb.ai/openapi.json"
    
    print(f"Downloading OpenAPI spec from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error downloading OpenAPI spec: {e}", file=sys.stderr)
        sys.exit(1)


def update_server_url(spec):
    """Update the server URL to the production endpoint."""
    if "servers" not in spec or not spec["servers"]:
        spec["servers"] = []
    
    # Ensure the production server is listed
    spec["servers"] = [{"url": "https://trace.wandb.ai"}]
    return spec


def save_openapi_spec(spec, output_path):
    """Save the OpenAPI spec to a file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(spec, f, indent=2)
    
    print(f"OpenAPI spec saved to {output_path}")


def main():
    """Main function."""
    # Download the spec
    spec = download_openapi_spec()
    
    # Update server URL
    spec = update_server_url(spec)
    
    # Update the title and description for better presentation
    if "info" in spec:
        spec["info"]["title"] = "Weave Service API"
        spec["info"]["description"] = "REST API endpoints for the Weave service"
    
    # Save to the appropriate location for Mintlify
    output_path = "openapi.json"
    save_openapi_spec(spec, output_path)
    
    print("Service API spec generation complete!")


if __name__ == "__main__":
    main() 