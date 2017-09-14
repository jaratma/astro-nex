# -*- coding: utf-8 -*-
import cairo
import pango
from .. chart import zodnames,planames,aspnames
from roundedcharts import NodalChart,SoulChart,LocalChart
from .. boss import boss
curr = boss.get_state()

aspcol = None

class ProgMixin(object):
    def __init__(self,zodiac):
        global aspcol
        aspcol = zodiac.get_aspcolors() 
        self.zod = zodiac.zod
        self.plan = zodiac.plan
    
    def prog_nat(self,cr,w,h,chartob):
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(0.5)
        self.d_prog(cr,chartob)
    
    def prog_local(self,cr,w,h,chartob):
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(0.5)
        chartob.__class__ = LocalChart
        self.d_prog(cr,chartob,kind='local')
    
    def prog_soul(self,cr,w,h,chartob):
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(0.5)
        chartob.__class__ = SoulChart
        self.d_prog(cr,chartob,kind='soul')
    
    def prog_nod(self,cr,w,h,chartob):
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(0.5)
        chartob.__class__ = NodalChart
        self.d_prog(cr,chartob,kind='nodal')
    
    def d_prog(self,cr,chartob,kind='radix'):
        if kind == 'radix': 
            age = chartob.get_age_prog()
        elif kind == 'soul':
            age = chartob.get_age_prog()
            #age = curr.curr_chart.calc_agep(kind) 
        elif kind == 'local':
            age = chartob.get_age_prog()
            #age = curr.curr_chart.calc_agep(kind) 
        elif kind == 'nodal':
            age = chartob.get_age_prog()
            #age = curr.curr_chart.calc_nodal_agep()

        ho = 128; vo = 15
        hm = 50; vm = 110
        year = prev_y = ""
        
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        self.main_labels(cr,font,kind)
        cr.set_source_rgb(0,0,0)
        cr.move_to(50,80)
        cr.line_to(540,80)
        cr.stroke()
        if kind in ['radix','nodal']:
            self.cross_points(cr)
        else:
            vm = 90
        
        for i in range(len(age)): 
            font = pango.FontDescription(self.opts.font)
            font.set_size(9*pango.SCALE)
            layout.set_font_description(font)
            cr.set_source_rgb(0,0,0.4)
            y = age[i]['year']
            if i == 0:
                year = prev_y = y
            else:
                if y != prev_y:
                    year = prev_y = y
                else:
                    if i % 48 == 0: year = y  
                    else: year = " "

            x = hm + int(ho*(i/48))
            y = vm + vo*(i%48)
            cr.move_to(x,y)
            text = "%s.%s.%s" %  (age[i]['day'],age[i]['mon'],str(year))
            layout.set_text(text)
            cr.layout_path(layout)
            cr.fill()
            cl = age[i]['cl']
            text = age[i]['lab']
            if cl == "txt_cp":
                cr.set_source_rgb(0.6,0,0)
                layout.set_text(text)
                cr.move_to(x+80,y)
                cr.layout_path(layout)
                cr.fill()
            elif cl == "pr":
                cr.set_source_rgb(0,0.4,0)
                layout.set_text(text)
                cr.move_to(x+80,y)
                cr.layout_path(layout)
                cr.fill()
            elif cl == "pi":
                cr.set_source_rgb(0,0,0.6)
                layout.set_text(text)
                cr.move_to(x+80,y)
                cr.layout_path(layout)
                cr.fill()
            else:
                font = pango.FontDescription("Astro-Nex")
                font.set_size(11*pango.SCALE)
                layout.set_font_description(font)
                if cl == 'asp':
                    tx = age[i]['lab'].split('/')
                    asp = self.asplet[aspnames.index(tx[0])]
                    cr.move_to(x+80,y)
                    cr.set_source_rgb(*aspcol[aspnames.index(tx[0])])
                    layout.set_text("%s" % asp)
                    cr.layout_path(layout)
                    cr.fill()
                    pl = self.plan[planames.index(tx[1])].let
                    colp = self.plan[planames.index(tx[1])].col
                    cr.set_source_rgb(*colp) 
                    cr.move_to(x+100,y)
                    layout.set_text("%s" % pl)
                    cr.layout_path(layout)
                    cr.fill()
                elif cl == 'sign':
                    colp = self.zod[zodnames.index(text)%4].col
                    sign = self.zod[zodnames.index(text)].let
                    cr.set_source_rgb(*colp) 
                    cr.move_to(x+85,y)
                    layout.set_text("%s" % sign)
                    cr.layout_path(layout)
                    cr.fill()
                elif cl == 'mid':
                    tx = age[i]['lab'].split('/')
                    pl = self.plan[planames.index(tx[0])].let
                    colp = self.plan[planames.index(tx[0])].col
                    cr.set_source_rgb(*colp) 
                    cr.move_to(x+80,y)
                    layout.set_text("%s" % pl)
                    cr.layout_path(layout)
                    cr.fill()
                    pl = self.plan[planames.index(tx[1])].let
                    colp = self.plan[planames.index(tx[1])].col
                    cr.set_source_rgb(*colp) 
                    cr.move_to(x+100,y)
                    layout.set_text("%s" % pl)
                    cr.layout_path(layout)
                    cr.fill()
            cr.new_path()
            
    def cross_points(self,cr):
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        
        cp = curr.curr_chart.calc_cross_points(True)
        dat1 = cp['dat1']
        dat2 = cp['dat2']
        deg1 = cp['cp1']['deg']
        deg2 = cp['cp2']['deg']
        
        cr.set_source_rgb(0.5,0,0.5)
        cr.move_to(50,88)
        layout.set_text(_("Cruce PE - K1: %s  %s") % (dat1,deg1))
        cr.layout_path(layout)
        cr.fill() 
        cr.move_to(310,88)
        layout.set_text("K2: %s  %s" % (dat2,deg2))
        cr.layout_path(layout)
        cr.fill()
        
        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        s1 = self.zod[cp['cp1']['name']].let
        s2 = self.zod[cp['cp2']['name']].let
        c1 = self.zod[cp['cp1']['col']%4].col
        c2 = self.zod[cp['cp2']['col']%4].col
        cr.move_to(274,86)
        cr.set_source_rgb(*c1)
        layout.set_text("%s" % (s1))
        cr.layout_path(layout)
        cr.fill()
        cr.move_to(466,86)
        cr.set_source_rgb(*c2)
        layout.set_text("%s" % (s2))
        cr.layout_path(layout)
        cr.fill()


    

