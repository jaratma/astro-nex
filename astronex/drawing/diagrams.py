# -*- coding: utf-8 -*-
import gtk
import cairo
import pango
import pangocairo
import math
from math import pi as PI
from .. boss import boss
st = boss.get_state()

labs = [_("Conservador"),_("Desconfiado"),_("Duda y critica"),_("Vacilante"),
        _("Espontaneo"),_("Intuitivo"),_("Formacion ideas"),_("Observador"),
        _("Investigador"),_("Contemplativo"),
        _("Planificador"),_("Formacion"),_("Impaciente por rendir"),
        _("Accion inmediata"),_("Ofensivo"),_("Proceso creativo"),_("Afan de rendimiento"),
        _("Largo plazo"),_("Prudente"),
        _("Resignado"),_("Consolidacion"),_("Economico"),_("Impulso a poseer"),
        _("Asiduo"),_("Organizador"),_("Utilizacion"),_("Pensamiento utilitario"),
        _("Disfrute"),_("Conservacion"),_("Defensivo")]
lkeys = {}

RAD = PI /180
PHI = 1 / ((1+math.sqrt(5))/2)
facsingle = [0.965,1.035]
facclick = [0.98,1.02]

card = (0.7,0,0.2)
fix = (0.1,0.1,0.6)
mut = (0,0.6,0.1)

