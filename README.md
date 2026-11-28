# Dreyer2023B Motor Imagery Replay Benchmark

Compares CSP+LDA and CSP+SVM on Dreyer2023B EEG using held-out runs and simulated real-time replay. Reports window-level accuracy above a confidence threshold, accuracy by confidence bin, decoder failure modes, and trial-level accuracy using majority voting.

## Overview

- **Dataset.** Dreyer2023B left- and right-hand motor imagery contains 21 subjects, 27 EEG channels, and six runs of 40 trials per subject. This benchmark reports results for subjects 61–63.
- **Split.** Train on calibration runs R1–R2 and evaluate on online-feedback runs R3–R6.
- **Epoch window.** 3.5–7.5 s, starting 0.5 s after the cue to reduce cue-evoked contamination.
- **Channels.** C3, C4, Cz, FC1, FC2, CP1, and CP2.
- **Decoders.** CSP+LDA and CSP+SVM share the feature and replay settings within each version.
- **Replay.** The retained configuration uses a 3 s window, a 0.2 s update interval, a confidence threshold of 0.6, and four CSP components.

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

| Version | Configuration | Window accuracy above threshold, LDA | Window accuracy above threshold, SVM | Accuracy at confidence ≥ 0.9 |
| --- | --- | ---: | ---: | --- |
| v0.1 | Baseline, 2 s window | 60.5% | 61.0% | ~65% |
| v0.2 | 3 s replay window | 63.0% | 63.5% | ~70% |
| v0.3 | CAR, epoch rejection, CSP `reg=0.01`, four components | 68.8% | 77.4% | 85.8% LDA / 91.4% SVM |
| v0.4 | Six CSP components (reverted to four) | 69.1% | 69.8% | 79.5% LDA / 87.1% SVM |

In v0.3, LDA accepted 1,909 of 2,400 windows (79.5% coverage) and SVM accepted 1,336 (55.7% coverage). Version 5 evaluates trial-level decisions. The highest reported trial accuracy was 77.7% for subject 62 with LDA.

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

| Subject | Training trials | Left | Right | CV AUC | Std |
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

| Subject | Decoder | Left accuracy | Right accuracy | Trials | Trials < 50% | Trials > 80% |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 61 | LDA | 0.467 | 0.790 | 160 | 51 | 57 |
| 61 | SVM | 0.379 | 0.885 | 160 | 51 | 68 |
| 62 | LDA | 0.640 | 0.665 | 160 | 50 | 62 |
| 62 | SVM | 0.637 | 0.709 | 160 | 52 | 70 |
| 63 | LDA | 0.339 | 0.713 | 160 | 79 | 39 |
| 63 | SVM | 0.257 | 0.773 | 160 | 81 | 41 |

For subjects 61 and 63, right-hand accuracy ranged from 0.71 to 0.89 and left-hand accuracy from 0.26 to 0.47. The 3 s window had the highest mean calibration CV AUC across the three subjects. Gains from increasing CSP dimensionality were small and subject-specific.

## Version 2 — Preprocessing

- Applied common average reference (CAR) to suppress signal components shared across channels.
- Added epoch rejection at 100 µV peak-to-peak.
- Added CSP regularization (`reg=0.01`) to handle rank deficiency after CAR.
- Retained the 3 s replay window.
- Fixed buffer priming by pushing the first window before entering the replay loop.

### CV AUC on calibration runs (R1–R2)

| Subject | Baseline LDA | After preprocessing LDA | Baseline SVM | After preprocessing SVM |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.62 | 0.80 | 0.63 | 0.82 |
| 62 | 0.77 | 0.88 | 0.73 | 0.89 |
| 63 | 0.59 | 0.61 | 0.60 | 0.61 |

### Online accuracy on held-out runs (R3–R6)

| Decoder | v0.1 baseline | v0.3 after preprocessing | Difference (percentage points) |
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

The raw failure counts reflect both the error rate and the number of evaluated windows.

## Version 3 — Post-Preprocessing Diagnosis

### Training signal quality (CV AUC, R1–R2)

| Subject | Training trials | Left | Right | CV AUC | Std |
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

### Window-length sensitivity

