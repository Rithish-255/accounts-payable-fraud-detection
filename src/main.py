from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ALLOWED_SEQUENCE = [
    "invoice_created",
    "supplier_validation",
    "manager_approval",
    "finance_check",
    "payment_released",
]


def generate_event_log(n_invoices: int = 1200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []

    vendors = [f"VENDOR_{i:02d}" for i in range(1, 21)]
    departments = ["Procurement", "Finance", "Operations", "AP", "Audit"]
    payment_modes = ["ACH", "Wire", "Check", "Card"]

    for invoice_id in range(1, n_invoices + 1):
        vendor = vendors[(invoice_id - 1) % len(vendors)]
        amount = round(float(rng.uniform(250, 50000)), 2)
        invoice_date = pd.Timestamp("2025-01-01") + pd.Timedelta(days=(invoice_id % 365))
        department = departments[(invoice_id - 1) % len(departments)]
        payment_mode = payment_modes[(invoice_id - 1) % len(payment_modes)]

        steps = [
            "invoice_created",
            "supplier_validation",
            "manager_approval",
            "finance_check",
            "payment_released",
        ]

        if rng.random() < 0.2:
            steps.insert(2, "supplier_validation")
        if rng.random() < 0.12:
            steps.insert(3, "manager_approval")

        if rng.random() < 0.015:
            steps = ["invoice_created", "supplier_validation", "finance_check", "payment_released"]

        start_time = pd.Timestamp(invoice_date) + pd.Timedelta(hours=int(rng.integers(6, 48)))
        payment_reference = f"{vendor}-{invoice_id % 57}-{amount:,.2f}"

        for idx, step in enumerate(steps):
            ts = start_time + pd.Timedelta(hours=idx * 12 + int(rng.integers(1, 18)))
            records.append(
                {
                    "invoice_id": invoice_id,
                    "vendor": vendor,
                    "amount": amount,
                    "invoice_date": invoice_date,
                    "department": department,
                    "event_name": step,
                    "event_timestamp": ts,
                    "payment_mode": payment_mode,
                    "approval_status": "approved" if step in {"manager_approval", "finance_check"} else "pending",
                    "case_id": f"AP-{invoice_id:05d}",
                    "duplicate_flag": False,
                    "payment_reference": payment_reference,
                }
            )

        if rng.random() < 0.035:
            duplicate_ts = start_time + pd.Timedelta(days=2, hours=int(rng.integers(2, 10)))
            records.append(
                {
                    "invoice_id": invoice_id + n_invoices,
                    "vendor": vendor,
                    "amount": amount,
                    "invoice_date": invoice_date,
                    "department": department,
                    "event_name": "payment_released",
                    "event_timestamp": duplicate_ts,
                    "payment_mode": payment_mode,
                    "approval_status": "unapproved",
                    "case_id": f"AP-{invoice_id + n_invoices:05d}",
                    "duplicate_flag": True,
                    "payment_reference": payment_reference,
                }
            )

    df = pd.DataFrame(records)
    df = df.sort_values(["case_id", "event_timestamp"]).reset_index(drop=True)
    return df


def compute_activity_lag(df: pd.DataFrame) -> pd.Series:
    s = df.sort_values(["case_id", "event_timestamp"]).copy()
    s["lag_hours"] = s.groupby("case_id")["event_timestamp"].diff().dt.total_seconds() / 3600
    return s["lag_hours"].fillna(0)


def detect_duplicate_payments(df: pd.DataFrame) -> pd.DataFrame:
    payment_releases = df[df["event_name"] == "payment_released"].copy()
    grouped = (
        payment_releases.groupby(["vendor", "amount", "payment_reference"], as_index=False)
        .size()
        .rename(columns={"size": "payment_count"})
    )
    duplicates = grouped[grouped["payment_count"] > 1].copy()
    duplicate_cases = df[df["payment_reference"].isin(duplicates["payment_reference"])].copy()
    duplicate_cases["duplicate_flag"] = True
    return duplicate_cases


def detect_rogue_payments(df: pd.DataFrame) -> pd.DataFrame:
    payment_events = df[df["event_name"] == "payment_released"].copy()
    payment_events["rogue_flag"] = payment_events["approval_status"].eq("unapproved")
    return payment_events[payment_events["rogue_flag"]]


def detect_looped_cases(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.groupby(["case_id", "event_name"]).size().reset_index(name="count")
    return counts[counts["count"] > 1]


def run_conformance_checks(df: pd.DataFrame) -> pd.DataFrame:
    result = []
    for case_id, group in df.groupby("case_id"):
        events = list(group.sort_values("event_timestamp")["event_name"])
        ok = True
        for expected, actual in zip(ALLOWED_SEQUENCE, events[: len(ALLOWED_SEQUENCE)]):
            if actual != expected:
                ok = False
                break
        result.append({"case_id": case_id, "sequence_ok": ok, "events": events})
    return pd.DataFrame(result)


def summarize(df: pd.DataFrame) -> dict:
    total_invoices = df["invoice_id"].nunique()
    duplicate_cases = detect_duplicate_payments(df)
    rogue_cases = detect_rogue_payments(df)
    looped = detect_looped_cases(df)
    conformance = run_conformance_checks(df)

    invoice_activity = df.sort_values(["case_id", "event_timestamp"]).copy()
    invoice_activity["lag_hours"] = compute_activity_lag(invoice_activity)
    avg_activity_lag = float(invoice_activity["lag_hours"].mean())

    payment_events = df[df["event_name"] == "payment_released"].copy()
    payment_events = payment_events.sort_values(["case_id", "event_timestamp"]).reset_index(drop=True)
    payment_events["approval_to_payment_lag"] = (
        payment_events.groupby("case_id")["event_timestamp"].diff().dt.total_seconds() / 3600
    )
    approval_to_payment_lag = payment_events["approval_to_payment_lag"].fillna(0).mean()

    top_vendor = (
        df.groupby("vendor").size().sort_values(ascending=False).head(1).index[0]
        if not df.empty
        else "N/A"
    )

    return {
        "total_invoices": int(total_invoices),
        "duplicate_payment_candidates": int(duplicate_cases["payment_reference"].nunique()),
        "rogue_payments": int(rogue_cases.shape[0]),
        "invoices_with_skipped_approval": int((~conformance["sequence_ok"]).sum()),
        "looped_invoices": int(looped["case_id"].nunique()),
        "avg_activity_lag_hours": round(avg_activity_lag, 2),
        "approval_to_payment_lag_hours": round(approval_to_payment_lag, 2),
        "max_loops_per_invoice": int(looped["count"].max() if not looped.empty else 0),
        "top_risky_vendor": top_vendor,
        "risk_reasons": [
            "Duplicate vendor-reference clustering",
            "Payment release without proper approval",
            "Repeated validation loops",
            "Delayed approval-to-payment flow",
        ],
        "pql_metrics": {
            "PU_COUNT": total_invoices,
            "case_conformance_rate": round((conformance["sequence_ok"].mean() * 100), 2),
            "loop_rate": round((looped["case_id"].nunique() / total_invoices) * 100, 2),
        },
    }


def build_report(summary: dict) -> str:
    risk_text = "\n".join(f"- {i}" for i in summary["risk_reasons"])
    return f"""# Accounts Payable Duplicate Payment Detection Report

## Executive Overview

This report summarizes the process-mining analysis of the invoice-to-pay workflow and highlights duplicate and rogue payment risks.

## Key Metrics

- Total invoices analyzed: {summary['total_invoices']}
- Duplicate payment candidates: {summary['duplicate_payment_candidates']}
- Rogue / unauthorized payments: {summary['rogue_payments']}
- Invoices with skipped approval: {summary['invoices_with_skipped_approval']}
- Looping invoice cases: {summary['looped_invoices']}
- Average activity lag: {summary['avg_activity_lag_hours']} hours
- Approval-to-payment lag: {summary['approval_to_payment_lag_hours']} hours
- Top risky vendor: {summary['top_risky_vendor']}

## Process Mining Interpretation

- PU_COUNT: {summary['pql_metrics']['PU_COUNT']}
- Case conformance rate: {summary['pql_metrics']['case_conformance_rate']}%
- Loop rate: {summary['pql_metrics']['loop_rate']}%

## Risk Reasons

{risk_text}

## Recommendation

Priority must be given to duplicate payment references, approval bypass events, and invoices with repeated looping activities.
"""


def save_outputs(event_log: pd.DataFrame, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "ap_invoice_eventlog.csv"
    event_log.to_csv(csv_path, index=False)

    summary = summarize(event_log)
    json_path = output_dir / "duplicate_payment_summary.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_path = output_dir / "ap_process_report.md"
    report_path.write_text(build_report(summary), encoding="utf-8")
    return summary
