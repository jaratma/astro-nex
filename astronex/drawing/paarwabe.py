# -*- coding: utf-8 -*-
import gtk
import cairo
import pango
import pangocairo
import math
from math import pi as PI
from roundedcharts import NodalNodalChart
from .. directions import strdate_to_date
from collections import deque
import datetime 
from itertools import izip
from .. boss import boss
state = boss.get_state()
aspclass = [4,0,1,2,3,1,4,1,3,2,1,0] 
asplet = ( '1','2','3','4','5','6','7','6','5','4','3','2' )
pwlet = { 'S': _('A'), 'M': _('N'), 'R': _('R')   } 

aspcolors = [(1.0, 0.5, 0.0), (0.0, 0.65, 0.0), (0.0, 0.0, 0.97), (0.93, 0.0, 0.0),
        (0.0, 0.0, 0.97), (0.0, 0.65, 0.0), (0.93, 0.0, 0.0), (0.0, 0.65, 0.0),
        (0.0, 0.0, 0.97), (0.93, 0.0, 0.0), (0.0, 0.0, 0.97), (0.0, 0.65, 0.0)]                                                                                    
RAD = PI /180
PHI = 1 / ((1+math.sqrt(5))/2)
MAGICK_FONTSCALE=0.002
    
she_col = (0.72,0.58,0) 
he_col = (0.74,0.42,0.85) 
wunsen_cols = { 'wun': [(0.39,0.27,0.7),(0.89,0.81,1),(0.95,0.9,1),(0.2,0.1,0.5)], 
        'sen': [(0.28,0.64,0.44),(0.78,0.98,0.84),(0.8,1,0.9),(0.1,0.5,0.2)] }
pol_col = (0,0.7,0)
fem_col = (0,0.2,0.6)
mas_col = (0.7,0,0)

polar_texts = { 'P6': _('El la idealiza'),
        'P5': _('Ella lo idealiza'),
        'P14': _('Proyeccion de padre/madre ideal'),
        'P9': _('Mentalidad coincidente'),
        'P10': _('Seguridad coincidente'),
        'P13': _('Deseo de ser padres'),
        'P4': _('El activa su sentimiento maternal'),
        'P3': _('Ella activa su sentimiento paternal'),
        'P12': _('Atraccion erotica'),
        'P7': _('Erotismo mutuo'),
        'P8': _('Placer mutuo'),
        'P11': _('Compatibilidad sexual'),
        'P2': _('Funcion edipica femenina'),
        'P1': _('Funcion edipica masculina'),
        'P0': _('Analisis de polaridades') }

ascent_texts = {
        'a0': _('Estrella de ascenso'),
        'a1': _('Contactos comunes - Los caminos se cruzan una y otra vez'),
        'a2': _('Conocidos comunes - Los caminos transcurren paralelos'),
        'a3': _('La presencia de ella estimula el desarrollo de el'),
        'a3b': _('\tEl le muestra el camino hacia si misma'),
        'a4':_('La presencia de el estimula el desarrollo de ella'),
        'a4b':_('\tElla le muestra el camino hacia si mismo'),
        'a5': _('Su tarea del alma. Conexiones cosmicas indefinibles'),
        'a7': _('Su tarea karmica. Caminos del destino entre ambos, providencia') }

wunder_texts = { 'w1': _('Encaje maravilloso'),
        'w2': _('Admiracion'),
        'w3': _('Coincidencias maravillosas'),
        'w4': _('Sensualidad maravillosa'),
        's1': _('Aspecto de comprension, comprenderlo todo siempre'),
        's2': _('Aspecto de conversacion, te entiendo'),
        's3': _('Aspecto de coqueteo, sensualidad emocional'),
        's4': _('Aspecto de discusion, desintegrar un tema hablando'),
        's5': _('Aspecto de charla, acuerdo momentaneo'),
        'w0': _('Estrella maravillosa'),
        's0': _('Sensi-estrella')
        }

def warpPath(cr,let):
    for path in let:
        path = path.replace("close path","close_path")
        plist = path.split(' ')
        typ, points = plist[0].strip(),plist[1:] 
        floatpoints = [float(point.strip()) for point in points]
        getattr(cr,typ)(*floatpoints)


def ascent_calc(asc_1, asc_2, nod_1, nod_2):
    #aa 1 nn 2 an 3 na 4 nar 5 arn 6  acar 7 arac 8 
    orbs = state.orbs[0]
    asc_asp = []
    aa1 = abs(asc_1 - asc_2)
    nn2 = abs(nod_1 - nod_2)
    an3 = abs(asc_1 - nod_2)
    na4 = abs(nod_1 - asc_2)
    for dis in aa1,nn2,an3,na4,nod_1,nod_2,asc_1,asc_2: 
        nsig = int(dis/30)
        orb = dis - nsig*30
        if orb > 20.0:
            nsig += 1; orb = 30.0 - orb
        acl = aspclass[nsig%12]
        if orb <= 9.0:
            asc_asp.append(nsig%12)
            #orbA = 9.0 #orbs[acl]
            #if orb <= orbA:
            #   asc_asp.append(nsig%12)
            #else:
            #   asc_asp.append(-1)
        else:
            asc_asp.append(-1)
    return asc_asp

def simple_asp(p1,cl1,p2,cl2):
    orbs = state.orbs[:]
    dis = abs(p1-p2)
    nsig = int(dis/30)
    orb = dis - nsig*30
    if orb > 20.0:
        nsig += 1; orb = 30.0 - orb
    acl = aspclass[nsig%12]
    if orb <= 9.0:
        orb1 = orbs[cl1][acl]
        orb2 = orbs[cl2][acl]
        if orb <= orb1 and orb <= orb2:
            return nsig%12
        elif orb <= orb1 or orb <= orb2:
            return -(nsig%12)
        else:
            return -1000
    else:
        return -1000


def wunder_calc(chartobj):
    she = []; he = [] # 0l  1n  2j  3m
    she.append(chartobj.chart.planets[1])
    she.append(chartobj.chart.planets[8])
    she.append(chartobj.chart.planets[5])
    she.append(chartobj.chart.planets[2])
    he.append(chartobj.click.planets[1])
    he.append(chartobj.click.planets[8])
    he.append(chartobj.click.planets[5])
    he.append(chartobj.click.planets[2])
    #(l) 0 0; (n) 1 3; (j) 2 1 (m) 3 1

    wunder = {}; sensi = {}
    wunder['1'] = simple_asp(she[0],0,he[0],0)
    wunder['2a'] = simple_asp(she[0],0,he[1],3)
    wunder['2b'] = simple_asp(she[1],3,he[0],0)
    wunder['3a'] = simple_asp(she[2],1,he[1],3)
    wunder['3b'] = simple_asp(she[1],3,he[2],1)
    wunder['4'] = simple_asp(she[2],1,he[2],1)
    sensi['1a'] = simple_asp(she[3],1,he[1],3) 
    sensi['1b'] = simple_asp(she[1],3,he[3],1) 
    sensi['2a'] = simple_asp(she[0],0,he[3],1) 
    sensi['2b'] = simple_asp(she[3],1,he[0],0) 
    sensi['3a'] = simple_asp(she[0],0,he[2],1) 
    sensi['3b'] = simple_asp(she[2],1,he[0],0) 
    sensi['4a'] = simple_asp(she[2],1,he[3],1) 
    sensi['4b'] = simple_asp(she[3],1,he[2],1) 
    sensi['5'] = simple_asp(she[3],1,he[3],1)
    return wunder,sensi

def polar_calc(chartobj):
    she = []; he = [] # 0s  1sat  2ma  3ve 4up
    # (s)0 0 (sat)1 2 (ma)2 2 (v)3 1 (u)4 3
    she.append(chartobj.chart.planets[0])
    she.append(chartobj.chart.planets[6])
    she.append(chartobj.chart.planets[4])
    she.append(chartobj.chart.planets[3])
    she.append(chartobj.chart.planets[7])
    he.append(chartobj.click.planets[0])
    he.append(chartobj.click.planets[6])
    he.append(chartobj.click.planets[4])
    he.append(chartobj.click.planets[3])
    he.append(chartobj.click.planets[9])
    polar = {}
    polar['1'] = simple_asp(she[0],0,he[2],2)
    polar['2'] = simple_asp(she[3],1,he[1],2)
    polar['3'] = simple_asp(she[2],2,he[0],0)
    polar['4'] = simple_asp(she[1],2,he[3],1)
    polar['5'] = simple_asp(she[0],0,he[4],3)
    polar['6'] = simple_asp(she[4],3,he[1],2)
    polar['7'] = simple_asp(she[2],2,he[2],2)
    polar['8'] = simple_asp(she[3],1,he[3],1)
    polar['9'] = simple_asp(she[0],0,he[0],0)
    polar['10'] = simple_asp(she[1],2,he[1],2)
    polar['11'] = simple_asp(she[3],1,he[2],2)
    polar['12'] = simple_asp(she[2],2,he[3],1)
    polar['13'] = simple_asp(she[1],2,he[0],0)
    polar['14'] = simple_asp(she[0],0,he[1],2)
    return polar

def crown_calc(chartobj):
    she_r = chartobj.chart.planets[:-1]
    he_r = chartobj.click.planets[:-1]
    she_s = chartobj.chart.soulplan()[:-4]
    he_s = chartobj.click.soulplan()[:-4]
    she_h = chartobj.chart.house_plan_long()[:-1]
    he_h = chartobj.click.house_plan_long()[:-1]
    chartobj.__class__ = NodalNodalChart
    she_n = chartobj.get_planets(True)
    she_n = she_n[0:2]+she_n[6:-1]
    chartobj.swap_charts()
    he_n = chartobj.get_planets(True)
    he_n = he_n[0:2]+he_n[6:-1] 
    chartobj.swap_charts()

    crown_she = {}
    crown_she['1'] = simple_asp(she_r[9],3,he_s[0],0)
    crown_she['2'] = simple_asp(she_r[8],3,he_s[1],0)
    crown_she['3'] = simple_asp(she_r[7],3,he_s[6],2)
    crown_she['4'] = simple_asp(she_r[6],3,he_s[3],1)
    crown_she['5a'] = simple_asp(she_r[1],0,he_s[2],1)
    crown_she['5b'] = simple_asp(she_r[1],0,he_s[5],1)
    crown_she['6'] = simple_asp(she_r[0],0,he_s[4],2)
    crown_she['7'] = simple_asp(she_h[0],0,he_n[5],3)
    crown_she['8'] = simple_asp(she_h[1],0,he_n[4],3)
    crown_she['9'] = simple_asp(she_h[6],2,he_n[3],3)
    crown_she['10'] = simple_asp(she_h[3],1,he_n[2],2)
    crown_she['11a'] = simple_asp(she_h[2],1,he_n[1],0)
    crown_she['11b'] = simple_asp(she_h[5],1,he_n[1],0)
    crown_she['12'] = simple_asp(she_h[4],2,he_n[0],0)
    
    crown_he = {}
    crown_he['1'] = simple_asp(he_r[9],3,she_s[0],0)
    crown_he['2'] = simple_asp(he_r[8],3,she_s[1],0)
    crown_he['3'] = simple_asp(he_r[7],3,she_s[6],2)
    crown_he['4'] = simple_asp(he_r[6],3,she_s[3],1)
    crown_he['5a'] = simple_asp(he_r[1],0,she_s[2],1)
    crown_he['5b'] = simple_asp(he_r[1],0,she_s[5],1)
    crown_he['6'] = simple_asp(he_r[0],0,she_s[4],2)
    crown_he['7'] = simple_asp(he_h[0],0,she_n[5],3)
    crown_he['8'] = simple_asp(he_h[1],0,she_n[4],3)
    crown_he['9'] = simple_asp(he_h[6],2,she_n[3],3)
    crown_he['10'] = simple_asp(he_h[3],1,she_n[2],2)
    crown_he['11a'] = simple_asp(he_h[2],1,she_n[1],0)
    crown_he['11b'] = simple_asp(he_h[5],1,she_n[1],0)
    crown_he['12'] = simple_asp(he_h[4],2,she_n[0],0)
    return crown_she,crown_he

