# -*- coding: utf-8 -*-
import pango
from datetime import datetime
from .. utils import format_latitud, format_longitud
from .. drawing.roundedcharts import RadixChart,HouseChart,NodalChart
from .. drawing.aspects import SimpleAspectManager
from .. countries import cata_reg
from .. boss import boss
curr = boss.get_state()

aspcol = None

labels = { 'draw_nat': _('Radix'), 'draw_nod': _('Carta Nodal'), 
        'draw_house':_('Carta de las Casas'),'draw_radsoul':_('Carta Clics Radix alma'),
            'draw_local': _('Carta Local'), 'draw_soul': _('Carta del Alma'),
            'draw_dharma': _('Carta del Dharma'),
            'draw_prof': _('Carta del Perfil'), 'draw_int': _('Carta de Integracion'), 
            'draw_single': _('Carta Clics Individual'), 'dat_nat': _('Datos Radix'),
            'dat_nod': _('Datos C. Nodal'), 'dat_house': _('Datos C. Casas'), 
            'prog_nat': _('Progresion E. Radix'), 'prog_nod': _('Progresion E. Nodal'),
            'prog_local': _('Progresion E. Local'), 'prog_soul': _('Progresion E. Alma'), 
            'bio_nat': _('Biografia radix'), 'bio_nod': _('Biografia nodal'), 'bio_soul': _('Biografia alma'), 
            'dyn_cuad': _('Cuadrantes dinamicos'),'dyn_cuad2': _('Clic Cuadrantes dinamicos'),
            'click_hh': _('Clics Casas-Casas'), 'click_nn': _('Clics Nodal-Nodal'),
            'click_nh': _('Clics Nodal-Casas'), 'click_hn': _('Clics Casas-Nodal'),
            'click_rr': _('Clics Radix-Radix'),
            'click_bridge': _('Clic puente'),'dyn_stars':_('Estrellas dinamicas'),
            'draw_transits':_('Transitos'), 'rad_and_transit': _('Radix con transitos'),
            'subject_click':_('Clic subjetivo'), 'ascent_star' :_('Estrella de ascenso'),
            'compo_one': _('Comparacion pareja 1'), 'compo_two': _('Comparacion pareja 2'),
            'click_counterpanel': _('Contra horoscopos'), 'paarwabe_plot': _('Panal de la pareja'),
            'crown_comp': _('Uniones corona'),
            'wundersensi_star': _('Estrella maravillosa'),'polar_star':_('Analisis de polaridades'),
            'comp_pe': _('PE de la pareja'),
            'solar_rev': _('Revolución Solar'), 'sec_prog': 'Progresión Secundaria' }

conj_class = [[(0,4),(0,6),(0,9),(3,4),(3,9),(4,6),(4,7),(4,8),(4,9),(6,7),(7,9)],
            [(0,1),(0,3),(0,5),(0,7),(0,8),(1,3),(1,5),(1,6),(2,6),(2,7),(3,5),(3,6),(3,9),(5,7),(5,9),(6,8),(6,9)],
            [(0,2),(1,2),(1,4),(1,7),(1,8),(1,9),(2,3),(2,4),(2,5),(2,8),(2,9),(3,7),(4,5),(5,6),(5,8),(7,8),(8,9)]] 
plan_class = [[0,4,9],[3,6,7],[1,2,5,8]]

weekdays = [_('Lunes'),_('Martes'),_('Miercoles'),_('Jueves'),_('Viernes'),_('Sabado'),_('Domingo')]

def get_personal_info():
    from .. utils import parsestrtime
    date,time = parsestrtime(curr.curr_chart.date)
    d = date.split('/'); d.reverse()
    d = datetime(*[int(x) for x in d])
    wday = weekdays[d.weekday()]
    datestr = " ".join([wday, date,  time]) 
    lat = curr.curr_chart.latitud
    long = curr.curr_chart.longitud
    geodat = format_longitud(long) + " " + format_latitud(lat)
    name = curr.curr_chart.first + " " + curr.curr_chart.last
    loc = curr.curr_chart.city + " (" + t(curr.curr_chart.country) + ")"
    return name,datestr,loc,geodat

