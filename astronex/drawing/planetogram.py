# -*- coding: utf-8 -*-
import sys
import cairo, pango
import math
from math import pi as PI
from itertools import cycle, izip
from bisect import bisect_left
from .. boss import boss
from roundedcharts import Plagram, SoulChart, NodalChart
from .. extensions import euclid as eu
from .. extensions.color_conv import Rgb2Hsl,Hsl2Rgb
curr = boss.get_state()

aspcol = None
R_VERYINNER = 0.065
R_INNER = 0.48     #shared
R_ASP = 0.431
SIGN_OUTER = 0.51
NODAL_OUTER = 0.565
KAUSAL_OUTER = 0.635
PE_OUTER = 0.655
HCIRCLES_BEGIN = 0.605
hcfac = 8.0
H_1 = HCIRCLES_BEGIN * (1.03 + 0.01 * hcfac)
H_2 = HCIRCLES_BEGIN * (1.03 + 0.02 * hcfac)
H_3 = HCIRCLES_BEGIN * (1.03 + 0.03 * hcfac)
H_4 = HCIRCLES_BEGIN * (1.03 + 0.04 * hcfac)
H_5 = HCIRCLES_BEGIN * (1.03 + 0.05 * hcfac)
H_6 = HCIRCLES_BEGIN * (1.03 + 0.06 * hcfac)
HC = [H_1,H_2,H_3,H_4,H_5,H_6]

house_circles = [(6,3),(4,1),(6,3),(4,1),(5,2),(5,2),(6,3),(4,1),(6,3),(5,2),(5,2),(6,3)]
MAGICK_SECT_1 = 0.66744 # 0.4125
MAGICK_SECT_2 = 0.74583
MAGICK_SECT_3 = 0.96667


extend = 1.052

RAD = PI /180
PHI = 1 / ((1+math.sqrt(5))/2)
MAGICK_FONTSCALE=0.002

plagramcol = [ 
        (0,0.39,0.625),
        (0.96, 0.7, 0.02),
        (0.625,0.23,0.08),
        (1.0,0.39,0) ]
magenta = [(1,0,1),(1,0.78,1)] # [pure, dilued]
violet = [(0.43,0,0.78), (0.78,0.7,1)] # 	(tramado  200,180,255)
yellow = (1.0,0.95,0.2)
cream = (0.97,1.0,0.97)
cross_cols = [(0.8,0,0),(0,0,0.8),(0,0.6,0)]
cross_cols_1 = [(0.7,0,0),(0.0,0.0,0.8),(0,0.6,0)]
cross_cols_2 = [(1.0,0.2,0.3),(0.3,0.3,1.0),(0,0.8,0)]
bar_cols = [(1.0,0.6,1.0),(0,1.0,1.0),(0.6,1.6,0)]
orange =  (1.0,0.55,0)

pla_cols = {}
pla_cols['d'] = pla_cols['k'] = pla_cols['c'] = (0.95,0,0.2) 
pla_cols['f'] = pla_cols['h'] = pla_cols['l'] = pla_cols['x'] = pla_cols['b'] = (0,0.85,0)
pla_cols['j'] = pla_cols['g'] = pla_cols['z'] = (0.2,0.2,1.0)
pla_cols['v'] = (0.5,0.5,0.5)

let_keys = {'d':'r','k':'r','c':'r','f':'g','b':'g','h':'g','l':'g','x':'g','j':'b','g':'b','z':'b','v':'n'} 
mod_keys = ['r','b','g']
keys_col = {
        'rgr': { 'p':(0.9,0.0,0.0), 'z':(0.3,0.9,0.3), 'h':(0.9,0.2,0.2) },
        'rbb': { 'p':(1.0,0.0,0.0), 'z':(0.2,0.5,1.0), 'h':(0.0,0.0,0.75) },
        'rgb': { 'p':(0.9,0.0,0.0), 'z':(0.0,0.85,0.0), 'h':(0.0,0.0,0.95) },
        'rbr': { 'p':(0.9,0.0,0.0), 'z':(0.3,0.3,1.0), 'h':(1.0,0.1,0.1) },

        'gbg': { 'p':(0.0,0.85,0.0), 'z':(0.2,0.2,1.0), 'h':(0.0,0.95,0.0) },
        'gbb': { 'p':(0.0,0.9,0.0), 'z':(0.4,0.4,1.0), 'h': (0.0,0.1,0.8)},
        'gbr': { 'p':(0.0,0.9,0.0), 'z':(0.0,0,1.0), 'h':(1.0,0,0.2) },
        'grb': { 'p':(0.0,0.9,0.0), 'z':(1.0,0.3,0.3), 'h':(0.0,0,1.0) },
        'grr': { 'p':(0.0,1.0,0.0), 'z':(0.8,0.1,0.0), 'h':(1.0,0,0.0) },
        'grg': { 'p':(0.0,1.0,0.0), 'z':(1.0,0.2,0.2), 'h':(0.0,0.75,0.0) },
        'ggb': { 'p':(0.0,0.8,0.0), 'z':(0.1,1.0,0.1), 'h':(0.1,0.1,1.0) },
        'ggr': { 'p':(0.0,1.0,0.0), 'z':(0.0,0.7,0.0), 'h':(0.9,0.1,0.1) },
        'ggg': { 'p':(0.0,1.0,0.0), 'z':(0.0,0.7,0.0), 'h':(0.0,0.9,0.0) },

        'bbg': { 'p':(0.0,0.0,0.8), 'z':(0.5,0.5,1.0), 'h':(0,0.85,0) },
        'bbr': { 'p':(0.0,0.0,0.8), 'z':(0.3,0.3,1.0), 'h':(1,0.1,0.1) },
        'bbb': { 'p':(0.0,0.0,0.8), 'z':(0.4,0.5,1.0), 'h':(0.2,0.3,1.0) },
        'brr': { 'p':(0.0,0.0,0.8), 'z':(1.0,0.4,0.4), 'h':(0.8,0.0,0.0) },
        'brg': { 'p':(0.0,0.0,0.8), 'z':(1.0,0.4,0.4), 'h':(0.0,0.8,0.0) },
        'brb': { 'p':(0.0,0.0,1.0), 'z':(1.0,0.1,0.1), 'h':(0.0,0.2,1.0) },
        'bgb': { 'p':(0.0,0.0,0.8), 'z':(0.0,0.8,0.0), 'h':(0,0.2,1) },
        'bgg': { 'p':(0.0,0.0,0.8), 'z':(0.0,0.65,0.0), 'h':(0,0.85,0) },
        'bgr': { 'p':(0.0,0.0,0.8), 'z':(0.0,0.75,0.0), 'h':(1,0.0,0.1) },

        'ngb': { 'p':(0.5,0.5,0.5), 'z':(0.0,0.8,0.0), 'h':(0.1,0.1,1.0) },
        'nbg': { 'p':(0.5,0.5,0.5), 'z':(0.0,0.0,1.0), 'h':(0.0,0.7,0.0) },
        'ngr': { 'p':(0.6,0.6,0.6), 'z':(0.2,0.9,0.0), 'h':(1.0,0.3,0.2) },
        'nrg': { 'p':(0.6,0.6,0.6), 'z':(1.0,0.0,0.2), 'h':(0.0,0.8,0.0) },
        'nrb': { 'p':(0.6,0.6,0.6), 'z':(1.0,0.1,0.1), 'h':(0.0,0.0,1.0) },
        }

