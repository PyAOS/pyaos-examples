#!/usr/bin/env/python

# Module that will make it easier for users to generate nice polar
# plots. At least 2 polar plots in landscape mode
#
# See example at the bottom (and execute this module as a script to
# check the result
#
# J-Y Peterschmitt - 05/2011 - pmip2web@lsce.ipsl.fr

# from cdms.selectors import Selector # for old versions of CDAT
from cdms2.selectors import Selector # for up-to-date CDAT

# Template positionning options
leg_height_default = 0.02
shift_left_default = 0.05

# Create templates with "no legend" (basically, only keep the data
# area and the titles), based on the existing templates
def create_tpl_nl(x, tpl_d):
    tpl_exist = tpl_d.keys()
    for tpl_name in tpl_exist:
        # Do not do anything, if the current template is already OK
        # (ie already ends with '_nl')
        if tpl_name.endswith('_nl'):
            continue
        name_no_legend = '%s_%s' % (tpl_name, 'nl')
        if name_no_legend not in x.listelements('template'):
            tpl_no_legend = x.createtemplate(name_no_legend, tpl_name)
            tpl_no_legend.legend.priority = 0
            tpl_no_legend.min.priority = 0
            tpl_no_legend.mean.priority = 0
            tpl_no_legend.max.priority = 0
            tpl_no_legend.units.priority = 0
            tpl_no_legend.title.priority = 0
        else:
            tpl_no_legend = x.gettemplate(name_no_legend)
        tpl_d[name_no_legend] = tpl_no_legend

# Create 2 templates suitable for polar plots in landscape
# orientation: tpl_left, tpl_right
#
# Notes:
# * comment1 and comment2 centered above the data area
def create_tpl_land(x, tpl_d={},
                    leg_height=leg_height_default,
                    shift_left=shift_left_default):
    
    # Left template
    if not tpl_d.has_key('tpl_l_left'):
        if 'tpl_l_left' not in x.listelements('template'):
            tpl_l_left = x.createtemplate('tpl_l_left', 'polar')
            tpl_l_left.scale(.5, 'x')
            tpl_l_left.scale(.9)
            tpl_l_left.scale(9.9/11.3, 'y')  # Try to get a really round polar plot!
            tpl_l_left.dataname.priority = 0
            tpl_l_left.comment1.x = (tpl_l_left.data.x1 + tpl_l_left.data.x2) / 2
            tpl_l_left.comment1.y = tpl_l_left.data.y2 + 0.05
            tpl_l_left.comment1.textorientation = 'center20'
            tpl_l_left.comment2.x = tpl_l_left.comment1.x
            tpl_l_left.comment2.y = tpl_l_left.data.y2 + 0.025
            tpl_l_left.comment2.textorientation = 'center15'
            leg_height = tpl_l_left.legend.y2 - tpl_l_left.legend.y1
            tpl_l_left.legend.x1 = tpl_l_left.data.x1 + (tpl_l_left.data.x1 + tpl_l_left.data.x2) * .25 - shift_left
            tpl_l_left.legend.x2 = tpl_l_left.data.x2 - shift_left
            tpl_l_left.legend.y2 = tpl_l_left.data.y1 - leg_height
            tpl_l_left.legend.y1 = tpl_l_left.legend.y2 - leg_height
            tpl_l_left.title.priority = 0
            tpl_l_left.min.priority = 0
            tpl_l_left.mean.priority = 0
            tpl_l_left.max.priority = 0
            tpl_l_left.units.priority = 0
        else:
            tpl_l_left = x.gettemplate('tpl_l_left')
        tpl_d['tpl_l_left'] = tpl_l_left

    # The 'right' template is based on the previously created 'left'
    # template shifted a bit right
    if not  tpl_d.has_key('tpl_l_right'):
        if 'tpl_l_right' not in x.listelements('template'):
            tpl_l_right = x.createtemplate('tpl_l_right', 'tpl_l_left')
            tpl_l_right.move(.47, 'x')
        else:
            tpl_l_right = x.gettemplate('tpl_l_right')
        tpl_d['tpl_l_right'] = tpl_l_right

    # Create the 'no legend' templates
    create_tpl_nl(x, tpl_d)

    return tpl_d

