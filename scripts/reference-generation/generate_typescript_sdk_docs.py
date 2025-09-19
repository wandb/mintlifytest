#!/usr/bin/env python3
"""
Generate TypeScript SDK reference documentation for Mintlify.

This script generates TypeScript documentation using typedoc and converts
it to Mintlify's format.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def check_node_dependencies():
    """Check if Node.js and npm are available."""
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✓ Node.js is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Node.js is not installed", file=sys.stderr)
        print("  Please install Node.js 18+ from https://nodejs.org/")
        sys.exit(1)
    
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        print("✓ npm is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ npm is not installed", file=sys.stderr)
        sys.exit(1)


def download_weave_source(version="main"):
    """Download Weave source code for a specific version using shallow clone."""
    print(f"\nDownloading Weave source code (version: {version})...")
    
    # Handle "latest" by fetching the latest release tag
    if version == "latest":
        # Use git ls-remote to get latest tag without API calls
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--tags", "--sort=-v:refname", "https://github.com/wandb/weave.git"],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse the output to get the latest version tag
            for line in result.stdout.strip().split('\n'):
                if '\trefs/tags/' in line and not line.endswith('^{}'):
                    tag = line.split('\trefs/tags/')[-1]
                    if tag.startswith('v') and not 'dev' in tag and not 'rc' in tag:
                        version = tag
                        print(f"  Using latest release: {version}")
                        break
            else:
                print("  Warning: Could not determine latest release, using main branch")
                version = "main"
        except Exception as e:
            print(f"  Warning: Could not fetch latest release, using main branch: {e}")
            version = "main"
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    weave_dir = Path(temp_dir) / "weave"
    
    try:
        # Use shallow clone with single branch
        print(f"  Cloning Weave repository (shallow clone)...")
        clone_cmd = [
            "git", "clone",
            "--depth", "1",
            "--single-branch"
        ]
        
        # Add branch/tag specification
        if version != "main":
            clone_cmd.extend(["--branch", version])
        
        clone_cmd.extend([
            "https://github.com/wandb/weave.git",
            str(weave_dir)
        ])
        
        # Run the clone command
        subprocess.run(clone_cmd, check=True, capture_output=True, text=True)
        
        print(f"  ✓ Successfully cloned Weave {version} to {weave_dir}")
        
        return weave_dir
        
    except subprocess.CalledProcessError as e:
        print(f"Error cloning Weave repository: {e}", file=sys.stderr)
        if e.stderr:
            print(f"  stderr: {e.stderr}", file=sys.stderr)
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)
    except Exception as e:
        print(f"Error downloading Weave source: {e}", file=sys.stderr)
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)


def setup_typescript_project(weave_source):
    """Set up the TypeScript project and install dependencies."""
    sdk_path = Path(weave_source) / "sdks" / "node"
    
    if not sdk_path.exists():
        print(f"TypeScript SDK not found at {sdk_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nSetting up TypeScript project...")
    os.chdir(sdk_path)
    
    try:
        # Install dependencies
        print("  Installing dependencies...")
        subprocess.run(["npm", "install"], check=True)
        
        # Install typedoc and markdown plugin with compatible versions
        print("  Installing typedoc...")
        subprocess.run([
            "npm", "install", "--save-dev",
            "typedoc@0.25.13",
            "typedoc-plugin-markdown@3.17.1"
        ], check=True)
        
        print("  ✓ Dependencies installed")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}", file=sys.stderr)
        sys.exit(1)
    
    return sdk_path


def generate_typedoc(sdk_path, output_path):
    """Generate TypeScript documentation using typedoc."""
    print(f"\nGenerating TypeScript documentation...")
    
    # Create typedoc config
    config = {
        "entryPoints": ["src/index.ts"],
        "out": str(output_path),
        "plugin": ["typedoc-plugin-markdown"],
        "readme": "none",
        "githubPages": False,
        "excludePrivate": True,
        "excludeProtected": True,
        "excludeInternal": True,
        "disableSources": False,
        "cleanOutputDir": True
    }
    
    config_path = sdk_path / "typedoc.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        # Run typedoc
        subprocess.run(["npx", "typedoc"], check=True, cwd=sdk_path)
        print("  ✓ Documentation generated")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate documentation: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up config file
        if config_path.exists():
            config_path.unlink()


def convert_to_mintlify_format(docs_dir):
    """Convert TypeDoc markdown to Mintlify MDX format."""
    print(f"\nConverting to Mintlify format...")
    
    docs_path = Path(docs_dir)
    md_files = list(docs_path.rglob("*.md"))
    
    for md_file in md_files:
        content = md_file.read_text()
        
        # Skip if already has frontmatter
        if content.startswith("---"):
            continue
        
        # Extract title from content
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # Remove the title line if it exists (Mintlify uses frontmatter title)
        if title_match:
            content = content.replace(title_match.group(0), '', 1).strip()
        
        # Add Mintlify frontmatter
        frontmatter = f"""---
