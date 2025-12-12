#!/bin/bash

# Usage: ./w.sh <command> [args...]

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command> [args...]"
    exit 1
fi

# Determine the absolute path of the project directory
# This assumes w.sh is located in the project root
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Temporary file to store output
LOG_FILE=$(mktemp)

# Run the command using 'script' to preserve TTY behavior (colors, interactive apps).
# -q: Quiet mode (don't show start/done messages)
# -F: Flush output immediately (macOS specific, useful for real-time logging)
# The command output is saved to LOG_FILE and also shown on screen.
script -q -F "$LOG_FILE" "$@"
EXIT_CODE=$?

# Wait a moment for I/O to flush (just in case)
sleep 0.1

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "=================================================="
    echo "🚨 Command failed with exit code $EXIT_CODE"
    echo "🤖 Analyzing error with RAG Error Summarizer..."
    echo "=================================================="
    echo ""

    # Switch to project directory to run docker-compose
    pushd "$PROJECT_DIR" > /dev/null

    # Send the log file to the error summarizer
    # We use the interactive mode (passing filename) to enable feedback
    
    # Get container ID (safer than relying on name if multiple projects exist, though name is fixed now)
    CONTAINER_ID=$(docker-compose ps -q app)
    
    if [ -z "$CONTAINER_ID" ]; then
        echo "Error: Error Summarizer service is not running."
        echo "Please run 'docker-compose up -d' in $PROJECT_DIR"
    else
        docker cp "$LOG_FILE" "$CONTAINER_ID":/app/last_error.txt
        docker-compose exec app python src/main.py last_error.txt
    fi
    
    popd > /dev/null
    
    # Clean up
    rm "$LOG_FILE"
else
    rm "$LOG_FILE"
fi

exit $EXIT_CODE
