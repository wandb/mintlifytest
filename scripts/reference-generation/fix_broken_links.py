#!/usr/bin/env python3
"""
Fix common broken links in the documentation.
"""

import os
import re
from pathlib import Path


def fix_links_in_file(file_path):
    """Fix common broken link patterns in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix links to reference docs that are missing /weave prefix
    content = re.sub(
        r'\[([^\]]+)\]\(/reference/(python-sdk|typescript-sdk|service-api)',
        r'[\1](/weave/reference/\2',
        content
    )
    
    # Fix links to quickstart pages
    content = re.sub(
        r'\(/quickstart-inference\)',
        '(/weave/quickstart-inference)',
        content
    )
    content = re.sub(
        r'\(/quickstart\)',
        '(/weave/quickstart)',
        content
    )
    
    # Fix links to tutorial pages
    content = re.sub(
        r'\(/tutorial-([\w-]+)\)',
        r'(/weave/tutorial-\1)',
        content
    )
    
    # Fix links to guides
    content = re.sub(
        r'\(/guides/',
        '(/weave/guides/',
        content
    )
    
    # Fix links to cookbooks
    content = re.sub(
        r'\(/cookbooks/',
        '(/weave/cookbooks/',
        content
    )
    
    # Fix image paths that are missing /weave prefix
    content = re.sub(
        r'!\[([^\]]*)\]\(/weave/images/',
        r'![\1](/images/',
        content
    )
    
    # Fix ./images/ paths
    content = re.sub(
        r'!\[([^\]]*)\]\(\./images/',
        r'![\1](/images/',
        content
    )
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False


def main():
    """Fix broken links in all MDX files."""
    # Find all MDX files in the weave directory
    weave_dir = Path('weave')
    mdx_files = list(weave_dir.rglob('*.mdx'))
    
    print(f"Found {len(mdx_files)} MDX files to check...")
    
    fixed_count = 0
    for mdx_file in mdx_files:
        if fix_links_in_file(mdx_file):
            print(f"  ✓ Fixed links in {mdx_file}")
            fixed_count += 1
    
    print(f"\n✓ Fixed links in {fixed_count} files")


if __name__ == "__main__":
    main()
