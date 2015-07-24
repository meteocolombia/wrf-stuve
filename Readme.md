# Introduction:

WRF_Stuve.py is published as free software under the terms of the GNU General Public
License (http://www.gnu.org/licenses/gpl.html)

This script is for those who prefer using Stüve diagram.
Those who like SkewT can rely on the GrADS script. 
If you need to calculate storm indices, this script can be usefull.


# Functions:

* Generates atmospheric soundings from the WRF output and displays it together with the measured sounding in one Stüve diagram
* Calculates storm indices from WRF output (Mixing Ratio of the mixing layer, Cape, Lift, Lifted Condensation Level, Level of Free Convection, Level of Neutral Bouancy) and puts it together with the measured ones in the same table. 


# Requirements:

* wget (http://www.gnu.org/software/wget/)
* nco (http://nco.sourceforge.net/, with ncrcat installed in /usr/local)
* python
* matplotlib
* scipy

# Install

Execute the following commands.

```
apt-get install nco wget
pip install -r requirements.pip

```

# Execution:


1. Edit file "namelist" 
2. python WRF_Stuve.py
(namelist and script have to be in the same directory)

namelist:
ruta = absolute path to wrfout* files
If you want to process only one file put its name in the path
codigo = WMO station code
wfecha = Date of the first wrfout* file
ifecha = Date of the first sounding
efecha = Date of the last sounding
dh = time interval (hours) between sounding ascents (normally 12 or 24, depends on nationality)
ifecha should have hours 00 or 12 to match with the sounding.
wfecha has to be before or the same date as ifecha.


# How it works:

The script has to be executed once for every sounding station changing "codigo" in the namelist.
Generates output in a loop over times from ifecha to efecha for every interval dh. 
There can be several dates in the same wrfout* file and ther can be several files. 
Model time steps can be less than dh.
The script seraches for all wrfout* files with initial date between wfecha and efecha. 
For every hour of the n soundings (ifecha+n*dh) it selects the file with the nearest date previous to the sounding. 
The name of every WRF output file has to begin with "wrfout" and has to contain the initial date in the format YYYY-MM-dd_HH:mm

Giving the station code, the script downloads the measured sounding using wget from http://weather.uwyo.edu/ as a text file to a file called <code>_<date>.csv
The download command includes the option -c, so you can reexecute the script without downloading the same text file every time. 
For the coordinates of the station given in the text file, extracts the simulated data from the WRF netcdf file for the nearest grid point by use of the "ncrcat" function of the NCO library.
 
**_Note:_** NCO is used in order to produce a smaller netcdf file that will be opened with scipy.io.netcdf. Nevertheless the script could work without NCO using only scipy.io.netcdf: Replace the commands os.system('ncrcat ... wrffile ...') with "io.netcdf.netcdf_file(wrffile,'r')", extract coordinates (lat=a.variables['XLAT'][0],lon=a.variables['XLONG'][0]), find grid points i,j, extract remaining variables for grid point i,j  
   

# Output:

For each sounding there will be two files:

<stationcode>_<date>.png:
The Stüve diagram with the simulated and measured soundings
red = simulated dew point (ºC)
blue = simulated temperature (ºC)
green = mixing ratio (g/kg) of the mixing layer
dark grey = measured dew point (ºC)
light grey = measured temperature 
You can chnage colors in the function stuve() from line 400.

<stationcode>_<date>.csv:
The table with the storm indices simulated (2.column) and observed (3.column).
The script calculates several indices que at te moment don't appear in the measured sounding.




