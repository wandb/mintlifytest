# Reference Documentation Generation Scripts

This directory contains scripts to automatically generate reference documentation for the Weave project from source code.

## Overview

The documentation generation system consists of three main components:

1. **Service API Documentation** - Generated from the OpenAPI specification served by the Weave service
2. **Python SDK Documentation** - Generated from Python source code using lazydocs
3. **TypeScript SDK Documentation** - Generated from TypeScript source code using typedoc

## Key Improvements

This implementation provides several improvements over the previous approach:

- **Minimal Dependencies**: Only essential packages (requests, lazydocs, pyyaml) reducing security risks
- **Native Mintlify Support**: Leverages Mintlify's built-in OpenAPI support for Service API docs
- **Clean Output**: Simplified post-processing that maintains documentation quality
- **No Custom Processing**: Eliminates complex custom scripts that introduced Socket Security issues
- **Version-based Generation**: Accepts specific Weave versions, tags, or commit hashes

## Scripts

### `generate_service_api_spec.py`
- Downloads the OpenAPI specification from https://trace.wandb.ai/openapi.json
- Saves it directly for Mintlify to consume
- No custom processing needed - Mintlify handles OpenAPI natively

### `generate_python_sdk_docs.py`
- Uses lazydocs to generate Python API documentation
- Installs specific Weave version from PyPI or GitHub
- Post-processes output to add Mintlify frontmatter
- Converts .md files to .mdx for Mintlify compatibility

### `generate_typescript_sdk_docs.py`
- Downloads Weave source code for specified version
- Uses typedoc with typedoc-plugin-markdown
- Generates clean markdown documentation
- Post-processes to add Mintlify frontmatter
- Handles Node.js dependency management with pnpm

## GitHub Action

The `.github/workflows/generate-reference-docs.yml` workflow:

- Runs weekly on a schedule or manually via workflow_dispatch
- Accepts a Weave version parameter (tag, commit SHA, or branch name)
- Generates all three types of documentation
- Creates a pull request if changes are detected
- Uses caching for faster builds

## Usage

### Manual Generation

1. Set up Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r scripts/requirements.txt
   ```

2. Generate documentation for a specific version:
   ```bash
   # For latest PyPI version
   python scripts/generate_service_api_spec.py
   python scripts/generate_python_sdk_docs.py
   python scripts/generate_typescript_sdk_docs.py
   
   # For specific version
   export WEAVE_VERSION=v0.50.0  # or commit SHA, or branch name
   python scripts/generate_python_sdk_docs.py
   python scripts/generate_typescript_sdk_docs.py
   ```

### GitHub Action

The workflow can be triggered:
- Manually from the Actions tab with optional parameters
- Automatically every Monday at 00:00 UTC
- Parameters:
  - `weave_version`: Version tag (e.g., v0.50.0), commit SHA, or branch name (default: main)
  - `create_pr`: Whether to create a PR (default: true)

### Supported Version Formats

- **Latest**: Uses the latest version from PyPI (default)
- **Version tags**: `v0.50.0` or `0.50.0`
- **Commit SHA**: Full or short commit hash
- **Branch names**: `main`, `feature/branch-name`, etc.

## Requirements

- Python 3.11+
- Node.js 18+
- pnpm (will be installed automatically if missing)
- Internet access to download packages and source code 