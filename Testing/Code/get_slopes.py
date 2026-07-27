import pandas as pd
from sklearn.linear_model import LinearRegression


control = pd.read_csv("./frequency_control.csv", sep=";")

# Fit where tune is about centered (2144)
# Do an individual fit for each range
for range in [0, 1, 2, 4]:
    data = control[(control["tune"] == 2144) & (control["range / 1"] == range)]
    lr = LinearRegression()
    lr.fit(data[["coarse / 1", "gain / 1"]], data["freq / Hz"])

    print(
        f"f{range}(coarse, gain) = {lr.intercept_}  {lr.coef_[0]}*coarse {lr.coef_[1]}*gain",
    )
