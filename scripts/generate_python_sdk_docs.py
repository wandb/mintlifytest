#!/usr/bin/env python3
"""
Generate Python SDK reference documentation using lazydocs.

This simplified version generates clean markdown documentation
suitable for Mintlify without custom processing that might
introduce security issues.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def install_weave_from_source(weave_path):
    """Install Weave from source for documentation generation."""
    print(f"Installing Weave from source: {weave_path}")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", weave_path],
            check=True,
            capture_output=True,
            text=True
        )
        print("Weave installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Weave: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def generate_docs_with_lazydocs(output_dir):
    """Generate documentation using lazydocs."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Key modules to document
    modules_to_document = [
        "weave",
        "weave.trace.op",
        "weave.trace.weave_client",
        "weave.trace.util",
        "weave.trace_server.trace_server_interface",
    ]
    
    for module in modules_to_document:
        print(f"Generating documentation for {module}...")
        
        # Use lazydocs command line interface for cleaner output
        cmd = [
            "lazydocs",
            "--output-path", str(output_path),
            "--overview-file", "",  # No overview file
            "--src-base-url", "https://github.com/wandb/weave/blob/master",
            module
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  ✓ Generated docs for {module}")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Error generating docs for {module}: {e.stderr}")


def post_process_docs(docs_dir):
    """Post-process the generated documentation for Mintlify."""
    docs_path = Path(docs_dir)
    
    for md_file in docs_path.rglob("*.md"):
        content = md_file.read_text()
        
        # Add Mintlify frontmatter
        module_name = md_file.stem
        if module_name == "README":
            module_name = md_file.parent.name
        
        frontmatter = f"""---
title: '{module_name}'
description: 'Python SDK reference for {module_name}'
---

"""
        
        # Only add frontmatter if not already present
        if not content.startswith("---"):
            content = frontmatter + content
        
        # Change .md extension to .mdx
        mdx_file = md_file.with_suffix('.mdx')
        mdx_file.write_text(content)
        
        # Remove original .md file
        md_file.unlink()
        
        print(f"  ✓ Processed {md_file.name} → {mdx_file.name}")


def main():
    """Main function."""
    # Check if we're in the Weave repo or need to use a separate source
    weave_source = os.environ.get("WEAVE_SOURCE_PATH", "../weave-source")
    
    if not Path(weave_source).exists():
        print(f"Weave source not found at {weave_source}")
        print("Please set WEAVE_SOURCE_PATH environment variable or ensure weave-source exists")
        sys.exit(1)
    
    # Install Weave from source
    install_weave_from_source(weave_source)
    
    # Generate documentation
    output_dir = "reference/python-sdk/weave"
    print(f"\nGenerating Python SDK documentation to {output_dir}...")
    
    # Clean existing docs
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)
    
    generate_docs_with_lazydocs(output_dir)
    
    # Post-process for Mintlify
    print("\nPost-processing documentation for Mintlify...")
    post_process_docs(output_dir)
    
    print("\nPython SDK documentation generation complete!")


if __name__ == "__main__":
    main() 