import json
import pandas as pd

def save_results(results: list, json_path: str, csv_path: str):
    with open(json_path, "w") as f:
        json.dump(results, f, indent=4)

    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False)