# -*- coding: utf-8 -*-
import cairo, pango
import math
from itertools import izip,cycle
from math import pi as PI
from roundedcharts import RadixChart, NodalChart
from .. boss import boss

PHI = 1 / ((1+math.sqrt(5))/2)
RAD = PI /180
MAGICK_FONTSCALE = 0.00246

R_INNER = 0.48     #shared
R_RULEDINNER = 0.65     #shared

R_VERYINNER = 0.065
R_YEARS = 0.8
R_LOW = 0.965
R_INV = 0.993
R_ASP = 0.435

def rebuild_paths(cr,paths):
    dispatch = { cairo.PATH_MOVE_TO: 'move_to',cairo.PATH_LINE_TO:'line_to',
                cairo.PATH_CURVE_TO:'curve_to', cairo.PATH_CLOSE_PATH:'close_path'} 
    for type, points in paths:
        getattr(cr,dispatch[type])(*points)

class CoreMixin(object):
    cuspnames = ( 'AC','2','3','IC','5','6','DC','8','9','MC','11','12' )

    def __init__(self,zodiac,surface):
        self.auxcol = zodiac.auxcolors
        self.surface = surface
    
    def d_ruline(self,cr,chartob):
        cr.set_source_rgb(0,0,0.4)
        cr.set_line_width(0.5)
        cr.move_to(0,0)
        cr.line_to(*self.ruline)
        cr.stroke()
        x,y = self.ruline
        cr.arc(x/2,y/2,2,0,360*RAD)
        cr.fill()
        x,y = self.ruline
        deg = math.degrees(math.atan2(y,x))
        self.surface.rulinepending = chartob.adjust_degpe(deg,chartob.chart)
    
    def d_radial_line(self,cr,radius,inset,angle):
        cr.move_to(inset*math.cos(angle),inset*math.sin(angle))
        cr.line_to(radius*math.cos(angle),radius*math.sin(angle))
        cr.stroke()
    
    def set_font(self,cr,size,bold=False):
        font = self.opts.font.split(" ")[0].rstrip()
        slant = cairo.FONT_SLANT_NORMAL
        weight =cairo.FONT_WEIGHT_NORMAL
        if bold:
            weight =cairo.FONT_WEIGHT_BOLD
        cr.select_font_face(font,slant,weight)
        cr.set_font_size(size)

    def d_radial_text(self,cr,radius,angle,text):
        _, _, width, height, _, _ = cr.text_extents(text)
        x = radius*math.cos(angle); y= radius*math.sin(angle)
        cr.move_to(x-width/2,y+height/2)
        cr.show_text(text)
    
    def d_gold_circle(self,cr,angle,radius,scl):
        cr.arc(radius*math.cos(angle),
               radius*math.sin(angle),1.5*scl,0,360*RAD)
        cr.fill() 
    
    def d_inner_circles(self,cr,radius):
        cr.save()
        cr.set_source_rgb(1,1,1)
        cr.arc(0,0,radius*R_VERYINNER,0,360*RAD)
        cr.fill_preserve()
        cr.set_source_rgb(0,0,0)
        cr.set_line_width(0.35*cr.get_line_width())
        cr.stroke()
        cr.arc(0,0,radius*R_INNER,0,360*RAD)
        cr.stroke() 
        cr.restore()

    def d_pe_zones(self,cr,radius,chartob):
        cross = chartob.chart.calc_cross_points()
        node = chartob.get_planets()[10] 
        offset = chartob.get_cross_offset()
        cp1_ang = chartob.sup_cross(offset-cross)
        cp2_ang = chartob.sup_cross(offset-cross-180)
        nod_ang = chartob.sup_cross(offset-node)
        if cp1_ang < 0: cp1_ang += 360
        if cp2_ang < 0: cp2_ang += 360
        if nod_ang < 0: nod_ang += 360
        cp1_ang %= 360
        cp2_ang %= 360
        nod_ang %= 360
        if cp1_ang > cp2_ang:
            cp1_ang,cp2_ang = cp2_ang,cp1_ang

        cp1_ang = cp1_ang * RAD
        cp2_ang = cp2_ang * RAD
        nod_ang = nod_ang * RAD

        cols = chartob.pez_cols
        cr.set_source_rgb(*cols['paleblue'])
        cr.move_to(0,0)
        cr.arc(0,0,radius*R_INNER,cp1_ang,180*RAD)
        cr.fill()

        cr.set_source_rgb(*cols['palegreen'])
        cr.move_to(0,0)
        cr.arc(0,0,radius*R_INNER,nod_ang,cp1_ang)
        cr.fill()

        cr.set_source_rgb(*cols['paleblue'])
        cr.move_to(0,0)
        cr.arc(0,0,radius*R_INNER,cp2_ang,nod_ang)
        cr.fill()

        cr.set_source_rgb(*cols['teal'])
        cr.move_to(0,0)
        if nod_ang > cp2_ang:
            cr.arc(0,0,radius*R_INNER*0.7,cp2_ang,nod_ang)
        else:
            cr.arc(0,0,radius*R_INNER*0.7,cp2_ang,0)
        cr.fill()

        if nod_ang > cp2_ang:
            cr.set_source_rgb(*cols['darkgreen'])
            cr.move_to(0,0)
            cr.arc(0,0,radius*R_INNER*0.7,nod_ang,0)
            cr.fill()
        
        cr.set_source_rgb(*cols['pink'])
        cr.move_to(0,0)
        cr.arc(0,0,radius*R_INNER,180*RAD,cp2_ang)
        cr.fill()
        cr.set_source_rgb(*cols['darkblue'])
        cr.move_to(0,0)
        cr.arc(0,0,radius*R_INNER*0.7,180*RAD,cp2_ang)
        cr.fill()

    def d_subject_circles(self,cr,radius):
        cr.save()
        cr.set_source_rgb(0,0,0)
        cr.arc(0,0,radius*0.85,0,360*RAD)
        cr.set_line_width(0.35*cr.get_line_width())
        cr.stroke()
        cr.arc(0,0,radius*0.75,0,360*RAD)
        cr.stroke() 
        cr.restore()

    def d_year_lines(self,cr,radius,chartob):
        chart = chartob.chart
        year = int(chart.date.split('-')[0]) - 1
        cycles = chart.get_cycles(boss.state.date.dt)
        year += 72*cycles
        sizes = chartob.get_sizes()
        font_size = 10.0 * radius * MAGICK_FONTSCALE
        radius = radius * R_YEARS
        scl = radius * chartob.plan_scale
        inset = scl * 6 + radius
        offsets = chartob.get_cusps_offsets()
        cr.save()
        cr.set_source_rgb(0.4,0.4,0.4)
        cr.set_line_width(0.5*cr.get_line_width())
        self.set_font(cr,font_size)
        for off,size in izip(offsets,sizes):
            year += 1
            ysize = size / 6
            for j in range(1,6):
                angle = (off - ysize * j) * RAD
                self.d_radial_line(cr,radius,inset,angle)
                year += 1 
                if j == 4:
                    yr = str(year)[2:]
                    self.d_radial_text(cr,radius+16,angle,yr)
        cr.restore()

    def d_golden_points(self,cr,radius,chartob):
        offset = chartob.get_gold_offset()
        lowradius = radius * R_YEARS * R_LOW
        invradius = radius * R_YEARS * R_INV
        low_inv_gen = chartob.get_golden_points()
        scl = radius * chartob.plan_scale
        if self.surface .__class__.__name__ == 'DrawPdf':
            scl *= 1.3
        cr.save()
        for house,low,inv in low_inv_gen:
            cr.set_source_rgb(*self.auxcol['low']) 
            angle = (offset-house-low)*RAD
            self.d_gold_circle(cr,angle,lowradius,scl) 
            cr.set_source_rgb(*self.auxcol['inv']) 
            angle = (offset-house-inv)*RAD
            self.d_gold_circle(cr,angle,invradius,scl) 
        cr.restore()
    
    def make_all_rulers(self,cr,radius,chartob,mid=False):
        R_RULEDINNER, R_RULEDOUTER, R_RULEDMID = chartob.get_ruled()
        rules = { R_RULEDOUTER: [0.016,0.010,0.004], 
                R_RULEDMID: [0.014,0.010,0.004],
                R_RULEDINNER:  [-0.018,-0.012,-0.004]}
        offset = chartob.get_offset()
        self.make_ruler(cr,radius,chartob,R_RULEDOUTER,rules,offset)
        self.make_ruler(cr,radius,chartob,R_RULEDINNER,rules,offset)
        if mid:
            self.make_ruler(cr,radius,chartob,R_RULEDMID,rules,offset)

    def make_ruler(self,cr,radius,chartob,rule,rules,offset):
        insets = [radius * i for i in rules[rule]]
        radius = radius * rule 
        
        default = insets.pop()
        insets = dict(zip((0,5),insets))
        try:
            col = chartob.rulecol
        except AttributeError:
            col = (0,0,0)
        cr.save()
        cr.set_source_rgb(*col)
        if chartob.name == 'soul':
            cr.set_source_rgb(0.2,0,0.2)
        cr.set_line_width(0.5*cr.get_line_width())
        for i in xrange(360):
            angle = (offset+i) * RAD
            inset = radius - insets.get(i%10,default)
            self.d_radial_line(cr,radius,inset,angle)
        cr.restore()

    def d_radial_lines(self,cr,radius,chartob):
        sign_cusps = chartob.get_sign_cusps()
        fac,ins,_ = chartob.get_radial_param()
        radius = radius * fac
        cr.save()
        cr.set_source_rgb(0,0,0)
        if chartob.name == 'soul':
            cr.set_source_rgb(0.2,0,0.2)
        cr.set_line_width(0.5*cr.get_line_width())
        inset = ins * radius
        for i in sign_cusps:
            angle = (180-i) * RAD
            self.d_radial_line(cr,radius+inset,radius,angle)
        cr.restore()
    
    def d_cross_points(self,cr,radius,chartob):
        fac,ins,_ = chartob.get_radial_param()
        radius = radius * fac 
        cr.save()
        if self.surface .__class__.__name__ == 'DrawPdf':
            cr.set_line_width(0.75*cr.get_line_width())
        else:
            cr.set_line_width(0.9*cr.get_line_width())
        cr.set_source_rgb(0.9,0,0.9)
        inset = ins * radius * 1.25
        cross = chartob.chart.calc_cross_points()
        offset = chartob.get_cross_offset()
        for i in (0,180):
            angle = chartob.sup_cross(offset-cross-i) * RAD 
            self.d_radial_line(cr,radius+inset,radius*0.965,angle)
        cr.restore()

    def draw_signs(self,cr,radius,chartob):
        radius = radius * chartob.get_sign_radfac()
        scly = chartob.scl * radius
        offsets = chartob.get_sign_offsets()
        zodiac = chartob.get_zod_iter()
        paint = self.paint[chartob.name]
        #pdfsoul = chartob.name == 'soul' and self.surface.__class__.__name__  == 'DrawPdf'
        try:
            sign_fac = chartob.sign_fac
        except AttributeError:
            sign_fac = 1.02

        #if pdfsoul:
        #    w = self.surface.w; h = self.surface.h 
        #    tmp_cr = cr
        #    target = cr.get_target()
        #    #over = target.create_similar(cairo.CONTENT_COLOR_ALPHA,int(w),int(h))
        #    over = target.create_similar(cairo.CONTENT_ALPHA,int(w),int(h))
        #    over_cr = cairo.Context(over)
        #    over_cr.translate(w/2,h/2)
        #    over_cr.set_line_width(0.5 * cr.get_line_width())
        #    cr = over_cr

        for i,z in enumerate(zodiac):
            cr.save()
            cr.rotate(offsets.next() * RAD)
            x_bearing,_,width,_,_,_ = z.extents
            sclx = chartob.get_sclx(scly)
            cr.translate(sclx*(-width/2-x_bearing),-radius*sign_fac)
            if chartob.name == 'plagram':
                sclyy = scly / 2.0
                col = self.plagramcol[i%4]
            else:
                sclyy = scly
                col = z.col
            cr.scale(sclx,sclyy)
            rebuild_paths(cr,z.paths)
            #print z.let, z.col
            paint(self,cr,col,radius)
            cr.restore()
        
        #if pdfsoul:
        #    cr = tmp_cr
        #    cr.set_source_surface(over,-w/2,-h/2)
        #    cr.paint()

    def paint_basic_sign(self,cr,color,radius=None):
        cr.set_source_rgb(*color)
        cr.fill()

    def paint_soul_sign(self,cr,color,radius):
        vdistance = radius*1.2 - radius
        pat = cairo.LinearGradient(0,0,0,-vdistance)
        colstop = [0.0] + list(color) + [0.4]
        pat.add_color_stop_rgba(*colstop)
        colstop = [0.3] + list(color) + [0.2]
        pat.add_color_stop_rgba(*colstop)
        colstop = [1.0] + list(color) + [0.5]
        pat.add_color_stop_rgba(*colstop)
        cr.set_source(pat)
        cr.fill_preserve()
        cr.set_source_rgb(*color)
        cr.stroke() 

    def paint_radsoul_sign(self,cr,color,radius):
        vdistance = radius*1.25 - radius
        pat = cairo.LinearGradient(0,0,0,-vdistance)
        colstop = [0.0] + list(color) + [0.3]
        pat.add_color_stop_rgba(*colstop)
        colstop = [1.0] + list(color) + [1.0]
        pat.add_color_stop_rgba(*colstop)
        cr.set_source(pat)
        cr.fill()
    
    def paint_nod_sign(self,cr,color,radius=None):
        #path = cr.copy_path()
        cr.set_source_rgba(*(list(color) + [0.1]))
        cr.fill_preserve()
        #cr.fill()
        #cr.append_path(path)
        cr.set_source_rgb(*color)
        cr.stroke()

    paint = {'basic': paint_basic_sign, 'soul': paint_soul_sign, 'nodal':
            paint_nod_sign, 'radsoul': paint_radsoul_sign, 'plagram': paint_basic_sign}
    
    #### plan and lines
    def set_plots(self,chartob,plot="plot1"):
        plots = chartob.inject_plan_degrees()
        setattr(chartob.plmanager,plot,plots)
        return plots

    def draw_planets(self,cr,radius,chartob,plot="plot1"):
        chartob.check_moons()
        plots = self.set_plots(chartob,plot)
        glyphs = chartob.plmanager.glyphs 
        scl = radius * chartob.plan_scale
        r_pl = radius *  chartob.get_rpl()
        click_col = chartob.get_col() 
        for glyph,plot in izip(glyphs,plots):
            cr.save()
            rpl = r_pl * plot.fac
            angle = (plot.degree + plot.corr) * RAD
            x_b,_,w,h,_,_ = glyph.extents
            shiftx = scl*(w+x_b)/2; shifty = scl*h/2
            cr.translate(rpl*math.cos(angle) - shiftx, rpl*math.sin(angle) + shifty)
            if chartob.__class__.__name__ == "CounterChart":
                rotangle = chartob.click.houses[0] - chartob.chart.houses[0]
                cr.translate(shiftx, -shifty)
                cr.rotate(rotangle * RAD)
            cr.scale(scl,scl)
            rebuild_paths(cr,glyph.paths)
            if click_col:
                cr.set_source_rgb(*self.auxcol[click_col])
            else:
                cr.set_source_rgb(*glyph.col) 
            cr.fill()
            cr.restore() 
    
    def draw_urnodal_planets(self,cr,radius,chartob,plot="plot1"):
        cusps = chartob.get_cusps_offsets()
        cusps = [ c % 360 for c in cusps ] 
        sizes = chartob.get_sizes()
        chartob.check_moons()
        chartob.__class__ = NodalChart
        
        plots = self.set_plots(chartob,plot)
        glyphs = chartob.plmanager.glyphs 
        scl = radius * chartob.plan_scale
        r_pl = radius *  chartob.get_rpl()
        for glyph,plot in izip(glyphs,plots):
            cr.save()
            rpl = r_pl * plot.fac
            
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
            cr.set_source_rgb(*glyph.col) 
            cr.fill()
            cr.restore() 
        chartob.__class__ = RadixChart


    def make_plines(self,cr,radius,chartob,pos='EXT',plot="plot1"):
        radius = radius * chartob.pl_radfac[pos]
        inset = radius * chartob.pl_insets[pos]
        line_width = chartob.pl_line_width[pos]
        click_col = chartob.get_col()
        lw = cr.get_line_width()
        if click_col:
            cr.set_source_rgb(*self.auxcol[click_col])
        cr.save()
        cr.set_line_width(line_width*lw) 
        plots = getattr(chartob.plmanager,plot)
        glyphs = chartob.plmanager.glyphs
        for glyph,plt in izip(glyphs,plots):
            angle = plt.degree * RAD
            if not click_col:
                cr.set_source_rgb(*glyph.col) 
            self.d_radial_line(cr,radius,radius-inset,angle)
        cr.restore()
    
    def draw_ap_aspects(self,cr,radius,chartob,man,pe):
        chart = chartob.chart
        if chartob.name == 'nodal':
            pedraw = pe + 180 - chartob.chart.planets[10]
        else: 
            pedraw = 180 + chartob.chart.houses[0] - pe
        pe_col = chartob.pe_col
        r = radius
        rap = (radius/R_ASP)*R_RULEDINNER
        xap = math.cos(pedraw*RAD); yap = math.sin(pedraw*RAD) 
        cr.set_line_width(0.5 * cr.get_line_width())
        cr.set_source_rgba(*(list(pe_col)+[0.65]))
        scl = radius * chartob.plan_scale
        cr.arc(rap*xap,rap*yap,12*scl,0,360*RAD)
        cr.fill()
        cr.set_source_rgb(*pe_col)
        cr.move_to(r*xap,r*yap)
        cr.line_to(rap*xap,rap*yap)
        cr.stroke()
        man.manage_now_aspects(cr,radius,chartob.get_planets(),pe,pedraw)
        try:
            if not self.rightdraw:
                self.surface.pepending[0:2] = True,pe
            else:
                self.surface.pepending[-1] = pe
        except AttributeError:
            pass
    
    def d_lonely_cusp(self,cr,radius,chartob):
        chart = chartob.chart
        offh = 180 + chart.houses[0] - chart.houses[9]
        cr.save()
        fcusp = radius * 0.5
        r = radius * 0.57
        cr.set_source_rgb(1,0.8,0.8)
        #cr.set_line_width(cr.get_line_width())
        self.d_radial_line(cr,fcusp,r,offh*RAD)
        cr.restore() 

    def draw_double_cusp(self,cr,radius,chartob):
        offset1 = 180 + chartob.chart.houses[0]
        offset2 = 180 + chartob.click.houses[0]
        clickmode = boss.state.clickmode
        cr.save()
        #lw = cr.get_line_width()
        font_size = 16.0 * radius * MAGICK_FONTSCALE
        self.set_font(cr,font_size)
        fcusp = radius * 1.1
        for i in [0,9]:
            offh1 = offset1 - chartob.chart.houses[i]
            offh2 = offset1 - chartob.click.houses[i]
            if clickmode == 'click':
                cr.set_source_rgb(*self.auxcol['click1'])
            else:
                cr.set_source_rgb(*self.auxcol['click2'])
            cr.move_to(radius*math.cos(offh1*RAD),radius*math.sin(offh1*RAD))
            x = fcusp*math.cos(offh1*RAD)
            y = fcusp*math.sin(offh1*RAD)
            cr.line_to(x,y)
            cr.stroke() 
            thiscusp = self.cuspnames[i]
            if i == 0: x *= 1.01; y -= 2
            cr.move_to(x*1.007,y*1.007)
            cr.show_text(thiscusp)
            #if chartob.name != 'soul':
            if clickmode == 'click':
                cr.set_source_rgb(*self.auxcol['click2'])
                cr.move_to(radius*math.cos(offh2*RAD),radius*math.sin(offh2*RAD))
                x = fcusp*math.cos(offh2*RAD)
                y = fcusp*math.sin(offh2*RAD)
                cr.line_to(x,y)
                cr.stroke() 
                thiscusp = self.cuspnames[i]
                cr.move_to(x*1.007,y*1.007)
                cr.show_text(thiscusp)
        cr.restore()

    def draw_cusps(self,cr,radius,chartob,transit=False):
        chart = chartob.chart
        radius = radius * chartob.get_cusp_radfac()
        cusp_cols = cycle(((0.8,0,0),(0,0,0.6),(0,0.5,0)))  
        lw = cr.get_line_width()
        lwidth_iter = cycle(chartob.cusps_widths)        
        cuspnames = iter(self.cuspnames)
        cr.save()
        font_size = chartob.cusp_font_size * radius * MAGICK_FONTSCALE
        self.set_font(cr,font_size)
        fcusp = radius * chartob.cuspfac
        if transit: 
            fcusp = (radius*1.47) 
        dx = iter(chartob.dx)
        dy = iter(chartob.dy)
        for angle in chartob.get_cusps_offsets():
            angle *= RAD
            cr.set_line_width(lwidth_iter.next()*lw)
            cr.set_source_rgb(*cusp_cols.next())
            self.d_radial_line(cr,fcusp,radius,angle)
            thex = fcusp*math.cos(angle)
            they = fcusp*math.sin(angle)
            thiscusp = cuspnames.next()
            _,_, width, height,_,_ = cr.text_extents(thiscusp)
            x = width*dx.next()
            y = height*dy.next() 
            cr.move_to(thex+x,they+y)
            cr.show_text(thiscusp)
        cr.restore() 
    
    def d_house_zones(self,cr,radius,chartob):
        cols = chartob.zonecols
        percents = [0.21,0.41,0.68,0.75,0.87,0.97,1.0]
        sizes = iter(chartob.get_sizes())
        offsets = chartob.get_cusps_offsets()
        radius = radius * chartob.R_RULEDOUTER * 1.006

        lw = cr.get_line_width()*radius*MAGICK_FONTSCALE
        cr.save()
        cr.set_source_rgb(0.4,0.4,0.9)
        cr.set_line_width(6.5*lw)
        cr.arc(0,0,radius,0,360*RAD)
        cr.stroke()
        cr.set_line_width(5*lw)
        cr.set_line_cap(cairo.LINE_CAP_BUTT)
        for house,size in izip(offsets,sizes):
            prev_angle = house*RAD
            for i,c in enumerate(cols):
                #cr.set_source_rgba(*(list(c)+[0.7]))
                cr.set_source_rgb(*c)
                angle = (house-size*percents[i])*RAD
                cr.arc_negative(0,0,radius,prev_angle,angle)
                cr.stroke()
                prev_angle = angle
        cr.restore() 

    def d_local_trimming(self,cr,radius,chartob):
        chart = chartob.chart
        wave = [0,0.99,0.98,0.97,0.96,
                0.95,0.94,0.93,0.924,0.915,
                0.909,0.904,0.899,0.896,0.893,
                0.891,0.89,0.888,0.887,0.887,
                0.89,0.893,0.898,0.905,0.91,
                0.922,0.935,0.95,0.97,0.985]
        off = 180 + chart.houses[0]
        cr.save()
        cr.set_line_width(0.6*cr.get_line_width())
        fcusp = radius * 1.14
        cols = [(0.8,0.6,0.8),(0.1,0,0.1)]
        for size,house in zip(chart.sizes(),chart.houses):
            trimsize = size / 30
            for j in range(1,30):
                cr.set_source_rgb(*cols[j % 5 == 0]) 
                angle = (off - house - trimsize*j) * RAD
                self.d_radial_line(cr,fcusp*wave[j],radius,angle)
        cr.restore() 

    def d_house_trimming(self,cr,radius,h):
        offset = 180 
        size = 30.0
        low = radius * 0.79
        cusp = radius  * 0.89
        talk= size * PHI
        inv= size - talk
        cr.save()
        surfname = self.surface.__class__.__name__

        if surfname  == 'DrawPdf': 
            cr.set_line_width(0.5*cr.get_line_width())
        else:
            cr.set_line_width(1.1*cr.get_line_width())

        for i in range(12): 
            off = offset-i*30 
            bx = low*math.cos((off+inv)*RAD)
            by = low*math.sin((off+inv)*RAD)
            cr.move_to(bx,by)
            
            x = cusp*math.cos(off*RAD)
            y = cusp*math.sin(off*RAD)
            lx = low*math.cos((off-talk)*RAD)
            ly = low*math.sin((off-talk)*RAD)

            if surfname  == 'DrawPdf': 
                if i % 3 == 0:
                    cr.set_source_rgb(0.7,0,0)
                elif i % 3 == 1:
                    cr.set_source_rgb(0,0,0.6)
                else:
                    cr.set_source_rgb(0,0.6,0)
            else:
                pat = cairo.LinearGradient(bx,by,lx,ly)
                if i % 3 == 0:
                    pat.add_color_stop_rgb(0,0,0.6,0)
                    pat.add_color_stop_rgb(0.3,0.7,0,0)
                elif i % 3 == 1:
                    pat.add_color_stop_rgb(0,0.7,0,0)
                    pat.add_color_stop_rgb(0.3,0,0,0.6)
                else:
                    pat.add_color_stop_rgb(0,0,0,0.6)
                    pat.add_color_stop_rgb(0.3,0,0.6,0)
                cr.set_source(pat)
            # control points
            ilx = low*math.cos((off+inv*0.45)*RAD)
            ily = low*math.sin((off+inv*0.45)*RAD)
            ix = 0.95*cusp*math.cos((off+inv*0.15)*RAD)
            iy = 0.95*cusp*math.sin((off+inv*0.15)*RAD)
            
            tx = 0.95*cusp*math.cos((off-inv*0.45)*RAD)
            ty = 0.95*cusp*math.sin((off-inv*0.45)*RAD)
            tlx = low*math.cos((off-talk*0.7)*RAD)
            tly = low*math.sin((off-talk*0.7)*RAD)
            
            cr.curve_to(ilx,ily,ix,iy,x,y)
            cr.curve_to(tx,ty,tlx,tly,lx,ly)
            cr.stroke() 
        cr.restore()
    
    def d_dharma_trimming(self,cr,radius,w,h,chartob=None):
        cusps = chartob.get_cusps_offsets()
        sizes = chartob.get_sizes()
        offset = 180 
        low = radius * 0.78
        cusp = radius  * 0.89
        
        target = cr.get_target()
        over = target.create_similar(cairo.CONTENT_COLOR_ALPHA,w,h)
        over_cr = cairo.Context(over)
        over_cr.translate(w/2,h/2)
        over_cr.set_operator (cairo.OPERATOR_ADD)

        cr.save()
        surfname = self.surface.__class__.__name__ 
        tmp_cr = cr
        cr = over_cr

        maskpat =  cairo.RadialGradient(0,0,low,0,0,cusp)
        maskpat.add_color_stop_rgba(0,0,0,0,1)
        #maskpat.add_color_stop_rgba(0.3,0,0,0,1)
        maskpat.add_color_stop_rgba(1,0,0,0,0)

        for i in range(12): 
            off = cusps.next()
            size = sizes[i]
            talk = size * PHI
            inv = size - talk
            size0 = sizes[(i+11)%12]
            inv0 = size0 - size0 * PHI

            bx = low*math.cos((off+inv0)*RAD)
            by = low*math.sin((off+inv0)*RAD)
            cr.move_to(bx,by)
            bx = cusp*math.cos((off+inv0)*RAD)
            by = cusp*math.sin((off+inv0)*RAD)
            cr.line_to(bx,by) 
            cr.arc_negative(0,0,cusp, (off+inv0)*RAD ,(off-talk)*RAD )
            x = low*math.cos((off-talk)*RAD)
            y = low*math.sin((off-talk)*RAD)
            cr.line_to(x,y)
            cr.arc(0,0,low, (off-talk)*RAD , (off+inv0)*RAD )
            cr.close_path()

            lx = cusp*math.cos((off-talk)*RAD)
            ly = cusp*math.sin((off-talk)*RAD)


            pat = cairo.LinearGradient(bx,by,lx,ly)
            if i % 3 == 0:
                pat.add_color_stop_rgba(0,0,0.6,0,0.4)
                pat.add_color_stop_rgba(0.3,0.7,0,0,0.4)
            elif i % 3 == 1:
                pat.add_color_stop_rgba(0,0.7,0,0,0.4)
                pat.add_color_stop_rgba(0.3,0,0,0.6,0.4)
            else:
                pat.add_color_stop_rgba(0,0,0,0.6,0.4)
                pat.add_color_stop_rgba(0.3,0,0.6,0,0.4)
            cr.set_source(pat)
            cr.fill()
        cr = tmp_cr
        cr.set_source_surface(over,-w/2,-h/2)
        #cr.paint()
            
        cr.mask(maskpat)
        cr.restore()
    
    def d_coup_dates(self,cr,w,h,ch,col,dts):
        cr.save()
        radius = min(w,h) * 0.47
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(7*pango.SCALE*radius*2*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        cr.set_source_rgb(*col)
        for i,dt in enumerate(dts):
            dt = 180 + ch.houses[0] - dt
            layout.set_text(str(i+1))
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(radius*math.cos(dt*RAD)-w/2,radius*math.sin(dt*RAD)-h/2)
            cr.show_layout(layout) 
            self.d_radial_line(cr,radius*0.83,radius*0.96,dt*RAD)
            cr.arc(radius*math.cos(dt*RAD),
                radius*math.sin(dt*RAD),radius*0.04,0,360*RAD)
            cr.stroke()
        cr.restore()


    def draw_urnod_signs(self,cr,radius,chartob):
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

    def d_urnod_radial_lines(self,cr,radius,chartob):
        sign_cusps = chartob.chart.nod_sign_long()
        fac,ins,_ = chartob.get_radial_param()
        radius = radius * fac
        cr.save()
        cr.set_source_rgb(0.5,0.5,0.5)
        cr.set_line_width(0.5*cr.get_line_width())
        inset = ins * radius
        for i in sign_cusps:
            angle = (180-i) * RAD
            self.d_radial_line(cr,radius+inset,radius,angle)
        cr.restore()
    
    def make_spec_ruler(self,cr,radius,chartob,rule,rules,offset):
        cols = [(0.55,0,0),(0,0.5,0),(0.9,0.4,0),(0,0.0,0.6)]
        asc =   chartob.get_ascendant() % 4
        insets = [radius * i for i in rules[rule]]
        radius = radius * rule 
        default = insets.pop()
        insets = dict(zip((0,5),insets))
        cr.save()
        cr.set_line_width(0.5*cr.get_line_width())
        for i in xrange(360):
            if i % 30 == 0: 
                cr.set_source_rgb(*cols[(asc + i/30)%4])
            angle = (180+offset-i) * RAD
            inset = radius - insets.get(i%10,default)
            self.d_radial_line(cr,radius,inset,angle)
        cr.restore()
    
    def make_all_urn_rulers(self,cr,radius,chartob):
        R_RULEDINNER, R_RULEDOUTER, R_RULEDMID = chartob.get_ruled()
        rules = { R_RULEDOUTER: [0.016,0.010,0.004], 
                R_RULEDMID: [0.014,0.010,0.004],
                R_RULEDINNER:  [-0.018,-0.012,-0.004]}
        offset = chartob.get_offset()
        #print offset
        self.make_spec_ruler(cr,radius,chartob,R_RULEDOUTER,rules,offset)
        self.make_spec_ruler(cr,radius,chartob,R_RULEDINNER,rules,offset)
