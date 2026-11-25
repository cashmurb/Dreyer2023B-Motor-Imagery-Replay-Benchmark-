import numpy as np
from moabb.datasets import Dreyer2023B
from moabb.paradigms import MotorImagery

# ---- Config (inline, so no external file needed) ----
SUBJECT = 61
CHANNELS = ["C3", "C4", "Cz", "FC1", "FC2", "CP1", "CP2"]
FMIN, FMAX = 8.0, 30.0
TMIN, TMAX = 3.5, 7.5
SFREQ = 250
TRAIN_RUNS = [1, 2]
TEST_RUNS = [3, 4, 5, 6]


def crop_to_window(X, sfreq, tmin_actual, tmin_target, tmax_target):
    start = int(round((tmin_target - tmin_actual) * sfreq))
    stop = int(round((tmax_target - tmin_actual) * sfreq))
    return X[:, :, start:stop]


def split_by_runs(meta, train_runs, test_runs):
    run_num = meta["run"].astype(str).str.extract(r"R(\d+)")[0].astype(int)
    train_mask = run_num.isin(train_runs).values
    test_mask = run_num.isin(test_runs).values
    return train_mask, test_mask


# ---- Load ----
ds = Dreyer2023B(subjects=[SUBJECT])
para = MotorImagery(fmin=FMIN, fmax=FMAX, tmin=TMIN, tmax=TMAX, channels=CHANNELS)

# Get epochs object first, to learn the ACTUAL time axis
X_ep, labels, meta = para.get_data(dataset=ds, subjects=[SUBJECT], return_epochs=True)
tmin_actual = float(X_ep.times[0])
tmax_actual = float(X_ep.times[-1])
print(f"Actual epoch time axis: {tmin_actual:.3f}s to {tmax_actual:.3f}s")
print(f"Epoch shape: {X_ep.get_data().shape}")

# Get plain numpy array (same data, no MNE object)
X, labels, meta = para.get_data(dataset=ds, subjects=[SUBJECT])

# ---- Crop ----
X = crop_to_window(X, SFREQ, tmin_actual, TMIN, TMAX)

print("\n=== After crop ===")
print("X shape:", X.shape)          # expect (240, 7, 1000)
print("Labels:", set(labels))
print("Runs present:", sorted(meta["run"].astype(str).unique()))
print(meta.groupby(meta["run"].astype(str))["run"].count())

# ---- Split ----
train_mask, test_mask = split_by_runs(meta, TRAIN_RUNS, TEST_RUNS)
print("\n=== Split ===")
print("Train trials:", train_mask.sum(), "| Test trials:", test_mask.sum())
print("Train runs:", sorted(meta.loc[train_mask, "run"].astype(str).unique()))
print("Test runs: ", sorted(meta.loc[test_mask, "run"].astype(str).unique()))

# ---- Assertions (fail loudly if something is wrong) ----
assert X.shape[0] == len(labels) == len(meta), "Trial count mismatch"
assert abs(X.shape[2] - (TMAX - TMIN) * SFREQ) <= 2, f"Unexpected window length: {X.shape[2]}"
assert train_mask.sum() > 0 and test_mask.sum() > 0, "Empty split"
assert not (set(meta.loc[train_mask, "run"]) & set(meta.loc[test_mask, "run"])), "Run overlap between train and test!"

print("\nAll checks passed.")