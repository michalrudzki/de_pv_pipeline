import pickle
import pandas as pd

objects = []
with (open("data/meteo_daily_Szczecin_2026-08-09.pkl", "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break

print(objects[0].columns.tolist())
pd.set_option('display.max_columns', None)
print(objects[0].head(1))