class SheetMixin(object):
    zodlet = ( 'q','w','e','r','t','y','u','i','o','p','a','s' )
    planlet = [ 'd','f','h','j','k','l','g','z','x','c','v' ]
    asplet = ( '1','2','3','4','5','6','7','6','5','4','3','2' )
    def __init__(self,zodiac):
        global aspcol
        aspcol = zodiac.get_aspcolors() 
        self.zod = zodiac.zod
        self.plan = zodiac.plan

    def dat_nat(self,cr,w,h,chartob):
        cr.save()
        cr.set_line_width(0.5)
        
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        self.main_labels(cr,font)
        cr.set_source_rgb(0,0,0)
        cr.move_to(50,80)
        cr.line_to(540,80)
        cr.stroke()
        self.data_planh(cr,font)
        chartob.__class__ = RadixChart
        self.data_aspects(cr,chartob)
        self.data_dyncalc(cr)
        self.data_rays(cr)
        cr.restore()

    def dat_house(self,cr,w,h,chartob):
        cr.save()
        cr.set_line_width(0.5) 
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        self.main_labels(cr,font)
        cr.set_source_rgb(0,0,0)
        cr.move_to(50,80)
        cr.line_to(540,80)
        cr.stroke()
        self.data_house_planh(cr)
        chartob.__class__ = HouseChart
        self.data_aspects(cr,chartob,kind='house')
        cr.restore()
    
    def dat_nod(self,cr,w,h,chartob):
        cr.save()
        cr.set_line_width(0.5) 
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        self.main_labels(cr,font)
        cr.set_source_rgb(0,0,0)
        cr.move_to(50,80)
        cr.line_to(540,80)
        cr.stroke()
        self.data_nodal_planh(cr)
        chartob.__class__ = NodalChart
        chartob.name = 'nodal'
        self.data_aspects(cr,chartob,kind='nodal')
        cr.restore()
    
    def data_rays(self,cr):
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        rays = curr.curr_chart.rays_calc()
        hm = 426; vm = 620

        cr.set_source_rgb(0,0,0.4)
        layout.set_markup("<u>"+ _("Carta de Rayos")+"</u>")
        cr.move_to(hm+10,vm+16) 
        cr.show_layout(layout)
        
        layout.set_markup("<b>%s</b>" % (rays[0]))
        cr.move_to(hm+10,vm+38) 
        cr.show_layout(layout)
        layout.set_markup("")
        
        layout.set_text("%s %s %s" % (rays[1], rays[2], rays[3]))
        cr.move_to(hm+26,vm+38) 
        cr.show_layout(layout)
        layout.set_text("(%s %s %s) %s" % (rays[4], rays[5], rays[6], rays[7]))
        cr.move_to(hm+63,vm+38) 
        cr.show_layout(layout)
    
    
    def data_dyncalc(self,cr):
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        whole = curr.curr_chart.dyncalc_list()
        hm = 50; vm = 680
        ho = 44; vo = 20
        cols=[(0,0,0),(0.6,0,0),(0,0,0.5),(0,0.5,0),
                self.zod[0].col,self.zod[1].col,
                self.zod[2].col,self.zod[3].col]
        tcols=[self.zod[0].col,self.zod[1].col,
                self.zod[2].col,self.zod[3].col]

        cr.set_source_rgb(0,0,0.4)
        layout.set_markup("<u>"+_("Calculos dinamicos")+"</u>")
        cr.move_to(50,636) 
        cr.show_layout(layout)
        layout.set_markup("")
        
        texts = ("Total"," "+_("Card"),"  "+_("Fija"),"  "+_("Mut"), _("Fuego")," "+_("Tierra"),"  "+_("Aire"),_("Agua"))
        for i in range(len(texts)):
            o = [0,18][i>3]
            layout.set_text(texts[i]) 
            cr.move_to(50+(44*i)+o,660) 
            cr.set_source_rgb(*cols[i]) 
            cr.show_layout(layout)

        font = pango.FontDescription("Monospace")
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        
        for i in range(8):
            for j in(0,1,2):
                o = [0,18][i>3]
                cr.move_to(hm+8+o+ho*i,vm+vo*j)
                cr.set_source_rgb(*cols[i]) 
                text ="%s" % whole[j][i]
                layout.set_text(text.rjust(3,' '))
                cr.show_layout(layout)
        
        cr.set_source_rgb(0,0,0)
        cr.set_line_width(0.4)
        cr.move_to(50,676) 
        cr.line_to(410,676)
        cr.move_to(50,716) 
        cr.line_to(410,716)
        cr.move_to(90,658) 
        cr.line_to(90,736)
        cr.move_to(222,676) 
        cr.line_to(222,716)
        cr.move_to(240,676) 
        cr.line_to(240,716)
        cr.stroke()

        font = pango.FontDescription(self.opts.font)
        font.set_size(8*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0.2,0.2,0.4)
        cr.move_to(228,681)
        layout.set_text(_('s'))
        cr.show_layout(layout)
        cr.move_to(228,701)
        layout.set_text(_('c'))
        cr.show_layout(layout)

    def data_aspects(self,cr,chartob,kind='radix'):
        cr.save()
        aspects = curr.curr_chart.aspects(kind)
        hm = 50; vm = 325
        ho = 44; vo = 20

        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0,0,0.4)
        layout.set_markup("<u>"+_("Tabla de aspectos")+"</u>")
        cr.move_to(50,305) 
        cr.show_layout(layout)
        layout.set_markup("")
        
        cr.set_source_rgb(0,0,0)
        cr.set_line_width(0.4)
        for i in range(12):
            cr.move_to(hm,vm+vo*i)
            cr.line_to(hm+484,vm+vo*i)
            cr.stroke()
        for i in range(12):
            cr.move_to(hm+ho*i,vm)
            cr.line_to(hm+ho*i,vm+vo*11)
            cr.stroke()
        
        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(10):
            cr.move_to(hm+15,vm+2+vo*(i+1))
            colp = self.plan[i].col
            cr.set_source_rgb(*colp) 
            text ="%s" % self.planlet[i]
            layout.set_text(text)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()
        hmm = hm + 16
        for i in range(1,11):
            cr.move_to(hmm+ho*i,vm+2)
            colp = self.plan[i].col
            cr.set_source_rgb(*colp) 
            text ="%s" % self.planlet[i]
            layout.set_text(text)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()

        asp_count = [0]*12
        conj_count = [0]*3
        layout = cr.create_layout()
        for i in range(len(aspects)):
            asp = aspects[i]
            if not self.goodwill and asp['gw']:
                continue
            a = asp['a']
            if a > 0:
                asp_count[a] += 1 
            else:
                for ij,cj in enumerate(conj_class):
                    if (asp['p1'],asp['p2']) in cj:
                        conj_count[ij] += 1 
                        break
                else:
                    for il,pl in enumerate(plan_class):
                        if (asp['p1']) in pl:
                            conj_count[il] += 1
                            break

            f1 = int(10-asp['f1']*10)
            if f1 > 9: f1 = 9;
            elif f1 < 0: f1 = ' '
            elif f1 == 0: f1 = 1 
            f2 = int(10-asp['f2']*10)
            if f2 > 9: f2 = 9
            elif f2 < 0: f2 = ' '
            elif f2 == 0: f2 = 1 
            font = pango.FontDescription("Astro-Nex")
            font.set_size(11*pango.SCALE)
            layout.set_font_description(font)
            cr.move_to(hmm+ho*asp['p2'],vm+2+vo*(asp['p1']+1))
            cr.set_source_rgb(*aspcol[asp['a']])
            text ="%s" % self.asplet[asp['a']]
            layout.set_text(text)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()
            font = pango.FontDescription('Monospace')
            font.set_size(8*pango.SCALE)
            layout.set_font_description(font)
            cr.move_to(hmm-9+ho*asp['p2'],vm+4+vo*(asp['p1']+1))
            text = "%s   %s" % (f1,f2)
            layout.set_text(text)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()

        vo = 556
        font = pango.FontDescription("Astro-Nex")
        font.set_size(10*pango.SCALE)
        layout.set_font_description(font)
        cr.move_to(54,vo)
        cr.set_source_rgb(*aspcol[1])
        layout.set_text(self.asplet[1])
        cr.layout_path(layout)
        cr.move_to(100,vo)
        layout.set_text(self.asplet[5])
        cr.layout_path(layout)
        if conj_count[2]:
            cr.move_to(144,vo)
            layout.set_text(self.asplet[0])
            cr.layout_path(layout)
        cr.fill()
        
        cr.set_source_rgb(*aspcol[2])
        cr.move_to(54,vo+20)
        layout.set_text(self.asplet[2])
        cr.layout_path(layout)
        cr.move_to(100,vo+20)
        layout.set_text(self.asplet[4])
        cr.layout_path(layout)
        if conj_count[1]:
            cr.move_to(144,vo+20)
            layout.set_text(self.asplet[0])
            cr.layout_path(layout)
        cr.fill()
        cr.set_source_rgb(*aspcol[3])
        cr.move_to(54,vo+40)
        layout.set_text(self.asplet[3])
        cr.layout_path(layout)
        cr.move_to(100,vo+40)
        layout.set_text(self.asplet[6])
        cr.layout_path(layout)
        if conj_count[0]:
            cr.move_to(144,vo+40)
            layout.set_text(self.asplet[0])
            cr.layout_path(layout)
        cr.fill()

        font = pango.FontDescription('Monospace')
        font.set_size(8*pango.SCALE)
        layout.set_font_description(font)
        cr.set_source_rgb(0,0,0.4)
        cr.move_to(80,vo)
        layout.set_text(str(asp_count[1]+asp_count[11]))
        cr.layout_path(layout)
        cr.move_to(124,vo)
        layout.set_text(str(asp_count[5]+asp_count[7]))
        cr.layout_path(layout)
        cr.move_to(80,vo+20)
        layout.set_text(str(asp_count[2]+asp_count[10]))
        cr.layout_path(layout)
        cr.move_to(124,vo+20)
        layout.set_text(str(asp_count[4]+asp_count[8]))
        cr.layout_path(layout)
        cr.move_to(80,vo+40)
        layout.set_text(str(asp_count[3]+asp_count[9]))
        cr.layout_path(layout)
        cr.move_to(124,vo+40)
        layout.set_text(str(asp_count[6]))
        cr.layout_path(layout)
        if conj_count[2]:
            cr.move_to(164,vo)
            layout.set_text(str(conj_count[2]))
            cr.layout_path(layout)
        if conj_count[1]:
            cr.move_to(164,vo+20)
            layout.set_text(str(conj_count[1]))
            cr.layout_path(layout)
        if conj_count[0]:
            cr.move_to(164,vo+40)
            layout.set_text(str(conj_count[0]))
            cr.layout_path(layout)
        cr.fill()

        green = asp_count[1]+asp_count[11]+asp_count[5]+asp_count[7]+conj_count[2]
        blue = asp_count[2]+asp_count[10]+asp_count[4]+asp_count[8]+conj_count[1]
        red = asp_count[3]+asp_count[6]+asp_count[9]+conj_count[0]
        cr.move_to(182,vo)
        layout.set_text('= '+str(green))
        cr.layout_path(layout)
        cr.move_to(182,vo+20)
        layout.set_text('= '+str(blue))
        cr.layout_path(layout)
        cr.move_to(182,vo+40)
        layout.set_text('= '+str(red))
        cr.layout_path(layout)
        cr.fill()
        cr.move_to(218,vo+20)
        layout.set_text(str(red+blue+green))
        cr.layout_path(layout)
        cr.fill()
        cr.rectangle(216,vo+16,16,16)
        cr.stroke()

        pl = chartob.get_planets()
        am = SimpleAspectManager()
        asp_for_slop = am.strong_chain(pl)
        slopeob = chartob.slope_classify(asp_for_slop)
        #print slopeob.__dict__
        
        #if kind != 'radix':
        #    return

        cr.set_line_width(0.85)
        cr.set_source_rgb(*aspcol[1])
        cr.move_to(300,vo+5)
        cr.line_to(310,vo+5) 
        cr.stroke()
        cr.move_to(300,vo+30)
        cr.line_to(310,vo+20) 
        cr.stroke() 
        cr.move_to(305,vo+50)
        cr.line_to(305,vo+40) 
        cr.stroke() 

        cr.set_source_rgb(*aspcol[2])
        cr.move_to(350,vo+5)
        cr.line_to(360,vo+5) 
        cr.stroke()
        cr.move_to(350,vo+30)
        cr.line_to(360,vo+20) 
        cr.stroke()
        cr.move_to(355,vo+50)
        cr.line_to(355,vo+40) 
        cr.stroke() 
        cr.set_source_rgb(*aspcol[3])
        cr.move_to(400,vo+5)
        cr.line_to(410,vo+5) 
        cr.stroke()
        cr.move_to(400,vo+30)
        cr.line_to(410,vo+20) 
        cr.stroke()
        cr.move_to(405,vo+50)
        cr.line_to(405,vo+40) 
        cr.stroke() 
        
        cr.set_line_width(0.5)
        cr.set_source_rgb(0,0,0.4)
        cr.move_to(325,vo) 
        layout.set_text(str(slopeob.hg))
        cr.layout_path(layout)
        cr.move_to(375,vo) 
        layout.set_text(str(slopeob.hb))
        cr.layout_path(layout)
        cr.move_to(425,vo) 
        layout.set_text(str(slopeob.hr))
        cr.layout_path(layout)
        cr.move_to(445,vo) 
        layout.set_text('= '+str(slopeob.hr+slopeob.hg+slopeob.hb))
        cr.layout_path(layout) 
        cr.move_to(325,vo+20) 
        layout.set_text(str(slopeob.dg))
        cr.layout_path(layout)
        cr.move_to(375,vo+20) 
        layout.set_text(str(slopeob.db))
        cr.layout_path(layout)
        cr.move_to(425,vo+20) 
        layout.set_text(str(slopeob.dr))
        cr.layout_path(layout)
        cr.move_to(445,vo+20) 
        layout.set_text('= '+str(slopeob.dr+slopeob.dg+slopeob.db))
        cr.layout_path(layout)
        cr.move_to(325,vo+40) 
        layout.set_text(str(slopeob.vg))
        cr.layout_path(layout)
        cr.move_to(375,vo+40) 
        layout.set_text(str(slopeob.vb))
        cr.layout_path(layout)
        cr.move_to(425,vo+40) 
        layout.set_text(str(slopeob.vr))
        cr.layout_path(layout)
        cr.move_to(445,vo+40) 
        layout.set_text('= '+str(slopeob.vr+slopeob.vg+slopeob.vb))
        cr.layout_path(layout)
        cr.fill()
        cr.restore()

    def data_nodal_planh(self,cr):
        h = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"]
        plan = curr.curr_chart.planets[:]
        cusp = plan[10]
        plan[10] = curr.curr_chart.houses[0]
        cr.set_source_rgb(0,0,0.4)
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        taba = pango.TabArray(1,True)
        taba.set_tab(0,pango.TAB_LEFT,120)
        layout.set_tabs(taba)

        layout.set_markup("<u>"+_("Planetas")+"</u>\t<u>"+_("Casa")+"</u>")
        cr.move_to(50,86) 
        cr.show_layout(layout)
        layout.set_markup("")
        taba.set_tab(0,pango.TAB_LEFT,98)
        layout.set_tabs(taba)
        for i in range(len(plan)):
            deg = plan[i] - cusp
            if deg > 0: deg = 360 - deg
            else: deg = abs(deg)
            house = int(deg/30)
            deg -= house*30
            d = int(deg)
            m = int(60*(deg-d))
            d = str(d).rjust(2,'0')
            m = str(m).rjust(2,'0')
            res = u"%s\u00b0 %s\u00b4\t%s" % (d,m,h[house%12])
            cr.move_to(74,105+i*16)
            layout.set_text(res)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()

        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(50,105+i*16)
            colp = self.plan[i].col
            cr.set_source_rgb(*colp) 
            text ="%s" % self.planlet[i]
            layout.set_text(text)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()

    def data_house_planh(self,cr):
        hh = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"]
        pl = curr.curr_chart.housepos_and_sector()
        cr.set_source_rgb(0,0,0.4)
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        taba = pango.TabArray(2,True)
        taba.set_tab(0,pango.TAB_LEFT,100)
        taba.set_tab(1,pango.TAB_LEFT,150)
        layout.set_tabs(taba)
        layout.set_markup("<u>"+_("Planetas")+"</u>\t<u>"+_("Casa")+"</u>\t<u>"+_("Zona")+"</u>")
        cr.move_to(50,86) 
        cr.show_layout(layout)
        layout.set_markup("")
        signs = curr.curr_chart.which_all_signs()
        text = ""
        
        taba = pango.TabArray(2,True)
        taba.set_tab(0,pango.TAB_LEFT,90)
        taba.set_tab(1,pango.TAB_LEFT,140)
        layout.set_tabs(taba)
        cr.set_source_rgb(0,0,0)
        for i in range(len(pl)):
            l = str(pl[i][0]).rjust(2,'0')
            m = str(pl[i][1]).rjust(2,'0')
            h = hh[pl[i][2]]
            z = pl[i][3]
            res = u"%s\u00b0 %s\u00b4\t%s\t%s" % (l,m,h,z) 
            cr.move_to(70,105+i*16)
            layout.set_text(res)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()

        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(50,105+i*16)
            colp = self.plan[i].col
            cr.set_source_rgb(*colp) 
            text ="%s" % self.planlet[i]
            layout.set_text(text)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()

    def data_planh(self,cr,font):
        cr.set_source_rgb(0,0,0.4)
        layout = cr.create_layout()
        taba = pango.TabArray(4,True)
        taba.set_tab(0,pango.TAB_LEFT,50)
        taba.set_tab(1,pango.TAB_LEFT,200)
        taba.set_tab(2,pango.TAB_LEFT,350)
        taba.set_tab(3,pango.TAB_LEFT,466)
        layout.set_tabs(taba)
        layout.set_markup("\t<u>"+_("Planetas")+"</u>\t<u>"+_("Casas")+"</u>\t<u>"+_("P.Inv.")+"</u>\t<u>"+_("P.Rep.")+"</u>")
        layout.set_font_description(font)
        font.set_size(9*pango.SCALE)
        cr.move_to(0,86) 
        cr.show_layout(layout)
       
        layout.set_markup("")
        signs = curr.curr_chart.which_all_signs()
        text = ""
        
        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(50,105+i*16)
            colp = self.plan[i].col
            cr.set_source_rgb(*colp) 
            text ="%s" % self.planlet[i]
            layout.set_text(text)
            cr.show_layout(layout)
            cr.new_path()
            
        cr.set_source_rgb(0,0,0)
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(70,105+i*16)
            text = signs[i]['deg']
            layout.set_text(text)
            cr.show_layout(layout)
            cr.new_path()

        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(126,103+i*16)
            col = self.zod[signs[i]['col']%4].col
            text ="%s" % (self.zodlet[signs[i]['name']])
            cr.set_source_rgb(*col) 
            layout.set_text(text)
            cr.show_layout(layout)
            cr.new_path()

        h = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"]
        chart = curr.curr_chart
        hh = chart.which_all_houses()
        cr.set_source_rgb(0,0,0)
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        taba = pango.TabArray(3,True)
        taba.set_tab(0,pango.TAB_LEFT,26)
        taba.set_tab(1,pango.TAB_LEFT,106)
        taba.set_tab(2,pango.TAB_LEFT,146)
        layout.set_tabs(taba)
        for i in range(12):
            cr.move_to(200,105+i*16)
            d,ii,l = hh[i]
            text = h[i] + "\t" + d['deg'] +"\t\t"+ii['deg']+"\t\t"+l['deg']
            layout.set_text(text)
            cr.show_layout(layout)
            cr.new_path()

        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(12):
            for j in (0,1,2):
                sign = hh[i][j]
                cr.move_to(284+120*j,103+i*16)
                text = self.zodlet[sign['name']]
                layout.set_text(text)
                col = self.zod[sign['col']%4].col
                cr.set_source_rgb(*col) 
                cr.show_layout(layout)
                cr.new_path()

    def main_labels(self,cr,font,kind='radix'):
        layout = cr.create_layout()
        label = labels[curr.curr_op]
        layout.set_text("%s\n%s\n%s %s" % get_personal_info())
        layout.set_font_description(font)
        cr.move_to(50,30)
        cr.set_source_rgb(0,0,0)
        cr.show_layout(layout)
        cr.set_source_rgb(0,0,0.4) 
        layout.set_text(label)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(540-xpos,30)
        cr.show_layout(layout)
        if kind == 'local':
            font = pango.FontDescription(self.opts.font)
            font.set_size(8*pango.SCALE)
            layout.set_font_description(font)
            cr.set_source_rgb(0,0.5,0.3) 
            region = curr.loc.region
            if boss.opts.lang == 'ca' and curr.loc.country == u'España':
                region = cata_reg[region]
            layout.set_text(curr.loc.city+' ('+region+'-'+t(curr.loc.country)[0]+')')
            ink,logical = layout.get_extents()
            xpos = logical[2]/pango.SCALE
            cr.move_to(540-xpos,45)
            cr.show_layout(layout)



