import glob
import yaml
import pandas as pd
from src.analysis import online_accuracy, confidence_bins, failure_counts, run_to_run_drift


def main(config_path="config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    threshold = config["replay"]["confidence_threshold"]

    all_df = pd.concat([pd.read_csv(p) for p in glob.glob(f"{config['output']['results_dir']}/*_replay.csv")])

    print("\n Online accuracy (above threshold) ")
    print(pd.DataFrame(online_accuracy(all_df, threshold)).T)

    print("\n Failure counts ")
    print(pd.DataFrame(failure_counts(all_df, threshold)).T)

    print("\n Confidence calibration ")
    for name, table in confidence_bins(all_df).items():
        print(f"\n{name}:\n{table}")


if __name__ == "__main__":
    main()