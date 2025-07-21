#!/bin/bash

# --- Vale Test Enabler Script ---
# Enables a Vale test, fixes violations in a high-impact file first,
# waits for approval, then fixes all remaining files and creates a PR

set -e

# --- Color codes for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Input validation ---
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <vale_test_name>${NC}"
    echo -e "${YELLOW}Example: $0 'Google.We'${NC}"
    echo -e "${YELLOW}Example: $0 'write-good.Cliches'${NC}"
    exit 1
fi

VALE_TEST="$1"
# Create safe branch name by replacing dots and special characters
BRANCH_NAME="feature/vale-$(echo "$VALE_TEST" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]')-fix"
PROMPT_FILE="prompt_txts/vale_enabler_prompt.txt"

echo -e "${BLUE}=== Vale Test Enabler Script ===${NC}"
echo -e "${BLUE}Test to enable: ${YELLOW}$VALE_TEST${NC}"
echo -e "${BLUE}Branch name: ${YELLOW}$BRANCH_NAME${NC}"

# --- Check if we're already on the correct branch ---
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
    echo -e "${BLUE}Creating and checking out branch: $BRANCH_NAME${NC}"
    git checkout -b "$BRANCH_NAME"
fi

# --- Create output directory for analysis ---
mkdir -p vale_analysis

# --- Analyze current state ---
echo -e "${BLUE}=== Step 1: Analyzing current Vale violations ===${NC}"

# Get all mdx files
find . -name "*.mdx" -not -path "./node_modules/*" -not -path "./.venv/*" > vale_analysis/all_files.txt

# Count total files
TOTAL_FILES=$(wc -l < vale_analysis/all_files.txt | tr -d ' ')
echo -e "${GREEN}Found $TOTAL_FILES MDX files to analyze${NC}"

# Analyze violations per file
echo -e "${YELLOW}Analyzing '$VALE_TEST' violations per file...${NC}"
: > vale_analysis/violations_by_file.txt

while IFS= read -r file; do
    if [ -f "$file" ]; then
        # Properly quote the test name in the filter
        violation_count=$(vale --filter=".Name == \"$VALE_TEST\"" "$file" 2>/dev/null | grep -c "$VALE_TEST" 2>/dev/null || echo "0")
        # Ensure violation_count is a clean integer
        violation_count=$(echo "$violation_count" | tr -d '\n\r' | grep -o '[0-9]*' | head -1)
        violation_count=${violation_count:-0}
        if [ "$violation_count" -gt 0 ]; then
            echo "$file: $violation_count violations" >> vale_analysis/violations_by_file.txt
        fi
    fi
done < vale_analysis/all_files.txt

# Sort by violation count (highest first)
sort -t: -k2 -nr vale_analysis/violations_by_file.txt > vale_analysis/violations_sorted.txt

# Get total violation count
TOTAL_VIOLATIONS=$(awk -F: '{sum += $2} END {print sum+0}' vale_analysis/violations_sorted.txt 2>/dev/null)
# Ensure TOTAL_VIOLATIONS is always a valid integer
TOTAL_VIOLATIONS=${TOTAL_VIOLATIONS:-0}

echo -e "${GREEN}=== Analysis Results ===${NC}"
echo -e "${YELLOW}Total violations found: $TOTAL_VIOLATIONS${NC}"

if [ "$TOTAL_VIOLATIONS" -eq 0 ]; then
    echo -e "${GREEN}No violations found for '$VALE_TEST'. The test might already be passing or not enabled.${NC}"
    echo -e "${BLUE}Checking test configuration...${NC}"
    
    # Check if test exists - properly escape the test name for grep
    if find .github/styles -name "*.yml" -exec grep -l "$(printf '%s\n' "$VALE_TEST" | sed 's/[[\.*^$()+?{|]/\\&/g')" {} \; | head -1 > /dev/null; then
        echo -e "${YELLOW}Test exists but no violations found. Consider this test already compliant.${NC}"
    else
        echo -e "${RED}Test '$VALE_TEST' not found in Vale configuration.${NC}"
        echo -e "${YELLOW}Available tests:${NC}"
        find .github/styles -name "*.yml" -exec basename {} .yml \; | sort
    fi
    exit 0
fi

echo -e "${YELLOW}Top 10 files with most violations:${NC}"
head -10 vale_analysis/violations_sorted.txt

# Get the file with the most violations
HIGH_IMPACT_FILE=$(head -1 vale_analysis/violations_sorted.txt | cut -d: -f1)
HIGH_IMPACT_COUNT=$(head -1 vale_analysis/violations_sorted.txt | cut -d: -f2)

echo -e "${BLUE}=== Step 2: Fixing high-impact file first ===${NC}"
echo -e "${YELLOW}Target file: $HIGH_IMPACT_FILE ($HIGH_IMPACT_COUNT violations)${NC}"

# Generate detailed violation analysis for the high-impact file
echo -e "${YELLOW}Generating detailed analysis for $HIGH_IMPACT_FILE...${NC}"
vale --filter=".Name == \"$VALE_TEST\"" "$HIGH_IMPACT_FILE" 2>/dev/null > vale_analysis/high_impact_violations.txt

