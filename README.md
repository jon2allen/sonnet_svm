# Shakespeare vs. Elizabethan Mimicry: MLX SVM Classification & Generation Pipeline

This repository contains an end-to-end Machine Learning, NLP, and LLM experiment designed to evaluate style classification and detection between authentic Shakespearean sonnets and high-fidelity simulated Elizabethan mimicries. 

By leveraging TF-IDF feature extraction (800 unigram/bigram features) and a Soft-Margin Linear Support Vector Machine (SVM) trained with **Apple Silicon GPU acceleration via MLX**, the system achieves state-of-the-art attribution accuracy.

---

## Key Experimental Results

| Test Dataset | Ground Truth | Total Sonnets | Correctly Classified | Accuracy |
| :--- | :--- | :---: | :---: | :---: |
| **`fresh_sonnets__fake_test/`** | **Fake (LLM Elizabethan Mimicry)** | 154 | **154** | **100.00%** |
| **`fresh_real_sonnets_test/`** | **Real (Authentic Shakespeare)** | 154 | **153** | **99.35%** |
| **Combined Benchmark** | **Real & Fake Datasets** | **308** | **307** | **99.68%** |

* **Decision Boundary Cutoff**: `0.8800` (Raw SVM Score $\ge 0.8800 \implies$ Real Shakespeare, $< 0.8800 \implies$ Fake Mimicry).
* **Speed**: In-process inference latency is $< 0.5 \text{ ms}$ per sonnet.

---

## Repository Directory Layout

```text
sonnets_svm/
│
├── README.md                          # Primary reproduction guide & project documentation
├── .gitignore                         # Git exclusion rules (.venv, cache, etc.)
├── LICENSE                            # Project license file
├── requirements.txt                   # Python dependencies (mlx, scikit-learn, numpy)
├── seq.txt                            # Sequence counter for generation tasks
│
├── Python Scripts (Training & Inference)
│   ├── train_svm.py                   # Primary MLX Soft-Margin SVM trainer & model saver
│   ├── classify_sonnet.py             # MLX SVM inference CLI for single sonnet files
│   ├── classify_sonnet_numpy.py       # Non-MLX / NumPy inference script
│   ├── svm_training_nomlx.py          # Pure NumPy / Scikit-Learn SVM trainer
│   ├── evaluate_fresh_sonnets.py      # Batch dataset evaluator & boundary distance calculator
│   ├── tune_feature_cap.py            # Feature cap & threshold sweep hyperparameter tuner
│   ├── benchmark_in_process.py        # MLX vs. NumPy in-process inference latency benchmark
│   ├── mix_compare_results.py         # Ground-truth accuracy parser for anal8 experiment
│   ├── extract_sonnets.py             # Gutenberg source text sonnet extractor
│   ├── extract_sonnets_1609.py        # 1609 Quarto edition HTML extractor
│   ├── mix_sonnets_5.py               # Dataset randomization & mixture builder
│   └── bundle_sonnets.py              # Packaging utility for sonnet collections
│
├── ChatDSL Scripts & Shell Automation
│   ├── generate_batch_154_forloop.chatdsl # Batch ChatDSL pipeline (LLM prompt + SVM classify 154 fakes)
│   ├── generate_real_154_forloop.chatdsl  # Batch ChatDSL pipeline (LLM prompt + SVM classify 154 reals)
│   ├── generate_and_classify.chatdsl  # Single-sonnet ChatDSL generation pipeline
│   ├── generate_real_shakespeare.chatdsl # Single-sonnet control test ChatDSL script
│   ├── sonnet1.chatdsl                # 20-Author composite Elizabethan prompt generator
│   ├── anal8.chatdsl                  # Zero-shot LLM baseline classifier prompt
│   ├── gen_and_classify_154.sh        # Legacy batch execution shell script
│   └── gen_all_sonnets.sh             # Legacy bulk fake dataset generator shell script
│
├── Model Checkpoints (Tracked in Git)
│   ├── sonnet_data_mlx/               # Primary MLX Model Checkpoint Directory
│   │   ├── svm_vectorizer.pkl         # Serialized TF-IDF Vectorizer (800 features)
│   │   └── svm_model_weights.npz      # MLX Tensors: Weights (w), Bias (b), Threshold (0.8800)
│   ├── sonnet_data_numpy/             # Non-MLX Model Checkpoint Directory
│   │   └── svm_numpy_model.pkl        # Bundled NumPy model dictionary
│   └── svm_visualization.jpg          # 2D PCA Decision Boundary & Margin Plot
│
└── Datasets & Text Corpora
    ├── orig_sonnets/                  # 154 Authentic Shakespeare Sonnets (Modern Gutenberg)
    ├── orig_sonnet_quarto/            # 154 Authentic Shakespeare Sonnets (1609 Quarto)
    ├── orig_fake_sonnets/             # 154 Generated Elizabethan Mimicry Sonnets (Training set)
    ├── fresh_sonnets__fake_test/      # 154 Generated Fake Sonnets & SVM analysis reports (Test set)
    └── fresh_real_sonnets_test/       # 154 Authentic Shakespeare Sonnets & SVM reports (Test set)
```

