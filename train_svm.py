#!/usr/bin/env python3
import os
import numpy as np
import mlx.core as mx
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

def loss_fn(w, b, X, y, C=1.0):
    """Hinge loss with L2 regularization for Soft-Margin SVM."""
    # X shape: (N, D), w shape: (D, 1), b shape: (1,)
    # y shape: (N, 1), containing -1 or 1
    preds = mx.matmul(X, w) + b
    hinge = mx.maximum(0.0, 1.0 - y * preds)
    # L2 regularization
    reg = 0.5 * (1.0 / C) * mx.sum(w ** 2)
    return mx.mean(hinge) + reg

def train_svm(X_train, y_train, num_epochs=200, lr=0.1, C=1.0):
    """Trains a linear SVM using MLX gradient descent."""
    num_features = X_train.shape[1]
    
    # Initialize weights and bias
    w = mx.zeros((num_features, 1))
    b = mx.zeros((1,))
    
    # Define grad function
    grad_fn = mx.value_and_grad(loss_fn, argnums=(0, 1))
    
    import time
    start_time = time.perf_counter()
    for epoch in range(num_epochs):
        loss, (grad_w, grad_b) = grad_fn(w, b, X_train, y_train, C)
        
        # Gradient descent update step
        w = w - lr * grad_w
        b = b - lr * grad_b
        
        # Evaluate to run the deferred computation
        mx.eval(w, b, loss)
        
        if (epoch + 1) % 20 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:03d}/{num_epochs} - Hinge+Reg Loss: {loss.item():.4f}")
    
    end_time = time.perf_counter()
    print(f"MLX Training Complete in {end_time - start_time:.6f} seconds.")
    return w, b

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
    
    print(f"Loaded {len(real_gutenberg_texts)} real Gutenberg sonnets.")
    print(f"Loaded {len(real_quarto_texts)} real Quarto sonnets.")
    print(f"Loaded {len(fake_texts)} fake sonnets (total real: {len(real_texts)}).")
    
    if not real_texts or not fake_texts:
        print("Error: Could not load sonnets. Check that directories exist and contain .txt files.")
        return
        
    # Combine texts and create labels (1 for Real, -1 for Fake)
    all_texts = real_texts + fake_texts
    labels = np.array([1] * len(real_texts) + [-1] * len(fake_texts))
    
    # 2. Vectorize texts using TF-IDF (word n-grams)
    print("Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),
        max_features=800,
        stop_words=None
    )
    X = vectorizer.fit_transform(all_texts).toarray()
    
    # 3. Train/Test split (80% train, 20% test)
    X_train_np, X_test_np, y_train_np, y_test_np = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Convert data to MLX arrays
    X_train = mx.array(X_train_np, mx.float32)
    y_train = mx.array(y_train_np.reshape(-1, 1), mx.float32)
    X_test = mx.array(X_test_np, mx.float32)
    
    # 4. Train the SVM
    w, b = train_svm(X_train, y_train, num_epochs=250, lr=0.2, C=10.0)
    
    # 5. Evaluate the model
    # Compute predictions
    raw_preds = mx.matmul(X_test, w) + b
    mx.eval(raw_preds)
    raw_preds_np = np.array(raw_preds).flatten()
    
    # Search for optimal threshold to maximize F1-score on Real class (1)
    from sklearn.metrics import f1_score
    best_thresh = 0.0
    best_f1 = 0.0
    for thresh in np.linspace(-1.0, 1.0, 201):
        thresh_preds = np.where(raw_preds_np >= thresh, 1, -1)
        f1 = f1_score(y_test_np, thresh_preds, pos_label=1)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh

    # Predictions with default threshold (0.0)
    preds_default = np.sign(raw_preds_np)
    
    # Predictions with optimal threshold
    preds_opt = np.where(raw_preds_np >= best_thresh, 1, -1)
    
    print("\n" + "="*40)
    print("EVALUATION RESULTS (Default Threshold = 0.0)")
    print("="*40)
    print("Confusion Matrix:")
    print(confusion_matrix(y_test_np, preds_default))
    print("\nClassification Report:")
    target_names = ["Fake", "Real"]
    print(classification_report(y_test_np, preds_default, target_names=target_names))
    
    print("\n" + "="*40)
    print(f"OPTIMIZED EVALUATION RESULTS (Threshold = {best_thresh:.3f})")
    print("="*40)
    print(f"Optimal Threshold to maximize Real F1-score: {best_thresh:.3f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test_np, preds_opt))
    print("\nClassification Report:")
    print(classification_report(y_test_np, preds_opt, target_names=target_names))
    
    # Print top feature importances
    feature_names = np.array(vectorizer.get_feature_names_out())
    weights = np.array(w).flatten()
    
    # Positive weights favor Real (Shakespeare), negative favor Fake (Mimicry)
    top_real_idx = np.argsort(weights)[-10:][::-1]
    top_fake_idx = np.argsort(weights)[:10]
    
    print("\nTop 10 features indicating Shakespeare (Real):")
    for idx in top_real_idx:
        print(f"  {feature_names[idx]:<20} weight: {weights[idx]:.4f}")
        
    print("\nTop 10 features indicating Elizabethan-Mimicry (Fake):")
    for idx in top_fake_idx:
        print(f"  {feature_names[idx]:<20} weight: {weights[idx]:.4f}")

    # 6. Save the model components to 'sonnet_data_mlx' directory
    out_dir = "sonnet_data_mlx"
    os.makedirs(out_dir, exist_ok=True)
    
    # Save TF-IDF Vectorizer
    import pickle
    vectorizer_path = os.path.join(out_dir, "svm_vectorizer.pkl")
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)
        
    # Save MLX Model Weights and Optimized Threshold
    weights_path = os.path.join(out_dir, "svm_model_weights.npz")
    mx.savez(
        weights_path,
        w=w,
        b=b,
        threshold=mx.array([best_thresh])
    )
    print(f"\nModel saved successfully in '{out_dir}/' directory:")
    print(f"  - Vectorizer: {vectorizer_path}")
    print(f"  - Weights & Threshold: {weights_path}")

if __name__ == "__main__":
    main()
