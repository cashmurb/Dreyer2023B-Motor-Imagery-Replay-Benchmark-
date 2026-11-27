import os 
import yaml 
import numpy as np 
from sklearn.model_selection import cross_val_score, StratifiedKFold
from src.data_loader import load_dataset, load_paradigm, get_subject_data, split_by_runs 
from src.decoder import build_decoder, save_decoder

def main(config_path="config.yaml"):
    with open(config_path) as f: 
        config = yaml.safe_load(f)
    
    os.makedirs(config["output"]["models_dir"], exist_ok=True)
    dataset=load_dataset(config)
    paradigm=load_paradigm(config)


    for subject in config["dataset"]["subjects"]:
        print(f"\n Subject {subject}")
        X, labels, meta = get_subject_data(dataset, paradigm, subject, config)
        train_mask, _ = split_by_runs(
            meta, config["training"]["train_runs"], config["training"]["test_runs"]
        )
        X_train, y_train = X[train_mask], labels[train_mask]
        label_map = {"left_hand": 0, "right_hand": 1}
        y_train = np.array([label_map[l] for l in y_train])

        cv = StratifiedKFold(n_splits=config["training"]["cv_folds"], shuffle=True, random_state=42)
        for name in ["lda", "svm"]:
            pipe = build_decoder(name, config["training"]["csp_components"])
            scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc")
            print(f" {name}: CV AUC = {scores.mean():.3f} ± {scores.std():.3f}")
            pipe.fit(X_train, y_train)
            save_decoder(pipe, f"{config['output']['models_dir']}/sub{subject}_{name}.joblib")

if __name__ == "__main__":
    main()
        