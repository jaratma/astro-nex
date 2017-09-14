# -*- coding: utf-8 -*-
import cairo, pango
import math
from math import pi as PI
from .. boss import boss
from roundedcharts import HouseChart
curr = boss.get_state()

aspcol = None

RAD = PI /180
PHI = 1 / ((1+math.sqrt(5))/2)
MAGICK_FONTSCALE=0.002

class ProfileMixin(object):
    showEA = False
    
    def __init__(self,zodiac,showea):
        global aspcol,showEA
        aspcol = zodiac.get_aspcolors() 
        self.zod = zodiac.zod
        self.plan = zodiac.plan
        showEA = showea
    
    def warpPath(self,cr,let):
        dispatch = { cairo.PATH_MOVE_TO: 'move_to',cairo.PATH_LINE_TO:'line_to', cairo.PATH_CURVE_TO:'curve_to', cairo.PATH_CLOSE_PATH:'close_path'} 
        for type, points in let:
            getattr(cr,dispatch[type])(*points)   
    
    def draw_prof(self,cr,w,h,chartob):
        move_to = (-158.89974,-84.103884) 
        curve_to=[[-149.8869,-99.214804,-113.48919,-134.41882,-84.256949,-151.24671],
                [-69.373359,-161.81461,-29.885869,-177.30825,-14.070848,-183.19909],
                [3.3697041,-190.32293,50.394494,-215.37312,68.921638,-206.13957],#ix
                [106.25015,-182.88612,78.421633,-126.28242,108.6717,-97.675314],
                [140.97301,-62.797364,202.1636,-70.568024,197.52883,-9.3895892],#vii
                [196.02401,3.535866,189.14238,20.551186,187.7371,26.280512],
                [182.33183,50.009832,182.40094,58.002562,179.26098,66.396115],
                [165.33479,95.45549,150.77129,90.42277,139.94417,100.82774],
                [126.37219,110.85965,128.0461,126.53195,110.38516,139.47078],#v
                [98.603184,150.01071,79.181818,136.90847,42.100204,146.61043],
                [-22.8729941,158.54051,-32.044299,189.65538,-68.265109,184.2763],#iii
                [-98.366119,182.66299,-86.609989,118.24007,-110.69529,92.57654],
                [-128.98431,75.184255,-190.70129,80.288915,-205.11402,43.896102],
                [-214.97901,20.111282,-184.59737,1.8157109,-176.06381,-20.750504],
                [-170.48081,-39.440284,-175.84712,-62.819244,-158.89974,-84.103884]]


        RI0 = 0.05
        RI1 = 0.192
        RI2 = 0.245
        RO1 = 0.405
        RO2 = 0.52
        RO3 = 0.64
        RO4 = 0.76
        RO5 = 0.88
        cusps = [0.96,0.74,0.95,0.78,0.85,0.88,0.94,0.74,0.96,0.87,0.86,0.93]
        lows =  [0.52,0.34,0.46,0.34,0.40,0.46,0.48,0.34,0.56,0.44,0.41,0.40]
        
        up =    [1.12,1.08,1.05,1.05,1.05,1.05,1.05,1.05,1.05,1.05,1.05,1.05]
        dw =    [0.99,0.99,0.99,0.99,0.99,0.99,0.99,0.99,0.99,0.99,0.99,0.99]
        dw1 =   [0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9]
        ab =    [1.5,0.4,0.8,0.5,0.5,0.6,1.1,0.4,0.6,0.6,0.5,1.5]
        aa =    [1.5,0.2,0.9,0.8,0.8,0.9,1.6,0.8,0.8,0.8,0.8,1.6]
        
        x1 = [0] * 12; y1 = [0] * 12
        x2 = [0] * 12; y2 = [0] * 12

        placoord = [0]*11
        chart = chartob.chart
        offset = chart.houses[0] % 30
        sdasc = int(chart.houses[0] / 30)
        width = w
        height = h
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        ##### profile
        cr.save()
        scl = 0.0033*radius
        cr.scale(scl,scl)
        cr.set_line_width(1)
        cr.move_to(*move_to)
        for c in curve_to:
            cr.curve_to(*c)
        cr.close_path()
        profile = cr.copy_path()
        cr.set_source_rgb(0.85,0.85,0.85)
        cr.fill_preserve() 
        cr.set_source_rgb(0.7,0,0)
        cr.stroke() 
        cr.restore()
        
        phi = 30 * PHI; inv = 30 - phi
        cr.save()
        target = cr.get_target()
        over = target.create_similar(cairo.CONTENT_COLOR_ALPHA,int(w),int(h))
        over_cr = cairo.Context(over)
        over_cr.translate(cx,cy)
        over_cr.scale(scl,scl)
        over_cr.append_path(profile)
        over_cr.clip()
        ## star path
        scl =1/scl
        over_cr.scale(scl,scl)
        over_cr.set_source_rgb(0.95,0.95,0.95)
        for i in range(0,360,30):
            m = i / 30
            c = 180 - i
            l = 180 - i - phi; iv = 180 - i - inv
            if m == 0:            
                over_cr.move_to(radius*lows[(m+11)%12]*math.cos((c+inv)*RAD),
                        radius*lows[(m+11)%12]*math.sin((c+inv)*RAD))
            over_cr.line_to(radius*cusps[m]*math.cos(c*RAD),radius*cusps[m]*math.sin(c*RAD))
            over_cr.line_to(radius*lows[m]*math.cos(l*RAD),radius*lows[m]*math.sin(l*RAD))
            if m == 11:
                over_cr.close_path()
        over_cr.fill()
        cr.set_source_surface(over,-cx,-cy)
        cr.paint()
        cr.restore()

        ## yellow tris
        cr.set_line_width(0.4)
        third1 = phi/3; third2 = (30-phi)/3
        for m in range(12): 
            c = 180 - m*30
            l = 180 - m*30 - phi; iv = 180 - m*30 - inv
            x = radius*cusps[m]*math.cos(c*RAD); x1[m] = x
            y = radius*cusps[m]*math.sin(c*RAD); y1[m] = y
            x = radius*lows[m]*math.cos(l*RAD) ; x2[m] = x
            y = radius*lows[m]*math.sin(l*RAD) ; y2[m] = y 
        for h in range(12):
            cr.set_source_rgb(1,1,0.8) 
            cr.move_to(x1[h],y1[h])
            m = phi - third1
            n = third1
            x =  (n*x2[h] + m*x1[h])/(m+n)
            y =  (n*y2[h] + m*y1[h])/(m+n) 
            cr.line_to(x,y)
            m = third2*2
            n = third2
            xx =  (n*x2[(h+11)%12] + m*x1[h])/(m+n)
            yy =  (n*y2[(h+11)%12] + m*y1[h])/(m+n) 
            cr.line_to(xx,yy)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(1,0,0) 
            cr.move_to(x,y)
            cr.line_to(xx,yy)
            cr.stroke()
        third11 = phi/6; third22 = (30-phi)/6
        for h in range(12):
            cr.set_source_rgb(0.7,0.7,0.7) 
            cr.move_to(x2[h],y2[h])
            n = phi - third11
            m = third11
            x =  (n*x2[h] + m*x1[h])/(m+n)
            y =  (n*y2[h] + m*y1[h])/(m+n) 
            cr.line_to(x,y)
            n = third22*5
            m = third22
            xx =  (n*x2[h] + m*x1[(h+1)%12])/(m+n)
            yy =  (n*y2[h] + m*y1[(h+1)%12])/(m+n) 
            cr.line_to(xx,yy)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(0.4,0.4,0.4) 
            cr.move_to(x,y)
            cr.line_to(xx,yy)
            cr.stroke()
        
       #### axes
        icusp = radius * 0.07
        for i in range(12):
            off = 180 - i*30
            ocusp = radius*cusps[i]
            if i % 3 == 0:
                cr.set_source_rgb(0.6,0,0)
            elif i % 3 == 1:
                cr.set_source_rgb(0,0,0.6)
            else:
                cr.set_source_rgb(0,0.5,0)
            cr.move_to(ocusp*math.cos(off*RAD),ocusp*math.sin(off*RAD))
            cr.line_to(icusp*math.cos(off*RAD),icusp*math.sin(off*RAD))
            cr.stroke() 
        
        #### star
        cr.set_line_width(1.5)
        
        for i in range(0,360,30):
            m = i / 30
            if m % 3 == 0:
                cr.set_source_rgba(0.9,0,0,0.5)
            elif m % 3 == 1:
                cr.set_source_rgba(0,0,0.8,0.5)
            else:
                cr.set_source_rgba(0,0.7,0,0.5)
            c = 180 - i
            l = 180 - i - phi; iv = 180 - i - inv
            
            cr.move_to(radius*lows[(m+11)%12]*math.cos((c+inv)*RAD),
                    radius*lows[(m+11)%12]*math.sin((c+inv)*RAD))
            
            x = radius*cusps[m]*math.cos(c*RAD); x1[m] = x
            y = radius*cusps[m]*math.sin(c*RAD); y1[m] = y
            cr.line_to(x,y)
            x = radius*lows[m]*math.cos(l*RAD) ; x2[m] = x
            y = radius*lows[m]*math.sin(l*RAD) ; y2[m] = y 
            cr.line_to(x,y)
            cr.line_to(radius*cusps[(m+1)%12]*math.cos((c-30)*RAD),
                    radius*cusps[(m+1)%12]*math.sin((c-30)*RAD)) 
            
            cr.line_to(radius*lows[m]*dw[m]*math.cos(l*RAD),# low down
                    radius*lows[m]*dw[m]*math.sin(l*RAD))
            cr.line_to(radius*cusps[m]*dw[m]*math.cos(c*RAD),# cusp down
                    radius*cusps[m]*dw[m]*math.sin(c*RAD))
            cr.move_to(radius*lows[(m+11)%12]*1.02*math.cos((c+inv)*RAD),#low after
                    radius*lows[(m+11)%12]*1.02*math.sin((c+inv)*RAD))

            cr.close_path()
            cr.fill_preserve()
            cr.stroke()
        
        scl = 0.0023*radius
        chartob.__class__ = HouseChart 
        pls = chartob.sortplan()
        cr.set_line_width(0.5)
        for pl in pls:
            pang = pl['degree']
            h = int(math.floor(pang/30))
            pang -= h*30
            c = 180 - h*30
            if pang < phi:
                m = pang
                n = phi - pang
                x =  (n*x1[h] + m*x2[h])/(m+n)
                y =  (n*y1[h] + m*y2[h])/(m+n) 
            else:
                m = pang - phi
                n = 30 - pang                  
                x =  (n*x2[h] + m*x1[(h+1)%12])/(m+n)
                y =  (n*y2[h] + m*y1[(h+1)%12])/(m+n) 
            placoord[pl['ix']] = { 'x': x, 'y': y }
            cr.set_source_rgb(0.8,0.8,0.8) 
            cr.arc(x,y,2*scl,0,180*PI)
            cr.fill_preserve()
            cr.set_source_rgb(0.3,0.3,0.3) 
            cr.stroke() 

        if ProfileMixin.showEA:
            aspects = chart.aspects()
            cr.set_line_width(0.5)
            for asp in aspects:
                if not self.goodwill and asp['gw']:
                    continue
                x1 = placoord[asp['p1']]['x']; y1 = placoord[asp['p1']]['y'];
                x2 = placoord[asp['p2']]['x']; y2 = placoord[asp['p2']]['y'];
                
                f1 = 5 - 5*asp['f1']; f2 = 5 -5*asp['f2']
                xx = (x2 + x1)/2; yy = (y2 + y1)/2
                if asp['a'] != 0:
                    if asp['gw']:# goodwill
                        cr.set_source_rgb(*aspcol[asp['a']])
                        cr.set_dash([12,6],2)
                        cr.move_to(x1,y1)
                        cr.line_to(x2,y2)
                        cr.stroke() 
                    elif f1 < 0 or f2 < 0:#unilateral
                        if f1 < f2:
                            xi = x1; yi = y1
                            xe = x2; ye = y2
                        else:
                            xi = x2; yi = y2
                            xe = x1; ye = y1
                        cr.set_source_rgb(*aspcol[asp['a']])
                        cr.set_dash([12,6],2)
                        cr.move_to(xi,yi)
                        cr.line_to(xx,yy)
                        cr.stroke()
                        cr.set_dash([1,0],0)
                        cr.set_source_rgb(*aspcol[asp['a']])
                        cr.move_to(xx,yy)
                        cr.line_to(xe,ye) 
                        cr.set_line_width(0.5)
                        cr.stroke()
                    else:
                        cr.set_source_rgb(*aspcol[asp['a']])
                        f = (f1+f2)/10
                        lx1 = x1; lx2 = x2 
                        ly1 = y1; ly2 = y2
                        angle = math.atan((ly2-ly1)/(lx2-lx1)) / RAD 
                        dx = math.cos((90+angle)*RAD)#*2*f 
                        dy = math.sin((90+angle)*RAD)#*2*f
                        cr.move_to(lx1,ly1)
                        cr.curve_to((xx+dx),(yy+dy),(xx+dx),(yy+dy),lx2,ly2)
                        cr.curve_to((xx-dx),(yy-dy),(xx-dx),(yy-dy),lx1,ly1)
                        cr.fill_preserve()
                        cr.set_line_width(0.3)
                        cr.stroke()
        
        scl = 0.002*radius
        for pl in pls:
            pang = pl['degree']
            h = int(math.floor(pang/30))
            pang -= h*30
            c = 180 - h*30
            x = placoord[pl['ix']]['x']; y = placoord[pl['ix']]['y'];
            col = self.plan[pl['ix']].col
            cr.set_source_rgb(*col) 
            x_b,_,w,hh,_,y_b = self.plan[pl['ix']].extents
            cr.save()
            #if h in[5,6,7] and pang < phi:
            #    cr.translate(x-w/2,y-hh/3)
            #else:
            #    cr.translate(x-w/2,y+hh*1.5) 
            cr.translate(x-scl*w/2,y+scl*hh*1.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl['ix']].paths)
            cr.fill()
            cr.restore()

        #### circles 
        cr.set_line_width(0.3)
        cols = [(1,1,1),(0.9,0.9,0.9)]
        for r in (RI2,RI1,RI0):
            cr.set_source_rgb(*cols[0])
            cr.arc(0,0,radius*r,0,180*PI)
            cr.fill_preserve()
            cr.set_source_rgb(0,0,0)
            cr.stroke()
            cols.insert(0,cols.pop())
        cr.set_source_rgb(0,0,0)
        for r in (RO1,RO2,RO3,RO4,RO5):
            cr.arc(0,0,radius*r,0,180*PI)
            cr.stroke()

        ##### signs 
        for i in range(0,360,30):
            off = offset+i
            mod = i / 30
            ix = (8+sdasc-mod)%12
            s = self.zod[ix].let
            col = self.zod[ix].col
            cr.save()
            cr.set_source_rgb(*col) 
            cr.rotate((off+15)*RAD)
            x_b,_,width,height,_,_ = self.zod[ix].extents
            scl = 0.0009*radius
            cr.translate(scl*(-width/2-x_b),-radius*0.2)
            cr.scale(scl,scl)
            self.warpPath(cr,self.zod[ix].paths)
            cr.fill()
            cr.restore()
            cr.set_source_rgb(0,0,0) 
            cr.move_to(radius*RI1*math.cos(off*RAD),radius*RI1*math.sin(off*RAD))
            cr.line_to(radius*RI2*math.cos(off*RAD),radius*RI2*math.sin(off*RAD))
            cr.stroke() 
        
        #### minor axes
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(12*pango.SCALE*radius*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        
        cr.set_line_width(0.3)
        ocusp = RI1*radius; icusp = RI0*2.5*radius
        for i in range(12):
            off = 180 - i*30
            if i % 3 == 0:
                cr.set_source_rgb(0.6,0,0)
            elif i % 3 == 1:
                cr.set_source_rgb(0,0,0.6)
            else:
                cr.set_source_rgb(0,0.5,0)
            cr.move_to(ocusp*math.cos(off*RAD),ocusp*math.sin(off*RAD))
            cr.line_to(icusp*math.cos(off*RAD),icusp*math.sin(off*RAD))
            cr.stroke() 
            cr.set_source_rgb(0.4,0.4,0.4)
            layout.set_text("%s" % str(i+1))
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            x_b,y_b,w,h,x_a,y_a = cr.text_extents(str(i+1))
            cr.move_to(0.8*ocusp*math.cos((off-15)*RAD)-w/2,
                    0.8*ocusp*math.sin((off-15)*RAD)-h/2)
            cr.show_layout(layout)
        
