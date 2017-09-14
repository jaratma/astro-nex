# -*- coding: utf-8 -*-
from itertools import izip
from collections import deque
from math import sqrt,cos,sin,pi
PHI = 1 / ((1+sqrt(5))/2)
RAD = pi / 180

zodiac = None
planetmanager = None 

def dif(l,h):
    d = h - l
    if d < 0: d += 360.0
    return d

class Basic_Chart(object):
    R_INNER = 0.48 
    R_RULEDINNER = 0.65 
    R_RULEDOUTER = 0.78
    R_RULEDMID   = 0.84
    R_LINSET = 0.2 
    R_PL = R_INNER + (R_RULEDINNER - R_INNER)/2 
    pl_insets = { 'EXT': -0.03, 'INN': 0.09 }
    pl_line_width = { 'EXT': 0.85, 'INN': 0.55 }
    pl_radfac = { 'EXT': R_RULEDINNER , 'INN': R_INNER } 
    dx = [-1.3 ,-1.5,1.0,   0.5,2.0, 1.5,  0.5, -0.5, -1.5,   -1.5,-2.0,-1.7]
    dy = [  2 ,  2,   2,   1.5,  1, -0.5,  -1, -1.0,-1.2,   -1.1, 1.0, 1.5]
    scl = 0.0038
    plan_scale = 0.0024
    plan_factor = [0.93,1.07] 
    cusps_widths = (0.6,0.5,0.5)
    cuspfac = 1.14
    cusp_font_size = 16.0 
    cusp_line_width = 0.6
    click_col = None
    pe_col = (0.8,0,0.4) 
    zonecols = [(0.87,0.21,0.21),(0.97,0.94,0.51),(0.72,0.72,0.9),(0.34,0.77,0.41),(0.96,0.8,0.32),(0.83,0.5,0.51),(0.87,0.21,0.21)]
    pez_cols = {'paleblue': (0.8,1,1),'palegreen':(0.6,1,0.6), 
            'teal' :(0.3,0.6,0.8), 'darkgreen' :(0,0.95,0.4), 
            'pink' :(1,0.85,1), 'darkblue':(0.6,0.6,1) }

    def __init__(self,chart,click,plmanager=None):
        self.chart = chart
        self.click = click
        if plmanager:
            self.plmanager = plmanager
        else:
            self.plmanager = planetmanager
        self.zod = zodiac.zod
        self.name = self.get_name()

    def get_name(self):
        return 'basic'
   
    def get_sign_radfac(self):
        return self.R_RULEDINNER
    
    def get_cusp_radfac(self):
        return self.R_RULEDOUTER
    
    def swap_charts(self):
        self.chart, self.click = self.click ,self.chart

    def get_offset(self):
        '''Get degree of ascendant as constant offset.'''
        return self.chart.houses[0] % 30 

    def get_ascendant(self):
        '''Get de index of the ascendant sign.'''
        return int(self.chart.houses[0] / 30)
    
    def get_ruled(self):
        return (self.R_RULEDINNER, self.R_RULEDOUTER, 
                self.R_RULEDMID)

    def get_radial_param(self):
        return (self.R_RULEDINNER, self.R_LINSET,self.R_RULEDOUTER)

    def get_sign_cusps(self):
        '''Get iterator over sign offsets.'''
        offset = self.get_offset()
        return ((30*h - offset) for h in range(12))

    def get_planets(self):
        return self.chart.planets[:]

    def get_rpl(self):
        return self.R_PL

    def get_col(self):
        return self.click_col
    
    def check_moons(self):
        sun = self.chart.planets[0]
        moon = self.chart.planets[1] 
        diff = sun - moon
        if (diff < 0 and abs(diff) < 180) or (diff >= 0 and abs(diff) >= 180): 
            self.plmanager.swap_fmoon()
        else:
            self.plmanager.swap_bmoon()

    def get_plan_degrees(self):
        plans = []
        for pl in self.get_planets():
            plans.append(self.offsets_plan_degree(pl))
        return plans

    def basic_slopes(self):
        sizes = self.get_sizes()
        houses = self.get_houses_noiter()
        if self.name == 'basic':
            pr8 = -self.offsets_plan_degree(houses[7] + (sizes[7] * PHI))
            pr5 = -self.offsets_plan_degree(houses[4] + (sizes[4] * PHI))
            pr2 = -self.offsets_plan_degree(houses[1] + (sizes[1] * PHI))
        else: # node
            pr8 = 30 + 30 * PHI
            pr5 =  -(60 - 30 * PHI)
            pr2 = -(150 - 30 * PHI)
        slh8 = (sin(180*RAD) - sin(pr8*RAD)) / (cos(180*RAD) - cos(pr8*RAD))
        slh5 = (sin(180*RAD) - sin(pr5*RAD)) / (cos(180*RAD) - cos(pr5*RAD))
        slv2 = (sin(90*RAD) - sin(pr2*RAD)) / (cos(90*RAD) - cos(pr2*RAD))
        slv5 = (sin(90*RAD) - sin(pr5*RAD)) / (cos(90*RAD) - cos(pr5*RAD))
        return slh8,slh5,slv2,slv5

    def aspect_slope(self,p1,p2):
        return (sin(p1*RAD) - sin(p2*RAD)) / (cos(p1*RAD) - cos(p2*RAD))

    def slope_classify(self,aspects):
        pl = [-x for x in self.get_plan_degrees()]
        bslopes = self.basic_slopes()
        hor = [0]*12; ver = [0]*12; diag = [0]*12
        for a in aspects:
            sl = self.aspect_slope(pl[a.p1],pl[a.p2])
            if bslopes[0] >= sl >= bslopes[1]:
                hor[a.a] += 1
            elif bslopes[2] <= sl or sl <= bslopes[3]:
                ver[a.a] += 1
            else:
                diag[a.a] += 1
        class slope(object): pass
        slo = slope()
        slo.hr = hor[3]+hor[6]+hor[9]
        slo.vr = ver[3]+ver[6]+ver[9]
        slo.dr = diag[3]+diag[6]+diag[9]
        slo.hg = hor[1]+hor[5]+hor[7]+hor[11]
        slo.vg = ver[1]+ver[5]+ver[7]+ver[11]
        slo.dg = diag[1]+diag[5]+diag[7]+diag[11]
        slo.hb = hor[2]+hor[4]+hor[8]+hor[10]
        slo.vb = ver[2]+ver[4]+ver[8]+ver[10]
        slo.db = diag[2]+diag[4]+diag[8]+diag[10]
        return slo

    def inject_plan_degrees(self,shadow=False):
        jail = self.marshall_planets()
        plots = [None] * 11
        class plot_obj(object): pass
        for cell in jail:
            name = self.__class__.__name__
            num_plans = len(cell)
            fac = self.plan_factor[:]
            if shadow:
                fac = self.shadow_plan_factor[:]
            #fac.reverse()
            gen_corr = 6.5
            witness = self.joinsort(cell)
            for pos,pl in enumerate(witness):
                po = plot_obj()
                po.degree = self.offsets_plan_degree(pl[0])
                if num_plans < 2:
                    po.fac = 1.0
                else: 
                    po.fac = fac[0]
                    fac[0],fac[1] = fac[1],fac[0]
                if num_plans < 3:
                    po.corr = 0.0
                else: 
                    faraway = pos - (num_plans // 2)
                    if faraway < 0:
                        diff = dif(pl[0],witness[pos+1][0])
                    elif faraway > 0:
                        diff = dif(witness[pos-1][0],pl[0]) 
                        if diff >= 353.5: 
                            diff = -(diff - 353.5)
                            po.fac = fac[0] 
                    po.corr = self.correct_shift(-faraway * (6.5 - diff)/2.5) 
                if shadow:
                    plots[pl[1]] = po 
                    continue
                if name == "Plagram" and num_plans == 2:
                    po.fac = 1.0
                    diff = (witness[1][0] - witness[0][0]) % 360.0
                    if gen_corr < 0:
                        po.corr = (gen_corr + diff) / 1.8
                    else:
                        po.corr = (gen_corr - diff) / 1.8
                    gen_corr = -gen_corr
                plots[pl[1]] = po 
        return plots

    def joinsort(self,cell):
        witness = sorted(cell)
        lth = len(witness)
        if lth < 2:
            return witness
        ix = 0
        # reorder 2 358 to 358 2
        for pos in range(lth): 
             diff = dif(witness[pos][0],witness[(pos+1)%lth][0])
             if diff > 6.5:
                 ix = pos + 1
                 break
        return witness[ix:]+witness[:ix]

    def correct_shift(self,corr):
        '''Overridden in Nodal'''
        return corr

    def marshall_planets(self):
        '''Partition planets too close in groups'''
        def diftuple(tuple):
            d = tuple[1]['degree'] - tuple[0]['degree']
            if d < 0: d += 360
            return d <= 6.5
        
        plans = self.sortplan()
        planque = deque(plans) 
        boolque = deque([diftuple(t) for t in izip(plans,plans[1:]+[plans[0]])])
        if True in boolque:
            while boolque[0] != True or boolque[-1] != False:
                boolque.rotate(-1)
                planque.rotate(-1) 

        jail = []; cell = set()
        for low,btuple in izip(planque,boolque):
            cell.add((low['degree'],low['ix'])) 
            if btuple is False: 
                jail.append(cell)
                cell = set()
        return jail
    
    def sortplan(self): 
        pl = []
        for i,p in enumerate(self.get_planets()):
            pl.append( { 'degree': p, 'ix': i} )
        return sorted(pl)

    def get_zod_iter(self):
        '''Iterate over signs.'''
        return reversed(self.zod)

    def offsets_plan_degree(self,degree):
        '''Get offset for planet drawing.'''
        return (180 + self.chart.houses[0]) - degree

    def get_sign_offsets(self):
        '''Iterator for rotation angles.'''
        sign = self.get_ascendant() * 30 + self.get_offset() - 90
        return ((sign + 30*i + 15) for i in range(12))

    def get_sclx(self,scly):
        return scly
    
    def adjust_degpe(self,deg,chart): 
        return ((180+chart.houses[0]-deg)%360)

    def when_angle(self,cycles,angle,chart):
        return chart.when_angle(cycles,angle)

    def get_age_prog(self):
        plan = self.sortplan()
        return self.chart.calc_agep(plan) 

    def get_house_age_prog(self,h):
        plan = self.sortplan()
        return self.chart.calc_house_agep(plan,h) 


class ClickChart(Basic_Chart):
    R_INNER = Basic_Chart.R_INNER    
    R_RULEDINNER = 0.73
    R_RULEDOUTER = 0.95
    R_LINSET1 = 0.13 
    R_LINSET2 = 0.15 
    R_RULEDCLICK_MID = 0.84
    R_RULEDCLICK_INN = 0.73     #shared
    R_PL = R_INNER + 3*(R_RULEDINNER - R_INNER)/4
    R_PL_CLICK = R_INNER + (R_RULEDINNER - R_INNER)/4    
    
    dx = [ 0.5 , 1.5, 1.5, 0.5, 0,  -1, -1.5,-2.7,-2.7, -1.5, -1.3,-0.5]
    dy = [  2 ,  1,   0,  -0.5, -1, -1, -1,  0,   0.5, 1.5,  2,   2] 
    
    scl = 0.0024
    plan_factor = [0.95,1.05]
    plan_scale = 0.0021
    cusps_widths = (0.4,0.34,0.34)
   
    cuspfac = 1.52
    cusp_font_size = 20.0 
    cusp_line_width = 0.4   
    click_col = 'click1'
    click_col_other = 'click2'
    pl_radfac = { 'EXT': R_RULEDINNER , 'INN': Basic_Chart.R_INNER } 

    def prepare_params1(self):
        self.get_radial_param = self.get_radial_param1
        self.get_col = self.get_col1
        self.get_rpl = self.get_rpl1
        self.get_sign_radfac = self.get_sign_radfac1

    def prepare_params2(self):
        self.get_radial_param = self.get_radial_param2
        self.get_col = self.get_col2
        self.get_rpl = self.get_rpl2
        self.get_sign_radfac = self.get_sign_radfac2
    
    def get_radial_param1(self):
        return (self.R_RULEDCLICK_MID,self.R_LINSET1,self.R_RULEDOUTER)

    def get_radial_param2(self):
        return (self.R_RULEDCLICK_INN,self.R_LINSET2,self.R_RULEDOUTER)
    
    def get_cusp_radfac(self):
        return self.R_INNER 

    def get_rpl1(self):
        return self.R_PL

    def get_rpl2(self):
        return self.R_PL_CLICK

    def get_sign_radfac1(self):
        return self.R_RULEDCLICK_MID

    def get_sign_radfac2(self):
        return self.R_RULEDCLICK_INN
    
    def get_col1(self):
        return self.click_col
    
    def get_col2(self):
        return self.click_col_other 

    def get_cusps_offsets(self):
        return ((180 - 30*i) for i in range(12)) 

class UnequalHousesChart(object): 
    def get_sizes(self):
        return self.chart.sizes()

    def get_cusps_offsets(self):
        houses = self.chart.houses
        offset = 180 + houses[0]
        return ((offset - h) for h in iter(houses)) 

    def get_houses(self):
        return iter(self.chart.houses)

    def get_houses_noiter(self):
        return (self.chart.houses)
    
    def get_gold_offset(self):
        return 180 + self.chart.houses[0] 

    def get_golden_points(self):
        '''Iterator over low/inv proportions.'''
        for house,size in izip(self.get_houses(),self.get_sizes()):
            yield house,size*PHI, size*(1-PHI) 

class EqualHousesChart(object):
    def get_sizes(self):
        return [30.0]*12
    
    def get_cusps_offsets(self):
        return ((180 - 30*i) for i in range(12)) 
    
    def get_houses(self):
        return (30*i for i in range(12)) 
    
    def get_houses_noiter(self):
        return [30*i for i in range(12)] 
    
    
    def get_gold_offset(self):
        return 180

    def get_golden_points(self):
        '''Iterator over low/inv proportions.'''
        for house,size in izip(self.get_houses(),self.get_sizes()):
            yield house,size*PHI, size*(1-PHI) 

class RadixChart(Basic_Chart,UnequalHousesChart): 
    def get_cross_offset(self):
        return 180 + self.chart.houses[0] 

    def sup_cross(self,angle):
        return angle

class CounterChart(RadixChart): 
    def offsets_plan_degree(self,degree):
        '''Get offset for planet drawing.'''
        return (180 + self.click.houses[0]) - degree

class UrNodal(RadixChart):
    #R_INNER = 0.45 
    #R_RULEDINNER = 0.6 
    #R_RULEDOUTER = 0.78
    #R_RULEDMID   = 0.86

    def get_planets(self,click=False):
        return self.chart.urnodplan()
    
    def get_sign_radfac(self):
        return 0.61
    
    def get_nod_sign_offsets(self):
        node = self.chart.planets[10] % 30
        asc = self.chart.houses[0]
        sizes = self.chart.sizes()
        houses = self.chart.houses[:]
        factors = [s/30 for s in sizes]
        thish_part = node
        prevh_part = 30 - node
        offs = []; hh = []
        for m in range(0,360,30):
            d = m + 15.0
            h = self.chart.which_house_nodal(d)
            if node > 15.0:
                this_frac = thish_part*factors[h]
                prev_frac = prevh_part*factors[(h+11)%12]
                middle = (this_frac + prev_frac)/2 - prev_frac
                deg =  houses[h] + middle 
            else:
                prev_frac = prevh_part*factors[h]
                this_frac = thish_part*factors[(h+1)%12]
                middle = (this_frac + prev_frac)/2 - this_frac
                deg =  houses[(h+1)%12] - middle 
            off = (270  - (deg - asc)) % 360.0
            offs.append(off)
            midh = self.chart.which_house(deg)
            hh.append(midh)
        return offs,hh
    
    def get_nod_zod_iter(self):
        return iter(self.zod)    

class SoulChart(Basic_Chart,UnequalHousesChart):
    R_INNER = Basic_Chart.R_INNER
    R_RULEDINNER = Basic_Chart.R_RULEDINNER
    R_PL_CLICK = R_INNER + (R_RULEDINNER - R_INNER)/3.5 
    click_col_other = 'clicksoul'
    plan_click_scale = 0.0021
    plan_click_factor = [0.96,1.04]
    
    def get_name(self):
        return 'soul'
    
    def get_planets(self):
        return self.chart.soulplan()

    def set_clickvals(self):
        self.plan_scale = SoulChart.plan_click_scale
        self.plan_factor = SoulChart.plan_click_factor

    
class LocalChart(Basic_Chart,UnequalHousesChart):
    def adjust_degpe(self,deg,chart): 
        return ((180+chart.calc_localhouses()[0]-deg)%360)
    
    def when_angle(self,cycles,angle,chart):
        return chart.when_angle(cycles,angle,local=True)
    
    def get_age_prog(self):
        plan = self.sortplan()
        return self.chart.calc_agep(plan,local=True) 

    def get_house_age_prog(self,h):
        plan = self.sortplan()
        return self.chart.calc_house_agep(plan,h,local=True) 


#class DharmaChart(Basic_Chart,UnequalHousesChart): 
class DharmaChart(SoulChart): 
    def get_cross_offset(self):
        return 180 + self.chart.houses[0] 

    def sup_cross(self,angle):
        return angle
    
    def get_planets(self):
        return self.chart.house_plan_long()
    
    #def set_clickvals(self):
    #    self.plan_scale = SoulChart.plan_click_scale
    #    self.plan_factor = SoulChart.plan_click_factor

class HouseChart(Basic_Chart,EqualHousesChart):
    def get_offset(self):
        return 0.0
    
    def get_planets(self):
        return self.chart.house_plan_long()
    
    def get_sign_cusps(self):
        return self.chart.house_sign_long()
    
    def offsets_plan_degree(self,degree):
        return 180.0 - degree

    def get_sign_offsets(self):
        for long,size in izip(reversed(self.get_sign_cusps()),reversed(self.chart.sign_sizes())):
            off = 180 - long
            yield (off + (90 - size/2)) 
    
    def get_sclx(self,scly): 
        return scly * self.iter_sizes.next()/30

    def set_iter_sizes(self):
        self.iter_sizes = (size for size in reversed(self.chart.sign_sizes()))

class NodalChart(Basic_Chart,EqualHousesChart):
    pe_col = (0.4,0,0.8)
    
    def get_name(self):
        return 'nodal'
    
    def get_offset(self):
        return 30 - self.chart.planets[10] % 30
    
    def get_ascendant(self):
        return int(self.chart.planets[10]/30) 

    def get_planets(self,click=False):
        plans = self.chart.planets[:]
        plans[10] = self.chart.houses[0]
        if click:
            asc = self.chart.planets[10]
            tmp = [p - asc for p in plans]
            plans = [360 - (p + 360)%360 for p in tmp]
        return plans

    def get_cross_offset(self):
        return 180 + self.chart.planets[10] 

    def sup_cross(self,angle):
        return 360 - angle
    
    def correct_shift(self,corr):
        return -corr

    def offsets_plan_degree(self,degree):
        '''Get offset for planet drawing.'''
        return (180 - self.chart.planets[10]) + degree
    
    def get_zod_iter(self):
        return iter(self.zod)    

    def get_sign_offsets(self):
        sign = (11 - self.get_ascendant()) * 30 + self.get_offset() - 90
        return ((sign + 30*i + 15) for i in range(12))

    def adjust_degpe(self,deg,chart): 
        return ((180+chart.planets[10]+deg)%360)

    def when_angle(self,cycles,angle,chart):
        return chart.when_angle_nodal(cycles,angle)

    def get_age_prog(self):
        plan = self.sortplan()
        return self.chart.calc_nodal_agep(plan) 

    def get_house_age_prog(self,h):
        plan = self.sortplan()
        return self.chart.calc_house_nodal_agep(plan,h) 


class HouseHouseChart(ClickChart,HouseChart):
    pass

class NodalNodalChart(ClickChart,NodalChart):
    pass

class SoulHouseChart(ClickChart):
    def get_offset(self):
       return 0
    
    def get_ascendant(self):
        return 0

    def get_sign_cusps(self):
        return ((30*h) for h in range(12))
    
    def offsets_plan_degree(self,degree):
        '''Get offset for planet drawing.'''
        return 180 - degree

class SubjectClickChart(RadixChart):
    R_INNER = ClickChart.R_INNER *0.9
    R_RULEDINNER = 0.7
    R_RULEDOUTER = 0.82
    R_LINSET = 0.16 
    R_PL = R_INNER + 5.5*(R_RULEDINNER - R_INNER)/8
    R_PL_CLICK = R_INNER + (R_RULEDINNER - R_INNER)/3.5
    scl = 0.0028
    pl_radfac = { 'EXT': R_RULEDINNER , 'INN': R_INNER } 
    plan_scale = 0.002
    plan_factor = [0.95,1.05] 

    def set_inv_params(self):
        self.R_LINSET = 0.14
        self.R_RULEDINNER = 0.77

    def set_inv_funcs(self):
        self.temp_funcs = [self.get_planets,self.get_sign_cusps,self.get_sign_offsets,self.get_sclx]
        self.get_planets = self.subject_planets
        self.get_sign_cusps = self.invert_sign_cusps
        self.get_sign_offsets = self.subject_sign_offsets
        self.get_sclx = self.subject_sclx

    def restore_funcs(self):
        self.get_planets = self.temp_funcs[0]
        self.get_sign_cusps = self.temp_funcs[1]
        self.get_sign_offsets = self.temp_funcs[2]
        self.get_sclx = self.temp_funcs[3]
    
    def subject_planets(self):
        return self.chart.invert_house_plan(self.click.house_plan_long())

    def invert_sign_cusps(self):
        asc = self.chart.houses[0]
        invert = self.chart.invert_house_sign(self.click.house_sign_long())
        return [h - asc for h in invert]

    def subject_sign_offsets(self):
        for long,size in izip(reversed(self.get_sign_cusps()),reversed(self.subject_sizes())):
            off = 180 - long
            yield (off + (90 - size/2)) 
    
    def subject_sclx(self,scly): 
        return scly * self.iter_sizes.next()/30
    
    def set_iter_sizes(self):
        self.iter_sizes = (size for size in reversed(self.subject_sizes()))

    def subject_sizes(self):
        cusps = self.invert_sign_cusps()
        return self.chart.invert_sign_sizes(cusps)

class OneCircle(ClickChart):
    R_INNER = ClickChart.R_INNER
    R_RULEDINNER = 0.7
    R_RULEDOUTER = 0.82
    R_LINSET = 0.16 
    R_PL = R_INNER + 6*(R_RULEDINNER - R_INNER)/8
    R_PL_CLICK = R_INNER + (R_RULEDINNER - R_INNER)/3.5
    scl = 0.0032
    pl_radfac = { 'EXT': R_RULEDINNER , 'INN': R_INNER } 

    def offsets_plan_degree(self,degree):
        return  self.get_fixed_offset() - degree

    def get_fixed_offset(self):
        '''Hack - only want first offset'''
        try:
            self.fixed_offset
        except AttributeError:
            self.fixed_offset = 180 + self.chart.houses[0]
        return self.fixed_offset

class RadixRadixChart(OneCircle,RadixChart):
    R_INNER = 0.585 
    R_RULEDINNER = 0.7
    R_RULEDOUTER = 0.82
    cuspfac = 1.47
    click_col_other = 'clicksoul'
    get_cusps_offsets = RadixChart.get_cusps_offsets
    #pass

class RadixDharmaChart(OneCircle,RadixChart):
    #R_INNER = ClickChart.R_INNER
    R_INNER = 0.585 
    R_RULEDINNER = 0.7
    R_RULEDOUTER = 0.82
    cuspfac = 1.47
    click_col_other = 'clicksoul'
    get_cusps_offsets = RadixChart.get_cusps_offsets

class SoulSoulChart(OneCircle,SoulChart):
    click_col_other = 'clicksoul'


class TransitChart(OneCircle,RadixChart):
    click_col_other = 'transcol'
    click_col = None
    
    def get_rpl1(self):
        return self.R_PL_CLICK

    def get_rpl2(self):
        return self.R_PL

    def get_cusps_offsets(self):
        houses = self.chart.houses
        offset = 180 + houses[0]
        return ((offset - h) for h in iter(houses)) 

class Plagram(Basic_Chart,UnequalHousesChart): 
    R_INNER = 0.455
    R_RULEDINNER = 0.455 
    R_RULEDOUTER = 0.564
    R_LINSET = 0.12 
    rulecol = (0.4,0.4,0.4)
    pl_insets = { 'EXT': -0.03, 'INN': 0.055 }
    pl_radfac = { 'EXT': R_RULEDINNER , 'INN': R_INNER } 
    sign_fac = 1.005
    shadow_plan_factor = [0.99,1.01] 

    def get_name(self):
        return 'plagram'
    
    def get_cross_offset(self):
        return 180 + self.chart.houses[0] 

    def sup_cross(self,angle):
        return angle
    
    def get_ruled(self):
        return (self.R_RULEDINNER, self.R_RULEDOUTER)
    
    def get_radial_param(self):
        return (self.R_RULEDINNER, self.R_LINSET,self.R_RULEDOUTER)
    
    def get_cusps_offsets(self):
        houses = self.chart.houses
        offset = 180 + houses[0]
        return [(offset - h) for h in iter(houses)]
    
    def get_lowp_offsets(self):
        lp = self.chart.get_low_points()
        offset = 180 + self.chart.houses[0]
        return [(offset - h) for h in iter(lp)]

    def get_nod_sign_offsets(self):
        node = self.chart.planets[10] % 30
        asc = self.chart.houses[0]
        sizes = self.chart.sizes()
        houses = self.chart.houses[:]
        factors = [s/30 for s in sizes]
        thish_part = node
        prevh_part = 30 - node
        offs = []; hh = []
        for m in range(0,360,30):
            d = m + 15.0
            h = self.chart.which_house_nodal(d)
            if node > 15.0:
                this_frac = thish_part*factors[h]
                prev_frac = prevh_part*factors[(h+11)%12]
                middle = (this_frac + prev_frac)/2 - prev_frac
                deg =  houses[h] + middle 
            else:
                prev_frac = prevh_part*factors[h]
                this_frac = thish_part*factors[(h+1)%12]
                middle = (this_frac + prev_frac)/2 - this_frac
                deg =  houses[(h+1)%12] - middle 
            off = (270  - (deg - asc)) % 360.0
            offs.append(off)
            midh = self.chart.which_house(deg)
            hh.append(midh)
        return offs,hh
    
    def get_nod_zod_iter(self):
        return iter(self.zod)    
