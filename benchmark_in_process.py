#!/usr/bin/env python3
import time
import pickle
import numpy as np
import mlx.core as mx

def load_sonnets(directory):
    import os
    texts = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                texts.append(f.read())
    return texts

def main():
    # Load MLX model
    with open("sonnet_data_mlx/svm_vectorizer.pkl", "rb") as f:
        vectorizer_mlx = pickle.load(f)
    weights_dict = mx.load("sonnet_data_mlx/svm_model_weights.npz")
    w_mlx = weights_dict["w"]
    b_mlx = weights_dict["b"]
    
    # Load NumPy model
    with open("sonnet_data_numpy/svm_numpy_model.pkl", "rb") as f:
        model_data = pickle.load(f)
    vectorizer_np = model_data["vectorizer"]
    w_np = model_data["w"]
    b_np = model_data["b"]

    texts = load_sonnets("orig_fake_sonnets")
    print(f"Benchmarking in-process inference on {len(texts)} texts...")

    # Warmup
    for _ in range(5):
        # MLX warmup
        X_np = vectorizer_mlx.transform([texts[0]]).toarray()
        X = mx.array(X_np, mx.float32)
        score = mx.matmul(X, w_mlx) + b_mlx
        mx.eval(score)
        # NumPy warmup
        X_np_np = vectorizer_np.transform([texts[0]]).toarray()
        _ = np.dot(X_np_np, w_np) + b_np

    # 1. Benchmark MLX
    start_mlx = time.perf_counter()
    for text in texts:
        X_np = vectorizer_mlx.transform([text]).toarray()
        X = mx.array(X_np, mx.float32)
        score = mx.matmul(X, w_mlx) + b_mlx
        mx.eval(score)
        _ = score.item()
    end_mlx = time.perf_counter()
    mlx_time = end_mlx - start_mlx

    # 2. Benchmark NumPy
    start_np = time.perf_counter()
    for text in texts:
        X_np_np = vectorizer_np.transform([text]).toarray()
        score = np.dot(X_np_np, w_np) + b_np
        _ = score.item()
    end_np = time.perf_counter()
    np_time = end_np - start_np

    print("--------------------------------------------------")
    print(f"MLX In-Process Total:    {mlx_time * 1000:.3f} ms (Avg: {mlx_time * 1000 / len(texts):.3f} ms/doc)")
    print(f"NumPy In-Process Total:  {np_time * 1000:.3f} ms (Avg: {np_time * 1000 / len(texts):.3f} ms/doc)")
    print(f"NumPy is {mlx_time / np_time:.2f}x faster in-process.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
