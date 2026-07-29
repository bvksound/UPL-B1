import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

control = pd.read_csv("../../Documentation//frequency_control.csv", sep=";")

# Mark bad readings
for column in control.columns:
    control.loc[control[column] > 9e32] = np.nan


# Do an individual fit for each range
for range in [0, 1, 2, 4]:
    data = control[(control["range / 1"] == range)]
    lr = LinearRegression()
    lr.fit(data[["coarse / 1", "gain / 1", "tune"]], data["freq / Hz"])
    coef = lr.coef_.round(4)
    print(
        f"f{range}(coarse, gain) = {round(lr.intercept_,4)}  {coef[0]}*coarse {coef[1]}*gain {coef[2]}*tune",
    )
