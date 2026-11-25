# Dreyer2023B Motor Imagery Replay Benchmark

Compares CSP+LDA vs CSP+SVM on real Dreyer2023B EEG, using a held-out run split and a simulated real-time replay loop. Documents online accuracy, confidence calibration, and failure modes.

## Overview

- **Dataset:** Dreyer2023B (left/right hand motor imagery), 21 subjects,
  27 EEG channels, 6 runs per subject (40 trials each).
- **Split:** Train on runs R1–R2 (calibration), test on R3–R6 (online).
  Trial-disjoint, run-disjoint.
- **Epoch window:** 3.5–7.5 s (after the red arrow cue; avoids visual ERP
  contamination).
- **Channels:** C3, C4, Cz, FC1, FC2, CP1, CP2.
- **Decoders:** CSP(4) + LDA vs CSP(4) + SVM (identical features, same windows,
  same threshold).
- **Replay:** 2 s sliding window, 0.2 s update, confidence threshold 0.6.

## Setup

```bash
pip install -r requirements.txt
python -m scripts.download_data
python -m scripts.train_decoders
python -m scripts.run_replay
python -m scripts.analyze_results
python -m scripts.diagnose

```

## Diagnosis v1 — Baseline CSP(4) + LDA/SVM, 2 s window

### 1. Training signal quality (CV AUC, runs 1–2)

| Subject | `n_train` | `n_left` | `n_right` | `cv_auc_mean` | `cv_auc_std` |
| --- | ---: | ---: | ---: | ---: | ---: |
| 61 | 80 | 40 | 40 | 0.62 | 0.11 |
| 62 | 80 | 40 | 40 | 0.77 | 0.05 |
| 63 | 80 | 40 | 40 | 0.59 | 0.15 |

### 2. CSP dimensionality sensitivity

| Subject | 2 components | 4 components | 6 components | 8 components |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.600000 | 0.621875 | 0.621875 | 0.640625 |
| 62 | 0.653125 | 0.771875 | 0.721875 | 0.750000 |
| 63 | 0.606250 | 0.593750 | 0.600000 | 0.612500 |

### 3. Window-length sensitivity

| Subject | 1.0 s | 2.0 s | 3.0 s | 4.0 s |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.793750 | 0.800000 | 0.862500 | 0.821875 |
| 62 | 0.750000 | 0.850000 | 0.856250 | 0.893750 |
| 63 | 0.546875 | 0.693750 | 0.640625 | 0.587500 |

### 4. Error concentration

| Subject | Decoder | `acc_left` | `acc_right` | `n_trials` | `trials_below_50pct` | `trials_above_80pct` |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 61 | LDA | 0.467490 | 0.789638 | 160 | 51 | 57 |
| 61 | SVM | 0.378895 | 0.885235 | 160 | 51 | 68 |
| 62 | LDA | 0.640106 | 0.664978 | 160 | 50 | 62 |
| 62 | SVM | 0.637491 | 0.709103 | 160 | 52 | 70 |
| 63 | LDA | 0.338593 | 0.712878 | 160 | 79 | 39 |
| 63 | SVM | 0.256820 | 0.773237 | 160 | 81 | 41 |

## Interpretation

- For subjects 61 and 63, right-hand accuracy ranged from 0.71 to 0.89. Subject 62 showed a smaller gap between hands.
- The best window was 3 s for subject 61, 4 s for subject 62, and 2 s for subject 63. Compared with 2 s, the best longer window improved CV AUC by 0.063 for subject 61 and 0.044 for subject 62.
- The best CSP dimensionality varied by subject. Relative to four components, the largest gain was about 0.019 AUC.
- Subject 63 had a baseline CV AUC of 0.59, with scores ranging from 0.59 to 0.61 across the tested CSP dimensionalities.

## Decision

- Test a 3 s replay window against the 2 s baseline.
- Document the right-hand bias, subject 63’s baseline performance, and the concentration of trials below 50% and above 80% accuracy.