class DiagramMixin(object):
    def __init__(self,zodiac):
        self.plan = zodiac.plan
        self.cols = zodiac.auxcolors
        self.zodcols = zodiac.get_zodcolors()
    
    def warpPlan(self,cr,s):
        for kind, points in s:
            if kind == cairo.PATH_MOVE_TO:
                cr.move_to(*points)
            elif kind == cairo.PATH_LINE_TO:
                cr.line_to(*points)
            elif kind == cairo.PATH_CURVE_TO:
                cr.curve_to(*points)
            elif kind == cairo.PATH_CLOSE_PATH:
                cr.close_path() 
    
    def draw_title(self,cr,title):
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(8*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0,0,0.6)
        layout.set_text(title)
        cr.show_layout(layout)

    def dyn_stars(self,cr,w,h,chartob):
        cx,cy = w/2.5,h/2.5
        cr.set_line_width(0.6)
        
        cr.save()
        self.dyn_signs(cr,cx,cy,chartob) 
        cr.translate(cx*1.5,0)
        self.dyn_houses(cr,cx,cy,chartob)        
        cr.translate(-cx*1.5,cy*1.5)
        self.dyn_energy(cr,cx,cy,chartob)
        cr.translate(cx*1.5,0)
        self.dyn_differences(cr,cx,cy,chartob)
        cr.translate(-cx*0.65,-cx*0.65)
        cr.scale(0.9,0.9)
        self.dyn_bars(cr,cx*0.95,cy,chartob) 
        cr.restore()
    
    def dyn_bars(self,cr,w,h,chartob=None):
        if chartob: 
            srow, hrow, diff = chartob.chart.dyncalc_list()
        else:
            srow, hrow, diff = st.curr_chart.dyncalc_list()
        zcol = self.zodcols
        cols = [card,fix,mut,zcol[0],zcol[1],zcol[2],zcol[3]]
        minim = min(w,h)

        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(8*pango.SCALE*minim*0.0032))
        layout.set_font_description(font)
        cr.save()
        cr.set_source_rgb(0.44,0.32,0.25)
        
        bari = w*0.05
        barwidth = w*0.9; barheight = h*0.06
        columnwidth = barwidth / 8
        maxheight = (h/2 * 0.9) - barheight/2
        vstep = maxheight / 90
        cbase = h*0.47

        cr.rectangle(bari,cbase,barwidth,barheight)
        cr.fill() 

        cr.set_source_rgb(1.0,1.0,1.0)
        for i,t in enumerate(diff): 
            cr.move_to(bari*1.5+i*columnwidth,cbase+barheight/6)
            layout.set_text(t.rjust(3,' '))
            cr.show_layout(layout)

        hrow = hrow[1:] 
        maxheight = 0
        for i,hr in enumerate(hrow):
            cr.set_source_rgb(*cols[i])
            cheight = int(hr)*vstep
            maxheight = max(maxheight,cheight) 
            cr.rectangle(bari*1.2+(i+1)*columnwidth,cbase-cheight,columnwidth*0.7,cheight)
            cr.fill()

        cr.set_source_rgb(0.5,0.5,0.5)
        for i,t in enumerate(hrow): 
            cr.move_to(bari*1.5+(i+1)*columnwidth,h/2-maxheight-30)
            layout.set_text(t.rjust(3,' '))
            cr.show_layout(layout) 

        srow = srow[1:]
        cdownbase = h-cbase
        maxheight = 0
        for i,sr in enumerate(srow):
            cr.set_source_rgb(*cols[i])
            cheight = int(sr)*vstep
            maxheight = max(maxheight,cheight) 
            cr.rectangle(bari*1.2+(i+1)*columnwidth,cdownbase,columnwidth*0.7,cheight)
            cr.fill()
        
        cr.set_source_rgb(0.5,0.5,0.5)
        for i,t in enumerate(srow): 
            cr.move_to(bari*1.5+(i+1)*columnwidth,h/2+maxheight+20)
            layout.set_text(t.rjust(3,' '))
            cr.show_layout(layout)

        diff = diff[1:]
        cr.set_source_rgb(0.85,0.85,0.85)
        for i,t in enumerate(diff): 
            t = int(t)
            ini = bari*1.2+(i+1)*columnwidth
            theight = t*vstep
            if t > 0: 
                cr.move_to(ini,cbase)
                cr.line_to(ini+columnwidth*0.7,cbase)
                cr.line_to(ini+columnwidth*0.7/2,cbase-theight)
                cr.close_path()
                cr.fill()
            else:
                cr.move_to(ini,cdownbase)
                cr.line_to(ini+columnwidth*0.7,cdownbase)
                cr.line_to(ini+columnwidth*0.7/2,cdownbase-theight)
                cr.close_path()
                cr.fill()

        cr.move_to(3,3)
        self.draw_title(cr,_("Diagrama de barras")) 
        cr.restore()

    def dyn_energy(self,cr,w,h,chartob=None):
        if chartob: 
            dyns = chartob.chart.dynstar_signs()
            dynh = chartob.chart.dynstar_houses()
        else:
            dyns = st.curr_chart.dynstar_signs() 
            dynh = st.curr_chart.dynstar_houses() 
        cx,cy = w/2,h/2
        radius = min(cx,cy)
        cr.save()
        cr.translate(cx,cy)
        r = radius*0.7
        ro = radius*0.34
        ru = (r-ro)/50
        lw = cr.get_line_width()
        cr.set_line_width(0.6*lw)
        cr.set_source_rgb(0,0,0)
        cr.new_path()
        cr.arc(0,0,r,0,180*PI)
        cr.stroke()

        for i in range(12):
            off = 180 - i*30
            ps = dyns[i]; ph = dynh[i]
            if ps >= ph:
                cr.set_source_rgb(*self.zodcols[i%4])
                cr.move_to((ro+ps*ru)*math.cos(off*RAD),(ro+ps*ru)*math.sin(off*RAD))
                cr.line_to(ro*math.cos((off+15)*RAD),ro*math.sin((off+15)*RAD))
                cr.arc_negative(0,0,ro,(off+15)*RAD,(off-15)*RAD)
                cr.close_path()
                cr.fill()
                cr.set_source_rgb(0.8,0.8,0.8)
                cr.move_to((ro+ph*ru)*math.cos(off*RAD),(ro+ph*ru)*math.sin(off*RAD))
                cr.line_to(ro*math.cos((off+15)*RAD),ro*math.sin((off+15)*RAD))
                cr.arc_negative(0,0,ro,(off+15)*RAD,(off-15)*RAD)
                cr.close_path()
                cr.fill()
            else:
                cr.set_source_rgb(0.7,0.7,0.7)
                cr.move_to((ro+ph*ru)*math.cos(off*RAD),(ro+ph*ru)*math.sin(off*RAD))
                cr.line_to(ro*math.cos((off+15)*RAD),ro*math.sin((off+15)*RAD))
                cr.arc_negative(0,0,ro,(off+15)*RAD,(off-15)*RAD)
                cr.close_path()
                cr.fill()
                cr.set_source_rgb(*self.zodcols[i%4])
                cr.move_to((ro+ps*ru)*math.cos(off*RAD),(ro+ps*ru)*math.sin(off*RAD))
                cr.line_to(ro*math.cos((off+15)*RAD),ro*math.sin((off+15)*RAD))
                cr.arc_negative(0,0,ro,(off+15)*RAD,(off-15)*RAD)
                cr.close_path()
                cr.fill()
            cr.set_source_rgb(0.4,0.4,0.4)
            cr.arc((ro+ph*ru)*math.cos(off*RAD),(ro+ph*ru)*math.sin(off*RAD),
                    1,0,180*PI)
            cr.stroke()
        cr.set_source_rgb(0.4,0.4,0.4)
        for i,p in enumerate(dynh):
            off = 180 - i*30
            ph = dynh[i]
            if i == 0: 
                cr.move_to((ro+ph*ru)*math.cos(off*RAD),(ro+ph*ru)*math.sin(off*RAD))
            else:
                cr.line_to((ro+ph*ru)*math.cos(off*RAD),(ro+ph*ru)*math.sin(off*RAD))
        cr.close_path()
        cr.stroke()

        cr.move_to(-cx+3,+cy-13)
        self.draw_title(cr,_("Diagrama de energia")) 
        cr.restore()

    def dyn_differences(self,cr,w,h,chartob=None):
        if chartob: 
            dyns = chartob.chart.dynstar_signs()
            dynh = chartob.chart.dynstar_houses()
            stress = chartob.chart.dyncalc_stress()
        else:
            dyns = st.curr_chart.dynstar_signs() 
            dynh = st.curr_chart.dynstar_houses() 
            stress = st.curr_chart.dyncalc_stress()
        stress = abs(stress)
        if stress > 100:
            stress = 100
        #stress -= 10
        if stress < 3:
            stress = 3
        cx,cy = w/2,h/2
        radius = min(cx,cy)
        cr.save()
        cr.translate(cx,cy)
        fac = 0.7
        r = radius*fac
        ro = radius * (fac + (stress/450.0))
        ri = radius * (fac - (stress/450.0))
        rui = (r - ri)/stress
        ruo = (ro - r)/stress
        lw = cr.get_line_width()
        cr.set_line_width(0.4*lw)
        cr.set_source_rgb(0,0,0)
        cr.new_path()
        cr.arc(0,0,ri,0,180*PI)
        cr.stroke()
        cr.arc(0,0,ro,0,180*PI)
        cr.stroke()
        cr.arc(0,0,r*0.15,0,180*PI)
        cr.stroke() 
        
        for i in range(12):
            off = 180 - i*30
            ps = dyns[i]; ph = dynh[i]
            dif = ph - ps
            if stress > 15:
                cr.set_source_rgb(0.7,0.7,0.7)
            else:
                cr.set_source_rgb(0.8,0.56,1.0)
            cr.move_to((r+dif*ruo)*math.cos(off*RAD),(r+dif*ruo)*math.sin(off*RAD))
            cr.line_to(r*math.cos((off+13)*RAD),r*math.sin((off+13)*RAD))
            cr.arc_negative(0,0,r,(off+13)*RAD,(off-13)*RAD)
            cr.close_path()
            cr.fill()
                
        target = cr.get_target()
        over = target.create_similar(cairo.CONTENT_COLOR_ALPHA,int(w),int(h))
        cut = target.create_similar(cairo.CONTENT_ALPHA,int(w),int(h))
        over_cr = cairo.Context(over)
        cut_cr = cairo.Context(cut)
        over_cr.translate(ro,ro)
        over_cr.arc(0,0,ro,0,180*PI)
        over_cr.clip()
        cr.set_line_width(0.2)
        over_cr.set_source_rgb(0.7,0.7,0.7)
        over_cr.arc(0,0,r,0,180*PI)
        over_cr.close_path()
        over_cr.stroke()
        for i in range(12):
            off = 180 - i*30
            col = self.zodcols[i%4]
            ps = dyns[i]; ph = dynh[i]
            dif = ph - ps
            over_cr.set_source_rgb(*col)
            over_cr.move_to((r+dif*ruo)*math.cos(off*RAD),(r+dif*ruo)*math.sin(off*RAD))
            over_cr.line_to(r*math.cos((off+13)*RAD),r*math.sin((off+13)*RAD))
            over_cr.arc_negative(0,0,r,(off+13)*RAD,(off-13)*RAD)
            over_cr.close_path()
            over_cr.fill()
        cut_cr.set_source_rgb(0,0,0)
        cut_cr.translate(ri,ri)
        cut_cr.arc(0,0,ri,0,180*PI)
        cut_cr.fill()
        over_cr.set_operator (cairo.OPERATOR_DEST_OUT)
        over_cr.set_source_surface(cut,-ri,-ri)
        over_cr.paint()
        cr.set_source_surface(over,-ro,-ro)
        cr.paint()
        
        cr.set_line_width(0.8*lw)
        for i in range(12):
            off = 180 - i*30
            col = self.zodcols[i%4]
            ps = dyns[i]; ph = dynh[i]
            cr.set_source_rgb(*col)
            out = r+ph*ruo; inn = r-ps*rui
            xo = out*math.cos(off*RAD)
            yo = out*math.sin(off*RAD)
            xi = inn*math.cos(off*RAD)
            yi = inn*math.sin(off*RAD)
            cr.move_to(xo,yo)
            cr.line_to(xi,yi)
            cr.stroke()
            cr.arc(xo,yo,2,0,180*PI)
            cr.fill()
            cr.arc(xi,yi,2,0,180*PI)
            cr.fill()
            cr.set_source_rgb(0.7,0.7,0.7)
            cr.arc(r*math.cos(off*RAD),r*math.sin(off*RAD),2,0,180*PI)
            cr.fill()
        
        cr.move_to(-cx+3,+cy-13)
        self.draw_title(cr,_("Diagrama de diferencias")) 
        cr.restore()

    def dyn_signs(self,cr,w,h,chartob=None):
        if chartob: 
            dyns = chartob.chart.dynstar_signs()
        else:
            dyns = st.curr_chart.dynstar_signs() 
        cx,cy = w/2,h/2
        radius = min(cx,cy)
        cr.save()
        cr.translate(cx,cy)
        r = radius*0.7
        ro = radius*0.34
        ru = (r-ro)/50
        lw = cr.get_line_width()
        cr.set_line_width(0.6*lw)
        cr.set_source_rgb(0,0,0)
        cr.new_path()
        cr.arc(0,0,r,0,180*PI)
        cr.stroke()
    
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(8*pango.SCALE*radius*0.006))
        layout.set_font_description(font)
        
        for i,p in enumerate(dyns):
            off = 180 - i*30
            cr.set_source_rgb(*self.zodcols[i%4])
            cr.move_to((ro+p*ru)*math.cos(off*RAD),(ro+p*ru)*math.sin(off*RAD))
            cr.line_to(ro*math.cos((off+15)*RAD),ro*math.sin((off+15)*RAD))
            cr.arc_negative(0,0,ro,(off+15)*RAD,(off-15)*RAD)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(0,0,0.6)
            layout.set_text("%s" % str(p))
            ink,logical = layout.get_extents()
            xpos = logical[2]/pango.SCALE
            ypos = logical[3]/pango.SCALE
            cr.move_to(r*0.92*math.cos((off-15)*RAD)-xpos/2,
                    r*0.92*math.sin((off-15)*RAD)-ypos/2)
            cr.show_layout(layout)

        font_size = 13.0
        cr.set_font_size(font_size) 
        cr.set_source_rgb(0,0,0.6)
        cr.move_to(-cx+3,-cy+3)
        self.draw_title(cr,_("Diagrama de signos")) 
        cr.restore()
    
    def dyn_houses(self,cr,w,h,chartob=None):
        if chartob: 
            dynh = chartob.chart.dynstar_houses()
        else:
            dynh = st.curr_chart.dynstar_houses() 
        cx,cy = w/2,h/2
        radius = min(cx,cy)
        cr.save()
        cr.translate(cx,cy)
        r = radius*0.7
        ro = radius*0.34
        ru = (r-ro)/50
        lw = cr.get_line_width()
        cr.set_line_width(0.6*lw)
        cr.set_source_rgb(0,0,0)
        cr.new_path()
        cr.arc(0,0,r,0,180*PI)
        cr.stroke()
    
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(8*pango.SCALE*radius*0.006))
        layout.set_font_description(font)
        
        for i,p in enumerate(dynh):
            off = 180 - i*30
            cr.set_source_rgb(*self.zodcols[i%4])
            cr.move_to((ro+p*ru)*math.cos(off*RAD),(ro+p*ru)*math.sin(off*RAD))
            cr.line_to(ro*math.cos((off+15)*RAD),ro*math.sin((off+15)*RAD))
            cr.arc_negative(0,0,ro,(off+15)*RAD,(off-15)*RAD)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(0,0,0.6)
            layout.set_text("%s" % str(p))
            ink,logical = layout.get_extents()
            xpos = logical[2]/pango.SCALE
            ypos = logical[3]/pango.SCALE
            cr.move_to(r*0.92*math.cos((off-15)*RAD)-xpos/2,
                    r*0.92*math.sin((off-15)*RAD)-ypos/2)
            cr.show_layout(layout)
    
        font_size = 13.0
        cr.set_font_size(font_size) 
        cr.set_source_rgb(0,0,0.6)
        cr.move_to(-cx+3,-cy+3)
        self.draw_title(cr,_("Diagrama de casas")) 
        cr.restore() 


    def dyn_cuad(self,cr,w,h,chartob=None):
        cr.set_line_cap(cairo.LINE_CAP_SQUARE) 
        width = w
        height = h
        minim = min(width,height)

        hoff = width*0.1 
        vtop = height*0.08
        voff = height*0.3
        vbot = height*0.7
        vbox = vbot - voff
        vstep =  vbox / 4
        hroff = width*0.9
        hbox = hroff - hoff
        deg = hbox/90
        house = deg * 30
        low = house * PHI
        inv = house - low
        self.d_cuad_frame(cr,minim,hoff,hroff,voff,vtop,vbot)
        self.d_cuad_plans(cr,minim,deg,hoff,voff,vstep)

    def dyn_cuad2(self,cr,w,h,chartob=None):
        cr.set_line_cap(cairo.LINE_CAP_SQUARE) 
        width = w
        height = h
        minim = min(width,height)

        hoff = width*0.1 
        vtop = height*0.08
        voff = height*0.3
        vbot = height*0.7
        vbox = vbot - voff
        vstep =  vbox / 4
        hroff = width*0.9
        hbox = hroff - hoff
        deg = hbox/90
        house = deg * 30
        low = house * PHI
        inv = house - low
        self.d_cuad_frame(cr,minim,hoff,hroff,voff,vtop,vbot)
        self.d_cuad_plans(cr,minim,deg,hoff,voff,vstep,kind='click1')
        self.d_cuad_plans(cr,minim,deg,hoff,voff,vstep,kind='click2')
    
    def d_cuad_frame(self,cr,minim,hoff,hroff,voff,vtop,vbot):
        vbox = vbot - voff
        hbox = hroff - hoff
        vstep =  vbox / 4
        deg = hbox/90
        house = deg * 30
        low = house * PHI
        inv = house - low

        #up box
        cr.set_line_width(0.8)
        cr.set_source_rgb(0,0,0.4)
        cr.move_to(hoff,vtop)
        cr.line_to(hoff,vtop*3.4)
        cr.line_to(hroff,vtop*3.4)
        cr.line_to(hroff,vtop)
        cr.close_path()
        cr.stroke()
        # low box
        cr.move_to(hoff,vbot*1.05)
        cr.line_to(hoff,vbot*1.2)
        cr.line_to(hroff,vbot*1.2)
        cr.line_to(hroff,vbot*1.05)
        cr.close_path()
        cr.stroke() 
        #rules
        cr.set_line_width(0.4)
        cr.set_source_rgb(0.3,0.3,0.3)
        o = hoff + deg - deg * PHI
        for j in range(1,5):
            for i in range(90):
                ho = o + deg*i
                if (i+4) % 10 == 0:
                    cr.move_to(ho,voff+vstep*j-4)
                elif (i+4) % 5 == 0:
                    cr.move_to(ho,voff+vstep*j-3)
                else:
                    cr.move_to(ho,voff+vstep*j-2)
                cr.line_to(ho,voff+vstep*j)
        cr.stroke()
        # mid box
        cr.set_line_width(1)
        cr.set_source_rgb(0,0,0.4)
        cr.move_to(hoff-hoff*0.1,voff)
        cr.line_to(hoff-hoff*0.1,vbot)
        cr.line_to(hroff+hoff*0.15,vbot)
        cr.line_to(hroff+hoff*0.15,voff)
        cr.close_path()
        cr.stroke()
        # vert
        cr.set_line_width(0.5)
        cr.set_source_rgb(0,0,0.7)
        cr.move_to(hoff,voff)
        cr.line_to(hoff,vbot)
        cr.stroke()
        cr.set_source_rgb(0,0.5,0)
        cr.set_line_width(0.8)
        mutline = hoff+inv
        lkeys[mutline] = [' 9',' 6',' 3','12']
        cr.move_to(mutline,vtop)
        cr.line_to(mutline,vbot*1.2)
        cr.stroke()
        cr.set_line_width(0.5)
        for vert in [(voff,vbot),(vtop,vtop*3.4),(vbot*1.05,vbot*1.2)]:
            cr.move_to(mutline+inv,vert[0])
            cr.line_to(mutline+inv,vert[1])
            cr.move_to(mutline+low,vert[0])
            cr.line_to(mutline+low,vert[1])
        cr.stroke()
        
        cardline = hoff+inv+house
        lkeys[cardline] = ['10',' 7',' 4',' 1']
        cr.set_line_width(0.8)
        cr.set_source_rgb(0.5,0,0)
        cr.move_to(cardline,vtop)
        cr.line_to(cardline,vbot*1.2)
        cr.stroke()
        cr.set_line_width(0.5)
        for vert in [(voff,vbot),(vtop,vtop*3.4),(vbot*1.05,vbot*1.2)]:
            cr.move_to(cardline+inv,vert[0])
            cr.line_to(cardline+inv,vert[1])
            cr.move_to(cardline+low,vert[0])
            cr.line_to(cardline+low,vert[1])
        cr.stroke()


        fixline = hoff+inv+house*2
        lkeys[fixline] = ['11',' 8',' 5',' 2']
        cr.set_line_width(0.8)
        cr.set_source_rgb(0,0,0.7)
        cr.move_to(fixline,vtop)
        cr.line_to(fixline,vbot*1.2)
        cr.stroke()
        cr.set_line_width(0.5)
        for vert in [(voff,vbot),(vtop,vtop*3.4),(vbot*1.05,vbot*1.2)]:
            cr.move_to(fixline+inv,vert[0])
            cr.line_to(fixline+inv,vert[1])
            cr.move_to(fixline+low,vert[0])
            cr.line_to(fixline+low,vert[1])
        cr.stroke()

        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(8*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0.3,0.3,0.3)
        ink,logical = layout.get_extents()
        ypos = logical[3]/pango.SCALE
        for col in [mutline,cardline,fixline]:
            for l in [0,1,2,3]:
                layout.set_text(lkeys[col][l])
                cr.move_to(col,voff+vstep*l+vstep*0.5-ypos/2)
                cr.show_layout(layout)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0,0.5,0)
        layout.set_text("M\n" + _("Pensamiento"))
        cr.move_to(mutline,vbot*1.21)
        cr.show_layout(layout)
        layout.set_text("M")
        cr.move_to(mutline,vtop*0.7)
        cr.show_layout(layout)
        cr.set_source_rgb(0.5,0,0)
        layout.set_text("C\n" + _("Energia"))
        cr.move_to(cardline,vbot*1.21)
        cr.show_layout(layout)
        layout.set_text("C")
        cr.move_to(cardline,vtop*0.7)
        cr.show_layout(layout)
        cr.set_source_rgb(0,0,0.5)
        layout.set_text("F\n" + _("Forma"))
        cr.move_to(fixline,vbot*1.21)
        cr.show_layout(layout)
        layout.set_text("F")
        cr.move_to(fixline,vtop*0.7)
        cr.show_layout(layout)
        cr.save()
        font.set_size(10*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0.3,0.3,0.3)
        for o in [hoff*0.7,hroff*1.015]:
            cr.move_to(o,vbot)
            cr.rotate(-90*RAD)
            cr.rel_move_to(vstep*0.4,0)
            layout.set_text(_("Yo"))
            cr.show_layout(layout)
            cr.rel_move_to(vstep,0)
            layout.set_text(_("Col"))
            cr.show_layout(layout)
            cr.rel_move_to(vstep,0)
            layout.set_text(_("Tu"))
            cr.show_layout(layout)
            cr.rel_move_to(vstep,0)
            layout.set_text(_("Ind"))
            cr.show_layout(layout)
            cr.rotate(90*RAD)
        cr.restore()

        # curves
        cr.set_line_width(1)
        x = [mutline,cardline,fixline]
        c = [(0,0.5,0),(0.5,0,0),(0,0,0.5)]
        yu = vbot*1.05
        yd = vbot*1.2 
        cr.move_to(hoff,vbot*1.2)
        for i,col in enumerate(x):
            if i > 0:
                cr.move_to(col-inv,vbot*1.2)
            cr.set_source_rgb(*c[i])
            cr.curve_to(col-inv*0.45,yd,col,yu+vstep/2,col,yu)
            cr.curve_to(col,yu+vstep*0.3,col+inv*0.5,yd,col+low,yd)
            if i < 2:
                cr.curve_to(x[(i+1)%3]-inv*0.45,yd,x[(i+1)%3],yu+vstep/2,x[(i+1)%3],yu)
            else:
                cr.move_to(hoff,vbot*1.2)
                cr.curve_to(x[0]-inv*0.45,yd,x[0],yu+vstep/2,x[0],yu)

            cr.stroke()

        # labels 
        if self.surface.__class__.__name__ == 'DrawPdf':
            font.set_size(8*pango.SCALE)
        else:
            font.set_size(10*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.move_to(hoff,vtop*3.4)
        layout.set_text(labs[0])
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        cr.show_layout(layout)
        loff = (mutline-hoff)/4
        cr.rel_move_to(2,loff)
        layout.set_text(labs[1])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff)
        cr.set_source_rgb(0.5,0,0)
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(labs[2])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff)
        cr.set_source_rgb(0.3,0.3,0.3)
        font.set_weight(pango.WEIGHT_NORMAL)
        layout.set_font_description(font)
        layout.set_text(labs[3])
        cr.show_layout(layout)
        cr.rotate(90*RAD)
        
        cr.move_to(mutline,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[4])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff)
        layout.set_text(labs[5])
        cr.show_layout(layout)
        cr.set_source_rgb(0.5,0,0)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(labs[6])
        cr.show_layout(layout)
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_NORMAL)
        layout.set_font_description(font)
        layout.set_text(labs[7])
        cr.show_layout(layout)
        cr.rotate(90*RAD)

        cr.move_to(mutline+inv,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[8])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff*1.5)
        layout.set_text(labs[9])
        cr.show_layout(layout)
        cr.rotate(90*RAD)

        cr.move_to(cardline-inv,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[10])
        cr.show_layout(layout)
        cr.set_source_rgb(0.5,0,0)
        cr.rel_move_to(0,loff+3)
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(labs[11])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff-3)
        layout.set_text(_("de voluntad"))
        cr.show_layout(layout)
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_NORMAL)
        layout.set_font_description(font)
        layout.set_text(labs[12])
        cr.show_layout(layout)
        cr.rotate(90*RAD)

        cr.move_to(cardline,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[13])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff)
        layout.set_text(labs[14])
        cr.show_layout(layout)
        cr.set_source_rgb(0.5,0,0)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(labs[15])
        cr.show_layout(layout)
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_NORMAL)
        layout.set_font_description(font)
        layout.set_text(labs[16])
        cr.show_layout(layout)
        cr.rotate(90*RAD)

        cr.move_to(cardline+inv,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[17])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff*1.5)
        layout.set_text(labs[18])
        cr.show_layout(layout)
        cr.rotate(90*RAD)

        cr.move_to(fixline-inv,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[19])
        cr.show_layout(layout)
        cr.set_source_rgb(0.5,0,0)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(labs[20])
        cr.show_layout(layout)
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_NORMAL)
        layout.set_font_description(font)
        layout.set_text(labs[21])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff)
        layout.set_text(labs[22])
        cr.show_layout(layout)
        cr.rotate(90*RAD)

        cr.move_to(fixline,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[23])
        cr.show_layout(layout)
        cr.rel_move_to(0,loff)
        layout.set_text(labs[24])
        cr.show_layout(layout)
        cr.set_source_rgb(0.5,0,0)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(labs[25])
        cr.show_layout(layout)
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.rel_move_to(0,loff)
        font.set_weight(pango.WEIGHT_NORMAL)
        layout.set_font_description(font)
        layout.set_text(labs[26])
        cr.show_layout(layout)
        cr.rotate(90*RAD)
        
        cr.move_to(fixline+inv,vtop*3.4)
        cr.rotate(-90*RAD)
        cr.rel_move_to(2,0)
        layout.set_text(labs[27])
        cr.show_layout(layout)
        cr.set_source_rgb(0.5,0,0)
        cr.rel_move_to(0,loff*0.8)
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(labs[28])
        cr.show_layout(layout)
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.rel_move_to(0,loff*0.8)
        font.set_weight(pango.WEIGHT_NORMAL)
        layout.set_font_description(font)
        layout.set_text(labs[29])
        cr.show_layout(layout)
        cr.rotate(90*RAD)

    def d_cuad_plans(self,cr,minim,deg,hoff,voff,vstep,kind='single'):
        if kind == 'click2': 
            ind,you,col,ii = st.curr_click.cuad_plan()
        else:
            ind,you,col,ii = st.curr_chart.cuad_plan() 
        if kind in ['click1','click2']:
            scl = 0.0009*minim
            colo = self.cols[kind]
            fac = facclick
        else:
            scl = 0.001*minim
            fac = facsingle
        low = 30*PHI
        o = hoff + deg - deg * PHI
        for i in range(len(ind)):
            d = ind[i]['degree'] - (210+low)
            if kind not in ['click1','click2']:
                colo = self.plan[ind[i]["ix"]].col
            cr.set_source_rgb(*colo) 
            plet = self.plan[ind[i]["ix"]].let
            ho = o + deg*d
            vpos = voff+vstep
            cr.move_to(ho,vpos)
            cr.line_to(ho,vpos*0.98)
            cr.stroke()
            x_b,_,w,h,_,y_b = self.plan[ind[i]["ix"]].extents
            if kind == 'click1':
                rpl = voff+vstep*0.2+h/2
            elif kind == 'click2':
                rpl = voff+vstep*0.65+h/2
            else: 
                rpl = voff+vstep*0.5+h/2
            if ind[i]['conflict']:
                rpl *= fac[0]
                fac[0],fac[1] = fac[1],fac[0]
            cr.save()
            cr.translate(ho-(w+x_b)/2,rpl)
            cr.scale(scl,scl)
            self.warpPlan(cr,self.plan[ind[i]["ix"]].paths)
            cr.fill()
            cr.restore()

        for i in range(len(you)):
            d = you[i]['degree'] - (120+low)
            if kind not in ['click1','click2']:
                colo = self.plan[you[i]["ix"]].col
            cr.set_source_rgb(*colo) 
            plet = self.plan[you[i]["ix"]].let
            ho = o + deg*d
            vpos = voff+vstep*2
            cr.move_to(ho,vpos)
            cr.line_to(ho,vpos*0.985)
            cr.stroke()
            x_b,_,w,h,_,y_b = self.plan[you[i]["ix"]].extents
            if kind == 'click1':
                rpl = voff+vstep*1.2+h/2
            elif kind == 'click2':
                rpl = voff+vstep*1.65+h/2
            else: 
                rpl = voff+vstep*1.5+h/2
            if you[i]['conflict']:
                rpl *= fac[0]
                fac[0],fac[1] = fac[1],fac[0]
            cr.save()
            cr.translate(ho-(w+x_b)/2,rpl)
            cr.scale(scl,scl)
            self.warpPlan(cr,self.plan[you[i]["ix"]].paths)
            cr.fill()
            cr.restore()

        for i in range(len(col)):
            d = col[i]['degree'] - (30+low)
            if kind not in ['click1','click2']:
                colo = self.plan[col[i]["ix"]].col
            cr.set_source_rgb(*colo) 
            plet = self.plan[col[i]["ix"]].let
            ho = o + deg*d
            vpos = voff+vstep*3
            cr.move_to(ho,vpos)
            cr.line_to(ho,vpos*0.987)
            cr.stroke()
            x_b,_,w,h,_,y_b = self.plan[col[i]["ix"]].extents
            if kind == 'click1':
                rpl = voff+vstep*2.2+h/2
            elif kind == 'click2':
                rpl = voff+vstep*2.65+h/2
            else: 
                rpl = voff+vstep*2.5+h/2
            if col[i]['conflict']:
                rpl *= fac[0]
                fac[0],fac[1] = fac[1],fac[0]
            cr.save()
            cr.translate(ho-(w+x_b)/2,rpl)
            cr.scale(scl,scl)
            self.warpPlan(cr,self.plan[col[i]["ix"]].paths)
            cr.fill()
            cr.restore()
        
        for i in range(len(ii)):
            d = ii[i]['degree'] - (300+low)
            if d < 0: d += 360
            if kind not in ['click1','click2']:
                colo = self.plan[ii[i]["ix"]].col
            cr.set_source_rgb(*colo)
            plet = self.plan[ii[i]["ix"]].let
            ho = o + deg*d
            vpos = voff+vstep*4
            cr.move_to(ho,vpos)
            cr.line_to(ho,vpos*0.988)
            cr.stroke()
            x_b,_,w,h,_,y_b = self.plan[ii[i]["ix"]].extents
            if kind == 'click1':
                rpl = voff+vstep*3.2+h/2
            elif kind == 'click2':
                rpl = voff+vstep*3.65+h/2
            else: 
                rpl = voff+vstep*3.5+h/2
            if ii[i]['conflict']:
                rpl *= fac[0]
                fac[0],fac[1] = fac[1],fac[0]
            cr.save()
            cr.translate(ho-(w+x_b)/2,rpl)
            cr.scale(scl,scl)
            self.warpPlan(cr,self.plan[ii[i]["ix"]].paths)
            cr.fill()
            cr.restore()