| Subject | 1 s | 2 s | 3 s | 4 s |
| --- | ---: | ---: | ---: | ---: |
| 61 | 0.83 | 0.83 | 0.87 | 0.80 |
| 62 | 0.75 | 0.84 | 0.88 | 0.88 |
| 63 | 0.56 | 0.74 | 0.61 | 0.61 |

After preprocessing, the 3 s window performed best for subject 61 and tied with 4 s for subject 62. The 2 s window performed best for subject 63 and had the highest mean calibration CV AUC across the three subjects.

### Error concentration

| Subject | Decoder | Left accuracy | Right accuracy | Trials | Trials < 50% | Trials > 80% |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 61 | LDA | 0.55 | 0.90 | 155 | 42 | 108 |
| 61 | SVM | 0.55 | 0.93 | 149 | 40 | 108 |
| 62 | LDA | 0.78 | 0.78 | 157 | 33 | 113 |
| 62 | SVM | 0.74 | 0.87 | 154 | 34 | 113 |
| 63 | LDA | 0.13 | 0.82 | 119 | 58 | 60 |
| 63 | SVM | 0.00 | 0.50 | 5 | 3 | 2 |

Subject 62 had equal class-wise accuracy with LDA. Subject 61 retained a large class-wise gap with both decoders. Subject 63 had 0.13 left-hand LDA accuracy, and the SVM diagnosis included five trials. The cause of the low SVM trial count remains unverified.

## Version 4 — Six-Component CSP Test (Reverted to Four)

### CV AUC on calibration runs (R1–R2)

| Subject | 4 components | 6 components |
| --- | ---: | ---: |
| 61 | 0.80 | 0.83 |
| 62 | 0.88 | 0.90 |
| 63 | 0.61 | 0.69 |

### Online accuracy on held-out runs (R3–R6)

| Decoder | v0.3 (4 components) | v0.4 (6 components) | Difference (percentage points) |
| --- | ---: | ---: | ---: |
| LDA | 68.8% | 69.1% | +0.3 |
| SVM | 77.4% | 69.8% | −7.6 |

### Other replay metrics

| Metric | v0.3 LDA | v0.4 LDA | v0.3 SVM | v0.4 SVM |
| --- | ---: | ---: | ---: | ---: |
| Accuracy at confidence ≥ 0.9 | 85.8% | 79.5% | 91.4% | 87.1% |
| Confident-but-wrong windows | 596 | 653 | 302 | 594 |
| Majority-class fraction | 63.8% | 58.9% | 65.8% | 63.1% |

Six components raised calibration CV AUC for all three subjects. Held-out SVM accuracy fell by 7.6 points and accuracy in the highest confidence bin fell for both decoders. The benchmark reverted to four components.

## Version 5 — Per-Trial Majority Vote (Final)

Aggregate the replay window predictions within each trial by majority vote to produce one class decision per trial.

| Subject | LDA trial accuracy | SVM trial accuracy |
| --- | ---: | ---: |
| 61 | 72.9% | 73.2% |
| 62 | **77.7%** | 77.3% |
| 63 | 50.4% | 40.0% |

The v0.3 window references (68.8% LDA and 77.4% SVM) pool windows across subjects. Measuring a voting gain requires subject-matched window results and the trial counts or coverage for each decoder.

Subject 62 achieved the highest reported trial accuracy with both decoders. Subject 63 had the lowest reported trial accuracy with both decoders. Quantifying temporal consistency requires examining the prediction sequence within each trial.

## Final Results — Four vs. Six CSP Components

Both configurations used common average reference (CAR), epoch rejection at 100 µV peak-to-peak, and CSP regularization (`reg=0.01`). The window-level scores are pooled across subjects 61–63. The trial-level scores are reported by subject.

### Per-window accuracy on held-out runs (R3–R6)

| Decoder | 4 components | 6 components | Difference, 6 minus 4 (percentage points) |
| --- | ---: | ---: | ---: |
| LDA | 68.8% | 69.1% | +0.3 |
| SVM | **77.4%** | 69.8% | −7.6 |

Six components raised calibration-run CV AUC for all three subjects. In held-out replay, LDA window accuracy changed by 0.3 percentage points and SVM window accuracy fell by 7.6 points.

### Per-trial majority vote accuracy

