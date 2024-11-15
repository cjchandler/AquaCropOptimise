#tools to setup an aquacrop sim. Nothing to run here. these tools are used to make the files that aquacrop expects before running.  

from datetime import datetime, date, time
from datetime import timedelta



def save_file( lines, filename):
    f = open(filename, "w")
    for l in lines:
        f.write(l)
        f.write("\n")
    f.close()

def convert_value_to_str_with_colon(number, p , d):
    pos_spaces = p
    decimal_spaces = d 
    
    strnum = str(number) 
    if '.' in strnum:
        num,dec = strnum.split(".") 
        #pad it. 
        n = len(num)
        d = len(dec)
        out = " "*(pos_spaces - n) + num + "." + dec + (decimal_spaces-d)*" " + ":"
        
    else:
        #pad it. 
        n = len(strnum)
        out = " "*(pos_spaces - n) + strnum + " " + decimal_spaces*" " + ":"
    
    
    return out
    
def days_since_1901_convert( y , m , d ):
    out = y - 1901 
    out = out*365.25
    month_days = [ 0 , 31  , 59.25 , 90.25 , 120.25 , 151.25 , 181.25 , 212.25 , 243.25 , 273.25 , 304.25 , 334.25 ]
    out = out + month_days[m-1]
    out = out + d 
    return int(out) 
    
def days_since_jan1_convert( y , m , d ):
    month_days = [ 0 , 31  , 59.25 , 90.25 , 120.25 , 151.25 , 181.25 , 212.25 , 243.25 , 273.25 , 304.25 , 334.25 ]
    out =  month_days[m-1]
    out = out + d 
    return int(out) 
  


