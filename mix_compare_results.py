#!/usr/bin/env python3
import os
import re
import sys

def main():
    # Define directories and files - use current working directory
    project_dir = "."
    manifest_path = os.path.join(project_dir, "mix_sonnet/manifest.txt")
    anal_dir = os.path.join(project_dir, "anal8")

    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file not found at {manifest_path}")
        sys.exit(1)
        
    if not os.path.exists(anal_dir):
        print(f"Error: Analysis directory not found at {anal_dir}")
        sys.exit(1)

    # 1. Parse ground truth from manifest.txt
    ground_truth = {}
    print(f"Loading manifest from {manifest_path}...")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Example format: "copying:  data/sonnet_CIX.txt" or "copying:  fake_sonnet/sonnet_XII.txt"
            match = re.search(r"copying:\s+(data|fake_sonnet)/sonnet_([A-Z]+)\.txt", line)
            if match:
                source, roman = match.groups()
                ground_truth[roman.upper()] = "Real" if source == "data" else "Fake"

    print(f"Found {len(ground_truth)} sonnet definitions in the manifest.")

    # 2. Parse predictions from anal8 directory
    predictions = {}
    unparseable = []
    
    print(f"Parsing classification files from {anal_dir}...")
    for filename in sorted(os.listdir(anal_dir)):
        if filename.startswith("analysis_1_sonnet_") and filename.endswith(".txt"):
            match = re.search(r"analysis_1_sonnet_([A-Z]+)\.txt", filename)
            if match:
                roman = match.group(1).upper()
                filepath = os.path.join(anal_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
                    continue
                
                # Look for "Shakespeare: True" or "Shakespeare: False"
                lbl_match = re.search(r"Shakespeare:\s*(True|False)", content, re.IGNORECASE)
                if lbl_match:
                    lbl = lbl_match.group(1).strip().capitalize()
                    predictions[roman] = "Real" if lbl == "True" else "Fake"
                else:
                    predictions[roman] = "Unknown"
                    unparseable.append(roman)

    print(f"Found {len(predictions)} analysis files in {anal_dir}.")

    # 3. Compare and compute metrics
    tp = 0  # Real classified as Real (Shakespeare: True)
    fn = 0  # Real classified as Fake (Shakespeare: False)
    tn = 0  # Fake classified as Fake (Shakespeare: False)
    fp = 0  # Fake classified as Real (Shakespeare: True)
    unknowns = 0
    mismatches = []
    
    # We evaluate all sonnets that have predictions
    evaluated = 0
    for roman, pred in predictions.items():
        if roman not in ground_truth:
            # Prediction for a sonnet not in manifest
            continue
            
        actual = ground_truth[roman]
        evaluated += 1
        
        if pred == "Unknown":
            unknowns += 1
            mismatches.append((roman, actual, "Unknown (Unparseable)"))
        elif actual == "Real" and pred == "Real":
            tp += 1
        elif actual == "Real" and pred == "Fake":
            fn += 1
            mismatches.append((roman, "Real", "Fake"))
        elif actual == "Fake" and pred == "Fake":
            tn += 1
        elif actual == "Fake" and pred == "Real":
            fp += 1
            mismatches.append((roman, "Fake", "Real"))

    # Compute statistics
    correct = tp + tn
    total_valid = tp + tn + fp + fn
    accuracy = correct / total_valid if total_valid > 0 else 0.0
    
    precision_real = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall_real = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_real = 2 * precision_real * recall_real / (precision_real + recall_real) if (precision_real + recall_real) > 0 else 0.0
    
    precision_fake = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    recall_fake = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1_fake = 2 * precision_fake * recall_fake / (precision_fake + recall_fake) if (precision_fake + recall_fake) > 0 else 0.0

    # 4. Generate the report
    report = []
    report.append("==================================================")
    report.append("🏆 LLM Classification Accuracy vs Ground Truth Manifest 🏆")
    report.append("==================================================")
    report.append(f"Total Sonnets in Manifest:  {len(ground_truth)}")
    report.append(f"Total Analysis Files Found: {len(predictions)}")
    report.append(f"Total Evaluated Matches:    {evaluated}")
    report.append("")
    report.append("📊 Confusion Matrix & Statistics")
    report.append("--------------------------------------------------")
    report.append(f"True Positives (Real -> Real):   {tp}")
    report.append(f"True Negatives (Fake -> Fake):   {tn}")
    report.append(f"False Positives (Fake -> Real):  {fp}  (Model fell for the mimicry!)")
    report.append(f"False Negatives (Real -> Fake):  {fn}  (Model rejected authentic Shakespeare!)")
    report.append(f"Unparseable Classifications:    {unknowns}")
    report.append("--------------------------------------------------")
    report.append(f"Overall Accuracy:                {accuracy:.2%} ({correct}/{total_valid})")
    report.append("")
    report.append("📈 Style-Specific Performance Metrics")
    report.append("--------------------------------------------------")
    report.append("AUTHENTIC SHAKESPEARE (Real) Detection:")
    report.append(f"  Precision: {precision_real:.2%}")
    report.append(f"  Recall:    {recall_real:.2%}")
    report.append(f"  F1 Score:  {f1_real:.4f}")
    report.append("")
    report.append("ELIZABETHAN MIMICRY (Fake) Detection:")
    report.append(f"  Precision: {precision_fake:.2%}")
    report.append(f"  Recall:    {recall_fake:.2%}")
    report.append(f"  F1 Score:  {f1_fake:.4f}")
    report.append("--------------------------------------------------")
    
    if mismatches:
        report.append("")
        report.append("❌ Detailed Mismatches List")
        report.append("--------------------------------------------------")
        report.append(f"{'Sonnet':<10} | {'Actual':<10} | {'Model Prediction':<20}")
        report.append("-" * 48)
        for roman, actual, pred in sorted(mismatches):
            report.append(f"{roman:<10} | {actual:<10} | {pred:<20}")
        report.append("--------------------------------------------------")
        
    final_output = "\n".join(report)
    print(final_output)

    # Save output to a text file for records
    output_path = os.path.join(project_dir, "accuracy_comparison_report.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"\nReport saved to: {output_path}")

if __name__ == "__main__":
    main()
