#!/bin/bash
# Script to benchmark inference speed on MLX vs. pure NumPy over all 154 fake sonnets

FAKE_DIR="orig_fake_sonnets"

if [ ! -d "$FAKE_DIR" ]; then
    echo "Directory $FAKE_DIR not found."
    exit 1
fi

echo "=================================================="
echo "BENCHMARKING INFERENCE: MLX VS. NUMPY"
echo "Target: 154 sonnets in $FAKE_DIR"
echo "=================================================="

# 1. Benchmark MLX Inference
echo "Running MLX inference..."
start_mlx=$(python3 -c "import time; print(time.perf_counter())")

for file in "$FAKE_DIR"/*.txt; do
    if [ -f "$file" ]; then
        # Run MLX classifier and suppress standard output (capture stderr if any)
        .venv/bin/python classify_sonnet.py "$file" > /dev/null
    fi
done

end_mlx=$(python3 -c "import time; print(time.perf_counter())")
mlx_time=$(awk "BEGIN {print $end_mlx - $start_mlx}")

# 2. Benchmark NumPy Inference
echo "Running NumPy inference..."
start_np=$(python3 -c "import time; print(time.perf_counter())")

for file in "$FAKE_DIR"/*.txt; do
    if [ -f "$file" ]; then
        # Run NumPy classifier and suppress standard output
        .venv/bin/python classify_sonnet_numpy.py "$file" > /dev/null
    fi
done

end_np=$(python3 -c "import time; print(time.perf_counter())")
np_time=$(awk "BEGIN {print $end_np - $start_np}")

# 3. Calculate metrics and print summary
avg_mlx=$(awk "BEGIN {print ($mlx_time * 1000) / 154}")
avg_np=$(awk "BEGIN {print ($np_time * 1000) / 154}")

echo "================================================--"
echo "INFERENCE BENCHMARK RESULTS:"
echo "--------------------------------------------------"
echo "MLX Total Time:      ${mlx_time} seconds"
echo "MLX Avg per Sonnet:  ${avg_mlx} ms"
echo "--------------------------------------------------"
echo "NumPy Total Time:    ${np_time} seconds"
echo "NumPy Avg per Sonnet: ${avg_np} ms"
echo "--------------------------------------------------"
ratio=$(awk "BEGIN {print $mlx_time / $np_time}")
echo "NumPy is ${ratio}x faster than MLX for single-text inference workloads."
echo "================================================--"
