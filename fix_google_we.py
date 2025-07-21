#!/usr/bin/env python3
"""
Script to automatically fix Google.We Vale violations in MDX files.
Replaces first-person plural pronouns with second-person or objective language.
"""

import os
import re
import glob

def fix_google_we_violations(content):
    """Fix common Google.We violations in content."""
    
    # Pattern replacements for common Google.We violations
    replacements = [
        # "We" at start of sentence
        (r'\bWe\b(?=\s+[a-z])', 'You'),
        (r'\bWe\b(?=\s+will)', 'This tutorial'),
        (r'\bWe\b(?=\s+can)', 'You'),
        (r'\bWe\b(?=\s+need)', 'You'),
        (r'\bWe\b(?=\s+use)', 'This tutorial uses'),
        (r'\bWe\b(?=\s+have)', 'You have'),
        (r'\bWe\b(?=\s+are)', 'You are'),
        (r'\bWe\b(?=\s+show)', 'This tutorial shows'),
        (r'\bWe\b(?=\s+demonstrate)', 'This tutorial demonstrates'),
        (r'\bWe\b(?=\s+learn)', 'You learn'),
        (r'^\s*We\s+', 'You '),  # We at start of line
        
        # "we" in middle of sentence
        (r'\bwe\b(?=\s+will)', 'you will'),
        (r'\bwe\b(?=\s+can)', 'you can'),
        (r'\bwe\b(?=\s+need)', 'you need'),
        (r'\bwe\b(?=\s+use)', 'the tutorial uses'),
        (r'\bwe\b(?=\s+have)', 'you have'),
        (r'\bwe\b(?=\s+are)', 'you are'),
        (r'\bwe\b(?=\s+show)', 'this shows'),
        (r'\bwe\b(?=\s+demonstrate)', 'this demonstrates'),
        (r'\bwe\b(?=\s+learn)', 'you learn'),
        (r'\bwe\b(?=\s+\')', 'you\''),
        (r'\bwe\b', 'you'),  # Generic "we" replacement
        
        # "our" replacements
        (r'\bour\b(?=\s+[a-zA-Z]+\s+workflow)', 'the LLM workflow'),
        (r'\bour\b(?=\s+workflow)', 'the workflow'),
        (r'\bour\b(?=\s+[a-zA-Z]+\s+strategy)', 'the prompting strategy'),
        (r'\bour\b(?=\s+strategy)', 'the strategy'),
        (r'\bour\b(?=\s+[a-zA-Z]+\s+application)', 'the application'),
        (r'\bour\b(?=\s+application)', 'the application'),
        (r'\bour\b(?=\s+[a-zA-Z]+\s+model)', 'the model'),
        (r'\bour\b(?=\s+model)', 'the model'),
        (r'\bour\b(?=\s+[a-zA-Z]+\s+function)', 'the function'),
        (r'\bour\b(?=\s+function)', 'the function'),
        (r'\bour\b(?=\s+[a-zA-Z]+\s+dataset)', 'the dataset'),
        (r'\bour\b(?=\s+dataset)', 'the dataset'),
        (r'\bour\b(?=\s+[a-zA-Z]+\s+evaluation)', 'the evaluation'),
        (r'\bour\b(?=\s+evaluation)', 'the evaluation'),
        (r'\bour\b(?=\s+example)', 'the example'),
        (r'\bour\b(?=\s+tutorial)', 'the tutorial'),
        (r'\bour\b', 'your'),  # Generic "our" replacement
        
        # "us" replacements
        (r'\bus\b', 'you'),
        
        # "let's" and "Let's" replacements
        (r"\blet's\b", ''),
        (r"\bLet's\b", ''),
        
        # Clean up extra spaces created by removals
        (r'\s+', ' '),
        (r'^\s+', ''),  # Remove leading spaces
        (r'\s+$', ''),  # Remove trailing spaces
    ]
    
    modified_content = content
    for pattern, replacement in replacements:
        modified_content = re.sub(pattern, replacement, modified_content, flags=re.MULTILINE)
    
    return modified_content

def process_file(filepath):
    """Process a single file to fix Google.We violations."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixed_content = fix_google_we_violations(content)
    
    if fixed_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"Fixed violations in: {filepath}")
        return True
    return False

def main():
    """Main function to process all MDX files."""
    # Find all .mdx files
    mdx_files = glob.glob("**/*.mdx", recursive=True)
    
    # Exclude node_modules and other unwanted directories
    mdx_files = [f for f in mdx_files if not any(exclude in f for exclude in ['node_modules', '.venv', '.git'])]
    
    print(f"Found {len(mdx_files)} MDX files to process")
    
    fixed_count = 0
    for filepath in mdx_files:
        if process_file(filepath):
            fixed_count += 1
    
    print(f"Fixed Google.We violations in {fixed_count} files")

if __name__ == "__main__":
    main() 