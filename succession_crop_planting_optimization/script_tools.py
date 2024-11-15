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


atlantic = timezone('Canada/Atlantic')
utc = timezone('UTC')


##all times are in local time (UTC-4 or UTC-3 DST for NS)
##load the solcast data file 




def getSimYield( year , month , day , yearend , monthend , dayend,  df , minimum_harvest_temperature  , irrigation_file):
    
    
    
    print( " getting sim files ready for year =" , year , "month = " , month, "day = " , day) 
    make_yar_sim_setup_files( year ,month , day ,yearend , monthend  ,dayend , df , irrigation_file)
    os.system('./aquacrop')

    #now look at data 
    headerlist = [    'RunNr'   ,  'Day1'  , 'Month1'  ,  'Year1'   ,  'Rain'   ,   'ETo'    ,   'GD'   ,  'CO2'    ,  'Irri' ,  'Infilt'  , 'Runoff' ,   'Drain'  , 'Upflow'      ,  'E'   ,  'E/Ex'   ,    'Tr'   ,   'TrW'  , 'Tr/Trx'  ,  'SaltIn'  , 'SaltOut'  ,  'SaltUp' , 'SaltProf'   ,  'Cycle'  , 'SaltStr' , 'FertStr' , 'WeedStr' , 'TempStr'  , 'ExpStr'  , 'StoStr' , 'BioMass' , 'Brelative'  , 'HI'   , 'Y(dry)' , 'Y(fresh)'    ,"WPet"   ,   'Bin' ,    'Bout' ,    'DayN' ,  'MonthN' ,   'YearN' ,'file']
    #I have to give this as a huge list because the .OUT format is not consistent with how many spaces it uses for variable seperation.  
    daily_header =[  'Day','Month' , 'Year'  , 'DAP', 'Stage'  , 'WC(1.20)a'  , 'Raina'  ,   'Irri' ,  'Surf'  , 'Infilt'  , 'RO'   , 'Drain'    ,   'CR'  ,  'Zgwta'    ,   'Ex'    ,  'E'   ,  'E/Ex'   ,  'Trxa' ,      'Tra' , 'Tr/Trx',    'ETx'   ,   'ET' , 'ET/ETx'   ,   'GD'    ,   'Za'  ,  'StExp' , 'StSto' , 'StSen' ,'StSalta', 'StWeed'  , 'CC'    ,  'CCw'   ,  'StTr' , 'Kc(Tr)'   ,  'Trxb'   ,    'Trb'    ,  'TrW'  ,'Tr/Trxb'  , 'WP'  ,  'Biomass'  ,   'HI'  ,  'Y(dry)' , 'Y(fresh)' , 'Brelative'  ,  'WPet'   ,   'Bin'    , 'Bout' ,'WC(1.20)b' ,'Wr(0.40)'   , 'Zb'   ,   'Wr'  ,  'Wr(SAT)'  ,  'Wr(FC)' ,  'Wr(exp)'  , 'Wr(sto)'  , 'Wr(sen)' ,  'Wr(PWP)'   , 'SaltIn'  ,  'SaltOut' ,  'SaltUp'  , 'Salt(1.20)' , 'SaltZ'   ,  'Zc'    ,   'ECe'  ,  'ECsw'  , 'StSaltb' , 'Zgwtb'   , 'ECgw'     ,  'WC01'    ,   'WC 2'    ,   'WC 3'    ,   'WC 4'    ,   'WC 5'      , 'WC 6'     ,  'WC 7'     ,  'WC 8'      , 'WC 9'    ,  'WC10'    ,   'WC11'   ,    'WC12'   ,   'ECe01'   ,   'ECe 2'   ,   'ECe 3'   ,   'ECe 4'   ,   'ECe 5'   ,  'ECe 6'   ,   'ECe 7'   ,  'ECe 8'    ,  'ECe 9'   ,   'ECe10'   ,   'ECe11'    ,  'ECe12'   ,  'Rainb'    ,   'ETo'    ,  'Tmin'    ,  'Tavg'   ,   'Tmax'     , 'CO2']
    #these next rows are just here for debugging, i had to rename some to avoid doubles
                        # ~ Day Month     Year       DAP   Stage       WC(1.20)       Rain        Irri      Surf      Infilt       RO      Drain          CR       Zgwt            Ex       E         E/Ex        Trx             Tr     Tr/Trx      ETx         ET     ET/ETx         GD          Z        StExp     StSto     StSen    StSalt     StWeed      CC        CCw         StTr     Kc(Tr)        Trx           Tr          TrW      Tr/Trx      WP        Biomass        HI      Y(dry)     Y(fresh)     Brelative        WPet        Bin         Bout    WC(1.20)     Wr(0.40)      Z          Wr       Wr(SAT)       Wr(FC)      Wr(exp)      Wr(sto)      Wr(sen)      Wr(PWP)       SaltIn       SaltOut      SaltUp      Salt(1.20)      SaltZ       Z           ECe       ECsw      StSalt     Zgwt        ECgw          WC01          WC 2          WC 3          WC 4          WC 5          WC 6          WC 7          WC 8          WC 9         WC10          WC11          WC12         ECe01         ECe 2         ECe 3         ECe 4         ECe 5         ECe 6         ECe 7       ECe 8         ECe 9         ECe10         ECe11         ECe12        Rain           ETo          Tmin        Tavg        Tmax          CO2
                                      # ~ mm      mm       mm     mm     mm     mm       mm       mm      m        mm       mm     %        mm       mm    %        mm      mm       %  degC-day     m       %      %      %      %      %      %       %       %       -        mm       mm       mm    %     g/m2    ton/ha      %    ton/ha   ton/ha       %       kg/m3   ton/ha   ton/ha      mm       mm       m       mm        mm        mm        mm        mm        mm         mm    ton/ha    ton/ha    ton/ha    ton/ha    ton/ha     m      dS/m    dS/m      %     m      dS/m       0.05       0.15       0.25       0.35       0.45       0.55       0.65       0.75       0.85       0.95       1.05       1.15       0.05       0.15       0.25       0.35       0.45       0.55       0.65       0.75       0.85       0.95       1.05       1.15       mm        mm     degC      degC      degC       ppm
                        # ~ 1     1       2017       1      1          359.3           0.0         0.0      0.0        0.0         0.0      0.0           0.0     -9.90            0.7      0.7       97          0.0             0.0     100         0.7        0.7      97           11.5       0.30       -9         0         0        0         0          1.2       1.2          0        0.02          0.0          0.0         0.0       100       18.6       0.004         -9.9      0.000      0.000        100              0.00      0.000       0.000     359.3        119.3       0.30        89.3     150.0      90.0      65.7      52.3      35.1      30.0    0.000     0.000     0.000     0.000     0.000    0.30     0.00    0.00      0   -9.90   -9.00       29.3       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0      0.0       0.6       6.0      15.5      25.0    406.77
 


    dfout = pd.read_csv("./OUTP/yarPRMday.OUT", skiprows = 5, names= daily_header, sep="\s+"  , index_col=None )
    dfout.to_csv("temp2.csv")
    
    
    
    
    # ~ print("dfout" )
    # ~ print( dfout)
    # ~ dfout = dfout.iloc[1:, :] #drop row with units 
    dfout["DAP"] = pd.to_numeric(dfout["DAP"])
    
    
    #find the date when crop is mature
    cropendindex = dfout['DAP'].idxmax()
    ndays = dfout["DAP"].loc[cropendindex]
    cropstartindex = dfout.index[0]
    # ~ print(cropstartindex)
    
    yield_fresh_per_ha = (dfout['Y(fresh)'].loc[cropendindex])
    # ~ print(yield_fresh_per_ha)
    harvest_year = int(dfout['Year'].loc[cropendindex])
    harvest_month = int(dfout['Month'].loc[cropendindex])
    harvest_day = int(dfout['Day'].loc[cropendindex])
    
    

    #collect some weather stats
    Tmax_at_start = float(dfout['Tmax'].loc[cropstartindex])
    Tmin_at_start = float(dfout['Tmin'].loc[cropstartindex])
    
    # ~ dfout.to_csv("temp.csv")
    
    return yield_fresh_per_ha, harvest_year , harvest_month , harvest_day , Tmax_at_start, Tmin_at_start, ndays

