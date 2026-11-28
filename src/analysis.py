# src/analysis.py
import pandas as pd
import numpy as np


def online_accuracy(df, threshold):
    """Accuracy only on windows above confidence threshold."""
    d = df[df["above_threshold"]]
    if len(d) == 0:
        return {}
    out = {}
    for name, g in d.groupby("decoder"):
        out[name] = {
            "n_windows": len(g),
            "accuracy": float(g["correct"].mean()),
            "mean_latency_ms": float(g["latency"].mean() * 1000),
        }
    return out


def confidence_bins(df, bins=(0.5, 0.6, 0.7, 0.8, 0.9, 1.01)):
    """Accuracy vs confidence bin, per decoder."""
    out = {}
    for name, g in df.groupby("decoder"):
        g = g.copy()
        g["bin"] = pd.cut(g["confidence"], bins=bins, right=False)
        out[name] = g.groupby("bin", observed=True)["correct"].agg(["mean", "count"])
    return out


def failure_counts(df, threshold):
    """Count failure modes per decoder."""
    out = {}
    for name, g in df.groupby("decoder"):
        low_conf = (~g["above_threshold"]).sum()
        confident_wrong = ((g["above_threshold"]) & (~g["correct"])).sum()
        default_class = g["predicted"].value_counts(normalize=True).max()
        out[name] = {
            "low_confidence_windows": int(low_conf),
            "confident_but_wrong": int(confident_wrong),
            "majority_class_fraction": float(default_class),
            "total_windows": int(len(g)),
        }
    return out


def run_to_run_drift(df):
    """Accuracy per trial index (proxy for run drift)."""
    out = {}
    for name, g in df.groupby("decoder"):
        per_trial = g.groupby("trial")["correct"].mean()
        out[name] = per_trial
    return out

def per_trial_majority(df):
    """Aggregates window predictions into one vote per trial."""
    above = df[df["above_threshold"]].copy()
    results = []
    for (subj, dec, trial), g in above.groupby(["subject", "decoder", "trial"]):
        majority = g["predicted"].mode()[0]
        true = g["true_label"].iloc[0]
        results.append({
            "subject": subj,
            "decoder": dec,
            "trial": trial,
            "true_label": true,
            "majority_prediction": majority,
            "correct": majority == true,
            "n_windows": len(g),
            "n_correct_windows": int(g["correct"].sum()),
        })
    return pd.DataFrame(results)