#!/usr/bin/env python3
import os
import argparse
import pickle
import mlx.core as mx
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Classify a sonnet as Shakespeare (Real) or Elizabethan-Mimicry (Fake) using a trained MLX SVM model.")
    parser.add_argument("file", type=str, help="Path to the text file containing the sonnet to classify.")
    parser.add_argument("--model_dir", type=str, default="sonnet_data_mlx", help="Directory where model files are stored (default: sonnet_data_mlx).")
    
    args = parser.parse_args()
    
    # 1. Resolve model file paths
    vectorizer_path = os.path.join(args.model_dir, "svm_vectorizer.pkl")
    weights_path = os.path.join(args.model_dir, "svm_model_weights.npz")
    
    if not os.path.exists(vectorizer_path) or not os.path.exists(weights_path):
        print(f"Error: Model files not found in '{args.model_dir}'. Run train_svm.py first.")
        return
        
    if not os.path.exists(args.file):
        print(f"Error: Sonnet file not found at '{args.file}'.")
        return
        
    # 2. Load model components
    try:
        with open(vectorizer_path, "rb") as f:
            vectorizer = pickle.load(f)
            
        weights_dict = mx.load(weights_path)
        w = weights_dict["w"]
        b = weights_dict["b"]
        threshold = weights_dict["threshold"].item()
    except Exception as e:
        print(f"Error loading model: {e}")
        return
        
    # 3. Read input sonnet
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            sonnet_text = f.read()
    except Exception as e:
        print(f"Error reading sonnet file: {e}")
        return
        
    # 4. Extract features & perform inference in MLX
    X_np = vectorizer.transform([sonnet_text]).toarray()
    X = mx.array(X_np, mx.float32)
    
    # Compute decision value: w^T x + b
    score = mx.matmul(X, w) + b
    mx.eval(score)
    score_val = score.item()
    
    # Classify based on the optimized threshold
    prediction = "Real (Shakespeare)" if score_val >= threshold else "Fake (Elizabethan-Mimicry)"
    
    # 5. Display output
    print("=" * 50)
    print(f"SVM CLASSIFICATION REPORT FOR: {os.path.basename(args.file)}")
    print("=" * 50)
    print(f"Raw SVM Score:      {score_val:.4f}")
    print(f"Decision Boundary:  {threshold:.4f}")
    print(f"Classification:     {prediction}")
    print("=" * 50)

if __name__ == "__main__":
    main()
