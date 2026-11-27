import moabb 
import numpy as np 
from moabb.datasets import Dreyer2023B
from moabb.paradigms import MotorImagery

moabb.set_log_level('info')

def apply_car(X):
    """
    Apply common average reference to X. 
    X shape: (n_trials, n_channels, n_times)
    """
    return X - X.mean(axis=1, keepdims=True)

def reject_bad_epochs(X, labels, meta, threshold=100.0):
    """
    Reject epochs where any channel exceeds a peak-to-peak amplitude threshold.
    """

    # Calculate peak-to-peak amplitude for each channel in each trial.
    ptp = np.ptp(X, axis=2) 

    # Trial -> good if all its channels are below threshold.
    good_mask = np.all(ptp < threshold, axis=1)

    n_rejected =(~good_mask).sum()
    if n_rejected > 0:
        print(f" [Preprocessing] Rejected {n_rejected} noisy trials (>{threshold}uV)")
    return X[good_mask], labels[good_mask], meta[good_mask]

def load_paradigm(config):
    p = config["paradigm"]
    return MotorImagery(
        fmin=p["fmin"],
        fmax=p["fmax"],
        tmin=p["tmin"],
        tmax=p["tmax"],
        channels=config["dataset"]["channels"],
    )

def load_dataset(config):
    return Dreyer2023B(subjects=config["dataset"]["subjects"])

def get_subject_data(dataset, paradigm, subject, config):
    """Return X, labels, meta for one subject."""
    X, labels, meta = paradigm.get_data(dataset=dataset, subjects=[subject])

    # 1. Crop to the specific time window (3.5s - 7.5s)
    sfreq = 250 
    tmin_actual = float(config["paradigm"]["tmin"])
    start = int(round((config["paradigm"]["tmin"] - tmin_actual) * sfreq))
    stop = int(round((config["paradigm"]["tmax"] - tmin_actual) * sfreq))
    X = X[:, :, start:stop]

    # 2. Apply common average reference 
    X = apply_car(X)

    # 3. Reject bad epochs 
    X, labels, meta = reject_bad_epochs(X, labels, meta, threshold=100.0)

    return X, labels, meta

def split_by_runs(meta, train_runs, test_runs):
    """Boolean masks for train/test based on run ID."""
    run_col = meta["run"].astype(str).str.extract(r"R(\d+)")[0].astype(int)
    train_mask = run_col.isin(train_runs).values
    test_mask = run_col.isin(test_runs).values
    return train_mask, test_mask

def crop_to_window(x, sfreq, tmin_actual, tmin_target, tmax_target):
    """
    X: (n_trials, n_channels, n_times) as returned by MOABB (uncropped)
    sfreq: sampling rate (Dreyer2023 = 250 Hz)
    tmin_actual: the actual start time of the returned epoch 
    tmin_target, tmax_target: the desired start and end times of the cropped epoch
    """
    start = int(round((tmin_target - tmin_actual) * sfreq))
    stop = int(round((tmax_target - tmin_actual) * sfreq))
    return x[:, :, start:stop]