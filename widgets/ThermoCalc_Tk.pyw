#!/usr/bin/env python
import sys

from Tkinter import *

if sys.version_info[0] != 3:
    from Tkinter import *    # if Python 2.X
else:
    from tkinter import *    # if Python 3.X
    
import math

# Some physical constants as global variables
g = 9.80665  #  gravity m/s
Rd = 287.1 # Specific gas contant for dry air, J kg-1 K-1
Rv = 461.5 # Specific gas constant for water vapor, J kg-1 K-1
Lv = 2.5e6 # Latent heat of vaporization, J kg-1
cp = 1007.0 # Specific heat at constant pressure, J kg-1 K-1

class ThermoCalc:
    '''This application is a thermodynamic calculator for air under normal atmospheric conditions.
    The user inputs pressure, temperature, and relative humidity, and other thermodynamic quantities
    are calculated and displayed.  Pressure can be input either as station pressure, or as sea-level
    pressure and altitude.'''
    # Created by Alex DeCaria
    # Latest version:  3/3/2011
    # Requires Python 2.6 or later.

    def __init__(self, master):

        master.title('ThermoCalc')
        master.resizable(0,0)

        # Some instance and global variables
        self.t_template = '{0:.1f} {1:s}' # format for temperature strings
        self.p_template = ('{0:.1f} {1:s}', '{0:.2f} {1:s}') # format for pressure strings
        self.vap_template = ('{0:.1f}  /  {1:.1f}  {2:s}', '{0:.2f}  /  {1:.2f}  {2:s}') # format for vapor pressure string
        self.a_template = ('{0:.0f} {1:s}', '{0:.0f} {1:s}') # format for altitude strings
        self.h_template = '{0:.1f} %' # format for relative humidity string
        self.mix_template = '{0:.2f}  /  {1:.2f}  g/kg'
        self.slider_xpad = 60  # padding for all sliders
        
        master.title('ThermoCalc')

        #Create blurb label
        self.blurb_frame = Frame(master)
        self.blurb_frame.pack(side = BOTTOM, fill = BOTH, pady = 5)
        self.blurb = StringVar()
        self.blurb_string = '''ThermoCalc written in 2011 by Alex DeCaria
For Educational Use Only.  Accuracy Not Guaranteed.  No Warranty Implied'''
        self.blurb.set(self.blurb_string)
        Label(self.blurb_frame, textvariable = self.blurb,
                                font = "Arial 8 italic").pack(side = TOP, fill = BOTH)

        # Creates an input frame within the main window.  This frame contains all the sliders and button
        # that control and displaythe inputs variables
        self.input_frame = Frame(master)
        self.input_frame.pack(side = LEFT, padx=5)

        # Creates a results frame within the main window.  This frame contains all the display
        # labels for the calculated variables.
        self.results_frame = Frame(master)
        self.results_frame.pack(side = RIGHT, padx=5)
        

        # Creates a frame for holding options radio buttons
        self.options_frame = Frame(self.input_frame)
        self.options_frame.pack(side=TOP, fill=BOTH)

        #Creates a frame and buttons for temperature units
        self.t_buttons_frame = LabelFrame(self.options_frame,
                                text = 'Temperature Units',
                                fg = 'blue')
        self.t_buttons_frame.pack(side=LEFT, fill=BOTH)
        self.t_choice = IntVar()
        self.t_choice.set(1)
        self.t_units = ('K', 'C', 'F')
        self.t_conv = ((1.0, 0.0), (1.0, -273.15), (1.8, -459.67))
        for i, j in enumerate(self.t_units):
            Radiobutton(self.t_buttons_frame, text = j, variable = self.t_choice,
                                value = i, command=self.t_unit_change).pack(side=LEFT)

        #Creates a frame and buttons for pressure units
        self.p_buttons_frame = LabelFrame(self.options_frame,
                                text = 'Pressure Units',
                                fg = 'blue')
        self.p_buttons_frame.pack(side=LEFT, fill=BOTH)
        self.p_choice = IntVar()
        self.p_choice.set(0)
        self.p_units = ('hPa', 'in-Hg')
        self.p_conv = (0.01, 0.00029528744140143107)
        for i, j in enumerate(self.p_units):
            Radiobutton(self.p_buttons_frame, text = j, variable = self.p_choice,
                                value = i, command = self.p_unit_change).pack(side=LEFT)

        #Creates a frame and buttons for altitude units
        self.a_buttons_frame = LabelFrame(self.options_frame,
                                text = 'Altitude Units',
                                fg = 'gray')
        self.a_buttons_frame.pack(side=RIGHT, fill=BOTH)
        self.a_choice = IntVar()
        self.a_choice.set(0)
        self.a_units = ('m', 'ft')
        self.a_conv = (1.0, 3.28084)
        self.a_button = [i for i in range(len(self.a_units))] # array to hold altitude units buttons
        for i, j in enumerate(self.a_units):
            self.a_button[i] = Radiobutton(self.a_buttons_frame, text = j,
                                variable = self.a_choice,value = i,command = self.a_unit_change)
            self.a_button[i].pack(side=LEFT)
            self.a_button[i]['state'] = 'disabled'

        #Creates a frame for station pressure slider and indicator
        self.p_frame = LabelFrame(self.input_frame, text = 'Pressure', fg = 'blue')
        self.p_frame.pack(side=TOP, fill=BOTH)
        self.p_scale = Scale(self.p_frame, orient = HORIZONTAL, from_=5000, to=116000,
                             resolution = 10, showvalue = 0, command = self.update_p_label)
        self.p_scale.set(101320)
        self.p_scale.pack(side=LEFT, fill=BOTH, ipadx=self.slider_xpad)
        self.p_string = StringVar()
        self.p_label = Label(self.p_frame, textvariable=self.p_string)
        self.p_label.pack(side=RIGHT)

        #Creates a frame for temperature slider and indicator
        self.t_frame = LabelFrame(self.input_frame, text = 'Temperature', fg = 'blue')
        self.t_frame.pack(side=TOP, fill=BOTH)
        self.t_scale = Scale(self.t_frame, orient = HORIZONTAL, from_=190, to=330,
                             resolution = 0.1, showvalue = 0, command = self.update_t_label)
        self.t_scale.set(288)
        self.t_scale.pack(side=LEFT, fill=BOTH, ipadx=self.slider_xpad)
        self.t_string = StringVar()
        self.t_label = Label(self.t_frame, textvariable=self.t_string)
        self.t_label.pack(side=RIGHT)

        #Creates a frame for relative humidity slider and indicator
        self.h_frame = LabelFrame(self.input_frame, text = 'Relative Humidity', fg = 'blue')
        self.h_frame.pack(side=TOP, fill=BOTH)
        self.h_scale = Scale(self.h_frame, orient = HORIZONTAL, from_=0, to=102,
                             resolution = 0.5, showvalue = 0, command = self.update_h_label)
        self.h_scale.set(0)
        self.h_scale.pack(side=LEFT, fill=BOTH, ipadx=self.slider_xpad)
        self.h_string = StringVar()
        self.h_label = Label(self.h_frame, textvariable=self.h_string)
        self.h_label.pack(side=RIGHT)

        #Create check button for using sea-level pressure
        self.use_slp = IntVar()
        self.use_slp.set(0)
        Checkbutton(self.input_frame, text = 'Calculate pressure from sea-level pressure',
                    variable=self.use_slp,command = self.slp_button).pack(side=TOP)
        
        #Creates a frame for sea-level pressure slider and indicator
        self.mslpalt_frame = Frame(self.input_frame)
        self.mslpalt_frame.pack(side=TOP, fill=BOTH)
        self.mslp_frame = LabelFrame(self.mslpalt_frame, text = 'Sea-level Pressure', fg = 'gray')
        self.mslp_frame.pack(side=TOP, fill=BOTH)
        self.mslp_scale = Scale(self.mslp_frame, orient = HORIZONTAL, from_=85000, to=106000,
                             resolution = 10, showvalue = 0, command = self.update_mslp_label)
        self.mslp_scale.set(101320)
        self.mslp_scale.pack(side=LEFT, fill=BOTH, ipadx=self.slider_xpad)
        self.mslp_scale['state'] = 'disabled'
        self.mslp_string = StringVar()
        self.mslp_label = Label(self.mslp_frame, textvariable=self.mslp_string)
        self.mslp_label.pack(side=RIGHT)

        #Creates a frame for altitude slider and indicator
        self.a_frame = LabelFrame(self.mslpalt_frame, text = 'Altitude', fg = 'gray')
        self.a_frame.pack(side=TOP, fill=BOTH)
        self.a_scale = Scale(self.a_frame, orient = HORIZONTAL, from_= -500, to=16700,
                             resolution = 1, showvalue = 0, command = self.update_a_label)
        self.a_scale.set(0)
        self.a_scale.pack(side=LEFT, fill=BOTH, ipadx=self.slider_xpad)
        self.a_scale['state'] = 'disabled'
        self.a_string = StringVar()
        self.a_label = Label(self.a_frame, textvariable=self.a_string)
        self.a_label.pack(side=RIGHT)

        #Creates a frame for density
        self.rho_frame = LabelFrame(self.results_frame, text = 'Density', fg = 'brown')
        self.rho_frame.pack(side=TOP, fill='x')
        self.rho_string = StringVar()
        Label(self.rho_frame, textvariable=self.rho_string).pack(side=TOP)

        #Creates a frame for virtual temperature
        self.virt_frame = LabelFrame(self.results_frame, text = 'Virtual Temperature', fg = 'brown')
        self.virt_frame.pack(side=TOP, fill='x')
        self.virt_string = StringVar()
        Label(self.virt_frame, textvariable=self.virt_string).pack(side=TOP)
        
        #Creates a frame for dew-point temperature
        self.td_frame = LabelFrame(self.results_frame, text = 'Dew Point', fg = 'brown')
        self.td_frame.pack(side=TOP, fill='x')
        self.td_string = StringVar()
        Label(self.td_frame, textvariable=self.td_string, justify='left').pack(side=TOP)

        #Creates a frame for vapor pressure/saturation vapor pressure
        self.vapor_frame = LabelFrame(self.results_frame, text = 'Vap./Sat-Vap. Pressure', fg = 'brown')
        self.vapor_frame.pack(side=TOP, fill='x')
        self.vapor_string = StringVar()
        Label(self.vapor_frame, textvariable=self.vapor_string).pack(side=TOP)

        #Creates a frame for mixing ratio/specific humidity
        self.mix_frame = LabelFrame(self.results_frame, text = 'Mix. Ratio/Spec. Hum.', fg = 'brown')
        self.mix_frame.pack(side=TOP, fill='x')
        self.mix_string = StringVar()
        Label(self.mix_frame, textvariable=self.mix_string).pack(side=TOP)

        #Creates a frame for absolute humidity
        self.abs_frame = LabelFrame(self.results_frame, text = 'Absolute Humidity', fg = 'brown')
        self.abs_frame.pack(side=TOP, fill='x')
        self.abs_string = StringVar()
        Label(self.abs_frame, textvariable=self.abs_string).pack(side=TOP)

        #Creates a frame for potential temperature
        self.theta_frame = LabelFrame(self.results_frame, text = 'Potential Temperature', fg = 'brown')
        self.theta_frame.pack(side=TOP, fill='x')
        self.theta_string = StringVar()
        Label(self.theta_frame, textvariable=self.theta_string).pack(side=TOP)

    def slp_button(self, val=0): # actions if use slp button checked
        if self.use_slp.get():
            self.mslp_frame['fg'] = 'blue'
            self.a_frame['fg'] = 'blue'
            self.a_scale['state'] = 'active'
            self.a_buttons_frame['fg'] = 'blue'
            self.p_frame['fg'] = 'brown'
            for i in self.a_button:
                i['state'] = 'active'
            self.mslp_scale['state'] = 'active'
            self.mslp_scale.set(self.p_scale.get())
            self.update_mslp_label()
            self.a_scale.set(0)
            self.update_a_label()
            self.p_scale['state'] = 'disabled'
            
        else:
            self.mslp_frame['fg'] = 'gray'
            self.a_frame['fg'] = 'gray'
            self.update_mslp_label()
            self.update_a_label()
            self.a_scale['state'] = 'disabled'
            self.a_buttons_frame['fg'] = 'gray'
            self.p_frame['fg'] = 'blue'
            for i in self.a_button:
                i['state'] = 'disabled'
            self.mslp_scale['state'] = 'disabled'
            self.p_scale['state'] = 'active'

    def p_unit_change(self, val=0):  #val is dummy
        self.update_mslp_label()
        self.update_p_label()

    def a_unit_change(self, val=0):  #val is dummy
        self.update_a_label()            

    def t_unit_change(self, val=0):  # val is dummy
        self.update_t_label()
        self.calculate()

    def update_mslp_label(self, val=0):   # val is dummy
        i = self.p_choice.get()
        if self.use_slp.get():
            self.pressure_reduction()
            self.mslp_string.set(self.p_template[i].format(self.mslp_scale.get()*self.p_conv[i],
                                            self.p_units[i]))
            self.calculate()
        else:
            self.mslp_scale.set(101320)
            self.mslp_string.set('')
        
    def update_p_label(self, val=0):  # val is dummy
        i = self.p_choice.get()
        self.p_string.set(self.p_template[i].format(self.p_scale.get()*self.p_conv[i],
                                            self.p_units[i]))
        self.calculate()

    def update_h_label(self, val=0):  # val is dummy
        self.h_string.set(self.h_template.format(self.h_scale.get()))
        self.calculate()

    def update_a_label(self, val=0):   # val is dummy
        i = self.a_choice.get()
        if self.use_slp.get():
            self.a_string.set(self.a_template[i].format(self.a_scale.get()*self.a_conv[i], self.a_units[i]))
            self.pressure_reduction()
        else:
            self.a_scale.set(0)
            self.a_string.set('')

    def update_t_label(self, val=0):   # val is dummy 
        self.t_string.set(self.t_template.format(self.t_scale.get()*self.t_conv[self.t_choice.get()][0]+
                         self.t_conv[self.t_choice.get()][1], self.t_units[self.t_choice.get()]))
        if self.use_slp.get():
            self.pressure_reduction()
        self.calculate()

    def pressure_reduction(self):
        i = self.p_choice.get()
        H = Rd*self.t_scale.get()/g  # Scale height
        term = math.exp(-self.a_scale.get()/H)
        p = self.mslp_scale.get()*term
        self.p_scale['state'] = 'normal'
        self.p_scale.set(p)
        self.p_string.set(self.p_template[i].format(self.p_scale.get()*self.p_conv[i],
                                                self.p_units[i]))
        self.p_scale['state'] = 'disabled'

    def calculate(self):
        '''Calculates thermodynamic variables from p, T, and RH.'''
        i = self.p_choice.get()  # index for pressure units
        T = self.t_scale.get()
        p = self.p_scale.get()
        RH = self.h_scale.get()/100.0
        term=Lv/Rv
        sat_vapor = 611.0*math.exp(term*(1.0/273.15 - 1.0/T))
        vapor = sat_vapor*RH
        e = (vapor*self.p_conv[i], sat_vapor*self.p_conv[i])
        s = self.vap_template[i].format(e[0], e[1], self.p_units[i])
        self.vapor_string.set(s)
        if vapor == 0:
            Td = float('-inf')
            self.td_string.set('dry')
        else:
            Td_recip = 1.0/T - math.log(vapor/sat_vapor)/term
            Td = 1.0/Td_recip
            self.td_string.set(self.t_template.format(Td*self.t_conv[self.t_choice.get()][0]+
                         self.t_conv[self.t_choice.get()][1], self.t_units[self.t_choice.get()]))
        abs_hum = vapor/Rv/T
        self.abs_string.set("{0:.2f} g/m^3".format(abs_hum*1000.0))        
        mix_ratio = (Rd/Rv)*vapor/(p-vapor)
        spec_hum = mix_ratio/(1 + mix_ratio)
        self.mix_string.set(self.mix_template.format(mix_ratio*1000, spec_hum*1000))
        Tv = T*(1 + 0.61*spec_hum)
        self.virt_string.set(self.t_template.format(Tv*self.t_conv[self.t_choice.get()][0]+
                         self.t_conv[self.t_choice.get()][1], self.t_units[self.t_choice.get()]))
        rho = p/Rd/Tv
        self.rho_string.set("{0:.2f} kg/m^3".format(rho))
        theta = T*(100000.0/p)**(Rd/cp)
        self.theta_string.set(self.t_template.format(theta*self.t_conv[self.t_choice.get()][0]+
                         self.t_conv[self.t_choice.get()][1], self.t_units[self.t_choice.get()]))
        

# ------------- END OF APP DEFINITION -----------------------------------

# Calls Tk library, instantiates application, and enters the main loop
root = Tk()
app = ThermoCalc(root)
root.mainloop()

        



