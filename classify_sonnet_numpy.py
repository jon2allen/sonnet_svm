#!/usr/bin/env python3
import os
import argparse
import pickle
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Classify a sonnet as Shakespeare (Real) or Elizabethan-Mimicry (Fake) using a trained NumPy SVM model.")
    parser.add_argument("file", type=str, help="Path to the text file containing the sonnet to classify.")
    parser.add_argument("--model_file", type=str, default="sonnet_data_numpy/svm_numpy_model.pkl", help="Path to the pickled NumPy model.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model_file):
        print(f"Error: NumPy model file not found at '{args.model_file}'. Run svm_training_nomlx.py first.")
        return
        
    if not os.path.exists(args.file):
        print(f"Error: Sonnet file not found at '{args.file}'.")
        return
        
    # 1. Load model components
    try:
        with open(args.model_file, "rb") as f:
            model_data = pickle.load(f)
            
        vectorizer = model_data["vectorizer"]
        w = model_data["w"]
        b = model_data["b"]
        threshold = model_data["threshold"]
    except Exception as e:
        print(f"Error loading model: {e}")
        return
        
    # 2. Read input sonnet
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            sonnet_text = f.read()
    except Exception as e:
        print(f"Error reading sonnet file: {e}")
        return
        
    # 3. Extract features & perform inference in NumPy
    X = vectorizer.transform([sonnet_text]).toarray()
    
    # Compute decision value: w^T x + b
    score_val = np.dot(X, w).item() + b
    
    # Classify based on the optimized threshold
    prediction = "Real (Shakespeare)" if score_val >= threshold else "Fake (Elizabethan-Mimicry)"
    
    # 4. Display output
    print("=" * 50)
    print(f"NUMPY SVM CLASSIFICATION REPORT FOR: {os.path.basename(args.file)}")
    print("=" * 50)
    print(f"Raw SVM Score:      {score_val:.4f}")
    print(f"Decision Boundary:  {threshold:.4f}")
    print(f"Classification:     {prediction}")
    print("=" * 50)

if __name__ == "__main__":
    main()
