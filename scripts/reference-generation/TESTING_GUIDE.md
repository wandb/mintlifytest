# Testing Guide for Reference Documentation Generation

## Production Usage (After Merge)

Once merged to main, the workflow will be triggered manually from the Actions tab:

1. Go to [Actions](https://github.com/wandb/mintlifytest/actions)
2. Select "Generate Reference Documentation"
3. Click "Run workflow"
4. Enter the Weave version (e.g., "latest", "0.51.34", "v0.51.34", or commit SHA)
5. Choose whether to create a PR (recommended: true)
6. Click "Run workflow"

The workflow will generate the reference docs and create a new PR with the changes.

## Testing While on Feature Branch

The workflow has a **temporary push trigger** for testing before merge. Any push to the branch will trigger the workflow with the latest version.

To test with a specific version while on the feature branch:
```bash
# Set the version as an environment variable in your commit message or use the local test script
./scripts/reference-generation/test-locally.sh 0.51.34
```

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
1. Remove the `push` trigger from `.github/workflows/generate-reference-docs.yml` (lines 16-19)
2. The workflow should only have `workflow_dispatch` trigger in production
3. Delete any test files created during testing

## Troubleshooting

- **Permission errors**: The workflow needs write permissions to create PRs
- **Package not found**: Check the Weave version exists on PyPI
- **TypeScript download fails**: Check the npm registry for the @wandb/weave package
- **Broken links persist**: Run the fix_broken_links.py script manually

## Clean Up Before Merging

After testing is complete:
```bash
# Remove the test configuration file
rm -f scripts/reference-generation/test-config.txt

# Edit .github/workflows/generate-reference-docs.yml to:
# 1. Remove the issue_comment trigger (lines 4-6)
# 2. Remove the comment parsing steps
# 3. Keep only the workflow_dispatch trigger
```

The production workflow should only respond to manual triggers via the Actions UI.
