#this is aquacrop setup tools



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

from setup_aquacrop_input_files import *


class climate:
    def __init__(self):
        self.data_path  = "" 
        self.solcast_filename = ""
        self.list_historical_daily_files = []
        self.lon = 0 
        self.lat = 0 
        
        
        self.df_solcast_all = pd.DataFrame()
        self.df_historical = pd.DataFrame()
        
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
    






    def reformat_solcast_to_daily_add_ET0( self ): #assumes UTC times 
        df = pd.DataFrame()
        df['T_mean'] = self.df_solcast_all['AirTemp']
        df['R_s joules per hour'] = self.df_solcast_all['Ghi']*60*60
        df['R_s'] = df['R_s joules per hour']/(1000000.)
        df['RH_mean'] = self.df_solcast_all['RelativeHumidity']
        df['U_z'] = self.df_solcast_all['WindSpeed10m']
        df['P']= self.df_solcast_all['SurfacePressure']

        dfmean = df.copy()
        
        dfmaxD = df.resample('D').max()
        dfminD = df.resample('D').min()
        
        dfminmax = pd.DataFrame()
        dfminmax.index = dfmaxD.index
        dfminmax['Tmax(C)'] = dfmaxD['T_mean']
        dfminmax['Tmin(C)'] = dfminD['T_mean']
        
        et1 = ETo()

        z_msl = 70
        # ~ lat = 43.6
        # ~ lon = -66
        TZ_lon = 0
        freq = 'H'
        et1.param_est(df, freq, z_msl, self.lat, self.lon, TZ_lon)

        # ~ print(et1.ts_param.head())
        df['ET0'] = et1.eto_fao()
        dfsumD = df.resample('D').sum()
        
        dfminmax['ET0'] = dfsumD['ET0']
        # ~ dfminmax.plot()
        # ~ plt.show()
        # ~ quit()
        self.df_solcast_all = dfminmax




    def load_daily_data( self  ):
        df_yar = pd.DataFrame()
        for a in self.list_historical_daily_files: #["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]:
            # ~ path = "/home/carl/Git_Projects/AquaCropFAO/yarmouthData/"
            filestring = a 
            dfwater = pd.read_csv(self.data_path + filestring, sep=',')
            print(a)

            dfwater['Datetime'] = pd.to_datetime(dfwater['LOCAL_DATE'])
            # ~ print(dfwater)

            dfwater['Datetime'] = dfwater['Datetime']
           

            df_yar = pd.concat([df_yar , dfwater])
            
        df_yar = df_yar.drop_duplicates(subset=['Datetime'])
        df_yar = df_yar.set_index('Datetime')
        df_yar.tz_localize('UTC')
        df_yar = df_yar.sort_index()
        df_yar = df_yar.interpolate()
        # ~ start = datetime(y, 1, 1, 0, 0, 0, 0) 
        # ~ end = datetime(y+2, 1, 1, 0, 0, 0, 0) 
        df_out = pd.DataFrame()
        self.df_historical = df_yar  #.loc[start:end]
        
        # ~ print(self.df_historical.columns)

     



    def get_daily_data_for_year(self, year ) :
        y = year
        start = datetime(y, 1, 1, 0, 0, 0, 0) 
        end = datetime(y+1, 1, 1, 0, 0, 0, 0) 
        dfeto = pd.DataFrame()
        dfeto = self.df_solcast_all.loc[start :end]
        dfwater = pd.DataFrame()
        dfwater = self.df_historical.loc[start:end]
            
        

        df = pd.DataFrame()
        df['ET0'] = dfeto['ET0']
        df['Tmin(C)'] = dfwater['MIN_TEMPERATURE']
        df['Tmax(C)'] = dfwater['MAX_TEMPERATURE']
        df['Prcp(mm)'] = dfwater['TOTAL_PRECIPITATION']
        df['Day'] = pd.DatetimeIndex(df.index).day
        df['Month'] = pd.DatetimeIndex(df.index).month
        df['Year'] = pd.DatetimeIndex(df.index).year
        df = df[['Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0' ]]

        df = df.interpolate()

        # ~ print(dfwater)
        df.to_csv("climate.csv")
        
        # ~ df.plot()
        # ~ plt.show()
        # ~ quit()
        
        
        return df