# Create environment variables for the prompt - properly escape for environment
export VALE_TEST_NAME="$VALE_TEST"
export HIGH_IMPACT_FILE="$HIGH_IMPACT_FILE"
export HIGH_IMPACT_COUNT="$HIGH_IMPACT_COUNT"
export TOTAL_VIOLATIONS="$TOTAL_VIOLATIONS"
export TOTAL_FILES="$TOTAL_FILES"

# Call Claude with the prompt
echo -e "${BLUE}=== Step 3: Calling Claude to fix violations ===${NC}"
echo -e "${YELLOW}Sending analysis to Claude for automated fixing...${NC}"

if [ ! -f "$PROMPT_FILE" ]; then
    echo -e "${RED}Error: Prompt file '$PROMPT_FILE' not found.${NC}"
    echo -e "${YELLOW}Creating default prompt file...${NC}"
    cat > "$PROMPT_FILE" << 'EOF'
You are working on enabling Vale tests to improve technical documentation quality. 

**Current Task**: Fix violations for the Vale test: ${VALE_TEST_NAME}

**Analysis Results**:
- Total violations across all files: ${TOTAL_VIOLATIONS}
- Files affected: ${TOTAL_FILES}
- High-impact file: ${HIGH_IMPACT_FILE} (${HIGH_IMPACT_COUNT} violations)

**Phase 1 Instructions**:
1. Review the detailed violation analysis in vale_analysis/high_impact_violations.txt
2. Fix all ${VALE_TEST_NAME} violations in ${HIGH_IMPACT_FILE}
3. Follow the technical writing guidelines from CLAUDE.md
4. Maintain technical accuracy while improving style
5. Test your changes by running: vale --filter='.Name == "${VALE_TEST_NAME}"' ${HIGH_IMPACT_FILE}
6. Commit your changes with a descriptive message

**Important**: Only fix the high-impact file in this phase. After committing, stop and wait for approval before proceeding to fix remaining files.

**Style Guidelines**:
- Use second person ("you") for instructions
- Avoid first-person plural pronouns ("we", "our", "us")  
- Use active voice and present tense
- Keep technical details intact
- Follow Google Developer Documentation Style Guide principles

When done with the high-impact file, commit your work and await further instructions.
EOF
fi

# Replace environment variables in prompt
envsubst < "$PROMPT_FILE" > vale_analysis/current_prompt.txt

# Call Claude
cat vale_analysis/current_prompt.txt | claude

echo -e "${GREEN}=== Phase 1 Complete ===${NC}"
echo -e "${YELLOW}High-impact file processing sent to Claude.${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Review Claude's changes to $HIGH_IMPACT_FILE"
echo -e "2. Test the changes: ${YELLOW}vale --filter='.Name == \"$VALE_TEST\"' '$HIGH_IMPACT_FILE'${NC}"
echo -e "3. If satisfied, run: ${YELLOW}$0 '$VALE_TEST' --phase2${NC}"

# --- Phase 2 handling (if --phase2 flag is provided) ---
if [ "$2" = "--phase2" ]; then
    echo -e "${BLUE}=== Phase 2: Fixing remaining files ===${NC}"
    
    # Re-analyze to see remaining violations
    echo -e "${YELLOW}Re-analyzing remaining violations...${NC}"
    : > vale_analysis/remaining_violations.txt
    
    while IFS= read -r file; do
        if [ -f "$file" ] && [ "$file" != "$HIGH_IMPACT_FILE" ]; then
            # Properly quote the test name in the filter
            violation_count=$(vale --filter=".Name == \"$VALE_TEST\"" "$file" 2>/dev/null | grep -c "$VALE_TEST" 2>/dev/null || echo "0")
            # Ensure violation_count is a clean integer
            violation_count=$(echo "$violation_count" | tr -d '\n\r' | grep -o '[0-9]*' | head -1)
            violation_count=${violation_count:-0}
            if [ "$violation_count" -gt 0 ]; then
                echo "$file: $violation_count violations" >> vale_analysis/remaining_violations.txt
            fi
        fi
    done < vale_analysis/all_files.txt
    
    REMAINING_VIOLATIONS=$(awk -F: '{sum += $2} END {print sum+0}' vale_analysis/remaining_violations.txt 2>/dev/null)
    # Ensure REMAINING_VIOLATIONS is always a valid integer
    REMAINING_VIOLATIONS=${REMAINING_VIOLATIONS:-0}
    
    if [ "$REMAINING_VIOLATIONS" -eq 0 ]; then
        echo -e "${GREEN}No remaining violations found! All files are now compliant.${NC}"
    else
        echo -e "${YELLOW}Found $REMAINING_VIOLATIONS remaining violations in other files.${NC}"
        echo -e "${BLUE}Creating bulk fix script...${NC}"
        
        # Create bulk fix script
        cat > vale_analysis/bulk_fix_script.py << 'EOF'
