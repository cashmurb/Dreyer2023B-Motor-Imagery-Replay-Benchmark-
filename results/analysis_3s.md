## Online accuracy (above threshold)

| Decoder | Windows | Accuracy | Mean latency (ms) |
| --- | ---: | ---: | ---: |
| LDA | 4,923 | 62.9697% | 0.329128 |
| SVM | 4,703 | 63.4701% | 0.317558 |

## Failure counts

| Decoder | Low-confidence windows | Confident but wrong | Majority-class fraction | Total windows |
| --- | ---: | ---: | ---: | ---: |
| LDA | 837 | 1,823 | 0.627257 | 5,760 |
| SVM | 1,057 | 1,718 | 0.697743 | 5,760 |

## Confidence calibration

| Confidence bin | LDA mean | LDA count | SVM mean | SVM count |
| --- | ---: | ---: | ---: | ---: |
| `[0.5, 0.6)` | 0.548387 | 837 | 0.556291 | 1,057 |
| `[0.6, 0.7)` | 0.542254 | 852 | 0.549451 | 1,001 |
| `[0.7, 0.8)` | 0.599022 | 818 | 0.594727 | 1,024 |
| `[0.8, 0.9)` | 0.591029 | 1,137 | 0.666425 | 1,382 |
| `[0.9, 1.01)` | 0.697543 | 2,116 | 0.698302 | 1,296 |