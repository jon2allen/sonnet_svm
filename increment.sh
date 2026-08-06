#!/bin/bash
# increment.sh
# Increments a sequence counter in a specified directory and prints the new value.

DIR="${1:-fresh_sonnets}"
mkdir -p "$DIR"
SEQ_FILE="$DIR/seq.txt"

# Initialize if file does not exist or is empty
if [ ! -f "$SEQ_FILE" ] || [ ! -s "$SEQ_FILE" ]; then
    echo "0" > "$SEQ_FILE"
fi

VAL=$(cat "$SEQ_FILE")

# Ensure it's a valid integer
if ! [[ "$VAL" =~ ^[0-9]+$ ]]; then
    VAL=0
fi

NEW_VAL=$((VAL + 1))
echo "$NEW_VAL" > "$SEQ_FILE"

# Print new value to stdout without trailing newline
printf "%s" "$NEW_VAL"
