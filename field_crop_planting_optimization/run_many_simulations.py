#this is the main interface script file for doing a field crop simulation where there is one crop per year. 


from load_climate_data import *


class simulate_years:
    def __init__(self):
        self.climate = climate()
        # ~ self.df_climate = pd.DataFrame()
        self.crop_file = ".CRO"
        self.irrigation_file = "(None)"#'NONE' means rainfall only
        self.death_temperature = 0#assumes an anual crop that cannot survive below this temperature. 0 for frost. -2 for mildly frost hardy etc 
        self.years = []
        self.df_yield = pd.DataFrame()
        self.df_growing_days = pd.DataFrame()

    def simulate_year( self, year):
        df = self.climate.get_daily_data_for_year( year )
        
        self.df_yield[year] = np.zeros(366)
        self.df_growing_days[year] = np.zeros(366)
        
        earliest_planting_date = datetime( year , 1 ,1 )

        
        lastest_harvest_date = datetime( year , 12 ,31 )

        
        #now look at the data and find the dates above death temperature 
        #find the frost dates
        start_row = int(len(df.index)/2)

        for a in range( 0 , start_row):
            Tmin = float( df["Tmin(C)"].iloc[ start_row - a])
            if( Tmin <= self.death_temperature ):
                earliest_planting_date = datetime(year , df["Month"].iloc[ start_row - a], df["Day"].iloc[ start_row - a])
                break
        
        for a in range(  start_row , len(df.index) ):
            Tmin = float( df["Tmin(C)"].iloc[ a])
            if( Tmin <= self.death_temperature ):
                latest_harvest_date = datetime( year , df["Month"].iloc[  a] , df["Day"].iloc[  a]  )  
                break
    
        
        growing_dates = pd.date_range(start=earliest_planting_date, end=latest_harvest_date  , freq='D')
        
        
        ylist = []
        for day in growing_dates:
            print(year) 
            print(day.month )
            print(day.day )
            # ~ print( year)
            # ~ print( latest_harvest_month)
            # ~ print( latest_harvest_day )
            # ~ print(df)
    
            #run the sim for this start date
            #prepare all the basic aquacrop inputs for this year 
            yield_fresh_ton_per_ha, harvest_date , Tmax_at_start, Tmin_at_start , ndays = getSimYield( day , latest_harvest_date  ,df , self.death_temperature, self.crop_file , self.irrigation_file )
            # ~ yield_fresh_ton_per_ha, harvest_year , harvest_month , harvest_day , Tmax_at_start, Tmin_at_start , ndays = getSimYield( 2007 ,8 , 9 ,year ,latest_harvest_month ,latest_harvest_day ,df , death_temperature)
            
            #save output as csv? Nah 
            #collect the output into a yeild df where year is col, planing date is index . make another df where value is n day going for crop too.  
            harvest_day_from_jan1 = days_since_jan1_convert( harvest_date.year , harvest_date.month , harvest_date.day )
            planting_day_from_jan1 = days_since_jan1_convert( year , day.month , day.day )
            self.df_yield[year].loc[planting_day_from_jan1] = yield_fresh_ton_per_ha
            self.df_growing_days[year].loc[planting_day_from_jan1] = ndays
        
            # ~ print("yield_fresh_ton_per_ha", yield_fresh_ton_per_ha)
            print( yield_fresh_ton_per_ha, harvest_date.year , harvest_date.month , harvest_date.day , Tmax_at_start, Tmin_at_start , ndays)
            ylist.append(yield_fresh_ton_per_ha)
            
        print(ylist)

    def sim_all_years(self):
        for year in self.years:
            self.simulate_year( year)
            
        self.df_yield.to_csv("multi_year_yield.csv")
        self.df_growing_days.to_csv( "multi_year_growing_season.csv" )



c = climate()
c.list_historical_daily_files = ["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]
c.solcast_filename = "43.913601_-66.070782_Solcast_PT60M.csv" 
c.data_path= "../yarmouthData/"
c.lon = -66
c.lat = 43.9
c.load_solcast_all()
c.reformat_solcast_to_daily_add_ET0()
c.load_daily_data()
df = c.get_daily_data_for_year(2008)

s = simulate_years()
s.climate = c
s.crop_file = 'PotatoGDD.CRO'
s.years = list(range(2007, 2019, 1))
s.sim_all_years()



quit()


