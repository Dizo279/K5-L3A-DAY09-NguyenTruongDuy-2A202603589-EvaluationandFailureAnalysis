# Judge audit

## M2 calibration results

| Criterion | n | kappa | Precision | Recall | Floors (kappa>=0.6, P>=0.8, R>=0.7) | Decision |
|---|---:|---:|---:|---:|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | PASS | Use for tone gate |
| helpful | 100 | 0.375 | 1.000 | 0.300 | FAIL | Exclude from gate |

Observed FAIL rate for `tone_ok` is 0.280; Rogan-Gladen corrected rate is 0.300.
`helpful` has perfect precision but recall 0.300, missing 21 of 30 human-labeled failures. It is too permissive to be used as a release gate.

## Manual audit of five disagreements

| # | Case | Judge | Human | Correct | Rubric action |
|---:|---|---|---|---|---|
| 1 | H-008 | PASS | FAIL | Human | Reject overly casual register. |
| 2 | H-017 | PASS | FAIL | Human | Add a negative example for inappropriate familiarity. |
| 3 | H-029 | PASS | FAIL | Human | Reject replies that do not address the request. |
| 4 | H-042 | FAIL | PASS | Human | Accept valid paraphrases with the correct amount/order. |
| 5 | H-051 | FAIL | PASS | Human | Do not penalize the valid synonym `refund`. |

The audit indicates both false negatives and false positives. `tone_ok` still passes all three floors, but should be recalibrated with held-out labels before broader use.

## M2 conclusion

- Use `tone_ok` only for language/tone criteria after calibration.
- Exclude `helpful` from the gate because kappa and recall fail the floors.
- Money, approval, secret, and ledger-state checks remain code-based; a judge must not replace trajectory assertions.
- Both datasets are public replay data, so new human-labeled held-out examples are still required.

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | | | | | | dùng / loại |
| helpful | | | | | | dùng / loại |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | | | | | |

## Kết luận
- Tiêu chí bị loại và lý do (dẫn ma trận nhầm lẫn).
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.
