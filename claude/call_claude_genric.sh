#!/bin/bash

# --- Generic script to call Claude with a prompt from a file
# Usage: ./call_claude.sh <prompt_file>

# --- Input validation ---
if [ -z "$1" ]; then
  echo "Usage: $0 <prompt_file>"
  echo "Example: $0 prompt.txt"
  exit 1
fi

PROMPT_FILE="$1"

# --- File existence check ---
if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: File '$PROMPT_FILE' not found."
  exit 1
fi


# --- Run Claude and log output ---
echo "Sending prompt from '$PROMPT_FILE' to Claude..."

# cat "$PROMPT_FILE" | claude | tee "$LOG_FILE"
cat "$PROMPT_FILE" | claude 