def paarwabe_calc(chartobj):
    sheplan = chartobj.chart.planets[:]
    she_r = [sheplan[0],sheplan[1],sheplan[6]]
    sheplan = chartobj.chart.soulplan()
    she_s = [sheplan[0],sheplan[1],sheplan[6]]

    heplan = chartobj.click.planets[:]
    he_r = [heplan[0],heplan[1],heplan[6]]
    heplan = chartobj.click.soulplan()
    he_s = [heplan[0],heplan[1],heplan[6]]
    
    sheplan = chartobj.chart.house_plan_long()
    she_h = [sheplan[0],sheplan[1],sheplan[6]]
    heplan = chartobj.click.house_plan_long()
    he_h = [heplan[0],heplan[1],heplan[6]]

    chartobj.__class__ = NodalNodalChart
    sheplan = chartobj.get_planets(True)
    she_n = [sheplan[0],sheplan[1],sheplan[6]]
    chartobj.swap_charts()
    heplan = chartobj.get_planets(True)
    he_n = [heplan[0],heplan[1],heplan[6]]
    
    paar = {}
    paar['ss'] = []
    for i,ps in enumerate(she_s):
        for j,ph in enumerate(he_s):
            paar['ss'].append(simple_paar(ps,i/2*2,ph,j/2*2))
    
    paar['rs'] = []
    for i,ps in enumerate(she_r):
        for j,ph in enumerate(he_s):
            paar['rs'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    paar['sr'] = []
    for i,ps in enumerate(she_s):
        for j,ph in enumerate(he_r):
            paar['sr'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    paar['rr'] = []
    for i,ps in enumerate(she_h):
        for j,ph in enumerate(he_h):
            paar['rr'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    paar['nn'] = []
    for i,ps in enumerate(she_n):
        for j,ph in enumerate(he_n):
            paar['nn'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    paar['nr'] = []
    for i,ps in enumerate(she_n):
        for j,ph in enumerate(he_h):
            paar['nr'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    paar['rn'] = []
    for i,ps in enumerate(she_h):
        for j,ph in enumerate(he_n):
            paar['rn'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    paar['sn'] = []
    for i,ps in enumerate(she_r):
        for j,ph in enumerate(he_n):
            paar['sn'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    paar['ns'] = []
    for i,ps in enumerate(she_n):
        for j,ph in enumerate(he_r):
            paar['ns'].append(simple_paar(ps,i/2*2,ph,j/2*2))

    return paar

def simple_paar(p1,cl1,p2,cl2):
    orbs = state.orbs[:]
    dis = abs(p1-p2)
    nsig = int(dis/30)
    orb = dis - nsig*30
    if orb > 20.0:
        nsig += 1; orb = 30.0 - orb
    acl = aspclass[nsig%12]
    if orb <= 9.0:
        orb1 = orbs[cl1][acl]
        orb2 = orbs[cl2][acl]
        if orb <= orb1 or orb <= orb2:
            return nsig%12
        else:
            return -1
    else:
        return -1

def count_paar_sum(paar):
    cpaar = {}
    for k in paar.keys():
        cpaar[k] = 0
        for i in paar[k]:
            if i > -1: cpaar[k] += 1

    red= cpaar['ss']+cpaar['sr']+cpaar['rs']+cpaar['sn']+cpaar['ns'] 
    blue= cpaar['nn']+cpaar['ns']+cpaar['sn']+cpaar['rn']+cpaar['nr'] 
    green= cpaar['rr']+cpaar['rn']+cpaar['nr']+cpaar['rs']+cpaar['sr'] 

    return (str(red),str(green),str(blue))

def count_paar_asp(paar):
    colcj = [0,2,0,2,1,2,0,2,2] # 0 r 1 g 2 b
    asptype = [0,0,0] # 0 conj 1 opos 2 rest 
    colglob = [0,0,0]
    for k in paar.keys():
        for p,i in enumerate(paar[k]):
            if i == 0: 
                asptype[0] += 1
                colglob[colcj[p]] += 1
            elif i == 6: 
                asptype[1] += 1
                colglob[0] += 1
            elif i > -1:
                asptype[2] += 1
                if i in [1,5,7,11]:
                    colglob[1] += 1
                elif i in [2,4,8,10]:
                    colglob[2] += 1
                elif i in [3,9]:
                    colglob[0] += 1
    return asptype,colglob

def count_paar_inasp(paar):
    inasp = {}
    for k in paar.keys():
        nor = [ (x+1) for x in paar[k] ]
        inasp[k] =  6 * [0]
        inasp[k][0] = nor[0] or nor[1] or nor[2]
        inasp[k][1] = nor[3] or nor[4] or nor[5]
        inasp[k][2] = nor[6] or nor[7] or nor[8]
        inasp[k][3] = nor[0] or nor[3] or nor[6]
        inasp[k][4] = nor[1] or nor[4] or nor[7]
        inasp[k][5] = nor[2] or nor[5] or nor[8]
        for i,x in enumerate(inasp[k]):
            if x: inasp[k][i] = x/x
    return inasp

def count_paar_plan(paar):
    planpaar = { 'suns': 0, 'moons':0, 'sats':0 }
    for k in paar.keys():
        nor = [ (x+1) for x in paar[k] ]
        for i,n in enumerate(nor):
            if n and i in [0,1,2,3,6]:
                planpaar['suns'] += 1
            if n and i in [3,4,5,1,7]:
                planpaar['moons'] += 1
            if n and i in [6,7,8,2,5]:
                planpaar['sats'] += 1
    return planpaar

def count_paar_cells(paar):
    cells = 9 * [0]
    for k in paar.keys():
        for i,c in enumerate(paar[k]):
            if c > -1:
                cells[i] += 1
    return cells

class PaarWabeMixin(object):
    def __init__(self,zodiac):
        self.plan = zodiac.plan[:]
        self.zod = zodiac.zod
        self.moon_f = self.plan[1]
        self.moon_b = self.plan.pop()

    def swap_fmoon(self):
        self.plan[1] = self.moon_f
    
    def swap_bmoon(self):
        self.plan[1] = self.moon_b 

    def paarwabe_plot(self,cr,width,height,chartob):
        name = self.surface.__class__.__name__
        cx,cy = width/2,height/2
        if name == "DrawMaster":
            r = min(cx,cy)*0.80
        else:
            r = min(cx,cy)*0.8 
       
        paar = paarwabe_calc(chartob)
        planpaar = count_paar_plan(paar)
        cells = count_paar_cells(paar)
        sump = count_paar_sum(paar)
        asp, colglob = count_paar_asp(paar)
        inasp = count_paar_inasp(paar)
        sumshe = 27; sumhe = 27
        for k in inasp.keys():
            sumshe -= sum(inasp[k][0:3])
            sumhe -= sum(inasp[k][3:])
        
        rr = r * math.sin(PI*RAD/3) / math.tan(PI*RAD/3)
        cr.save()
        cr.translate(0,rr/3.8)

        rr = r*0.328
        w = pwlet; p = paar; i = inasp
        self.make_pwhexagon(cr,rr,0,-r,0,0,0,0,w['S'],w['S'],p['ss'],i['ss'])
        self.make_pwhexagon(cr,rr,r*math.cos(30*RAD),r*math.sin(30*RAD),1,1,1,1,w['R'],w['R'],
                p['rr'],i['rr'])
        self.make_pwhexagon(cr,rr,r*math.cos(150*RAD),r*math.sin(150*RAD),2,2,2,2,w['M'],w['M'],
                p['nn'],i['nn'])
        r = r*0.578 # inner circle
        self.make_pwhexagon(cr,rr,r*math.cos(-60*RAD),r*math.sin(-60*RAD),0,1,0,1,w['S'],w['R'],
                p['sr'],i['sr'])
        self.make_pwhexagon(cr,rr,r*math.cos(0*RAD),r*math.sin(0*RAD),1,0,1,0,w['R'],w['S'],
                p['rs'],i['rs'])
        self.make_pwhexagon(cr,rr,r*math.cos(60*RAD),r*math.sin(60*RAD),1,2,2,1,w['M'],w['R'],
                p['nr'],i['nr'])
        self.make_pwhexagon(cr,rr,r*math.cos(120*RAD),r*math.sin(120*RAD),2,1,1,2,w['R'],w['M'],
                p['rn'],i['rn'])
        self.make_pwhexagon(cr,rr,r*math.cos(180*RAD),r*math.sin(180*RAD),2,0,2,0,w['M'],w['S'],
                p['ns'],i['ns'])
        self.make_pwhexagon(cr,rr,r*math.cos(240*RAD),r*math.sin(240*RAD),0,2,0,2,w['S'],w['M'],
                p['sn'],i['sn'])

        # ext eggs
        cr.set_line_width(r*0.1)
        cr.save()
        cr.set_line_width(r*0.005)
        cr.scale(1,1.2)
        cr.set_source_rgb(1,0.8,0.8)
        cr.arc(0,-r*1.01,r*0.09,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(1,0.2,0.2)
        cr.stroke()
        cr.set_source_rgb(0.75,0.93,0.75)
        cr.arc(r*1.16*math.cos(30*RAD),r*0.85*math.sin(30*RAD),r*0.09,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(0.1,0.7,0.1)
        cr.stroke()
        cr.set_source_rgb(0.78,0.8,1)
        cr.arc(r*1.16*math.cos(150*RAD),r*0.85*math.sin(150*RAD),r*0.09,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(0.2,0.2,1)
        cr.stroke()
        cr.restore()

        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(10*pango.SCALE*r*3*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        
        # ext egg numbers
        cr.set_source_rgb(0.4,0.3,0.4)
        layout.set_text(sump[0])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2, -r*1.21-h/2)
        cr.show_layout(layout)
        layout.set_text(sump[1])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r*1.16*math.cos(30*RAD)-w/2,r*1.21*math.sin(30*RAD)-h*1.4)
        cr.show_layout(layout)
        layout.set_text(sump[2])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r*1.16*math.cos(150*RAD)-w/2,r*1.21*math.sin(150*RAD)-h*1.4)
        cr.show_layout(layout)

        # background
        
        #cr.set_source_rgb(0.9,0.9,0.9)
        #cr.move_to(0,0)
        #cr.line_to(rr*math.cos(-30*RAD),rr*math.sin(-30*RAD))
        #cr.line_to(rr*math.cos(30*RAD),rr*math.sin(30*RAD))
        #cr.close_path()
        #cr.fill() 
        #cr.move_to(0,0)
        #cr.line_to(rr*math.cos(-150*RAD),rr*math.sin(-150*RAD))
        #cr.line_to(rr*math.cos(150*RAD),rr*math.sin(150*RAD))
        #cr.close_path()
        #cr.fill() 

        cr.set_source_rgb(1,0.86,0.65)
        cr.move_to(0,0)
        cr.line_to(rr*0.87*math.cos(180*RAD),rr*0.87*math.sin(180*RAD))
        cr.line_to(rr*math.cos(210*RAD),rr*math.sin(210*RAD))
        cr.line_to(rr*math.cos(-90*RAD),rr*math.sin(-90*RAD))
        cr.close_path()
        cr.fill() 
        cr.set_source_rgb(1,0.85,0.86)
        cr.move_to(0,0)
        cr.line_to(rr*0.87*math.cos(0*RAD),rr*0.87*math.sin(0*RAD))
        cr.line_to(rr*math.cos(-30*RAD),rr*math.sin(-30*RAD))
        cr.line_to(rr*math.cos(-90*RAD),rr*math.sin(-90*RAD))
        cr.close_path()
        cr.fill() 
        
        cr.set_source_rgb(0.93,0.85,0.48)
        cr.move_to(0,0)
        cr.line_to(rr*0.87*math.cos(180*RAD),rr*0.87*math.sin(180*RAD))
        cr.line_to(rr*math.cos(150*RAD),rr*math.sin(150*RAD))
        cr.line_to(rr*math.cos(90*RAD),rr*math.sin(90*RAD))
        cr.close_path()
        cr.fill() 
        cr.set_source_rgb(0.88,0.63,1)
        cr.move_to(0,0)
        cr.line_to(rr*0.87*math.cos(0*RAD),rr*0.87*math.sin(0*RAD))
        cr.line_to(rr*math.cos(30*RAD),rr*math.sin(30*RAD))
        cr.line_to(rr*math.cos(90*RAD),rr*math.sin(90*RAD))
        cr.close_path()
        cr.fill() 
        
        cr.set_line_width(r*0.005)
        # transparecny
        #cr.set_source_rgba(0.7,0.7,0.7,0.6)
        #cr.move_to(rr*math.cos(210*RAD),rr*math.sin(210*RAD))
        #cr.line_to(rr*math.cos(-30*RAD),rr*math.sin(-30*RAD))
        #cr.line_to(rr*math.cos(30*RAD),rr*math.sin(30*RAD))
        #cr.line_to(rr*math.cos(150*RAD),rr*math.sin(150*RAD))
        #cr.close_path()
        #cr.fill()
        #cr.set_source_rgb(0.3,0.2,0.3)
        #cr.move_to(rr*math.cos(210*RAD),rr*math.sin(210*RAD))
        #cr.line_to(rr*math.cos(-30*RAD),rr*math.sin(-30*RAD))
        #cr.stroke()
        #cr.move_to(rr*math.cos(30*RAD),rr*math.sin(30*RAD))
        #cr.line_to(rr*math.cos(150*RAD),rr*math.sin(150*RAD))
        #cr.stroke()

        rrr = rr*0.18
        cr.save()
        cr.set_source_rgb(0.9,0.85,1)
        # hexagon tot fig.
        #cr.move_to(rrr,0)
        #cr.line_to(rrr*math.cos(60*RAD),rrr*math.sin(60*RAD))
        #cr.line_to(rrr*math.cos(120*RAD),rrr*math.sin(120*RAD))
        #cr.line_to(-rrr,0)
        #cr.line_to(rrr*math.cos(240*RAD),rrr*math.sin(240*RAD))
        #cr.line_to(rrr*math.cos(-60*RAD),rrr*math.sin(-60*RAD))
        #cr.close_path()
        #cr.fill_preserve()
        #cr.set_source_rgb(0.5,0.2,0.5)
        #cr.stroke()
        
        # cuasi penta
        cr.set_source_rgb(0.8,0.91,1)
        cr.move_to(0,-rr)
        cr.line_to(rrr*4.79*math.cos(240*RAD),rrr*4.79*math.sin(240*RAD))
        cr.line_to(rrr*math.cos(240*RAD),rrr*math.sin(240*RAD))
        cr.line_to(rrr*math.cos(-60*RAD),rrr*math.sin(-60*RAD))
        cr.line_to(rrr*4.79*math.cos(-60*RAD),rrr*4.79*math.sin(-60*RAD))
        cr.close_path()
        cr.fill_preserve()
        cr.set_source_rgb(0.5,0.7,0.5)
        cr.stroke()
       
        # asp numbers
        cr.set_source_rgb(0.4,0.3,0.4)
        #layout.set_text(str(asp[0]+asp[1]+asp[2]))
        #ink,logical = layout.get_extents()
        #w = logical[2]/pango.SCALE
        #h = logical[3]/pango.SCALE
        #cr.move_to(-w/2, -h/2)
        #cr.show_layout(layout)
        
        layout.set_text(str(asp[0]+asp[1]))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-rr*0.27-w/2,-rr*0.16 -h/2)
        cr.show_layout(layout)
        
        layout.set_text(str(asp[2]))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(rr*0.27-w/2, -rr*0.16 -h/2)
        cr.show_layout(layout)
        
        # inasp
        cr.translate(0,-rr*0.5)
        layout.set_text(str(sumshe))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-rr*0.15-w/2, rr*1.26 -h/2)
        cr.show_layout(layout)
        layout.set_text(str(sumhe))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(rr*0.15-w/2, rr*1.26 -h/2)
        cr.show_layout(layout)
        cr.restore()

        # triangles
        cr.set_line_width(r*0.01)
        cr.set_source_rgb(1,0.8,0.8)
        cr.move_to(0,r*1.16)
        cr.line_to(r*0.5,r*1.44)
        cr.line_to(-r*0.5,r*1.44)
        cr.close_path()
        cr.fill()
        cr.set_source_rgb(1,0.1,0.1)
        cr.move_to(r*0.5,r*1.44)
        cr.line_to(-r*0.5,r*1.44)
        cr.stroke()
        cr.set_source_rgb(0.8,1,0.8)
        cr.move_to(r,r*1.16)
        cr.line_to(r*1.5,r*1.44)
        cr.line_to(r*0.5,r*1.44)
        cr.close_path()
        cr.fill()
        cr.set_source_rgb(0.1,0.7,0.1)
        cr.move_to(r*1.5,r*1.44)
        cr.line_to(r*0.5,r*1.44)
        cr.stroke()
        cr.set_source_rgb(0.8,0.8,1)
        cr.move_to(-r,r*1.16)
        cr.line_to(-r*1.5,r*1.44)
        cr.line_to(-r*0.5,r*1.44)
        cr.close_path()
        cr.fill()
        cr.set_source_rgb(0.1,0.1,0.8)
        cr.move_to(-r*1.5,r*1.44)
        cr.line_to(-r*0.5,r*1.44)
        cr.stroke()
        cr.set_source_rgb(0.4,0.3,0.4)
        layout.set_text(str(colglob[0]))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2, r*1.35-h/2)
        cr.show_layout(layout)
        layout.set_text(str(colglob[1]))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w/2, r*1.35-h/2)
        cr.show_layout(layout)
        layout.set_text(str(colglob[2]))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-r-w/2, r*1.35-h/2)
        cr.show_layout(layout)

        font.set_size(int(6*pango.SCALE*r*3*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        layout.set_text('MAX.:45')
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r*0.3-w/2, r * 0.04 -h/2)
        cr.show_layout(layout)
        cr.new_path()
        
        # inn eggs
        cr.set_line_width(r*0.1)
        cr.save()
        cr.set_line_width(r*0.004)
        cr.scale(1,1.2)
        cr.set_source_rgb(1,0.8,0.8)
        cr.arc(0,-r*0.37,r*0.09,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(1,0.2,0.2)
        cr.stroke()
        cr.set_source_rgb(0.75,0.93,0.75)
        cr.arc(r*0.46*math.cos(30*RAD),r*0.35*math.sin(30*RAD),r*0.09,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(0.1,0.7,0.1)
        cr.stroke()
        cr.set_source_rgb(0.78,0.8,1)
        cr.arc(r*0.46*math.cos(150*RAD),r*0.35*math.sin(150*RAD),r*0.09,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(0.2,0.2,1)
        cr.stroke()
        cr.restore()
        font.set_size(int(9*pango.SCALE*r*3*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        layout.set_text(str(planpaar['suns']))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2, -r * 0.44 -h/2)
        cr.show_layout(layout)
        layout.set_text(str(planpaar['moons']))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r*0.4-w/2, r * 0.22 -h/2)
        cr.show_layout(layout)
        layout.set_text(str(planpaar['sats']))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-r*0.4-w/2, r * 0.22 -h/2)
        cr.show_layout(layout)
        

        # center hex
        cr.set_line_width(r*0.008)
        r = r*0.11
        cr.set_source_rgb(0.87,0.93,0.89)
        cr.move_to(0,0)
        cr.line_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.close_path()
        cr.fill()
        cr.set_source_rgb(0.85,0.9,0.8)
        cr.move_to(0,0)
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.close_path()
        cr.fill()
        cr.set_source_rgb(0.9,0.95,0.9)
        cr.move_to(0,0)
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.line_to(0,-r)
        cr.close_path()
        cr.fill()
        cr.move_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.close_path()
        cr.set_source_rgb(0.5,0.2,0.5)
        cr.stroke()
        cr.set_source_rgb(0.4,0.3,0.4)
        layout.set_text(str(asp[0]+asp[1]+asp[2]))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2, -h/2)
        cr.show_layout(layout)
        
        # ext yellow
        r /= 0.11
        rrr = rr*0.2; fs = 18
        self.make_yellowpw(cr,rrr,0,-r*2.4,cells[0],True,0)
        self.make_yellowpw(cr,rrr,r*0.9*math.cos(30*RAD),-r*2.67*math.sin(30*RAD),cells[1],True,0,fs)
        self.make_yellowpw(cr,rrr,-r*0.9*math.cos(30*RAD),-r*2.67*math.sin(30*RAD),cells[2],True,0,fs)
        self.make_yellowpw(cr,rrr,r*2.0*math.cos(30*RAD),r*2.72*math.sin(30*RAD),cells[4],True,1,fs)
        self.make_yellowpw(cr,rrr,r*0.58*math.cos(30*RAD),r*3.0*math.sin(30*RAD),cells[7],True,1,fs)
        self.make_yellowpw(cr,rrr,r*1.8*math.cos(30*RAD),-r*0.65*math.sin(30*RAD),cells[3],True,1,fs)
        self.make_yellowpw(cr,rrr,-r*2.0*math.cos(30*RAD),r*2.72*math.sin(30*RAD),cells[8],True,2,fs)
        self.make_yellowpw(cr,rrr,-r*0.58*math.cos(30*RAD),r*3.0*math.sin(30*RAD),cells[5],True,2,fs)
        self.make_yellowpw(cr,rrr,-r*1.8*math.cos(30*RAD),-r*0.65*math.sin(30*RAD),cells[6],True,2,fs)
        cr.restore()
    
    def make_pwhexagon(self,cr,r,x,y,co,ci,il,ir,ll,lr,paar,inasp):
        bcol = [(0.9,0,0),(0,0.7,0),(0,0,9)]
        icol = [(1,0.7,0.7),(0.63,1,0.63),(0.75,0.8,1)]
        dcol = [(0.93,0.85,0.48),(0.88,0.63,1)]
        cr.save()
        cr.set_line_width(r*0.04)
        cr.translate(x,y)
        cr.set_source_rgb(*bcol[co])
        cr.move_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.close_path()
        cr.stroke()
        r *= 0.96
        cr.set_source_rgb(*bcol[ci])
        cr.move_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.close_path()
        cr.stroke() 
        cr.set_source_rgb(*icol[il])
        cr.move_to(0,0)
        cr.line_to(0,-r)
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.close_path()
        cr.fill() 
        cr.set_source_rgb(*icol[ir])
        cr.move_to(0,0)
        cr.line_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.close_path()
        cr.fill() 
        cr.set_source_rgb(*dcol[0])
        cr.move_to(0,0)
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.close_path()
        cr.fill() 
        cr.set_source_rgb(*dcol[1])
        cr.move_to(0,0)
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.close_path()
        cr.fill() 
        
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(40*pango.SCALE*r*3*MAGICK_FONTSCALE))
        font.set_style(pango.STYLE_ITALIC)
        layout.set_font_description(font)
        cr.set_source_rgb(*she_col)
        layout.set_text(ll)
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-r*0.7-w/1.8, -r*0.5-h/5)
        cr.show_layout(layout)
        cr.set_source_rgb(*he_col)
        layout.set_text(lr)
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r*0.73-w/1.8, -r*0.5-h/5)
        cr.show_layout(layout)

        self.swap_bmoon()
        col = [she_col,he_col]
        pls = [0,1,6]
        xx = [-6,-5.9,-3,4.5,3.6,0.2]
        yy = [8.8,9.9,8.4,8.6,9.8,8.4]
        scl = 0.006*r
        for i,a in enumerate(inasp):
            if not a:
                pl = pls[i%3]
                cr.set_source_rgb(*col[i/3])
                x_b,_,w,hh,_,y_b = self.plan[pl].extents
                cr.save()
                cr.translate(xx[i]*scl*w/2,yy[i]*scl*hh/2)
                cr.scale(scl,scl)
                self.warpPath(cr,self.plan[pl].paths)
                cr.fill()
                cr.restore()
        self.swap_fmoon()

        p = paar
        rrr = r*0.247; r2 = r*0.74
        n = len([ n for n in p if n > -1 ])
        self.make_yellowpw(cr,rrr,0,0,n)
        self.make_innerpw(cr,rrr,0,-r2,0,0,0,0,p[0])
        self.make_innerpw(cr,rrr,r2*math.cos(30*RAD),r2*math.sin(30*RAD),1,1,1,1,p[4])
        self.make_innerpw(cr,rrr,r2*math.cos(150*RAD),r2*math.sin(150*RAD),2,2,6,6,p[8])
        r2 = r2*0.57 # inner circle
        self.make_innerpw(cr,rrr,r2*math.cos(-60*RAD),r2*math.sin(-60*RAD),0,1,1,0,p[1])
        self.make_innerpw(cr,rrr,r2*math.cos(0*RAD),r2*math.sin(0*RAD),1,0,0,1,p[3])
        self.make_innerpw(cr,rrr,r2*math.cos(60*RAD),r2*math.sin(60*RAD),1,2,1,6,p[7])
        self.make_innerpw(cr,rrr,r2*math.cos(120*RAD),r2*math.sin(120*RAD),2,1,6,1,p[5])
        self.make_innerpw(cr,rrr,r2*math.cos(180*RAD),r2*math.sin(180*RAD),2,0,0,6,p[6])
        self.make_innerpw(cr,rrr,r2*math.cos(240*RAD),r2*math.sin(240*RAD),0,2,6,0,p[2])
        cr.restore()

    def make_innerpw(self,cr,r,x,y,co,ci,pa,pb,a):
        bcol = [(0.9,0,0),(0,0.7,0),(0,0,9)]
        icol = [(1,0.7,0.7),(0.63,1,0.63),(0.75,0.8,1)]
        she_col = (0.8,0.7,0) # (0.72,0.58,0)
        he_col = (0.4,0,0.6) # (0.48,0,0.66)
        cr.save()
        cr.set_line_width(r*0.04)
        cr.translate(x,y)
        cr.move_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.close_path()
        cr.set_source_rgb(1,1,1)
        cr.fill_preserve()
        if a > -1:
            alet = asplet[a] 
            col = list(aspcolors[int(alet)-1]) + [0.4]
            cr.set_source_rgba(*col)
            cr.fill_preserve()
        cr.set_source_rgb(*bcol[co])
        cr.stroke()
        r *= 0.96
        cr.set_source_rgb(*bcol[ci])
        cr.move_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.close_path()
        cr.stroke() 
        self.swap_bmoon()
        scl = 0.020*r
        cr.set_source_rgb(*he_col)
        x_b,_,w,hh,_,y_b = self.plan[pa].extents
        cr.save()
        offh = w/1.4
        offv = hh*0.6
        if pa == 0: offh = w/2.45
        if pa == 6: offv = hh*0.5
        cr.translate(-scl*offh,-1.2*scl*offv)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[pa].paths)
        cr.fill()
        cr.restore()
        cr.set_source_rgb(*she_col)
        x_b,_,w,hh,_,y_b = self.plan[pb].extents
        cr.save()
        offh = w/1.2
        offv = hh*0.6
        if pb == 0: offh = w/2.45
        if pb == 6: offv = hh*0.5
        cr.translate(-scl*offh,2.8*scl*offv)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[pb].paths)
        cr.fill()
        cr.restore()
        layout = cr.create_layout()
        font = pango.FontDescription('Astro-Nex')
        font.set_size(int(10*pango.SCALE*r*26*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        if a > -1:
            alet = asplet[a] 
            cr.set_source_rgb(*aspcolors[int(alet)-1])
            layout.set_text(alet)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(-w*0.5,-h/1.8)
            cr.layout_path(layout)
            cr.fill()
        cr.restore()
        self.swap_fmoon()

    def make_yellowpw(self,cr,r,x,y,n,stroke=False,ix=0,fs=16):
        cols = [(0.9,0.1,0.1),(0.1,0.7,0.1),(0.1,0.2,0.8)]
        cr.save()
        cr.set_line_width(r*0.04)
        cr.translate(x,y)
        cr.set_source_rgb(1,1,0)
        cr.move_to(0,-r)
        cr.line_to(r*math.cos(-30*RAD),r*math.sin(-30*RAD))
        cr.line_to(r*math.cos(30*RAD),r*math.sin(30*RAD))
        cr.line_to(r*math.cos(90*RAD),r*math.sin(90*RAD))
        cr.line_to(r*math.cos(150*RAD),r*math.sin(150*RAD))
        cr.line_to(r*math.cos(210*RAD),r*math.sin(210*RAD))
        cr.close_path()
        if stroke:
            cr.fill_preserve()
            cr.set_source_rgb(*cols[ix])
            cr.stroke()
        else:
            cr.fill()
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(fs*pango.SCALE*r*14*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        cr.set_source_rgb(0.4,0.3,0.4)
        layout.set_text(str(n))
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2, -h/2)
        cr.show_layout(layout)
        cr.restore()
    
    def compo_two(self,cr,width,height,chartob):
        she_asp, he_asp = crown_calc(chartob)
        she_col = [(0.48,0.4,0.08),(0.6,0.5,0.2),(0.8,0.72,0.43)]
        he_col = [(0.48,0,0.66),(0.6,0.17,0.76),(0.81,0.5,0.91)]
        
        try:
            fullscreen = self.surface.fullscreen
        except AttributeError:
            fullscreen = False
        
        cr.translate(-width/2.8,-height/4)
        if not fullscreen:
            cr_h = height/2.5
        else:
            cr_h = height/2.1
        self.crown_plot(cr,width/2,cr_h,she_asp,she_col)
        cr.translate(2*width/2.8,0)
        self.crown_plot(cr,width/2,cr_h,he_asp,he_col)
        cr.translate(-width/2.8,0)
        
        if not fullscreen:
            cr.translate(0,height/5.6)
        else:
            cr.translate(0,height/8)
        cr.save()
        self.paarwabe_plot(cr,width*0.7,height*0.7,chartob)
        cr.restore()
        if not fullscreen:
            cr.translate(-width*.3,height/4.5)
        else:
            cr.translate(-width*.3,height/3.5)
        self.comp_pe(cr,width*0.6,height*0.5,chartob,texts=False)
    
    def crown_comp(self,cr,width,height,chartob):
        name = self.surface.__class__.__name__
        she_asp, he_asp = crown_calc(chartob)
        she_col = [(0.48,0.4,0.08),(0.6,0.5,0.2),(0.8,0.72,0.43)]
        he_col = [(0.48,0,0.66),(0.6,0.17,0.76),(0.81,0.5,0.91)]

        if name == "DrawMaster":
            scl_w = 2
            scl_h = 1
        else:
            scl_h = 1.3
            scl_w = 3
        cr.save()
        cr.translate(-width/4,0)
        self.crown_plot(cr,width/scl_w,height/scl_h,she_asp,she_col)
        cr.translate(width/2,0)
        self.crown_plot(cr,width/scl_w,height/scl_h,he_asp,he_col)
        cr.restore()

    def crown_plot(self,cr,width,height,asp,col):
        cx,cy = width/2,height/2
        if cx < cy:
            r = max(cx,cy)*0.95 
        else:
            r = min(cx,cy)*0.95 
        ry = r*0.6
        rx = r*0.6*0.46   # magick, 0.46 
        
        paleblue = (0.68,0.9,0.95)
        pink = (1.0,0.77,0.87)
        pat = cairo.LinearGradient(-rx*1.32,0,rx*1.32,0)
        pat.add_color_stop_rgb(0,*col[1])
        pat.add_color_stop_rgb(0.5,*col[2])
        pat.add_color_stop_rgb(1,*col[1])
        cr.set_source(pat)
        cr.arc(0,-ry*0.9,rx*1.65,-206*RAD,28*RAD)
        cr.arc_negative(rx*4.05,0,rx*1.73*1.65,-160*RAD,-200*RAD)
        cr.arc(0,ry*0.9,rx*1.65,-26*RAD,206*RAD)
        cr.arc_negative(-rx*4.05,0,rx*1.73*1.65,20*RAD,-20*RAD)
        cr.close_path()
        cr.fill()
        cr.set_source_rgb(0,0,0)
        cr.set_source_rgb(1,1,1)
        cr.arc(0,-ry*0.9,rx*1.25,0,180*PI)
        cr.arc(0,ry*0.9,rx*1.25,0,180*PI)
        cr.fill()
        cr.set_source_rgb(*paleblue)
        cr.arc(0,-ry*0.9,rx*0.8,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(0.4,0.3,0.4)
        cr.stroke()
        cr.set_source_rgb(*pink)
        cr.arc(0,ry*0.9,rx*0.8,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(0.4,0.3,0.4)
        cr.stroke()

        cr.set_source_rgb(*col[0])
        points = [-rx*0.78,0,rx*0.78]
        for xi in points:
            cr.save()
            cr.scale(1,1.36)
            cr.arc(xi,0,rx*0.35,0,180*PI)
            cr.fill()
            cr.restore()
        
        self.swap_bmoon()
        cr.set_source_rgb(1,0.5,0) 
        for i,pl in enumerate((6,1,0)):
            scl = 0.010*ry
            points = [-rx*0.76,0,rx*0.76]
            x_b,_,w,hh,_,y_b = self.plan[pl].extents
            cr.save()
            if pl == 0: 
                off = w/2.45
            else:
                off = w/1.4
            cr.translate(points[i]-scl*off,scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
            points = [(-rx*0.6,-ry*0.8),(-0.3,-ry*0.98),(rx*0.6,-ry*0.8)]
            scl = 0.006*ry
            cr.save()
            off = w/1.8
            cr.translate(points[i][0]-scl*off,points[i][1]-scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
            points = [(-rx*0.65,ry*1.15),(-0.3,ry*1.31),(rx*0.58,ry*1.15)]
            scl = 0.006*ry
            cr.save()
            off = w/1.8
            cr.translate(points[i][0]-scl*off,points[i][1]-scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
        
        scl = 0.007*ry
        cr.set_source_rgb(*self.plan[2].col) 
        for i,pl in enumerate((7,8,9)):
            points = [(-rx*1.46,-ry*0.85),(0,-ry*1.4),(rx*1.49,-ry*0.85)]
            x_b,_,w,hh,_,y_b = self.plan[pl].extents
            off = w/1.8
            cr.save()
            cr.translate(points[i][0]-scl*off,points[i][1]-scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
            points = [(-rx*0.46,ry*0.9),(0,ry*0.8),(rx*0.46,ry*0.9)]
            cr.save()
            cr.translate(points[i][0]-scl*off,points[i][1]-scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()

        cr.set_source_rgb(*self.plan[2].col) 
        for i,pl in enumerate((3,2,5,4)):
            scl = 0.007*ry
            points = [(-rx*1.44,ry*1.15),(-rx*0.5,ry*1.7),(rx*0.5,ry*1.7),(rx*1.42,ry*1.15)]
            x_b,_,w,hh,_,y_b = self.plan[pl].extents
            off = w/1.8
            cr.save()
            cr.translate(points[i][0]-scl*off,points[i][1]-scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
            scl = 0.006*ry
            points = [(-rx*0.48,-ry*0.6),(-rx*0.15,-ry*0.5),
                    (rx*0.18,-ry*0.5),(rx*0.48,-ry*0.6)]
            cr.save()
            cr.translate(points[i][0]-scl*off,points[i][1]-scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
        
        # arrows
        cr.set_source_rgb(*self.plan[2].col) 
        cr.move_to(-rx*0.758,-ry*0.8)
        cr.curve_to(-rx*0.85,-ry*0.55,-rx*0.85,-ry*0.55,-rx*0.86,-ry*0.33)
        cr.line_to(-rx*1.08,-ry*0.35) #
        cr.line_to(-rx*0.76,-ry*0.22) #sat
        cr.line_to(-rx*0.43,-ry*0.35)  #
        cr.line_to(-rx*0.66,-ry*0.33)  #
        x1 = -rx*0.65; y1 = -ry*0.45; x2 = -rx*0.56; y2 = -ry*0.6
        cr.curve_to(x1,y1,x2,y2,-rx*0.35,-ry*0.65)
        cr.line_to(-rx*0.58,-ry*0.65)
        cr.close_path()
        cr.fill()

        cr.move_to(-rx*0.758,ry*0.8)
        cr.curve_to(-rx*0.85,ry*0.55,-rx*0.85,ry*0.55,-rx*0.86,ry*0.33)
        cr.line_to(-rx*1.08,ry*0.35) #
        cr.line_to(-rx*0.76,ry*0.22) #sat
        cr.line_to(-rx*0.43,ry*0.35)  #
        cr.line_to(-rx*0.66,ry*0.33)  #
        x1 = -rx*0.65; y1 = ry*0.45; x2 = -rx*0.56; y2 = ry*0.6
        cr.curve_to(x1,y1,x2,y2,-rx*0.35,ry*0.65)
        cr.line_to(-rx*0.58,ry*0.65)
        cr.close_path()
        cr.fill()
        
        cr.set_source_rgb(1,0,0) 
        cr.move_to(rx*0.758,-ry*0.8)
        cr.curve_to(rx*0.85,-ry*0.55,rx*0.85,-ry*0.55,rx*0.86,-ry*0.33)
        cr.line_to(rx*1.08,-ry*0.35) #
        cr.line_to(rx*0.76,-ry*0.22) #sat
        cr.line_to(rx*0.43,-ry*0.35)  #
        cr.line_to(rx*0.66,-ry*0.33)  #
        x1 = rx*0.65; y1 = -ry*0.45; x2 = rx*0.56; y2 = -ry*0.6
        cr.curve_to(x1,y1,x2,y2,rx*0.35,-ry*0.65)
        cr.line_to(rx*0.58,-ry*0.65)
        cr.close_path()
        cr.fill()

        cr.move_to(rx*0.758,ry*0.8)
        cr.curve_to(rx*0.85,ry*0.55,rx*0.85,ry*0.55,rx*0.86,ry*0.33)
        cr.line_to(rx*1.08,ry*0.35) #
        cr.line_to(rx*0.76,ry*0.22) #sat
        cr.line_to(rx*0.43,ry*0.35)  #
        cr.line_to(rx*0.66,ry*0.33)  #
        x1 = rx*0.65; y1 = ry*0.45; x2 = rx*0.56; y2 = ry*0.6
        cr.curve_to(x1,y1,x2,y2,rx*0.35,ry*0.65)
        cr.line_to(rx*0.58,ry*0.65)
        cr.close_path()
        cr.fill()
        
        cr.set_source_rgb(0,0.7,0) 
        cr.move_to(0,ry*0.22)
        cr.line_to(-rx*0.3,ry*0.328)
        cr.line_to(-rx*0.1,ry*0.32)
        cr.line_to(-rx*0.23,ry*0.55)
        cr.line_to(0,ry*0.53)
        cr.line_to(rx*0.23,ry*0.55) 
        cr.line_to(rx*0.1,ry*0.32)
        cr.line_to(rx*0.3,ry*0.328)
        cr.close_path()
        cr.fill()

        cr.set_source_rgb(0,0.7,0) 
        cr.move_to(-rx*0.03,-ry*0.22)
        cr.line_to(-rx*0.03,-ry*0.345)
        cr.line_to(-rx*0.15,-ry*0.32) 
        x1 = -rx*0.16; y1 = -ry*0.46; x2 = -rx*0.18; y2 = -ry*0.48
        cr.curve_to(x1,y1,x2,y2,-rx*0.07,-ry*0.56)
        cr.line_to(-rx*0.20,-ry*0.55)
        cr.line_to(-rx*0.35,-ry*0.6)
        x1 = -rx*0.36; y1 = -ry*0.46; x2 = -rx*0.32; y2 = -ry*0.42
        cr.curve_to(x1,y1,x2,y2,-rx*0.175,-ry*0.32)
        cr.line_to(-rx*0.32,-ry*0.31)
        cr.close_path()
        cr.fill()

        cr.set_source_rgb(0,0.7,0) 
        cr.move_to(rx*0.03,-ry*0.22)
        cr.line_to(rx*0.03,-ry*0.345)
        cr.line_to(rx*0.15,-ry*0.32) 
        x1 = rx*0.16; y1 = -ry*0.46; x2 = rx*0.18; y2 = -ry*0.48
        cr.curve_to(x1,y1,x2,y2,rx*0.07,-ry*0.56)
        cr.line_to(rx*0.20,-ry*0.55)
        cr.line_to(rx*0.35,-ry*0.6)
        x1 = rx*0.36; y1 = -ry*0.46; x2 = rx*0.32; y2 = -ry*0.42
        cr.curve_to(x1,y1,x2,y2,rx*0.175,-ry*0.32)
        cr.line_to(rx*0.32,-ry*0.31)
        cr.close_path()
        cr.fill()
        
        self.make_crown_circle(cr,rx,rx*1.02,-ry*0.97,'1',asp['1'])
        self.make_crown_circle(cr,rx,0,-ry*1.37,'2',asp['2'])
        self.make_crown_circle(cr,rx,-rx*1.02,-ry*0.97,'3',asp['3'])
        self.make_crown_circle(cr,rx,-rx*0.70,-ry*0.55,'4',asp['4'])
        self.make_crown_circle(cr,rx,-rx*0.23,-ry*0.43,'5',asp['5a'])
        self.make_crown_circle(cr,rx,rx*0.23,-ry*0.43,'5',asp['5b'])
        self.make_crown_circle(cr,rx,rx*0.70,-ry*0.55,'6',asp['6'])
        self.make_crown_circle(cr,rx,rx*0.72,ry*0.56,'7',asp['7'])
        self.make_crown_circle(cr,rx,0,ry*0.43,'8',asp['8'])
        self.make_crown_circle(cr,rx,-rx*0.72,ry*0.56,'9',asp['9'])
        self.make_crown_circle(cr,rx,-rx*1.01,ry*0.98,'10',asp['10'])
        self.make_crown_circle(cr,rx,-rx*0.275,ry*1.36,'11',asp['11a'])
        self.make_crown_circle(cr,rx,rx*0.275,ry*1.36,'11',asp['11b'])
        self.make_crown_circle(cr,rx,rx*1.01,ry*0.98,'12',asp['12'])

        self.swap_fmoon()
        
    def make_crown_circle(self,cr,rr,x,y,n,a):
        cr.set_source_rgb(0.87,0.79,0.9)
        cr.arc(x,y,rr*0.22,0,180*PI)
        cr.fill_preserve()
        cr.set_source_rgb(0.4,0.2,0.4)
        cr.stroke()
        cr.arc(x,y-rr*0.18,rr*0.065,0,180*PI)
        cr.set_source_rgb(0.85,0.87,0.9)
        cr.fill_preserve()
        cr.set_source_rgb(0.4,0.2,0.4)
        cr.stroke()
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(6*pango.SCALE*rr*6*MAGICK_FONTSCALE))
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(n)
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(x-w/2,y-rr*0.18-h/2)
        cr.show_layout(layout)
        cr.fill()
        font = pango.FontDescription('Astro-Nex')
        font.set_size(int(14*pango.SCALE*rr/0.13*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        if a > -1000:
            if a > -1:
                a = -a
            alet = asplet[a] 
            cr.set_source_rgb(*aspcolors[int(alet)-1])
            layout.set_text(alet)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(x-w*0.5,y-h/2)
            cr.layout_path(layout)
            cr.fill()
    
    def compo_one(self,cr,width,height,chartob):
        name = self.surface.__class__.__name__
        try:
            fullscreen = self.surface.fullscreen
        except AttributeError:
            fullscreen = False
        cx,cy = width/2,height/2
        cr.set_source_rgb(0.3,0.3,0.3)
        cr.save()
        cr.set_line_width(2)
        cr.move_to(-cx*0.05,-cy*0.9)
        cr.line_to(-cx*0.05,cy*0.88)
        cr.stroke()
        if not fullscreen:
            layout = cr.create_layout()
            font = pango.FontDescription(boss.opts.font)
            font.set_size(int(6*pango.SCALE*width*0.95*MAGICK_FONTSCALE))
            font.set_weight(pango.WEIGHT_BOLD)
            font.set_style(pango.STYLE_ITALIC)
            layout.set_font_description(font)
            cr.move_to(-cx*0.085,-cy*0.45)
            cr.rotate(-90*RAD)
            layout.set_text(_('Consciente'))
            cr.show_layout(layout)
            cr.rotate(90*RAD)
            cr.move_to(-cx*0.085,cy*0.04)
            cr.rotate(-90*RAD)
            layout.set_text(_('Subconsciente'))
            cr.show_layout(layout) 
            cr.rotate(90*RAD)
            cr.move_to(-cx*0.085,cy*0.35)
            cr.rotate(-90*RAD)
            layout.set_text(_('Inconsciente'))
            cr.show_layout(layout) 
            cr.restore()
        
        cr.new_path()
        cr.save()
        if not fullscreen:
            cr.translate(-cx/2,cy*0.76-cy)
            #cr.translate(-cx/2,-cy*0.9)
            self.polar_star(cr,cx,height*0.65,chartob)
            cr.translate(0,cy*0.7)
            font.set_size(int(8*pango.SCALE*width*0.95*MAGICK_FONTSCALE))
            layout.set_font_description(font)
            layout.set_text(polar_texts['P0'])
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(-w/2,-h/4)
            cr.set_source_rgb(0.1,0.1,0.1)
            cr.show_layout(layout)
            cr.translate(0,cy*0.06) 
            self.text_for_polar(cr,cx,height*0.2)
        else:
            cr.translate(-cx/2,0)
            self.polar_star(cr,cx,height*0.9,chartob)
        cr.restore()
        cr.save()
        if not fullscreen:
            cr.translate(cx/2.1,-cy/1.7)
            self.ascent_star(cr,cx*0.9,cy*0.9,chartob)
            cr.translate(0,cy/3.5)
            layout.set_text(ascent_texts['a0'])
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(-w/2,-h/2)
            cr.set_source_rgb(1,0.1,0.1)
            cr.show_layout(layout)
            cr.translate(-cx/2.1,cy*0.03)
            self.text_for_ascent(cr,cx)
        else:
            cr.translate(cx/2.1,-cy/2.5)
            self.ascent_star(cr,cx,cy,chartob)
        cr.restore()
        cr.new_path()

        if not fullscreen:
            cr.translate(cx/2.1,cy*0.3)
        else:
            cr.translate(cx/2.1,cy*0.5)
        if name == "DrawPng":
            self.wundersensi_star(cr,cx,cy,chartob)
        else:
            self.wundersensi_star(cr,cx*0.9,cy*0.9,chartob)
        if not fullscreen:
            cr.translate(-cx/2.1,cy*0.37)
            self.text_for_wunder(cr,width)


    def text_for_wunder(self,cr,width):
        r = width*0.76
        v = r*0.022
        w_col = (0.6,0,0.6)
        s_col = (0,0.6,0.2)
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        
        font.set_size(int(8*pango.SCALE*width*0.95*MAGICK_FONTSCALE))
        font.set_weight(pango.WEIGHT_BOLD)
        font.set_style(pango.STYLE_ITALIC)
        layout.set_font_description(font)
        cr.set_source_rgb(*w_col)
        layout.set_text(wunder_texts['w0'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width*0.47-w,0)
        cr.show_layout(layout)
        cr.set_source_rgb(*s_col)
        layout.set_text(wunder_texts['s0'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width*0.47-w,v*2.5)
        cr.show_layout(layout)
        
        font.set_size(int(6*pango.SCALE*r*1.1*MAGICK_FONTSCALE))
        font.set_weight(pango.WEIGHT_NORMAL)
        font.set_style(pango.STYLE_NORMAL)
        layout.set_font_description(font)
        
        cr.set_source_rgb(*w_col)
        layout.set_text("1  %s" % wunder_texts['w1'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,0)
        cr.show_layout(layout)
        layout.set_text("2  %s" % wunder_texts['w2'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v)
        cr.show_layout(layout)
        layout.set_text("3  %s" % wunder_texts['w3'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*2)
        cr.show_layout(layout)
        layout.set_text("4  %s" % wunder_texts['w4'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*3)
        cr.show_layout(layout)
        cr.set_source_rgb(*s_col)
        layout.set_text("1  %s" % wunder_texts['s1'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width*0.47-w,v*4)
        cr.show_layout(layout)
        layout.set_text("2  %s" % wunder_texts['s2'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width*0.47-w,v*5)
        cr.show_layout(layout)
        layout.set_text("3  %s" % wunder_texts['s3'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width*0.47-w,v*6)
        cr.show_layout(layout)
        layout.set_text("4  %s" % wunder_texts['s4'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width*0.47-w,v*7)
        cr.show_layout(layout)
        layout.set_text("5  %s" % wunder_texts['s5'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width*0.47-w,v*8)
        cr.show_layout(layout)

    def text_for_ascent(self,cr,width):
        r = width*0.76
        v = r*0.045
        fem_col = (0,0.2,0.6)
        mas_col = (0.7,0,0)
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(7*pango.SCALE*r*1.9*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        
        cr.set_source_rgb(*mas_col)
        layout.set_text("1  %s" % ascent_texts['a1'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,0)
        cr.show_layout(layout)
        layout.set_text("2  %s" % ascent_texts['a2'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v)
        cr.show_layout(layout)
        layout.set_text("3  %s" % ascent_texts['a3'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*2)
        cr.show_layout(layout)
        layout.set_text("%s" % ascent_texts['a3b'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*3)
        cr.show_layout(layout)
        layout.set_text("4  %s" % ascent_texts['a4'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*4)
        cr.show_layout(layout)
        layout.set_text("%s" % ascent_texts['a4b'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*5)
        cr.show_layout(layout)
        cr.set_source_rgb(*fem_col)
        layout.set_text("5/6  %s" % ascent_texts['a5'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*6)
        cr.show_layout(layout)
        layout.set_text("7/8  %s" % ascent_texts['a7'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*7)
        cr.show_layout(layout)

    def text_for_polar(self,cr,width,height):
        r = width/2*0.8
        v = r*0.077
        
        cr.set_source_rgb(1.0,1,0.8)
        cr.rectangle(-r*1.05,10.2*v*0.97,2*r*1.05,6*v)
        cr.fill()
        
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(9*pango.SCALE*r*3*MAGICK_FONTSCALE))
        layout.set_font_description(font)

        layout.set_text("6  %s" % polar_texts['P6'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,1.5*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("5 %s" % polar_texts['P5'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,1.5*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("14  %s" % polar_texts['P14'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,3*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("9  %s" % polar_texts['P9'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,4.5*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)

        layout.set_text("10  %s" % polar_texts['P10'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,4.5*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)

        layout.set_text("13  %s" % polar_texts['P13'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,6*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("4  %s" % polar_texts['P4'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,7.5*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("3  %s" % polar_texts['P3'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,9*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("12  %s" % polar_texts['P12'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,10.5*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("7  %s" % polar_texts['P7'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,12*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)
        
        layout.set_text("8  %s" % polar_texts['P8'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,12*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)

        layout.set_text("11  %s" % polar_texts['P11'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,13.5*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("2 %s" % polar_texts['P2'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,15*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)
        
        layout.set_text("1 %s" % polar_texts['P1'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,15*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)


    def polar_star(self,cr,width,height,chartob):
        cx,cy = width/2,height/2
        polar = polar_calc(chartob)
        she_col = (0.88,0.74,0.15) 
        he_col = (0.8,0.55,0.97) 

        if cx < cy:
            r =  max(cx,cy)*0.95 
        else: # cx > cy
            r =  min(cx,cy)*0.95 
        rx = r*0.456
        ry = r*1.9

        cr.save()
        cr.translate(0,-r*0.9)
        
        cr.set_source_rgb(0.9,0.89,0.94) 
        cr.rectangle(-rx,0,rx*2,ry*0.48)
        cr.fill()

        pat = cairo.LinearGradient(0,ry*0.48,0,ry*0.75)
        pat.add_color_stop_rgb(0,0.89,1,0.74)
        pat.add_color_stop_rgb(1,0.95,0.92,0.54)
        cr.set_source(pat)
        cr.rectangle(-rx,ry*0.48,rx*2,ry*0.27)
        cr.fill()

        cr.set_source_rgb(0.83,0.75,0.68) 
        cr.rectangle(-rx,ry*0.75,rx*2,ry*0.25)
        cr.fill()

        #### cells
        rcell = ry*0.09
        poscell = ry*0.48 - rcell*3
        for i in (0,2,4,6):
            cr.set_source_rgb(*she_col) 
            cr.rectangle(-rx,poscell+rcell*i,rcell,rcell)
            cr.fill()
            cr.set_source_rgb(*he_col) 
            cr.rectangle(rx-rcell,poscell+rcell*i,rcell,rcell)
            cr.fill()
        
        scl = 0.0057*r
        pls = (0,6,4,3)
        gen_col = [(0,0.25,1),(1,0,0)]
        poscell += rcell
        scls = [scl,scl,0.0065*r,0.0065*r] 
        offsets = [(scl/2.5,scl*0.06), (scl/1.5,scl*0.06),
                (scls[2]/1.5,scls[2]/10), (scls[2]/2,scls[2]/8)]
        for i,pl in enumerate(pls):
            col = gen_col[1]
            gen_col[0],gen_col[1] = gen_col[1],gen_col[0]
            cr.set_source_rgb(*col) 
            x_b,_,w,hh,_,y_b = self.plan[pl].extents
            cr.save()
            cr.translate(-rx+rcell/2-w*offsets[i][0],(poscell+rcell*i*2)-hh*offsets[i][1])
            cr.scale(scls[i],scls[i])
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
        pls = (6,0,3,4)
        offsets = [(scl/1.5,scl*0.06),(scl/2.5,scl*0.06),
                (scls[2]/2,scl/8),(scls[2]/1.5,scls[2]/10)]
        for i,pl in enumerate(pls):
            col = gen_col[0]
            gen_col[0],gen_col[1] = gen_col[1],gen_col[0]
            cr.set_source_rgb(*col) 
            x_b,_,w,hh,_,y_b = self.plan[pl].extents
            cr.save()
            cr.translate(rx-rcell/2-w*offsets[i][0],(poscell+rcell*i*2)-hh*offsets[i][1])
            cr.scale(scls[i],scls[i])
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()

        x_b,_,w,hh,_,y_b = self.plan[0].extents
        cr.save()
        cr.translate(-rx+rcell/2-w*scl/2.5,ry-hh*scl*0.1)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[0].paths)
        cr.fill()
        cr.restore()
        cr.set_source_rgb(*gen_col[0]) 
        x_b,_,w,hh,_,y_b = self.plan[6].extents
        cr.save()
        cr.translate(rx-rcell/2-w*scl/1.5,ry-hh*scl*0.06)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[6].paths)
        cr.fill()
        cr.restore()
        x_b,_,w,hh,_,y_b = self.plan[7].extents
        cr.save()
        cr.translate(-rx+rcell/2-w*scl/1.8,ry*0.13-hh*scl*0.06)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[7].paths)
        cr.fill()
        cr.restore()
        cr.set_source_rgb(*gen_col[1]) 
        x_b,_,w,hh,_,y_b = self.plan[9].extents
        cr.save()
        cr.translate(rx-rcell/2-w*scl/2.5,ry*0.13-hh*scl*0.06)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[9].paths)
        cr.fill()
        cr.restore()
        
        rr = rcell/2
        self.make_grad_pad(cr,0,ry*0.23,rr,-rcell*1.7,ry*0.23,
                rcell*1.7,ry*0.23 ,170,10,1)
        self.make_grad_pad(cr,0,ry*0.43,rr,-rcell*1.7,ry*0.43,
                rcell*1.7,ry*0.43 ,170,10,0)
        self.make_grad_pad(cr,0,ry*0.62,rr,-rcell*1.7,ry*0.62,
                rcell*1.7,ry*0.62 ,170,10,1)
        self.make_grad_pad(cr,0,ry*0.81,rr,-rcell*1.7,ry*0.81,
                rcell*1.7,ry*0.81 ,170,10,0)
        
        self.make_hexagon(cr,0,ry*0.23,rcell/2,'14',2,polar)
        self.make_hexagon(cr,0,ry*0.43,rcell/2,'13',2,polar)
        self.make_hexagon(cr,0,ry*0.62,rcell/2,'12',2,polar)
        self.make_hexagon(cr,0,ry*0.81,rcell/2,'11',2,polar)

        # left
        self.make_solid_pad(cr,-rcell*0.75,ry*0.14,rr,-rcell*1.8,ry*0.09,rcell*1.7,ry*0.23,140,-15,0,1)
        self.make_solid_pad(cr,-rcell*0.75,ry*0.31,rr,-rcell*1.7,ry*0.265,rcell*1.7,ry*0.43,140,-20,1,0)
        self.make_solid_pad(cr,-rcell*0.75,ry*0.53,rr,-rcell*2.1,ry*0.48,rcell*1.7,ry*0.62,146,-20,0,1)
        self.make_solid_pad(cr,-rcell*0.75,ry*0.70,rr,-rcell*1.7,ry*0.655,rcell*1.7,ry*0.81,140,-20,1,0)
        self.make_solid_pad(cr,-rcell*0.75,ry*0.89,rr,-rcell*1.7,ry*0.84,rcell*1.7,ry*0.985,140,-15,0,0) 

        self.make_hexagon(cr,-rcell*0.75,ry*0.14,rcell/2,'6',0,polar)
        self.make_hexagon(cr,-rcell*0.75,ry*0.31,rcell/2,'9',1,polar)
        self.make_hexagon(cr,-rcell*0.75,ry*0.53,rcell/2,'4',0,polar)
        self.make_hexagon(cr,-rcell*0.75,ry*0.70,rcell/2,'7',1,polar)
        self.make_hexagon(cr,-rcell*0.75,ry*0.89,rcell/2,'2',0,polar)
        #right
        self.make_solid_pad(cr,rcell*0.75,ry*0.14,rr,-rcell*1.8,ry*0.23,rcell*1.8,ry*0.09,195,35,1,1)
        self.make_solid_pad(cr,rcell*0.75,ry*0.31,rr,-rcell*1.7,ry*0.43,rcell*1.7,ry*0.265,200,35,0,0) #sat sat
        self.make_solid_pad(cr,rcell*0.75,ry*0.53,rr,-rcell*1.7,ry*0.62,rcell*2.1,ry*0.48,200,30,1,1)
        self.make_solid_pad(cr,rcell*0.75,ry*0.70,rr,-rcell*1.7,ry*0.81,rcell*1.7,ry*0.655,200,35,0,0)
        self.make_solid_pad(cr,rcell*0.75,ry*0.89,rr,-rcell*1.7,ry*0.985,rcell*1.7,ry*0.84,195,38,1,0) 

        self.make_hexagon(cr,rcell*0.75,ry*0.14,rcell/2,'5',0,polar)
        self.make_hexagon(cr,rcell*0.75,ry*0.31,rcell/2,'10',1,polar)
        self.make_hexagon(cr,rcell*0.75,ry*0.53,rcell/2,'3',0,polar)
        self.make_hexagon(cr,rcell*0.75,ry*0.70,rcell/2,'8',1,polar)
        self.make_hexagon(cr,rcell*0.75,ry*0.89,rcell/2,'1',0,polar)

        
        xtra = r*0.9-r
        pat = cairo.LinearGradient(-rx,0,0,0)
        pat.add_color_stop_rgb(0,0.88,0.74,0.15)
        pat.add_color_stop_rgb(1,1,1,1)
        cr.set_source(pat) 
        cr.rectangle(-rx,0,rx,xtra)
        cr.fill()
        cr.rectangle(-rx,-xtra*0.55,rx*0.28,xtra)
        cr.fill()
        cr.arc(-rx*0.72,-xtra*0.05,rx*0.11,0,180*PI)
        cr.fill()
        #he_col = (0.8,0.55,0.97) 

        pat = cairo.LinearGradient(0,0,rx,0)
        pat.add_color_stop_rgb(0,1,1,1)
        pat.add_color_stop_rgb(1,0.8,0.55,0.97)
        cr.set_source(pat) 
        cr.rectangle(0,0,rx,xtra)
        cr.fill()
        cr.rectangle(rx-rx*0.28,-xtra*0.55,rx*0.28,xtra)
        cr.fill()
        cr.arc(rx*0.72,-xtra*0.05,rx*0.11,0,180*PI)
        cr.fill()
        
        she_col = (0.58,0.44,0.15) 
        cr.set_source_rgb(*she_col) 
        cr.rectangle(-rx,xtra,rx*2,ry*1.053)
        cr.stroke()
        cr.restore()

    def make_grad_pad(self,cr,x,y,rr,x1,y1,x2,y2,a1,a2,g):
        v = [0,1]
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(v[g],0.83,0.82,0.96)
        pat.add_color_stop_rgb(v[(g+1)%2],0.98,0.8,0.83)
        cr.set_source(pat)
        cr.move_to(x1,y1)
        cr.arc(x,y,rr*1.07,-a1*RAD,-a2*RAD)
        cr.line_to(x2,y2)
        cr.arc(x,y,rr*1.05,(-a2+20)*RAD,(-a1-20)*RAD)
        cr.close_path()
        cr.fill()

    def make_solid_pad(self,cr,x,y,rr,x1,y1,x2,y2,a1,a2,c,o):
        v = [(0.81,0.82,0.94),(1,0.81,0.75)] #blue, pink
        off = [20,15]
        cr.set_source_rgb(*v[c])
        cr.move_to(x1,y1)
        cr.arc(x,y,rr*1.07,-a1*RAD,-a2*RAD)
        cr.line_to(x2,y2)
        cr.arc(x,y,rr*1.05,(-a2+off[o])*RAD,(-a1-off[o])*RAD)
        cr.close_path()
        cr.fill()

    def make_hexagon(self,cr,x,y,rr,n,c,polar):
        ncol = [(1,0,0),(0,0,1),(0,0.8,0) ]
        cr.set_source_rgb(0.95,0.93,0.77)
        cr.save()
        cr.translate(x,y)
        cr.move_to(rr,0)
        cr.line_to(rr*math.cos(60*RAD),rr*math.sin(60*RAD))
        cr.line_to(rr*math.cos(120*RAD),rr*math.sin(120*RAD))
        cr.line_to(-rr,0)
        cr.line_to(rr*math.cos(240*RAD),rr*math.sin(240*RAD))
        cr.line_to(rr*math.cos(300*RAD),rr*math.sin(300*RAD))
        cr.close_path()
        cr.fill_preserve()
        cr.set_source_rgb(0.4,0.3,0.4)
        cr.stroke()
        cr.save()
        cr.translate(0,-rr*0.9)
        cr.scale(0.35,0.35)
        cr.set_source_rgb(0.95,0.93,0.77)
        cr.move_to(rr,0)
        cr.line_to(rr*math.cos(60*RAD),rr*math.sin(60*RAD))
        cr.line_to(rr*math.cos(120*RAD),rr*math.sin(120*RAD))
        cr.line_to(-rr,0)
        cr.line_to(rr*math.cos(240*RAD),rr*math.sin(240*RAD))
        cr.line_to(rr*math.cos(300*RAD),rr*math.sin(300*RAD))
        cr.close_path()
        cr.fill_preserve()
        cr.set_source_rgb(0.4,0.3,0.4)
        cr.stroke()
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(28*pango.SCALE*rr*16*MAGICK_FONTSCALE))
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
        layout.set_text(n)
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,-h/2)
        cr.set_source_rgb(*ncol[c])
        cr.show_layout(layout)
        cr.restore()
        font = pango.FontDescription('Astro-Nex')
        font.set_size(int(36*pango.SCALE*rr/0.13*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        a = polar[n]
        if a > -1000:
            alet = asplet[a] 
            cr.set_source_rgb(*aspcolors[int(alet)-1])
            layout.set_text(alet)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(-w*0.5,-h/2)
            cr.layout_path(layout)
            cr.fill()
        cr.restore()


    def wundersensi_star(self,cr,width,height,chartob):
        cx,cy = width/2,height/2
        r = min(cx,cy)*0.95
        wunder, sensi = wunder_calc(chartob)

        ## eggs
        rr = r * 0.19
        re,g,b = she_col
        points = [(-r+rr,-r+r*0.65),(-r+rr*1.3,r-r*0.55),(-r+r*0.75,-r+rr),(-r+r*0.5,r-rr)]
        for p in points:
            cr.save()
            cr.translate(p[0],p[1])
            pat = cairo.RadialGradient(0,0,5,0,0,rr)
            pat.add_color_stop_rgba(0,re,g,b,0.2)
            pat.add_color_stop_rgba(1,re,g,b,1)
            cr.set_source(pat)
            cr.arc(0,0,rr,0,180*PI)
            cr.fill()
            cr.restore()

        self.swap_bmoon()
        scl = 0.010*r
        for pl,point in zip([1,5,8,2],points):
            col = self.plan[pl].col
            cr.set_source_rgb(*col) 
            x_b,_,w,hh,_,y_b = self.plan[pl].extents
            cr.save()
            if pl == 1: x_b = 9
            cr.translate(point[0]-scl*w/2-x_b*scl,point[1]+scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()

        self.swap_fmoon()
        re,g,b = he_col
        points = [(r-rr,-r+r*0.65),(r-rr*1.3,r-r*0.55),(r-r*0.75,-r+rr),(r-r*0.5,r-rr)]
        for p in points:
            cr.save()
            cr.translate(p[0],p[1])
            pat = cairo.RadialGradient(0,0,5,0,0,rr)
            pat.add_color_stop_rgba(0,re,g,b,0.2)
            pat.add_color_stop_rgba(1,re,g,b,1)
            cr.set_source(pat)
            cr.arc(0,0,rr,0,180*PI)
            cr.fill()
            cr.restore()

        for pl,point in zip([1,5,8,2],points):
            col = self.plan[pl].col
            cr.set_source_rgb(*col) 
            x_b,_,w,hh,_,y_b = self.plan[pl].extents
            cr.save()
            cr.translate(point[0]-scl*w/2,point[1]+scl*hh*0.5)
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[pl].paths)
            cr.fill()
            cr.restore()
        
        rr = r * 0.13
        wungrad_l = (0.73,0.65,1)
        wungrad_d = (0.4,0.25,0.95)

        pat = cairo.LinearGradient(0,rr*2.9,0,rr*2.1)
        re,g,b = wungrad_l
        pat.add_color_stop_rgb(0,re,g,b)
        pat.add_color_stop_rgb(1,re,g,b)
        re,g,b = wungrad_d
        pat.add_color_stop_rgb(0.5,re,g,b)
        cr.set_source(pat)
        cr.move_to(-r+rr*3.05,rr*2.6)                   # jj
        cr.line_to(0,rr*2.9)
        cr.line_to(r-rr*3.05,rr*2.6)
        cr.line_to(0,rr*2.1)
        cr.close_path()
        cr.fill()
        
        pat = cairo.LinearGradient(0,-rr*2.5,0,-rr*1.7)
        re,g,b = wungrad_l
        pat.add_color_stop_rgb(0,re,g,b)
        pat.add_color_stop_rgb(1,re,g,b)
        re,g,b = wungrad_d
        pat.add_color_stop_rgb(0.5,re,g,b)
        cr.set_source(pat)
        cr.move_to(-r+rr*2.75,-rr*2.1)               # ll
        cr.line_to(0,-rr*2.5)
        cr.line_to(r-rr*2.75,-rr*2.1)
        cr.line_to(0,-rr*1.7)
        cr.close_path()
        cr.fill()
        
        pat = cairo.LinearGradient(-rr*1.8,-rr*1.2,-rr*1.45,-rr*0.9)
        re,g,b = wungrad_l
        pat.add_color_stop_rgb(0,re,g,b)
        pat.add_color_stop_rgb(1,re,g,b)
        re,g,b = wungrad_d
        pat.add_color_stop_rgb(0.5,re,g,b)
        cr.set_source(pat)
        cr.move_to(-r+rr*3.05,rr*2.6)                   # jn
        cr.line_to(-rr*1.9,-rr*1.3)
        cr.line_to(rr*1.5,-rr*4.9)
        cr.line_to(-rr*1.3,-rr*0.75)
        cr.close_path()
        cr.fill()
        
        pat = cairo.LinearGradient(rr*1.8,-rr*1.2,rr*1.45,-rr*0.9)
        re,g,b = wungrad_l
        pat.add_color_stop_rgb(0,re,g,b)
        pat.add_color_stop_rgb(1,re,g,b)
        re,g,b = wungrad_d
        pat.add_color_stop_rgb(0.5,re,g,b)
        cr.set_source(pat)
        cr.move_to(r-rr*3.05,rr*2.6)                    # nj
        cr.line_to(rr*1.9,-rr*1.3)
        cr.line_to(-rr*1.5,-rr*4.9)
        cr.line_to(rr*1.3,-rr*0.75)
        cr.close_path()
        cr.fill()
        
        ### sen
        pat = cairo.LinearGradient(-rr*1.1,rr*0.35,-rr*0.7,rr*0.545)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(-rr*3.3,rr*5.0)                  # mn
        cr.line_to(-rr*1.5,rr*0.8)
        cr.line_to(rr*1.5,-rr*4.9)
        cr.line_to(-rr*0.5,rr*0.6)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(rr*1.1,rr*0.35,rr*0.7,rr*0.545)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(rr*3.3,rr*5.0)                   # nm
        cr.line_to(rr*1.5,rr*0.8)
        cr.line_to(-rr*1.5,-rr*4.9)
        cr.line_to(rr*0.5,rr*0.6)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(-rr*2.83,rr*1.4,-rr*2.6,rr*1.85)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(-r+rr*3.05,rr*2.6)                # jl
        cr.line_to(-r+rr*5.9,rr*0.49)
        cr.line_to(r-rr*2.75,-rr*2.1)
        cr.line_to(-r+rr*5.4,rr*2)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(rr*2.83,rr*1.4,rr*2.6,rr*1.85)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(-r+rr*2.75,-rr*2.1)               # lj
        cr.line_to(r-rr*5.9,rr*0.49)
        cr.line_to(r-rr*3.05,rr*2.6) 
        cr.line_to(r-rr*5.4,rr*2)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(-rr*3.05,-rr*0.65,-rr*3.48,-rr*0.1)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(-r+rr*2.75,-rr*2.1)               # lm
        cr.line_to(-r+rr*4.9,-rr*0.49)
        cr.line_to(rr*3.3,rr*5.0) 
        cr.line_to(-r+rr*3.9,-rr*0.42)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(rr*3.05,-rr*0.65,rr*3.48,-rr*0.1)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(-rr*3.3,rr*5.0)                  # ml
        cr.line_to(r-rr*4.9,-rr*0.49)
        cr.line_to(r-rr*2.75,-rr*2.1)           
        cr.line_to(r-rr*3.9,-rr*0.42)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(-rr*1.35,rr*3.5,-rr*1.5,rr*4.0)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(-r+rr*3.05,rr*2.6)                # jm
        cr.line_to(-rr*1.5,rr*3.3)
        cr.line_to(rr*3.3,rr*5.0)
        cr.line_to(-rr*1.6,rr*4.1)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(rr*1.35,rr*3.5,rr*1.5,rr*4.0)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(r-rr*3.05,rr*2.6)                 # mj
        cr.line_to(rr*1.5,rr*3.3)
        cr.line_to(-rr*3.3,rr*5.0)
        cr.line_to(rr*1.6,rr*4.1)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(0,rr*6.2,0,rr*6.6)
        re,g,b = wunsen_cols['sen'][3]
        pat.add_color_stop_rgb(0,0.5,0.85,0.6)
        pat.add_color_stop_rgb(0.5,re,g,b)
        pat.add_color_stop_rgb(1,0.5,0.85,0.6)
        cr.set_source(pat)
        cr.move_to(-r+rr*5.25,rr*6.4)             # mm
        cr.line_to(0,rr*6.1)
        cr.line_to(r-rr*5.25,rr*6.4)
        cr.line_to(0,rr*6.7)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(-rr*1.7,-rr*3.6,-rr*1.48,-rr*3.1)
        re,g,b = wungrad_l
        pat.add_color_stop_rgb(0,re,g,b)
        pat.add_color_stop_rgb(1,re,g,b)
        re,g,b = wungrad_d
        pat.add_color_stop_rgb(0.5,re,g,b)
        cr.set_source(pat)
        cr.move_to(-r+rr*2.75,-rr*2.1)               # ln
        cr.line_to(-rr*2,-rr*3.7)
        cr.line_to(rr*1.5,-rr*4.9)
        cr.line_to(-rr*1.5,-rr*3)
        cr.close_path()
        cr.fill()
        pat = cairo.LinearGradient(rr*1.7,-rr*3.6,rr*1.48,-rr*3.1)
        re,g,b = wungrad_l
        pat.add_color_stop_rgb(0,re,g,b)
        pat.add_color_stop_rgb(1,re,g,b)
        re,g,b = wungrad_d
        pat.add_color_stop_rgb(0.5,re,g,b)
        cr.set_source(pat)
        cr.move_to(r-rr*2.75,-rr*2.1)
        cr.line_to(rr*2,-rr*3.7)
        cr.line_to(-rr*1.5,-rr*4.9)
        cr.line_to(rr*1.5,-rr*3)
        cr.close_path()
        cr.fill()
        
        self.make_octogon(cr,0,-rr*2.0,rr,'wun','1',wunder['1']) 
        self.make_octogon(cr,-rr*1.4,-rr*3.5,rr,'wun','2',wunder['2a']) 
        self.make_octogon(cr,rr*1.4,-rr*3.5,rr,'wun','2',wunder['2b']) 
        self.make_octogon(cr,-rr*1.7,-rr*1.2,rr,'wun','3',wunder['3a'])
        self.make_octogon(cr,rr*1.7,-rr*1.2,rr,'wun','3',wunder['3b'])
        self.make_octogon(cr,0,rr*2.45,rr,'wun','4',wunder['4'])
        
        self.make_octogon(cr,-rr,rr*0.75,rr,'sen','1',sensi['1a'])
        self.make_octogon(cr,rr,rr*0.75,rr,'sen','1',sensi['1b']) 
        self.make_octogon(cr,-rr*3.45,-rr*0.40,rr,'sen','2',sensi['2a'])
        self.make_octogon(cr,rr*3.45,-rr*0.40,rr,'sen','2',sensi['2b'])
        self.make_octogon(cr,-rr*2.7,rr*1.7,rr,'sen','3',sensi['3b'])
        self.make_octogon(cr,rr*2.7,rr*1.7,rr,'sen','3',sensi['3a'])
        self.make_octogon(cr,-rr*1.4,rr*3.8,rr,'sen','4',sensi['4a'])
        self.make_octogon(cr,rr*1.4,rr*3.8,rr,'sen','4',sensi['4b'])
        self.make_octogon(cr,0,rr*6.4,rr,'sen','5',sensi['5'])

    def make_octogon(self,cr,x,y,rr,wscol,n,a):
        cr.set_source_rgb(*wunsen_cols[wscol][0])
        cr.save()
        cr.translate(x,y)
        cr.move_to(0,-rr)
        cr.line_to(rr*math.cos(225*RAD),rr*math.sin(225*RAD))
        cr.line_to(-rr,0)
        cr.line_to(rr*math.cos(135*RAD),rr*math.sin(135*RAD))
        cr.line_to(0,rr)
        cr.line_to(rr*math.cos(45*RAD),rr*math.sin(45*RAD))
        cr.line_to(rr,0)
        cr.line_to(rr*math.cos(-45*RAD),rr*math.sin(-45*RAD))
        cr.close_path()
        cr.fill()
        cr.scale(0.97,0.97)
        pat = cairo.LinearGradient(rr*math.cos(225*RAD),rr*math.sin(225*RAD),
                rr*math.cos(45*RAD),rr*math.sin(45*RAD))
        r1,g1,b1 = wunsen_cols[wscol][2]
        pat.add_color_stop_rgb(0,r1,g1,b1)
        r1,g1,b1 = wunsen_cols[wscol][3]
        pat.add_color_stop_rgb(1,r1,g1,b1)
        cr.set_source(pat)
        cr.move_to(0,-rr)
        cr.line_to(rr*math.cos(225*RAD),rr*math.sin(225*RAD))
        cr.line_to(-rr,0)
        cr.line_to(rr*math.cos(135*RAD),rr*math.sin(135*RAD))
        cr.line_to(0,rr)
        cr.line_to(rr*math.cos(45*RAD),rr*math.sin(45*RAD))
        cr.line_to(rr,0)
        cr.line_to(rr*math.cos(-45*RAD),rr*math.sin(-45*RAD))
        cr.close_path()
        cr.fill()
        cr.scale(0.93,0.93)
        cr.set_source_rgb(*wunsen_cols[wscol][1])
        cr.move_to(0,-rr)
        cr.line_to(rr*math.cos(225*RAD),rr*math.sin(225*RAD))
        cr.line_to(-rr,0)
        cr.line_to(rr*math.cos(135*RAD),rr*math.sin(135*RAD))
        cr.line_to(0,rr)
        cr.line_to(rr*math.cos(45*RAD),rr*math.sin(45*RAD))
        cr.line_to(rr,0)
        cr.line_to(rr*math.cos(-45*RAD),rr*math.sin(-45*RAD))
        cr.close_path()
        cr.fill()
        cr.set_line_width(0.5)
        cr.arc(0,-rr*0.9,rr*0.2,0,180*PI)
        cr.set_source_rgb(*wunsen_cols[wscol][1])
        cr.fill_preserve()
        cr.set_source_rgb(*wunsen_cols[wscol][0])
        cr.stroke()
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(12*pango.SCALE*rr/0.13*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        layout.set_text(n)
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(0-w/1.9,-rr-h/4)
        cr.show_layout(layout)
        font = pango.FontDescription('Astro-Nex')
        font.set_size(int(36*pango.SCALE*rr/0.13*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        if a > -1000:
            alet = asplet[a] 
            cr.set_source_rgb(*aspcolors[int(alet)-1])
            layout.set_text(alet)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(-w*0.5,-h/2)
            cr.layout_path(layout)
            cr.fill()
        cr.restore()


    def ascent_star(self,cr,width,height,chartobj):
        cx,cy = width/2,height/2
        r = min(cx,cy)*0.75
        asc_1 = chartobj.chart.houses[0]
        asc_2 = chartobj.click.houses[0]
        nod_1 = chartobj.chart.planets[10]
        nod_2 = chartobj.click.planets[10]
        aspects = ascent_calc(asc_1, asc_2, nod_1, nod_2)

        c1 = 0.25*(math.sqrt(5) - 1)
        c2 = 0.25*(math.sqrt(5) + 1)
        s1 = 0.25*math.sqrt(10+2*math.sqrt(5))
        s2 = 0.25*math.sqrt(10-2*math.sqrt(5))

        ## eggs
        cr.save()
        cr.set_source_rgb(0.82,0.69,1) # aries col
        cr.scale(1,0.75)
        cr.arc(0,-r*1.52,0.2*r,0,180*PI)
        cr.fill()
        cr.restore()
        cr.set_source_rgb(1,0,0.42) #arsym_col
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(36*pango.SCALE*r*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        layout.set_text(u"0\u00b0")
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        cr.move_to(0-w/2, -r*1.25)
        cr.show_layout(layout)
        
        s = self.zod[0].let
        cr.save()
        cr.set_source_rgb(1,0,0.42) #arsym_col
        x_b,_,width,height,_,_ = self.zod[0].extents
        scl = 0.003*r
        cr.translate(scl*(-width/2-x_b),-r*1.03)
        cr.scale(scl,scl)
        self.warpPath(cr,self.zod[0].paths)
        cr.fill()
        cr.restore()
        
        cr.save()
        cr.scale(1,0.95)
        cr.set_source_rgba(*(list(she_col)+[0.4]))
        cr.arc(-s1*r*1.15,-c1*r,0.16*r,0,180*PI)
        cr.fill()
        cr.set_source_rgba(*(list(he_col)+[0.4]))
        cr.arc(s1*r*1.15,-c1*r,0.16*r,0,180*PI)
        cr.fill()
        cr.restore()
        
        cr.save()
        cr.scale(1,0.89)
        cr.set_source_rgba(*(list(she_col)+[0.4]))
        cr.arc(-s2*r*1.3,c2*r*1.2,0.2*r,0,180*PI)
        cr.fill()
        cr.set_source_rgba(*(list(he_col)+[0.4]))
        cr.arc(s2*r*1.3,c2*r*1.2,0.2*r,0,180*PI)
        cr.fill()
        cr.restore()
        
        scl = 0.012*r
        x_b,_,w,hh,_,y_b = self.plan[10].extents
        
        cr.set_source_rgb(*she_col) 
        cr.save()
        cr.translate(-s2*r*1.3-scl*w/2.2,c2*r*1.19)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[10].paths)
        cr.fill()
        cr.restore()
        
        cr.set_source_rgb(*he_col) 
        cr.save()
        cr.translate(s2*r*1.3-scl*w/2.2,c2*r*1.19)
        cr.scale(scl,scl)
        self.warpPath(cr,self.plan[10].paths)
        cr.fill()
        cr.restore()

        acpaths = boss.acpaths
        scl = 0.0028*r
        warpPath(cr,acpaths['A'].split('\n'))
        _,_,right,_ = cr.fill_extents()
        cr.new_path()
        x,y = (-s1*r*1.28,-c1*r*0.75)
        cr.set_source_rgb(*she_col) 
        for i,s in enumerate(['A','C']):
            cr.save()
            off = i * right
            cr.translate(x+scl*off,y) 
            cr.scale(scl,scl)
            warpPath(cr,acpaths[s].split('\n'))
            cr.fill()
            cr.restore()
            
        x,y = (s1*r*1.02,-c1*r*0.75)
        cr.set_source_rgb(*he_col) 
        for i,s in enumerate(['A','C']):
            cr.save()
            off = i * right
            cr.translate(x+scl*off,y) 
            cr.scale(scl,scl)
            warpPath(cr,acpaths[s].split('\n'))
            cr.fill()
            cr.restore()
        
        ## zod
        cr.set_line_width(0.5)
        for i in range(0,12):
            off = 30*i
            ix = 8-i
            s = self.zod[ix].let
            col = self.zod[ix].col
            cr.save()
            cr.set_source_rgb(*col) 
            cr.rotate((off+15)*RAD)
            x_b,_,width,height,_,_ = self.zod[ix].extents
            scl = 0.0011*r
            cr.translate(scl*(-width/2-x_b),-r*0.24)
            cr.scale(scl,scl)
            self.warpPath(cr,self.zod[ix].paths)
            cr.fill()
            cr.restore()
            cr.set_source_rgb(0,0,0) 
            cr.move_to(r*0.235*math.cos(off*RAD),r*0.235*math.sin(off*RAD))
            cr.line_to(r*0.3*math.cos(off*RAD),r*0.3*math.sin(off*RAD))
            cr.stroke() 

        cr.set_source_rgb(0,0,0)
        cr.arc(0,0,r*0.23,0,180*PI)
        cr.stroke() 
        cr.arc(0,0,r*0.3,0,180*PI)
        cr.stroke() 
        
        ## gradients
        rr = r*0.165 # 117
        
        x1 = rr; y1 = rr*1.6; x2 = rr*2.3; y2 = rr*2.9         #4
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(s1*r,-c1*r)
        cr.line_to(rr,rr*1.6)
        cr.line_to(rr*2.15,rr*3)
        cr.close_path()
        cr.fill()
        x1 =  rr; y1 = rr*1.6; x2 = rr*1.8; y2 = rr*3.2
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(-s2*r,c2*r)
        cr.line_to(rr,rr*1.6) 
        cr.line_to(rr*2.15,rr*3)
        cr.close_path()
        cr.fill()
        
        cr.set_source_rgb(1,0.18,0.21) 
        x1 = -rr; y1 = rr*1.6; x2 = -rr*2.3; y2 = rr*2.9         # 3
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(-s1*r,-c1*r)         
        cr.line_to(-rr,rr*1.6)
        cr.line_to(-rr*2.15,rr*3)
        cr.close_path()
        cr.fill()
        x1 =  -rr; y1 = rr*1.6; x2 = -rr*1.8; y2 = rr*3.2
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(s2*r,c2*r)
        cr.line_to(-rr,rr*1.6)     
        cr.line_to(-rr*2.15,rr*3)
        cr.close_path()
        cr.fill()
        
        #cr.set_source_rgb(1,0,0) 
        #cr.arc(x1,y1,15,0,180*PI)
        #cr.fill()
        #cr.arc(x2,y2,15,0,180*PI)
        #cr.fill()
        
        x1 = -rr*1.8; y1 = -rr*0.5; x2 = -rr*3.3; y2 = -rr*1.25     # 5
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(0,-r)
        cr.line_to(-rr*3.5,-rr*1.15)
        cr.line_to(-rr*1.8,-rr*0.5)
        cr.close_path()
        cr.fill()
        x1 = -rr*1.8; y1 = -rr*0.5; x2 = -rr*3.35; y2 = -rr*0.8
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(-s2*r,c2*r)          # 5
        cr.line_to(-rr*3.5,-rr*1.15)
        cr.line_to(-rr*1.8,-rr*0.5)
        cr.close_path()
        cr.fill()
        
        x1 = rr*1.8; y1 = -rr*0.5; x2 = rr*3.3; y2 = -rr*1.25     # 6
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(0,-r)             
        cr.line_to(rr*3.5,-rr*1.15)
        cr.line_to(rr*1.8,-rr*0.5)
        cr.close_path()
        cr.fill()
        x1 = rr*1.8; y1 = -rr*0.5; x2 = rr*3.35; y2 = -rr*0.8
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(s2*r,c2*r)
        cr.line_to(rr*3.5,-rr*1.15)
        cr.line_to(rr*1.8,-rr*0.5)
        cr.close_path()
        cr.fill()
        

        x1 = -rr*3.5; y1 = -rr*5; x2 = -rr*2.5; y2 = -rr*3.4     # 7
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(0,-r)            
        cr.line_to(-rr*2.3,-rr*3.5)
        cr.line_to(-rr*2.9,-rr*5.28) 
        cr.close_path()
        cr.fill()
        x1 = -rr*3.3; y1 = -rr*5; x2 = -rr*2.2; y2 = -rr*3.6    
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(-s1*r,-c1*r)
        cr.line_to(-rr*2.3,-rr*3.5)
        cr.line_to(-rr*3.85,-rr*4.59)
        cr.close_path()
        cr.fill()
        
        x1 = rr*3.5; y1 = -rr*5; x2 = rr*2.5; y2 = -rr*3.4     # 8
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(0,-r)           
        cr.line_to(rr*2.3,-rr*3.5)
        cr.line_to(rr*2.9,-rr*5.28) 
        cr.close_path()
        cr.fill()
        x1 = rr*3.3; y1 = -rr*5; x2 = rr*2.2; y2 = -rr*3.6    
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,0,0,1)
        pat.add_color_stop_rgb(0.5,0.85,0.85,1)
        pat.add_color_stop_rgb(1,0,0,1)
        cr.set_source(pat)
        cr.move_to(s1*r,-c1*r)
        cr.line_to(rr*2.3,-rr*3.5)
        cr.line_to(rr*3.85,-rr*4.59)
        cr.close_path()
        cr.fill()
       
        ## 1
        x1 = -7; y1 = -c1*r*1.65; x2 = 0; y2 = -c1*r
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(-s1*r,-c1*r)
        cr.line_to(0,-c1*r)
        cr.line_to(-rr,-rr*3)
        cr.close_path()
        cr.fill()
        x1 = 7; y1 = -c1*r*1.65; x2 = 0; y2 = -c1*r
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(s1*r,-c1*r)
        cr.line_to(0,-c1*r)
        cr.line_to(rr,-rr*3)
        cr.close_path()
        cr.fill()
        
        ## 2
        x1 = -s2*r*1.01; y1 = c2*r*1.15; x2 = -s2*r*0.98; y2 = c2*r*0.85
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(-s2*r,c2*r)
        cr.line_to(0,rr*4.15)
        cr.line_to(-rr*0.6,rr*5.95)
        cr.close_path()
        cr.fill()
        x2 = s2*r*1.01; y2 = c2*r*1.15; x1 = s2*r*0.98; y1 = c2*r*0.85
        pat = cairo.LinearGradient(x1,y1,x2,y2)
        pat.add_color_stop_rgb(0,1,0.18,0.21)
        pat.add_color_stop_rgb(0.5,1,0.85,0.85)
        pat.add_color_stop_rgb(1,1,0.18,0.21)
        cr.set_source(pat)
        cr.move_to(s2*r,c2*r)
        cr.line_to(0,rr*4.15)
        cr.line_to(rr*0.6,rr*5.95)
        cr.close_path()
        cr.fill()

        ## pentagons
        layout = cr.create_layout()
        
        rrr = rr * 0.95
        redpent = { '2': (0,c2*r*1.05), '1': (0,-c1*r-rr*0.8),
                '3': (-s2*r*0.44,c2*r*0.44), '4': (s2*r*0.44,c2*r*0.44) }
        for k,pos in redpent.iteritems():
            cr.save()
            font = pango.FontDescription(boss.opts.font)
            font.set_size(int(22*pango.SCALE*r*MAGICK_FONTSCALE))
            layout.set_font_description(font)
            cr.translate(*pos)
            pat = cairo.LinearGradient(-s1*rr,-c1*rr,s2*rr,c2*rr)
            pat.add_color_stop_rgb(0,0.4,0,0)
            pat.add_color_stop_rgb(1,0.8,0.4,0.4)
            cr.set_source(pat)
            cr.move_to(0,-rr)
            cr.line_to(-s1*rr,-c1*rr)
            cr.line_to(-s2*rr,c2*rr)
            cr.line_to(s2*rr,c2*rr)
            cr.line_to(s1*rr,-c1*rr)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(1,0.76,0.76)
            cr.move_to(0,-rrr)
            cr.line_to(-s1*rrr,-c1*rrr)
            cr.line_to(-s2*rrr,c2*rrr)
            cr.line_to(s2*rrr,c2*rrr)
            cr.line_to(s1*rrr,-c1*rrr)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(1,0,0)
            layout.set_text("%s" % k)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(0-w/1.8, -rrr+h/5)
            cr.show_layout(layout)
            font = pango.FontDescription('Astro-Nex')
            font.set_size(int(48*pango.SCALE*r*MAGICK_FONTSCALE))
            layout.set_font_description(font)
            asp = aspects[int(k)-1]
            if asp > -1:
                alet = asplet[asp] 
                cr.set_source_rgb(*aspcolors[int(alet)-1])
                layout.set_text(alet)
                ink,logical = layout.get_extents()
                w = logical[2]/pango.SCALE
                h = logical[3]/pango.SCALE
                cr.move_to(-w*0.5,-h/2)
                cr.layout_path(layout)
                cr.fill()
            cr.restore()

        bluepent = { '7': (-s1*r*0.5,-c1*r*2.3), '8': (s1*r*0.5,-c1*r*2.3),
                '5': (-s2*r*0.715,-rr*0.85), '6': (s2*r*0.714,-rr*0.85) }
        for k,pos in bluepent.iteritems():
            cr.save()
            font = pango.FontDescription(boss.opts.font)
            font.set_size(int(22*pango.SCALE*r*MAGICK_FONTSCALE))
            layout.set_font_description(font)
            cr.translate(*pos)
            pat = cairo.LinearGradient(-s1*rr,-c1*rr,s2*rr,c2*rr)
            pat.add_color_stop_rgb(0,0,0,0.4)
            pat.add_color_stop_rgb(1,0.4,0.4,0.8)
            cr.set_source(pat)
            cr.move_to(0,-rr)
            cr.line_to(-s1*rr,-c1*rr)
            cr.line_to(-s2*rr,c2*rr)
            cr.line_to(s2*rr,c2*rr)
            cr.line_to(s1*rr,-c1*rr)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(0.82,0.82,1)
            cr.move_to(0,-rrr)
            cr.line_to(-s1*rrr,-c1*rrr)
            cr.line_to(-s2*rrr,c2*rrr)
            cr.line_to(s2*rrr,c2*rrr)
            cr.line_to(s1*rrr,-c1*rrr)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(0,0,1)
            layout.set_text("%s" % k)
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            h = logical[3]/pango.SCALE
            cr.move_to(0-w/1.8, -rrr+h/5)
            cr.show_layout(layout)
            font = pango.FontDescription('Astro-Nex')
            font.set_size(int(48*pango.SCALE*r*MAGICK_FONTSCALE))
            layout.set_font_description(font)
            asp = aspects[int(k)-1]
            if asp > -1:
                alet = asplet[asp] 
                cr.set_source_rgb(*aspcolors[int(alet)-1])
                layout.set_text(alet)
                ink,logical = layout.get_extents()
                w = logical[2]/pango.SCALE
                h = logical[3]/pango.SCALE
                cr.move_to(-w*0.5,-h/2)
                cr.layout_path(layout)
                cr.fill()
            cr.restore()

    def comp_pe(self,cr,width,height,chartob,texts=True):
        female = chartob.chart.first
        if chartob.chart.last:
            female += " "+ chartob.chart.last
        male = chartob.click.first
        if chartob.click.last:
            male += " "+ chartob.click.last
        dates = boss.search_couple(female,male)

        she_h_plan = chartob.chart.house_plan_long()
        she_h_plan = [she_h_plan[0],she_h_plan[1],she_h_plan[6]]
        he_h_plan = chartob.click.house_plan_long()
        he_h_plan = [he_h_plan[0],he_h_plan[1],he_h_plan[6]]

        she_r_plan = chartob.chart.planets[:]
        she_r_plan = [she_r_plan[0],she_r_plan[1],she_r_plan[6]]
        he_r_plan = chartob.click.planets[:]
        he_r_plan = [he_r_plan[0],he_r_plan[1],he_r_plan[6]]
        
        she_h_plan = [ (x % 30,i,she_col) for x,i in zip(she_h_plan,[0,1,6]) ]
        he_h_plan = [ (x % 30,i,he_col) for x,i in zip(he_h_plan,[0,1,6]) ]
        h_plan = sorted(she_h_plan + he_h_plan)
        she_r_plan = sorted([(x % 30,ix) for x,ix in zip(she_r_plan,[0,1,6])])
        he_r_plan = sorted([(x % 30,ix) for x,ix in zip(he_r_plan,[0,1,6])])
        
        side = min(width,height)
        cr.save()
        cr.translate((width-side)/2,(height-side)/2)
        w = side
        h = side
        loff = roff = w*0.075
        hs = w*0.85
        voff = h*0.1
        vs = h*0.5
        vzones = vs*0.35
        vs1 = vs*0.12
        vs2 = vs*0.09*2
        vr = vs*0.05
        fem_col = (0.92,0.85,0.54)
        male_col = (0.9,0.61,1)
        cr.set_source_rgb(*she_col)
        cr.rectangle(loff,voff+vzones,hs,vs-vzones)
        cr.stroke()

        cr.set_source_rgb(*male_col)
        cr.rectangle(loff,voff+vzones,hs,vs1)
        cr.fill()
        cr.set_source_rgb(*fem_col)
        cr.rectangle(loff,voff+vzones+vs1,hs,vs1)
        cr.fill()
        
        cr.save()
        cr.set_line_cap(cairo.LINE_CAP_SQUARE)
        
        self.make_srule(cr,loff,voff+vzones+vs1*2,hs,vr)
        self.make_finerule(cr,loff,voff+vzones,hs)
        self.make_finerule(cr,loff,voff+vzones+vs1,hs)

        cr.set_source_rgb(*male_col)
        cr.rectangle(loff,voff+vzones+vs1*2+vr,hs,vs2)
        cr.fill()
        cr.set_source_rgb(*fem_col)
        cr.rectangle(loff,voff+vzones+vs1*2+vr+vs2,hs,vs2)
        cr.fill()
        
        self.make_finerule(cr,loff,voff+vzones+vs1*2+vr+vs2/2,hs)
        self.make_finerule(cr,loff,voff+vzones+vs1*2+vr+vs2,hs)
        self.make_finerule(cr,loff,voff+vzones+vs1*2+vr+vs2*1.5,hs)
        self.make_finerule(cr,loff,voff+vzones+vs1*2+vr+vs2*2,hs)
       
        cr.set_source_rgb(0.7,0.7,0.7)
        step = hs/33.0
        sf = step*0.618
        si = step - sf
        cusp = loff+si+step*12
        wi = hs/200
        cr.rectangle(cusp-wi/2,voff*1.2,wi,vzones*0.85)
        cr.fill()
        cr.set_line_width(step/6)
        cr.move_to(loff+step,voff+vzones*0.965)
        cr.curve_to(loff+step*4,voff*2.7,cusp-step*2,voff*2.2, cusp,voff*1.2)
        cr.curve_to(cusp+step*4,voff*2,cusp+step*12,voff*2.7,loff+step*31-sf,voff+vzones*0.965)
        cr.stroke()
        cr.set_line_width(step/10)
        cr.move_to(cusp+si+step*11,voff*2.3)
        cr.line_to(cusp+si+step*11,voff+vzones*0.94)
        cr.stroke()
        cr.move_to(loff+step,voff+vzones*0.965)
        cr.line_to(loff+step,voff+vzones*0.93)
        cr.stroke()
        cr.move_to(loff+step*31-sf,voff+vzones*0.965)
        cr.line_to(loff+step*31-sf,voff+vzones*0.93)
        cr.stroke()
        cr.restore()
        
        cr.set_line_width(step/15)
        self.swap_bmoon()
        cr.set_source_rgb(0.3,0.3,0.3) 
        scl = 0.003*side*0.5
        sparse = sparse_plans(he_r_plan)
        sparse.reverse()
        for pl in he_r_plan:
            pos = pl[0]; i =pl[1]
            x_b,_,ww,hh,_,y_b = self.plan[i].extents
            cr.save()
            if pos < 20.0:
                pos = cusp+step*pos
            else:
                pos = loff+si+step*2+step*(pos-20.0)
            cr.move_to(pos,voff+vzones+vs1*0.93)
            cr.line_to(pos,voff+vzones+vs1*1.1)
            cr.stroke()
            pos += sparse.pop()*step
            cr.translate(pos-scl*ww/2,(voff+vzones+vs1)-scl*hh/4) 
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[i].paths)
            cr.fill()
            cr.restore()
        sparse = sparse_plans(she_r_plan)
        sparse.reverse()
        for pl in she_r_plan:
            pos = pl[0]; i =pl[1]
            x_b,_,ww,hh,_,y_b = self.plan[i].extents
            cr.save()
            if pos < 20.0:
                pos = cusp+step*pos
            else:
                pos = loff+si+step*2+step*(pos-20.0)
            cr.move_to(pos,voff+vzones+vs2*1.3)
            cr.line_to(pos,voff+vzones+vs2*1.4)
            cr.stroke()
            pos += sparse.pop()*step
            cr.translate(pos-scl*ww/2,(voff+vzones+vs2)+scl*hh/2) 
            cr.scale(scl,scl)
            self.warpPath(cr,self.plan[i].paths)
            cr.fill()
            cr.restore()
        jail = sparse_curve(h_plan)
        for cell in jail:
            corr = step*0.65
            numplan = len(cell)
            for i,pl in enumerate(cell):
                pos = pl[0]; ix =pl[1]
                cr.set_source_rgb(*pl[2]) 
                x_b,_,ww,hh,_,y_b = self.plan[ix].extents
                cr.save()
                if pos < 19.0:
                    fac = pos*0.045*0.9
                    pos = cusp+step*pos
                else:
                    fac = (29-pos)*0.08
                    pos = loff+si+step*2+step*(pos-20.0)
                cr.move_to(pos,voff+vzones*0.97)
                cr.line_to(pos,voff+vzones*1.03)
                cr.stroke()
                if numplan == 2:
                    pos += corr
                    corr = -corr
                elif numplan > 2:
                    faraway = i - (numplan // 2)
                    pos += faraway*abs(corr)
                cr.translate(pos-scl*ww/2,(voff+vzones*fac)+scl*hh/2) 
                cr.scale(scl,scl)
                self.warpPath(cr,self.plan[ix].paths)
                cr.fill()
                cr.restore()
            
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(24*pango.SCALE*step*22*MAGICK_FONTSCALE))
        font.set_weight(pango.WEIGHT_BOLD)
        layout.set_font_description(font)
    
        if not dates:
            self.swap_fmoon()
            return
        
        for i,d in enumerate(dates):
            dt = [ int(x) for x in d[0].split("/") ]
            dt = datetime.date(dt[2],dt[1],dt[0])
            #birthdt1 = strdate_to_date(chartob.chart.date).date()
            #birthdt2 = strdate_to_date(chartob.click.date).date()
            #dt721 = datetime.date(birthdt1.year+72,birthdt1.month,birthdt1.day)
            #dt722 = datetime.date(birthdt2.year+72,birthdt2.month,birthdt2.day)
            #lifedelta1 = dt721 - birthdt1 
            #lifedelta2 = dt722 - birthdt2 
            #nowdelta1 = dt - birthdt1 
            #nowdelta2 = dt - birthdt2
            #frac1 = nowdelta1.days / (lifedelta1.days*1.0)
            #frac2 = nowdelta2.days / (lifedelta2.days*1.0)
            #circle1 = 360 * frac1 
            #circle2 = 360 * frac2 
            dt = datetime.datetime.combine(dt,datetime.time())		
            deg1 = chartob.chart.which_degree_today_simple(dt)
            deg2 = chartob.click.which_degree_today_simple(dt)
            degree1 = deg1 % 30
            degree2 = deg2 % 30
            ndeg1 = chartob.chart.which_degree_today_simple(dt,kind='nodal')
            ndeg2 = chartob.click.which_degree_today_simple(dt,kind='nodal')
            ndegree1 = ndeg1 % 30
            ndegree2 = ndeg2 % 30
            #ndegree1 = chartob.chart.planets[10] - deg1
            #if ndegree1 < 0: ndegree1 += 360
            #ndegree2 = chartob.click.planets[10] - deg2
            #if ndegree2 < 0: ndegree2 += 360
            #ndegree1 %= 30
            #ndegree2 %= 30
            #print dt, degree1, degree2, ndegree1, ndegree2
            
            if i == 0:
                rplan1 = chartob.chart.planets[:] 
                rplan2 = chartob.click.planets[:]
                
                moddeg1 = deg1 % 30
                modplan1 = [ p % 30 for p  in rplan1 ]
                diffp1 = []
                for p in modplan1:
                    diff = p - moddeg1
                    if diff < 0 and abs(diff) > 15 : 
                        diff += 30
                    diffp1.append(diff)
                cs1 = [30.0,-1]; ci1 = [-30.0,-1]
                for j,d in enumerate(diffp1):
                    if d > 0 and d < cs1[0]:
                        cs1[0] = d; cs1[1] = j
                    elif d < 0 and d > ci1[0]:
                        ci1[0] = d; ci1[1] = j
                ci1[0] =  abs(ci1[0]) 
                p1 = -1
                pp = min(cs1,ci1)
                if pp[0] <= 3.0: 
                    p1 = pp[1]
                else:
                    p1 = (ci1[1],cs1[1])
                
                moddeg2 = deg2 % 30
                modplan2= [ p % 30 for p  in rplan2 ]
                diffp2 = []
                for p in modplan2:
                    diff = p - moddeg2
                    if diff < 0 and abs(diff) > 15 : 
                        diff += 30
                    diffp2.append(diff)
                cs2 = [30.0,-1]; ci2 = [-30.0,-1]
                #print rplan2, diffp2
                for j,d in enumerate(diffp2):
                    if d > 0 and d < cs2[0]:
                        cs2[0] = d; cs2[1] = j
                    elif d < 0 and d > ci2[0]:
                        ci2[0] = d; ci2[1] = j
                ci2[0] =  abs(ci2[0]) 
                p2 = -1
                pp = min(cs2,ci2)
                if pp[0] <= 3.0: 
                    p2 = pp[1]
                else:
                    p2 = (ci2[1],cs2[1])
                
                #dif1 = []; dif2 = []
                #cs1 = [180.0,-1]; ci1 = [-180.0,-1]
                #cs2 = [180.0,-1]; ci2 = [-180.0,-1]
                #p1 = -1; p2 = -1
                #for p in rplan1:
                #    dif = p - deg1
                #    if dif < 0 and abs(dif) >= 180  : dif += 360
                #    dif1.append(dif)
                #for j,d in enumerate(dif1):
                #    if d > 0 and d < cs1[0]:
                #        cs1[0] = d; cs1[1] = j
                #    elif d < 0 and d > ci1[0]:
                #        ci1[0] = d; ci1[1] = j
                #ci1[0] =  abs(ci1[0]) 
                #for p in rplan2:
                #    dif = p - deg2
                #    if dif < 0 and abs(dif) >= 180  : dif += 360
                #    dif2.append(dif)
                #for j,d in enumerate(dif2):
                #    if d > 0 and d < cs2[0]:
                #        cs2[0] = d; cs2[1] = j
                #    elif d < 0 and d > ci2[0]:
                #        ci2[0] = d; ci2[1] = j
                #ci2[0] =  abs(ci2[0]) 
                #
                #pp = min(cs1,ci1)
                #if pp[0] <= 3.0: 
                #    p1 = pp[1]
                #else:
                #    p1 = (ci1[1],cs1[1])
                #pp = min(cs2,ci2)
                #if pp[0] <= 3.0: 
                #    p2 = pp[1]
                #else:
                #    p2 = (ci2[1],cs2[1])
                
                cr.set_source_rgb(0.5,0.3,0.1)
                if type(p1) == tuple:
                    x_b,_,ww,hh,_,y_b = self.plan[p1[0]].extents
                    if p1[0] in [0,1,6]:
                        scl = 0.003*side*0.6
                    else:
                        scl = 0.003*side*0.7 
                    cr.save()
                    cr.translate(loff*0.6-scl*ww/2,voff+vzones*0.6)
                    cr.scale(scl,scl)
                    self.warpPath(cr,self.plan[p1[0]].paths)
                    cr.fill()
                    cr.restore()
                    x_b,_,ww,hh,_,y_b = self.plan[p1[1]].extents
                    if p1[1] in [0,1,6]:
                        scl = 0.003*side*0.6
                    else:
                        scl = 0.003*side*0.7 
                    cr.save()
                    cr.translate(loff*1.4-scl*ww/2,voff+vzones*0.6)
                    cr.scale(scl,scl)
                    self.warpPath(cr,self.plan[p1[1]].paths)
                    cr.fill()
                    cr.restore()
                    layout = cr.create_layout()
                    font = pango.FontDescription(boss.opts.font)
                    font.set_size(int(32*pango.SCALE*step*22*MAGICK_FONTSCALE))
                    layout.set_font_description(font)
                    font.set_weight(pango.WEIGHT_BOLD)
                    layout.set_text('/')
                    cr.move_to(loff*0.9,voff+vzones*0.3)
                    cr.show_layout(layout) 
                else:
                    x_b,_,ww,hh,_,y_b = self.plan[p1].extents
                    if p1 in [0,1,6]:
                        scl = 0.003*side*0.6
                    else:
                        scl = 0.003*side*0.7 
                    cr.save()
                    cr.translate(loff-scl*ww/2,voff+vzones*0.6)
                    cr.scale(scl,scl)
                    self.warpPath(cr,self.plan[p1].paths)
                    cr.fill()
                    cr.restore()

                cr.set_source_rgb(0.5,0.2,0.5)
                if type(p2) == tuple:
                    x_b,_,ww,hh,_,y_b = self.plan[p2[0]].extents
                    if p2[0] in [0,1,6]:
                        scl = 0.003*side*0.6
                    else:
                        scl = 0.003*side*0.7 
                    cr.save()
                    cr.translate(side-loff*1.4-scl*ww/2,voff+vzones*0.6)
                    cr.scale(scl,scl)
                    self.warpPath(cr,self.plan[p2[0]].paths)
                    cr.fill()
                    cr.restore()
                    x_b,_,ww,hh,_,y_b = self.plan[p2[1]].extents
                    if p2[1] in [0,1,6]:
                        scl = 0.003*side*0.6
                    else:
                        scl = 0.003*side*0.7 
                    cr.save()
                    cr.translate(side-loff*0.6-scl*ww/2,voff+vzones*0.6)
                    cr.scale(scl,scl)
                    self.warpPath(cr,self.plan[p2[1]].paths)
                    cr.fill()
                    cr.restore()
                    layout = cr.create_layout()
                    font = pango.FontDescription(boss.opts.font)
                    font.set_size(int(32*pango.SCALE*step*22*MAGICK_FONTSCALE))
                    layout.set_font_description(font)
                    font.set_weight(pango.WEIGHT_BOLD)
                    layout.set_text('/')
                    cr.move_to(side-loff*1.1,voff+vzones*0.3)
                    cr.show_layout(layout) 
                else:
                    x_b,_,ww,hh,_,y_b = self.plan[p2].extents
                    if p2 in [0,1,6]:
                        scl = 0.003*side*0.6
                    else:
                        scl = 0.003*side*0.7 
                    cr.save()
                    cr.translate(side-loff-scl*ww/2,voff+vzones*0.6)
                    cr.scale(scl,scl)
                    self.warpPath(cr,self.plan[p2].paths)
                    cr.fill()
                    cr.restore()

            cr.set_source_rgb(0.4,0.3,0.4)
            layout = cr.create_layout()
            font = pango.FontDescription(boss.opts.font)
            font.set_size(int(24*pango.SCALE*step*22*MAGICK_FONTSCALE))
            font.set_weight(pango.WEIGHT_BOLD)
            layout.set_font_description(font)
            cr.set_source_rgb(0.4,0.3,0.4) 
            layout.set_text(str(i+1))
            ink,logical = layout.get_extents()
            w = logical[2]/pango.SCALE
            for i,pos in enumerate([degree2,degree1]):
                if pos < 30 * PHI:
                    pos = cusp+step*pos
                else:
                    pos = loff+si+step*(pos-30*PHI)
                cr.move_to(pos-w/2,voff+vzones+vs2*(i+1)+vr*2.3)
                cr.show_layout(layout)
                cr.move_to(pos,voff+vzones+vs2*(i+1)+vr*2.0)
                cr.line_to(pos,voff+vzones+vs2*(i+1)+vr*2.4)
                cr.stroke()
            for i,pos in enumerate([ndegree2,ndegree1]):
                if pos < 30 * PHI:
                    pos = cusp+step*pos
                else:
                    pos = loff+si+step*(pos-30*PHI)
                cr.move_to(pos-w/2,voff+vzones+vs2*(i+1.5)+vr*2.3)
                cr.show_layout(layout)
                cr.move_to(pos,voff+vzones+vs2*(i+1.5)+vr*2.0)
                cr.line_to(pos,voff+vzones+vs2*(i+1.5)+vr*2.4)
                cr.stroke()
            
            if texts:
                cr.set_source_rgb(0.2,0.1,0.2)
                font.set_size(int(12*pango.SCALE*step*22*MAGICK_FONTSCALE))
                font.set_weight(pango.WEIGHT_NORMAL)
                layout.set_font_description(font) 
                for i,d in enumerate(dates):
                    layout.set_text("%s:" % str(i+1))
                    cr.move_to(loff,vs*1.3+vs*0.05*i)
                    cr.show_layout(layout)
                    layout.set_text(d[0])
                    cr.move_to(loff*1.5,vs*1.3+vs*0.05*i)
                    cr.show_layout(layout)
                    layout.set_text(d[1])
                    cr.move_to(loff*3,vs*1.3+vs*0.05*i)
                    cr.show_layout(layout)

        self.swap_fmoon()
        cr.restore()

    def make_finerule(self,cr,x,y,w):
        step = w/33.0
        sf = step*0.618
        si = step - sf

        pat = cairo.LinearGradient(x,y,x+w,y)
        pat.add_color_stop_rgb(0,0.3,0.14,0.47)
        pat.add_color_stop_rgb(0.2,0.68,0.14,0.31)
        pat.add_color_stop_rgb(0.4,0.6,0.76,0.1)
        pat.add_color_stop_rgb(0.6,0.1,0.51,0.6)
        pat.add_color_stop_rgb(0.3,0.4,0.1,1.0)
        pat.add_color_stop_rgb(1,0.3,0.14,0.47)
        cr.set_source(pat)
        #cr.set_source_rgb(0.8,0.8,0.8)
        h = w/250
        cr.rectangle(x,y-h/2,w,h)
        cr.fill()
        
        cr.set_source_rgb(0.3,0.3,0.3)
        for i in range(33):
            if i in [2,7,12,17,22,27,32]:
                cr.set_line_width(step/18)
                dw = 1.01; up = 0.992
            else:
                cr.set_line_width(step/20)
                dw = 1.007; up = 0.995
            cr.move_to(x+si+step*i,y+h/2)
            cr.line_to(x+si+step*i,y-h/2)
            cr.stroke()

    def make_srule(self,cr,x,y,w,h):
        step = w/33.0
        sf = step*0.618
        si = step - sf
        cr.set_source_rgb(0.93,0.85,0.88)
        cr.rectangle(x,y,si,h)
        cr.fill()
        cr.set_source_rgb(0.83,0.8,0.92)
        cr.rectangle(x+si,y,10*step,h)
        cr.fill()
        cr.set_source_rgb(0.8,0.8,0.95)
        cr.rectangle(x+si+10*step,y,5*step,h)
        cr.fill()
        cr.set_source_rgb(0.9,0.83,1.0)
        cr.rectangle(x+si+15*step,y,5*step,h)
        cr.fill()
        cr.set_source_rgb(0.93,0.85,0.88)
        cr.rectangle(x+si+20*step,y,10*step,h)
        cr.fill()
        cr.set_source_rgb(0.83,0.8,0.92)
        cr.rectangle(x+si+30*step,y,2*step+sf,h)
        cr.fill()
        cr.set_source_rgba(0.7,0.7,0.7,0.3)
        cr.rectangle(x,y,w,h*0.15)
        cr.fill()
        cr.rectangle(x,y+h*0.85,w,h*0.15)
        cr.fill()

        cr.set_source_rgb(0.5,0.5,0.5)
        for i in range(33):
            if i in [2,7,12,17,22,27,32]:
                cr.set_line_width(step/18)
                dw = 1.015; up = 0.985
            else:
                cr.set_line_width(step/20)
                dw = 1.01; up = 0.99
            cr.move_to(x+si+step*i,y)
            cr.line_to(x+si+step*i,y*dw)
            cr.stroke()
            cr.move_to(x+si+step*i,y+h)
            cr.line_to(x+si+step*i,(y+h)*up)
            cr.stroke()
        
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(int(10*pango.SCALE*step*22*MAGICK_FONTSCALE))
        layout.set_font_description(font)
        cr.set_source_rgb(0.4,0.3,0.4)
        for i in range(33):
            if i in [2,7,12,17,22,27,32]:
                if i <= 12:
                    layout.set_text(str(i+18))
                else:
                    layout.set_text(str((i+18)%30))
                ink,logical = layout.get_extents()
                w = logical[2]/pango.SCALE
                h = logical[3]/pango.SCALE
                cr.move_to(x+si+step*i-w/2,y+h/4)
                cr.show_layout(layout)

def sparse_plans(plan): 
    boolist = [False,False,False]
    if plan[1][0] - plan[0][0] < 1:
        boolist[0] = True
    if plan[2][0] - plan[1][0] < 1:
        boolist[1] = True
    if plan[0][0] + 30.0 - plan[2][0] < 1:
        boolist[2] = True

    if boolist == [True,False,True]:
        return [0,1,-1]
    elif boolist == [True,True,False]:
        return [-1,0,1]
    elif boolist == [False,True,True]:
        return [1,-1,0]
    elif boolist == [False,False,True]:
        return [1,0,-1]
    elif boolist == [False,True,False]:
        return [0,-1,1]
    elif boolist == [True,False,False]:
        return [-1,1,0]
    else:
        return [0,0,0]

def sparse_curve(plan):
    def diftuple(tuple):
        d = tuple[1][0] - tuple[0][0]
        if d < 0: 
            d += 360
        return d <= 1
    planque = deque(plan)
    boolque = deque([diftuple(t) for t in izip(plan,plan[1:]+[plan[0]])])

    if True in boolque:
        while boolque[0] != True or boolque[-1] != False:
            boolque.rotate(-1)
            planque.rotate(-1) 

    jail = []; cell = set()
    for low,btuple in izip(planque,boolque):
        cell.add((low)) 
        if btuple is False: 
            jail.append(cell)
            cell = set()
    sortedjail = []
    for cell in jail:
        sortedjail.append(sorted(cell))
    return sortedjail
