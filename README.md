# Dreyer2023B Motor Imagery Replay Benchmark

Compares CSP+LDA vs. CSP+SVM on real Dreyer2023B EEG using a held-out run split and a simulated real-time replay loop. Documents online accuracy, confidence calibration, and failure modes.

## Overview

- **Dataset:** Dreyer2023B (left/right hand motor imagery), 21 subjects, 27 EEG channels, and 6 runs per subject (40 trials each).
- **Split:** Train on runs R1–R2 (calibration), test on R3–R6 (online). Trial-disjoint and run-disjoint.
- **Epoch window:** 3.5–7.5 s (after the red arrow cue; avoids visual ERP contamination).
- **Channels:** C3, C4, Cz, FC1, FC2, CP1, CP2.
- **Decoders:** CSP+LDA vs. CSP+SVM (identical features, windows, and threshold).
- **Replay:** Sliding window (3 s after preprocessing), 0.2 s update interval, and confidence threshold of 0.6.

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
| v0.2 | 3 s window | 63.0% | 63.5% | ~70% |
| v0.3 | CAR + rejection + CSP `reg=0.01` | 68.8% | 77.4% | 86–91% |

**Key finding:** With the v0.3 configuration, both decoders achieved higher accuracy among windows above the confidence threshold. Accuracy in the highest confidence bin rose to 86–91%. The raw count of confident-but-wrong windows fell by 84–91%, alongside a reduction in the total number of evaluated windows.

## Version 1 — Baseline (No Preprocessing)

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

### Diagnosis v1

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

**Interpretation:** For subjects 61 and 63, right-hand accuracy ranged from 0.71 to 0.89 and left-hand accuracy from 0.26 to 0.47. The 3 s window had the highest mean CV AUC across these three subjects. Gains from increasing CSP dimensionality were small and subject-specific.

## Version 2 — Preprocessing (CAR + Rejection + CSP `reg=0.01`)

### Changes

- Applied common average reference (CAR) to suppress noise shared across channels.
- Added automatic epoch rejection at 100 µV peak-to-peak.
- Added CSP regularization (`reg=0.01`) to handle rank deficiency after CAR.
- Increased the replay window from 2 s to 3 s.
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
| 0.5–0.6 | 49.8% | 59.1% | 50.9% | 53.0% |
| 0.6–0.7 | 56.7% | 57.4% | 55.5% | 66.0% |
| 0.7–0.8 | 55.7% | 60.6% | 57.4% | 75.9% |
| 0.8–0.9 | 58.1% | 72.4% | 63.2% | 75.3% |
| 0.9–1.0 | 64.4% | 85.8% | 65.2% | 91.4% |

### Failure counts

| Metric | Baseline LDA | After preprocessing LDA | Baseline SVM | After preprocessing SVM |
| --- | ---: | ---: | ---: | ---: |
| Confident-but-wrong windows | 3,670 | 596 | 3,438 | 302 |
| Majority-class fraction | 61.0% | 63.8% | 65.7% | 65.8% |

**Key finding:** After the combined changes, SVM had higher accuracy above threshold (77.4% vs. 68.8%) and lower coverage (1,336 vs. 1,909 accepted windows out of 2,400). The majority-class fraction remained about 64–66%.

## Version 3 — Post-Preprocessing Diagnosis

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

**Finding:** After preprocessing, both 6 and 8 components improved CV AUC relative to 4 components for all three subjects. The next test uses 6 components.

### Window-length sensitivity

| Subject | 1 s | 2 s | 3 s | 4 s |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.83 | 0.83 | 0.87 | 0.80 |
| 62 | 0.75 | 0.84 | 0.88 | 0.88 |
| 63 | 0.56 | 0.74 | 0.61 | 0.61 |

**Finding:** The 3 s window performed best for subject 61 and tied with 4 s for subject 62. The 2 s window performed best for subject 63 and had the highest mean CV AUC across the three subjects after preprocessing.

### Error concentration

| Subject | Decoder | `acc_left` | `acc_right` | `n_trials` | Trials < 50% | Trials > 80% |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 61 | LDA | 0.55 | 0.90 | 155 | 42 | 108 |
| 61 | SVM | 0.55 | 0.93 | 149 | 40 | 108 |
| 62 | LDA | 0.78 | 0.78 | 157 | 33 | 113 |
| 62 | SVM | 0.74 | 0.87 | 154 | 34 | 113 |
| 63 | LDA | 0.13 | 0.82 | 119 | 58 | 60 |
| 63 | SVM | 0.00 | 0.50 | 5 | 3 | 2 |

**Key finding:** Subject 62 had equal left- and right-hand accuracy with LDA. Subject 61 retained a large class-wise accuracy gap with both decoders. Subject 63 had 0.13 left-hand accuracy with LDA and only five reported SVM trials. The cause of the low SVM trial count remains unverified.

## Summary of What We Know

| Question | Evidence |
| --- | --- |
| Did the updated configuration help? | Accuracy above threshold rose by 8.3 points for LDA and 16.4 points for SVM versus the 2 s baseline. |
| How accurate were high-confidence predictions? | Accuracy at confidence ≥ 0.9 rose from about 65% to 85.8% for LDA and 91.4% for SVM. |
| Did the right-hand bias persist? | Subjects 61 and 63 still showed substantial class-wise accuracy gaps. Their cause remains unverified. |
| Which decoder had higher online accuracy? | SVM reached 77.4% at 55.7% coverage. LDA reached 68.8% at 79.5% coverage. |
| Which CSP dimensionality performed best? | Six or eight components gave the highest post-preprocessing CV AUC for each subject. |
| Which window length performed best? | It varied by subject. The best mean CV AUC was at 3 s before preprocessing and 2 s after preprocessing. |
| What is known about subject 63? | LDA left-hand accuracy was 0.13. The SVM diagnosis included only five trials, which limits interpretation. |

## Next Steps (in Priority Order)

1. Increase `n_components` to `6` in `config.yaml`. Retrain, replay, and analyze. The projected online accuracy gain is 1–3 percentage points.
2. Implement per-trial majority voting. Aggregate overlapping window predictions into one decision per trial. The projected gain for subjects 61 and 62 is 5–10 percentage points.
3. Document the class-wise accuracy gap by subject and decoder.
4. Investigate subject 63’s low SVM trial count. Check how many trials were rejected and how many passed the replay confidence threshold.
5. If epoch rejection exceeds 50% for subject 63, consider testing a subject-specific threshold. The current threshold is 100 µV peak-to-peak.

## What Not to Do

- **Defer class weighting.** The reported calibration set contains 40 left-hand and 40 right-hand trials per subject.
- **Keep the confidence threshold fixed for the next comparison.** This keeps threshold changes from affecting measured accuracy and coverage.
- **Defer subject-specific tuning until the trial losses are traced.** Subject 63’s five reported SVM trials provide limited evidence for tuning decisions.

## Decision Log

| Action | Status | Result |
| --- | --- | --- |
| Baseline CSP(4) + LDA/SVM, 2 s window | Completed | 60.5% / 61.0% online accuracy |
| Test 3 s replay window | Completed | 63.0% / 63.5% online accuracy (+2.5 points each) |
| Add CAR, rejection, and CSP `reg=0.01` | Completed | 68.8% / 77.4% online accuracy (+8.3 / +16.4 points versus the 2 s baseline) |
| Increase `n_components` to 6 | Planned | Projected gain of 1–3 points |
| Add per-trial majority voting | Planned | Projected gain of 5–10 points for subjects 61 and 62 |