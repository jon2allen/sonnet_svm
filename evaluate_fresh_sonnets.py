#!/usr/bin/env python3
"""
evaluate_fresh_sonnets.py

Evaluates generated fake sonnets in a target directory (default: fresh_sonnets_test),
computing how many are correctly classified as Fake (Elizabethan-Mimicry) vs Real (Shakespeare).
Supports reading pre-computed analysis reports or running direct MLX SVM model inference in-process.
"""

import os
import re
import sys
import argparse
import pickle
import numpy as np

def load_mlx_model(model_dir="sonnet_data_mlx"):
    """Loads vectorizer and MLX model weights if available."""
    try:
        import mlx.core as mx
    except ImportError:
        return None, None, None, None

    vectorizer_path = os.path.join(model_dir, "svm_vectorizer.pkl")
    weights_path = os.path.join(model_dir, "svm_model_weights.npz")

    if not os.path.exists(vectorizer_path) or not os.path.exists(weights_path):
        return None, None, None, None

    try:
        with open(vectorizer_path, "rb") as f:
            vectorizer = pickle.load(f)
        weights_dict = mx.load(weights_path)
        w = weights_dict["w"]
        b = weights_dict["b"]
        threshold = weights_dict["threshold"].item()
        return vectorizer, w, b, threshold
    except Exception as e:
        print(f"Warning: Could not load MLX model components: {e}")
        return None, None, None, None

def classify_text_in_memory(text, vectorizer, w, b, threshold):
    """Performs in-memory inference on a sonnet string using MLX."""
    import mlx.core as mx
    X_np = vectorizer.transform([text]).toarray()
    X = mx.array(X_np, mx.float32)
    score = mx.matmul(X, w) + b
    mx.eval(score)
    score_val = score.item()
    pred = "Fake (Elizabethan-Mimicry)" if score_val < threshold else "Real (Shakespeare)"
    return score_val, threshold, pred