title: "{title}"
description: "TypeScript SDK reference"
---

"""
        content = frontmatter + content
        
        # Fix TypeDoc specific formatting
        # Convert **`code`** to just `code`
        content = re.sub(r'\*\*`([^`]+)`\*\*', r'`\1`', content)
        
        # Fix parameter tables
        content = re.sub(r'\|\s*:--\s*\|', '| --- |', content)
        
        # Fix internal links to have proper prefix
        # Convert relative links like [WeaveObject](../classes/WeaveObject.md) to absolute
        content = re.sub(
            r'\[([^\]]+)\]\(\.\./(classes|functions|interfaces|type-aliases)/([^)]+)\)',
            r'[\1](/weave/reference/typescript-sdk/weave/\2/\3)',
            content
        )
        
        # Also fix links that start with just the type folder
        content = re.sub(
            r'\[([^\]]+)\]\((classes|functions|interfaces|type-aliases)/([^)]+)\)',
            r'[\1](/weave/reference/typescript-sdk/weave/\2/\3)',
            content
        )
        
        # Remove .md extensions from links
        content = re.sub(r'\.md(#[^)]+)?\)', r'\1)', content)
        
        # Special handling for index files - they use direct links without ../ 
        if md_file.name == "README.md":
            # Fix links like [Dataset](classes/Dataset.md)
            content = re.sub(
                r'\[([^\]]+)\]\((?!http|/)([^/]+)/([^)]+)\)',
                r'[\1](/weave/reference/typescript-sdk/weave/\2/\3)',
                content
            )
        
        # Write as .mdx file
        mdx_file = md_file.with_suffix('.mdx')
        mdx_file.write_text(content)
        
        # Remove original .md file
        md_file.unlink()
        
        print(f"  ✓ Converted {md_file.name} → {mdx_file.name}")


def organize_for_mintlify(temp_output, final_output):
    """Organize the generated docs according to Mintlify structure."""
    print(f"\nOrganizing documentation structure...")
    
    temp_path = Path(temp_output)
    final_path = Path(final_output)
    
    # Clean existing docs
    if final_path.exists():
        shutil.rmtree(final_path)
    
    # Copy the generated docs to the final location
    shutil.copytree(temp_path, final_path)
    
    # Rename README.mdx to index.mdx if it exists
    readme_path = final_path / "README.mdx"
    if readme_path.exists():
        index_path = final_path / "index.mdx"
        readme_path.rename(index_path)
        print("  ✓ Renamed README.mdx to index.mdx")
    
    print("  ✓ Documentation organized")


def cleanup_temp_dirs(*paths):
    """Clean up temporary directories."""
    for path in paths:
        if path and Path(path).exists():
            shutil.rmtree(path, ignore_errors=True)


def main():
    """Main function."""
    # Check dependencies
    check_node_dependencies()
    
    # Get Weave version from environment or use latest
    weave_version = os.environ.get("WEAVE_VERSION", "latest")
    
    # Download Weave source
    weave_source = download_weave_source(weave_version)
    
    try:
        # Set up TypeScript project
        sdk_path = setup_typescript_project(weave_source)
        
        # Generate documentation to a temporary directory
        temp_output = tempfile.mkdtemp()
        generate_typedoc(sdk_path, temp_output)
        
        # Convert to Mintlify format
        convert_to_mintlify_format(temp_output)
        
        # Organize for Mintlify
        final_output = "weave/reference/typescript-sdk/weave"
        organize_for_mintlify(temp_output, final_output)
        
        print("\n✓ TypeScript SDK documentation generation complete!")
        
    finally:
        # Clean up temporary directories
        cleanup_temp_dirs(weave_source.parent if 'weave_source' in locals() else None,
                         temp_output if 'temp_output' in locals() else None)


if __name__ == "__main__":
    main()