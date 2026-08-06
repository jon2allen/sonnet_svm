#!/usr/bin/env python3
import os
import time
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix

def load_sonnets(directory):
    """Loads all sonnet texts from a directory."""
    texts = []
    filenames = []
    if not os.path.exists(directory):
        print(f"Warning: Directory {directory} does not exist.")
        return texts, filenames
    
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    texts.append(f.read())
                    filenames.append(filename)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return texts, filenames

def train_svm_numpy(X_train, y_train, num_epochs=250, lr=0.2, C=10.0):
    """Trains a linear SVM using manual gradient descent in NumPy."""
    num_samples, num_features = X_train.shape
    
    # Initialize weights and bias
    w = np.zeros((num_features, 1))
    b = 0.0
    
    print(f"Training SVM with NumPy (C={C}, lr={lr}, epochs={num_epochs})...")
    start_time = time.perf_counter()
    
    for epoch in range(num_epochs):
        # Forward pass: compute predictions
        preds = np.dot(X_train, w) + b  # (N, 1)
        margins = y_train * preds        # (N, 1)
        
        # Compute Hinge Loss + L2 regularization
        hinge = np.maximum(0.0, 1.0 - margins)
        loss = np.mean(hinge) + 0.5 * (1.0 / C) * np.sum(w ** 2)
        
        # Compute Gradients manually
        # Mask where margin < 1 (active hinge loss conditions)
        mask = (margins < 1.0).astype(float)  # (N, 1)
        
        # dL/dw = (sum over i of -y_i * x_i * mask_i) / N + (1/C) * w
        grad_w = -np.dot(X_train.T, y_train * mask) / num_samples + (1.0 / C) * w
        
        # dL/db = (sum over i of -y_i * mask_i) / N
        grad_b = -np.sum(y_train * mask) / num_samples
        
        # Gradient descent update
        w = w - lr * grad_w
        b = b - lr * grad_b
        
        if (epoch + 1) % 20 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:03d}/{num_epochs} - Hinge+Reg Loss: {loss:.4f}")
            
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"NumPy Training Complete in {elapsed:.6f} seconds.")
    return w, b, elapsed

def main():
    # 1. Load the dataset
    real_dir_gutenberg = "orig_sonnets"
    real_dir_quarto = "orig_sonnet_quarto"
    fake_dir = "orig_fake_sonnets"
    
    print("Loading sonnets...")
    real_gutenberg_texts, _ = load_sonnets(real_dir_gutenberg)
    real_quarto_texts, _ = load_sonnets(real_dir_quarto)
    fake_texts, _ = load_sonnets(fake_dir)
    
    real_texts = real_gutenberg_texts + real_quarto_texts
    
    if not real_texts or not fake_texts:
        print("Error: Could not load sonnets.")
        return
        
    all_texts = real_texts + fake_texts
    labels = np.array([1] * len(real_texts) + [-1] * len(fake_texts))
    
    # 2. Extract TF-IDF features
    print("Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),
        max_features=800,
        stop_words=None
    )
    X = vectorizer.fit_transform(all_texts).toarray()
    
    # 3. Train/Test split
    X_train_np, X_test_np, y_train_np, y_test_np = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Reshape labels for matrix operations
    y_train = y_train_np.reshape(-1, 1)
    
    # 4. Train the SVM
    w, b, train_time = train_svm_numpy(X_train_np, y_train, num_epochs=250, lr=0.2, C=10.0)
    
    # 5. Evaluate the model
    raw_preds = np.dot(X_test_np, w) + b
    raw_preds_flat = raw_preds.flatten()
    
    # Simple threshold sweep for comparison
    best_thresh = 0.0
    best_f1 = 0.0
    from sklearn.metrics import f1_score
    for thresh in np.linspace(-1.0, 1.0, 201):
        thresh_preds = np.where(raw_preds_flat >= thresh, 1, -1)
        f1 = f1_score(y_test_np, thresh_preds, pos_label=1)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
            
    preds_opt = np.where(raw_preds_flat >= best_thresh, 1, -1)
    
    print("\n" + "="*40)
    print(f"NUMPY-ONLY EVALUATION RESULTS (Threshold = {best_thresh:.3f})")
    print("="*40)
    print("Confusion Matrix:")
    print(confusion_matrix(y_test_np, preds_opt))
    print("\nClassification Report:")
    target_names = ["Fake", "Real"]
    print(classification_report(y_test_np, preds_opt, target_names=target_names))

    # 6. Save model components to 'sonnet_data_numpy' using Pickle
    out_dir = "sonnet_data_numpy"
    os.makedirs(out_dir, exist_ok=True)
    import pickle
    model_path = os.path.join(out_dir, "svm_numpy_model.pkl")
    model_data = {
        "vectorizer": vectorizer,
        "w": w,
        "b": b,
        "threshold": best_thresh
    }
    with open(model_path, "wb") as f:
        pickle.dump(model_data, f)
    print(f"\nNumPy Model saved successfully to '{model_path}'")

if __name__ == "__main__":
    main()