| Subject | Decoder | 4 components | 6 components | Higher observed accuracy |
| --- | --- | ---: | ---: | --- |
| 61 | LDA | 72.9% | **75.3%** | 6 components |
| 61 | SVM | 73.2% | **74.2%** | 6 components |
| 62 | LDA | **77.7%** | 72.3% | 4 components |
| 62 | SVM | **77.3%** | 73.9% | 4 components |
| 63 | LDA | 50.4% | **51.9%** | 6 components |
| 63 | SVM | 40.0%† | 52.4% | Inconclusive |

† The four-component SVM result for subject 63 covers five trials. The observed difference has limited interpretability without comparable trial counts and coverage.

### Combined interpretation

- **Window-level default.** Four components gave the highest pooled accuracy above threshold, 77.4% with SVM. The LDA results were close across dimensionalities.
- **Trial-level results.** Voting yields one decision per trial. Six components had higher observed accuracy for subject 61 with both decoders, while four had higher accuracy for subject 62. Subject 63 remained the weakest performer under both configurations.
- **Subject-specific selection.** A follow-up could choose `n_components` on each subject’s calibration runs using the intended decision metric, then evaluate once on held-out runs. Calibration CV AUC alone favored six components for all three subjects in this benchmark.
- **Best observed scores.** Four-component SVM reached 77.4% pooled window accuracy and 77.3% trial accuracy for subject 62. Four-component LDA achieved the highest observed trial accuracy, 77.7% for subject 62.

## Summary of What We Know

| Question | Evidence |
| --- | --- |
| Did the updated configuration improve replay accuracy? | Accuracy above threshold rose by 8.3 points for LDA and 16.4 points for SVM from v0.1 to v0.3. Several settings changed between these versions. |
| How accurate were high-confidence predictions? | At confidence ≥ 0.9, v0.3 accuracy was 85.8% for LDA and 91.4% for SVM. |
| Did the class-wise accuracy gap persist? | Subjects 61 and 63 showed substantial gaps after preprocessing. The cause remains unverified. |
| Which decoder had higher online accuracy in v0.3? | SVM reached 77.4% at 55.7% coverage. LDA reached 68.8% at 79.5% coverage. |
| Which CSP dimensionality was retained? | Four components. Six increased calibration-run CV AUC and reduced held-out SVM accuracy by 7.6 percentage points. |
| Which window length performed best? | It varied by subject. Mean calibration CV AUC peaked at 3 s before preprocessing and 2 s after preprocessing. The retained replay window is 3 s. |
| What was the best trial-level result? | Subject 62 reached 77.7% with LDA and 77.3% with SVM. |

## Decision Log

| Action | Status | Result |
| --- | --- | --- |
| Baseline CSP(4) + LDA/SVM, 2 s window | Completed | 60.5% LDA / 61.0% SVM online accuracy |
| Test 3 s replay window | Completed | 63.0% LDA / 63.5% SVM online accuracy |
| Add CAR, epoch rejection, and CSP `reg=0.01` | Completed | 68.8% LDA / 77.4% SVM online accuracy |
| Test `n_components=6` | Completed, reverted to four | Held-out accuracy changed by +0.3 points for LDA and −7.6 points for SVM. |
| Add per-trial majority voting | Completed | Highest reported trial accuracy was 77.7% for subject 62 with LDA. |
| Compare four and six components at trial level | Completed | Six scored higher for subject 61. Four scored higher for subject 62. Four remains the default. |

## Conclusion

Moving from 2 s to 3 s in v0.2 raised pooled window accuracy by about 2.5 percentage points for both decoders. The combined preprocessing and replay changes in v0.3 raised accuracy above threshold by 8.3 points for LDA and 16.4 for SVM relative to v0.1. In the highest confidence bin, observed accuracy rose from approximately 65% to 85.8% for LDA and 91.4% for SVM.

The final pipeline uses CAR, 100 µV peak-to-peak epoch rejection, regularized CSP (`reg=0.01`), 3 s replay windows, and per-trial majority voting. Four CSP components remain the default based on pooled SVM window accuracy. Six components gave higher trial accuracy for some subject–decoder pairs. Subject 63 showed weak trial-level performance under both settings, with especially limited evidence for four-component SVM.