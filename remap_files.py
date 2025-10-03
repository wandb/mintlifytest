#!/usr/bin/env python3
"""
Script to remap files based on remap_files.json.
Adds .mdx extension to source and destination paths and moves files accordingly.
"""

import json
import shutil
from pathlib import Path


def remap_files():
    # Load the remap configuration
    with open("remap_files.json", "r") as f:
        remaps = json.load(f)

    # Base directory (current directory)
    base_dir = Path.cwd()

    # Track statistics
    moved = 0
    skipped = 0
    errors = []

    for remap in remaps:
        # Remove leading slash and add .mdx extension
        source_path = base_dir / (remap["source"].lstrip("/") + ".mdx")
        dest_path = base_dir / (remap["destination"].lstrip("/") + ".mdx")

        # Check if source file exists
        if not source_path.exists():
            skipped += 1
            print(f"⚠️  Source not found: {source_path}")
            continue

        # Create destination directory if it doesn't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        try:
            shutil.move(str(source_path), str(dest_path))
            moved += 1
            print(
                f"✓ Moved: {source_path.relative_to(base_dir)} → {dest_path.relative_to(base_dir)}"
            )
        except Exception as e:
            errors.append((source_path, dest_path, str(e)))
            print(f"✗ Error moving {source_path}: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Files moved: {moved}")
    print(f"  Files skipped (not found): {skipped}")
    print(f"  Errors: {len(errors)}")

    if errors:
        print("\nErrors encountered:")
        for src, dst, err in errors:
            print(f"  {src} → {dst}: {err}")


if __name__ == "__main__":
    remap_files()
