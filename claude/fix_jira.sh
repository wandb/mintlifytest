#!/bin/bash

# --- Generic script to call Claude with a prompt from a file
# Usage: ./fix_jira.sh <prompt_file> <jira_ticket_number>

# --- Input validation ---
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <prompt_file> <jira_ticket_number>"
  echo "Example: $0 prompt.txt 'Fix the bug in the login flow'"
  exit 1
fi

PROMPT_FILE="$1"
JIRA_TICKET_NUMBER="$2"

bash jira-api.sh get-issue "$JIRA_TICKET_NUMBER" > jira_ticket_info.txt

# -- Cat the prompt file and pipe it to Claude
echo -e "$(cat "$PROMPT_FILE")\n\n$(cat jira_ticket_info.txt)" | claude 
