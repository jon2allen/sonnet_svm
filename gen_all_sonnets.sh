#!/bin/bash

# Configuration - adjust these paths if needed
DATA_DIR="data"
DSL_SCRIPT="sonnet1.chatdsl"

# Verify that the data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory '${DATA_DIR}' does not exist."
    exit 1
fi

# Find all sonnet files matching the pattern
SONNET_FILES=("$DATA_DIR"/sonnet_*.txt)
TOTAL_FILES=${#SONNET_FILES[@]}

# Check if any matching files were found
if [ "$TOTAL_FILES" -eq 0 ] || [ ! -e "${SONNET_FILES[0]}" ]; then
    echo "No sonnets matching '${DATA_DIR}/sonnet_*.txt' were found."
    exit 1
fi

echo "=================================================="
echo "Found ${TOTAL_FILES} sonnet(s) to process."
echo "=================================================="

# Counter for tracking progress
CURRENT_COUNT=0

# Loop through each sonnet file
for filepath in "${SONNET_FILES[@]}"; do
    filename=$(basename "$filepath")
    ((CURRENT_COUNT++))
    
    echo ""
    echo "--------------------------------------------------"
    echo "[$CURRENT_COUNT/$TOTAL_FILES] Processing: $filename"
    echo "--------------------------------------------------"
    
    # Run chatybot, passing the script command and quitting immediately after
    chatybot <<EOF
/script ${DSL_SCRIPT} x="${filename}"
/quit
EOF

    # Optional: Brief sleep to avoid hitting API rate limits
    sleep 5 
done

echo ""
echo "=================================================="
echo "Finished processing all ${TOTAL_FILES} sonnets!"
echo "=================================================="

