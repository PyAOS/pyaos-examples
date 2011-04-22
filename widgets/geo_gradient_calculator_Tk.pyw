#!/usr/bin/env python
# File: geo_gradient_calculator_TK.py

'''This Tkinter application allows the user to enter latitude, contour spacing, contour interval, and curvature
and then calculates the geostrophic and gradient winds for both cyclonic and anticyclonic flow.  It will also
calculate the anomalous cases'''

# Written by Alex DeCaria
# Latest version date:  2/23/2011

import sys
if sys.version_info[0] != 3:
    from Tkinter import *    # if Python 2.X
else:
    from tkinter import *    # if Python 3.X
    
import math

class Geo_Gradient:

    def __init__(self, master):

        master.title('GeoGradient Wind Calculator')
        master.resizable(0,0)
        #master.foreground = 'green'
        #Creates an outer frame within the main window
        self.outer_frame = Frame(master)
        self.outer_frame.pack(expand=YES, fill=BOTH)

        #Creates a data entry frame within the outer frame
        self.data_entry_frame = Frame(self.outer_frame)
        self.data_entry_frame.pack(side = LEFT, padx=10, pady=10,fill=BOTH)

        #Creates a frame and widgets for latitude label and slider
        self.lat_frame = LabelFrame(self.data_entry_frame, text = 'Latitude', foreground = 'blue')
        self.lat_frame.pack(fill=BOTH, pady=5)
        self.lat_scale = Scale(self.lat_frame, orient = HORIZONTAL, from_=5, to=90,
                               command=self.calculate)
        self.lat_scale.set(40)
        self.lat_scale.pack(fill=BOTH)

        #Creates a frame and widgets for interval label and slider        
        self.int_frame = LabelFrame(self.data_entry_frame, text = 'Contour Interval', foreground = 'blue')
        self.int_frame.pack(fill=BOTH, pady=5)
        self.p_or_z = IntVar()
        self.p_or_z.set(0)  # Set to 0 for pressure coordinates or 1 for height coordinates
        Radiobutton(self.int_frame, text = 'hPa', variable = self.p_or_z, value = 1,
                    command = self.change_scale).pack(side=LEFT)
        Radiobutton(self.int_frame, text = 'gpm', variable = self.p_or_z, value = 0,
                    command = self.change_scale).pack(side=LEFT)
        self.int_scale = Scale(self.int_frame, orient = HORIZONTAL, from_=1, to=120, bigincrement = 10,
                               command=self.calculate)
        self.int_scale.set(60)
        self.int_scale.pack(side = BOTTOM, fill = BOTH)
        
        #Creates a frame and widgets for distance label and slider        
        self.dist_frame = LabelFrame(self.data_entry_frame, text = 'Contour Spacing (km)', foreground = 'blue')
        self.dist_frame.pack(fill=BOTH, pady=5)
        self.dist_scale = Scale(self.dist_frame, orient = HORIZONTAL, from_=10, to=1500, bigincrement = 10,
                                command=self.calculate)
        self.dist_scale.set(400)
        self.dist_scale.pack(fill = BOTH)
        
        #Creates a frame and widgets for curvature label and slider        
        self.curv_frame = LabelFrame(self.data_entry_frame, text = 'Curvature (km)', foreground = 'blue')
        self.curv_frame.pack(fill=BOTH, pady=5)
        self.curv_scale = Scale(self.curv_frame, orient = HORIZONTAL, from_=100, to=4000, bigincrement = 100,
                                command=self.calculate)
        self.curv_scale.set(1500)
        self.curv_scale.pack(fill = BOTH)

        #Create results display frame within the outer frame
        self.results_frame = Frame(self.outer_frame)
        self.results_frame.pack(side = RIGHT, padx=10, pady=10, fill=BOTH)

        #Create units frame
        self.units_frame = LabelFrame(self.results_frame, text = 'Units', foreground = 'blue')
        self.units_frame.pack(side = TOP, fill=BOTH, pady=5)
        
        #Creates radiobuttons for units
        self.conversion = (1.0, 1.9438, 2.2351, 3.6) # conversion factors m/s to (m/s, kts, mph, hm/h)
        self.unit_types = ('m/s', 'kts', 'mph', 'km/h')
        self.units = IntVar()
        self.units.set(0)
        Radiobutton(self.units_frame, text = 'm/s',variable = self.units, value = 0,
                    command=self.calculate).pack(side = LEFT)
        Radiobutton(self.units_frame, text = 'kts',variable = self.units, value = 1,
                    command=self.calculate).pack(side = LEFT)
        Radiobutton(self.units_frame, text = 'mph',variable = self.units, value = 2,
                    command=self.calculate).pack(side = LEFT)
        Radiobutton(self.units_frame, text = 'km/h',variable = self.units, value = 3,
                    command=self.calculate).pack(side = LEFT)

        #Create geostrophic wind display labels
        self.geo_frame = LabelFrame(self.results_frame, text = 'Geostrophic Wind', foreground = 'blue')
        self.geo_frame.pack(side = TOP, fill = BOTH)
        self.geo_text = StringVar()
        self.geo_text.set('bye')
        self.geo_label = Label(self.geo_frame, text = 'hi',textvariable = self.geo_text)
        self.geo_label.pack(side = TOP,pady=5)

        #Create gradient cyclone wind display labels
        self.gradcyc_frame = LabelFrame(self.results_frame, text = 'Cyclonic Gradient Wind', foreground = 'blue')
        self.gradcyc_frame.pack(side = TOP, fill = BOTH)
        self.gradcyc_text = StringVar()
        self.gradcyc_text.set('bye')
        self.gradcyc_label = Label(self.gradcyc_frame, text = 'hi', textvariable = self.gradcyc_text)
        self.gradcyc_label.pack(side = TOP,pady=5)

        #Create gradient anticyclone wind display labels
        self.gradanti_frame = LabelFrame(self.results_frame, text = 'Anticyclonic Gradient Wind', foreground = 'blue')
        self.gradanti_frame.pack(side = TOP, fill = BOTH)
        self.gradanti_text = StringVar()
        self.gradanti_text.set('bye')
        self.gradanti_label = Label(self.gradanti_frame, text = 'hi', textvariable = self.gradanti_text)
        self.gradanti_label.pack(side = TOP,pady=5)
        #self.gradanti_label.configure(fg = 'red') # doesn't work!!!!

        #Create blurb label
        self.blurb_frame = Frame(self.results_frame)
        self.blurb_frame.pack(side = TOP, fill = BOTH, pady = 5)
        self.blurb = StringVar()
        self.blurb_string = '''GeoGradient written in 2011
by Alex DeCaria
For Educational Use Only
Accuracy Not Guaranteed
No Warranty Implied'''
        self.blurb.set(self.blurb_string)
        self.blurb_label = Label(self.blurb_frame, textvariable = self.blurb,
                                 font = "Arial 8 italic")
        self.blurb_label.pack(side = TOP, fill = BOTH)

    def change_scale(self): # This just sets the slider value when transitioning between height and pressure coord.

        if self.p_or_z.get():
            self.int_scale.set(4)
        else:
            self.int_scale.set(60)

    def calculate(self, val=0):
        '''Sets up and performs calculations when sliders are moved.'''
        # val is a dummy variable.  It is needed because when a scale widget or a radio button calls a command
        # they also send a value, so we need a variable to accept it, even though we don't need it.  Val is
        # assigned a default value because when a checkbutton issues a command call, it doesn't send a
        # value, and Python complains that not enough arguments are sent.
        
        results = self.geo_gradient(self.lat_scale.get(),self.int_scale.get(),
                                self.dist_scale.get(),self.curv_scale.get(),pressure=self.p_or_z.get())
        results = list(results) # converts results from tuple to list (so that it is mutable)
        #print(results)
        for i in range(len(results)):  # applies unit conversion
            results[i] *= self.conversion[self.units.get()]
        #print(results)
        template = "{0:.1f} {1:s}" # formatting template
        #set labels for winds
        self.geo_text.set("%.1f %s" % (results[0], self.unit_types[self.units.get()]))
        self.gradcyc_text.set(template.format(results[1], self.unit_types[self.units.get()]))
        if math.isnan(results[2]): # used math.isnan because in Python float('nan')==float('nan') is False!
            self.gradanti_text.set('Does not exist.')
            self.gradanti_label['fg'] = 'red'
        else:
            self.gradanti_text.set(template.format(results[2], self.unit_types[self.units.get()]))
            self.gradanti_label['fg'] = 'black'

    def geo_gradient(self, lat, interval, distance, radius, pressure = False, anomalous = False):
        '''Calulates geostrophic and gradient wind speeds (m/s).
        Input is latitude (deg), contour interval, distance (km), and radius (km).
        Set pressure = True for pressure.  Default is height.
        Set anomalous = True to return both normal and anomalous values.  Default is normal only.
        Pressure in hPa, distances in kilometers.'''
        import math
        omega = 7.292e-5  #  angular velocity of Earth, rad per second
        g = 9.80665  #  standard gravity
        f = 2*omega*math.sin(lat*math.pi/180.0) # Coriolis parameter
        distance *= 1000.0  #  Convert to meters
        radius *= 1000.0    #  Convert to meters
        if pressure:
            v_geo = interval*100.0/1.23/f/distance
        else:
            v_geo = g*interval/f/distance

        fr = f*radius

        # Calculate anticyclonic gradient wind
        term = fr**2 - 4*fr*v_geo
        v_grad_anti = float('nan') if term < 0 else (fr - math.sqrt(term))/2.0
        v_grad_anti_anom = float('nan') if term < 0 else (fr + math.sqrt(term))/2.0

        # Calculate cyclonic gradient wind
        term = fr**2 + 4*fr*v_geo
        v_grad_cyc = (-fr + math.sqrt(term))/2.0
        v_grad_cyc_anom = (fr + math.sqrt(term))/2.0

        if anomalous:
            return v_geo, v_grad_cyc, v_grad_anti, v_grad_cyc_anom, v_grad_anti_anom
        else:
            return v_geo, v_grad_cyc, v_grad_anti

# ------------ END OF APP DEFINITION -------------------------------------------------------

# Calls Tk library, instantiates application, and enters the main loop
root = Tk()
app = Geo_Gradient(root)
root.mainloop()

