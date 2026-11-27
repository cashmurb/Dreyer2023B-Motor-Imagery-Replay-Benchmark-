import glob 
import yaml
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold
from src.data_loader import load_dataset, load_paradigm, get_subject_data, split_by_runs
from src.decoder import build_decoder

def check_training_signal(config):
    """
    Per-subject CV AUC on runs 1-2: is the signal learnable at all?
    """
    dataset = load_dataset(config)
    paradigm = load_paradigm(config)
    rows = []
    for subject in config["dataset"]["subjects"]:
        X, labels, meta = get_subject_data(dataset, paradigm, subject, config)
        train_mask, _ = split_by_runs(meta, config["training"]["train_runs"], config["training"]["test_runs"])
        X_tr, y_tr = X[train_mask], labels[train_mask]
        label_map = {"left_hand": 0, "right_hand": 1} 
        y_tr = np.array([label_map[l] for l in y_tr])

        # class balance in training 
        n_left = int((y_tr == 0).sum())
        n_right = int((y_tr == 1).sum())

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        pipe = build_decoder("lda", config["training"]["csp_components"])
        auc = cross_val_score(pipe, X_tr, y_tr, cv=cv, scoring="roc_auc")

        rows.append({
            "subject": subject, 
            "n_train": len(y_tr),
            "n_left": n_left,
            "n_right": n_right,
            "cv_auc_mean": float(auc.mean()),
            "cv_auc_std": float(auc.std()),
        })
    return pd.DataFrame(rows)

def check_csp_dimensionality(config):
    """ Does more CSP components help? Tested on runs 1-2 only. """
    dataset = load_dataset(config)
    paradigm = load_paradigm(config)
    rows = []
    for subject in config["dataset"]["subjects"]:
        X, labels, meta = get_subject_data(dataset, paradigm, subject, config)
        train_mask, _ = split_by_runs(meta, config["training"]["train_runs"], config["training"]["test_runs"])
        X_tr, y_tr = X[train_mask], labels[train_mask]
        label_map = {"left_hand": 0, "right_hand": 1}
        y_tr = np.array([label_map[l] for l in y_tr])
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        for n in [2, 4, 6, 8]:
            pipe = build_decoder("lda", n)
            auc = cross_val_score(pipe, X_tr, y_tr, cv=cv, scoring="roc_auc")
            rows.append({
                "subject": subject, 
                "n_components": n, 
                "cv_auc_mean": float(auc.mean())
            })
    return pd.DataFrame(rows).pivot(index="subject", columns="n_components", values="cv_auc_mean")

def check_window_length(config):
    """Replay-style accuracy at different window lengths using saved CSVs is not possible; 
    instead approximate via training-window truncation on runs 1-2."""

    dataset = load_dataset(config)
    paradigm = load_paradigm(config)
    sfreq = 250
    rows = []
    for subject in config["dataset"]["subjects"]:
        X, labels, meta = get_subject_data(dataset, paradigm, subject, config)
        train_mask, _ = split_by_runs(meta, config["training"]["train_runs"], config["training"]["test_runs"])
        X_tr, y_tr = X[train_mask], labels[train_mask]
        label_map = {"left_hand": 0, "right_hand": 1}
        y_tr = np.array([label_map[l] for l in y_tr])
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        for win_s in [1.0, 2.0, 3.0, 4.0]:
            n_samples = int(win_s * sfreq)
            X_cut = X_tr[:, :, :n_samples]
            pipe = build_decoder("lda", config["training"]["csp_components"])
            auc = cross_val_score(pipe, X_cut, y_tr, cv=cv, scoring="roc_auc")
            rows.append({
                "subject": subject, 
                "window_s": win_s, 
                "cv_auc_mean": float(auc.mean())
            })
    return pd.DataFrame(rows).pivot(index="subject", columns="window_s", values="cv_auc_mean")

def check_error_concentration(config):
    """ From existing replay CSVs: which trials/classes produce errors?"""
    rows = []
    for path in glob.glob(f"{config['output']['results_dir']}/*_replay.csv"):
        df = pd.read_csv(path)
        subject = path.split("sub")[-1].split("_")[0]
        for name, g in df.groupby("decoder"):
            above = g[g["above_threshold"]]
            if len(above) == 0:
                continue 
            # per-class accuracy
            acc_by_class = above.groupby("true_label")["correct"].mean().to_dict()

            # per-trial accuracy
            per_trial = above.groupby("trial")["correct"].mean().astype(float).squeeze()

            if isinstance(per_trial, pd.DataFrame): 
                per_trial = per_trial.iloc[:, 0]
            rows.append({
                "subject": subject, 
                "decoder": name,
                "acc_left": float(acc_by_class.get(0, np.nan)),
                "acc_right": float(acc_by_class.get(1, np.nan)),
                "n_trials": int(len(per_trial)),
                "trials_below_50pct": int((per_trial < 0.5).sum()), 
                "trials_above_80pct": int((per_trial > 0.8).sum()),
            })
    return pd.DataFrame(rows)

def main(config_path="config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    print("\n 1. Training signal quality (Is there anything to learn?)")
    print(check_training_signal(config).to_string(index=False))

    print("\n 2. CSP dimensionality sensitivity (Are 4 components enough?)")
    print(check_csp_dimensionality(config).to_string())

    print("\n 3. Window length sensitivity (Is 2s too short?)")
    print(check_window_length(config).to_string())

    print("\n 4. Error concentration (Where do eerrors come from?)")
    print(check_error_concentration(config).to_string(index=False))

if __name__ == "__main__":
    main()