---

## Model Persistence & Git Tracking

All trained model weights, vectorizer pickles, and configuration checkpoints are **tracked directly in this Git repository**:

* **MLX Model**: Located in [`sonnet_data_mlx/`](file:///Users/jon2allen/projects/sonnets_svm/sonnet_data_mlx)
  * `svm_vectorizer.pkl` (Scikit-Learn TF-IDF vectorizer object)
  * `svm_model_weights.npz` (MLX arrays: weight vector `w`, bias `b`, and boundary threshold `0.8800`)
* **NumPy Model**: Located in [`sonnet_data_numpy/`](file:///Users/jon2allen/projects/sonnets_svm/sonnet_data_numpy)
  * `svm_numpy_model.pkl` (Bundled Python dictionary)

---

## Environment Setup & Installation

### 1. Requirements
* macOS with Apple Silicon (M1/M2/M3/M4) recommended for MLX GPU acceleration.
* Python 3.11+
* `chatybot` CLI (for running ChatDSL generation scripts)

### 2. Virtual Environment Setup
```bash
# Clone the repository
git clone https://github.com/jon2allen/sonnets_svm.git
cd sonnets_svm

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step-by-Step Reproduction Guide

### Step 1: Train the MLX SVM Model
To retrain the model from scratch on the 462-sonnet corpus (308 Real, 154 Fake):

```bash
python3 train_svm.py
```

This will:
1. Extract 800 unigram/bigram TF-IDF features.
2. Train a Soft-Margin Linear SVM using MLX GPU gradient descent for 250 epochs.
3. Perform an F1-score threshold optimization sweep to determine `best_thresh` (`0.8800`).
4. Save the trained model files into `sonnet_data_mlx/`.

*(For pure CPU / non-MLX environments, run `python3 svm_training_nomlx.py` instead).*

---

### Step 2: Run Single Sonnet Inference
Classify any text file as Shakespeare (Real) or Elizabethan-Mimicry (Fake):

```bash
# Classify an authentic Shakespeare sonnet
python3 classify_sonnet.py orig_sonnets/sonnet_XVIII.txt --model_dir sonnet_data_mlx

# Classify a generated fake sonnet
python3 classify_sonnet.py fresh_sonnets__fake_test/fake_sonnet_1.txt --model_dir sonnet_data_mlx
```

**Sample Output:**
```text
==================================================
SVM CLASSIFICATION REPORT FOR: sonnet_XVIII.txt
==================================================
Raw SVM Score:      0.9782
Decision Boundary:  0.8800
Classification:     Real (Shakespeare)
==================================================
```

---

### Step 3: Run Batch Generation & SVM Classification (via ChatDSL)

To generate 154 fake Elizabethan sonnets in batch using `mistral_1` and evaluate each automatically:

```bash
# Batch generate & classify 154 fake sonnets
chatybot <<EOF
/source generate_batch_154_forloop.chatdsl
/quit
EOF

# Batch generate & classify 154 authentic sonnets from memory
chatybot <<EOF
/source generate_real_154_forloop.chatdsl
/quit
EOF
```

---

### Step 4: Evaluate Test Datasets & Distance Metrics
To parse generated test directories, compute overall accuracy, and inspect the sonnets closest to the decision boundary:

```bash
# Evaluate the generated fake sonnets test dataset
python3 evaluate_fresh_sonnets.py --dir fresh_sonnets__fake_test

# Evaluate the authentic sonnets test dataset
python3 evaluate_fresh_sonnets.py --dir fresh_real_sonnets_test

# Force live in-memory MLX re-classification on raw files
python3 evaluate_fresh_sonnets.py --dir fresh_sonnets__fake_test --reclassify
```

---

## Linguistic Analysis & Key Predictors

The learned weights of the Support Vector Machine highlight distinct linguistic signatures separating authentic 1590s/1609 Shakespeare from modern LLM mimicry:

| Feature (Word / Bigram) | Weight | Class Association | Linguistic Rationale |
| :--- | :---: | :--- | :--- |
| **`which`** / **`of`** | `+0.1197` | **Real (Shakespeare)** | Functional syntax structures typical of authentic Shakespeare. |
| **`you`** | `+0.0955` | **Real (Shakespeare)** | Pronoun frequently used by Shakespeare when addressing the Fair Youth. |
| **`loue`** | `+0.0595` | **Real (Shakespeare)** | Original 1609 Quarto spelling of "love" (*loue*). |
| **`yet`** / **`light`** | `-0.1456` | **Fake (Mimicry)** | Poetic filler vocabulary over-utilized by LLMs. |
| **`the`** | `-0.1430` | **Fake (Mimicry)** | Overused by LLMs in heavy, repetitive noun phrases. |
| **`its`** | `-0.1217` | **Fake (Mimicry)** | Modern linguistic leak; `its` was virtually non-existent in Shakespeare's era (he used `his` or `thereof`). |

---

## License & Citation
* License: MIT License
* Author: Jon Allen