def natural_sort_key(s):
    """Sort key for natural sorting (e.g. fake_sonnet_2 before fake_sonnet_10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def main():
    parser = argparse.ArgumentParser(description="Evaluate classification results for fresh_sonnets_test directory.")
    parser.add_argument("--dir", type=str, default="fresh_sonnets_test", help="Target directory containing sonnet files and analysis reports (default: fresh_sonnets_test).")
    parser.add_argument("--model_dir", type=str, default="sonnet_data_mlx", help="MLX SVM model directory (default: sonnet_data_mlx).")
    parser.add_argument("--reclassify", action="store_true", help="Force re-running MLX SVM model inference on all sonnets directly.")

    args = parser.parse_args()

    target_dir = args.dir
    if not os.path.exists(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    # Find all fake sonnet files (excluding analysis files and seq.txt)
    all_files = sorted(os.listdir(target_dir), key=natural_sort_key)
    sonnet_files = [f for f in all_files if f.startswith("fake_sonnet_") and f.endswith(".txt") and not f.endswith("_analysis.txt")]

    if not sonnet_files:
        print(f"No sonnet files matching 'fake_sonnet_*.txt' found in '{target_dir}'.")
        sys.exit(1)

    print("=" * 65)
    print(f"EVALUATING SVM CLASSIFICATION ON DATASET: {target_dir}")
    print("=" * 65)
    print(f"Total Sonnet Files Found: {len(sonnet_files)}")

    vectorizer, w, b, threshold = None, None, None, None
    if args.reclassify:
        print("Mode: In-Memory MLX Model Inference (--reclassify specified)")
        vectorizer, w, b, threshold = load_mlx_model(args.model_dir)
        if vectorizer is None:
            print("Error: Could not load MLX model for --reclassify. Exiting.")
            sys.exit(1)
    else:
        print("Mode: Parsing Existing Analysis Reports (with In-Memory Fallback)")

    results = []

    for filename in sonnet_files:
        seq_match = re.search(r"fake_sonnet_(\d+)\.txt", filename)
        seq_num = int(seq_match.group(1)) if seq_match else 0
        
        filepath = os.path.join(target_dir, filename)
        analysis_filename = f"fake_sonnet_{seq_num}_analysis.txt"
        analysis_filepath = os.path.join(target_dir, analysis_filename)

        score_val = None
        thresh_val = None
        prediction = None
        source = ""

        # Option A: Parse existing analysis report if not forcing reclassification
        if not args.reclassify and os.path.exists(analysis_filepath):
            try:
                with open(analysis_filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                score_m = re.search(r"Raw SVM Score:\s*([-\d.]+)", content)
                thresh_m = re.search(r"Decision Boundary:\s*([-\d.]+)", content)
                class_m = re.search(r"Classification:\s*(.+)", content)

                if score_m and class_m:
                    score_val = float(score_m.group(1))
                    thresh_val = float(thresh_m.group(1)) if thresh_m else 0.8800
                    prediction = class_m.group(1).strip()
                    source = "report"
            except Exception as e:
                pass

        # Option B: Run in-memory model inference if report missing or --reclassify requested
        if prediction is None:
            if vectorizer is None:
                vectorizer, w, b, threshold = load_mlx_model(args.model_dir)

            if vectorizer is not None:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        sonnet_text = f.read()
                    score_val, thresh_val, prediction = classify_text_in_memory(sonnet_text, vectorizer, w, b, threshold)
                    source = "inference"
                except Exception as e:
                    print(f"Error classifying {filename}: {e}")

        if prediction is not None:
            is_fake = "Fake" in prediction
            results.append({
                "filename": filename,
                "seq": seq_num,
                "score": score_val,
                "threshold": thresh_val,
                "prediction": prediction,
                "is_fake": is_fake,
                "source": source
            })

    if not results:
        print("Error: Could not parse or evaluate any sonnets.")
        sys.exit(1)

    # Compute aggregate statistics
    total_evaluated = len(results)
    fake_detected = sum(1 for r in results if r["is_fake"])
    real_mismatches = sum(1 for r in results if not r["is_fake"])
    accuracy = (fake_detected / total_evaluated) * 100.0

    scores = [r["score"] for r in results if r["score"] is not None]

    print("\n" + "=" * 65)
    print("                      SUMMARY RESULTS                       ")
    print("=" * 65)
    print(f"Total Sonnets Evaluated:           {total_evaluated}")
    print(f"Correctly Detected as Fake:        {fake_detected} ({accuracy:.2f}%)")
    print(f"Incorrectly Classified as Real:    {real_mismatches} ({(100 - accuracy):.2f}%)")
    print(f"SVM Detection Success Rate:        {accuracy:.2f}%")
    print("-" * 65)

    if scores:
        print(f"Score Distribution:")
        print(f"  - Min SVM Score:                 {min(scores):.4f}")
        print(f"  - Max SVM Score:                 {max(scores):.4f}")
        print(f"  - Mean SVM Score:                {np.mean(scores):.4f}")
        if results[0]["threshold"] is not None:
            print(f"  - Decision Boundary Threshold:   {results[0]['threshold']:.4f}")
    print("=" * 65)

    # Calculate distance to decision boundary for each sonnet
    # Distance = abs(score - boundary). The smaller the distance, the closer to flipping classification!
    for r in results:
        b = r["threshold"] if r["threshold"] is not None else 0.8800
        r["boundary_dist"] = abs(r["score"] - b) if r["score"] is not None else float('inf')

    # Sort sonnets by boundary distance (closest first)
    closest_sorted = sorted(results, key=lambda x: x["boundary_dist"])

    # Print table of mismatches (sonnets that fooled the model)
    mismatch_items = [r for r in results if not r["is_fake"]]
    if mismatch_items:
        print("\n" + "!" * 65)
        print("MISMATCHES: Sonnets Classified as Real (Shakespeare)")
        print("!" * 65)
        print(f"{'Filename':<25} | {'Raw Score':<10} | {'Decision Boundary':<18} | {'Prediction':<20}")
        print("-" * 65)
        for m in mismatch_items:
            print(f"{m['filename']:<25} | {m['score']:<10.4f} | {m['threshold']:<18.4f} | {m['prediction']:<20}")
        print("!" * 65)
    else:
        print("\nPerfect Score! All evaluated sonnets were correctly detected as Fake.")

    # Display Top 5 Sonnets Closest to Decision Boundary
    print("\n" + "=" * 65)
    print("      SONNETS CLOSEST TO DECISION BOUNDARY (MOST AMBIGUOUS)      ")
    print("=" * 65)
    print(f"{'Rank':<5} | {'Filename':<20} | {'Raw Score':<10} | {'Boundary':<10} | {'Margin / Dist':<12}")
    print("-" * 65)
    for idx, item in enumerate(closest_sorted[:5], 1):
        print(f"{idx:<5} | {item['filename']:<20} | {item['score']:<10.4f} | {item['threshold']:<10.4f} | {item['boundary_dist']:<12.4f}")
    print("=" * 65)

    # Print full text for Top 2 closest sonnets
    print("\n" + "*" * 65)
    print("          TOP 2 SONNETS CLOSEST TO DECISION BOUNDARY            ")
    print("*" * 65)
    for idx, item in enumerate(closest_sorted[:2], 1):
        filepath = os.path.join(target_dir, item['filename'])
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read().strip()
        except Exception:
            text = "(Could not read file text)"

        print(f"\n--- [#{idx} Closest to Boundary] {item['filename']} ---")
        print(f"Raw SVM Score: {item['score']:.4f} (Boundary: {item['threshold']:.4f}, Margin: {item['boundary_dist']:.4f})")
        print(f"Classification: {item['prediction']}\n")
        print(text)
        print("-" * 65)

if __name__ == "__main__":
    main()
