

from itertools import islice
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime, date, time
from datetime import timedelta
import matplotlib.dates as mdates
from pytz import timezone
import pytz


import numpy as np
import random

import dateutil.parser



df = pd.read_csv("multi_year_yield.csv" ,index_col = "Unnamed: 0")
df[df < 0] = np.nan
df = df.interpolate()

df['worst'] = df.min(axis=1)
dfw = df['worst']
df = df.drop('worst', axis=1)

df['best'] = df.max(axis=1)
dfb = df['best']
df = df.drop('best', axis=1)



df['mean'] = df.mean(axis=1)
dfm = df['mean']
df = df.drop('mean', axis=1)

print(dfm)

dfplot = pd.DataFrame( )
dfplot['mean'] = dfm
dfplot['best'] = dfb
dfplot['worst'] = dfw

dfplot.index = pd.date_range(start="1/1/1901", end="1/1/1902"  , freq='D')
dfplot.plot(title="Yield vs planting date for mean of all years. \n Worst is lowest yeild on that day of any year. \n Best is hieghts yeild on that day of any year")
plt.show()

df = pd.read_csv("multi_year_growing_season.csv" ,index_col = "Unnamed: 0")
df.index = pd.date_range(start="1/1/1901", end="1/1/1902"  , freq='D')
df[df < 0] = np.nan
df = df.interpolate()
print(df)
df.plot()
plt.show()









quit()







