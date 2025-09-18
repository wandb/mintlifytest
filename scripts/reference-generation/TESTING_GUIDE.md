# Testing Guide for Reference Documentation Generation

## Quick Start Testing

The GitHub Action has a **temporary push trigger** for testing. Any push to the `feature/reference-docs-generation-v2` branch that modifies:
- The workflow file (`.github/workflows/generate-reference-docs.yml`)
- Any file in `scripts/reference-generation/`

Will automatically trigger the documentation generation.

## Testing Methods

### 1. Automatic Testing (Push Trigger)
Simply push any change to trigger the workflow:
```bash
# Make a small change to trigger the workflow
echo "# Test trigger $(date)" >> scripts/reference-generation/test-trigger.txt
git add scripts/reference-generation/test-trigger.txt
git commit -m "test: Trigger workflow"
git push origin feature/reference-docs-generation-v2
```

Then check the Actions tab in GitHub to see the workflow run.

### 2. Manual Testing (Workflow Dispatch)
1. Go to the [Actions tab](https://github.com/wandb/mintlifytest/actions) in the repository
2. Click on "Generate Reference Documentation" workflow
3. Click "Run workflow"
4. Choose options:
   - **Branch**: `feature/reference-docs-generation-v2`
   - **Weave version**: `latest` (or specific version like `0.51.34`)
   - **Create PR**: `true` (to test PR creation) or `false` (to test without PR)
5. Click "Run workflow"

### 3. Local Testing
Test individual scripts locally:
```bash
# Test Service API generation
python scripts/reference-generation/generate_service_api_spec.py

# Test Python SDK generation (in isolated environment)
./scripts/reference-generation/generate_docs_isolated.sh

# Test TypeScript SDK generation
python scripts/reference-generation/generate_typescript_sdk_docs.py

# Test broken links fix
python scripts/reference-generation/fix_broken_links.py
```

## What to Check

1. **Workflow Success**: 
   - All steps should complete successfully
   - Check the logs for any warnings or errors

2. **Generated Files**:
   - `weave/api-reference/openapi.json` - Service API spec
   - `weave/reference/python-sdk/` - Python SDK docs
   - `weave/reference/typescript-sdk/` - TypeScript SDK docs

3. **Link Validation**:
   - Run `mint broken-links` locally after pulling the changes
   - All internal links should work

4. **PR Creation** (if enabled):
   - A new PR should be created with the title "Update reference documentation"
   - The PR should have proper labels and description

## Important Notes

⚠️ **BEFORE MERGING THE PR**:
1. Remove the push trigger from `.github/workflows/generate-reference-docs.yml`
2. Delete the test trigger file if created
3. The workflow should only have `workflow_dispatch` trigger in production

## Troubleshooting

- **Permission errors**: The workflow needs write permissions to create PRs
- **Package not found**: Check the Weave version exists on PyPI
- **TypeScript download fails**: Check the npm registry for the @wandb/weave package
- **Broken links persist**: Run the fix_broken_links.py script manually

## Clean Up Test Files

After testing:
```bash
# Remove test trigger file if created
rm -f scripts/reference-generation/test-trigger.txt

# Remove the push trigger from the workflow before merging
# Edit .github/workflows/generate-reference-docs.yml and remove lines 4-10
```
