import moabb 
import numpy as np 
from moabb.datasets import Dreyer2023B
from moabb.paradigms import MotorImagery

moabb.set_log_level('info')

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

def get_subject_data(dataset, paradigm, subject):
    """Return X, labels, meta for one subject."""
    X, labels, meta = paradigm.get_data(dataset=dataset, subjects=[subject])
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