def make_yar_sim_setup_files( year_s ,month_s , day_s ,year_e ,month_e ,day_e ,df_aquain , crop_file, irrigation_file ):
    #aquacrop represents day as days since jan 1 901, so 
    # ~ assert( year_s == year_e)

    sim_datetime_start  = datetime(year_s, month_s, day_s, 0, 0, 0, 0)
    sim_datetime_year_jan1  = datetime(year_s, 1, 1, 0, 0, 0, 0)
    sim_datetime_end  = datetime(year_e, month_e, day_e, 0, 0, 0, 0)
    sim_datetime_1901  = datetime(1901, 1, 1, 0, 0, 0, 0)
    deltastart = sim_datetime_start - sim_datetime_1901
    deltaend = sim_datetime_end - sim_datetime_1901
    sim_start_days_into_year = days_since_jan1_convert(year_s, month_s, day_s) #number of days since jan 1 on the year in question
    # ~ print( "sim_start_days_into_year" , sim_start_days_into_year)
    # ~ print( days_since_jan1_convert(year_s, 1, 1))
    # ~ print( days_since_jan1_convert(year_s, 2, 1))
    # ~ print( days_since_jan1_convert(year_s, 3, 1))
    # ~ print( days_since_jan1_convert(year_s, 4, 1))
    # ~ print( days_since_jan1_convert(year_s, 5, 1))
    # ~ df_aquain = df_aquain.loc[sim_datetime_year_jan1 :sim_datetime_end]
    # ~ print(df_aquain)
    #now load local weather data, put it in a dataframe
    # ~ df_aquain = get_daily_data_for_year( year_s )


    #first file is a list of other files:
    l = [None]*6
    l[0]= "Yarmouth, NS, CANADA"
    l[1]= " 7.1   : AquaCrop Version (oct 2024)"
    l[2] = "yar.Tnx"
    l[3]= "yar.ETo"
    l[4] = "yar.PLU"
    l[5] = "MaunaLoa.CO2"
 
 
    save_file( l , "./DATA/yar.CLI")

    ##I need to make file for: daily high and low temps  .Tnx 
    l = [None]*7
    l[0] = "yarmouth daily highs and lows temperature"
    l[1] = "     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)"
    l[2] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First day of record (1, 11 or 21 for 10-day or 1 for months)"
    l[3] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First month of record"
    l[4] = convert_value_to_str_with_colon( year_s , 6 , 1) + "First year of record (1901 if not linked to a specific year)"
    l[5] = "  Tmin (C)   TMax (C)"
    l[6]= "======================="

    for a in range( 0 , len(df_aquain.index)):
        l.append( str( df_aquain["Tmin(C)"].iloc[a] ) + " " + str(df_aquain["Tmax(C)"].iloc[a]) )


    save_file( l , "./DATA/yar.Tnx")

    #I need to make file for ETo
    l = [None]*7
    l[0] = "yarmouth daily ETo"
    l[1] = "     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)"
    l[2] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First day of record (1, 11 or 21 for 10-day or 1 for months)"
    l[3] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First month of record"
    l[4] = convert_value_to_str_with_colon( year_s , 6 , 1) + "First year of record (1901 if not linked to a specific year)"
    l[5] = "  Average ETo (mm/day)"
    l[6]= "======================="

    for a in range( 0 , len(df_aquain.index)):
        l.append( str( df_aquain["ET0"].iloc[a] )  )
    save_file( l , "./DATA/yar.ETo")


    #I need to make a file for rainfall
    l = [None]*7
    l[0] = "yarmouth daily precipitation mm"
    l[1] = "     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)"
    l[2] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First day of record (1, 11 or 21 for 10-day or 1 for months)"
    l[3] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First month of record"
    l[4] = convert_value_to_str_with_colon( year_s , 6 , 1) + "First year of record (1901 if not linked to a specific year)"
    l[5] = "Total Rain mm"
    l[6]= "======================="

    for a in range( 0 , len(df_aquain.index)):
        l.append( str( df_aquain["Prcp(mm)"].iloc[a] )  )
    save_file( l , "./DATA/yar.PLU")


    #make a calendar file
    l = [None]*9
    l[0]= "Onset: " + str(year_s) + " " +str(month_s) + " " + str(day_s) 
    l[1] = convert_value_to_str_with_colon( 7.1 , 10 , 3) + " AquaCrop Version (August 2023)"
    l[2] = convert_value_to_str_with_colon( 0 , 10 , 3)   + " The onset of the growing period is fixed on a specific date"
    l[3] = convert_value_to_str_with_colon( -9 , 10 , 3)   + " Day-number (1 ... 366) of the Start of the time window for the onset criterion: Not applicable"
    l[4] = convert_value_to_str_with_colon( -9 , 10 , 3)   + " Length (days) of the time window for the onset criterion: Not applicable"
    l[5] = convert_value_to_str_with_colon(  sim_start_days_into_year, 10 , 3)   + " Day-number (1 ... 366) for the onset of the growing period"
    l[6] = convert_value_to_str_with_colon(  -9, 10 , 3)   + " preset value for generation of the onset: Not applicable"
    l[7] = convert_value_to_str_with_colon(  -9, 10 , 3)   + " Number of successive days: Not applicable"
    l[8] = convert_value_to_str_with_colon(  -9, 10 , 3)   + " Number of occurrences: Not applicable"

    save_file( l , "./DATA/yar.CAL")


    ##take all that and make a PRM file 
    cropfile = crop_file
    irrigationfile = irrigation_file

    l =[None]*49
    l[0]=   "Yarmouth NS "
    l[1]=(  convert_value_to_str_with_colon(7.1, 7 , 8) + "AquaCrop Version (August 2023)")
    l[2] = convert_value_to_str_with_colon(1, 7 , 8) + "Year number of cultivation (Seeding/planting year)"

    l[3] =  convert_value_to_str_with_colon( days_since_1901_convert(year_s , month_s, day_s) , 7 , 8) + " First day of simulation period "
    l[4] =  convert_value_to_str_with_colon( days_since_1901_convert(year_e , month_e, day_e) , 7 , 8) + " Last day of simulation period "
    l[5] =  convert_value_to_str_with_colon( days_since_1901_convert(year_s , month_s, day_s) , 7 , 8) + " First day of cropping period "
    l[6] =  convert_value_to_str_with_colon( days_since_1901_convert(year_e , month_e, day_e) , 7 , 8) + " Last day of cropping period "


    project = "yar"

    l[7] = "-- 1. Climate (CLI) file"
    l[8] = "   "+project+ ".CLI"
    l[9] = "   './DATA/'"

    l[10] = "   1.1 Temperature (Tnx or TMP) file"
    l[11] =     "   "+project+ ".Tnx"
    l[12] = "   './DATA/'"

    l[13] = "   1.2 Reference ET (ETo) file"
    l[14] =      "   "+project+ ".ETo"
    l[15] = "   './DATA/'"

    l[16] = "   1.3 Rain (PLU) file"
    l[17] = "   "+project+ ".PLU"
    l[18] = "   './DATA/'"

    l[19] = "   1.4 Atmospheric CO2 concentration (CO2) file"
    l[20]="   MaunaLoa.CO2"
    l[21]="   './SIMUL/'"

    l[22]="-- 2. Calendar (CAL) file"
    l[23]="   "+project+".CAL"
    l[24]="   './DATA/'"
    l[25]="-- 3. Crop (CRO) file"
    l[26]="   "+cropfile+ " " 
    l[27]="   './DATA/' "
    l[28]="-- 4. Irrigation management (IRR) file"
    l[29]="   "+irrigationfile
    l[30]="   './DATA/'"
    l[31]="-- 5. Field management (MAN) file"
    l[32]="   (None)"
    l[33]="   (None)"
    l[34]="-- 6. Soil profile (SOL) file"
    l[35]="   (None)"
    l[36]="   (None)"
    l[37]="-- 7. Groundwater table (GWT) file"
    l[38]="   (None)"
    l[39]="   (None)"
    l[40]="-- 8. Initial conditions (SW0) file"
    l[41]="   (None)"
    l[42] ="   (None)"
    l[43]="-- 9. Off-season conditions (OFF) file"
    l[44]="   (None)"
    l[45]="   (None)"
    l[46]="-- 10. Field data (OBS) file"
    l[47]="   (None)"
    l[48]="   (None)"
    save_file( l , "./LIST/yar.PRM")




