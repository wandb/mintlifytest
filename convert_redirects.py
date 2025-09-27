#!/usr/bin/env python3
"""
Convert _redirects file to JSON format with source/destination objects.

Usage:
    python convert_redirects.py
"""

import json
from typing import List, Dict


def parse_redirects_file(filepath: str = "_redirects") -> List[Dict[str, str]]:
    """
    Parse the _redirects file and convert to JSON format.

    Args:
        filepath: Path to the _redirects file

    Returns:
        List of redirect objects with source and destination
    """
    redirects = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Split the line into parts
        parts = line.split()

        if len(parts) < 2:
            print(f"Warning: Line {line_num} has insufficient parts: {line}")
            continue

        source = parts[0]
        destination = parts[1]
        # status_code = parts[2] if len(parts) > 2 else "301"

        # Handle wildcards in the source and destination
        if '*' in source or ':splat' in destination:
            # Convert wildcard syntax to the appropriate format
            if source.endswith('*'):
                source = source[:-1] + ':slug*'
            elif source.endswith('_'):
                source = source[:-1] + '*'

            if ':splat' in destination:
                destination = destination.replace(':splat', ':slug*')

        redirects.append({
            "source": source,
            "destination": destination
        })

    return redirects


def save_redirects_json(redirects: List[Dict[str, str]], output_file: str = "redirects.json") -> None:
    """
    Save redirects to JSON file with proper formatting.

    Args:
        redirects: List of redirect objects
        output_file: Output JSON filename
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(redirects, f, indent=2, ensure_ascii=False)

    print(f"✅ Converted {len(redirects)} redirects to {output_file}")


def main():
    """Main function to convert _redirects to JSON format."""
    try:
        print("🔄 Converting _redirects file to JSON format...")

        # Parse the _redirects file
        redirects = parse_redirects_file()

        # Save to JSON
        save_redirects_json(redirects)

        print(f"📊 Total redirects converted: {len(redirects)}")

        # Show a few examples
        if redirects:
            print("\n📋 Sample redirects:")
            for i, redirect in enumerate(redirects[:3]):
                print(f"  {i + 1}. {redirect['source']} → {redirect['destination']}")

            if len(redirects) > 3:
                print(f"  ... and {len(redirects) - 3} more")

    except FileNotFoundError:
        print("❌ Error: _redirects file not found in current directory")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()