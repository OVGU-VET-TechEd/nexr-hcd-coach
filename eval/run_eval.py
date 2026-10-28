#!/usr/bin/env python3
"""Ask every question in eval/questions/*.yaml and write a CSV for human rating.

    python eval/run_eval.py [--only P2] [--out eval/results/run.csv]
"""
import argparse
import csv
import datetime as dt
import os
import pathlib
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from nexr_common import ROOT, webui_session  # noqa: E402

RUBRIC = ["grounding", "citation", "phase_fit", "tool_agnostic", "language", "ethics_gdpr", "actionability"]


def load_questions(only):
    for path in sorted((ROOT / "eval" / "questions").glob("*.yaml")):
        if path.name.startswith("_TEMPLATE"):
            continue
        data = yaml.safe_load(path.read_text("utf-8")) or {}
        if only and data.get("phase") != only:
            continue
        for item in data.get("items", []):
            yield data.get("phase", path.stem), item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="phase key to run, e.g. P2 or guardrails")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    model = os.environ.get("NEXR_MODEL_ID", "nexr-coach")
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = pathlib.Path(args.out or ROOT / "eval" / "results" / f"run-{stamp}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)

    s, base = webui_session()
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "phase", "lang", "question", "expect", "answer", "sources", "model", "timestamp",
                    *RUBRIC, "hard_fail", "rater", "notes"])
        for phase, item in load_questions(args.only):
            r = s.post(f"{base}/api/chat/completions", timeout=600, json={
                "model": model, "stream": False,
                "messages": [{"role": "user", "content": item["question"]}],
            })
            if r.ok:
                body = r.json()
                answer = body["choices"][0]["message"]["content"]
                sources = "; ".join(
                    sorted({m.get("source", "") for src in body.get("sources", []) for m in src.get("metadata", [])})
                )
            else:
                answer, sources = f"ERROR {r.status_code}: {r.text[:300]}", ""
            w.writerow([item["id"], phase, item.get("lang", "en"), item["question"], item.get("expect", ""),
                        answer, sources, model, dt.datetime.now().isoformat(timespec="seconds"),
                        *[""] * len(RUBRIC), "", "", ""])
            print(f"{item['id']}: {'ok' if r.ok else r.status_code}")
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
