import os 
import yaml 
import numpy as np 
from src.data_loader import load_dataset, load_paradigm, get_subject_data, split_by_runs
from src.decoder import load_decoder, ReplayDecoder
from src.replay import replay_trials

def main(config_path="config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    os.makedirs(config["output"]["results_dir"], exist_ok=True)
    dataset = load_dataset(config)
    paradigm = load_paradigm(config)

    for subject in config["dataset"]["subjects"]:
        X, labels, meta = get_subject_data(dataset, paradigm, subject)
        _, test_mask = split_by_runs(
            meta, config["training"]["train_runs"], config["training"]["test_runs"]
        )
        X_test, y_test = X[test_mask], labels[test_mask]

        decoders = {}
        for name in ["lda", "svm"]:
            path = f"{config['output']['models_dir']}/sub{subject}_{name}.joblib"
            decoders[name] = ReplayDecoder(load_decoder(path))

        log_path = f"{config['output']['results_dir']}/sub{subject}_replay.csv"
        df = replay_trials(X_test, y_test, meta[test_mask], decoders, config, log_path)
        print(f"Subject {subject}: {len(df)} window predictions logged to {log_path}")

if __name__ == "__main__":
    main()