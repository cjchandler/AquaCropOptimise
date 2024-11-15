**Install**

Make sure you have python 3.x installed, with scipy, os, pandas. Python will warn you if you need to install any other packages, you can do this through pip.

Download the FAO command line aquacrop program (https://github.com/KUL-RSDA/AquaCrop/releases) v7.2 . You will need a fortran90 compiler to set it up, there is a test procedure included in the that git archive. Run the test, make sure it works.

Copy the compiled aquacrop program and replace the one in this directory (Likely the compiled one here won't work on your computer.) Now you should be able to run the optimisation example here with
$python run_many_simulations.py

**Using the tools for other simulations**
load_climate_data.py uses a solcast (https://www.solcast.com) historical data file to get basic hourly climate data. This does not include precipitation data, so that comes from the Canadian historical weather data site (https://climate-change.canada.ca/climate-data/#/daily-climate-data). These are often in separate files so you can put in a list of files. Output is saved in a pandas dataframe "climate.csv"

setup_aquacrop_input_files.py collects the information in the "climate.csv" file and other inputs for crop and irrigation and makes the files needed for the aquacrop program. Also included is a function for making the proper input files (using the tools in setup_aquacrop_input_files.py) and recording the daily output. I've chosen a few parameters I wanted to return, you can modify this for your needs. The whole daily data log of the simulation could be used as output but it's very verbose.

run_many_simulations.py has a class for staring crops on different days across many years. These simulations are saved, and put into a pandas dataframe. Using these we can simulate the harvests for planting times, and when is the best time to plant for maximum yield.

**Future work**
This is a simple example of what is possible with crop simulations. To be used commercially, the effect of future weather variability needs to be taken into account. Any questions can be directed to Carl Chandler at carljosepchandler@gmail.com
