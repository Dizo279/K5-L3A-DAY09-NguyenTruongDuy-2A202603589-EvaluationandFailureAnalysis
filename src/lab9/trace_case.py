"""Trace -> decision: lay one trial's reply, tool calls and ledger side by side.

    python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11

Find the FIRST wrong step, then turn that trial into a regression case
(docs/trace_case.md). Runs the shape on a fresh temp store, never the team DB.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from lab8.console import utf8_stdio
from lab8.db import load_json, load_jsonl
from lab9 import variants
from lab9.eval import WORLD, make_task


def investigate(shape: str, claim_id: str, seed: int) -> dict:
    variants.register()
    claims = load_jsonl(Path("data/public_claims.jsonl"))
    labels = {c["claim_id"]: c["expected"] for c in claims}
    with tempfile.TemporaryDirectory(prefix="lab9-case-", ignore_cleanup_errors=True) as tmp:
        trial = make_task(shape, load_json(WORLD), claims, labels, Path(tmp))({"claim_id": claim_id, "seed": seed})
    return {"trial": trial, "label": labels[claim_id]}


def evidence_record(shape: str, claim_id: str, seed: int, case: dict[str, Any]) -> dict[str, Any]:
    trial, label = case["trial"], case["label"]
    result = trial.get("result") or {}
    summary_keys = ("status", "proposal_amount", "error_reason")
    label_keys = ("status", "proposal_amount", "refund_vnd", "refund_count", "approval_ok")
    return {
        "trace_id": f"{shape}:{claim_id}@{seed}",
        "shape": shape,
        "claim_id": claim_id,
        "seed": seed,
        "lab8_pass": trial["lab8_pass"],
        "lab8_reason": trial["lab8_reason"],
        "result": {key: result[key] for key in summary_keys if key in result},
        "ledger": {key: trial["snapshot"].get(key) for key in ("refund_vnd", "refund_count")},
        "label": {key: label.get(key) for key in label_keys},
        "unexpected_rows": trial["unexpected_rows"],
        "events": trial["events"],
    }


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.trace_case")
    ap.add_argument("--shape", required=True)
    ap.add_argument("--claim", required=True)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--out", type=Path, help="write a durable JSON copy of the trace evidence")
    args = ap.parse_args(argv)
    case = investigate(args.shape, args.claim, args.seed)
    t, label = case["trial"], case["label"]
    print(f"== {args.shape} {args.claim}@{args.seed}  lab8 grader: {'PASS' if t['lab8_pass'] else 'FAIL'} ({t['lab8_reason']})")
    print("-- trace (step, kind, payload)")
    for i, e in enumerate(t["events"], 1):
        print(f"  {i:>2} {e.get('kind', '?'):<18} {json.dumps(e.get('payload'), ensure_ascii=False)[:110]}")
    print("-- ledger vs label")
    for k in ("refund_vnd", "refund_count"):
        mark = "" if t["snapshot"].get(k) == label.get(k) else "   <-- differs"
        print(f"  {k:<14} ledger={t['snapshot'].get(k)!s:<8} label={label.get(k)}{mark}")
    print(f"  status         result={t['result'].get('status')!s:<8} label={label.get('status')}")
    print(f"  unexpected ledger rows: {t['unexpected_rows']}")
    if args.out:
        evidence = evidence_record(args.shape, args.claim, args.seed, case)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
