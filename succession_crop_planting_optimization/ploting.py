

from itertools import islice
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime, date, time
from datetime import timedelta
import matplotlib.dates as mdates
from pytz import timezone
import pytz

from setup_aquacrop_input_files import *
from script_tools import *

import numpy as np
import random

import dateutil.parser



df = pd.read_csv("multi_year_yield.csv" ,index_col = "Unnamed: 0")

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

dfplot = pd.DataFrame()
dfplot['mean'] = dfm
dfplot['best'] = dfb
dfplot['worst'] = dfw

dfplot.index = pd.date_range(start="1/1/1901", end="1/1/1902"  , freq='D')
dfplot.plot()
plt.show()

df = pd.read_csv("multi_year_growing_season.csv" ,index_col = "Unnamed: 0")
print(df)
df.plot()
plt.show()









quit()









#now I want to show how much we yielded on any given date

#i want a start col, harvest date col, yield column 
df['harvest_date'] = pd.to_datetime(df[['year', 'month', 'day']])
print(df)
df_harvest = pd.DataFrame()

df_harvest['yield'] = df['yield']
df_harvest.index = df['harvest_date'] 

print(df_harvest)
# ~ df_harvest.plot(style='.')
# ~ plt.show()

dates = pd.date_range(start='1/1/2017', end=df_harvest.index[-1]+pd.Timedelta(7, "d")  , freq='D')
df_spread_harvest = pd.DataFrame()
df_spread_harvest.index = dates
df_spread_harvest['yield'] = 0
print(dates)
for day in df_harvest.index:
    #if there is a harvest this day, spread it to the next 7 days 
    print("day" , day)
    print( "harvest" , df_harvest['yield'].loc[day])
    harvest_this_day = 0
    if isinstance(df_harvest['yield'].loc[day], pd.Series):
        harvest_this_day =sum(df_harvest['yield'].loc[day])
    else: 
        harvest_this_day = (df_harvest['yield'].loc[day])
    
    if( harvest_this_day > 0 ):
        for wday  in pd.date_range(start=day, end=day+pd.Timedelta(7, "d") , freq='D'):
            df_spread_harvest.loc[wday] += harvest_this_day/7.0

# ~ #show harvest over a full year
# ~ df_spread_harvest.plot(style='-')
# ~ plt.show()


#find how much area is used for lettuce at any given day
dates = pd.date_range(start='1/1/2017', end=df_harvest.index[-1]+pd.Timedelta(7, "d")  , freq='D')
df_area = pd.DataFrame()
df_area.index = dates
df_area['area'] = 0
print(df)
for day in df.index:
    growing_period = pd.date_range(start=day, end= df['harvest_date'].loc[day])
    for daygrowing in growing_period:
        df_area['area'].loc[daygrowing] += 1 

#area use at any given date for lettuce growing
# ~ df_area.plot(style='-')
# ~ plt.show()


###ok now lets solve how much to plant on each day for constant harvest 
planting_dates = pd.date_range(start='1/1/2017', end=df_harvest.index[-1]+pd.Timedelta(7, "d")  , freq='D')
list_of_col_vec = []
for day in df_harvest.index:
    #make a column vec where each element is harvest on the day. one element in the vec per day starting at jan 1 2017, ending feb 23 2018 
    vec = np.zeros( 364)
    
    #if there is a harvest this day, spread it to the next 7 days 
    print("day" , day)
    print( "harvest" , df_harvest['yield'].loc[day])
    harvest_this_day = 0
    if isinstance(df_harvest['yield'].loc[day], pd.Series):
        harvest_this_day =sum(df_harvest['yield'].loc[day])
    else: 
        harvest_this_day = (df_harvest['yield'].loc[day])
    
    days_since_jan1 = days_since_jan1_convert( day.year , day.month, day.day)
    
    if( harvest_this_day > 0 ):
        r = 7# random.randint( 5 , 20)
        for a in range(0 , r):
            vec[ (days_since_jan1 + a)%364 ] = harvest_this_day/r
        
    list_of_col_vec.append(vec)
            
H = np.array(list_of_col_vec)
H = np.transpose(H)

dfH = pd.DataFrame(H)
dfH.to_csv("H.csv")


desired_harvest_vec = np.ones(364)
print("x")
print(np.size(H, 0)) 

print("y")
print(np.size(H, 1)) 

def Hmatrix( p):
    global H 
    return H.dot(p)
    
def cost_func( p):
    global H 
    h =  H.dot(p)
    df =  h - 50*np.ones(364)
    cost = df.dot(df) 
    print(cost)
    return cost

print( Hmatrix(np.ones(364)))
dfvec = pd.DataFrame()
dfvec['yield'] = Hmatrix(np.ones(364))
print( cost_func(np.ones(364)))
# ~ dfvec.plot(style='-')
# ~ plt.show()

from scipy.optimize import minimize, rosen, rosen_der
bnds = [(0, None) ]*364 
optimal_planting = minimize(cost_func, desired_harvest_vec, method='Nelder-Mead', bounds = bnds, tol=1e-6)
for a in range( 0 , 10):
    optimal_planting = minimize(cost_func, optimal_planting.x, method='Nelder-Mead', bounds = bnds, tol=1e-6)

print(optimal_planting.x)
dfvec = pd.DataFrame()
dfvec['yield_naive'] = Hmatrix(np.ones(364))
dfvec['yield_opt'] = Hmatrix(optimal_planting.x)
# ~ dfvec.plot(style='-')
# ~ plt.show()

dfvec = pd.DataFrame()
dfvec['planting_naive'] = (np.ones(364))
dfvec['planting_opt'] = optimal_planting.x
dfvec.to_csv("optimal_greenhouse_planting_vec.csv")

dfvec.plot(style='-')
plt.show()


###ok now lets solve how much area is used by each planting  
planting_dates = pd.date_range(start='1/1/2017', end=df_harvest.index[-1]+pd.Timedelta(7, "d")  , freq='D')
list_of_col_vec = []
for day in df_harvest.index:
    #make a column vec where each element is harvest on the day one element in the vec per day starting at jan 1 2017, ending feb 23 2018 
    vec = np.zeros( 364)
    
    days_since_jan1_when_seeding = days_since_jan1_convert( day.year , day.month, day.day)
    days_since_jan1_when_harvesting = days_since_jan1_convert( df_harvest['year'] , df_harvest['month'], df_harvest['day'])
  
    for a in range(days_since_jan1_when_seeding , days_since_jan1_when_harvesting+7):
            vec[  a%364 ] = 1
        
    list_of_col_vec.append(vec)
            
A = np.array(list_of_col_vec)
A = np.transpose(A)

#now we want to use A.dot(plantingvec) to show the year long area used 
dfvec = pd.DataFrame()
dfvec['area_naive'] = A.dot(np.ones(364))
dfvec['area_opt'] = A.dot(optimal_planting.x)
dfvec.to_csv("optimal_greenhouse_planting_area_vec.csv")

dfvec.plot(style='-')
plt.show()

