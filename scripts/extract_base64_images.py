#!/usr/bin/env python3
import re
import base64
import os
from pathlib import Path
import sys

def extract_base64_images(file_path, output_dir):
    """Extract base64 images from a markdown file and save them as PNG files."""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match markdown images with base64 data
    # Match the full base64 string including the truncated part
    pattern = r'!\[([^\]]*)\]\(([^)]*?)(data:image/(?:png|jpeg|gif);base64,)([^)]+)\)'
    
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print(f"No base64 images found in {file_path}")
        return content, 0
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    updated_content = content
    extracted_count = 0
    
    for i, match in enumerate(matches):
        alt_text = match.group(1)
        path_prefix = match.group(2)  # e.g., "/images/cookbooks/"
        data_prefix = match.group(3)  # e.g., "data:image/png;base64,"
        base64_data = match.group(4)
        
        # Generate filename based on alt text or index
        if alt_text:
            # Clean alt text for filename
            filename = re.sub(r'[^\w\s-]', '', alt_text).strip()
            filename = re.sub(r'[-\s]+', '-', filename).lower()
            if not filename:
                filename = f"image_{i+1}"
        else:
            filename = f"image_{i+1}"
        
        # Extract extension from data prefix
        ext = 'png'
        if 'jpeg' in data_prefix:
            ext = 'jpg'
        elif 'gif' in data_prefix:
            ext = 'gif'
        
        filename = f"{filename}.{ext}"
        filepath = os.path.join(output_dir, filename)
        
        # Check if file already exists and create unique name
        counter = 1
        while os.path.exists(filepath):
            filename = f"{filename.rsplit('.', 1)[0]}_{counter}.{ext}"
            filepath = os.path.join(output_dir, filename)
            counter += 1
        
        try:
            # Decode and save the image
            # Handle truncated base64 (add padding if needed)
            padded_data = base64_data
            padding = len(padded_data) % 4
            if padding:
                padded_data += '=' * (4 - padding)
            
            img_data = base64.b64decode(padded_data)
            with open(filepath, 'wb') as img_file:
                img_file.write(img_data)
            
            print(f"Saved: {filepath}")
            extracted_count += 1
            
            # Replace in content with proper markdown image reference
            relative_path = os.path.relpath(filepath, os.path.dirname(file_path))
            new_image_ref = f"![{alt_text}]({relative_path})"
            updated_content = updated_content.replace(match.group(0), new_image_ref)
            
        except Exception as e:
            print(f"Error processing image {i+1} in {file_path}: {e}")
            # For truncated images, just use a placeholder path
            relative_path = os.path.relpath(os.path.join(output_dir, filename), os.path.dirname(file_path))
            new_image_ref = f"![{alt_text}]({relative_path})"
            updated_content = updated_content.replace(match.group(0), new_image_ref)
    
    return updated_content, extracted_count

def process_files():
    """Process all files with base64 images."""
    
    files_to_process = [
        ("cookbooks/multi-agent-structured-output.mdx", "media/multi-agent-structured-output"),
        ("cookbooks/ocr-pipeline.mdx", "media/ocr-pipeline"),
        ("cookbooks/import_from_csv.mdx", "media/import-from-csv"),
        ("ko/cookbooks/multi-agent-structured-output.mdx", "media/multi-agent-structured-output"),
        ("ko/cookbooks/ocr-pipeline.mdx", "media/ocr-pipeline"),
        ("ko/cookbooks/import_from_csv.mdx", "media/import-from-csv"),
        ("ja/cookbooks/multi-agent-structured-output.mdx", "media/multi-agent-structured-output"),
        ("ja/cookbooks/ocr-pipeline.mdx", "media/ocr-pipeline"),
        ("ja/cookbooks/import_from_csv.mdx", "media/import-from-csv"),
    ]
    
    total_extracted = 0
    
    for file_path, output_dir in files_to_process:
        if os.path.exists(file_path):
            print(f"\nProcessing {file_path}...")
            updated_content, count = extract_base64_images(file_path, output_dir)
            
            if count > 0:
                # Write the updated content back
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                print(f"Updated {file_path} - extracted {count} images")
                total_extracted += count
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nTotal images extracted: {total_extracted}")

if __name__ == "__main__":
    process_files() 