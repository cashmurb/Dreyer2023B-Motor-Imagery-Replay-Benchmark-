# Dreyer2023B Motor Imagery Replay Benchmark

Compares CSP+LDA and CSP+SVM on Dreyer2023B EEG using a held-out run split and simulated real-time replay. Reports accuracy above a confidence threshold, accuracy by confidence bin, and decoder failure modes.

## Overview

- **Dataset:** Dreyer2023B left- and right-hand motor imagery. The dataset contains 21 subjects, 27 EEG channels, and six runs of 40 trials per subject. The results below cover subjects 61–63.
- **Split:** Train on runs R1–R2 (calibration) and test on R3–R6 (online feedback). Training and test sets contain separate runs and trials.
- **Epoch window:** 3.5–7.5 s, starting 0.5 s after the red-arrow cue to reduce cue-evoked contamination.
- **Channels:** C3, C4, Cz, FC1, FC2, CP1, and CP2.
- **Decoders:** CSP+LDA and CSP+SVM use the same feature configuration, replay windows, and confidence threshold within each version.
- **Replay:** Sliding windows with a 0.2 s update interval and a confidence threshold of 0.6. The retained configuration uses a 3 s window and four CSP components.

## Setup

```bash
pip install -r requirements.txt
python -m scripts.download_data
python -m scripts.train_decoders
python -m scripts.run_replay
python -m scripts.analyze_results
python -m scripts.diagnose
```

## Results Summary

| Version | Configuration | Online LDA | Online SVM | Accuracy at confidence ≥ 0.9 |
| --- | --- | ---: | ---: | ---: |
| v0.1 | Baseline, 2 s window | 60.5% | 61.0% | ~65% |
| v0.2 | 3 s replay window | 63.0% | 63.5% | ~70% |
| v0.3 | CAR, epoch rejection, CSP `reg=0.01`, four components | 68.8% | 77.4% | 85.8% LDA / 91.4% SVM |
| v0.4 | v0.3 with six CSP components (reverted to four) | 69.1% | 69.8% | 79.5% LDA / 87.1% SVM |

Online accuracy is calculated over windows that pass the confidence threshold. With the retained v0.3 configuration, SVM reached 77.4% accuracy at 55.7% coverage, and LDA reached 68.8% accuracy at 79.5% coverage.

## Version 1 — Baseline

### CV AUC on calibration runs (R1–R2)

| Subject | LDA | SVM |
| --- | ---: | ---: |
| 61 | 0.62 | 0.63 |
| 62 | 0.77 | 0.73 |
| 63 | 0.59 | 0.60 |

### Online accuracy on held-out runs (R3–R6)

| Decoder | Accuracy above threshold | Confident-but-wrong (% of all windows) |
| --- | ---: | ---: |
| LDA | 60.5% | 34.7% |
| SVM | 61.0% | 32.6% |

### Diagnosis

#### Training signal quality (CV AUC, R1–R2)

| Subject | `n_train` | `n_left` | `n_right` | CV AUC | Std |
| --- | ---: | ---: | ---: | ---: | ---: |
| 61 | 80 | 40 | 40 | 0.62 | 0.11 |
| 62 | 80 | 40 | 40 | 0.77 | 0.05 |
| 63 | 80 | 40 | 40 | 0.59 | 0.15 |

#### CSP dimensionality sensitivity

| Subject | 2 components | 4 components | 6 components | 8 components |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.600 | 0.622 | 0.622 | 0.641 |
| 62 | 0.653 | 0.772 | 0.722 | 0.750 |
| 63 | 0.606 | 0.594 | 0.600 | 0.613 |

#### Window-length sensitivity

| Subject | 1 s | 2 s | 3 s | 4 s |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.794 | 0.800 | 0.863 | 0.822 |
| 62 | 0.750 | 0.850 | 0.856 | 0.894 |
| 63 | 0.547 | 0.694 | 0.641 | 0.588 |

#### Error concentration

| Subject | Decoder | `acc_left` | `acc_right` | `n_trials` | Trials < 50% | Trials > 80% |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 61 | LDA | 0.467 | 0.790 | 160 | 51 | 57 |
| 61 | SVM | 0.379 | 0.885 | 160 | 51 | 68 |
| 62 | LDA | 0.640 | 0.665 | 160 | 50 | 62 |
| 62 | SVM | 0.637 | 0.709 | 160 | 52 | 70 |
| 63 | LDA | 0.339 | 0.713 | 160 | 79 | 39 |
| 63 | SVM | 0.257 | 0.773 | 160 | 81 | 41 |

For subjects 61 and 63, right-hand accuracy ranged from 0.71 to 0.89 and left-hand accuracy from 0.26 to 0.47. The 3 s window had the highest mean CV AUC across the three subjects. Gains from increasing CSP dimensionality were small and subject-specific.

## Version 2 — Preprocessing

### Changes

