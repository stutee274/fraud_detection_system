import pandas as pd
import numpy as np
def log_new_transaction(df_new):
    df_new.to_csv("data/new_data.csv", mode='a', header=False, index=False)
    print("New transaction saved!")

# Example new transaction (normal)
sample = pd.DataFrame([{
    "Time": 30,
    "Amount": 12000,
    **{f"V{i}": np.random.randn() for i in range(1,29)},
    "Class": 0
}])

log_new_transaction(sample)
