## Online accuracy (above threshold)

| Decoder | Windows | Accuracy | Mean latency (ms) |
| --- | ---: | ---: | ---: |
| LDA | 1,909 | 68.7795% | 0.250616 |
| SVM | 1,336 | 77.3952% | 0.241440 |

## Failure counts

| Decoder | Low-confidence windows | Confident but wrong | Majority-class fraction | Total windows |
| --- | ---: | ---: | ---: | ---: |
| LDA | 491 | 596 | 0.637917 | 2,400 |
| SVM | 1,064 | 302 | 0.657500 | 2,400 |

## Confidence calibration

| Confidence bin | LDA mean | LDA count | SVM mean | SVM count |
| --- | ---: | ---: | ---: | ---: |
| `[0.5, 0.6)` | 0.590631 | 491 | 0.530075 | 1,064 |
| `[0.6, 0.7)` | 0.573657 | 577 | 0.660131 | 306 |
| `[0.7, 0.8)` | 0.606452 | 465 | 0.758904 | 365 |
| `[0.8, 0.9)` | 0.724242 | 330 | 0.753049 | 328 |
| `[0.9, 1.01)` | 0.858473 | 537 | 0.913947 | 337 |