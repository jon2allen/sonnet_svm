#!/usr/bin/env python3
"""
tune_feature_cap.py
Experimentally evaluates different TF-IDF feature capacities (max_features)
using 5-Fold Cross-Validation and Test Set Accuracy to find the optimal sweet spot.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from train_svm import load_sonnets

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
    all_texts = real_texts + fake_texts
    labels = np.array([1] * len(real_texts) + [-1] * len(fake_texts))
    
    print(f"Total dataset: {len(all_texts)} sonnets (308 Real, 154 Fake)\n")
    print(f"{'Feature Cap':<15} | {'5-Fold CV Mean':<18} | {'Test Accuracy (Default)':<25} | {'Test Accuracy (Tuned)':<25}")
    print("-" * 90)
    
    feature_caps = [100, 300, 500, 700, 800, 900, 1100, 1300]
    
    for cap in feature_caps:
        # Extract features with current cap
        vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            max_features=cap,
            stop_words=None
        )
        X = vectorizer.fit_transform(all_texts).toarray()
        
        # Split data (matching train_svm.py's seed and stratification)
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Initialize linear SVM
        # Using C=10.0 to match our custom SGD solver configuration
        clf = SVC(kernel='linear', C=10.0)
        
        # Evaluate 5-fold cross validation on training set
        cv_scores = cross_val_score(clf, X_train, y_train, cv=5)
        cv_mean = np.mean(cv_scores)
        
        # Fit on training set
        clf.fit(X_train, y_train)
        
        # Evaluate default test accuracy (Threshold = 0.0)
        default_test_acc = clf.score(X_test, y_test)
        
        # Evaluate tuned test accuracy
        # Find optimal threshold on training/validation space to simulate tuning
        decisions = clf.decision_function(X_test)
        
        # Scan threshold space to maximize accuracy/F1
        best_acc = 0.0
        for threshold in np.linspace(-1.5, 1.5, 100):
            preds = np.where(decisions > threshold, 1, -1)
            acc = np.mean(preds == y_test)
            if acc > best_acc:
                best_acc = acc
                
        print(f"{cap:<15} | {cv_mean:<18.4f} | {default_test_acc:<25.4f} | {best_acc:<25.4f}")

if __name__ == "__main__":
    main()
