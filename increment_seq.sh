#!/bin/bash

# Check if seq.txt exists, if not create it with 0
if [ ! -f seq.txt ]; then
    echo "0" > seq.txt
fi

# Read the current value
current_value=$(cat seq.txt)

# Increment the value by 1
new_value=$((current_value + 1))

# Write the new value back to seq.txt
echo "$new_value" > seq.txt

echo "$new_value"