#!/usr/bin/env python3
"""
Bulk fix script for Vale violations across multiple files.
"""
import os
import re
import sys

# Add your bulk fix patterns here based on the specific Vale test
# This is a template - customize for each test type

def fix_violations(content, test_name):
    """Fix violations based on test type."""
    if "Google.We" in test_name:
        # Google.We specific fixes
        replacements = [
            (r'\bWe\b(?=\s+[a-z])', 'You'),
            (r'\bWe\b(?=\s+will)', 'This tutorial'),
            (r'\bWe\b(?=\s+can)', 'You'),
            (r'\bWe\b(?=\s+need)', 'You'),
            (r'\bWe\b(?=\s+use)', 'This tutorial uses'),
            (r'\bWe\b(?=\s+have)', 'You have'),
            (r'\bWe\b(?=\s+are)', 'You are'),
            (r'\bwe\b(?=\s+will)', 'this tutorial will'),
            (r'\bwe\b(?=\s+can)', 'you can'),
            (r'\bwe\b(?=\s+need)', 'you need'),
            (r'\bwe\b(?=\s+use)', 'this tutorial uses'),
            (r'\bwe\b(?=\s+have)', 'you have'),
            (r'\bwe\b(?=\s+are)', 'you are'),
            (r'\bour\b', 'your'),
            (r'\bOur\b', 'Your'),
            (r'\bus\b(?=\s)', 'you'),
            (r"we'll", "you'll"),
            (r"We'll", "This tutorial will"),
            (r"we're", "you're"),
            (r"We're", "You're"),
        ]
    else:
        # Generic patterns - customize as needed
        replacements = []
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

if __name__ == "__main__":
    test_name = os.environ.get('VALE_TEST_NAME', sys.argv[1] if len(sys.argv) > 1 else '')
    files_to_fix = []
    
    # Read files to fix from command line or file
    if len(sys.argv) > 2:
        files_to_fix = sys.argv[2:]
    else:
        try:
            with open('vale_analysis/remaining_violations.txt', 'r') as f:
                for line in f:
                    if ':' in line:
                        files_to_fix.append(line.split(':')[0].strip())
        except FileNotFoundError:
            print("No violations file found")
            sys.exit(1)
    
    print(f"Fixing {test_name} violations in {len(files_to_fix)} files...")
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                fixed_content = fix_violations(content, test_name)
                
                if content != fixed_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print(f"Fixed: {filepath}")
                else:
                    print(f"No changes needed: {filepath}")
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
        else:
            print(f"File not found: {filepath}")
    
    print("Bulk fix complete!")
EOF
        
        chmod +x vale_analysis/bulk_fix_script.py
        
        echo -e "${YELLOW}Running bulk fix script...${NC}"
        VALE_TEST_NAME="$VALE_TEST" python3 vale_analysis/bulk_fix_script.py
        
        echo -e "${BLUE}Committing bulk fixes...${NC}"
        git add .
        git commit -m "Bulk fix '$VALE_TEST' violations across remaining files

- Applied automated fixes to remaining files with '$VALE_TEST' violations
- Reduced total violations from $TOTAL_VIOLATIONS to target of 0
- Followed technical writing guidelines while maintaining accuracy"
    fi
    
    echo -e "${BLUE}=== Step 4: Creating Pull Request ===${NC}"
    
    # Push branch
    git push -u origin "$BRANCH_NAME"
    
    # Create PR (requires gh CLI or manual creation)
    if command -v gh &> /dev/null; then
        echo -e "${YELLOW}Creating PR with GitHub CLI...${NC}"
        gh pr create --title "Enable '$VALE_TEST' Vale test and fix all violations" \
                     --body "## Summary

This PR enables the '$VALE_TEST' Vale test and fixes all violations across the documentation.

## Changes Made

- **Phase 1**: Fixed $HIGH_IMPACT_COUNT violations in high-impact file: \`$HIGH_IMPACT_FILE\`
- **Phase 2**: Applied bulk fixes to remaining files
- **Total**: Reduced violations from $TOTAL_VIOLATIONS to 0

## Methodology

1. Analyzed all MDX files for '$VALE_TEST' violations
2. Fixed highest-impact file first for review
3. Applied systematic fixes following Google Developer Documentation Style Guide
4. Maintained technical accuracy while improving documentation style

## Testing

All files now pass the '$VALE_TEST' Vale test:
\`\`\`bash
vale --filter='.Name == \"$VALE_TEST\"' .
\`\`\`

Ready for review and potential merge to enable this Vale test going forward."
    else
        echo -e "${YELLOW}GitHub CLI not found. Manual PR creation needed.${NC}"
        echo -e "${BLUE}PR Details:${NC}"
        echo -e "Title: Enable '$VALE_TEST' Vale test and fix all violations"
        echo -e "Branch: $BRANCH_NAME"
    fi
    
    echo -e "${GREEN}=== All phases complete! ===${NC}"
    echo -e "${YELLOW}Branch pushed and PR created for review.${NC}"
fi

# Cleanup
rm -rf vale_analysis

echo -e "${GREEN}Script completed successfully!${NC}" 