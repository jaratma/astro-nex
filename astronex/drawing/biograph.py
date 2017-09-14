# -*- coding: utf-8 -*-
import gtk
import cairo
import pango
import pangocairo
from datetime import datetime,timedelta
from math import pi as PI
import math
from .. chart import planclass,aspclass,orbs
from roundedcharts import NodalChart,SoulChart,LocalChart,RadixChart,DharmaChart
from .. boss import boss
curr = boss.get_state()

PHI = 1 / ((1+math.sqrt(5))/2)
aspcol = None
prev_chart = None

_bio = -1
ruler = [0.9,0.5]
biodate = datetime.now()
plorder = [0,1,6,2,3,4,5,7,8,9,10]
release = False
MAGICK_FONTSCALE=0.0012
nodorb = [0.75,1.0,1.5,1.75,2.0]

class BioMixin(object):
    def __init__(self,zodiac):
        global aspcol,prev_chart
        aspcol = zodiac.get_aspcolors() 
        self.zod = zodiac.zod
        self.plan = zodiac.plan
        surface = self.surface

        if surface.__class__.__name__ in ['DrawMaster','DrawAux']:
            info = { 'button': -1 }
            surface.set_data("move-info", info)
            surface.connect('event',self.pe_rulercb,surface)
        
        chart = curr.curr_chart
        prev_chart = chart,chart.first,curr.curr_op
        
        self.hoff = 0.125
        self.gridw = 0.0 # gridwith
        self.house_t = (None,None)

    def set_bio(self,h,frac=None):
        global _bio, ruler, biodate
        _bio = h
        if frac:
            ruler[0] = (frac*self.gridw+self.hoff)/self.surface.allocation.width 
        else:
            cycles =  curr.curr_chart.get_cycles(curr.date.dt)
            house_t = curr.curr_chart.house_time_lapsus(h,cycles)
            hpoint = self.surface.allocation.width*ruler[0]
            rulfrac = (hpoint - self.hoff) / self.gridw
            ruldays = rulfrac * house_t['lapsus'].days
            biodate = house_t['begin']+timedelta(days=ruldays) 
            boss.da.panel.set_date(biodate)

    def set_bio_from_date(self,bio,frac):
        global _bio, ruler
        _bio = bio 
        ruler[0] = (frac*self.gridw+self.hoff)/self.surface.allocation.width 
        if curr.curr_op.startswith('bio'):
            self.surface.queue_draw()

    def pe_rulercb(self,child,event,surface):
        global release,biodate
        if hasattr(surface,'opaux'):
            if not surface.opaux[0].startswith('bio'):
                return False
        else:
            if not curr.curr_op.startswith('bio') or curr.opmode != 'simple' or curr.curr_chart == curr.now:
                return False 
        state =  event.get_state()
        info = child.get_data("move-info")
        width = child.allocation.width
        if event.type == gtk.gdk._2BUTTON_PRESS:
            boss.da.panel.nowbut.emit('clicked')
            info['button'] = 100; #now
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS:
            if event.button != 1: return False
            if info['button'] < 0:
                info['button'] = event.button
            elif info['button'] == 100:
                info['button'] = -1
            return True 
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            if info['button'] < 0: 
                return True
            if info['button'] == event.button:
                info['button'] = -1;
                ruler[0] = event.x / width
                release = True
        elif gtk.gdk.MOTION_NOTIFY:
            if info['button'] < 0 or info['button'] == 100:
                info['button'] = -1
                return False
            x, y, state = event.window.get_pointer() # ensure more events
            ruler[0] = float(x) / width
        hpoint = width*ruler[0] # release & notify
        rulfrac = (hpoint - self.hoff) / self.gridw
        ruldays = rulfrac * self.house_t['lapsus'].days
        biodate = self.house_t['begin']+timedelta(days=ruldays)
        boss.da.panel.set_date(biodate)
        surface.queue_draw()
        return False

    def bio_nat(self,cr,w,h,chartob):
        chartob.__class__ = RadixChart
        self.draw_bio(cr,w,h,chartob)
    
    def bio_nod(self,cr,w,h,chartob):
        chartob.__class__ = NodalChart
        chartob.name = 'nodal'
        self.draw_bio(cr,w,h,chartob)
    
    def bio_soul(self,cr,w,h,chartob):
        chartob.__class__ = SoulChart
        chartob.name = 'soul'
        self.draw_bio(cr,w,h,chartob)
    
    def bio_dharma(self,cr,w,h,chartob):
        chartob.__class__ = DharmaChart
        chartob.name = 'dharma'
        self.draw_bio(cr,w,h,chartob)
    
    def draw_bio(self,cr,width,height,chartob):
        global _bio,prev_chart,release,ruler
        cr.set_line_width(0.5)
        self.minim = minim = min(width,height)
        self.hoff = hoff = width*0.125
        self.gridw = hoff*6
        self.hroff = hoff+self.gridw
        self.voff = voff = height*0.2
        
        self.chart = chart = chartob.chart
        cp = chart.calc_cross_points()
        cph = chart.which_house(cp) 
        self.sizes = chartob.get_sizes()

        this_chart = chart,chart.first,curr.curr_op
        if this_chart[1] != prev_chart[1]: 
            _bio = -1
        if this_chart != prev_chart: 
            prev_chart = this_chart 

        if _bio < 0 or chart.first == curr.curr_click.first:
            dt = curr.date.dt
            dt = dt.combine(dt.date(),dt.time()) 
            _bio,tfrac = chart.which_house_today(dt)
            ruler[0] = (hoff+self.gridw*tfrac)/width
        elif _bio == 100:
            dt = datetime.now()
            _bio,tfrac = chart.which_house_today(dt)
            ruler[0] = (hoff+self.gridw*tfrac)/width 
        
        bh = _bio
        htimes = chartob.get_house_age_prog(bh) 
        self.htimes = htimes

        cycles =  chart.get_cycles(curr.date.dt)
        self.house_t = chart.house_time_lapsus(bh,cycles)
        font = pango.FontDescription(self.opts.font)
        layout = cr.create_layout()
        font.set_size(int(14*pango.SCALE*minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        # vert lines
        self.d_vert_lines(cr)
        # house number
        self.d_house_number(cr,layout,bh)
        # years rules
        self.d_years_rule(cr,layout,htimes[0])
        # sign bar 
        if chartob.name == 'nodal':
            self.d_nodal_signbar(cr,layout,bh,chartob)
        else:
            self.d_signbar(cr,layout,bh,chartob)
        # ruler
        if self.surface.__class__.__name__ != 'DrawPdf':
            self.d_ruler(cr,width,height,voff,chartob.pe_col)
        # baselines
        self.baselines = []
        self.d_baselines(cr,layout)
        # pe zones
        if self.pe_zones:
            self.d_pe_zone(cr,bh,chartob)
        # midpoints/fixedpoints line
        self.d_midpoint_line(cr,chartob) 
        mids = [t for t in htimes if t['cl'] == 'mid']
        if mids: 
            self.d_midplans(cr,layout,mids)
        
        # aspects
        self.intensity = [0]*72
        self.d_prev_house(cr,layout,bh,chartob)
        self.d_this_house(cr,layout,bh,chartob.name)
        self.d_follow_house(cr,layout,bh,chartob)
        
        #plot intensity 
        self.d_intensity(cr,chartob)
        #cross points 
        if bh in [cph,(cph+6)%12]:
            if bh != cph: cp = (cp+180)%360
            self.d_cross_point(cr,bh,cp,chartob)
        #date label
        self.surface.pepending = [True,self.get_AP(chartob),None]
        hpoint = width*ruler[0]
        self.d_release(cr,hpoint) 
    
    ############## services
    def d_pe_zone(self,cr,bh,chartob):
        if chartob.name == 'soul':
            return
        chart = chartob.chart
        hz = chart.calc_pe_houses()[bh]
        cols = chartob.pez_cols
        above = chart.which_house(chart.planets[10]) >= 6
        seq = [ (cols['paleblue'], cols['paleblue']),
                (cols['palegreen'],cols['palegreen']),
                (cols['paleblue'], cols['paleblue']),
                (cols['paleblue'], cols['teal']),
                (cols['pink'], cols['darkblue']) ]
        if above:
            seq[2] = (cols['palegreen'],cols['darkgreen'])
        vzone = self.voff+self.voff*2.52
        vh = self.hoff/20
        hinit = self.hoff
        zone,frac = hz[0]
        gridfrac = 0
        for z,f in hz[1:]:
            frac = f
            cr.set_source_rgb(*seq[zone][0])
            cr.rectangle(hinit,vzone,self.gridw*frac-gridfrac,vh)
            cr.fill()
            cr.set_source_rgb(*seq[zone][1])
            cr.rectangle(hinit,vzone+vh,self.gridw*frac-gridfrac,vh)
            cr.fill()
            hinit = self.hoff + self.gridw*frac
            zone = z
            gridfrac = self.gridw*frac
        cr.set_source_rgb(*seq[zone][0])
        cr.rectangle(hinit,vzone,self.hroff-hinit,vh)
        cr.fill() 
        cr.set_source_rgb(*seq[zone][1])
        cr.rectangle(hinit,vzone+vh,self.hroff-hinit,vh)
        cr.fill() 
        

    def d_house_number(self,cr,layout,bh):
        cr.set_source_rgb(0.8,0.3,0.3)
        cr.move_to(self.hoff+6,self.voff-10)
        layout.set_text("%s" % str(bh+1))
        cr.show_layout(layout) 
        layout.set_text("%s" % str(bh+1))
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(self.hroff-xpos-6,self.voff-10)
        cr.show_layout(layout) 

    def d_vert_lines(self,cr):
        hoff = self.hoff
        voff = self.voff
        cr.set_source_rgb(0,0,0.5)
        cr.move_to(hoff,voff)
        cr.line_to(hoff,voff+voff*3)
        cr.move_to(self.hroff,voff)
        cr.line_to(self.hroff,voff+voff*3)
        cr.stroke()
        for i in range(1,6):
            cr.move_to(hoff+hoff*i,voff*2)
            cr.line_to(hoff+hoff*i,voff+voff*17/7)
        cr.stroke()

    def d_ruler(self,cr,width,height,voff,pe_col): 
        cr.set_source_rgba(*(list(pe_col)+[0.5]))
        cr.arc(width*ruler[0],height*ruler[1],5,0,180*PI)
        cr.fill()
        cr.move_to(width*ruler[0],voff)
        cr.line_to(width*ruler[0],voff+voff*3)
        cr.stroke()

    def d_midpoint_line(self,cr,chartob):
        cols = chartob.zonecols
        percents = [0.0,0.21,0.41,0.68,0.75,0.87,0.97,1.0]
        hoff = self.hoff
        voff = self.voff
        cr.save()
        cr.set_line_width(4)
        cr.set_line_cap(cairo.LINE_CAP_BUTT)
        cr.set_source_rgb(0.4,0.4,0.9)
        cr.move_to(hoff,voff*1.76)
        cr.line_to(self.hroff,voff*1.76)
        cr.stroke()
        cr.set_line_width(2.2)
        for i,c in enumerate(cols):
            #cr.set_source_rgba(*(list(c)+[0.7]))
            cr.set_source_rgb(*c)
            cr.move_to(hoff+self.gridw*percents[i],voff*1.76)
            cr.line_to(hoff+self.gridw*percents[i+1],voff*1.76)
            cr.stroke()
        cr.set_source_rgb(0.3,0.3,0.7)
        cr.arc(hoff+self.gridw*PHI,voff*1.76,2,0,180*PI)
        cr.fill()
        cr.set_source_rgb(0.3,0.3,0.7)
        cr.arc(self.hroff-self.gridw*PHI,voff*1.76,2,0,180*PI)
        cr.fill()
        cr.restore() 

    def d_midplans(self,cr,layout,mids):
        font = pango.FontDescription("Astro-Nex")
        font.set_size(int(10*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        for m in mids:
            date = datetime(m['year'],m['mon'],m['day'],0,0,0)
            pl1,pl2 = m['lab']
            plet1 = self.plan[pl1].let 
            plet2 = self.plan[pl2].let 
            if curr.curr_op == 'bio_nod':
                plet1, plet2 = plet2, plet1 
            col1 = self.plan[pl1].col
            col2 = self.plan[pl2].col
            phoff = date - self.house_t['begin']
            phoff = self.gridw*phoff.days/self.house_t['lapsus'].days + self.hoff
            pvoff = self.voff*1.8
            
            cr.set_source_rgb(*col1)
            layout.set_text("%s" % plet1)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(phoff-w*1.24,pvoff+h/2)
            cr.layout_path(layout)
            cr.fill()
            
            cr.set_source_rgb(*col2)
            layout.set_text("%s" % plet2)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE 
            cr.move_to(phoff+w*0.25,pvoff+h/2)
            cr.layout_path(layout)
            cr.fill()
            
            cr.move_to(phoff,self.voff*1.76+h/2)
            cr.line_to(phoff,self.voff*1.76-h/2)
            cr.set_source_rgb(0.9,0.3,0.3)
            cr.stroke()
    
    def d_baselines(self,cr,layout):
        for i in range(11):
            col = self.plan[plorder[i]].col
            cr.set_source_rgb(*col)
            bl = self.voff*2+self.voff/7*i; 
            self.baselines.append(bl)
            cr.move_to(self.hoff,bl)
            cr.line_to(self.hroff,bl)
            cr.stroke()
            plet = self.plan[plorder[i]].let
            layout.set_text("%s" % plet)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE 
            cr.move_to(self.hoff*0.7,bl-h/3)
            cr.layout_path(layout)
            cr.fill()

    def d_years_rule(self,cr,layout,ht):
        hoff = self.hoff
        voff = self.voff
        cr.set_source_rgb(0,0,0)
        font = pango.FontDescription(self.opts.font)
        font.set_size(int(8*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        byear = ht['year']
        yoff = self.house_t['begin'] - datetime(byear,1,1,0,0,0)
        yoff = hoff*yoff.days/(self.house_t['lapsus'].days/6)
        
        for i in range(7):
            inoff = hoff-yoff+hoff*i
            cr.move_to(inoff,voff+voff/8)
            cr.line_to(inoff,voff*1.3)
            cr.stroke()
            layout.set_text("%s" % str(byear+i))
            cr.move_to(inoff+hoff*0.02,voff+voff/9)
            cr.layout_path(layout)
            cr.fill()
            ininoff = hoff / 12
            for j in range(1,12):
                o = inoff+ininoff*j
                cr.move_to(o,voff+voff/5)
                if j % 2 == 1:
                    cr.line_to(o,voff+voff/4)
                else:
                    cr.line_to(o,voff+voff/3.5)
            cr.stroke()

    def d_cross_point(self,cr,bh,cdeg,chartob):
        if chartob.name == 'soul':
            return
        if chartob.name == 'basic':
            cdeg = (cdeg - self.chart.houses[bh]) % 360
            cr.set_source_rgb(1,0.9,1) 
        else:
            cusp = (self.chart.planets[10]-30*bh)%360
            cdeg = cusp - cdeg
            cr.set_source_rgb(0.8,0.8,0.8) 
        h = self.hoff + (cdeg/self.sizes[bh])*self.gridw
        cr.set_line_width(1)
        cr.move_to(h,self.voff*1.4)
        cr.line_to(h,self.voff*1.4+self.voff/8) 
        cr.stroke()

    def d_intensity(self,cr,chartob):
        intensity = self.intensity
        moff = self.gridw/72
        cr.set_source_rgb(0,0,0) 
        vint = self.voff+self.voff*3
        cr.move_to(self.hoff,vint)
        cr.line_to(self.hroff,vint)
        cr.stroke()
        if chartob.name == 'soul':
            cr.set_source_rgb(0.7,0,0.7)
            mag = 2
        elif chartob.name == 'nodal':
            cr.set_source_rgb(0.2,0,0.8)
            mag = 2
        else:
            cr.set_source_rgb(0.4,0,0) 
            mag = 1.5
        cr.move_to(self.hoff,vint-2*intensity[0])
        for n in range(len(intensity)):
            cr.line_to(self.hoff+moff*(n+1),vint-mag*intensity[n])
        cr.stroke()

    def d_nodal_signbar(self,cr,layout,bh,chartob):
        hoff = self.hoff
        voff = self.voff
        node = self.chart.planets[10]
        cr.set_source_rgb(0.4,0.5,0.4)
        cr.move_to(hoff,voff*1.525)
        cr.line_to(self.hroff,voff*1.525)
        cr.stroke()
        
        font = pango.FontDescription("Astro-Nex")
        font.set_size(int(12*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        degreefac = self.gridw/30
        
        prev_htimes = chartob.get_house_age_prog((bh+11)%12) 
        prev_sign = [t for t in prev_htimes if t['cl'] == 'sign'][0]
        t = [t for t in self.htimes if t['cl'] == 'sign'][0]
        soff = datetime(t['year'],t['mon'],t['day'],0,0,0)-self.house_t['begin']
        soff = self.gridw*soff.days/(self.house_t['lapsus'].days) 
        
        sign = self.zod[prev_sign['lab']].let
        col = (self.zod[prev_sign['lab']%4].col)
        colin = list(col) + [0.5]
        cr.set_source_rgba(*colin) 
        cr.rectangle(hoff,voff*1.4,soff,voff/8)
        cr.fill_preserve()
        cr.set_source_rgb(*col)
        cr.stroke()
        
        lowdeg = int(math.ceil(node - int(node/30)*30))
        self.down_sign_rule(cr,lowdeg,degreefac,soff)
        cr.set_source_rgb(1,1,1)
        layout.set_text("%s" % sign)
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        cr.move_to(hoff+soff-w*1.75,voff*1.4)
        cr.show_layout(layout) 
        
        sign = self.zod[t['lab']].let
        col = (self.zod[t['lab']%4].col)
        colin = list(col) + [0.5]
        cr.set_source_rgba(*colin)
        cr.rectangle(hoff+soff,voff*1.4,self.gridw-soff,voff/8)
        cr.fill_preserve()
        cr.set_source_rgb(*col)
        cr.stroke()
        
        updeg = 30 - int(math.floor(node - int(node/30)*30)) 
        self.up_sign_rule(cr,updeg,degreefac,soff)
        cr.set_source_rgb(1,1,1)
        cr.move_to(hoff+soff+8,voff*1.4)
        layout.set_text("%s" % sign)
        cr.show_layout(layout) 

    def down_sign_rule(self,cr,lowdeg,degreefac,soff):
        cr.save()
        cr.set_source_rgb(0,0,0)
        for d in range(0,lowdeg):
            amount = self.hoff + soff - d*degreefac
            if amount < self.hoff: break
            cr.move_to(amount,self.voff*1.525)
            if d % 5 == 0:
                cr.line_to(amount,self.voff*1.58)
            else:
                cr.line_to(amount,self.voff*1.55)
        cr.stroke()
        cr.restore()

    def up_sign_rule(self,cr,updeg,degreefac,soff):
        cr.save()
        cr.set_source_rgb(0,0,0)
        for d in range(1,updeg):
            amount = self.hoff + soff + d*degreefac
            if amount > self.hroff: break
            cr.move_to(amount,self.voff*1.525)
            if d % 5 == 0:
                cr.line_to(amount,self.voff*1.58)
            else:
                cr.line_to(amount,self.voff*1.55)
        cr.stroke()
        cr.restore()
       
    def d_signbar(self,cr,layout,bh,chartob):
        hoff = self.hoff
        voff = self.voff
        houses = chartob.chart.houses[:]
        cr.set_source_rgb(0.4,0.5,0.4)
        cr.move_to(hoff,voff*1.525)
        cr.line_to(self.hroff,voff*1.525)
        cr.stroke()
        
        font = pango.FontDescription("Astro-Nex")
        font.set_size(int(12*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        
        degree = self.gridw/30
        degreefac = 30/self.sizes[bh]*degree
        prev_sign = None; i = 11
        while not prev_sign: 
            prev_htimes = chartob.get_house_age_prog((bh+i)%12) 
            i -= 1
            t = [t for t in prev_htimes if t['cl'] == 'sign']
            if t: prev_sign = t[-1]

        col = (self.zod[prev_sign['lab']%4].col)
        sign = self.zod[prev_sign['lab']].let
        if chartob.name == 'soul':
            cr.set_source(sign_col_soul(col,voff))
        elif chartob.name == 'dharma':
            cr.set_source(sign_col_dharma(col,voff))
        else:
            cr.set_source_rgba(*(list(col)+[0.9]))
        
        temp_off = hoff; prev_slet = None; prev_soff = 0; post_soff = hoff
        lowdeg = 30 - int(math.floor(houses[bh] - int(houses[bh]/30)*30))
        tts = [t for t in self.htimes if t['cl'] == 'sign']
        for t in tts:
            soff=datetime(t['year'],t['mon'],t['day'],0,0,0)-self.house_t['begin']
            soff = self.gridw*soff.days/(self.house_t['lapsus'].days) 
            cr.rectangle(temp_off,voff*1.4,soff-prev_soff,voff/8)
            cr.fill()
            
            self.down_sign_rule(cr,lowdeg,degreefac,soff)
            lowdeg = 30
            
            cr.set_source_rgb(1,1,1)
            layout.set_text("%s" % sign)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            cr.move_to(hoff+soff-w*1.75,voff*1.4)
            cr.show_layout(layout) 
            
            if not prev_slet is None:
                cr.move_to(prev_slet[1]+8,voff*1.4)
                layout.set_text("%s" % prev_slet[0])
                cr.layout_path(layout)
                cr.fill() 
            sign = self.zod[t['lab']].let
            #prev_slet = (sign,temp_off+soff)
            prev_slet = (sign,hoff+soff)
            col = (self.zod[t['lab']%4].col)
            if chartob.name == 'soul':
                cr.set_source(sign_col_soul(col,voff))
            elif chartob.name == 'dharma':
                cr.set_source(sign_col_dharma(col,voff))
            else:
                cr.set_source_rgba(*(list(col)+[0.9]))
            prev_sign = t
            temp_off = hoff + soff
            prev_soff = post_soff = soff
        cr.rectangle(temp_off,voff*1.4,hoff*7-temp_off,voff/8)
        cr.fill()
        cr.set_source_rgb(1,1,1)
        cr.move_to(temp_off+8,voff*1.4)
        layout.set_text("%s" % sign)
        cr.show_layout(layout) 
        
        updeg = int(math.ceil(houses[(bh+1)%12] - int(houses[(bh+1)%12]/30)*30))
        if post_soff != hoff:
            self.up_sign_rule(cr,updeg,degreefac,soff)
        else: # intercepted
            lowdeg = int(math.ceil(houses[bh] - int(houses[bh]/30)*30))
            frac = degreefac - (lowdeg - int(lowdeg))*degree
            updeg = int(math.ceil(houses[(bh+1)%12] - int(houses[(bh+1)%12]/30)*30))
            for d in range(updeg-lowdeg):
                amount = hoff + frac + d*degreefac
                cr.move_to(amount,voff*1.525)
                if (d+lowdeg) % 5 == 0:
                    cr.line_to(amount,voff*1.58)
                else:
                    cr.line_to(amount,voff*1.55)
            cr.stroke()

    def d_this_house(self,cr,layout,bh,charttype):
        font = pango.FontDescription("Astro-Nex")
        font.set_size(int(8*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        house_t = self.house_t
        hoff = self.hoff
        voff = self.voff
        hroff = self.hroff
        moff = self.gridw/72
        vi = voff/24 
        bhouse = self.htimes
        intensity = self.intensity
        tts = [t for t in bhouse if t['cl'] == 'asp']
        for t in tts:
            date = datetime(t['year'],t['mon'],t['day'],0,0,0)
            asp,pl = t['lab']
            pvoff = self.baselines[plorder.index(pl)]
            phoff = date - house_t['begin']
            acl = aspclass[asp]
            if charttype == 'nodal':
                orb = nodorb[acl] 
                halfdays = orb * 6 /self.sizes[bh] * 365
            elif charttype == 'basic':
                if pl < 10:
                    orb = orbs[planclass[pl]][acl]
                else:
                    orb = 1.0
                halfdays = orb * 6 /self.sizes[bh] * 365
            else:
                halfdays = 365/2
            inf = phoff.days - halfdays
            sup = phoff.days + halfdays
            phoff = hoff*6*phoff.days/house_t['lapsus'].days + hoff
            infhoff = hoff*6*inf/house_t['lapsus'].days + hoff
            suphoff = hoff*6*sup/house_t['lapsus'].days + hoff
            asplength = suphoff - infhoff
            # intensity calc
            steps = int(math.ceil(asplength/moff))
            vstep = vi*2/steps
            begint = int(infhoff/moff)-12
            for s in range(steps):
                if begint+s < 0 or begint+s >= 72: continue
                intix = begint+s
                if pl in [0,1,2,5,6,10] or charttype != 'basic':
                    if s < steps/2:
                        intensity[intix] += vstep*s
                    elif s > steps/2:
                        intensity[intix] += (steps-1-s)*vstep
                    else:
                        intensity[intix] += (steps-1-s)*vstep
                elif pl in [3,9]:
                    intensity[intix] += vstep*s
                elif pl in [4,7]:
                    intensity[intix] += (steps-1-s)*vstep
                else:
                    if s < steps/2:
                        intensity[intix] += (steps-s*2)*vstep
                    else:
                        intensity[intix] += vstep*s

            cutleft = cutright = False
            if infhoff < hoff:
                diff = hoff - infhoff
                if pl in [0,1,2,5,6,8,10] or charttype != 'basic':
                    fac =  diff*2 / (suphoff-infhoff)
                else:
                    fac =  diff / (suphoff-infhoff)
                infhoff = hoff
                vcl = vi*fac
                if pl in [4,7,8] and charttype == 'basic':
                    vcl = vi - vcl
                cutleft = True 
            if suphoff > hroff:
                diff = suphoff - hroff
                if pl in [0,1,2,5,6,8,10] or charttype != 'basic':
                    fac =  diff*2 / (suphoff-infhoff)
                else:
                    fac =  diff / (suphoff-infhoff)
                suphoff = hroff
                vcr = vi*fac
                if pl in [3,8,9] and charttype == 'basic':
                    vcr = vi - vcr
                cutright = True
            if pl in [0,1,2,5,6,10] or charttype != 'basic':
                if cutleft:
                    path=[(infhoff,pvoff-vcl),(phoff,pvoff-vi),(suphoff,pvoff),
                            (phoff,pvoff+vi),(infhoff,pvoff+vcl)]
                elif cutright:
                    path=[(infhoff,pvoff),(phoff,pvoff-vi),(suphoff,pvoff-vcr),
                            (suphoff,pvoff+vcr),(phoff,pvoff+vi)]
                else:
                    path=[(infhoff,pvoff),(phoff,pvoff-vi),(suphoff,pvoff),
                            (phoff,pvoff+vi)]
            elif pl in [4,7]:
                if cutleft:
                    path = [(infhoff,pvoff-vcl),(suphoff,pvoff),(infhoff,pvoff+vcl)]
                elif cutright:
                    path = [(infhoff,pvoff-vi),(infhoff,pvoff+vi),
                            (suphoff,pvoff+vcr),(suphoff,pvoff-vcr)]
                else:
                    path = [(infhoff,pvoff-vi),(infhoff,pvoff+vi),(suphoff,pvoff)]
            elif pl in [3,9]:
                if cutleft:
                    path = [(infhoff,pvoff-vcl),(suphoff,pvoff-vi),(suphoff,pvoff+vi),
                        (infhoff,pvoff+vcl)]
                elif cutright:
                    path = [(suphoff,pvoff-vcr),(suphoff,pvoff+vcr),(infhoff,pvoff)]
                else:
                    path = [(infhoff,pvoff),(suphoff,pvoff-vi),(suphoff,pvoff+vi)]
            elif pl in [8]:
                if cutleft:
                    path = [(infhoff,pvoff-vcl),(infhoff,pvoff+vcl),(phoff,pvoff),
                            (suphoff,pvoff+vi),(suphoff,pvoff-vi),(phoff,pvoff)] 
                elif cutright:
                    path = [(infhoff,pvoff-vi),(infhoff,pvoff+vi),(phoff,pvoff),
                            (suphoff,pvoff+vcr),(suphoff,pvoff-vcr),(phoff,pvoff)] 
                else:
                    path = [(infhoff,pvoff-vi),(infhoff,pvoff+vi),(phoff,pvoff),
                            (suphoff,pvoff+vi),(suphoff,pvoff-vi),(phoff,pvoff)] 
            
            #if charttype == 'soul':
            #    set_soul_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
            #elif charttype == 'nodal':
            #    col = aspcol[asp]
            #    col = list(col); col.append(0.4)
            #    cr.set_source_rgba(*col)
            #else:
            #    set_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
            if self.surface.__class__.__name__ == 'DrawPdf':
                col = aspcol[asp] 
                cr.set_source_rgb(*col)
            else:
                if charttype == 'soul' or charttype == 'dharma' : 
                    set_soul_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                elif charttype == 'nodal':
                    col = aspcol[asp]
                    col = list(col); col.append(0.55)
                    cr.set_source_rgba(*col)
                else:
                    set_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)

            for i,p in enumerate(path):
                if i == 0:
                    cr.move_to(*p)
                else:
                    cr.line_to(*p)
            cr.close_path()
            cr.fill()
            #cr.fill_preserve()
            if charttype == 'soul':
                cr.set_source_rgb(0.7,0,0.7)
            else:
                cr.set_source_rgb(*aspcol[asp])
            #cr.stroke()
        
            alet = self.asplet[asp] 
            layout.set_text(alet)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            
            if pl == 8 and charttype == 'basic':
                cr.move_to(phoff-w/2,pvoff-h)
            else:
                cr.move_to(phoff-w/2,pvoff-h/1.8)
                cr.set_source_rgb(1,1,1)
            cr.layout_path(layout)
            cr.fill()

    def d_follow_house(self,cr,layout,bh,chartob):
        font = pango.FontDescription("Astro-Nex")
        font.set_size(int(9*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        charttype = chartob.name
        cycles =  self.chart.get_cycles(curr.date.dt)
        follow_house_t = self.chart.house_time_lapsus((bh+1)%12,cycles)
        hoff = self.hoff
        voff = self.voff
        hroff = self.hroff
        moff = self.gridw/72
        vi = voff/24
        intensity = self.intensity
        follow_bhouse = chartob.get_house_age_prog((bh+1)%12) 
        tts = [t for t in follow_bhouse if t['cl'] == 'asp']
        for t in tts:
            date = datetime(t['year'],t['mon'],t['day'],0,0,0)
            asp,pl = t['lab']
            pvoff = self.baselines[plorder.index(pl)]
            phoff = date - follow_house_t['begin']
            acl = aspclass[asp]
            if charttype == 'nodal':
                orb = nodorb[acl] 
                halfdays = orb * 6 /self.sizes[bh] * 365
            elif charttype == 'basic':
                if pl < 10:
                    orb = orbs[planclass[pl]][acl]
                else:
                    orb = 1.0
                halfdays = orb * 6 /self.sizes[bh] * 365
            else:
                halfdays = 365/2
            inf = phoff.days - halfdays
            sup = phoff.days + halfdays
            phoff = (hoff*6*phoff.days)/(follow_house_t['lapsus'].days) + hoff
            infhoff = hoff*6*inf/(follow_house_t['lapsus'].days) + hoff
            suphoff = hoff*6*sup/(follow_house_t['lapsus'].days) + hoff
            if infhoff < hoff:
                asplength = suphoff - infhoff
                steps = int(math.ceil(asplength/moff))
                vstep = vi*2/steps
                begint = int(infhoff/moff)-12
                for s in range(steps):
                    if begint+s >= 0: continue
                    intix = begint+s+72
                    if pl in [0,1,2,5,6,10] or charttype != 'basic':
                        if s < steps/2:
                            intensity[intix] += vstep*s
                        elif s > steps/2:
                            intensity[intix] += (steps-1-s)*vstep
                        else:
                            intensity[intix] += (steps-1-s)*vstep
                    elif pl in [3,9]:
                        intensity[intix] += vstep*s
                    elif pl in [4,7]:
                        intensity[intix] += (steps-1-s)*vstep
                    else:
                        if s < steps/2:
                            intensity[intix] += (steps-s*2)*vstep
                        else:
                            intensity[intix] += vstep*s
                
                diff = hoff - infhoff
                if pl in [0,1,2,5,6,8,10] or charttype != 'basic':
                    fac =  diff*2 / (suphoff-infhoff)
                else:
                    fac =  diff / (suphoff-infhoff)
                infhoff = hroff - diff
                vcl = vi*fac
                if pl in [4,7,8] and charttype == 'basic':
                    vcl = vi - vcl
                if pl in [0,1,2,3,5,6,9,10] or charttype != 'basic':
                    path = [(infhoff,pvoff),(hroff,pvoff-vcl),
                            (hroff,pvoff+vcl)]
                elif pl in [4,7,8]:
                    path = [(infhoff,pvoff-vi),(hroff,pvoff-vcl),
                            (hroff,pvoff+vcl),(infhoff,pvoff+vi)]
                
                #if charttype == 'soul':
                #    set_soul_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                #elif charttype == 'nodal':
                #    col = aspcol[asp]
                #    col = list(col); col.append(0.4)
                #    cr.set_source_rgba(*col)
                #else:
                #    set_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                if self.surface.__class__.__name__ == 'DrawPdf':
                    col = aspcol[asp] 
                    cr.set_source_rgb(*col)
                else:
                    if charttype == 'soul' or charttype == 'dharma' : 
                        set_soul_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                    elif charttype == 'nodal':
                        col = aspcol[asp]
                        col = list(col); col.append(0.4)
                        cr.set_source_rgba(*col)
                    else:
                        set_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                
                for i,p in enumerate(path):
                    if i == 0:
                        cr.move_to(*p)
                    else:
                        cr.line_to(*p)
                cr.close_path()
                cr.fill()
                #cr.fill_preserve()
                if charttype == 'soul':
                    cr.set_source_rgb(0.7,0,0.7)
                else:
                    cr.set_source_rgb(*aspcol[asp])
                #cr.stroke()
                cr.set_source_rgb(*aspcol[asp])
                alet = self.asplet[asp] 
                layout.set_text(alet)
                ink,logical = layout.get_extents()
                w = logical[2]/pango.SCALE
                h = logical[3]/pango.SCALE
                cr.move_to(hroff+w*0.3,pvoff-h/2)
                cr.layout_path(layout)
                cr.fill()

    def d_prev_house(self,cr,layout,bh,chartob):
        font = pango.FontDescription("Astro-Nex")
        font.set_size(int(9*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        charttype = chartob.name
        cycles =  self.chart.get_cycles(curr.date.dt)
        prev_house_t = self.chart.house_time_lapsus((bh+11)%12,cycles)
        hoff = self.hoff
        voff = self.voff
        hroff = self.hroff
        moff = self.gridw/72
        vi = voff/24
        intensity = self.intensity
        prev_bhouse = chartob.get_house_age_prog((bh+11)%12) 
        tts = [t for t in prev_bhouse if t['cl'] == 'asp']
        for t in tts:
            date = datetime(t['year'],t['mon'],t['day'],0,0,0)
            asp,pl = t['lab']
            pvoff = self.baselines[plorder.index(pl)]
            phoff = date - prev_house_t['begin']
            acl = aspclass[asp]
            if charttype == 'nodal':
                orb = nodorb[acl] 
                halfdays = (orb * 6 /self.sizes[(bh+11)%12]) * 365
            elif charttype == 'basic':
                if pl < 10:
                    orb = orbs[planclass[pl]][acl]
                else:
                    orb = 1.0
                halfdays = (orb * 6 /self.sizes[(bh+11)%12]) * 365
            else:
                halfdays = 365/2
            inf = phoff.days - halfdays
            sup = phoff.days + halfdays
            phoff = (hoff*6*phoff.days)/(prev_house_t['lapsus'].days) + hoff
            infhoff = hoff*6*inf/(prev_house_t['lapsus'].days) + hoff
            suphoff = hoff*6*sup/(prev_house_t['lapsus'].days) + hoff
            if suphoff > hroff:
                asplength = suphoff - infhoff
                steps = int(math.ceil(asplength/moff))
                vstep = vi*2/steps
                begint = int(infhoff/moff)-12
                for s in range(steps):
                    if begint+s < 72: continue
                    intix = begint+s-72
                    if pl in [0,1,2,5,6,10] or charttype != 'basic':
                        if s < steps/2:
                            intensity[intix] += vstep*s
                        elif s > steps/2:
                            intensity[intix] += (steps-1-s)*vstep
                        else:
                            intensity[intix] += (steps-1-s)*vstep
                    elif pl in [3,9]:
                        intensity[intix] += vstep*s
                    elif pl in [4,7]:
                        intensity[intix] += (steps-1-s)*vstep
                    else:
                        if s < steps/2:
                            intensity[intix] += (steps-s*2)*vstep
                        else:
                            intensity[intix] += vstep*s

                diff = suphoff - hroff
                if pl in [0,1,2,5,6,8,10] or charttype != 'basic':
                    fac =  diff*2 / (suphoff-infhoff)
                else:
                    fac =  diff / (suphoff-infhoff)
                suphoff = suphoff - hoff*6
                vcr = vi*fac
                if pl in [3,8,9] and charttype == 'basic':
                    vcr = vi - vcr
                if pl in [0,1,2,4,5,6,7,10] or charttype != 'basic':
                    path = [(hoff,pvoff-vcr),(suphoff,pvoff),(hoff,pvoff+vcr)]
                elif pl in [3,8,9]:
                    path = [(hoff,pvoff-vcr),(suphoff,pvoff-vi),
                            (suphoff,pvoff+vi),(hoff,pvoff+vcr)]
                
                #if charttype == 'soul':
                #    set_soul_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                #elif charttype == 'nodal':
                #    col = aspcol[asp]
                #    col = list(col); col.append(0.4)
                #    cr.set_source_rgba(*col)
                #else:
                #    set_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                
                if self.surface.__class__.__name__ == 'DrawPdf':
                    col = aspcol[asp] 
                    cr.set_source_rgb(*col)
                else:
                    if charttype == 'soul' or charttype == 'dharma' : 
                        set_soul_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                    elif charttype == 'nodal':
                        col = aspcol[asp]
                        col = list(col); col.append(0.4)
                        cr.set_source_rgba(*col)
                    else:
                        set_source(cr,list(aspcol[asp]),path,pl,hoff,asplength)
                
                for i,p in enumerate(path):
                    if i == 0:
                        cr.move_to(*p)
                    else:
                        cr.line_to(*p)
                cr.close_path()
                cr.fill()
                #cr.fill_preserve()
                if charttype == 'soul':
                    cr.set_source_rgb(0.7,0,0.7)
                else:
                    cr.set_source_rgb(*aspcol[asp])
                #cr.stroke()
                cr.set_source_rgb(*aspcol[asp])
                
                alet = self.asplet[asp] 
                layout.set_text(alet)
                ink,logical = layout.get_extents()
                w = logical[2]/pango.SCALE
                h = logical[3]/pango.SCALE
                cr.move_to(hoff-w*1.3,pvoff-h/2)
                cr.layout_path(layout)
                cr.fill()

    def d_release(self,cr,hpoint):
        global release,biodate
        if release: 
            y,m,d = biodate.year,biodate.month,biodate.day
            strdate = "%s/%s/%s" % (str(d).rjust(2,'0'),str(m).rjust(2,'0'),str(y))
            font = self.opts.font.split(" ")[0].rstrip()
            cr.select_font_face(font)
            font_size = 11.0 * self.minim * MAGICK_FONTSCALE
            cr.set_font_size(font_size) 
            x_b,y_b,w,h,x_a,y_a = cr.text_extents(strdate) 
            cr.move_to(hpoint,self.voff)
            cr.rel_line_to(0,-h)
            cr.rel_line_to(w+x_b*10,0)
            cr.rel_line_to(0,h)
            cr.close_path()
            cr.set_source_rgb(1,1,0.6)
            cr.fill()
            cr.set_source_rgb(0,0,0.5)
            cr.move_to(hpoint+x_b*2*self.minim*MAGICK_FONTSCALE,self.voff)
            cr.text_path(strdate)
            cr.fill()
            if self.surface.__class__.__name__ is 'DrawMaster':
                release = False
    
def sign_col_soul(col,voff):
    colin = list(col)
    pat = cairo.LinearGradient(0,voff*1.4,0,voff*1.4+voff/8) 
    colin = [0.0] + list(col) + [0.8]
    pat.add_color_stop_rgba(*colin)
    colin = [0.5] + list(col) + [0.3]
    pat.add_color_stop_rgba(*colin)
    colin = list(col)
    colin = [1.0] + list(col) + [0.8]
    pat.add_color_stop_rgba(*colin)
    return pat

def sign_col_dharma(col,voff):
    colin = list(col)
    pat = cairo.LinearGradient(0,voff*1.4,0,voff*1.4+voff/8) 
    colin = [0.0] + list(col) + [0.3]
    pat.add_color_stop_rgba(*colin)
    colin = [0.5] + list(col) + [0.8]
    pat.add_color_stop_rgba(*colin)
    colin = list(col)
    colin = [1.0] + list(col) + [0.3]
    pat.add_color_stop_rgba(*colin)
    return pat

def set_nod_source(cr,col,path,pl,hoff,alen):
    lcutoff = None; rcutoff = None
    x = []; y = []
    for p in path:
        x.append(p[0])
        y.append(p[1])
    xmn = min(x); xmx = max(x)
    mid = alen / 2
    if xmn == hoff:
        lcutoff = (alen - (xmx - xmn)) / mid
    elif xmx >= hoff+hoff*6:
        rcutoff = (alen - (xmx - xmn)) / mid 

def set_source(cr,col,path,pl,hoff,alen):
    lcutoff = None; rcutoff = None
    x = []; y = []
    for p in path:
        x.append(p[0])
        y.append(p[1])
    xmn = min(x); xmx = max(x)
    mid = alen / 2
    if xmn == hoff:
        lcutoff = (alen - (xmx - xmn)) / mid
    elif xmx >= hoff+hoff*6:
        rcutoff = (alen - (xmx - xmn)) / mid 

    bl = min(y) + (max(y) - min(y))/2
    pat = cairo.LinearGradient(xmn,bl,xmx,bl) 
    
    if pl in [0,1,2,5,6,10]:
        colin = col[:]
        if lcutoff is None: colin.append(0.1)
        else: colin.append(lcutoff) 
        colin.insert(0,0)
        pat.add_color_stop_rgba(*colin)
        colin = col[:]
        colin.append(1) 
        if lcutoff is None and rcutoff is None: 
            colin.insert(0,0.5)
        else:
            if not lcutoff is None: 
                colin.insert(0,0.5-(lcutoff/2))
            elif not rcutoff is None: 
                colin.insert(0,0.5+(rcutoff/2))
        pat.add_color_stop_rgba(*colin)
        colin = col[:]
        if rcutoff is None: colin.append(0.1)
        else: colin.append(rcutoff) 
        colin.insert(0,1)
        pat.add_color_stop_rgba(*colin)
    elif pl in [3,9]:
        colin = col[:]
        if lcutoff is None: colin.append(0.1)
        else: colin.append(0.5*lcutoff) 
        colin.insert(0,0)
        pat.add_color_stop_rgba(*colin)
        colin = col[:]
        if rcutoff is None: colin.append(1)
        else: colin.append(0.5+0.5*(1-rcutoff))
        colin.insert(0,1)
        pat.add_color_stop_rgba(*colin)
    elif pl in [4,7]:
        colin = col[:]
        if lcutoff is None: colin.append(1)
        else: colin.append(0.5+0.5*(1-lcutoff))
        colin.insert(0,0)
        pat.add_color_stop_rgba(*colin)
        colin = col[:]
        if rcutoff is None: colin.append(0.1)
        else: colin.append(0.5*rcutoff) 
        colin.insert(0,1)
        pat.add_color_stop_rgba(*colin)
    else:
        colin = col[:]
        if lcutoff is None: colin.append(1)
        else: colin.append(1-lcutoff) 
        colin.insert(0,0)
        pat.add_color_stop_rgba(*colin)
        colin = col[:]
        colin.append(0.1) 
        if not lcutoff is None: 
            colin.insert(0,0.5-(lcutoff/2))
        elif not rcutoff is None: 
            colin.insert(0,0.5+(rcutoff/2))
        else: 
            colin.insert(0,0.5)
        pat.add_color_stop_rgba(*colin)
        colin = col[:]
        if rcutoff is None: colin.append(1)
        else: 
            colin.append(0.5+0.5*(1-rcutoff))
        colin.insert(0,1)
        pat.add_color_stop_rgba(*colin)
    
    cr.set_source(pat)

def set_soul_source(cr,col,path,pl,hoff,alen):
    lcutoff = None; rcutoff = None
    x = []; y = []
    for p in path:
        x.append(p[0])
        y.append(p[1])
    xmn = min(x); xmx = max(x)
    mid = alen / 2
    if xmn == hoff:
        lcutoff = (alen - (xmx - xmn)) / mid
    elif xmx >= hoff+hoff*6:
        rcutoff = (alen - (xmx - xmn)) / mid 

    bl = min(y) + (max(y) - min(y))/2
    pat = cairo.LinearGradient(xmn,bl,xmx,bl) 
    
    colin = col[:]
    if lcutoff is None: colin.append(0.1)
    else: colin.append(lcutoff) 
    colin.insert(0,0)
    pat.add_color_stop_rgba(*colin)
    colin = col[:]
    colin.append(1) 
    if lcutoff is None and rcutoff is None: 
        colin.insert(0,0.5)
    else:
        if not lcutoff is None: 
            colin.insert(0,0.5-(lcutoff/2))
        elif not rcutoff is None: 
            colin.insert(0,0.5+(rcutoff/2))
    pat.add_color_stop_rgba(*colin)
    colin = col[:]
    if rcutoff is None: colin.append(0.1)
    else: colin.append(rcutoff) 
    colin.insert(0,1)
    pat.add_color_stop_rgba(*colin)
    
    cr.set_source(pat)
