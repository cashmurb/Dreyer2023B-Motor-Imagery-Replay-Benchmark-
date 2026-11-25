import yaml
from moabb.datasets import Dreyer2023B

if __name__ == "__main__":
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    Dreyer2023B(subjects=config["dataset"]["subjects"]).download()
    print("Download complete.")