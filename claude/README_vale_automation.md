# Vale Test Automation System

This system provides automated tools for enabling Vale tests, fixing violations systematically, and creating pull requests for review.

## Overview

The Vale test enabler automates the process of:
1. Analyzing Vale test violations across all documentation
2. Fixing the highest-impact file first for review
3. Applying bulk fixes to remaining files after approval  
4. Creating pull requests with detailed documentation

## Files

- **`vale_test_enabler.sh`** - Main automation script
- **`../prompt_txts/vale_enabler_prompt.txt`** - AI prompt template for guided fixes
- **`README_vale_automation.md`** - This documentation

## Usage

### Basic Usage

```bash
# Enable a specific Vale test and fix violations (note the quotes for safety)
./claude/vale_test_enabler.sh '<vale_test_name>'
```

### Examples

```bash
# Fix Google.We violations (first-person plural pronouns)
./claude/vale_test_enabler.sh 'Google.We'

# Fix write-good cliché violations  
./claude/vale_test_enabler.sh 'write-good.Cliches'

# Fix passive voice violations
./claude/vale_test_enabler.sh 'Google.Passive'

# Fix readability violations
./claude/vale_test_enabler.sh 'write-good.ReadabilityTransforms'
```

**Important**: Always quote the Vale test name to handle dots, hyphens, and other special characters safely.

## Workflow

### Phase 1: High-Impact Analysis and Fix

1. **Analysis**: Script analyzes all `.mdx` files for violations
2. **Prioritization**: Identifies file with most violations for maximum impact
3. **AI-Guided Fix**: Uses Claude AI to fix violations in the high-impact file
4. **Review**: Creates commit for manual review before proceeding

```bash
# Example output
=== Vale Test Enabler Script ===
Test to enable: Google.We
Working on current branch: feature/my-documentation-updates

=== Step 1: Analyzing current Vale violations ===
Found 128 MDX files to analyze
Total violations found: 247

Top 10 files with most violations:
cookbooks/dspy_prompt_optimization.mdx: 37 violations
cookbooks/multi-agent-structured-output.mdx: 32 violations
...

=== Step 2: Fixing high-impact file first ===
Target file: cookbooks/dspy_prompt_optimization.mdx (37 violations)
```

### Phase 2: Bulk Processing (After Approval)

```bash
# After reviewing and approving Phase 1 changes
./claude/vale_test_enabler.sh 'Google.We' --phase2
```

This will:
- Apply automated fixes to all remaining files
- Commit bulk changes
- Push changes to current branch

### Manual Workflow (No Claude CLI)

If Claude CLI is not available, the script provides a manual workflow:

```bash
# Run analysis (stops at manual step)
./claude/vale_test_enabler.sh 'Google.We'

# Script provides:
# 1. Detailed violation analysis in vale_analysis/
# 2. Generated prompt in vale_analysis/current_prompt.txt  
# 3. Clear instructions for manual fixing

# Manual steps:
# 1. Review violations: vale --filter='.Name == "Google.We"' target_file.mdx
# 2. Edit the file to fix violations
# 3. Test fixes: vale --filter='.Name == "Google.We"' target_file.mdx
# 4. Commit changes
# 5. Run Phase 2: ./claude/vale_test_enabler.sh 'Google.We' --phase2
```

**Alternative AI Tools:**
- Copy prompt from `vale_analysis/current_prompt.txt` to ChatGPT, Claude web, etc.
- Paste file content and get AI-assisted fixes
- Apply suggested changes manually

## Requirements

### Prerequisites

- **Vale CLI**: Must be installed and accessible (`vale --version`)
- **Claude Code** (optional): For enhanced manual workflow prompts
  - Install: `npm install -g @anthropic-ai/claude-code` 
  - Note: Claude Code is interactive-only, not suitable for automation
  - Script generates optimized prompts for manual use with Claude Code or web interface
  - Script always uses manual workflow regardless of Claude Code installation
- **Git**: For commits and pushes to current branch

### Environment

- Vale configuration must be present (`.vale.ini`, `.github/styles/`)
- Must be run from repository root directory
- Requires write access to commit and push changes
- `vale_analysis/` directory is auto-generated (added to .gitignore)

## Supported Vale Tests

The system is designed to work with any Vale test, with built-in support for:

### Google.We (First-person plural pronouns)
- Replaces "we", "our", "us" with appropriate alternatives
- Follows Google Developer Documentation Style Guide

### write-good.Cliches (Overused phrases)  
- Identifies and replaces clichéd expressions
- Promotes clear, direct language

### Google.Passive (Passive voice)
- Converts passive constructions to active voice
- Improves clarity and directness

