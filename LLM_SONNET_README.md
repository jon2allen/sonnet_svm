# Shakespearean vs. Elizabethan Mimicry: LLM Classification Experiment

This repository contains an end-to-end NLP and AI-driven experiment designed to evaluate the style classification capabilities of Modern Large Language Models (LLMs). Specifically, it generates high-fidelity simulated Elizabethan-era sonnets in a composite style of contemporary 1590s poets (such as Sir Philip Sidney, Edmund Spenser, and Samuel Daniel) on topics identical to Shakespeare's sonnets, mixes them into a randomized dataset, and blind-tests whether LLMs can successfully distinguish authentic Shakespeare originals from high-quality mimicry.

---

## The Execution Engine: Chatybot and ChatDSL

The automation, prompting, and bulk queries in this pipeline are powered by **Chatybot** (available at the GitHub repository `jon2allen/chatybot`), a flexible command-line chatbot and prompting environment developed by Jon Allen. 

### Key Features of Chatybot in this Project:
*   **ChatDSL Scripting:** Chatybot supports a custom Domain Specific Language (.chatdsl) allowing for scripted, programmatic execution of prompt sequences without writing verbose API wrapper scripts.
*   **Built-in Escape Commands:** Chatybot enables model switching via `/model <alias>`, temperature adjustments with `/temp <value>`, and file bank management using `/filebank1 <path>` directly from within scripts.
*   **Async Processing:** It efficiently handles multiple parallel and sequential AI completions over target datasets.

All script files with the `.chatdsl` extension (e.g., `sonnet1.chatdsl`, `anal8.chatdsl`) and the shell scripts executing them in this project rely on a functional installation of the `chatybot` utility on the host machine.

### Setup & Installation

1. Install chatybot from PyPI:
   ```bash
   pip install chatybot
   ```
   *Requires Python 3.11+*

2. Set your Mistral AI API key as an environment variable before running chatybot:
   ```bash
   export MISTRAL_API_KEY="your_api_key_here"
   ```
   This project uses the `mistral_1` model alias which is predefined in chatybot's configuration and will automatically use the `MISTRAL_API_KEY` environment variable.

---

## Project Pipeline & Architecture

The pipeline consists of five execution steps:

1. **Ingestion & Extraction:** Extract raw Shakespeare sonnets from Gutenberg texts into individual files.
2. **Mimicked Generation:** Call Chatybot with `sonnet1.chatdsl` to produce topic-aligned, stylized Elizabethan sonnets.
3. **Dataset Mixing:** Generate randomized test sequences with an 80/20 (4:1) ratio of real-to-fake sonnets to prepare a balanced testing set.
4. **LLM Classification:** Execute blind classification evaluations using Chatybot with `anal8.chatdsl`.
5. **Accuracy Comparison:** Evaluate classification predictions against the ground-truth manifest, computing confusion matrices and metrics.

---

## File Inventory & Purpose

Here is the directory catalog for the project:

### Orchestration & Generation DSLs (.chatdsl)
*   **`sonnet1.chatdsl`:** The Generator. Prepares the contemporary Elizabethan style prompt, loads target Shakespeare sonnets, and prompts the LLM via Chatybot to write mimicked sonnets.
*   **`anal8.chatdsl`:** The Classifier. Prompts the LLM to inspect the full text of a mixed sonnet and label it: `Shakespeare: True` or `Shakespeare: False`.

### Python Scripts
*   **`extract_sonnets.py`:** Splits the main Gutenberg source file `sonnets.txt` into individual sonnet files.
*   **`mix_sonnets_5.py`:** Generates randomized 4:1 mixtures of real and fake sonnets and outputs a ground-truth manifest copy log.
*   **`mix_compare_results.py`:** Evaluates accuracy by comparing classification logs against the manifest copy log.
*   **`bundle_sonnets.py`:** Packages individual mixed sonnets into a single sequential file sorted numerically.
*   **`test_mix.py`:** Ground-truth validation utilities.

### Automation Shell Scripts (.sh)
*   **`gen_all_sonnets.sh`:** Bulk-processes source sonnets using `chatybot` with `sonnet1.chatdsl` to generate fake sonnets.
*   **`anal_mix_sonnets.sh`:** Bulk-processes mixed datasets using `chatybot` with `anal8.chatdsl` to produce classifications.

### Raw Source Data
*   **`sonnets.txt` / `sonnets_orig.txt`:** Raw Shakespeare sonnet text downloaded from Project Gutenberg.
*   **`sonnet_authors.txt`:** Contextual Elizabethan authors list used to establish style constraints.

### Reference Compiled Dataset
*   **`all_154_mix_real_fake.txt`:** A single, sequential compiled manuscript of all 154 mixed sonnets sorted numerically from Sonnet I to Sonnet CLIV.

