#!/usr/bin/env python3
import os
import requests
import re
from pathlib import Path

# Map of our directory structure to Weave's structure
PATH_MAPPINGS = {
    'guides/tracking/imgs/': 'docs/docs/guides/tracking/imgs/',
    'guides/core-types/imgs/': 'docs/docs/guides/core-types/imgs/',
    'guides/integrations/imgs/': 'docs/docs/guides/integrations/imgs/',
    'guides/evaluation/img/': 'docs/docs/guides/evaluation/img/',
    'guides/tools/imgs/': 'docs/docs/guides/tools/imgs/',
}

# Parse the broken links file to get missing images
missing_images = {}
current_file = None

with open('broken-links-images.txt', 'r') as f:
    for line in f:
        # Match file paths
        if line.strip() and not line.startswith(' ') and '.mdx' in line:
            current_file = line.strip()
        # Match missing image references
        elif line.strip().startswith('⎿') and current_file:
            match = re.search(r'⎿\s+(.+\.(png|gif))', line)
            if match:
                image_path = match.group(1)
                if current_file not in missing_images:
                    missing_images[current_file] = []
                missing_images[current_file].append(image_path)

# Track statistics
downloaded = 0
skipped = 0
failed = 0

# Process each file and its missing images
for mdx_file, images in missing_images.items():
    print(f"\nProcessing {mdx_file}:")
    
    for image_path in images:
        # Skip absolute paths and special cases
        if image_path.startswith('/'):
            print(f"  ⚠️  Skipping absolute path: {image_path}")
            skipped += 1
            continue
            
        # Determine the target directory based on the MDX file location
        mdx_dir = os.path.dirname(mdx_file)
        target_path = os.path.join(mdx_dir, image_path)
        target_dir = os.path.dirname(target_path)
        
        # Create target directory if it doesn't exist
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            print(f"  📁 Created directory: {target_dir}")
        
        # Try to find the corresponding path in Weave repo
        weave_path = None
        for our_prefix, weave_prefix in PATH_MAPPINGS.items():
            if target_path.startswith(our_prefix):
                weave_path = target_path.replace(our_prefix, weave_prefix)
                break
        
        if not weave_path:
            # Try to guess the path
            if 'guides/' in target_path:
                weave_path = 'docs/docs/' + target_path
            else:
                print(f"  ⚠️  Could not map path: {image_path}")
                skipped += 1
                continue
        
        # Construct the GitHub raw URL
        url = f"https://raw.githubusercontent.com/wandb/weave/master/{weave_path}"
        
        try:
            print(f"  🔍 Fetching: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Save the image
                with open(target_path, 'wb') as f:
                    f.write(response.content)
                print(f"  ✅ Downloaded: {image_path} -> {target_path}")
                downloaded += 1
            else:
                print(f"  ❌ Failed (HTTP {response.status_code}): {image_path}")
                failed += 1
        except Exception as e:
            print(f"  ❌ Error downloading {image_path}: {str(e)}")
            failed += 1

# Clean up
os.remove('broken-links-images.txt')

print(f"\n✨ Done!")
print(f"📊 Summary: {downloaded} downloaded, {skipped} skipped, {failed} failed") 