# ~ c = climate()
# ~ c.list_historical_daily_files = ["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]
# ~ c.solcast_filename = "43.913601_-66.070782_Solcast_PT60M.csv" 
# ~ c.data_path= "/home/carl/Git_Projects/AquaCropFAO/yarmouthData/"
# ~ c.lon = -66
# ~ c.lat = 43.9
# ~ c.load_solcast_all()
# ~ c.reformat_solcast_to_daily_add_ET0()
# ~ c.load_daily_data()
# ~ df = c.get_daily_data_for_year(2008)




def getSimYield( start_date , stop_date ,  df , minimum_harvest_temperature , crop_file , irrigation_file):
    
    
    
    print( " getting sim files ready for year =" , start_date) 
    make_yar_sim_setup_files( start_date.year , start_date.month , start_date.day  ,stop_date.year , stop_date.month , stop_date.day , df, crop_file , irrigation_file)
    os.system('./aquacrop')

    #now look at data 
    headerlist = [    'RunNr'   ,  'Day1'  , 'Month1'  ,  'Year1'   ,  'Rain'   ,   'ETo'    ,   'GD'   ,  'CO2'    ,  'Irri' ,  'Infilt'  , 'Runoff' ,   'Drain'  , 'Upflow'      ,  'E'   ,  'E/Ex'   ,    'Tr'   ,   'TrW'  , 'Tr/Trx'  ,  'SaltIn'  , 'SaltOut'  ,  'SaltUp' , 'SaltProf'   ,  'Cycle'  , 'SaltStr' , 'FertStr' , 'WeedStr' , 'TempStr'  , 'ExpStr'  , 'StoStr' , 'BioMass' , 'Brelative'  , 'HI'   , 'Y(dry)' , 'Y(fresh)'    ,"WPet"   ,   'Bin' ,    'Bout' ,    'DayN' ,  'MonthN' ,   'YearN' ,'file']
    #I have to give this as a huge list because the .OUT format is not consistent with how many spaces it uses for variable seperation.  
    daily_header =[  'Day','Month' , 'Year'  , 'DAP', 'Stage'  , 'WC(1.20)a'  , 'Raina'  ,   'Irri' ,  'Surf'  , 'Infilt'  , 'RO'   , 'Drain'    ,   'CR'  ,  'Zgwta'    ,   'Ex'    ,  'E'   ,  'E/Ex'   ,  'Trxa' ,      'Tra' , 'Tr/Trx',    'ETx'   ,   'ET' , 'ET/ETx'   ,   'GD'    ,   'Za'  ,  'StExp' , 'StSto' , 'StSen' ,'StSalta', 'StWeed'  , 'CC'    ,  'CCw'   ,  'StTr' , 'Kc(Tr)'   ,  'Trxb'   ,    'Trb'    ,  'TrW'  ,'Tr/Trxb'  , 'WP'  ,  'Biomass'  ,   'HI'  ,  'Y(dry)' , 'Y(fresh)' , 'Brelative'  ,  'WPet'   ,   'Bin'    , 'Bout' ,'WC(1.20)b' ,'Wr(0.40)'   , 'Zb'   ,   'Wr'  ,  'Wr(SAT)'  ,  'Wr(FC)' ,  'Wr(exp)'  , 'Wr(sto)'  , 'Wr(sen)' ,  'Wr(PWP)'   , 'SaltIn'  ,  'SaltOut' ,  'SaltUp'  , 'Salt(1.20)' , 'SaltZ'   ,  'Zc'    ,   'ECe'  ,  'ECsw'  , 'StSaltb' , 'Zgwtb'   , 'ECgw'     ,  'WC01'    ,   'WC 2'    ,   'WC 3'    ,   'WC 4'    ,   'WC 5'      , 'WC 6'     ,  'WC 7'     ,  'WC 8'      , 'WC 9'    ,  'WC10'    ,   'WC11'   ,    'WC12'   ,   'ECe01'   ,   'ECe 2'   ,   'ECe 3'   ,   'ECe 4'   ,   'ECe 5'   ,  'ECe 6'   ,   'ECe 7'   ,  'ECe 8'    ,  'ECe 9'   ,   'ECe10'   ,   'ECe11'    ,  'ECe12'   ,  'Rainb'    ,   'ETo'    ,  'Tmin'    ,  'Tavg'   ,   'Tmax'     , 'CO2']
    #these next rows are just here for debugging, i had to rename some to avoid doubles
                        # ~ Day Month     Year       DAP   Stage       WC(1.20)       Rain        Irri      Surf      Infilt       RO      Drain          CR       Zgwt            Ex       E         E/Ex        Trx             Tr     Tr/Trx      ETx         ET     ET/ETx         GD          Z        StExp     StSto     StSen    StSalt     StWeed      CC        CCw         StTr     Kc(Tr)        Trx           Tr          TrW      Tr/Trx      WP        Biomass        HI      Y(dry)     Y(fresh)     Brelative        WPet        Bin         Bout    WC(1.20)     Wr(0.40)      Z          Wr       Wr(SAT)       Wr(FC)      Wr(exp)      Wr(sto)      Wr(sen)      Wr(PWP)       SaltIn       SaltOut      SaltUp      Salt(1.20)      SaltZ       Z           ECe       ECsw      StSalt     Zgwt        ECgw          WC01          WC 2          WC 3          WC 4          WC 5          WC 6          WC 7          WC 8          WC 9         WC10          WC11          WC12         ECe01         ECe 2         ECe 3         ECe 4         ECe 5         ECe 6         ECe 7       ECe 8         ECe 9         ECe10         ECe11         ECe12        Rain           ETo          Tmin        Tavg        Tmax          CO2
                                      # ~ mm      mm       mm     mm     mm     mm       mm       mm      m        mm       mm     %        mm       mm    %        mm      mm       %  degC-day     m       %      %      %      %      %      %       %       %       -        mm       mm       mm    %     g/m2    ton/ha      %    ton/ha   ton/ha       %       kg/m3   ton/ha   ton/ha      mm       mm       m       mm        mm        mm        mm        mm        mm         mm    ton/ha    ton/ha    ton/ha    ton/ha    ton/ha     m      dS/m    dS/m      %     m      dS/m       0.05       0.15       0.25       0.35       0.45       0.55       0.65       0.75       0.85       0.95       1.05       1.15       0.05       0.15       0.25       0.35       0.45       0.55       0.65       0.75       0.85       0.95       1.05       1.15       mm        mm     degC      degC      degC       ppm
                        # ~ 1     1       2017       1      1          359.3           0.0         0.0      0.0        0.0         0.0      0.0           0.0     -9.90            0.7      0.7       97          0.0             0.0     100         0.7        0.7      97           11.5       0.30       -9         0         0        0         0          1.2       1.2          0        0.02          0.0          0.0         0.0       100       18.6       0.004         -9.9      0.000      0.000        100              0.00      0.000       0.000     359.3        119.3       0.30        89.3     150.0      90.0      65.7      52.3      35.1      30.0    0.000     0.000     0.000     0.000     0.000    0.30     0.00    0.00      0   -9.90   -9.00       29.3       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0      0.0       0.6       6.0      15.5      25.0    406.77
 


    dfout = pd.read_csv("./OUTP/yarPRMday.OUT", skiprows = 5, names= daily_header, sep="\\s+"  , index_col=None )
    dfout.to_csv("temp2.csv")
    
    
    
    
    # ~ print("dfout" )
    # ~ print( dfout)
    # ~ dfout = dfout.iloc[1:, :] #drop row with units 
    dfout["DAP"] = pd.to_numeric(dfout["DAP"])
    
    #get rid of rows when it was too cold
    cold_index = -999 
    for a in range( 0 , len(dfout.index)):
        if( dfout['Tmin'].loc[a] < minimum_harvest_temperature):
            cold_index = a 
            break

    #if there are no days left just stop there and return placeholder values
    if ( cold_index) <= 1:
        return -1, start_date , -999, -999, -1
    
    #find the date when crop is mature
    cropendindex = dfout['DAP'].idxmax()
    if cold_index < cropendindex:
        cropendindex = cold_index
    ndays = dfout["DAP"].loc[cropendindex]
    cropstartindex = dfout.index[0]
    # ~ print(cropstartindex)
    
    yield_fresh_per_ha = (dfout['Y(fresh)'].loc[cropendindex])
    # ~ print(yield_fresh_per_ha)
    harvest_year = int(dfout['Year'].loc[cropendindex])
    harvest_month = int(dfout['Month'].loc[cropendindex])
    harvest_day = int(dfout['Day'].loc[cropendindex])
    harvest_date = datetime( harvest_year, harvest_month , harvest_day)
    

    #collect some weather stats
    Tmax_at_start = float(dfout['Tmax'].loc[cropstartindex])
    Tmin_at_start = float(dfout['Tmin'].loc[cropstartindex])
    
    # ~ dfout.to_csv("temp.csv")
    
    return yield_fresh_per_ha, harvest_date , Tmax_at_start, Tmin_at_start, ndays

