#!/bin/bash

# Exit if any command fails
set -e

# --- Input validation ---
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <filename> <prompt_file>"
  exit 1
fi

# Get the full path of the input file
INPUT_FILE="$(realpath "$1")"

# Get the full path of the prompt file
PROMPT_FILE="$(realpath "$2")"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File '$INPUT_FILE' not found."
  exit 1
fi

# --- Prepare output filename ---
OUTPUT_FILE="vale_output.txt"

# --- Run Vale and strip ANSI escape sequences ---
echo "Running Vale on '$INPUT_FILE'..."
vale "$INPUT_FILE" | sed -r "s/\x1B\[[0-9;]*[mK]//g" > "$OUTPUT_FILE"

echo "Vale output saved to '$OUTPUT_FILE'."

# --- Read the prompt from the file ---
PROMPT=$(cat "$PROMPT_FILE")

# Call Claude CLI with the prompt
echo "$PROMPT" | claude

