# Reference Documentation Generation Scripts

This directory contains scripts to automatically generate reference documentation for Weave from its source code, formatted for Mintlify.

## Overview

The system generates three types of documentation:

1. **Service API Documentation** - From the OpenAPI specification
2. **Python SDK Documentation** - From Python source code using lazydocs
3. **TypeScript SDK Documentation** - From TypeScript source code using typedoc

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r scripts/reference-generation/requirements.txt
   ```

## Usage

### Generate All Documentation

Run all three generators in sequence:

```bash
# Generate Service API docs
python scripts/reference-generation/generate_service_api_spec.py

# Generate Python SDK docs
python scripts/reference-generation/generate_python_sdk_docs.py

# Generate TypeScript SDK docs
python scripts/reference-generation/generate_typescript_sdk_docs.py
```

### Generate Specific Version

You can specify a Weave version using the `WEAVE_VERSION` environment variable:

```bash
# Latest PyPI release (default)
export WEAVE_VERSION=latest

# Specific version tag
export WEAVE_VERSION=v0.50.0

# Specific commit
export WEAVE_VERSION=abc123def

# Branch name
export WEAVE_VERSION=main
```

Then run the Python or TypeScript generation scripts.

## Output Structure

The scripts generate documentation in the following structure:

```
weave/
├── api-reference/
│   └── openapi.json          # Service API OpenAPI spec
└── reference/
    ├── python-sdk/
    │   └── weave/
    │       ├── index.mdx     # Main module docs
    │       ├── trace/
    │       │   ├── op.mdx
    │       │   ├── weave_client.mdx
    │       │   └── util.mdx
    │       └── trace_server/
    │           └── trace_server_interface.mdx
    └── typescript-sdk/
        └── weave/
            ├── index.mdx
            ├── classes/
            ├── functions/
            ├── interfaces/
            └── type-aliases/
```

## Testing Locally

After generating documentation, you can test it with Mintlify:

```bash
# From the project root
mint dev
```

Then navigate to the reference documentation sections to verify the output.

## How It Works

### Service API (`generate_service_api_spec.py`)
- Downloads the OpenAPI spec from https://trace.wandb.ai/openapi.json
- Updates server URLs and metadata
- Saves directly for Mintlify to consume (no conversion needed)

### Python SDK (`generate_python_sdk_docs.py`)
- Installs the specified Weave version
- Uses lazydocs to generate markdown documentation
- Converts from Docusaurus format to Mintlify MDX format
- Handles special cases like Pydantic models
- Fixes code fence indentation issues

### TypeScript SDK (`generate_typescript_sdk_docs.py`)
- Downloads Weave source code for the specified version
- Installs dependencies and typedoc
- Generates markdown documentation
- Converts to Mintlify MDX format
- Organizes files according to Mintlify structure

## Troubleshooting

### Python SDK Issues
- If module imports fail, check that Weave installed correctly
- For development versions, ensure you have git access to the Weave repository

### TypeScript SDK Issues
- Ensure Node.js 18+ is installed
- If typedoc fails, check for TypeScript compilation errors in the Weave SDK
- The script pins specific versions of typedoc that are known to work

### General Issues
- Check that you're in the activated virtual environment
- Ensure you have internet access for downloading packages and source code
- For version-specific issues, try using `latest` or `main` as a fallback