# Create polar graphic methods for the requested zones
# based on the supplied dictionary of graphic methods
def create_gm(x, gm_d={}, proj_d={}, select_d={},
              zones={'NH':(0, 90, -180, 180),
                     'SH':(-90, 0, -180, 180)},
              lat_tics={-90:'', -60:'', -30:'', 0:'', 30:'', 60:'', 90:''},
              lon_tics={-180:'', -120:'', -60:'', 0:'', 60:'', 120:''}):
    gm_exist = gm_d.keys()
    for gm_name in gm_exist:
        gm_source = gm_d[gm_name]
        if vcs.isboxfill(gm_source):
            creategm = x.createboxfill
        elif vcs.isisofill(gm_source):
            creategm = x.createisofill
        elif vcs.isisoline(gm_source):
            creategm = x.createisoline
        elif vcs.isoutline(gm_source):
            creategm = x.createoutline
        else:
            raise 'Unsupported graphic method in [%s]' % (gm_name,)

        for zone in zones.keys():
            zll = zones[zone]

            # Define selectors consistent with the requested zones
            if not select_d.has_key(zone):
                select_d[zone] = Selector(latitude=(zll[0], zll[1]),
                                            longitude=(zll[2], zll[3]))

            # Determine if we need a North or South pole projection,
            # depending on the specified zone
            if zll[1] > 0:
                # Requested max lat is in the northern hemisphere, so
                # we assume we want a North pole projection
                if not proj_d.has_key('p_north'):
                    if 'p_north' not in x.listelements('projection'):
                        p_north = x.createprojection('p_north')
                        p_north.type='orthographic'
                        p_north.centerlongitude = 0.
                        p_north.centerlatitude = 90.
                    else:
                        p_north = x.createprojection('p_north')
                    proj_d['p_north'] = p_north
                zone_proj = proj_d['p_north']
            else:
                # We need a South pole projection
                if not proj_d.has_key('p_south'):
                    if 'p_south' not in x.listelements('projection'):
                        p_south = x.createprojection('p_south')
                        p_south.type='orthographic'
                        p_south.centerlongitude = 0.
                        p_south.centerlatitude = -90.
                    else:
                        p_south = x.createprojection('p_south')
                    proj_d['p_south'] = p_south
                zone_proj = proj_d['p_south']
            
            # Create the apropriate graphic method for the current
            # zone
            name_zone = '%s_%s' % (gm_name, zone)
            gm_zone = creategm(name_zone, gm_name)
            gm_zone.projection = zone_proj
            gm_zone.datawc(zll[0], zll[1], zll[2], zll[3])
            gm_zone.yticlabels(lat_tics, '')
            gm_zone.xticlabels(lon_tics, '')
            
            gm_d[name_zone] = gm_zone

    return gm_d, proj_d, select_d

