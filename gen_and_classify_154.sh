#!/bin/bash
# gen_and_classify_154.sh
# Batch generates 154 fake Elizabethan sonnets using generate_and_classify.chatdsl,
# classifies each sonnet using the MLX SVM model, and calculates the SVM success rate.

set -e

NUM_SONNETS="${1:-154}"
DSL_SCRIPT="generate_and_classify.chatdsl"
FRESH_DIR="fresh_sonnets"
PYTHON_BIN=".venv/bin/python"
MODEL_DIR="sonnet_data_mlx"

# Check prerequisites
if ! command -v chatybot &> /dev/null; then
    echo "Error: 'chatybot' CLI utility is not installed or not in PATH."
    exit 1
fi

if [ ! -f "$DSL_SCRIPT" ]; then
    echo "Error: DSL script '$DSL_SCRIPT' not found."
    exit 1
fi

if [ ! -d "$MODEL_DIR" ]; then
    echo "Error: MLX model directory '$MODEL_DIR' not found."
    exit 1
fi

mkdir -p "$FRESH_DIR"

echo "=================================================="
echo "Starting batch generation & classification of $NUM_SONNETS sonnets"
echo "DSL Script:        $DSL_SCRIPT"
echo "Output Directory:  $FRESH_DIR"
echo "Model Directory:   $MODEL_DIR"
echo "=================================================="

START_TIME=$(date +%s)

for (( i=1; i<=NUM_SONNETS; i++ )); do
    echo ""
    echo "--------------------------------------------------"
    echo "[$i/$NUM_SONNETS] Generating & Classifying Sonnet #$i..."
    echo "--------------------------------------------------"

    # Execute chatybot passing script variables seq and fresh_dir
    chatybot <<EOF
/script ${DSL_SCRIPT} seq="${i}" fresh_dir="${FRESH_DIR}"
/quit
EOF

    # Brief delay between API requests to respect rate limits
    sleep 2
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "=================================================="
echo "Batch Generation Complete in $ELAPSED seconds."
echo "Calculating overall SVM Classifier Success Rate..."
echo "=================================================="

# Evaluate all generated fake sonnets in FRESH_DIR
total=0
fake_count=0
real_count=0
mismatches=()

# Sort sonnet files naturally by sequence number
for file in $(ls -v "$FRESH_DIR"/fake_sonnet_*.txt 2>/dev/null); do
    if [ -f "$file" ]; then
        total=$((total + 1))
        res=$("$PYTHON_BIN" classify_sonnet.py "$file" --model_dir "$MODEL_DIR" 2>/dev/null || true)
        
        if echo "$res" | grep -q "Fake (Elizabethan-Mimicry)"; then
            fake_count=$((fake_count + 1))
        else
            real_count=$((real_count + 1))
            score=$(echo "$res" | grep "Raw SVM Score:" | awk '{print $4}')
            mismatches+=("$(basename "$file") (Score: $score)")
        fi
    fi
done

if [ "$total" -eq 0 ]; then
    echo "Error: No sonnet files found in $FRESH_DIR."
    exit 1
fi

# Calculate percentage accuracy
accuracy=$(awk "BEGIN {printf \"%.2f\", ($fake_count * 100 / $total)}")

echo ""
echo "=================================================="
echo "        SVM CLASSIFIER EVALUATION SUMMARY         "
echo "=================================================="
echo "Total Generated Sonnets Evaluated: $total"
echo "Correctly Classified as Fake:      $fake_count"
echo "Incorrectly Classified as Real:    $real_count"
echo "SVM Detection Success Rate:        ${accuracy}%"
echo "=================================================="

if [ ${#mismatches[@]} -gt 0 ]; then
    echo ""
    echo "Sonnets that fooled the SVM model (False Positives):"
    for item in "${mismatches[@]}"; do
        echo " - $item"
    done
fi

echo ""
