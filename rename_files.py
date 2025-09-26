#!/usr/bin/env python3
"""
Script to rename files by removing uppercase characters from filenames.
Processes all files in a given folder and its subfolders.
"""

import os
import sys
from pathlib import Path


def remove_uppercase_from_filename(filename):
    """Convert filename to lowercase, preserving the file extension."""
    name, ext = os.path.splitext(filename)
    return name.lower() + ext.lower()


def rename_files_in_directory(folder_path):
    """
    Rename all files in the given folder and subfolders to remove uppercase characters.

    Args:
        folder_path (str): Path to the folder to process
    """
    folder_path = Path(folder_path)

    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return False

    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return False

    renamed_count = 0
    error_count = 0

    # Walk through all files and subdirectories
    for root, _, files in os.walk(folder_path):
        root_path = Path(root)

        for filename in files:
            old_filepath = root_path / filename
            new_filename = remove_uppercase_from_filename(filename)
            new_filepath = root_path / new_filename

            # Skip if filename doesn't need to change
            if filename == new_filename:
                continue

            # Check if target file already exists
            if new_filepath.exists():
                print(
                    f"Warning: Cannot rename '{old_filepath}' - target '{new_filepath}' already exists"
                )
                error_count += 1
                continue

            try:
                old_filepath.rename(new_filepath)
                print(f"Renamed: {old_filepath} -> {new_filepath}")
                renamed_count += 1
            except OSError as e:
                print(f"Error renaming '{old_filepath}': {e}")
                error_count += 1

    print("\nSummary:")
    print(f"Files renamed: {renamed_count}")
    print(f"Errors: {error_count}")

    return error_count == 0


def main():
    # Set your folder path here
    folder_path = "/home/raeder/mintlify/wandb/mintlify-wandb-docs/ref/python/public-api"  # Change this to your target folder

    print(f"Processing folder: {folder_path}")
    print("This will rename all files to remove uppercase characters.")

    # Ask for confirmation
    confirm = input("Do you want to continue? (y/N): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Operation cancelled.")
        sys.exit(0)

    success = rename_files_in_directory(folder_path)

    if success:
        print("All files processed successfully!")
    else:
        print("Some errors occurred during processing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