# Test the module by running it as a script
if __name__ == '__main__':

    import vcs
    # import cdms # for old versions of CDAT
    import cdms2 as cdms # for up-to-date CDAT

    # Background mode
    # 0 : everything is plotted directly (on the screen)
    # 1 : plot are made off-screen and only plotted on the screen (if need
    #     be) at the end of the script with 'x.showbg()'
    # Note: mode 1 is MUCH faster, but sometimes buggy...
    bg_type = 0 # bg mode 'on'
    #bg_type = 1 # bg mode 'off'

    # Dictionaries that will be used to store the manually and
    # automatically created templates, projections and graphic methods
    tpl_dic = {}
    proj_dic = {}
    gm_dic = {}
    select_dic={}

    # Get some data to plot
    #f = cdms.open('/home/motifdb/pmip2db/pmip2_21k_oa/atm/fixed/orog/orog_A_FX_pmip2_21k_oa_IPSL-CM4-V1-MR.nc')
    f = cdms.open('http://www-lscedods.cea.fr/cgi-bin/nph-dods/pmip2_dbext/pmip2_21k_oa/atm/fixed/orog/orog_A_FX_pmip2_21k_oa_IPSL-CM4-V1-MR.nc')
    orog_21k = f('orog')
    f.close()

    # Define the zones we want to plot (if not using the default full
    # NH and full SH)
    zones_dic={'NH':(30, 90, -180, 180),
               'SH':(-90, -30, -180, 180)}

    # Initialize vcs
    x = vcs.init()
    x.landscape()
    y = vcs.init()
    y.landscape()

    # Change the default continent line
    cont_line = x.getline('continents')
    cont_line.width = 1. # Get a thinner line than the default '2.0'

    # Create a basic boxfill method
    bf = x.createboxfill('pol_tst')
    bf.level_1 = -1000
    bf.level_2 = 5000
    bf.ext_2 = 'y'
    bf.legend = [-1000, 0, 1000, 2000, 3000, 4000, 5000]
    gm_dic['pol_tst'] = bf

    # Create the polar graphic and projection methods, and the
    # required selection zones
    print "User supplied graphic methods:", ', '.join(gm_dic.keys())
    print "User supplied zones:", ', '.join(zones_dic.keys())
    create_gm(x, zones=zones_dic,
              gm_d=gm_dic, proj_d=proj_dic, select_d=select_dic)
    print "Created graphic methods:", ', '.join(gm_dic.keys())
    print "Created polar projections:", ', '.join(proj_dic.keys())

    # Create the templates
    create_tpl_land(x, tpl_d=tpl_dic)
    print "Created templates", ', '.join(tpl_dic.keys())

    # Create the test plots
    x.plot(tpl_dic['tpl_l_left'],
           gm_dic['pol_tst_NH'],
           orog_21k(select_dic['NH']),
           comment1='Left plot',
           comment2='Northern hemisphere...',
           bg=bg_type)
    x.plot(tpl_dic['tpl_l_right'],
           gm_dic['pol_tst_SH'],
           orog_21k(select_dic['SH']),
           comment1='Right plot',
           comment2='Southern hemisphere...',
           bg=bg_type)
    if bg_type == 1:
        x.showbg()
    x.pdf('polargol_a', width=2*11, height=2*8)
    x.png('polargol_a')
    
    y.plot(tpl_dic['tpl_l_left'],
           gm_dic['pol_tst_NH'],
           orog_21k(select_dic['NH']),
           comment1='Left plot',
           comment2='Notice that right plot is slightly rotated...',
           bg=bg_type)
    # Change the projection a bit before plotting
    # (not very clean, but this is a test)
    proj_dic['p_north'].centerlongitude = -60
    y.plot(tpl_dic['tpl_l_right_nl'],
           gm_dic['pol_tst_NH'],
           orog_21k(select_dic['NH']),
           comment1='Right plot with no_legend template',
           comment2='Can be used to overlay isolines, etc...',
           bg=bg_type)

    #
    # Also plot a box around a zone, on the RIGHT figure
    # because we like challenges :-)
    #
    zone_box = x.createline('test_box')
    zone_box.projection = proj_dic['p_north']
    # Coordinates of the corners of the box (we have chosen to start
    # in the lower left corner and turn counter-clockwise
    zone_box.x = [0, 30, 30, 0, 0] # Longitudes
    zone_box.y = [45, 45, 75, 75, 45] # Latitudes
    # The lines have to be plotted in the same area of the canvas
    # as the polar graph in the RIGHT figure
    data_area = tpl_dic['tpl_l_right_nl'].data
    zone_box.viewport = [data_area.x1, data_area.x2,
                         data_area.y1, data_area.y2]
    # The box is plotted in the same area as the one specified
    # in the graphics methods
    gmz = gm_dic['pol_tst_NH']
    zone_box.worldcoordinate = [gmz.datawc_x1, gmz.datawc_x2,
                                gmz.datawc_y1, gmz.datawc_y2]
    # Make sure we see the zone!
    zone_box.width = [3.0]
    zone_box.color = [247] # Bright pink :)
    zone_box.type = ['dash'] # Default is 'solid'
    # Plot the zone at last
    y.plot(zone_box, bg=bg_type)
    
    if bg_type == 1:
        y.showbg()
    y.pdf('polargol_b', width=2*11, height=2*8)
    y.png('polargol_b')

    # Note: checking the created vcs objects after running the script
    # and staying in interactive mode ("python -i my_polar_script.py")
    # x.show('template')
    # x.show('projection')
    # x.show('boxfill')

# The end