- Applied common average reference (CAR) to suppress signal components shared across channels.
- Added automatic epoch rejection at 100 µV peak-to-peak.
- Added CSP regularization (`reg=0.01`) to handle rank deficiency after CAR.
- Retained the 3 s replay window introduced in v0.2.
- Fixed buffer priming by pushing the first window before entering the replay loop.

### CV AUC on calibration runs (R1–R2)

| Subject | Baseline LDA | After preprocessing LDA | Baseline SVM | After preprocessing SVM |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.62 | 0.80 | 0.63 | 0.82 |
| 62 | 0.77 | 0.88 | 0.73 | 0.89 |
| 63 | 0.59 | 0.61 | 0.60 | 0.61 |

### Online accuracy on held-out runs (R3–R6)

| Decoder | Baseline | After preprocessing | Change (percentage points) |
| --- | ---: | ---: | ---: |
| LDA | 60.5% | 68.8% | +8.3 |
| SVM | 61.0% | 77.4% | +16.4 |

### Confidence calibration

| Confidence bin | LDA before | LDA after | SVM before | SVM after |
| --- | ---: | ---: | ---: | ---: |
| `[0.5, 0.6)` | 49.8% | 59.1% | 50.9% | 53.0% |
| `[0.6, 0.7)` | 56.7% | 57.4% | 55.5% | 66.0% |
| `[0.7, 0.8)` | 55.7% | 60.6% | 57.4% | 75.9% |
| `[0.8, 0.9)` | 58.1% | 72.4% | 63.2% | 75.3% |
| `[0.9, 1.01)` | 64.4% | 85.8% | 65.2% | 91.4% |

### Failure counts

| Metric | Baseline LDA | After preprocessing LDA | Baseline SVM | After preprocessing SVM |
| --- | ---: | ---: | ---: | ---: |
| Total windows | 10,560 | 2,400 | 10,560 | 2,400 |
| Confident-but-wrong windows | 3,670 | 596 | 3,438 | 302 |
| Majority-class fraction | 61.0% | 63.8% | 65.7% | 65.8% |

The combined changes raised accuracy above threshold and accuracy in the highest confidence bin. The number of evaluated windows also fell from 10,560 to 2,400 per decoder, so raw failure counts reflect both the change in error rate and the change in evaluation volume.

## Post-Preprocessing Diagnosis

### Training signal quality (CV AUC, R1–R2)

| Subject | `n_train` | `n_left` | `n_right` | CV AUC | Std |
| --- | ---: | ---: | ---: | ---: | ---: |
| 61 | 80 | 40 | 40 | 0.80 | 0.09 |
| 62 | 80 | 40 | 40 | 0.88 | 0.10 |
| 63 | 80 | 40 | 40 | 0.61 | 0.10 |

### CSP dimensionality sensitivity

| Subject | 2 components | 4 components | 6 components | 8 components |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.82 | 0.80 | 0.83 | 0.86 |
| 62 | 0.83 | 0.88 | 0.90 | 0.89 |
| 63 | 0.63 | 0.61 | 0.69 | 0.70 |

Both six and eight components improved calibration-run CV AUC relative to four components for all three subjects. Version 4 tested whether the gains at six components transferred to held-out runs.

### Window-length sensitivity

| Subject | 1 s | 2 s | 3 s | 4 s |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.83 | 0.83 | 0.87 | 0.80 |
| 62 | 0.75 | 0.84 | 0.88 | 0.88 |
| 63 | 0.56 | 0.74 | 0.61 | 0.61 |

The 3 s window performed best for subject 61 and tied with 4 s for subject 62. The 2 s window performed best for subject 63 and had the highest mean CV AUC across the three subjects after preprocessing.

### Error concentration

| Subject | Decoder | `acc_left` | `acc_right` | `n_trials` | Trials < 50% | Trials > 80% |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 61 | LDA | 0.55 | 0.90 | 155 | 42 | 108 |
| 61 | SVM | 0.55 | 0.93 | 149 | 40 | 108 |
| 62 | LDA | 0.78 | 0.78 | 157 | 33 | 113 |
| 62 | SVM | 0.74 | 0.87 | 154 | 34 | 113 |
| 63 | LDA | 0.13 | 0.82 | 119 | 58 | 60 |
| 63 | SVM | 0.00 | 0.50 | 5 | 3 | 2 |

Subject 62 had equal left- and right-hand accuracy with LDA. Subject 61 retained a large class-wise accuracy gap with both decoders. For subject 63, LDA left-hand accuracy was 0.13 and the SVM diagnosis included only five reported trials. The cause of the low SVM trial count remains unverified.

## Version 4 — Six-Component CSP Test (Reverted to Four)

**Hypothesis:** Increasing CSP from four to six components would improve held-out replay accuracy, following the higher CV AUC observed on the calibration runs.

### CV AUC on calibration runs (R1–R2)

