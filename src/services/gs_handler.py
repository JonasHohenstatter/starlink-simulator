import pandas as pd
from pathlib import Path
import os

def load_from_config(configname):
    path = f"{Path(__file__).resolve().parents[2]}/data/GS/{configname}.csv"
    df = pd.read_csv(path)
    dict_data = df.to_dict(orient="records")
    return dict_data