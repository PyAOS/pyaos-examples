#!/usr/bin/env python

# J-Y Peterschmitt - LSCE - 09/2011 - pmip2web@lsce.ipsl.fr

# This script can be used to test some features of CDAT, as well as learn
# how to use them, or experiment with them
#
# Features:
# * read 1 time step  from a netcdf data file with cdms2
# * play a little bit with masks
# * perform many standard 'vcs' operations, including
#      + creating and modifying a template
#      + selecting a specific projection
#      + creating and modifying a 'boxfill' graphics method
#      + plotting on- or off-screen
#      + creating and plotting markers
#      + creating and plotting continents
#      + working with several graphics windows (aka 'canvas')
#      + saving the graphics
#      + ...
# * do some operating system related operations with 'path' and 'os'
#   in an os-independant way

# Notes for NEW CDAT USERS :-)
#
# Execute this script with
#   python -i this_script.py
# in order to stay in the python interpreter when the script is finished
#
# Quit the interpreter with CTRL-D
#
# * resize the displayed graphics canvas if you get an empty canvas,
#   to force redrawing...
# * use the built-in help for modules, functions and objects
#     help(vcs), help(path.join), help(bf), ...
# * use 'dir' to determine the methods and attributes of an object,
#   or the functions of a module
#     dir(vcs), dir(x), ...
#   'dir()' will show all the variables and modules used in the script
# * use the 'list' method of vcs objects to get information about the
#   objects in a human-readable way
#     marker_test.list(), tpl.data.list(), ...
# * use the 'info' method of a MV2 variable to get informatin
#   about a variable
#     v.info()

# Import some standard modules
import sys, os
from os import path

# Import what we need from CDAT
import cdms2
import vcs
from numpy import ma

# Some data we can plot from the 'sample_data' directory
# supplied with CDAT
#data_dir = '/home/share/unix_files/cdat/versions/cdat_install_6.0.0.alpha_x86_64_gcc4_05/sample_data'
data_dir = path.join(sys.prefix, 'sample_data')
data_file = 'tas_mo.nc'
var_name = 'tas'

# Projection type. You can select any of the follosing
#   'linear', 'utm', 'state plane', 'albers equal area', 'lambert',
#   'mercator', 'polar', 'polyconic', 'equid conic a', 'transverse
#   mercator', 'stereographic', 'lambert azimuthal', 'azimuthal',
#   'gnomonic', 'orthographic', 'gen. vert. near per', 'sinusoidal',
#   'equirectangular', 'miller', 'van der grinten', 'hotin',
#   'robinson', 'space oblique', 'alaska', 'interrupted goode',
#   'mollweide', 'interrupted mollweide', 'hammer', 'wagner iv',
#   'wagner vii', 'oblated'
#proj_type = 'linear'
proj_type = 'robinson'
#proj_type = 'mollweide'
#proj_type = 'sinusoidal'
#proj_type = 'van der grinten'

# Initialize the graphics canvas
x = vcs.init()

# Output file formats
#output_types = [x.png, x.pdf, x.svg]
output_types = [x.png, x.pdf]

# Output 'resolutions'
# Suggested resolution: use 2 or 3
# output_res = [1] # What we have by default
output_res = [0.5, 1, 2, 3, 4]

# Background mode
# 0 : everything is plotted directly (on the screen)
# 1 : plot are made off-screen and only plotted on the screen (if need
#     be) at the end of the script with 'x.showbg()'
# Note: mode 1 is MUCH faster, but sometimes buggy...
bg_type = 0 # bg mode 'on'
#bg_type = 1 # bg mode 'off'

# Zone that we want to plot
(latmin, latmax, lonmin, lonmax) = (-90, 90, -180, 180)

# Read one time step (the first one) from the data file
# and explicitely specify the lat/lon range we need. cdms2
# will retrieve the data in the order we want, regardless of the way
# it is stored in the data file
#
# WARNING!
# Should write something about the 'oo' option below... Using a
# redundant longitude point seems to make it possible to have nice
# clean edges when you use non linear projections.
# If you need to work with the variable (not just plot it), YOU SHOULD
# USE longitude=(-180, 180, 'co')
f = cdms2.open(path.join(data_dir, data_file))
v = f(var_name, time=slice(0, 1), latitude=(latmin, latmax),
      longitude=(lonmin, lonmax, 'oo'), squeeze=1)