| Subject | 4 components | 6 components |
| --- | ---: | ---: |
| 61 | 0.80 | 0.83 |
| 62 | 0.88 | 0.90 |
| 63 | 0.61 | 0.69 |

### Online accuracy on held-out runs (R3–R6)

| Decoder | v0.3 (4 components) | v0.4 (6 components) | Change (percentage points) |
| --- | ---: | ---: | ---: |
| LDA | 68.8% | 69.1% | +0.3 |
| SVM | 77.4% | 69.8% | −7.6 |

### Other replay metrics

| Metric | v0.3 LDA | v0.4 LDA | v0.3 SVM | v0.4 SVM |
| --- | ---: | ---: | ---: | ---: |
| Accuracy at confidence ≥ 0.9 | 85.8% | 79.5% | 91.4% | 87.1% |
| Confident-but-wrong windows | 596 | 653 | 302 | 594 |
| Majority-class fraction | 63.8% | 58.9% | 65.8% | 63.1% |

Six components improved calibration-run CV AUC for all three subjects. On held-out replay, accuracy above threshold rose by 0.3 percentage points for LDA and fell by 7.6 points for SVM. Accuracy in the highest confidence bin fell by 6.3 points for LDA and 4.3 points for SVM. The benchmark reverted to four components.

## Summary of What We Know

| Question | Evidence |
| --- | --- |
| Did the updated configuration improve replay accuracy? | Accuracy above threshold rose by 8.3 points for LDA and 16.4 points for SVM from v0.1 to v0.3. Several settings changed between these versions. |
| How accurate were high-confidence predictions? | At confidence ≥ 0.9, v0.3 accuracy was 85.8% for LDA and 91.4% for SVM, up from approximately 65% in v0.1. |
| Did the class-wise accuracy gap persist? | Subjects 61 and 63 showed substantial gaps after preprocessing. The cause remains unverified. |
| Which decoder had higher online accuracy in v0.3? | SVM reached 77.4% at 55.7% coverage. LDA reached 68.8% at 79.5% coverage. |
| Which CSP dimensionality was retained? | Four components. Six increased calibration-run CV AUC and reduced held-out SVM accuracy by 7.6 percentage points. |
| Which window length performed best? | It varied by subject. Mean calibration CV AUC was highest at 3 s before preprocessing and 2 s after preprocessing. The retained replay configuration uses 3 s. |
| What is known about subject 63? | Post-preprocessing LDA left-hand accuracy was 0.13. The SVM diagnosis included five reported trials, which limits interpretation. |

## Next Steps

1. **Keep `n_components=4`.** Record the six-component experiment as a negative result for held-out replay.
2. **Implement per-trial majority voting.** Aggregate existing window predictions into one decision per trial. Report trial-level accuracy and coverage alongside window-level metrics. This step requires no retraining.
3. **Document the class-wise accuracy gap.** Report left- and right-hand accuracy by subject and decoder. Check the v0.4 class-wise results to determine whether CSP dimensionality affected the gap.

## What Not to Do

- **Defer class weighting.** The reported calibration set contains 40 left-hand and 40 right-hand trials per subject.
- **Keep the confidence threshold fixed for the next comparison.** Use the same threshold when comparing window-level predictions with trial-level voting.
- **Defer subject-specific tuning until trial losses are traced.** Separate epoch rejection from losses at the replay confidence threshold before changing the rejection threshold for subject 63.

## Decision Log

| Action | Status | Result |
| --- | --- | --- |
<<<<<<< HEAD
| Baseline CSP(4) + LDA/SVM, 2 s window | Completed | 60.5% LDA / 61.0% SVM online accuracy |
| Test 3 s replay window | Completed | 63.0% LDA / 63.5% SVM (+2.5 points each) |
| Add CAR, epoch rejection, and CSP `reg=0.01` | Completed | 68.8% LDA / 77.4% SVM (+8.3 / +16.4 points versus the 2 s baseline) |
| Test `n_components=6` | Completed, reverted to four | Calibration CV AUC rose for all three subjects. Held-out accuracy changed by +0.3 points for LDA and −7.6 points for SVM. |
| Add per-trial majority voting | Planned | Evaluate trial-level accuracy and coverage using existing window predictions. |
=======
| Baseline CSP(4) + LDA/SVM, 2 s window | Completed | 60.5% / 61.0% online accuracy |
| Test 3 s replay window | Completed | 63.0% / 63.5% online accuracy (+2.5 points each) |
| Add CAR, rejection, and CSP `reg=0.01` | Completed | 68.8% / 77.4% online accuracy (+8.3 / +16.4 points versus the 2 s baseline) |
| Increase `n_components` to 6 | Planned | Projected gain of 1–3 points |
| Add per-trial majority voting | Planned | Projected gain of 5–10 points for subjects 61 and 62 |
>>>>>>> 241dccd27a5b2f0acca1f7024875d724e25508f3
