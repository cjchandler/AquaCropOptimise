#this is the main interface script file for doing a buch for sucessive plantings per year. 


from script_tools import *
from basic_greenhouse_simulator import *
from setup_aquacrop_input_files import *


#make a greenhouse climate file
data_path = "/home/carl/Git_Projects/AquaCropFAO/yarmouthData/"
solcast_pathfile = data_path  +"43.913601_-66.070782_Solcast_PT60M.csv" 
canada_historial_daily_files = ["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]
lon = -66
lat = 43.9
df_solcast = load_solcast_all( solcast_pathfile)
df_greenhouse = make_daily_ET0_adjust_temperature_yarmouth_greenhouse( df_solcast , lat , lon ,6 , 0.8, 0.6 , 0.85)
df_greenhouse.to_csv("greenhouse_climate.csv")


dff = get_daily_greenhouse_data_for_years( 2007 , 2008 , "greenhouse_climate.csv")
print(dff)





#get setup parameters for running aquacrop
cropfile = 'saladbowl3.CRO'
death_temperature = 0 #assumes an anual crop that cannot survive below this temperature. 0 for frost. -2 for mildly frost hardy etc 
irrigation_file = 'saladbowl.IRR' #'NONE' means rainfall only
lon = -66
lat = 43.9
planting_frequency = 3 


#run a simulation of crop growth for a full year, planting every n days. 
def simulate_year_of_plantings(planting_year, death_temperature):
    df_climate = get_daily_greenhouse_data_for_years( planting_year , planting_year+1 , "greenhouse_climate.csv")
    print(df_climate)
    first_planting_date = str(1) + '/' + str(1) + '/' + str(planting_year)  
    last_planting_date = str(12) + '/' + str(31) + '/' + str(planting_year)
      

        
    planting_dates = pd.date_range(start=first_planting_date, end=last_planting_date  , freq=str(planting_frequency)+'D')
    df_sim_output = pd.DataFrame( columns=['planting_date','harvest_date','yield_fresh_ton_per_ha','Tmax_at_planting','Tmin_at_planting','growing_days' ])

    for pday in planting_dates:
        make_yar_sim_setup_files( planting_year ,pday.month , pday.day ,planting_year+1 ,12 ,31 ,df_climate , irrigation_file )
        
        # ~ print( planting_year ,pday.month , pday.day ,planting_year+1 ,12 ,31  , death_temperature , irrigation_file)
        yield_fresh_ton_per_ha, harvest_year , harvest_month , harvest_day , Tmax_at_planting, Tmin_at_planting , ndays = getSimYield( planting_year ,pday.month , pday.day ,planting_year+1 ,9 ,28 ,df_climate , death_temperature , irrigation_file)
        harvest_date = str(harvest_year)+ "-" +str(harvest_month).zfill(2) + '-' + str(harvest_day).zfill(2)   
        df_sim_output.loc[pday] = [ pday , harvest_date , yield_fresh_ton_per_ha , Tmax_at_planting, Tmin_at_planting , ndays] 

    return df_sim_output

# ~ df_sim_output = simulate_year_of_plantings(2007, 0 )
# ~ print(df_sim_output)
# ~ df_sim_output.to_csv("2007test.csv")

df_yields = pd.read_csv( "2007test.csv").set_index('Unnamed: 0')
df_yields['harvest_date'] = pd.to_datetime(df_yields['harvest_date']) 
print(df_yields)


#ok, so if we want to plan the proper planting ammounts and intervals, we need to make a vector of dates, with a key 
vector_dates_key =  pd.date_range(start=df_yields['planting_date'].iloc[0] , end=df_yields['harvest_date'].iloc[-1]  ,freq=str(planting_frequency)+'D')
vector_len  = len(vector_dates_key)
vector_pandas_dates_key = pd.to_datetime(vector_dates_key)

#this is a function that gives yield vector for a given planting area vector:
def sim_year( df_yields, planting_area_vec ):
    yield_vec = np.zeros(len(planting_area_vec))
    for a in range( 0 , len(df_yields.index)):
        Y = planting_area_vec[a]*df_yields['yield_fresh_ton_per_ha'].iloc[a]
        #now where does that belong in the yeild vec?
        for b in range( 0 , vector_len):
            if( vector_pandas_dates_key[b] >= df_yields['harvest_date'].iloc[a] ):
                yield_vec[b] += Y
                break 
        
    return yield_vec 
    
single_planting = np.ones(vector_len)
single_planting[0] = 1     
single_yield = sim_year( df_yields, single_planting)
print(single_yield)
    
#ok, that sim year does work... but I imagine it's slow with those loops. 

#make a matrix 
def make_yield_matrix(df_yields):
    list_of_cols = []
    for a in range( 0 , vector_len):
        planting_area_vec = np.zeros((vector_len))
        planting_area_vec[a] = 1
        list_of_cols.append( sim_year( df_yields, planting_area_vec ))
            
    Y = np.column_stack(list_of_cols)
    return Y 
    
# ~ Y = make_yield_matrix(df_yields)
# ~ print(Y)
# ~ dfY = pd.DataFrame(Y)
# ~ dfY.to_csv("Ymatrix.csv", header=False, index=False)

dfYmat = pd.read_csv("Ymatrix.csv", header=None, index_col=False)
Y = dfYmat.to_numpy()
print(dfYmat)

#this is same as sim year, only it's fast 
def vectorized_sim( planting_areas_vector):
    return Y.dot(planting_areas_vector)

#group harvests by time interval, say 1 week. 
group_days = 7 
vector_harvest_group_key =  pd.date_range(start=df_yields['planting_date'].iloc[0] , end=df_yields['harvest_date'].iloc[-1]  ,freq=str(group_days)+'D')
vector_pandas_harvest_key = pd.to_datetime(vector_harvest_group_key)

def convert_harvest_vector_to_grouped( harvest_vector):
    yield_grouped_vec  = np.zeros(len(vector_pandas_harvest_key)) 
    for a in range( 0 , len(harvest_vector)):
        #now where does that belong in the grouped harvest vec?
        for b in range( 0 , len(yield_grouped_vec) ):
            if( vector_pandas_harvest_key[b] >= vector_pandas_dates_key[a] ):
                yield_grouped_vec[b] += harvest_vector[a]
                break 
    return yield_grouped_vec

def make_grouping_harvest_matrix():
    list_of_cols = []
    for a in range( 0 , vector_len):
        harvest_vec = np.zeros((vector_len))
        harvest_vec[a] = 1
        list_of_cols.append( convert_harvest_vector_to_grouped(harvest_vec ))
            
    C = np.column_stack(list_of_cols)
    return C 

# ~ C = make_grouping_harvest_matrix()
# ~ dfC = pd.DataFrame(C)
# ~ dfC.to_csv("Cmatrix.csv", header=False, index=False)

dfCmat = pd.read_csv("Cmatrix.csv", header=None, index_col=False)
C = dfCmat.to_numpy()

def cost_func( planting_areas_vector):
    
    yvec = Y.dot(planting_areas_vector)
    gyvec = C.dot(yvec)
    #now I need to look at only the last year part of it, so 
    groups_to_consider  = int( 365/group_days)
    initial_groups_to_discard = len(gyvec) - groups_to_consider
    gyvec_year = gyvec[initial_groups_to_discard:-1]
    std = gyvec_year.std()
    cost = abs(gyvec_year.mean() - 1)  + std + abs(sum(gyvec[0:initial_groups_to_discard]))
    print(cost)
    return cost

print( "cost" , cost_func(single_planting))
    
from scipy.optimize import minimize, rosen, rosen_der
bnds = [(0, None) ]*len(single_planting)
optimal_planting = minimize(cost_func, single_planting, method='Nelder-Mead', bounds = bnds, tol=1e-6)
for a in range( 0 , 10):
    optimal_planting = minimize(cost_func, optimal_planting.x, method='Nelder-Mead', bounds = bnds, tol=1e-6)

print(optimal_planting.x)
planting_solution = optimal_planting.x 
yvec = Y.dot(planting_solution)
gyvec = C.dot(yvec)
print( "grouped harvest vector" , gyvec)

# ~ for a in range( 0 , 10):
    # ~ optimal_planting = minimize(cost_func, optimal_planting.x, method='Nelder-Mead', bounds = bnds, tol=1e-6)




