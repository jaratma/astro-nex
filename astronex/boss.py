# -*- coding: utf-8 -*-
from gui.mainnb import MainPanel
from zodiac import Zodiac
from drawing.roundedcharts import *
from drawing.aspects import SimpleAspectManager
import database
import config
import chart
from gui.mainnb import Slot
boss = None
import pickle
from directions import solar_rev, sec_prog

suffixes = { 'draw_nat':'rx','draw_nod':'nd','draw_house':'hs','draw_local':'lc',
        'draw_soul':'ca','draw_prof':'pf','draw_int':'in','draw_single':'sn','draw_radsoul':'rsi','draw_dharma':'dh',
        'draw_planetogram':'pg',
        'click_hh':'hh','click_nn':'nn','click_hn':'hn','click_nh':'nh','click_ss':'ss',
        'click_sn':'sn','click_rs':'rsc','sec_prog':'sp','solar_rev':'sr',
        'click_rr':'rc','draw_transits':'tr','dat_nat':'dr','dat_house':'dh',
        'dat_node:':'dn','prog_nat':'pr','prog_nod':'pn','prog_local':'pl','prog_soul':'ps',
        'bio_nat':'br','bio_nod':'bn','bio_soul':'bs','dyn_cuad':'d1','dyn_stars':'ds',
        'subject_click':'cs', 'dyn_cuad2':'d2', 'click_bridge':'br',
        'compo_one':'c1','compo_two':'c2','ascent_star':'as','polar_star':'ps',
        'wundersensi_star':'ws','crown_comp':'cr','paarwabe_plot':'pw',
        'click_counterpanel': 'ch', 'comp_pe': 'pe', 'draw_ur_nodal': 'un'  } 

