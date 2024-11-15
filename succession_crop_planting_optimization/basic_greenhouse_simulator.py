#this takes solcast data and the daily temperature record data and makes the unified climate .csv for a greenhouse in that climate. 
#Another tool is needed to change this greenhouse_climate.csv into the files that aquacrop expects for each simulation run 


from itertools import islice
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date, time
from datetime import timedelta
import matplotlib.dates as mdates
from pytz import timezone
import pytz
import numpy as np
import dateutil.parser
from eto import ETo, datasets
import os





class greenhouse:
    
    def __init__(self):
        self.data_path  = "" 
        self.solcast_filename = ""
        self.lon = 0 
        self.lat = 0 
        
        self.greenhouse_Tmin = 6 
        self.greenhouse_Tmax = 25 
        self.greenhouse_Hmin = 0.6 
        self.greenhouse_Hmax = 0.85 
        self.glazing_transmission = 0.8 
        self.glazing_Rimp = 1.5 
        self.greenhouse_floor_reflectance = 0.5
        self.glazing_floor_ratio = 1.5 #about right for an arch greenhouse
        
        self.df_solcast_all = pd.DataFrame()
        self.greenhouse_filename = "greenhouse_climate.csv"
        
    def load_solcast_all(self):
        df = pd.read_csv(self.data_path + self.solcast_filename, sep=',')
    
        #make a date time column
        time_period_end = df["PeriodEnd"] 
        date_list = []
        for a in range(0, len(time_period_end)):
            temp_data_sun = dateutil.parser.isoparse(time_period_end[a])
            
            timestamp = datetime.timestamp(temp_data_sun)
            dt_object = datetime.fromtimestamp(timestamp)

            datetimeunaware = dt_object

            date_list.append(dt_object)

        df["datetime"] = date_list

        df = df.set_index('datetime') 

        self.df_solcast_all = df 
    
    def daily_greenhouse_data( self , year_start , year_end):
        df = pd.read_csv(self.greenhouse_filename).set_index( "datetime")
        # ~ print(df) 
        
        start = str(year_start)+ "-01-01" 
        end = str(year_end)+ "-12-31"
        return df.loc[ start: end] 
        
    def save_daily_ET0_adjust_temperature_greenhouse( self):
        df = pd.DataFrame()
        df['T_mean'] = self.df_solcast_all['AirTemp']
        df['R_s joules per hour'] = self.glazing_transmission*self.df_solcast_all['Ghi']*60*60
        df['R_s'] = df['R_s joules per hour']/(1000000.)
        df['RH_mean'] = self.df_solcast_all['RelativeHumidity']
        df['U_z'] = self.df_solcast_all['WindSpeed10m']*0.000000000001
        df['P']= self.df_solcast_all['SurfacePressure']
        # ~ df['T_dew']= self.df_solcast_all['DewpointTemp']

        #here I will do a simple estimate of the solar heating of greenhouse 
        
        Rsi = self.glazing_Rimp/5.68
        #Q_lost = 1.0*dT/Rsi
        A = self.glazing_floor_ratio #ratio of glazing area to floor area 
        Absorb = self.greenhouse_floor_reflectance #fraction of light abrobed in greenhouse
        df["dT"]  = self.glazing_transmission*self.df_solcast_all['Ghi']*Absorb*Rsi/A
        df["T_mean_inside"] = df["T_mean"] + df["dT"]
        
        df = df[~df.index.duplicated(keep='first')]#remove duplicated data
        df = df.interpolate() #fill any data holes
        
        dfn = pd.DataFrame() #this removes any temperature below the minimum and set that to the minimum temperature
        dfn = df.clip(lower=pd.Series({'T_mean_inside': self.greenhouse_Tmin}), axis=1)
        df['T_mean_inside'] = dfn['T_mean_inside']
        
        
        dfn = pd.DataFrame() #This set and temp over the max to be the max
        dfn = df.clip(upper=pd.Series({'T_mean_inside': self.greenhouse_Tmax}), axis=1)
        df['T_mean_inside'] = dfn['T_mean_inside']
        
      
        for i in df.index:#if the out side air is above greenhouse_Tmax, then the inside air should be the same as outside air, likely we won't be able to cool greenhouse below that 
            if df['T_mean'].loc[i] > self.greenhouse_Tmax: #--- we've got 2 entries for same date sometimes and this can cause an error here.  
                #print(i)
                df['T_mean_inside'].loc[i] = df['T_mean'].loc[i]
        
        
        dfn = pd.DataFrame() #set the humidity to be within specified bounds... this isn't super accurate because the change in temperature will change humidity
        
        dfn = df.clip(lower=pd.Series({'RH_mean': self.greenhouse_Hmin}), axis=1)
        df['RH_mean'] = dfn['RH_mean']

        dfn = pd.DataFrame()
        dfn = df.clip(upper=pd.Series({'RH_mean': self.greenhouse_Hmax}), axis=1)
        df['RH_mean'] = dfn['RH_mean']
        
        

        # ~ df.plot()
        # ~ plt.show()
        # ~ quit()


        dfmean = df.copy()
        
        dfmaxD = df.resample('D').max()
        dfminD = df.resample('D').min()
        
        dfminmax = pd.DataFrame()
        dfminmax.index = dfmaxD.index
        dfminmax['Tmax'] = dfmaxD['T_mean_inside']
        dfminmax['Tmin'] = dfminD['T_mean_inside']
        
        
        # ~ dfminmax.plot()
        # ~ plt.show()
        # ~ quit()
        
        et1 = ETo()

        z_msl = 70
        TZ_lon = 0 #utc time assumed
        freq = 'H'
        et1.param_est(df, freq, z_msl, self.lat, self.lon, TZ_lon)

        # ~ print(et1.ts_param.head())
        df['ET0'] = et1.eto_fao()
        dfsumD = df.resample('D').sum()
        
        dfminmax['ET0'] = dfsumD['ET0']
        dfminmax.plot()
        # ~ plt.show()
        # ~ quit()
      
        dfminmax['Prcp(mm)'] = np.zeros(len(dfminmax.index))
        dfminmax['Day'] = pd.DatetimeIndex(dfminmax.index).day
        dfminmax['Month'] = pd.DatetimeIndex(dfminmax.index).month
        dfminmax['Year'] = pd.DatetimeIndex(dfminmax.index).year
        dfminmax['Tmax(C)'] = dfminmax['Tmax']
        dfminmax['Tmin(C)'] = dfminmax['Tmin']
        dfminmax = dfminmax[['Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0' ]]
      
        dfminmax.to_csv("greenhouse_climate.csv")


    


# ~ g = greenhouse()
# ~ g.data_path = "/home/carl/Git_Projects/AquaCropFAO/yarmouthData/"
# ~ g.solcast_filename = "43.913601_-66.070782_Solcast_PT60M.csv" 
# ~ g.lon = -66
# ~ g.lat = 43
# ~ g.load_solcast_all()
# ~ g.save_daily_ET0_adjust_temperature_greenhouse()





