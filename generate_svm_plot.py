#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from train_svm import load_sonnets

def main():
    # 1. Load the dataset
    real_dir = "orig_sonnets"
    fake_dir = "orig_fake_sonnets"
    
    print("Loading sonnets...")
    real_texts, _ = load_sonnets(real_dir)
    fake_texts, _ = load_sonnets(fake_dir)
    
    if not real_texts or not fake_texts:
        print("Error: Could not load sonnets.")
        return
        
    all_texts = real_texts + fake_texts
    # 1 for Shakespeare, -1 for Fake
    y = np.array([1] * len(real_texts) + [-1] * len(fake_texts))
    
    # 2. Extract TF-IDF features
    print("Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),
        max_features=800,
        stop_words=None
    )
    X = vectorizer.fit_transform(all_texts).toarray()
    
    # 3. Reduce dimensionality to 2D using PCA for visualization
    print("Reducing dimensionality to 2D using PCA...")
    pca = PCA(n_components=2, random_state=42)
    X_2d = pca.fit_transform(X)
    
    # 4. Train a 2D Linear SVM on the PCA features
    print("Training 2D Linear SVM...")
    # C=1.0 soft margin to allow some violations, showing how SVM handles margins
    clf = SVC(kernel='linear', C=1.0)
    clf.fit(X_2d, y)
    
    # 5. Plotting
    plt.figure(figsize=(10, 8), dpi=300)
    
    # Scatter points
    real_mask = (y == 1)
    fake_mask = (y == -1)
    
    plt.scatter(X_2d[real_mask, 0], X_2d[real_mask, 1], 
                color='#1f77b4', edgecolors='k', s=60, alpha=0.8, label='Real (Shakespeare)')
    plt.scatter(X_2d[fake_mask, 0], X_2d[fake_mask, 1], 
                color='#d62728', edgecolors='k', s=60, alpha=0.8, label='Fake (Elizabethan-Mimicry)')
    
    # Plot decision boundary and margins
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    # Create grid to evaluate model
    xx = np.linspace(xlim[0], xlim[1], 100)
    yy = np.linspace(ylim[0], ylim[1], 100)
    YY, XX = np.meshgrid(yy, xx)
    xy = np.vstack([XX.ravel(), YY.ravel()]).T
    Z = clf.decision_function(xy).reshape(XX.shape)
    
    # Plot decision boundary (Z = 0) and margins (Z = -1, Z = 1)
    ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.9,
               linestyles=['--', '-', '--'], linewidths=[1.5, 2.5, 1.5])
    
    # Highlight support vectors
    ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=150,
               linewidth=1, facecolors='none', edgecolors='black', label='Support Vectors')
               
    # Add title and labels
    plt.title('Support Vector Machine (SVM) Decision Boundary in 2D PCA Space\nShakespeare Sonnets vs. LLM Elizabethan-Mimicry', 
              fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Principal Component 1', fontsize=12)
    plt.ylabel('Principal Component 2', fontsize=12)
    plt.legend(loc='upper right', frameon=True, shadow=True, fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # Adjust layout and save as JPEG
    plt.tight_layout()
    output_path = "svm_visualization.jpg"
    plt.savefig(output_path, format='jpg', dpi=300)
    print(f"Saved visualization to '{output_path}'")

if __name__ == "__main__":
    main()
