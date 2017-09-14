# -*- coding: utf-8 -*-
import gtk,cairo
import math
from coredraw import CoreMixin
from progsheet import ProgMixin
from profchart import ProfileMixin
from biograph import BioMixin
from diagrams import DiagramMixin
from datasheets import SheetMixin
from paarwabe import PaarWabeMixin
from planetogram import PlanetogramMixin
import roundedcharts 
from aspects import AspectManager
from roundedcharts import *
from datetime import datetime, date, time
from .. boss import boss
curr = boss.get_state()

R_ASP = 0.435

onlyEA = False
showEA = False
showAP = None
AP_DEG = None

nottranslate = ['dat_nat','dat_house','dat_nod','prog_nat','prog_nod','prog_local','prog_soul','click_bridge',
        'bio_nat','bio_nod','bio_soul','bio_dharma','dyn_cuad','dyn_stars','dyn_cuad2','rad_and_transit','comp_pe']

class DrawMixin(CoreMixin,ProgMixin,ProfileMixin,BioMixin,DiagramMixin,SheetMixin,PaarWabeMixin,PlanetogramMixin):
    goodwill = False
    uniaspect = True
    allclick = False
    egoclick = False
    extended_canvas = False 
    pe_zones = False
    hzones = False
    ruline = None
    notwanted = []
    trdiscard = []
    restricted = [0,1,2,3,4]
    planetmanager = None
    surface = None
    must_restore = False

    def __init__(self,opts,surface=None):
        self.opts = opts
        self.surface = surface
        DrawMixin.surface = surface
        DrawMixin.planetmanager or self.set_plmanager()
        roundedcharts.planetmanager = DrawMixin.planetmanager 
        roundedcharts.zodiac= opts.zodiac
        self.aspmanager = AspectManager(boss,self.get_gw,self.get_uni,self.get_nw, DrawMixin.planetmanager,opts.zodiac.aspcolors,opts.base)
        CoreMixin.__init__(self,opts.zodiac,surface)
        ProgMixin.__init__(self,opts.zodiac)
        ProfileMixin.__init__(self,opts.zodiac,showEA)
        SheetMixin.__init__(self,opts.zodiac)
        BioMixin.__init__(self,opts.zodiac)
        DiagramMixin.__init__(self,opts.zodiac)
        PaarWabeMixin.__init__(self,opts.zodiac)
        #PlanetogramMixin.__init__(self,opts.zodiac)
        self.rightdraw = False
        self.trdiscard = opts.discard
    
    def set_plmanager(self):
        DrawMixin.planetmanager = PlanetManager(self.opts.zodiac)

    def make_crown(self,cr,radius,chartob):
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT')
        self.draw_cusps(cr,radius,chartob)
        self.d_year_lines(cr,radius,chartob)
        self.d_golden_points(cr,radius,chartob)

    def draw_nat(self,cr,width,height,chartob=None):
        chartob.__class__ = RadixChart 
        cx,cy = width/2,height/2
        radius = min(cx,cy)

        if not onlyEA:
            if self.pe_zones:
                self.d_pe_zones(cr,radius,chartob)
            if self.hzones:
                self.d_house_zones(cr,radius,chartob)
            self.make_crown(cr,radius,chartob)
            self.d_cross_points(cr,radius,chartob)
        else:
            self.set_plots(chartob)
            cr.scale(1.4,1.4)
            self.d_lonely_cusp(cr,radius,chartob)
        if showAP:
            self.draw_ap_aspects(cr,radius*R_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)
        if self.ruline:
            self.d_ruline(cr,chartob)

    def draw_nat_strict(self,cr,width,height,chartob=None):
        chartob.__class__ = RadixChart 
        cx,cy = width/2,height/2
        radius = min(cx,cy)

        self.make_crown(cr,radius,chartob)
        self.d_cross_points(cr,radius,chartob)
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)
    
    def subject_click(self,cr,width,height,chartob=None):
        cx,cy = width/2,height/2
        radius = min(cx,cy)

        RR_ASP = R_ASP * 0.8
        chartob.__class__ = SubjectClickChart
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT')
        self.draw_cusps(cr,radius,chartob)
        self.d_year_lines(cr,radius*1.05,chartob)
        self.d_golden_points(cr,radius*1.05,chartob) 
        self.d_cross_points(cr,radius,chartob)
        if showAP:
            self.draw_ap_aspects(cr,radius*RR_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        if not showEA:
            chartob.pl_insets['INN'] = 0.09
            self.aspmanager.manage_aspects(cr,radius*RR_ASP,chartob.get_planets())
        else:
            chartob.pl_insets['INN'] = -0.03
        self.make_plines(cr,radius*0.89,chartob,'INN')

        chartob.set_iter_sizes()
        chartob.scl = 0.002
        chartob.set_inv_funcs()
        self.draw_signs(cr,radius*0.68,chartob)
        self.d_subject_circles(cr,radius*0.63)
        chartob.set_inv_params()
        self.d_radial_lines(cr,radius*.61,chartob)
        self.draw_planets(cr,radius*0.7,chartob)
        if showEA:
            self.set_plots(chartob)
            chartob.pl_insets['INN'] = 0.09 
            self.aspmanager.manage_aspects(cr,radius*RR_ASP,chartob.get_planets())
        else:
            chartob.pl_insets['INN'] = -0.03
        self.make_plines(cr,radius*0.89,chartob,'INN')
        self.d_inner_circles(cr,radius*0.8)
        chartob.pl_insets['INN'] = 0.09 

    def draw_ur_nodal(self,cr,width,height,chartob=None):
        chartob.__class__ = UrNodal 
        cx,cy = width/2,height/2
        radius = min(cx,cy)

        self.d_urnod_radial_lines(cr,radius,chartob)
        self.make_all_urn_rulers(cr,radius,chartob)
        self.draw_urnod_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT')
        self.draw_cusps(cr,radius,chartob)
        self.d_year_lines(cr,radius,chartob)
        self.d_golden_points(cr,radius,chartob)
        self.d_cross_points(cr,radius,chartob)
        if showAP:
            self.draw_ap_aspects(cr,radius*R_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)
        if self.ruline:
            self.d_ruline(cr,chartob)

    def draw_house(self,cr,width,height,chartob=None):
        chartob.__class__ = HouseChart
        chartob.set_iter_sizes()
        cx,cy = width/2,height/2
        radius = min(cx,cy)
    
        if not onlyEA:
            self.make_crown(cr,radius,chartob)
            self.d_house_trimming(cr,radius,height)
        else:
            self.set_plots(chartob)
            cr.scale(1.4,1.4)
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)
    
    def draw_dharma(self,cr,width,height,chartob=None):
        chartob.__class__ = DharmaChart
        #chartob.set_iter_sizes()
        cx,cy = width/2,height/2
        radius = min(cx,cy)
    
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob)
        chartob.name = 'soul' 
        self.draw_signs(cr,radius,chartob)
        chartob.__class__ = DharmaChart
        
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT')
        
        self.draw_cusps(cr,radius,chartob)
        self.d_dharma_trimming(cr,radius,width,height,chartob)
        self.d_year_lines(cr,radius,chartob)
        self.d_golden_points(cr,radius,chartob)
        if self.ruline:
            self.d_ruline(cr,chartob)
        
        if showAP:
            self.draw_ap_aspects(cr,radius*R_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)

    def draw_soul(self,cr,width,height,chartob=None):
        chartob.__class__ = SoulChart 
        chartob.name = 'soul' 
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        if not onlyEA:
            self.make_crown(cr,radius,chartob)
        else:
            self.set_plots(chartob)
            cr.scale(1.4,1.4)
            self.d_lonely_cusp(cr,radius,chartob)
        if showAP:
            self.draw_ap_aspects(cr,radius*R_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)
        if self.ruline:
            self.d_ruline(cr,chartob)
    
    def draw_local(self,cr,width,height,chartob=None):
        chartob.__class__ = LocalChart 
        chart = chartob.chart
        oldhouses = chart.houses[:]
        chart.houses = chart.calc_localhouses()
        cx,cy = width/2,height/2
        radius = min(cx,cy)

        if not onlyEA:
            self.make_crown(cr,radius,chartob)
            self.d_local_trimming(cr,radius*0.78 ,chartob)
        else:
            self.set_plots(chartob)
            cr.scale(1.4,1.4)
            self.d_lonely_cusp(cr,radius,chartob)
        if showAP:
            self.draw_ap_aspects(cr,radius*R_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)
        chart.houses = oldhouses[:]
    
    def draw_nod(self,cr,width,height,chartob=None):
        chartob.__class__ = NodalChart
        chartob.name = 'nodal' 
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        if not onlyEA:
            if self.pe_zones:
                self.d_pe_zones(cr,radius,chartob)
            self.make_crown(cr,radius,chartob)
            self.d_cross_points(cr,radius,chartob)
        else:
            self.set_plots(chartob)
            cr.scale(1.4,1.4)
        if showAP:
            self.draw_ap_aspects(cr,radius*R_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)
        if self.ruline:
            self.d_ruline(cr,chartob)
    
    def click_counter(self,cr,width,height,chartob):
        chartob.__class__ = CounterChart 
        cx,cy = width/2,height/2
        radius = min(cx,cy)

        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_cusps(cr,radius,chartob)
        self.d_year_lines(cr,radius,chartob)
        self.d_golden_points(cr,radius,chartob)
        self.d_cross_points(cr,radius,chartob)
        
        chartob.swap_charts()
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT')
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)

    def click_counterpanel(self,cr,width,height,chartob):
        female = chartob.chart.first
        if chartob.chart.last:
            female += " "+ chartob.chart.last
        male = chartob.click.first
        if chartob.click.last:
            male += " "+ chartob.click.last
        dates = boss.search_couple(female,male)
        if dates:
            onlydates = [ d[0] for d in dates]
            she_col = (0.72,0.58,0) 
            he_col = (0.74,0.42,0.85) 
            coup_dts1 = []; coup_dts2 = []
            for d in onlydates:
                dt = [ int(x) for x in d.split("/") ]
                dt = date(dt[2],dt[1],dt[0])
                dt = datetime.combine(dt,time())
                chart = chartob.chart
                cycles = chart.get_cycles(dt)
                coup_dts1.append(chart.which_degree_today(dt,cycles,chartob.name))
                chart = chartob.click
                cycles = chart.get_cycles(dt)
                coup_dts2.append(chart.which_degree_today(dt,cycles,chartob.name))
        
        cx,cy = width/2,height/2 
        curr.opmode = 'double'
        cr.translate(-cx/2,-cy/2)
        self.draw_nat_strict(cr,cx,cy,chartob)
        if dates:
            chart = chartob.chart
            self.d_coup_dates(cr,cx,cy,chart,she_col,coup_dts1) 
        cr.translate(cx,cy)
        self.click_counter(cr,cx,cy,chartob)
        if dates:
            self.d_coup_dates(cr,cx,cy,chart,she_col,coup_dts1) 
        cr.translate(0,-cy)
        self.draw_nat_strict(cr,cx,cy,chartob)
        if dates:
            chart = chartob.chart
            self.d_coup_dates(cr,cx,cy,chart,he_col,coup_dts2) 
        cr.translate(-cx,cy)
        self.click_counter(cr,cx,cy,chartob)
        if dates:
            self.d_coup_dates(cr,cx,cy,chart,he_col,coup_dts2) 
        cr.translate(-cx/2,0)
        curr.opmode = 'simple'
        
    def click_hh(self,cr,width,height,chartob=None):
        cx,cy = width/2,height/2
        radius = min(cx,cy)*0.9

        chartob.__class__ = HouseHouseChart
        chartob.set_iter_sizes()
        chartob.prepare_params1()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        chartob.swap_charts()
        chartob.set_iter_sizes()
        chartob.prepare_params2()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob,plot='plot2')
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        plan2 = chartob.get_planets()
        chartob.swap_charts()
        
        self.make_all_rulers(cr,radius,chartob,mid=True)
        self.draw_cusps(cr,radius,chartob) 
        
        flt = 'click' if not self.egoclick else 'pers' 
        flt = flt if not self.allclick else None 
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter=flt)
        self.d_inner_circles(cr,radius)

    def click_nn(self,cr,width,height,chartob=None):
        cx,cy = width/2,height/2
        radius = min(cx,cy)*0.9
        
        chartob.__class__ = NodalNodalChart
        chartob.name = 'nodal' 
        chartob.prepare_params1()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets(True)
        chartob.swap_charts()
        chartob.prepare_params2()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob,plot='plot2')
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        plan2 = chartob.get_planets(True)
        chartob.swap_charts()
        
        self.make_all_rulers(cr,radius,chartob,mid=True) 
        self.draw_cusps(cr,radius,chartob) 
        flt = 'click' if not self.egoclick else 'pers' 
        flt = flt if not self.allclick else None 
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter=flt)
        self.d_inner_circles(cr,radius)

    def draw_transits(self,cr,width,height,chartob=None):
        chartob.click  = curr.charts['now']
        
        chartob.__class__ = TransitChart
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob) 
        self.draw_signs(cr,radius,chartob)
        self.draw_cusps(cr,radius,chartob,transit=True)
        
        chartob.prepare_params1()
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        
        chartob.swap_charts()
        chartob.prepare_params2()
        self.draw_planets(cr,radius,chartob,plot='plot2')
        plan2 = chartob.get_planets()
        chartob.swap_charts()
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        if showEA:
            target = cr.get_target()
            over = target.create_similar(cairo.CONTENT_COLOR_ALPHA,width,height)
            over_cr = cairo.Context(over)
            over_cr.translate(cx,cy)
            self.aspmanager.manage_aspects(over_cr,radius*R_ASP,plan1)
            cr.set_source_surface(over,-cx,-cy)
            cr.paint_with_alpha(0.5)
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter='transit')
        self.d_inner_circles(cr,radius)
        if self.ruline:
            self.d_ruline(cr,chartob)
        
    def draw_radsoul(self,cr,width,height,chartob=None):
        chartob.click = chartob.chart
        
        chartob.__class__ = RadixRadixChart
        chartob.name = 'soul' 
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob) 
        self.draw_signs(cr,radius,chartob)
        #self.draw_double_cusp(cr,radius*0.82,chartob)
        self.draw_cusps(cr,radius*0.82,chartob)
        
        chartob.prepare_params1()
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        
        chartob.swap_charts()
        chartob.prepare_params2()
        chartob.__class__ = SoulChart
        plan2 = chartob.get_planets()
        chartob.set_clickvals()
        self.draw_planets(cr,radius,chartob,plot='plot2')
        chartob.__class__ = RadixRadixChart
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        chartob.swap_charts()
        
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter='click')
        self.d_inner_circles(cr,radius)
        
    def draw_raddharma(self,cr,width,height,chartob=None):
        chartob.click = chartob.chart
        
        chartob.__class__ = RadixDharmaChart
        chartob.name = 'soul' 
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob) 
        self.draw_signs(cr,radius,chartob)
        #self.draw_double_cusp(cr,radius*0.82,chartob)
        self.draw_cusps(cr,radius*0.82,chartob)
        
        chartob.prepare_params1()
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        
        chartob.swap_charts()
        chartob.prepare_params2()
        chartob.__class__ = DharmaChart
        plan2 = chartob.get_planets()
        chartob.set_clickvals()
        self.draw_planets(cr,radius,chartob,plot='plot2')
        chartob.__class__ = RadixRadixChart
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        chartob.swap_charts()
        
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter='click')
        self.d_inner_circles(cr,radius)

    def click_rr(self,cr,width,height,chartob=None):
        chartob.__class__ = RadixRadixChart
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob) 
        self.draw_signs(cr,radius,chartob)
        self.draw_double_cusp(cr,radius*0.82,chartob)
        
        chartob.prepare_params1()
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        
        chartob.swap_charts()
        chartob.prepare_params2()
        self.draw_planets(cr,radius,chartob,plot='plot2')
        plan2 = chartob.get_planets()
        chartob.swap_charts()
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        flt = 'click' if not self.egoclick else 'pers' 
        flt = flt if not self.allclick else None 
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter=flt)
        self.d_inner_circles(cr,radius)

    def click_ss(self,cr,width,height,chartob=None):
        chartob.__class__ = SoulSoulChart
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        chartob.name = 'soul' 
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob) 
        self.draw_signs(cr,radius,chartob)
        self.draw_double_cusp(cr,radius*0.82,chartob)
        
        chartob.prepare_params1()
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        
        chartob.swap_charts()
        chartob.prepare_params2()
        self.draw_planets(cr,radius,chartob,plot='plot2')
        plan2 = chartob.get_planets()
        chartob.swap_charts()
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        flt = 'click' if not self.egoclick else 'pers' 
        flt = flt if not self.allclick else None 
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter=flt)
        self.d_inner_circles(cr,radius)

    def click_rs(self,cr,width,height,chartob=None):
        chartob.__class__ = RadixRadixChart
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        chartob.name = 'radsoul' 
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob) 
        self.draw_signs(cr,radius,chartob)
        self.draw_double_cusp(cr,radius*0.82,chartob)
        
        chartob.prepare_params1()
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        
        chartob.__class__ = SoulSoulChart
        chartob.swap_charts()
        chartob.prepare_params2()
        self.draw_planets(cr,radius,chartob,plot='plot2')
        plan2 = chartob.get_planets()
        chartob.swap_charts()
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        flt = 'click' if not self.egoclick else 'pers' 
        flt = flt if not self.allclick else None 
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter=flt)
        self.d_inner_circles(cr,radius)
    
    def click_bridge(self,cr,width,height,chartob):
        cx,cy = width/2,height/2 
        curr.opmode = 'double'
        cr.translate(cx/2,cy)
        cr.scale(1.15,1.15)
        self.click_hn(cr,width/2,height,chartob,filter='bridge')
        cr.scale(1/1.15,1/1.15)
        cr.translate(cx,0)
        cr.scale(1.15,1.15)
        self.click_nh(cr,width/2,height,chartob,filter='bridge')
        cr.scale(1/1.15,1/1.15)
        cr.translate(-cx/2,0)
        curr.opmode = 'simple'

    def rad_and_transit(self,cr,width,height,chartob):
        cx,cy = width/2,height/2 
        curr.opmode = 'double'
        cr.translate(cx/2,cy)
        cr.scale(1.15,1.15)
        self.draw_nat(cr,width/2,height,chartob)
        cr.scale(1/1.15,1/1.15)
        cr.translate(cx,0)
        cr.scale(1.15,1.15)
        self.draw_transits(cr,width/2,height,chartob)
        cr.scale(1/1.15,1/1.15)
        cr.translate(-cx/2,0)
        curr.opmode = 'simple'
    
    def draw_single(self,cr,w,h,chartob):
        chartob.click = chartob.chart
        self.click_hn(cr,w,h,chartob,filter='single')
    
    def draw_int(self,cr,w,h,chartob):
        chartob.click = chartob.chart
        self.click_hn(cr,w,h,chartob,filter='int')
    
    def click_hn(self,cr,width,height,chartob,filter='click'):
        cx,cy = width/2,height/2
        radius = min(cx,cy)*0.9
        
        chartob.__class__ = HouseHouseChart
        chartob.set_iter_sizes()
        chartob.prepare_params1()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        chartob.__class__ = NodalNodalChart
        chartob.name = 'nodal' 
        chartob.swap_charts()
        chartob.prepare_params2()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob,plot='plot2')
        self.draw_planets(cr,radius,chartob,plot='plot2')
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        plan2 = chartob.get_planets(True)
        chartob.swap_charts()
        
        self.make_all_rulers(cr,radius,chartob,mid=True)
        self.draw_cusps(cr,radius,chartob)
        
        if filter == 'int': 
            flt = filter
        elif filter == 'click':
            flt = 'click' if not self.egoclick else 'pers' 
            flt = flt if not self.allclick else None 
        else:
            flt = 'click'

        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,flt)
        self.d_inner_circles(cr,radius)
    
    def click_nh(self,cr,width,height,chartob,filter='click'):
        cx,cy = width/2,height/2
        radius = min(cx,cy)*0.9
        
        chartob.__class__ = NodalNodalChart
        chartob.name = 'nodal' 
        chartob.prepare_params1()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets(True)
        chartob.__class__ = HouseHouseChart
        chartob.name = 'basic' 
        chartob.set_iter_sizes()
        chartob.swap_charts()
        chartob.prepare_params2()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob,plot='plot2')
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        plan2 = chartob.get_planets()
        chartob.swap_charts()
        
        self.make_all_rulers(cr,radius,chartob,mid=True)
        self.draw_cusps(cr,radius,chartob)

        if filter == 'click':
            flt = 'click' if not self.egoclick else 'pers' 
            flt = flt if not self.allclick else None 
        else:
            flt = 'click'
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,filter=flt)
        self.d_inner_circles(cr,radius)
    
    def click_sn(self,cr,width,height,chartob,filter='click'):
        cx,cy = width/2,height/2
        radius = min(cx,cy)*0.9
        
        chartob.__class__ = SoulHouseChart
        chartob.name = 'soul' 
        chartob.prepare_params1()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT',plot='plot1')
        self.make_plines(cr,radius,chartob,'INN',plot='plot1')
        plan1 = chartob.get_planets()
        chartob.__class__ = NodalNodalChart
        chartob.name = 'nodal' 
        chartob.swap_charts()
        chartob.prepare_params2()
        self.d_radial_lines(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob,plot='plot2')
        self.draw_planets(cr,radius,chartob,plot='plot2')
        self.make_plines(cr,radius,chartob,'EXT',plot='plot2')
        self.make_plines(cr,radius,chartob,'INN',plot='plot2')
        plan2 = chartob.get_planets(True)
        chartob.swap_charts()
        
        self.make_all_rulers(cr,radius,chartob,mid=True)
        self.draw_cusps(cr,radius,chartob)
        flt = 'click' if not self.egoclick else 'pers' 
        flt = flt if not self.allclick else None 
        self.aspmanager.manage_aspects(cr,radius*R_ASP,plan1,plan2,flt)
        self.d_inner_circles(cr,radius)

    def solar_rev(self,cr,width,height,chartob=None):
        boss.solar_rev()
        self.draw_nat(cr,width,height,chartob)

    def sec_prog(self,cr,width,height,chartob=None):
        boss.sec_prog()
        chartob.chart = curr.calc
        self.draw_nat(cr,width,height,chartob)

    def dispatch_pres(self,cr,w,h):
        chart_one, chart_two = curr.curr_chart, curr.curr_click
        currop = curr.curr_op
        if curr.opmode == 'simple':
            if curr.curr_op not in nottranslate:
                cr.translate(w/2,h/2)
            if currop == 'solar_rev':
                chart_one = curr.now
            chartobject = Basic_Chart(chart_one, chart_two)
            getattr(self,currop)(cr,w,h,chartobject)
        elif curr.opmode == 'double':
            scl = 1.05
            cx,cy = w/2,h/2
            cr.translate(cx/2,cy)
            cr.scale(scl,scl)
            chartobject = Basic_Chart(chart_one,chart_two)
            cr.save()
            getattr(self,curr.opleft)(cr,w/2,h,chartobject)
            cr.restore()
            cr.scale(1/scl,1/scl)
            cr.translate(cx,0)
            cr.scale(scl,scl)
            if curr.clickmode == 'master': 
                chartobject = Basic_Chart(chart_one,chart_two)
            else: 
                chartobject = Basic_Chart(chart_two,chart_one)
            self.rightdraw = True
            getattr(self,curr.opright)(cr,w/2,h,chartobject)
            self.rightdraw = False
            cr.scale(1/scl,1/scl)
        elif curr.opmode == 'triple':
            scl = 1.08
            cx,cy = w/2,h/2
            cr.translate(cx/2,3*cy/2-8)
            cr.scale(scl,scl)
            chartobject = Basic_Chart(chart_one,chart_two)
            cr.save()
            getattr(self,curr.opleft)(cr,w/2,h/2,chartobject)
            cr.restore()
            cr.scale(1/scl,1/scl)
            cr.translate(cx,0)
            cr.scale(scl,scl)
            if curr.clickmode == 'master': 
                chartobject = Basic_Chart(chart_one,chart_two)
            else: 
                chartobject = Basic_Chart(chart_two,chart_one)
            cr.save()
            getattr(self,curr.opright)(cr,w/2,h/2,chartobject)
            cr.restore()
            cr.scale(1/scl,1/scl)
            cr.translate(-cx/2,-cy+20)
            cr.scale(scl,scl)
            chartobject = Basic_Chart(chart_one,chart_two)
            getattr(self,curr.opup)(cr,w/2,h/2,chartobject)
            cr.scale(1/scl,1/scl)

    def dispatch_simple(self,cr,w,h,op,ch1,ch2):
        if op == 'solar_rev':
            ch1 = curr.now
        if not op.startswith('dyn') and not op.startswith('bio') and op != 'comp_pe':  
            cr.translate(w/2,h/2)
        chartobject = Basic_Chart(ch1, ch2)
        if op.startswith('dyn'):
            cr.translate(w*0.1,h*0.1) 
            getattr(self,op)(cr,int(w*0.8),int(h*0.8),chartobject)
            cr.translate(-w*0.1,-h*0.1) 
        else:
            getattr(self,op)(cr,w,h,chartobject)

    def get_gw(self):
        return self.goodwill
    
    def get_uni(self):
        return self.uniaspect
    
    def get_nw(self,filter=None):
        if hasattr(self.surface,"opaux"):
            op = self.surface.opaux[0]
        else:
            op = curr.curr_op
        if op in ['draw_nat','draw_house','draw_nod','draw_soul','draw_local']:
            return self.notwanted
        elif op  in ['draw_transits','rad_and_transit']:
            if  not filter:
                return []
            if boss.da.plselector:
                return self.notwanted 
            else:
                return self.trdiscard
        else:
            return []
    
    @staticmethod
    def set_showAP(ap):
        global showAP
        showAP = ap

    @staticmethod
    def get_showEA():
        return showEA

    @staticmethod
    def get_chartob(for_op):
        chartob = Basic_Chart(curr.curr_chart,curr.curr_click)
        if for_op == 'draw_nod':
            chartob.__class__ = NodalChart
            chartob.name = 'nodal'
        elif for_op == 'draw_local':
            chartob.__class__ = LocalChart
            chartob.name = 'local'
        return chartob

    @classmethod
    def set_AP(dispatcher,ap,for_op,for_ch):
        global AP_DEG
        chartob = dispatcher.get_chartob(for_op) 
        chart = {'chart':chartob.chart,'click':chartob.click}[for_ch]
        cycles = chart.get_cycles(curr.date.dt)
        ap = chartob.adjust_degpe(ap,chart) 
        AP_DEG = ap
        dt = chartob.when_angle(cycles,ap,chart)
        boss.da.panel.set_date(dt)

    @classmethod
    def set_op_AP(dispatcher,for_op,state):
        global AP_DEG
        if not state & gtk.gdk.CONTROL_MASK:
            am = 180
        else:
            am = [1,-1][state & gtk.gdk.SHIFT_MASK] * 30
        ap = (AP_DEG + am) % 360
        AP_DEG = ap
        chartob = dispatcher.get_chartob(for_op) 
        chart = chartob.chart
        cycles = chart.get_cycles(curr.date.dt)
        dt = chartob.when_angle(cycles,ap,chart)
        boss.da.panel.set_date(dt)

    @classmethod
    def get_AP(dispatcher,chartob):
        global AP_DEG
        dt = curr.date.dt
        dt = datetime.combine(dt.date(),dt.time())
        chart = chartob.chart
        cycles = chart.get_cycles(dt)
        pe = chart.which_degree_today(dt,cycles,chartob.name)
        AP_DEG = pe
        try:
            if dispatcher.surface.bridge:
                dispatcher.surface.redraw_auxwins(True)
        except AttributeError:
            pass
        return pe

    @staticmethod
    def get_showAP():
        return showAP

    @staticmethod
    def get_AP_DEG():
        global AP_DEG
        return AP_DEG 
    
    @staticmethod
    def set_AP_DEG(ap=None):
        global AP_DEG
        AP_DEG = ap if ap else curr.now.houses[0]
    
    @staticmethod
    def set_onlyEA(ea):
        global onlyEA
        onlyEA = ea

    @staticmethod
    def get_onlyEA():
        return onlyEA
    
    @staticmethod
    def set_showEA(ea):
        global showEA
        showEA = ProfileMixin.showEA = ea

class PlanetManager(object):
    def __init__(self,zodiac): 
        self.glyphs = zodiac.plan[:]
        self.moon_f = self.glyphs[1]
        self.moon_b = self.glyphs.pop()

    def swap_fmoon(self):
        self.glyphs[1] = self.moon_f
    
    def swap_bmoon(self):
        self.glyphs[1] = self.moon_b 