### Reference Original Run Directories (orig_*)
These folders house the authentic results from the initial experimental run, serving as a baseline:
*   **`orig_sonnets/`:** Contains the 154 authentic Shakespeare sonnets extracted from the Gutenberg source.
*   **`orig_fake_sonnets/`:** Contains the 154 LLM-generated simulated Elizabethan sonnets created by running `sonnet1.chatdsl`.
*   **`orig_mix/`:** Contains the randomized 4:1 mixture of authentic and fake sonnets along with its ground-truth `manifest.txt` copy log.
*   **`orig_anal8/`:** Contains the 154 classification logs generated by the `anal8.chatdsl` run.

### Historical Source Materials (1609 Quarto)
This project now includes the original 1609 Quarto sonnet texts as historical reference artifacts. These files preserve Shakespeare's sonnets exactly as they first appeared in print, with original Elizabethan spelling, typography (including the long ſ character), and formatting:
*   **`sonnets_1609_quarto_roman.txt`:** All 154 sonnets with Roman numeral designations (::I::, ::II::, etc.)
*   **`sonnets_1609_quarto_full.txt`:** Complete quarto text with section markers
*   **`sonnets_1609_quarto_complete.txt`:** Full unabridged quarto edition
*   **`sonnets_complete.html`:** HTML version with preserved formatting
*   **`sonnets_quarto_sections/`:** Individual section directories for detailed study
*   **`extract_sonnets_1609.py`:** Python script for parsing the original quarto format
*   **`README_SONNETS.md`:** Documentation on the historical source materials

**Source Attribution:** The original 1609 Quarto texts are sourced from the **Internet Shakespeare Editions (ISE)** — a non-profit scholarly project providing open-access, peer-reviewed editions. Founded in 1996 by Michael Best (Coordinating Editor) and supported by the University of Victoria, British Columbia, Canada, and the Social Sciences and Humanities Research Council of Canada.

Source URL: [https://internetshakespeare.uvic.ca/doc/Son_Q1/complete/index.html](https://internetshakespeare.uvic.ca/doc/Son_Q1/complete/index.html)

These artifacts serve as educational reference points and ground truth for understanding the stylistic differences between authentic Shakespeare and the Elizabethan-era mimicry generated by this experiment.

---

## How to Run the Pipeline

**Note:** Run all commands from the root directory of this project.

Follow these steps sequentially to reproduce the entire experiment:

### Step 1: Ingest & Extract
Extract raw Gutenberg texts into individual files:
```bash
python3 extract_sonnets.py
```
*Outputs: `data/sonnet_*.txt`*

### Step 2: Generate Fake Sonnets
Use the Chatybot utility and the generation template to produce mimicked sonnets in bulk:
```bash
./gen_all_sonnets.sh
```
*Outputs: `fake_sonnet/sonnet_*.txt`*

### Step 3: Create Mixed Dataset
Run the mixing script to select a randomized subset of real and fake sonnets. Output the copy log to create a ground-truth manifest:
```bash
python3 mix_sonnets_5.py > mix_sonnet/manifest.txt
```
*Outputs: `mix_sonnet/sonnet_*.txt` and `mix_sonnet/manifest.txt`*

### Step 4: Run LLM Blind Classifications
Orchestrate classification queries over the mixed dataset:
```bash
./anal_mix_sonnets.sh
```
*Outputs: `anal8/analysis_1_sonnet_*.txt`*

### Step 5: Evaluate Performance Metrics
Run the comparison utility to parse predictions, calculate confusion matrices, and generate a performance report:
```bash
python3 mix_compare_results.py
```
*Outputs: `accuracy_comparison_report.txt`*

### Optional: Bundle Dataset
Compile the mixed dataset into a single, clean manuscript:
```bash
python3 bundle_sonnets.py
```
*Outputs: `mix_sonnet/all_154_sonnets.txt` (which can be renamed to `all_154_mix_real_fake.txt`)*

---

## Reference Results (orig_anal8 baseline)

The experimental evaluation of the initial baseline run yields the following performance statistics:

*   **Total Sonnets Evaluated:** 154
*   **Overall Classification Accuracy:** **96.10%** (148/154)
*   **Authentic Shakespeare Detection F1-Score:** **0.9756** (Precision: 98.36%, Recall: 96.77%)
*   **Elizabethan Mimicry Detection F1-Score:** **0.9032** (Precision: 87.50%, Recall: 93.33%)

### Confusion Matrix
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
*   **False Positives (Fooled by Mimicry):** Sonnet II, Sonnet CII.
*   **False Negatives (Rejected Authentic):** Sonnet C, Sonnet CLI, Sonnet CXXIII, Sonnet XCIX.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
