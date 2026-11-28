import glob
import yaml
import pandas as pd
from src.analysis import (
    online_accuracy, confidence_bins, failure_counts,
    run_to_run_drift, per_trial_majority,
)


def main(config_path="config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    threshold = config["replay"]["confidence_threshold"]

    # Load all CSVs and attach subject ID from the filename
    dfs = []
    for p in glob.glob(f"{config['output']['results_dir']}/*_replay.csv"):
        df = pd.read_csv(p)
        subject = int(p.split("sub")[-1].split("_")[0])
        df["subject"] = subject
        dfs.append(df)
    all_df = pd.concat(dfs, ignore_index=True)

    print("\n Online accuracy (above threshold) ")
    print(pd.DataFrame(online_accuracy(all_df, threshold)).T)

    print("\n Failure counts ")
    print(pd.DataFrame(failure_counts(all_df, threshold)).T)

    print("\n Confidence calibration ")
    for name, table in confidence_bins(all_df).items():
        print(f"\n{name}:\n{table}")

    print("\n Per-trial majority vote ")
    trials_df = per_trial_majority(all_df)
    for (subj, dec), g in trials_df.groupby(["subject", "decoder"]):
        print(f"Subject {subj}, {dec}: {g['correct'].mean():.3f} "
              f"({int(g['correct'].sum())}/{len(g)} trials)")


if __name__ == "__main__":
    main()