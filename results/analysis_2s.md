## Online accuracy (above threshold)

| Decoder | Windows | Accuracy | Mean latency (ms) |
| --- | ---: | ---: | ---: |
| LDA | 9,268 | 60.4014% | 0.310117 |
| SVM | 8,815 | 60.9983% | 0.302432 |

## Failure counts

| Decoder | Low-confidence windows | Confident but wrong | Majority-class fraction | Total windows |
| --- | ---: | ---: | ---: | ---: |
| LDA | 1,292 | 3,670 | 0.610133 | 10,560 |
| SVM | 1,745 | 3,438 | 0.656818 | 10,560 |

## Confidence calibration

| Confidence bin | LDA mean | LDA count | SVM mean | SVM count |
| --- | ---: | ---: | ---: | ---: |
| `[0.5, 0.6)` | 0.497678 | 1,292 | 0.509456 | 1,745 |
| `[0.6, 0.7)` | 0.566814 | 1,362 | 0.555428 | 1,741 |
| `[0.7, 0.8)` | 0.556946 | 1,598 | 0.574009 | 1,993 |
| `[0.8, 0.9)` | 0.581081 | 1,998 | 0.631692 | 2,335 |
| `[0.9, 1.01)` | 0.643852 | 4,310 | 0.652221 | 2,746 |