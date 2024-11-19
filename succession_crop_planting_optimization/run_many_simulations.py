#this is the main interface script file for doing a buch for sucessive plantings per year. 


from run_one_aquacrop_sim import *
from basic_greenhouse_simulator import *
from setup_aquacrop_input_files import *
from scipy.optimize import minimize, rosen, rosen_der






class multi_sim_optimizer:
    
    def __init__(self):
        self.crop_file  = ".CRO" #this is in the DATA drectory
        self.death_temperature = 0 #this is extra info on the crop, can it stand frost? what temperature kills it? aquacrop doesn't take this into account
        self.irrigation_file = ".IRR" #this is in the DATA drectory
        self.planting_frequency_days = 2 #how often are we planting
        self.df_climate = pd.DataFrame() #this is the greenhouse_climate.csv or similar
        self.planting_start_datetime = datetime( 1901 , 1 ,1 )
        self.planting_stop_datetime = datetime( 1902 , 1 ,1 )
        self.planting_date_key =[]
        self.harvest_averaging_days = 7 #I only care about harvest per week, day resolution isn't important, esp if selling at a weekly farmers market 
        self.harvesting_date_key = []
        self.df_sims_summary = pd.DataFrame()  #row of info for each simulation
        self.planting_areas_solution_vec = []
        
        self.harvest_target = np.ones( 10)
        
        self.H = np.zeros(10  )#this is for vectorized evaluation of planting areas into harvests 
        self.C = np.zeros(10 )#this is for vectorized conversion of planting dates into harvests dates
        
        self.planting_areas_file_name = "optimal_planting_dates_areas.csv"
        self.harvest_projection_file_name = "optimal_harvest_amounts.csv"
        
    def sim_year_of_plantings(self):
        
        planting_dates = pd.date_range(start= self.planting_start_datetime, end=self.planting_stop_datetime  , freq=str(self.planting_frequency_days)+'D')
        self.planting_date_key = planting_dates
        df_sim_output = pd.DataFrame( columns=['planting_date','harvest_date','yield_fresh_ton_per_ha','Tmax_at_planting','Tmin_at_planting','growing_days' ])
        
        for pday in planting_dates:
            
            yield_fresh_ton_per_ha, harvest_datetime , Tmax_at_planting, Tmin_at_planting , ndays = getSimYield( pday , datetime(pday.year+1, 6 , 6) ,self.df_climate , self.death_temperature ,  self.crop_file, self.irrigation_file)
            df_sim_output.loc[pday] = [ pday , harvest_datetime , yield_fresh_ton_per_ha , Tmax_at_planting, Tmin_at_planting , ndays] 

        self.df_sims_summary =  df_sim_output  
        
    def optimize_for_constant_harvest(self):
        self.setup_vectors()
        self.make_H_matrix()
        planting_areas_initial = np.ones( len(self.planting_date_key)) 
        first_harvest_date  = self.df_sims_summary['harvest_date'].iloc[0]
        first_harvest_gindex  = self.find_harvesting_vector_index_from_date( first_harvest_date ) 
        self.harvest_target = 30*np.ones( len(self.harvesting_date_key)) 

        for b in range( 0 , len(self.harvesting_date_key)):
            if( b < first_harvest_gindex):
                self.harvest_target[b]  = 0
                
        print( self.harvest_target) 
        
           
        bnds = [(0, None) ]*len(planting_areas_initial)
        for a in range(0 , len(bnds)):
            if self.planting_date_key[a] > self.df_sims_summary['planting_date'].iloc[-1] : 
                bnds[a] = (0,0)

   
        optimal_planting = minimize(self.cost_func, planting_areas_initial, method='Nelder-Mead', bounds = bnds, tol=1e-6)
        for a in range( 0 , 10):
            optimal_planting = minimize(self.cost_func, optimal_planting.x, method='Nelder-Mead', bounds = bnds, tol=1e-6)

        planting_areas_initial = optimal_planting.x
        print(planting_areas_initial)
        self.planting_areas_solution_vec = planting_areas_initial
        yvec = self.H.dot(self.planting_areas_solution_vec)
        print("yvec")
        print(yvec)
        
        gyvec = self.C.dot(yvec)
        print( "grouped harvest vector" , gyvec)
        
        df_planting_plan = pd.DataFrame()
        df_planting_plan.index = self.planting_date_key 
        df_planting_plan['planting_optimized_areas_ha'] = planting_areas_initial
        df_planting_plan.to_csv(self.planting_areas_file_name)
        
        df_harvest_projection = pd.DataFrame()
        df_harvest_projection.index = self.harvesting_date_key 
        df_harvest_projection['harvest_tones'] = gyvec
        df_harvest_projection.to_csv(self.harvest_projection_file_name)
        
        
        
    def setup_vectors(self):
        #what's the first possible harvest
        first_harvest_dt = self.df_sims_summary['harvest_date'].iloc[0] 
        last_harvest_dt = self.df_sims_summary['harvest_date'].iloc[-1]
        #here's a list of harvest periods 
        self.harvesting_date_key = pd.date_range(start= self.planting_start_datetime, end=last_harvest_dt  , freq=str(self.harvest_averaging_days)+'D')
        self.planting_date_key = pd.date_range(start= self.planting_start_datetime, end=last_harvest_dt  , freq=str(self.planting_frequency_days)+'D')
        
    
    def find_planting_vector_index_from_date(self , date):
         for b in range( 0 , len(self.planting_date_key)):
             if (self.planting_date_key[b] >= date ):
                return b 
                
    def find_harvesting_vector_index_from_date(self , date):
         for b in range( 0 , len(self.harvesting_date_key)):
             if (self.harvesting_date_key[b] >= date ):
                return b 
        
    def make_H_matrix(self ):
        M = np.zeros( (len(self.planting_date_key), len(self.planting_date_key) )  )
        for a in range( 0 , len(self.planting_date_key)): #a is the planting start date
            #b is the harvest date, converted to planting vector index
            if( a < len(self.df_sims_summary.index)):
                b = self.find_planting_vector_index_from_date( self.df_sims_summary['harvest_date'].iloc[a] )
                Y = self.df_sims_summary['yield_fresh_ton_per_ha'].iloc[a]
                # ~ print(Y , b , a )
                M[b,a]= Y 
            
      
        self.H = M

        self.C = np.zeros( (len(self.harvesting_date_key), len(self.planting_date_key) )  )
        #each column of C has a 1 in the row that is it's yield output
        for a in range( 0 , len(self.planting_date_key)): #a is the planting start date
            b = self.find_harvesting_vector_index_from_date( self.planting_date_key[a] )
            #b is the planting date, but in the harvesting vector index notation
            self.C[b,a] = 1 
    
    
    def get_harvest_vec_from_planting_vec(self , planting_area_vec ):
        yvec = self.H.dot(planting_area_vec)
        gyvec = self.C.dot(yvec)
        return gyvec
        
    def cost_func( self , planting_areas_vector):
    
       
        gyvec = self.get_harvest_vec_from_planting_vec(planting_areas_vector)
       
        cost = sum( abs(gyvec - self.harvest_target )  )
        print(cost)
        return cost


#make a greenhouse climate file

g = greenhouse()
g.data_path = "../yarmouthData/"
g.solcast_filename = "43.913601_-66.070782_Solcast_PT60M.csv" 
g.lon = -66
g.lat = 43
g.load_solcast_all()
g.save_daily_ET0_adjust_temperature_greenhouse()


dff = g.daily_greenhouse_data( 2007 , 2019)
print(dff)

#setup multi runs

m = multi_sim_optimizer()
m.crop_file = 'saladbowl3.CRO'

m.death_temperature = 0 
m.irrigation_file  = 'saladbowl.IRR' #'NONE' means rainfall only
m.df_climate = dff
m.planting_start_datetime = datetime( 2007 , 1 ,1 )
m.planting_stop_datetime = datetime( 2007 , 12 ,31 )

m.sim_year_of_plantings()
m.optimize_for_constant_harvest()


quit()



