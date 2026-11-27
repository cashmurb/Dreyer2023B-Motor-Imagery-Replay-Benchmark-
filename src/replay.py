import time 
import numpy as np
import pandas as pd

class RingBuffer:
    def __init__(self, n_channels, capacity_samples):
        self.data = np.zeros((n_channels, capacity_samples))
        self.capacity = capacity_samples
        self.filled = 0 

    def push(self, chunk):
        """chunk: (n_channels, n_samples)."""
        n = chunk.shape[1]
        if n >= self.capacity:
            self.data = chunk[:, -self.capacity:]
            self.filled = self.capacity
        else:
            self.data = np.roll(self.data, -n, axis=1)
            self.data[:, -n:] = chunk
            self.filled = min(self.capacity, self.filled + n)

    def get_window(self, n_samples):
        if self.filled < n_samples:
            return None 
        return self.data[:, -n_samples:]

def replay_trials(X_test, y_test, meta_test, decoders, config, log_path):
    """
    Feed held-out trials through a sliding-window replay loop. 
    decoders: dict {name: ReplayDecoder}
    Logs one row per window per decoder. 
    """
    sfreq = 250 # Dreyer2023B sampling rate 
    win_samples = int(config["replay"]["window_seconds"]* sfreq)
    step_samples = int(config["replay"]["update_interval_seconds"]* sfreq) 
    threshold = config["replay"]["confidence_threshold"]

    LABEL_MAP = {"left_hand": 0, "right_hand": 1}
    rows = []
    for trial_idx in range(len(X_test)):
        trial = X_test[trial_idx]
        true_label = LABEL_MAP[y_test[trial_idx]]

        # Prime the buffer with the first full window 
        buf = RingBuffer(trial.shape[0], win_samples)
        buf.push(trial[:, :win_samples])

        # Then slide step_samples at a time
        for start in range(win_samples, trial.shape[1], step_samples):
            chunk = trial[:, start:start + step_samples]
            if chunk.shape[1] == 0:
                break
            buf.push(chunk)
            window = buf.get_window(win_samples)
            if window is None:
                continue 

            for name, dec in decoders.items():
                t0 = time.perf_counter()
                pred, conf = dec.predict(window) 
                latency = time.perf_counter() - t0 
                rows.append({
                    "trial": trial_idx,
                    "decoder": name, 
                    "true_label": true_label,
                    "predicted": pred,
                    "confidence": conf,
                    "above_threshold": conf >= threshold,
                    "correct": pred == true_label, 
                    "latency": latency,
                }) 
    df = pd.DataFrame(rows)
    df.to_csv(log_path, index=False)
    return df