zcusps = []
zlowps = []

def rebuild_paths(cr,paths):
    dispatch = { cairo.PATH_MOVE_TO: 'move_to',cairo.PATH_LINE_TO:'line_to',
                cairo.PATH_CURVE_TO:'curve_to', cairo.PATH_CLOSE_PATH:'close_path'} 
    for type, points in paths:
        getattr(cr,dispatch[type])(*points)

class PlanetogramMixin(object):

    def __init__(self,zodiac):
        global aspcol
        aspcol = zodiac.get_aspcolors() 
        self.zod = zodiac.zod[:]
        self.plagram_plan = zodiac.plagram[:]
        self.plextra = zodiac.plagram_extra[:]
        self.moon_f = self.plagram_plan[1]
        self.moon_b = self.plagram_plan.pop()
        self.plagramcol = plagramcol

    def draw_planetogram(self,cr,width,height,chartob):
        chartob.__class__ = Plagram 
        chartob.name = chartob.get_name()
        cx,cy = width/2,height/2
        radius = min(cx,cy)

        self.set_plots(chartob)
        self.set_zone_cusps(radius,chartob)
        self.draw_plagram_cusps(cr,radius,chartob)
        self.d_plan_arrows(cr,radius,chartob)
        self.pla_magick_circles(cr,radius)
        self.draw_signs(cr,radius,chartob)
        self.d_radial_lines(cr,radius,chartob)
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets(),extend=extend)
        self.make_plagram_rulers(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'INN')
        self.d_nod_radial_lines(cr,radius,chartob)
        self.draw_nod_signs(cr,radius,chartob)
        self.plagram_planets(cr,radius,chartob)
        self.d_plagram_sign_special(cr,radius,chartob)
        if self.crosspoints:
            self.plagram_cross_points(cr,radius,chartob)
        if self.turnpoints:
            self.middle_points(cr,radius,chartob)
        if self.shadow:
            self.d_shadow_planets(cr,radius,chartob)
        self.draw_causal_planets(cr,radius,chartob)
        self.draw_nodal_planets(cr,radius,chartob)
        if self.useagecircle:
            self.plagram_age_lines(cr,radius,chartob)
        else:
            self.plagram_year_lines(cr,radius,chartob)
        if self.personlines:
            self.d_person_lines(cr,radius,chartob)
        self.pla_inner_circles(cr,radius)
        if boss.da.drawer.get_showAP():
            pe = boss.da.drawer.get_AP(chartob)
            self.draw_pg_ap(cr,radius,chartob,pe)
    
    def plagram_cross_points(self,cr,radius,chartob):
        layout = cr.create_layout()
        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        cols = [ (0.38,0.0,1.0),(0.0,0.61,0.0),(0.95,0.0,1.0),(0.0,0.0,1.0)]
        chart = chartob.chart
        cross = chart.calc_cross_points()
        nnode = chart.planets[10]
        sizes = chart.sizes()
        houses = chart.houses[:]
        h = chart.which_house(cross) + 1
        i = 0
        hs = houses[h]
        acch = 0.0; accn = 0.0
        n = nnode - h*30
        while (acch + accn) < 180.0:
            am = (houses[h+i] - hs) % 360.0
            if 30*i + acch + am > 180.0:
                break
            acch += am
            accn = 30*i
            i += 1
        h += (i-1)
        n -= 30*(i-1)
        dist  = 180 - abs(n - houses[h])
        va = sizes[h] / 6
        la = dist * va / (va + 5.0)
        op_cross = houses[h]+la 
        offset = chartob.get_cross_offset()

        r = radius*SIGN_OUTER
        rr = radius*PE_OUTER*1.03
        for i in (0,1):
            cr.save()
            cr.set_source_rgb(*cols.pop())
            angle = (offset-cross-i*180) * RAD 
            cr.move_to(r*1.02*math.cos(angle),r*1.02*math.sin(angle))
            cr.line_to(r*math.cos(angle-2*RAD),r*math.sin(angle-2*RAD))
            cr.line_to(r*0.98*math.cos(angle),r*0.98*math.sin(angle))
            cr.line_to(r*math.cos(angle+2*RAD),r*math.sin(angle+2*RAD))
            cr.close_path()
            cr.fill()
            layout.set_text("1")
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(rr*math.cos(angle)-w/2,rr*math.sin(angle)-h/1.5)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()
            cr.set_source_rgb(1.0,1.0,1.0)
            cr.move_to(r*1.015*math.cos(angle),r*1.015*math.sin(angle))
            cr.line_to(r*0.985*math.cos(angle),r*0.985*math.sin(angle))
            if i:
                cr.line_to(r*math.cos(angle-1.6*RAD),r*math.sin(angle-1.6*RAD))
            else:
                cr.line_to(r*math.cos(angle+1.6*RAD),r*math.sin(angle+1.6*RAD))
            cr.close_path()
            cr.fill()

            cr.set_source_rgb(*cols.pop())
            angle = (offset-op_cross-i*180) * RAD 
            cr.move_to(r*1.02*math.cos(angle),r*1.02*math.sin(angle))
            cr.line_to(r*math.cos(angle-2*RAD),r*math.sin(angle-2*RAD))
            cr.line_to(r*0.98*math.cos(angle),r*0.98*math.sin(angle))
            cr.line_to(r*math.cos(angle+2*RAD),r*math.sin(angle+2*RAD))
            cr.close_path()
            cr.fill()
            layout.set_text("7")
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(rr*math.cos(angle)-w/2,rr*math.sin(angle)-h/2)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()
            cr.set_source_rgb(1.0,1.0,1.0)
            cr.move_to(r*math.cos(angle-1.6*RAD),r*math.sin(angle-1.6*RAD))
            cr.line_to(r*math.cos(angle+1.6*RAD),r*math.sin(angle+1.6*RAD))
            if i:
                cr.line_to(r*1.015*math.cos(angle),r*1.015*math.sin(angle))
            else:
                cr.line_to(r*0.985*math.cos(angle),r*0.985*math.sin(angle))
            cr.close_path()
            cr.fill()
            cr.restore()
    
    def middle_points(self,cr,radius,chartob):
        aspects = chartob.chart.aspects()
        sortplanets = chartob.sortplan()
        planets = [ p % 30 for p in chartob.chart.planets ]
        mainasp = {}
        tups = []
        asp_for_plan = [ [] for i in range(0,11) ]
        middle_points = []

        for a in aspects:
            if a['gw']:
                continue
            tups.append(set([a['p1'],a['p2']]))
            mainasp[str(a['p1'])+str(a['p2'])] = a['a']
            asp_for_plan[a['p1']].append([planets[a['p2']],a['a']])
            asp_for_plan[a['p2']].append([planets[a['p1']],a['a']])
            
        for i,pl in enumerate(asp_for_plan):
            ref = planets[i]
            for d in pl:
                res = d[0] - ref
                if res > 15.0:
                    res %=  -30.0
                elif res < -15:
                    res %=  30.0
                d[0] = res
            if not pl:
                asp_for_plan[i] = [[0,1]]
            pl.sort()

        for i in range(len(sortplanets)):
            one = sortplanets[i]['ix']
            two = sortplanets[(i+1)%11]['ix']
            d_one = sortplanets[i]['degree']
            d_two = sortplanets[(i+1)%11]['degree']
            middle = (((d_two - d_one)% 360.0)/2 + d_one) % 360.0
            pair = set([one,two])
            if pair in tups:
                a = mainasp[str(min(one,two))+str(max(one,two))]
                if a in [3,5,7]:
                    middle_points.append([middle,(a,)]) 
            else:
                a_last = asp_for_plan[one][-1][1]
                a_first = asp_for_plan[two][0][1]
                middle_points.append([middle,(a_last,a_first)]) 
                
        offset = 180 + chartob.chart.houses[0] 
        R_RULEDINNER, R_RULEDOUTER = chartob.get_ruled()
        cr.save()
        cr.set_line_width(0.7*cr.get_line_width())
        for m in middle_points:
            if len(m[1]) == 1:
                col1 = col2 = aspcol[m[1][0]]
                paint = cr.stroke
                ww = 0.3
            else:
                col1 = aspcol[m[1][0]]
                col2 = aspcol[m[1][1]]
                paint = cr.fill
                ww = 0.2
            cr.set_source_rgb(*col1)
            off = (offset - m[0] + ww) * RAD
            ext = (offset - m[0] + 2.0) * RAD
            cr.move_to(radius*R_RULEDINNER*math.cos(off),
                    radius*R_RULEDINNER*math.sin(off))
            cr.line_to(radius*R_RULEDINNER*0.96*math.cos(off),
                    radius*R_RULEDINNER*0.96*math.sin(off)) 
            cr.line_to(radius*R_RULEDINNER*0.98*math.cos(ext),
                    radius*R_RULEDINNER*0.98*math.sin(ext))
            cr.close_path()
            paint()
            off = (offset - 180.0 - m[0] + ww) * RAD
            ext = (offset - 180.0 - m[0] + 1.5) * RAD
            r = radius * PE_OUTER * 1.03
            cr.move_to(r*math.cos(off),r*math.sin(off))
            cr.line_to(r*0.97*math.cos(off),r*0.97*math.sin(off)) 
            cr.line_to(r*0.985*math.cos(ext),r*0.985*math.sin(ext))
            cr.close_path()
            paint()
            cr.set_source_rgb(*col2)
            off = (offset - m[0] - ww) * RAD
            ext = (offset - m[0] - 2.0) * RAD
            cr.move_to(radius*R_RULEDINNER*math.cos(off),
                    radius*R_RULEDINNER*math.sin(off))
            cr.line_to(radius*R_RULEDINNER*0.96*math.cos(off),
                    radius*R_RULEDINNER*0.96*math.sin(off)) 
            cr.line_to(radius*R_RULEDINNER*0.98*math.cos(ext),
                    radius*R_RULEDINNER*0.98*math.sin(ext))
            cr.close_path()
            paint()
            off = (offset - 180.0 - m[0] - ww) * RAD
            ext = (offset - 180.0 - m[0] - 1.5) * RAD
            r = radius * PE_OUTER * 1.03
            cr.move_to(r*math.cos(off),r*math.sin(off))
            cr.line_to(r*0.97*math.cos(off),r*0.97*math.sin(off)) 
            cr.line_to(r*0.985*math.cos(ext),r*0.985*math.sin(ext))
            cr.close_path()
            paint()
        cr.restore()

    def make_plagram_rulers(self,cr,radius,chartob,mid=False):
        R_RULEDINNER, R_RULEDOUTER = chartob.get_ruled()
        rules = { R_RULEDOUTER: [-0.009,-0.007,-0.004], 
                R_RULEDINNER:  [0.008,0.006,0.004]}
        offset = chartob.get_offset()
        self.make_ruler(cr,radius,chartob,R_RULEDOUTER,rules,offset)
        self.make_ruler(cr,radius,chartob,R_RULEDINNER,rules,offset)
    
    def pla_magick_circles(self,cr,radius):
        cr.save()
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.set_source_rgb(*violet[1])
        cr.arc(0,0,radius*NODAL_OUTER,0,360*RAD)
        cr.arc(0,0,radius*SIGN_OUTER,0,360*RAD)
        cr.fill_preserve()
        pat = cairo.RadialGradient(0,0,radius*SIGN_OUTER,0,0,radius*NODAL_OUTER)
        pat.add_color_stop_rgba(0.0,1.0,1.0,1.0,0.5)
        pat.add_color_stop_rgba(1.0,1.0,1.0,1.0,0.0)
        cr.set_source(pat)            
        cr.fill()        
        
        cr.set_source_rgb(*magenta[1])
        cr.arc(0,0,radius*KAUSAL_OUTER,0,360*RAD)
        cr.arc(0,0,radius*NODAL_OUTER,0,360*RAD)
        cr.fill_preserve()
        pat = cairo.RadialGradient(0,0,radius*NODAL_OUTER,0,0,radius*KAUSAL_OUTER)
        pat.add_color_stop_rgba(0.0,1.0,1.0,1.0,0.0)
        pat.add_color_stop_rgba(1.0,0.3,0.0,0.3,0.3)
        cr.set_source(pat)            
        cr.fill()
        
        cr.arc(0,0,radius*PE_OUTER,0,360*RAD)
        cr.arc(0,0,radius*KAUSAL_OUTER,0,360*RAD)
        cr.set_source_rgb(0.85,0.7,0.0)
        cr.set_line_width(cr.get_line_width()*1.1)
        cr.stroke_preserve()
        if self.useagecircle:
            cr.set_source_rgb(*cream)
        else:
            cr.set_source_rgb(*yellow)
        cr.fill()
        #pat = cairo.RadialGradient(0,0,radius*KAUSAL_OUTER,0,0,radius*PE_OUTER)
        #pat.add_color_stop_rgba(0.0,0.0,0.0,0.0,0.1)
        #pat.add_color_stop_rgba(0.5,1.0,0.6,0.0,0.2)
        #pat.add_color_stop_rgba(1.0,1.0,1.0,1.0,0.0)
        #cr.set_line_width(0.6)
        #cr.set_source_rgb(0.4,0.4,0.4)
        #cr.arc(0,0,radius*H_1,0,360*RAD)
        #cr.stroke()
        #cr.arc(0,0,radius*H_2,0,360*RAD)
        #cr.stroke()
        #cr.arc(0,0,radius*H_3,0,360*RAD)
        #cr.stroke()
        #cr.arc(0,0,radius*H_4,0,360*RAD)
        #cr.stroke()
        #cr.arc(0,0,radius*H_5,0,360*RAD)
        #cr.stroke()
        #cr.arc(0,0,radius*H_6,0,360*RAD)
        #cr.stroke()
        cr.restore()

    def pla_inner_circles(self,cr,radius):
        cr.save()
        cr.set_source_rgb(1,1,1)
        cr.arc(0,0,radius*R_VERYINNER,0,360*RAD)
        cr.fill_preserve()
        cr.set_source_rgb(0,0,0)
        cr.set_line_width(0.35*cr.get_line_width())
        cr.stroke()
        cr.arc(0,0,radius*R_VERYINNER/20,0,360*RAD)
        cr.fill()
        cr.restore()

    def set_zone_cusps(self,radius,chartob):
        global zcusps, zlowps
        cusps = chartob.get_cusps_offsets()
        lowps = chartob.get_lowp_offsets()
        this_cusps = []; this_lowps = []
        for i in range(12):
            anglec = cusps[i] * RAD
            anglel = lowps[i] * RAD
            cusp_r = radius * HC[house_circles[i][0]-1]
            lowp_r = radius * HC[house_circles[i][1]-1]
            cuspx = cusp_r*math.cos(anglec)
            cuspy = cusp_r*math.sin(anglec)
            this_cusps.append((cuspx,cuspy))
            lowpx = lowp_r*math.cos(anglel)
            lowpy = lowp_r*math.sin(anglel)
            this_lowps.append((lowpx,lowpy))
        zcusps = this_cusps
        zlowps = this_lowps
        
    def d_plagram_sign_special(self,cr,radius,chartob):
        res = chartob.chart.plagram_cusps_analysis()
        cs = res['c']
        lo = res['l']
        
        offset = 180 + chartob.chart.houses[0] 
        R_RULEDINNER, R_RULEDOUTER = chartob.get_ruled()
        lowradius = radius * SIGN_OUTER
        low_inv_gen = chartob.get_golden_points()
        scl = radius * 0.0026
        cr.set_source_rgb(0.4,0.4,0.8) 
        
        cr.save()
        for house,low,inv in low_inv_gen:
            angle = (offset-house-low)*RAD
            self.d_gold_circle(cr,angle,lowradius,scl) 

        for i in range(0,12):
            off = offset-30*i
            if cs[i] == 0 or lo[i] == 2:
                cr.arc_negative(0,0,radius*SIGN_OUTER,off*RAD,(off-30)*RAD)
                cr.stroke()
            if lo[i] == 0:
                cr.arc_negative(0,0,radius*R_RULEDINNER,off*RAD,(off-30)*RAD)
                cr.stroke()
            if cs[i] == 2:
                inn = radius*R_RULEDINNER
                out = radius*SIGN_OUTER
                cr.move_to(inn*math.cos(off*RAD),inn*math.sin(off*RAD))
                cr.line_to(out*math.cos(off*RAD),out*math.sin(off*RAD))
                cr.move_to(inn*math.cos((off-30)*RAD),inn*math.sin((off-30)*RAD))
                cr.line_to(out*math.cos((off-30)*RAD),out*math.sin((off-30)*RAD))
                cr.stroke() 
                inn *= 1.02
                out *= 0.98
                off1 = off - 1
                off2 = off - 29
                cr.move_to(inn*math.cos(off1*RAD),inn*math.sin(off1*RAD))
                cr.line_to(out*math.cos(off1*RAD),out*math.sin(off1*RAD))
                cr.move_to(inn*math.cos(off2*RAD),inn*math.sin(off2*RAD))
                cr.line_to(out*math.cos(off2*RAD),out*math.sin(off2*RAD))
                cr.stroke() 
                inn *= 1.02
                out *= 0.98
                off1 -= 1
                off2 += 1
                cr.move_to(inn*math.cos(off1*RAD),inn*math.sin(off1*RAD))
                cr.line_to(out*math.cos(off1*RAD),out*math.sin(off1*RAD))
                cr.move_to(inn*math.cos(off2*RAD),inn*math.sin(off2*RAD))
                cr.line_to(out*math.cos(off2*RAD),out*math.sin(off2*RAD))
                cr.stroke() 
        
        cr.restore() 


    def draw_plagram_cusps(self,cr,radius,chartob):
        chart = chartob.chart
        cusp_cols = cycle(((0.8,0,0),(0,0,0.9),(0,0.6,0)))  
        zone_cols = cycle(((1.0,0.1,0.1,1.0),(0.1,0.1,1.0,1.0),(0,0.755,0,1.0)))
        sect_cols = cycle(((1.0,0,0,0.4),(0,0,1.0,0.4),(0,0.655,0,0.4)))
        cusps = chartob.get_cusps_offsets()
        lowps = chartob.get_lowp_offsets()
        sizes = chartob.get_sizes()
        dyn = chart.dyn_span_diff()

        cuspnames = iter(self.cuspnames)
        font_size = chartob.cusp_font_size * radius * 0.0024
        self.set_font(cr,font_size,bold=True)
        fcusp = radius * chartob.cuspfac
        dx = iter(chartob.dx)
        dy = iter(chartob.dy)

        bcusp = radius * PE_OUTER
        blowp = radius * PE_OUTER
        zbase = radius * HCIRCLES_BEGIN #H_1
        mindyn = min(dyn)
        maxdyn = max(dyn)
        span = maxdyn - mindyn

        cr.save()
        lw = cr.get_line_width()*1.1
        cr.set_line_width(lw)
        for i in range(12):
            anglec = cusps[i] * RAD
            anglel = lowps[i] * RAD
            anglel_prev = lowps[(i+11)%12] * RAD
            cusp_r = radius * HC[house_circles[i][0]-1]
            lowp_r = radius * HC[house_circles[i][1]-1]
            lowp_r_prev = radius * HC[house_circles[(i+11)%12][1]-1]
            cuspx = cusp_r*math.cos(anglec)
            cuspy = cusp_r*math.sin(anglec)
            lowpx = lowp_r*math.cos(anglel)
            lowpy = lowp_r*math.sin(anglel)
            # area 
            ang_span = anglel_prev - anglel
            if ang_span < 0: ang_span = 360*RAD + ang_span
            prev_span = anglel_prev - anglec
            if prev_span < 0: prev_span = 360*RAD + prev_span
            zcol = list(zone_cols.next())
            zcol[-1] *= (((dyn[i]-mindyn)*60.0/span)+5)/100
            cr.move_to(cuspx,cuspy)
            cr.line_to(lowpx,lowpy)
            cr.line_to(zbase*math.cos(anglel),zbase*math.sin(anglel))
            cr.arc(0,0,zbase,anglel,anglel_prev)
            cr.line_to(lowp_r_prev*math.cos(anglel_prev),lowp_r_prev*math.sin(anglel_prev))
            cr.close_path()
            pbase = radius * H_1
            pat = cairo.LinearGradient(pbase*math.cos(anglel_prev),pbase*math.sin(anglel_prev),
                    pbase*math.cos(anglel),pbase*math.sin(anglel))            
            pat.add_color_stop_rgba(0.0,*zcol)
            pat.add_color_stop_rgba(1.0,*zcol)   
            zcol[-1] = 0.2 + zcol[-1] * 1.5
            pat.add_color_stop_rgba(prev_span/ang_span,*zcol)
            cr.set_source(pat)            
            cr.fill()
            # segments
            cl = eu.Line2(eu.Point2(cuspx,cuspy),eu.Point2(lowpx,lowpy))
            ang_mag1 = anglec - (anglec - anglel) * MAGICK_SECT_1
            sectx = cusp_r*math.cos(ang_mag1)
            secty = cusp_r*math.sin(ang_mag1)
            bsectx = zbase*math.cos(ang_mag1)
            bsecty = zbase*math.sin(ang_mag1)
            sl = eu.Line2(eu.Point2(sectx,secty),eu.Point2(bsectx,bsecty))
            ipoint = cl.intersect(sl)
            cr.move_to(cuspx,cuspy)
            cr.line_to(ipoint.x,ipoint.y)
            cr.set_source_rgba(*sect_cols.next())
            cr.stroke()
            ang_mag2 = anglec - (sizes[i] * RAD * MAGICK_SECT_2)
            anglecn = cusps[(i+1)%12] * RAD
            cusp_r = radius * HC[house_circles[(i+1)%12][0]-1]
            ncuspx = cusp_r*math.cos(anglecn)
            ncuspy = cusp_r*math.sin(anglecn)
            ncl = eu.Line2(eu.Point2(lowpx,lowpy),eu.Point2(ncuspx,ncuspy))
            sectx = cusp_r*math.cos(ang_mag2)
            secty = cusp_r*math.sin(ang_mag2)
            bsectx = zbase*math.cos(ang_mag2)
            bsecty = zbase*math.sin(ang_mag2)
            sl = eu.Line2(eu.Point2(sectx,secty),eu.Point2(bsectx,bsecty))
            ipoint2 = ncl.intersect(sl)
            cr.move_to(ipoint.x,ipoint.y)
            cr.line_to(lowpx,lowpy)
            cr.line_to(ipoint2.x,ipoint2.y)
            cr.set_source_rgba(*sect_cols.next())
            cr.stroke()
            cr.move_to(ipoint2.x,ipoint2.y)
            cr.line_to(ncuspx,ncuspy)
            cr.set_source_rgba(*sect_cols.next())
            cr.stroke()

        lw = cr.get_line_width()*1.1
        lpw = cr.get_line_width()*0.5
        for anglec, anglel,hc in izip(cusps,lowps,house_circles):
            anglec *= RAD
            anglel *= RAD
            col = cusp_cols.next()
            cr.set_source_rgb(*col)
            cr.set_line_width(lw)
            fcusp = radius * HC[hc[0]-1]
            self.d_radial_line(cr,fcusp,bcusp,anglec)
            cr.set_source_rgb(0.5,0,1.0)
            cr.set_line_width(lpw)
            fcusp = radius * HC[hc[1]-1]
            self.d_radial_line(cr,fcusp,blowp,anglel)
            
            cr.set_source_rgb(*col)
            thex = radius*PE_OUTER*1.1*math.cos(anglec)
            they = radius*PE_OUTER*1.1*math.sin(anglec)
            thiscusp = cuspnames.next()
            _,_, width, height,_,_ = cr.text_extents(thiscusp)
            x = width*dx.next()
            y = height*dy.next() 
            cr.move_to(thex+x,they+y)
            cr.show_text(thiscusp)
        cr.restore() 

    def draw_nod_signs(self,cr,radius,chartob):
        radius = radius * chartob.get_sign_radfac()
        scly = chartob.scl * radius
        offsets,sclhouses = chartob.get_nod_sign_offsets()
        sizes = chartob.chart.sizes()
        zodiac = chartob.get_nod_zod_iter()
        sign_fac = 1.13
        cr.set_source_rgb(0.7,0.65,0.7)

        for i,z in enumerate(zodiac):
            cr.save()
            cr.rotate(offsets[i] * RAD)
            x_bearing,_,width,_,_,_ = z.extents
            sclx_fac = sizes[sclhouses[i]]/30
            if sclx_fac > 1.6: sclx_fac = 1.6
            sclx = sclx_fac * scly
            #print sclx_fac, sclx, scly
            cr.translate(sclx*(-width/2-x_bearing),-radius*sign_fac)
            cr.scale(sclx,scly/2.1)
            rebuild_paths(cr,z.paths)
            _,_,w,_ = cr.fill_extents()
            cr.new_path()
            mtr = cairo.Matrix(-1,0,0,1,w*0.8,0)
            cr.transform(mtr)
            rebuild_paths(cr,z.paths)
            cr.fill()
            cr.restore()

    def d_nod_radial_lines(self,cr,radius,chartob):
        sign_cusps = chartob.chart.nod_sign_long()
        fac,ins,_ = chartob.get_radial_param()
        radius = radius * fac * 1.12
        cr.save()
        cr.set_source_rgb(0.9,0.9,0.9)
        cr.set_line_width(0.5*cr.get_line_width())
        inset = ins * radius * 0.85
        for i in sign_cusps:
            angle = (180-i) * RAD
            self.d_radial_line(cr,radius+inset,radius,angle)
        cr.restore()

    def d_plan_arrows(self,cr,radius,chartob):
        global zcusps, zlowps
        chart = chartob.chart
        cusps = chartob.get_cusps_offsets()
        lowps = chartob.get_lowp_offsets()
        nasp, ceval = chart.plagram_asp_analysis()
        plots = getattr(chartob.plmanager,"plot1")
        bcusp = radius * PE_OUTER * 0.98
        ecusp = radius * H_6 * 1.1 # make sure intersect
        offset = 180 + chart.houses[0]
        lw = cr.get_line_width()*2.0
        cr.save()
        cr.set_line_width(lw)
        for i,plt in enumerate(plots):
            thirdpoint = None
            n = nasp[i]
            offang = 0.4 + (n-1)*0.14
            if n == 0: offang = 1.1
            inf_ang = (plt.degree - offang) % 360.0
            sup_ang = (plt.degree + offang) % 360.0
            h = chart.which_house(offset - plt.degree)

            bx_inf = bcusp*math.cos(inf_ang * RAD)
            by_inf = bcusp*math.sin(inf_ang * RAD)
            bx_sup = bcusp*math.cos(sup_ang * RAD)
            by_sup = bcusp*math.sin(sup_ang * RAD)
            ex_inf = ecusp*math.cos(inf_ang * RAD)
            ey_inf = ecusp*math.sin(inf_ang * RAD)
            ex_sup = ecusp*math.cos(sup_ang * RAD)
            ey_sup = ecusp*math.sin(sup_ang * RAD)

            verl1 = eu.Line2(eu.Point2(ex_inf,ey_inf),
                    eu.Point2(bx_inf,by_inf))
            verl2 = eu.Line2(eu.Point2(ex_sup,ey_sup),
                    eu.Point2(bx_sup,by_sup))
            horlc = eu.Line2(eu.Point2(zcusps[h][0],zcusps[h][1]),
                    eu.Point2(zlowps[h][0],zlowps[h][1]))
            horll = eu.Line2(eu.Point2(zlowps[h][0],zlowps[h][1]),
                    eu.Point2(zcusps[(h+1)%12][0],zcusps[(h+1)%12][1]))
            
            this_cusp = cusps[h] % 360.0
            if 0.0 <= this_cusp < 0.001: this_cusp = 360.0
            #if this_cusp == 0.0: this_cusp = 360.0
            
            next_cusp = cusps[(h+1)%12] % 360.0
            if next_cusp == 360.0: next_cusp =0.0
            lowp = lowps[h] % 360
            if inf_ang > sup_ang: inf_ang -= 360.0
            if inf_ang < 0 and h == 6: this_cusp = 0.0

            if lowp < inf_ang and sup_ang < this_cusp:#from cusp to low
                lp = horlc.intersect(verl1)
                ex_inf = lp.x; ey_inf = lp.y
                sp = horlc.intersect(verl2)
                ex_sup = sp.x; ey_sup = sp.y
            elif next_cusp < inf_ang and sup_ang < lowp:
                lp = horll.intersect(verl1)
                ex_inf = lp.x; ey_inf = lp.y
                sp = horll.intersect(verl2)
                ex_sup = sp.x; ey_sup = sp.y
            elif inf_ang < lowp < sup_ang:
                lp = horll.intersect(verl1)
                ex_inf = lp.x; ey_inf = lp.y
                sp = horlc.intersect(verl2)
                ex_sup = sp.x; ey_sup = sp.y
                lx = radius * HC[house_circles[h][1]-1] * math.cos(lowp*RAD)
                ly = radius * HC[house_circles[h][1]-1] * math.sin(lowp*RAD)
                thirdpoint = lx,ly
            elif inf_ang < next_cusp and sup_ang > next_cusp:
                horlc = eu.Line2(eu.Point2(zcusps[(h+1)%12][0],zcusps[(h+1)%12][1]),
                        eu.Point2(zlowps[(h+1)%12][0],zlowps[(h+1)%12][1]))
                lp = horlc.intersect(verl1)
                ex_inf = lp.x; ey_inf = lp.y
                sp = horll.intersect(verl2)
                ex_sup = sp.x; ey_sup = sp.y
                lx = radius * HC[house_circles[(h+1)%12][0]-1] * math.cos(next_cusp*RAD)
                ly = radius * HC[house_circles[(h+1)%12][0]-1] * math.sin(next_cusp*RAD)
                thirdpoint = lx,ly 
            elif inf_ang < this_cusp and sup_ang > this_cusp:
                horlc = eu.Line2(eu.Point2(zcusps[h][0],zcusps[h][1]),
                        eu.Point2(zlowps[h][0],zlowps[h][1]))
                lp = horlc.intersect(verl1)
                ex_inf = lp.x; ey_inf = lp.y
                horll = eu.Line2(eu.Point2(zlowps[(h+11)%12][0],zlowps[(h+11)%12][1]),
                        eu.Point2(zcusps[h][0],zcusps[h][1]))
                sp = horll.intersect(verl2)
                ex_sup = sp.x; ey_sup = sp.y
                lx = radius * HC[house_circles[h][0]-1] * math.cos(this_cusp*RAD)
                ly = radius * HC[house_circles[h][0]-1] * math.sin(this_cusp*RAD)
                thirdpoint = lx,ly 
            else:
                print >> sys.stderr, "Bad angle:%s %d %f %f %f %f" % (chart.last, h, inf_ang, sup_ang, this_cusp, next_cusp)
                #print "must not reach here!"
            
            pat = cairo.LinearGradient(bx_inf,by_inf,bx_sup,by_sup)

            c = ceval[i]
            if n == 0: c = 2 # inasp green
            cr.move_to(bx_sup,by_sup)
            cr.line_to(bx_inf,by_inf)
            cr.line_to(ex_inf,ey_inf)
            if thirdpoint:
                cr.line_to(thirdpoint[0],thirdpoint[1])
            cr.line_to(ex_sup,ey_sup)
            cr.close_path()
            if i in [0,1,6]:
                fill_col = orange
            else:
                fill_col = cross_cols[c]
            pat.add_color_stop_rgb(0,*fill_col)
            conv = Rgb2Hsl(fill_col)
            if i in [0,1,6]:
                pat.add_color_stop_rgb(0.5,1.0,1.0,0.1)
            else:
                #conv = list(conv)
                #conv[2] *=  2.8
                #conv = Hsl2Rgb(conv)                
                #pat.add_color_stop_rgb(0.5,*conv)
                pat.add_color_stop_rgb(0.5,*bar_cols[c])
            pat.add_color_stop_rgb(1,*fill_col)
            cr.set_source(pat)
            if i in [0,1,6]:
                path = cr.copy_path()
                cr.new_path()
                cr.set_source_rgba(*list(cross_cols[c])+[0.8])
                cr.move_to(bx_sup,by_sup)
                cr.line_to(ex_sup,ey_sup)
                cr.stroke()
                cr.move_to(bx_inf,by_inf)
                cr.line_to(ex_inf,ey_inf)
                cr.stroke()
                cr.append_path(path)
                cr.set_source(pat)
                cr.fill()
            else:
                cr.fill()
        cr.restore()

    def check_plagram_moons(self,chartob):
        sun = chartob.chart.planets[0]
        moon = chartob.chart.planets[1] 
        diff = sun - moon
        if (diff < 0 and abs(diff) < 180) or (diff >= 0 and abs(diff) >= 180): 
            self.this_swap_fmoon()
        else:
            self.this_swap_bmoon()

    def this_swap_fmoon(self):
        self.plagram_plan[1] = self.moon_f
        self.plextra[1] = self.moon_f
    
    def this_swap_bmoon(self):
        self.plagram_plan[1] = self.moon_b 
        self.plextra[1] = self.moon_b 
    
    def plagram_planets(self,cr,radius,chartob):
        global zcusps, zlowps
        glyphs = self.plagram_plan
        extra = self.plextra
        s_lwidths = chartob.chart.sign_force_all()
        h_lwidths = chartob.chart.house_force_all()
        self.check_plagram_moons(chartob) 
        rings_h = [(6,3,4),(4,1,6),(6,3,4),(4,1,5),(5,2,5),(5,2,6),
                (6,3,4),(4,1,6),(6,3,5),(5,2,5),(5,2,6),(6,3,6)]
        plots = getattr(chartob.plmanager,"plot1")
        hplan = chartob.chart.house_plan_long()
        lowps = [ lp % 360.0 for lp in chartob.get_lowp_offsets() ]
        cusps = [ cp % 360.0 for cp in chartob.get_cusps_offsets()]
        bcusp = radius * PE_OUTER * 0.98
        ecusp = radius * H_6 * 1.1 
        pre_scl = radius * 0.0022 # chartob.plan_scale
        zplans = chartob.chart.planets[:]
	rpfacs = [ 0, 0.2, 0.23, 0.26, 0.29, 0.32, 0.34  ] 

        for plot,hp,glyph,xtra,slw,hlw,zpl in zip(plots,hplan,glyphs,extra,s_lwidths,h_lwidths,zplans):
            pl = plot.degree % 360.0
            h = int(hp / 30)
            bx = bcusp*math.cos(pl * RAD)
            by = bcusp*math.sin(pl * RAD)
            ex = ecusp*math.cos(pl * RAD)
            ey = ecusp*math.sin(pl * RAD)
            verl = eu.Line2(eu.Point2(bx,by),eu.Point2(ex,ey))
            if pl > lowps[h]:
                horl = eu.Line2(eu.Point2(zcusps[h][0],zcusps[h][1]),
                    eu.Point2(zlowps[h][0],zlowps[h][1]))
            else:
                horl = eu.Line2(eu.Point2(zlowps[h][0],zlowps[h][1]),
                        eu.Point2(zcusps[(h+1)%12][0],zcusps[(h+1)%12][1]))
            ip = horl.intersect(verl)
            r = ip.x/math.cos(pl*RAD)
            ring = bisect_left(HC,r/radius) + 1
            #ring_fac =  (1.0 + (ring-1)/10.0)
            #ring_fac =  (0.7 + ring/4.0)
            ring_fac =  (0.7 + ring*rpfacs[ring])
            scl =  pre_scl * ring_fac
            #print ring, ring_fac
            cr.save()
            #fac = 1.02 if plot.fac <= 1.0 else 1.055
            angle = (plot.degree + plot.corr) * RAD
            if plot.corr: 
                verl = eu.Line2(eu.Point2(bcusp*math.cos(angle),bcusp*math.sin(angle)),
                        eu.Point2(ecusp*math.cos(angle),ecusp*math.sin(angle)))
                if pl < lowps[h]:
                    horl = eu.Line2(eu.Point2(zlowps[h][0],zlowps[h][1]),
                            eu.Point2(zcusps[(h+1)%12][0],zcusps[(h+1)%12][1]))
                else:
                    horl = eu.Line2(eu.Point2(zcusps[h][0],zcusps[h][1]),
                        eu.Point2(zlowps[h][0],zlowps[h][1]))
                ip = horl.intersect(verl)
                r = ip.x/math.cos(angle)
                #cr.arc(ip.x,ip.y,2,0,360*RAD)
            rpl = r * 1.09# * fac
            
            x_b,_,w,height,_,_ = xtra.extents
            shiftx = scl*(w+x_b)/2; shifty = scl*height/2
            cr.translate(rpl*math.cos(angle) - shiftx, rpl*math.sin(angle) + shifty)
            cr.scale(scl,scl)

            xtra_cusp = [h,(h+1) % 12][(28.0 + 59.0/60) < (hp - h*30)]
            key = let_keys[glyph.let]+mod_keys[int(zpl/30)%3]+mod_keys[xtra_cusp%3]
            zcol = keys_col[key]['z'] if key in keys_col else cross_cols_1[int(zpl/30)%3] 
            pcol = keys_col[key]['p'] if key in keys_col else pla_cols[glyph.let]
            hcol = keys_col[key]['h'] if key in keys_col else cross_cols_2[xtra_cusp % 3]

            rebuild_paths(cr,xtra.paths)
            if 28.0 + 59.0/60 > hp - h*30  > 30*PHI:
                cr.set_source_rgba(*(list(cross_cols[(h+1)%3])+[0.6]))
                cr.set_line_width(slw+2*hlw)
                cr.stroke_preserve()
            cr.set_source_rgb(*hcol)
            cr.set_line_width(slw+hlw)
            cr.stroke_preserve()
            cr.set_source_rgba(*zcol)
            cr.set_line_width(slw)
            cr.stroke_preserve()
            cr.set_source_rgb(0.95,0.95,0.95)
            cr.fill()
            cr.new_path()
            
            rebuild_paths(cr,glyph.paths)
            cr.set_source_rgb(*pcol)
            cr.set_line_width(1.0)
            cr.stroke_preserve() 
            cr.fill()
            cr.restore() 


    def d_person_lines(self,cr,radius,chartob):
        plots = chartob.inject_plan_degrees()
        pers = [plots[0],plots[1],plots[6]]
        cr.save()
        cr.set_line_width(cr.get_line_width()*0.8)
        cr.set_source_rgb(1.0,0.95,0.6)
        r = radius * R_INNER* 0.9
        for plot in pers:
            angle = plot.degree * RAD
            cr.move_to(0,0)
            cr.line_to(r*math.cos(angle),r*math.sin(angle))
            cr.stroke()
        cr.restore() 

    def d_shadow_planets(self,cr,radius,chartob,plot="plot1"):
        chartob.check_moons()
        plots = chartob.inject_plan_degrees(shadow=True)
        glyphs = chartob.plmanager.glyphs 
        scl = radius * 0.001
        R_PL = NODAL_OUTER + 3*(KAUSAL_OUTER - NODAL_OUTER )/4
        R_RULEDINNER, R_RULEDOUTER = chartob.get_ruled()
        r_pl = radius * R_RULEDINNER * 0.95
        cr.set_source_rgb(0.5,0.5,0.5) 
        for glyph,plot in izip(glyphs,plots):
            cr.save()
            rpl = r_pl * plot.fac
            angle = (plot.degree + plot.corr + 180.0) * RAD
            x_b,_,w,h,_,_ = glyph.extents
            shiftx = scl*(w+x_b)/2; shifty = scl*h/2
            cr.translate(rpl*math.cos(angle) - shiftx, rpl*math.sin(angle) + shifty)
            cr.scale(scl,scl)
            rebuild_paths(cr,glyph.paths)
            cr.fill()
            cr.restore() 
        
        r= radius * R_RULEDINNER
        for plt in plots:
            angle = (plt.degree+180.0) * RAD
            cr.arc(r*math.cos(angle),r*math.sin(angle),1.5,0,360*RAD)
            cr.fill()

    def draw_causal_planets(self,cr,radius,chartob,plot="plot1"):
        chartob.check_moons()
        chartob.__class__ = SoulChart
        plots = self.set_plots(chartob,plot)
        glyphs = chartob.plmanager.glyphs 
        scl = radius * 0.0012
        R_PL = NODAL_OUTER + (KAUSAL_OUTER - NODAL_OUTER )/2
        r_pl = radius *  R_PL
        cr.set_source_rgb(*magenta[0])
        for glyph,plot in izip(glyphs,plots):
            cr.save()
            fac = plot.fac
            if fac < 1.0: fac = 0.98
            if fac > 1.0: fac = 1.02
            rpl = r_pl * fac
            angle = (plot.degree + plot.corr) * RAD
            x_b,_,w,h,_,_ = glyph.extents
            shiftx = scl*(w+x_b)/2; shifty = scl*h/2
            cr.translate(rpl*math.cos(angle) - shiftx, rpl*math.sin(angle) + shifty)
            cr.scale(scl,scl)
            rebuild_paths(cr,glyph.paths)
            cr.fill()
            cr.restore() 
        
        r= radius * NODAL_OUTER
        for plt in plots:
            angle = plt.degree * RAD
            cr.arc(r*math.cos(angle),r*math.sin(angle),1,0,360*RAD)
            cr.fill()
    
    def draw_nodal_planets(self,cr,radius,chartob,plot="plot1"):
        cusps = chartob.get_cusps_offsets()
        cusps = [ c % 360 for c in cusps ] 
        sizes = chartob.get_sizes()
        chartob.check_moons()
        chartob.__class__ = NodalChart
        plots = self.set_plots(chartob,plot)
        glyphs = chartob.plmanager.glyphs 
        scl = radius * 0.0012
        R_PL = SIGN_OUTER + (NODAL_OUTER - SIGN_OUTER )/2
        r_pl = radius *  R_PL
        r= radius * NODAL_OUTER
        cr.set_source_rgb(*violet[0])
        for glyph,plot in izip(glyphs,plots):
            cr.save()
            fac = plot.fac
            if fac < 1.0: fac = 0.98
            if fac > 1.0: fac = 1.02
            rpl = r_pl * fac
            plot.degree %= 360.0
            h = (5 - int(plot.degree/30)) % 12
            dist = 30.0 - plot.degree % 30.0
            degree = (cusps[h] - dist*sizes[h]/30.0) % 360
            corr =  plot.corr*sizes[h]/30.0
            angle = (degree + corr) * RAD
            x_b,_,w,h,_,_ = glyph.extents
            shiftx = scl*(w+x_b)/2; shifty = scl*h/2
            cr.translate(rpl*math.cos(angle) - shiftx, rpl*math.sin(angle) + shifty)
            cr.scale(scl,scl)
            rebuild_paths(cr,glyph.paths)
            cr.fill()
            cr.restore() 
            angle = degree * RAD
            cr.arc(r*math.cos(angle),r*math.sin(angle),1,0,360*RAD)
            cr.fill()
        chartob.__class__ = Plagram
    
    def plagram_year_lines(self,cr,radius,chartob):
        chart = chartob.chart
        yfrac = chart.birthday_frac()
        year = int(chart.date.split('-')[0]) - 1
        cycles = chart.get_cycles(boss.state.date.dt)
        year += 72*cycles
        sizes = chartob.get_sizes()
        font_size = 11.0 * radius * MAGICK_FONTSCALE
        inset = radius  * PE_OUTER * 0.972
        radius = radius * PE_OUTER * 0.997
        offsets = chartob.get_cusps_offsets()
        cr.save()
        cr.set_line_width(0.5*cr.get_line_width())
        self.set_font(cr,font_size)
        ysize = sizes[11] / 6
        corr_prev = yfrac * ysize
        for off,size in izip(offsets,sizes):
            ysize = size / 6
            corr = yfrac * ysize
            cr.set_source_rgb(0.5,0.8,0.4)
            for j in range(0,6):
                angle = off - ysize * j
                if j == 0:
                    self.d_radial_line(cr,radius,inset,(angle+corr_prev)*RAD)
                else:
                    self.d_radial_line(cr,radius,inset,(angle+corr)*RAD)
                year += 1 
                if j  in [0,3]:
                    cr.save()
                    if j == 0:
                        rot = (90+180+angle+corr-((ysize+corr-corr_prev)/2)) % 360
                    else:
                        rot = (90+180+angle+corr-ysize/2) % 360
                    cr.rotate(rot*RAD)
                    cr.translate(0,radius)
                    yr = str(year)[2:]
                    _, _, width, height, _, _ = cr.text_extents(yr)
                    if 90 < rot < 270:
                        cr.rotate(180*RAD)
                        cr.move_to(-width/2,height)
                    else:
                        cr.move_to(-width/2,0)
                    cr.set_source_rgb(0.0,0.7,0.0)
                    cr.show_text(yr)
                    cr.restore()
            corr_prev = corr
        cr.restore()
    
    def plagram_age_lines(self,cr,radius,chartob):
        chart = chartob.chart
        year = 0
        cycles = chart.get_cycles(boss.state.date.dt)
        year += 72*cycles
        sizes = chartob.get_sizes()
        font_size = 11.0 * radius * MAGICK_FONTSCALE
        inset = radius  * PE_OUTER * 0.972
        radius = radius * PE_OUTER * 0.997
        offsets = chartob.get_cusps_offsets()
        cr.save()
        cr.set_line_width(0.5*cr.get_line_width())
        self.set_font(cr,font_size)
        for off,size in izip(offsets,sizes):
            ysize = size / 6
            cr.set_source_rgb(0.5,0.8,0.4)
            for j in range(0,6):
                angle = (off - ysize * j )
                self.d_radial_line(cr,radius,inset,angle*RAD)
                year += 1 
                if j in [1,3,5]:
                    cr.save()
                    rot = (90+180+angle-ysize/2) % 360
                    cr.rotate(rot*RAD)
                    cr.translate(0,radius)
                    yr = str(year)
                    _, _, width, height, _, _ = cr.text_extents(yr)
                    if 90 < rot < 270:
                        cr.rotate(180*RAD)
                        cr.move_to(-width/2,height)
                    else:
                        cr.move_to(-width/2,0)
                    cr.set_source_rgb(0.0,0.7,0.0)
                    cr.show_text(yr)
                    cr.restore()
        cr.restore()
        cr.new_path()

    
    def draw_pg_ap(self,cr,radius,chartob,pe):
        chart = chartob.chart
        pedraw = 180 + chartob.chart.houses[0] - pe
        pe_col = chartob.pe_col
        r = radius
        rap = radius*0.645
        xap = math.cos(pedraw*RAD); yap = math.sin(pedraw*RAD) 
        cr.set_line_width(0.5 * cr.get_line_width())
        cr.set_source_rgba(*(list(pe_col)+[0.52]))
        scl = radius * chartob.plan_scale*0.4
        cr.arc(rap*xap,rap*yap,12*scl,0,360*RAD)
        cr.fill()
        cr.set_source_rgb(1,1,1)
        cr.move_to(r*0.635*xap,r*0.635*yap)
        cr.line_to(r*0.655*xap,r*0.655*yap)
        cr.stroke()
        #self.surface.pepending[-1] = pe