f.close()

# Mask some of the data (by using the 'masked' constant) to see how
# masked values are plotted with the boxfill graphics method
for i in range(min(v.shape)):
    # We mask 2 diagonals in the data matrix
    v[i, i] = ma.masked
    v[-1 -i, i] = ma.masked

# Locations of the markers in lat/lon
# Note: the test markers will be plotted on a regular grid and we only
# want 0 <= lat <= 90 and 0 <= lon < 180
marker_lats = range(0, 81, 20)
marker_lons = range(0, 161, 20)
# The marker types we want to test
marker_list = ['dot', 'diamond', 'diamond_fill', 'square', 'square_fill',
               'triangle_up_fill', 'triangle_down', 'star', 'cross']
nb_markers = len(marker_list)

# Explicitely select the orientation and colormap
# Note: choosing the 'landscape' mode and 'rainbow' colormap is what
# we would be by defauly anyway
x.landscape()
x.setcolormap('rainbow')

# Create a specific template to place everything correctly on the
# canvas (ie in the figure), rather that use the default
# We use 'normalized coordinates'
#   lower left corner of the canvas  = (0, 0)
#   upper right corner of the canvas = (1, 1)
tpl = x.createtemplate('custom_tpl', 'ASD')
# * The meridians and parallels are plotted by having the ticmarks
#   (tpl.xtic1 and tpl.ytic1) extend across the whole data plotting
#   area (tpl.data). This makes non 'linear' projections look nicer
#   => The actual location of the meridians/parallels will be
#      specified with the value of the {x|y}ticlabels1 attribute of
#      the graphics method
tpl.xtic1.y1 = tpl.data.y1
tpl.xtic1.y2 = tpl.data.y2
tpl.ytic1.x1 = tpl.data.x1
tpl.ytic1.x2 = tpl.data.x2
# * The longitude and latitude values will be plotted at the
#   'center' of the data area
tpl.ylabel1.x = (tpl.data.x1 + tpl.data.x2)/2 - 0.01
tpl.xlabel1.y = (tpl.data.y1 + tpl.data.y2)/2 - 0.02
# Disable the plotting of some stuff on the canvas
# by setting their priority to 0
tpl.box1.priority = 0 # No square box around the data area
tpl.max.priority = 0
tpl.min.priority = 0
tpl.mean.priority = 0
tpl.title.priority = 0
tpl.xtic2.priority = 0
tpl.ytic2.priority = 0
tpl.xlabel2.priority = 0
tpl.ylabel2.priority = 0

# Create the projection method
pm = x.createprojection('proj_test')
pm.type = proj_type

# Create a boxfill graphics method for plotting the data
bf = x.createboxfill('bf_test')
# Select the location (in world coordinates) and the annotations
# of the tick marks
bf.xticlabels1 = {-180:'', -160:'-160', -140:'-140', -120:'-120', -100:'-100',
                  -80:'-80', -60:'-60', -40:'-40', -20:'-20', 0:'',
                  20:'20E', 40:'40E', 60:'60E', 80:'80E',
                  100:'100E', 120:'120E', 140:'140E', 160:'160E', 180:''}
bf.yticlabels1 = {-90:'', -80:'-80', -60:'-60', -40:'-40', -20:'-20', 0:'',
                  20:'20N', 40:'40N', 60:'60N', 80:'80N', 90:''}
bf.datawc(latmin, latmax, lonmin, lonmax)
# Use 'light blue' instead of the default 'black' for plotting missing values
bf.missing = 255

# Plot the variable!
x.plot(tpl, pm, bf, v, bg=bg_type)

