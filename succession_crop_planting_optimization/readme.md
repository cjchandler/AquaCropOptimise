**Install**

Make sure you have python 3.x installed, with scipy, os, pandas. Python will warn you if you need to install any other packages, you can do this through pip.

Download the FAO command line aquacrop program (https://github.com/KUL-RSDA/AquaCrop/releases) v7.2 . You will need a fortran90 compiler to set it up, there is a test procedure included in the that git archive. Run the test, make sure it works.

Copy the compiled aquacrop program and replace the one in this directory (Likely the compiled one here won't work on your computer.) Now you should be able to run the optimisation example here with
$python run\_many\_simulations.py

Note that this example crop saladbowl3.CRO is unvalidated.

**Using the tools for other simulations**
basic\_greenhouse\_simulator.py uses a solcast (https://www.solcast.com) historical data file to get basic hourly climate data. There is a basic prediction of greenhouse temperature from this, and the base evaprotranspiration is calculated for inside the greenhouse (ET0). Output is saved in a pandas dataframe "climate.csv"

setup\_aquacrop\_input_files.py collects the information in the "climate.csv" file and other inputs for crop and irrigation and makes the files needed for the aquacrop program.

run\_one\_aquacrop\_sim.py is a function for making the proper input files (using the tools in setup\_aquacrop\_input\_files.py) and recording the daily output. I've chosen a few parameters I wanted to return, you can modify this for your needs. The whole daily data log of the simulation could be used as output but it's very verbose.

run\_many\_simulations.py has a class for staring many crops in a single year. These simulations are saved, and put into a pandas dataframe. Using these we can simulate the harvests for planting various areas throughout the year. To achieve a constant harvest throughout the year, the area planted on each date will have to change. An optimisation routine solves this problem and returns a dataframe with the optimal area to plant each day to achieve the desired harvest distribution.

**Future work**
This is a simple example of what is possible with crop simulations. To be used commercially, the crop file needs to be validated, and other the effect of future weather variability needs to be taken into account. Any questions can be directed to Carl Chandler at carljosepchandler@gmail.com
