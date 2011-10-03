#!/usr/bin/env python

# J-Y Peterschmitt - LSCE - 09/2011 - pmip2web@lsce.ipsl.fr

# Test the use of hatches and patterns in the isofill
# and fill area graphics methods

# Import some standard modules
import sys, os
from os import path

# Import what we need from CDAT
import cdms2
import vcs

# Some data we can plot from the 'sample_data' directory
# supplied with CDAT
data_dir = path.join(sys.prefix, 'sample_data')
data_file = 'tas_mo.nc'
var_name = 'tas'

# Zone that we want to plot
#
# NOTE: the (latmin, latmax, lonmin, lonmax) information HAS TO be the
# same in the variable, the 'isof' isofill method and the 2 'cont_*'
# continents plotting methods! Otherwise, the data will not match the
# continents that are plotted over it...
(latmin, latmax, lonmin, lonmax) = (-90, 90, -180, 180)

# Use black on white continents (nicer with black and white plots) i.e
# we plot a 'large' white continent outline over the data, and then a
# smaller 'black' continent outline
#bw_cont = False
bw_cont = True

# Read one time step (the first one) from the data file
# and explicitely specify the lat/lon range we need. cdms2
# will retrieve the data in the order we want, regardless of the way
# it is stored in the data file
f = cdms2.open(path.join(data_dir, data_file))
v = f(var_name, time=slice(0, 1), latitude=(latmin, latmax),
      longitude=(lonmin, lonmax, 'co'), squeeze=1)
f.close()

# Initialize the graphics canvas
x = vcs.init()

# Create the isofill method
isof = x.createisofill('test_hatch')
isof.datawc(latmin, latmax, lonmin, lonmax)
isof.levels = [220, 240, 260, 280, 300, 320]
isof.fillareastyle = 'hatch'
isof.fillareacolors = [241, 241, 241, 241, 241] # All black
#isof.fillareacolors = [243, 248, 254, 255, 241] # Colors
isof.fillareaindices = [20, 9, 2, 7, 3]

# Define some graphics methods for plotting black on white continents
if bw_cont:
    cont_black = x.createcontinents('black')
    cont_black.datawc(latmin, latmax, lonmin, lonmax)
    cont_black.linecolor = 241
    cont_black.linewidth = 2
    cont_white = x.createcontinents('white')
    cont_white.datawc(latmin, latmax, lonmin, lonmax)
    cont_white.linecolor = 240
    cont_white.linewidth = 6

    cont_type = 0 # Do not plot the default continents
else:
    cont_type = 1

# Plot the test data
#
# We have to make sure the data and the continents are plotted at the
# same place ('data' area) on the canvas, by using the same template!
# It's even better if we can use for the continents a template that
# will only plot the data area (the priority of the other elements of
# the canvas is set to zero)
tpl = x.createtemplate('tpl', 'ASD')
x.plot(tpl, isof, v, continents=cont_type)
if bw_cont:
    tpl_data = x.createtemplate('tpl_data', 'ASD_dud') # plots only data area
    x.plot(tpl_data, cont_white)
    x.plot(tpl_data, cont_black)

# Create a test plot for listing all the hatches and patterns
style_list = []
index_list = []
col_cycle = [243, 248, 254, 241, 255]
nb_cols = len(col_cycle)
color_list = []
x_list = []
y_list = []
txt_x_list = []
txt_y_list = []
txt_str_list = []

shear_x = .05
for j, style in enumerate(['hatch', 'pattern']):
    slide_y = j * .4
    for i in range(20):
        slide_x = i * 0.04
        x1, y1 = (.05 + slide_x, .25 + slide_y)
        x2, y2 = (.08 + slide_x, .45 + slide_y)

        # Add (sheared) rectangles to the list of positions
        # NOTE: no need to close the fill area. Giving 4 vertices
        #       for getting a filled rectangle is enough
        x_list.append([x1, x2, x2 + shear_x, x1 + shear_x])
        y_list.append([y1, y1, y2, y2])

        style_list.append(style)
        # Hatches/Patterns indices have to be in 1-20 range
        index_list.append(i+1)
        col_idx = col_cycle[i % nb_cols]
        color_list.append(col_idx)

        # Annotations
        txt_x_list.append(x1 + 0.015)
        txt_y_list.append(y1 - 0.015)
        txt_str_list.append('%s = %i  -  Color = %i' %
                             (style, i+1, col_idx))

# Create the fill area and the text annotations
fill_test = x.createfillarea('fill_test')
fill_test.style = style_list
fill_test.index = index_list
fill_test.color = color_list
fill_test.x = x_list
fill_test.y = y_list

fill_info = x.createtext('fill_info')
fill_info.angle = 45
fill_info.height = 20
fill_info.color = 241 # Black
fill_info.string = txt_str_list
fill_info.x = txt_x_list
fill_info.y = txt_y_list

# Create a title
plot_title = x.createtext('plot_title')
plot_title.height = 40
plot_title.string = ['Testing hatches and patterns in VCS/CDAT']
plot_title.x = [.01]
plot_title.y = [.9]

# Initialize and use a second graphics canvas
y = vcs.init()
y.plot(plot_title)
y.plot(fill_test)
y.plot(fill_info)

# Save the plots
x.pdf('test_fillarea')
x.png('test_fillarea')
y.pdf('test_fillarea_list')
y.png('test_fillarea_list')

# Note: depending on the version of CDAT, text may not resize
#       correctly when creating a bigger png
#x.png('test_fillarea_big', width=3*11, height=3*8)
#y.png('test_fillarea_list_big', width=3*11, height=3*8)

# The end
