#!/usr/bin/env python3
"""
Script to replace 'url:' with 'slug:' in frontmatter of MDX files.
Processes all MDX files in root directory and subdirectories.
"""

import os
import re
from pathlib import Path


def process_mdx_file(file_path):
    """
    Process a single MDX file to replace 'url:' with 'slug:' in frontmatter.

    Args:
        file_path (Path): Path to the MDX file

    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Check if file has frontmatter (starts with ---)
        if not content.startswith('---'):
            return False

        # Find the end of frontmatter
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            return False

        # Extract frontmatter and body
        frontmatter = content[3:frontmatter_end]
        body = content[frontmatter_end:]

        # Replace 'url:' with 'slug:' in frontmatter
        # Use word boundary to ensure we only match 'url:' as a key
        original_frontmatter = frontmatter
        frontmatter = re.sub(r'\burl:', 'slug:', frontmatter)

        # Check if any changes were made
        if frontmatter == original_frontmatter:
            return False

        # Reconstruct the file content
        new_content = '---' + frontmatter + body

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_and_process_mdx_files(root_dir='.'):
    """
    Find all MDX files in root directory and subdirectories and process them.

    Args:
        root_dir (str): Root directory to search from (default: current directory)
    """
    root_path = Path(root_dir)
    modified_files = []
    total_files = 0

    # Find all .mdx files recursively
    for mdx_file in root_path.rglob('*.mdx'):
        total_files += 1
        print(f"Processing: {mdx_file}")

        if process_mdx_file(mdx_file):
            modified_files.append(mdx_file)
            print(f"  ✓ Modified: replaced 'url:' with 'slug:'")
        else:
            print(f"  - No changes needed")

    # Print summary
    print(f"\n--- Summary ---")
    print(f"Total MDX files processed: {total_files}")
    print(f"Files modified: {len(modified_files)}")

    if modified_files:
        print(f"\nModified files:")
        for file_path in modified_files:
            print(f"  - {file_path}")


if __name__ == "__main__":
    print("Starting MDX frontmatter processing...")
    print("Replacing 'url:' with 'slug:' in frontmatter of all MDX files")
    print("-" * 60)

    find_and_process_mdx_files()

    print("\nProcessing complete!")