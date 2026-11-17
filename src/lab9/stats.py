"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge):
        raise ValueError("human and judge must have the same length")
    pairs = [(str(h).strip().upper(), str(j).strip().upper()) for h, j in zip(human, judge)]
    return {
        "tp": sum(h == POS and j == POS for h, j in pairs),
        "fp": sum(h != POS and j == POS for h, j in pairs),
        "fn": sum(h == POS and j != POS for h, j in pairs),
        "tn": sum(h != POS and j != POS for h, j in pairs),
    }


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    # TODO M2: precision = tp/(tp+fp), recall = tp/(tp+fn); return 0.0 when the denominator is 0
    cm = confusion(human, judge)
    p_den = cm["tp"] + cm["fp"]
    r_den = cm["tp"] + cm["fn"]
    return (cm["tp"] / p_den if p_den else 0.0, cm["tp"] / r_den if r_den else 0.0)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    if len(human) != len(judge) or not human:
        raise ValueError("kappa requires equally sized, non-empty labels")
    n = len(human)
    cm = confusion(human, judge)
    p_o = (cm["tp"] + cm["tn"]) / n
    h_fail = sum(str(x).strip().upper() == POS for x in human)
    j_fail = sum(str(x).strip().upper() == POS for x in judge)
    p_e = (h_fail * j_fail + (n - h_fail) * (n - j_fail)) / (n * n)
    if p_e == 1:
        raise ValueError("kappa is undefined when expected agreement is 1")
    return (p_o - p_e) / (1 - p_e)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    denominator = sensitivity + specificity - 1
    if denominator <= 0:
        raise ValueError("Rogan-Gladen is undefined for a non-informative judge")
    corrected = (observed_rate + specificity - 1) / denominator
    return min(1.0, max(0.0, corrected))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    if len(a) != len(b) or not a:
        raise ValueError("paired bootstrap requires equally sized, non-empty samples")
    import numpy as np
    from scipy.stats import bootstrap

    left = np.asarray(a, dtype=float)
    right = np.asarray(b, dtype=float)
    if np.array_equal(left, right):
        return 0.0, 0.0, 0.0
    result = bootstrap(
        (left, right),
        lambda x, y, axis: np.mean(x - y, axis=axis),
        paired=True,
        vectorized=True,
        n_resamples=n_resamples,
        confidence_level=confidence,
        method="percentile",
        rng=np.random.default_rng(rng),
    )
    return float((left - right).mean()), float(result.confidence_interval.low), float(result.confidence_interval.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    from math import comb
    if n <= 0 or c < 0 or c > n or k <= 0 or k > n:
        raise ValueError("require 0 <= c <= n and 1 <= k <= n")
    return 1.0 - (comb(n - c, k) / comb(n, k) if n - c >= k else 0.0)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    from math import comb
    if n <= 0 or c < 0 or c > n or k <= 0 or k > n:
        raise ValueError("require 0 <= c <= n and 1 <= k <= n")
    return comb(c, k) / comb(n, k) if c >= k else 0.0