### Custom Tests
- Easily extensible for new Vale tests
- Modify `bulk_fix_script.py` template for specific patterns

## Configuration

### Customizing Fix Patterns

Edit the bulk fix script template in `vale_test_enabler.sh` to add patterns for new tests:

```python
def fix_violations(content, test_name):
    if "YourCustom.Test" in test_name:
        replacements = [
            (r'pattern1', 'replacement1'),
            (r'pattern2', 'replacement2'),
        ]
```

### Prompt Customization

Modify `prompt_txts/vale_enabler_prompt.txt` to:
- Add test-specific guidance
- Include organization-specific style guidelines
- Customize quality requirements

## Output and Analysis

The script creates temporary analysis files:

```
vale_analysis/
├── all_files.txt              # List of all MDX files
├── violations_by_file.txt     # Raw violation counts
├── violations_sorted.txt      # Sorted by violation count
├── high_impact_violations.txt # Detailed analysis for target file
├── current_prompt.txt         # Generated prompt for AI
└── remaining_violations.txt   # Phase 2 analysis
```

## Error Handling

### Common Issues

**No violations found:**
```bash
No violations found for Google.We. The test might already be passing.
```
- Test may already be compliant
- Test name might be incorrect
- Check available tests with listed suggestions

**Test not found:**
```bash
Test 'BadTest.Name' not found in Vale configuration.
Available tests: [list shown]
```
- Verify test name spelling and case
- Check Vale configuration files

**Claude Code API key not configured:**
```bash
Error: ANTHROPIC_API_KEY environment variable not set.
Claude Code requires an API key for automation.

Setup instructions:
1. Get an API key:
   - Visit: https://console.anthropic.com
   - Create account or sign in
   - Navigate to API Keys section
   - Create a new API key

2. Set the environment variable:
   export ANTHROPIC_API_KEY='your-api-key-here'

3. Add to your shell profile for persistence:
   echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
   # or ~/.zshrc for zsh users
```
- **API Key Setup**: Requires Anthropic Console account and API key
- **Security**: Never commit API keys to version control
- Falls back to manual workflow if not configured

**Claude Code detected (designed for interactive use):**
```bash
Claude Code detected with API key configured.
However, Claude Code is designed for interactive use, not automation.
The script will use the manual workflow with enhanced prompts.
```
- **Claude Code reality**: Even with API key, it's an interactive development environment
- **Not scriptable**: Requires terminal control and user interaction
- **Manual workflow**: Script generates detailed prompts optimized for Claude Code web interface
- All analysis preserved for copy-paste into Claude Code or other AI tools

**No Claude CLI available:**
```bash
Error: 'claude' command not found
No suitable Claude API CLI tool available for automated fixing.
```
- **Note**: No official Claude API CLI exists from Anthropic
- Script provides comprehensive manual workflow with detailed instructions
- Generated prompt can be used with any AI tool (ChatGPT, Claude web interface, etc.)
- Analysis files preserved for manual review

## Best Practices

### Before Running

1. **Backup**: Ensure clean git state and current work is committed
2. **Test**: Verify Vale configuration with `vale --config`
3. **Review**: Check existing violations with `vale .`

### During Process

1. **Review Changes**: Carefully examine AI-generated fixes
2. **Test Locally**: Run Vale on modified files before committing
3. **Spot Check**: Manually verify a few changes for quality

### After Completion

1. **Full Test**: Run Vale on entire repository
2. **Documentation**: Update Vale configuration if permanently enabling test
3. **Team Review**: Request thorough PR review before merging

## Integration

### CI/CD Integration

Add to GitHub Actions or similar:

```yaml
- name: Enable Vale Test
  run: ./claude/vale_test_enabler.sh 'Google.We' --phase2
  env:
    CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
```

### Scheduled Maintenance

Consider monthly runs to:
- Check for new Vale test candidates
- Maintain documentation quality standards
- Address accumulated violations

## Troubleshooting

### Script Fails During Analysis

- Check Vale installation: `vale --version`
- Verify file permissions: `ls -la claude/`
- Ensure proper directory: `pwd` should show repo root

### AI Fixes Incomplete

- Review `vale_analysis/current_prompt.txt` for clarity
- Check file complexity - some files may need manual attention
- Verify Claude API access and rate limits

### PR Creation Fails

- Install GitHub CLI: `gh auth login`
- Check repository permissions
- Manually create PR using provided details

## Contributing

To extend this system:

1. Add new Vale test patterns to bulk fix script
2. Update prompt template with test-specific guidance
3. Test thoroughly on sample files
4. Document new patterns in this README

## License

This automation system follows the same license as the parent repository. 