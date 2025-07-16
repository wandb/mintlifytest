# Building Weave Documentation

This documentation uses [Mintlify](https://mintlify.com/) as the documentation framework.

## Prerequisites

- Node.js 18.0+ 
- Mintlify CLI: `npm install -g mintlify`

## Development

To start the local development server:

```bash
make dev
# or
mintlify dev
```

The documentation will be available at `http://localhost:3000`.

## Building for Production

To build the documentation:

```bash
make build
# or
mintlify build
```

## Configuration

The documentation is configured via `docs.json`. Key configuration includes:
- Navigation structure
- Color theme
- API reference tabs
- SEO metadata

## Project Structure

```
.
├── docs.json              # Main configuration file
├── index.mdx             # Homepage
├── quickstart.mdx        # Quick start guide
├── tutorial-*.mdx        # Tutorial pages
├── guides/               # In-depth guides
├── reference/            # API reference documentation
├── images/               # Shared images
├── api-reference/        # OpenAPI specifications
└── logo/                 # Logo assets
```

## Adding New Pages

1. Create a new `.mdx` file in the appropriate directory
2. Add the page to the navigation in `docs.json`
3. Use Mintlify components for rich content:
   - `<Note>`, `<Warning>`, `<Tip>` for callouts
   - `<CodeGroup>` and `<Tab>` for code examples
   - `<Card>` and `<CardGroup>` for feature cards

## Reference Documentation

The reference documentation is temporarily generated from the live API. To update:

1. Python SDK docs: Will need to be regenerated from source using `lazydocs`
2. Service API docs: Generated from OpenAPI spec at https://trace.wandb.ai/openapi.json
3. TypeScript SDK docs: Generated from TypeScript source

## Troubleshooting

- If images aren't displaying, check paths are relative to the MDX file location
- Run `make check-links` to find broken internal links
- Check `mint.log` for detailed error messages
- Use `mintlify broken-links` to validate internal references 