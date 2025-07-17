#!/usr/bin/env python3
"""
Generate TypeScript SDK reference documentation using typedoc.

This script generates TypeScript documentation in Markdown format
suitable for Mintlify.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_node_dependencies():
    """Check if Node.js and pnpm are available."""
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✓ Node.js is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Node.js is not installed", file=sys.stderr)
        sys.exit(1)
    
    try:
        subprocess.run(["pnpm", "--version"], check=True, capture_output=True)
        print("✓ pnpm is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing pnpm...")
        try:
            subprocess.run(["npm", "install", "-g", "pnpm"], check=True)
            print("✓ pnpm installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install pnpm: {e}", file=sys.stderr)
            sys.exit(1)


def setup_typescript_project(weave_source):
    """Set up the TypeScript project and install dependencies."""
    sdk_path = Path(weave_source) / "sdks" / "node"
    
    if not sdk_path.exists():
        print(f"TypeScript SDK not found at {sdk_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Setting up TypeScript project at {sdk_path}")
    
    # Install dependencies
    os.chdir(sdk_path)
    try:
        print("Installing dependencies...")
        subprocess.run(["pnpm", "install"], check=True)
        
        # Install typedoc and markdown plugin
        print("Installing typedoc...")
        subprocess.run([
            "pnpm", "add", "-D",
            "typedoc",
            "typedoc-plugin-markdown"
        ], check=True)
        
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}", file=sys.stderr)
        sys.exit(1)
    
    return sdk_path


def generate_typedoc_config(sdk_path, output_path):
    """Generate typedoc configuration."""
    config = {
        "entryPoints": ["src/index.ts"],
        "out": str(output_path),
        "plugin": ["typedoc-plugin-markdown"],
        "readme": "none",
        "hideBreadcrumbs": True,
        "hideInPageTOC": True,
        "disableSources": True,
        "excludePrivate": True,
        "excludeProtected": True,
        "excludeInternal": True,
        "githubPages": False,
        "cleanOutputDir": True
    }
    
    config_path = sdk_path / "typedoc.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_path


def run_typedoc(sdk_path, output_path):
    """Run typedoc to generate documentation."""
    print(f"Generating TypeScript documentation to {output_path}...")
    
    os.chdir(sdk_path)
    try:
        subprocess.run([
            "pnpm", "exec", "typedoc"
        ], check=True)
        print("✓ TypeScript documentation generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate documentation: {e}", file=sys.stderr)
        sys.exit(1)


def post_process_typescript_docs(docs_dir):
    """Post-process the generated TypeScript documentation for Mintlify."""
    docs_path = Path(docs_dir)
    
    # Process all markdown files
    for md_file in docs_path.rglob("*.md"):
        content = md_file.read_text()
        
        # Extract title from the first heading
        lines = content.split('\n')
        title = md_file.stem
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Add Mintlify frontmatter
        frontmatter = f"""---
title: '{title}'
description: 'TypeScript SDK reference for {title}'
---

"""
        
        # Only add frontmatter if not already present
        if not content.startswith("---"):
            content = frontmatter + content
        
        # Clean up typedoc artifacts
        content = content.replace('**`', '`')
        content = content.replace('`**', '`')
        
        # Change .md extension to .mdx
        mdx_file = md_file.with_suffix('.mdx')
        mdx_file.write_text(content)
        
        # Remove original .md file
        md_file.unlink()
        
        print(f"  ✓ Processed {md_file.name} → {mdx_file.name}")


def main():
    """Main function."""
    # Check Node.js dependencies
    check_node_dependencies()
    
    # Get Weave source path
    weave_source = os.environ.get("WEAVE_SOURCE_PATH", "../weave-source")
    
    if not Path(weave_source).exists():
        print(f"Weave source not found at {weave_source}")
        print("Please set WEAVE_SOURCE_PATH environment variable")
        sys.exit(1)
    
    # Setup TypeScript project
    sdk_path = setup_typescript_project(weave_source)
    
    # Output directory
    current_dir = Path.cwd()
    output_dir = current_dir / "reference" / "typescript-sdk" / "weave"
    
    # Clean existing docs
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    # Generate typedoc config
    generate_typedoc_config(sdk_path, output_dir)
    
    # Run typedoc
    run_typedoc(sdk_path, output_dir)
    
    # Change back to original directory
    os.chdir(current_dir)
    
    # Post-process for Mintlify
    print("\nPost-processing documentation for Mintlify...")
    post_process_typescript_docs(output_dir)
    
    print("\nTypeScript SDK documentation generation complete!")


if __name__ == "__main__":
    main() 