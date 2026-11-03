# T-033: Three-Seed Statistical Repeat (Main Model M1)

## Summary Metrics Across Seeds (Seeds 42, 43, 44)

| Seed | Val Macro F1 | Test Macro F1 | Test Accuracy | Test Cohen's Kappa | Best Epoch | Train Seconds | Brown Spot -> Leaf Blast Errors |
|---|---|---|---|---|---|---|---|
| **42** | 0.8561 | **0.8534** | 0.8333 (83.33%) | 0.7730 | 21 | 1459.66s | 11 |
| **43** | 0.8259 | **0.8532** | 0.8333 (83.33%) | 0.7735 | 14 | 649.43s | 9 |
| **44** | 0.8669 | **0.8761** | 0.8696 (86.96%) | 0.8219 | 23 | 1000.93s | 3 |
| **Mean** | **0.8496** | **0.8609** | **0.8454 (84.54%)** | **0.7895** | - | - | - |
| **Std (ddof=1)** | **0.0213** | **0.0132** | **0.0209** | **0.0281** | - | - | - |

## Quality Gate 2 Evaluation Across Seeds
- **Threshold**: Test Macro F1 $\ge 0.8000$
- **Seed 42**: 0.8534 (MET)
- **Seed 43**: 0.8532 (MET)
- **Seed 44**: 0.8761 (MET)
- **Mean Test Macro F1**: **0.8609 $\pm$ 0.0132**
- **Overall Gate 2 Status**: **MET ON ALL 3 SEEDS**

## Brown Spot to Leaf Blast Confusion Consistency
- **Baseline B2 (Frozen Base)**: 18 errors
- **Seed 42**: 11 errors
- **Seed 43**: 9 errors
- **Seed 44**: 3 errors
- **Mean Errors**: 7.67 $\pm$ 4.16

## Observations and Scientific Conclusions
1. Stage 2 fine-tuning demonstrates consistent convergence across diverse random initializations and data augmentation orderings, with a mean test macro F1 of 0.8609 $\pm$ 0.0132.
2. Quality Gate 2 (Macro F1 >= 0.80) is conclusively met across all three seeds, confirming statistical robustness beyond random seed variance.
3. Brown Spot to Leaf Blast confusion is consistently reduced in all fine-tuned seeds relative to the frozen baseline B2 (18 errors).
