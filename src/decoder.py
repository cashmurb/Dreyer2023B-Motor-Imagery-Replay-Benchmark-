import joblib
import numpy as np
from mne.decoding import CSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.svm import SVC 
from sklearn.pipeline import make_pipeline

def build_decoder(name, n_components):
    """Build CSP + classifier pipeline."""
    if name == "lda":
        clf = LDA()
    elif name == "svm":
        clf = SVC(kernel="linear", probability=True, class_weight="balanced", random_state=42)
    else:
        raise ValueError(f"Unknown decoder: {name}")

    return make_pipeline(CSP(n_components=n_components, reg=0.01, log=True), clf)

def save_decoder(pipe, path):
    joblib.dump(pipe, path)

def load_decoder(path):
    return joblib.load(path)


class ReplayDecoder:
    """Wraps a trained pipeline for a single-window real-time prediction."""

    def __init__(self, pipe):
        self.pipe = pipe 
    
    def predict(self, window):
        """Window: (n_channels, n_times) -> (label, configuration)."""
        X = window[np.newaxis, :,:]
        proba = self.pipe.predict_proba(X)[0]
        idx = int(np.argmax(proba))
        return self.pipe.classes_[idx], float(proba[idx])
