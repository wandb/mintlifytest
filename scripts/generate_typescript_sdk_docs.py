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
import tempfile
import tarfile
from pathlib import Path
import requests


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


def download_weave_source(version="main"):
    """Download Weave source code for a specific version."""
    print(f"Downloading Weave source code for version: {version}")
    
    # Handle "latest" by fetching the latest release tag
    if version == "latest":
        try:
            api_url = "https://api.github.com/repos/wandb/weave/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            version = response.json()["tag_name"]
            print(f"  Using latest release: {version}")
        except Exception as e:
            print(f"  Warning: Could not fetch latest release, using main branch: {e}")
            version = "main"
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Download tarball from GitHub
        url = f"https://github.com/wandb/weave/archive/{version}.tar.gz"
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Save and extract tarball
        tarball_path = Path(temp_dir) / "weave.tar.gz"
        with open(tarball_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract
        with tarfile.open(tarball_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
        
        # Find the extracted directory
        extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir() and d.name.startswith('weave-')]
        if not extracted_dirs:
            raise Exception("Could not find extracted Weave directory")
        
        weave_dir = extracted_dirs[0]
        print(f"✓ Downloaded and extracted Weave source to {weave_dir}")
        
        return weave_dir
        
    except Exception as e:
        print(f"Error downloading Weave source: {e}", file=sys.stderr)
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)


def check_package_json_versions(sdk_path):
    """Check if package.json has compatible typedoc versions."""
    package_json_path = sdk_path / "package.json"
    if package_json_path.exists():
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
            
        dev_deps = package_data.get("devDependencies", {})
        print("\nExisting TypeScript dependencies:")
        for pkg in ["typedoc", "typedoc-plugin-markdown", "typescript"]:
            if pkg in dev_deps:
                print(f"  {pkg}: {dev_deps[pkg]}")
    return


def setup_typescript_project(weave_source):
    """Set up the TypeScript project and install dependencies."""
    sdk_path = Path(weave_source) / "sdks" / "node"
    
    if not sdk_path.exists():
        print(f"TypeScript SDK not found at {sdk_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Setting up TypeScript project at {sdk_path}")
    
    # Check existing versions
    check_package_json_versions(sdk_path)
    
    # Install dependencies
    os.chdir(sdk_path)
    try:
        print("\nInstalling dependencies...")
        subprocess.run(["pnpm", "install"], check=True)
        
        # Install compatible versions of typedoc and markdown plugin
        # Use specific versions that are known to work together
        print("Installing compatible typedoc versions...")
        subprocess.run([
            "pnpm", "add", "-D",
            "typedoc@0.25.13",  # Use a stable version that works with CommonJS
            "typedoc-plugin-markdown@3.17.1"  # Compatible with typedoc 0.25.x
        ], check=True)
        
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}", file=sys.stderr)
        sys.exit(1)
    
    return sdk_path


def generate_typedoc_config(sdk_path, output_path):
    """Generate typedoc configuration."""
    # Use options compatible with typedoc 0.25.x
    config = {
        "entryPoints": ["src/index.ts"],
        "out": str(output_path),
        "plugin": ["typedoc-plugin-markdown"],
        "readme": "none",
        "disableSources": True,
        "excludePrivate": True,
        "excludeProtected": True,
        "excludeInternal": True,
        "githubPages": False,
        "cleanOutputDir": True,
        "hideGenerator": True,
        "navigationLinks": {
            "GitHub": "https://github.com/wandb/weave"
        }
    }
    
    config_path = sdk_path / "typedoc.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_path


def run_typedoc(sdk_path, output_path):
    """Run typedoc to generate documentation."""
    print(f"\nGenerating TypeScript documentation to {output_path}...")
    
    os.chdir(sdk_path)
    try:
        # Run typedoc with error output
        result = subprocess.run([
            "pnpm", "exec", "typedoc"
        ], capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print("TypeDoc output:")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            
            # Check if docs were still generated despite warnings
            if output_path.exists() and any(output_path.iterdir()):
                print("⚠ TypeDoc completed with warnings, but documentation was generated")
            else:
                raise subprocess.CalledProcessError(result.returncode, result.args)
        else:
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
    
    # Get Weave version from environment or use main
    weave_version = os.environ.get("WEAVE_VERSION", "main")
    
    # Download Weave source
    weave_source = download_weave_source(weave_version)
    
    try:
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
        
    finally:
        # Clean up temporary directory
        if weave_source:
            temp_dir = weave_source.parent
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main() 