class Manager(object):
    "manage component interactions"

    def __init__(self,app,opts,state):
        global boss
        self.home_dir = app.home_dir
        self.config_file = app.config_file
        self.app = app
        self.version = app.version
        self.opts = opts
        self.opts.zodiac = Zodiac(self.opts.transtyle)
        self.state = state
        self.ipshell = None
        self.datab = database
        boss = self
        chart.boss = self
        self.slotter = Slot
        SimpleAspectManager.orbs = state.orbs
        SimpleAspectManager.peorbs = state.peorbs
        SimpleAspectManager.trorbs = state.transits
        self.suffixes = suffixes

        f = open('astronex/resources/ac.pk') 
        self.acpaths = pickle.load(f) 
        f.close()

    def set_mainwin(self,mainwin):
        self.mainwin = mainwin
        self.da = self.mainwin.da
        self.mainwin.mpanel.browser.chartview.mainwin = mainwin # @!#?
        self.mpanel = mainwin.mpanel
        self.state.act_pool = MainPanel.actualize_pool
        mainwin.mpanel.init_pools()

        view = self.mpanel.chooser.notebook.get_nth_page(0)
        view.set_cursor(0,)
        view.grab_focus()
        self.da.drawer.hoff = self.da.allocation.width * 0.125
        self.da.drawer.gridw = self.da.drawer.hoff * 6
        self.da.drawer.set_AP_DEG()

    # winmain services
    def get_homer_dir(self):
        return app.home_dir
    
    def set_fullscreen_state(self,flag):
        self.da.__class__.fullscreen = flag    
    
    #################################
    def parse_colors(self):
        return config.parse_colors()

    def parse_aux_colors(self):
        return config.parse_aux_colors()
    
    def get_colors(self):
        return config.cfgcols

    def reset_colors(self):
        config.reset_colors(self.opts) 

    def redraw(self,both=True):
        if both:
            self.da.redraw()
        if self.mainwin.plagram:
            self.mainwin.plagram.sda.redraw()


    def get_state(self):
        return self.state
    
    def get_database(self):
        return self.datab

    def get_version(self):
        return self.version
    
    #####
    def get_showEA(self): 
        return self.da.drawer.get_showEA()

    ##### pdf
    def set_pdf(self,paper,labels=False):
        from surfaces import pdfsurface as surf
        surf.PDFW, surf.PDFH = surf.papers[paper]
        surf.pdflabels = labels

    def set_pdf_custom(self,w,h):
        from surfaces import pdfsurface as surf
        surf.papers['custom'] = (w,h)

    ##### scripts loading
    def load_script(self,script):
        sc = ".".join(['astronex.scripts',script])
        mod = __import__(sc)
        components = sc.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        mod = getattr(mod,script)
        return mod(self)

    ##### chart - Chart interface
    def giveme_single_chartob(self,kind='radix'):
        singles = {'radix':RadixChart,'house':HouseChart,'nodal':NodalChart,
                'soul':SoulChart}
        st = self.get_state()
        return singles[kind](st.curr_chart,st.curr_click)

    def get_simple_amanager(self):
        return SimpleAspectManager()

    def swap_to_ten(self):
        self.da.drawer.aspmanager.swap_to_ten()
        self.da.redraw()

    def swap_to_twelve(self):
        self.da.drawer.aspmanager.swap_to_twelve()
        self.da.redraw()
    
    ##### shell util
    def prepare_shell(self,kind='radix'):
        ch = self.giveme_single_chartob(kind)
        am = self.get_simple_amanager()
        return ch,am

    def calc_house_ap(self,h):
        c = self.get_state().curr_chart
        co = boss.giveme_single_chartob()
        p = co.sortplan()
        return c.calc_house_agep(p,h)


    def list_click_aspects(self,kind='hh'):
        clicks = {
                'hh': HouseHouseChart,
                'hn': HouseHouseChart,
                'nn': NodalNodalChart,
                'nh': NodalNodalChart,
                'ss': SoulSoulChart,
                'rr': RadixRadixChart
                }
        st = self.get_state()
        chobj = clicks[kind](st.curr_chart,st.curr_click)
        am = self.get_simple_amanager()
        
        if kind in ['nn','nh']: 
            p1 = chobj.get_planets(True)
        else:
            p1 = chobj.get_planets()
        chobj.swap_charts()
        if kind == 'nn': 
            p2 = chobj.get_planets(True)
        elif kind == 'hn': 
            chobj.__class__ = NodalNodalChart
            p2 = chobj.get_planets(True) 
        elif kind == 'nh': 
            chobj.__class__ = HouseHouseChart
            p2 = chobj.get_planets() 
        else:
            p2 = chobj.get_planets()

        aspects = set(am.twelve_aspects(p1,p2))
        gw = set(a for a in aspects if a.f1 > 1 and a.f2 > 1)
        aspects.difference_update(gw)
        conj = set(a for a in aspects if a.a == 0)
        aspects.difference_update(conj)
        noopos = set(a for a in aspects if a.a != 6)
        aspects.difference_update(noopos) 
        print 'conj'
        for a in conj:
            print a.p1, a.p2
        print 'opos'
        for a in aspects:
            print a.p1, a.p2


    def load_one_fav(self):
        if not self.state.fav:
            return
        ix = self.state.fav_ix
        active = Slot.storage
        self.state.load_from_fav(ix,active)
        MainPanel.actualize_pool(active,self.state.charts[active]) 
        ix = (ix + 1) % len(self.state.fav)
        self.state.fav_ix = ix 
    

    def solar_rev(self):
        solar_rev(self)
    
    def sec_prog(self): 
        sec_prog(self)  
        
    def load_couple(self):
        if not self.state.couples:
            return
        ix = self.state.coup_ix
        chart = self.state.charts['master']
        table = self.state.couples[ix]['fem'][1]
        id = self.state.couples[ix]['fem'][2]
        self.state.datab.load_chart(table,id,chart)
        self.mpanel.actualize_pool('master',chart) 
        chart = self.state.charts['click']
        table = self.state.couples[ix]['mas'][1]
        id = self.state.couples[ix]['mas'][2]
        self.state.datab.load_chart(table,id,chart)
        self.mpanel.actualize_pool('click',chart) 
        ix = (ix + 1) % len(self.state.couples)
        self.state.coup_ix = ix 

    def search_couple(self,female,male):
        for c in self.state.couples:
            if ((c['fem'][0] == female and c['mas'][0] == male) or 
                    (c['fem'][0] == male and c['mas'][0] == female)):
                return c['dates']
        return None

