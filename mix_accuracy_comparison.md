# Accuracy Analysis Report: anal8 vs Ground-Truth Manifest

This report evaluates the accuracy of the anal8 experiment against the ground-truth dataset manifest located in mix_sonnet/manifest.txt on your remote Fedora server. The Python evaluation script mix_compare_results.py has been successfully executed, and the results are detailed below.

---

## Performance Overview

The classification task evaluated a total of 154 sonnets in a randomized, balanced mixture. The overall performance is exceptionally high, demonstrating that the LLM is highly capable of identifying authentic Shakespeare, though not entirely immune to high-quality Elizabethan mimicry.

| Metric | Value | Details |
| :--- | :---: | :--- |
| **Overall Accuracy** | **96.10%** | **148** out of **154** sonnets classified correctly. |
| **Authentic Shakespeare Precision** | **98.36%** | Out of all sonnets labeled as Shakespeare, 98.36% were authentic. |
| **Authentic Shakespeare Recall** | **96.77%** | The model correctly identified 96.77% of all Shakespeare sonnets. |
| **Elizabethan Mimicry Precision** | **87.50%** | Out of all sonnets labeled as Fake, 87.50% were truly generated. |
| **Elizabethan Mimicry Recall** | **93.33%** | The model correctly detected 93.33% of all generated sonnets. |

---

## Confusion Matrix & Counts

Below is the distribution of the classifications:

```
                  PREDICTED AS REAL     PREDICTED AS FAKE
                 +-------------------+-------------------+
ACTUAL REAL      |    TP = 120       |     FN = 4        |
(Shakespeare)    | (True Positives)  | (False Negatives) |
                 +-------------------+-------------------+
ACTUAL FAKE      |     FP = 2        |     TN = 28       |
(Mimicry)        | (False Positives) | (True Negatives)  |
                 +-------------------+-------------------+
```

*   **True Positives (Real -> Real):** 120
*   **True Negatives (Fake -> Fake):** 28
*   **False Positives (Fake -> Real):** 2 — The model fell for the Elizabethan-style mimicry!
*   **False Negatives (Real -> Fake):** 4 — The model mistakenly rejected authentic Shakespeare sonnets as fake!
*   **Unparseable / Unknown Classifications:** 0 (100% of files were cleanly parsed!)

---

## Analysis of Mismatches (Errors)

The model made only 6 errors across all 154 sonnets. These errors represent highly interesting test cases where the model's classification failed.

### False Positives (Felled by Mimicry)
These are generated sonnets that the model confidently declared were authentic Shakespeare:
*   **Sonnet II** (Fake → Classified as Real)
*   **Sonnet CII** (Fake → Classified as Real)

### False Negatives (Rejected Authentic Shakespeare)
These are genuine Shakespeare sonnets that the model labeled as fake, believing they were stylistic imitations:
*   **Sonnet C** (Real → Classified as Fake)
*   **Sonnet CLI** (Real → Classified as Fake)
*   **Sonnet CXXIII** (Real → Classified as Fake)
*   **Sonnet XCIX** (Real → Classified as Fake)

---

## Performance Summary by Class

### 1. Authentic Shakespeare Detection
*   **Precision:** 98.36%
*   **Recall:** 96.77%
*   **F1-Score:** 0.9756

### 2. Elizabethan Mimicry (Fake) Detection
*   **Precision:** 87.50%
*   **Recall:** 93.33%
*   **F1-Score:** 0.9032

---

> [!NOTE]
> The full report output and individual log entries have been saved permanently to the remote file: /home/jon2allen/python/data/jon2allen/fake_sonnets/accuracy_comparison_report.txt