# Create the markers to overlay on the data plot
lat_list = []
lon_list = []
size_list = []
col_list = []
type_list = []
for lat_value in marker_lats:
    for lon_index, lon_value in enumerate(marker_lons):
        # Upper right side of the plot (NH, east of lon=0)
        # Same symbols, increasing size
        lat_list.append([lat_value])
        lon_list.append([lon_value])
        m_size = int(3 + lat_value / 12.)
        size_list.append(m_size)
        #col_list.append(241) # black
        col_list.append(247) # pink
        type_list.append('dot')
        
        # Lower right side of the plot (SH, east of lon=0)
        # Different symbols, same size
        if lat_value > 0:
            lat_list.append([-lat_value])
            lon_list.append([lon_value])
            size_list.append(10)
            col_list.append(246) # cyan (or magenta?)
            m_type = marker_list[lon_index % nb_markers]
            type_list.append(m_type)

        # SAME as above WEST of lon=0, except that we plot a
        # background below the markers
        
        # Upper left
        if lon_value > 0:
            lat_list.extend(([lat_value], [lat_value]))
            lon_list.extend(([-lon_value], [-lon_value]))
            size_list.extend((m_size + 2, m_size))
            col_list.extend((240, 247)) # pink/247 on white/240
            type_list.extend(('dot', 'dot'))
        
            # Lower right
            if lat_value > 0:
                lat_list.extend(([-lat_value], [-lat_value]))
                lon_list.extend(([-lon_value], [-lon_value]))
                size_list.extend((m_size + 2, m_size))
                col_list.extend((241, 246)) # cyan/246 on black/241
                type_list.extend((m_type, m_type))
        
marker_test = x.createmarker('marker_test')
# IMPORTANT! The markers have to be plotted with the
# * SAME projection as the graphics method they are overlaid on
# * SAME coordinates as the graphics method ("worldcoordinate")
# * SAME position as the data in the window ("viewport")
marker_test.projection = pm
marker_test.worldcoordinate = [lonmin, lonmax, latmin, latmax]
marker_test.viewport = [tpl.data.x1, tpl.data.x2,
                        tpl.data.y1, tpl.data.y2]
marker_test.x = lon_list
marker_test.y = lat_list
marker_test.size = size_list
marker_test.color = col_list
marker_test.type = type_list

# Plot the markers
x.marker(marker_test, bg=bg_type)

# Create a graphics method for just plotting the continents
# and plot the markers over it, in a new canvas
cont_test = x.createcontinents('cont')
cont_test.projection = pm
cont_test.xticlabels1 = bf.xticlabels1
cont_test.yticlabels1 = bf.yticlabels1
cont_test.datawc(latmin, latmax, lonmin, lonmax)
cont_test.type = 5 # continents with political borders
cont_test.linecolor = 242 # Red
y = vcs.init()
y.plot(tpl, cont_test, bg=bg_type)
y.marker(marker_test, bg=bg_type)

# Save the plot in a subdirectory
script_name = path.splitext(path.basename(sys.argv[0]))[0]
out_dir = script_name+ '_out'
if not path.exists(out_dir):
    # Create the new output directory
    os.mkdir(out_dir)

# We will be using proj_type in file names. Make sure it does
# not have any spaces in it
proj_type = proj_type.replace(' ', '-')

# We could just use a simple and default png and/or pdf plot
#   plotname = '%s_%s' % (script_name, proj_type)
#   plotname = path.join(out_dir, plotname)
#   x.png(plotname)
#   x.pdf(plotname)
# Instead, for testing purpose, we will loop on some functions
# that can be used for creating graphic files from the canvas
# and loop on different resolutions
for create_output in output_types: # Loop on functions :-)
    for resolution in output_res:
        plotname = '%s_%s_%s' % (script_name,
                                    proj_type, resolution)
        plotname = path.join(out_dir, plotname)
        # Note: 11"x8" is the size of the US Letter paper format
        create_output(plotname,
                      width=resolution*11,
                      height=resolution*8)

# Display the plots, if they were generated off-screen
if bg_type == 1:
    x.showbg()
    y.showbg()

print 'The %s script has finished running and now\nyou can play with python in interactive mode!' % (script_name,)
raw_input('Press return to finish')

# More things that new users  can try in interactive mode once the
# script has finished running
# * look at the python objects created in the script and try changing them
# * clear and close the graphics canvas with x.clear() and x.close()
# * look at the difference between
#     x.plot(tpl, pm, bf, v)
#   and
#     x.plot(v)
    
# The end
