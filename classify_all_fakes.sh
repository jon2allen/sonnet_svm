#!/bin/bash
# Script to run classification on all fake sonnets and summarize the results

FAKE_DIR="orig_fake_sonnets"
MODEL_DIR="sonnet_data"

if [ ! -d "$FAKE_DIR" ]; then
    echo "Directory $FAKE_DIR not found."
    exit 1
fi

echo "Classifying all sonnets in $FAKE_DIR..."
total=0
fake_count=0
real_count=0

for file in "$FAKE_DIR"/*.txt; do
    if [ -f "$file" ]; then
        # Run classification
        res=$(.venv/bin/python classify_sonnet.py "$file" --model_dir "$MODEL_DIR")
        classification=$(echo "$res" | grep "Classification:")
        
        total=$((total+1))
        if echo "$classification" | grep -q "Fake"; then
            fake_count=$((fake_count+1))
        else
            real_count=$((real_count+1))
            basename=$(basename "$file")
            score=$(echo "$res" | grep "Raw SVM Score:")
            echo "Mismatch: $basename classified as Real! ($score)"
        fi
    fi
done

echo "--------------------------------------------------"
echo "SUMMARY OF RESULTS:"
echo "Total Classified: $total"
echo "Classified as Fake: $fake_count"
echo "Classified as Real: $real_count"
# Use awk for division to avoid dependency on bc
accuracy=$(awk "BEGIN {print ($fake_count * 100 / $total)}")
echo "Accuracy on Fake dataset: ${accuracy}%"
echo "--------------------------------------------------"
