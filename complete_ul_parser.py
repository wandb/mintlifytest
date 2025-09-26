#!/usr/bin/env python3
"""
Complete UL parser - Captures ALL <ul> elements as groups and ALL <li> elements as pages
"""

import re
import json
from html import unescape
from typing import List, Dict, Any
from pathlib import Path


class CompleteNavigationParser:
    def __init__(self):
        self.all_items = []

    def parse_complete_navigation(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse the complete navigation structure without missing anything."""

        # First, let's extract ALL navigation items with their context
        self._extract_all_navigation_items(html_content)

        # Then build the hierarchical structure
        return self._build_complete_hierarchy()

    def _extract_all_navigation_items(self, html_content: str):
        """Extract every single navigation item with its depth and context."""

        # Split content into lines for processing
        lines = html_content.split('\n')

        current_depth = 0
        depth_stack = []  # Track ul depths

        for i, line in enumerate(lines):
            line = line.strip()

            # Track UL depth changes
            ul_match = re.search(r'<ul class="(ul-\d+[^"]*)"', line)
            if ul_match:
                ul_class = ul_match.group(1)
                depth_match = re.search(r'ul-(\d+)', ul_class)
                if depth_match:
                    depth = int(depth_match.group(1))
                    current_depth = depth

                    # Find the group title for this UL
                    group_title = self._find_group_title_before_ul(lines, i)

                    depth_stack.append({
                        'depth': depth,
                        'group_title': group_title,
                        'line_index': i
                    })

            # Track closing UL tags
            if '</ul>' in line:
                if depth_stack:
                    depth_stack.pop()
                    current_depth = depth_stack[-1]['depth'] if depth_stack else 0

            # Look for navigation items (LI with anchor tags)
            if re.search(r'<li[^>]*class="[^"]*td-sidebar-nav__section-title[^"]*"', line):
                # Extract anchor information from this line and the next few lines
                anchor_info = self._extract_anchor_from_lines(lines, i)

                if anchor_info:
                    # Determine if this item has children
                    has_children = self._check_has_children(lines, i, current_depth)

                    item = {
                        'href': anchor_info['href'],
                        'title': anchor_info['title'],
                        'depth': current_depth,
                        'has_children': has_children,
                        'line_index': i,
                        'parent_group': depth_stack[-1]['group_title'] if depth_stack else None
                    }

                    self.all_items.append(item)

    def _find_group_title_before_ul(self, lines: List[str], ul_line_index: int) -> str:
        """Find the group title that comes before a UL element."""

        # Look backwards for the anchor tag that defines this group
        for i in range(ul_line_index - 1, max(0, ul_line_index - 20), -1):
            anchor_match = re.search(r'<a href="[^"]+[^>]*>\s*<span[^>]*>(.*?)</span>\s*</a>', lines[i], re.DOTALL)
            if anchor_match:
                title = unescape(anchor_match.group(1).strip())
                title = re.sub(r'\s+', ' ', title).strip()
                return title

        return f"Group at line {ul_line_index}"

    def _extract_anchor_from_lines(self, lines: List[str], start_index: int) -> Dict[str, str]:
        """Extract anchor information from current and following lines."""

        # Look in current line and next few lines for the anchor tag
        combined_content = ""
        for i in range(start_index, min(len(lines), start_index + 10)):
            combined_content += lines[i] + " "

        # First try the original pattern (href and id in <a> tag)
        pattern = r'<a href="([^"]+)"[^>]*id="([^"]*)"[^>]*>\s*<span[^>]*>(.*?)</span>\s*</a>'
        match = re.search(pattern, combined_content, re.DOTALL)

        if match:
            href, element_id, title = match.groups()
            clean_title = unescape(title.strip())
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()

            return {
                'href': href.strip('/') or 'index',
                'title': clean_title,
                'element_id': element_id
            }

        # Alternative pattern: <a> tag and href might be on different lines
        pattern2 = r'<a[^>]*href="([^"]+)"[^>]*>\s*<span[^>]*>(.*?)</span>\s*</a>'
        match2 = re.search(pattern2, combined_content, re.DOTALL)

        if match2:
            href, title = match2.groups()
            clean_title = unescape(title.strip())
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()

            # Try to find id from the LI element
            id_match = re.search(r'id="([^"]*)"', combined_content)
            element_id = id_match.group(1) if id_match else ""

            return {
                'href': href.strip('/') or 'index',
                'title': clean_title,
                'element_id': element_id
            }

        return {}

    def _check_has_children(self, lines: List[str], li_index: int, current_depth: int) -> bool:
        """Check if this LI has children (contains nested UL)."""

        # Look ahead in the next several lines for a nested UL
        for i in range(li_index, min(len(lines), li_index + 50)):
            if f'<ul class="ul-{current_depth + 1}' in lines[i]:
                return True
            # Stop if we hit another LI at the same level or a closing UL
            if (re.search(r'<li[^>]*class="[^"]*td-sidebar-nav__section-title[^"]*"', lines[i]) and i > li_index) or '</ul>' in lines[i]:
                break

        return False

    def _build_complete_hierarchy(self) -> List[Dict[str, Any]]:
        """Build the complete hierarchical structure from all extracted items."""

        # Sort items by line index to maintain order
        self.all_items.sort(key=lambda x: x['line_index'])

        result = []
        stack = []  # Stack to track current nesting [(item, depth)]

        for item in self.all_items:
            current_depth = item['depth']

            # Adjust stack to current depth
            while stack and stack[-1][1] >= current_depth:
                stack.pop()

            if item['has_children']:
                # This is a group
                group_item = {
                    'group': item['title'],
                    'pages': []
                }

                if stack:
                    # Add to parent group
                    parent_group = stack[-1][0]
                    if 'pages' not in parent_group:
                        parent_group['pages'] = []
                    parent_group['pages'].append(group_item)
                else:
                    # Top-level group
                    result.append(group_item)

                # Push to stack
                stack.append((group_item, current_depth))
            else:
                # This is a regular page
                page_path = item['href']

                if stack:
                    # Add to current group
                    parent_group = stack[-1][0]
                    if 'pages' not in parent_group:
                        parent_group['pages'] = []
                    parent_group['pages'].append(page_path)
                else:
                    # Top-level page (shouldn't happen in this structure, but handle it)
                    result.append(page_path)

        return result


def create_mintlify_navigation(groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create Mintlify navigation structure."""
    return {
        'navigation': {
            'global': {},
            'languages': [
                {
                    'language': 'en',
                    'tabs': [
                        {
                            'tab': 'Platform',
                            'groups': groups if groups else [{
                                'group': 'Documentation',
                                'pages': []
                            }]
                        }
                    ]
                }
            ]
        }
    }


def count_items_recursive(items: List[Any]) -> int:
    """Count total items recursively."""
    count = 0
    for item in items:
        if isinstance(item, dict) and 'pages' in item:
            count += 1 + count_items_recursive(item['pages'])
        else:
            count += 1
    return count


def main():
    """Main function."""
    html_file = Path('index.html')
    if not html_file.exists():
        print(f"Error: {html_file} not found")
        return

    print(f"Reading navigation from {html_file}...")

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse complete navigation structure
    parser = CompleteNavigationParser()
    print("Parsing complete navigation structure...")
    groups = parser.parse_complete_navigation(html_content)

    print(f"Found {len(parser.all_items)} total navigation items")
    print(f"Organized into {len(groups)} top-level groups")

    # Convert to Mintlify format
    navigation = create_mintlify_navigation(groups)

    # Save result
    output_file = 'navigation_complete.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(navigation, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved to {output_file}")

    # Show detailed statistics
    tab = navigation['navigation']['languages'][0]['tabs'][0]
    total_items = count_items_recursive(tab['groups'])

    print(f"\n📊 Complete structure statistics:")
    print(f"Tab: {tab['tab']}")
    print(f"Top-level groups: {len(tab['groups'])}")
    print(f"Total items (groups + pages): {total_items}")

    def print_structure(items, indent=0, max_items=3):
        """Print structure with limited depth for readability."""
        prefix = "  " * indent
        for i, item in enumerate(items[:max_items]):
            if isinstance(item, dict) and 'group' in item:
                pages_count = len(item.get('pages', []))
                print(f"{prefix}{i+1}. Group: {item['group']} ({pages_count} items)")
                if item.get('pages') and indent < 2:  # Limit depth
                    print_structure(item['pages'], indent + 1, 2)
            elif isinstance(item, str):
                print(f"{prefix}{i+1}. Page: {item}")

        if len(items) > max_items:
            print(f"{prefix}... ({len(items) - max_items} more items)")

    print(f"\n📋 Structure preview:")
    print_structure(tab['groups'])


if __name__ == '__main__':
    main()