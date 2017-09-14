import pysw
import chart
import database
from collections import deque
from utils import PersonInfo,dectodeg,parsestrtime
from nexdate import NeXDate
from extensions.path import path
import pickle

datlist = deque(['dat_nat','dat_house','dat_nod','prog_nat','prog_nod','prog_local','prog_soul'])
dialist =  deque(['dyn_cuad','dyn_cuad2','dyn_stars'])
biolist =  deque(['bio_nat','bio_nod','bio_soul'])
tranlist = deque(['draw_transits','rad_and_transit'])
clicklist = deque(['click_hh','click_nn','click_hn','click_nh','subject_click','click_rr','click_bridge'])
opdouble = deque(['draw_nat',
    'draw_house','draw_nod','draw_soul','draw_dharma','draw_ur_nodal','draw_local','draw_prof', 'draw_int', 'draw_single', 'draw_radsoul', 'draw_planetogram'])
optriplepair = deque(['click_hh', 'click_nn', 'click_hn', 'click_nh',
    'click_ss', 'click_rr','subject_click'])
listlabels = { 'opdouble': opdouble,'charts': opdouble, 'data':datlist,'clicks':clicklist,'bio':biolist,'diagram':dialist,'transit':tranlist,'double1':opdouble,'double2':opdouble,'triple1':opdouble,'triple2':optriplepair}

#POOL_CAP = 6

class Current(object):
    datab = database
    def __new__(cls,app=None):
        it = cls.__dict__.get("__it__")
        if it: return it
        cls.__it__ = it = object.__new__(cls)
        it.init(app)
        return it

    def init(self,app):
        self.datab.connect(app)
        self.epheflag = 4
        self.country = ''
        self.usa = False
        self.orbs = []
        self.peorbs = []
        self.transits = []
        self.master = chart.Chart('master')
        self.click = chart.Chart('click')
        self.now = chart.Chart('now')
        self.now.first = _('Momento actual')
        self.calc = chart.Chart('calc')
        self.loc = Locality()
        self.date = NeXDate(self)
        self.calcdt = NeXDate(self)
        self.person = PersonInfo()
        self.charts = { 'master' : self.master, 'click' : self.click,
                'now' : self.now, 'calc' : self.calc }
        self.curr_chart = None
        self.curr_click = None
        self.crossed = True # False!

        self.opmode = 'simple'
        self.curr_op = 'draw_nat'
        self.opright = 'draw_house'
        self.opleft = 'draw_nat'
        self.opup = 'draw_nat'
        self.clickmode = 'master'
        self.curr_list = opdouble

        self.pool = deque([])
        file = path.joinpath(app.home_dir,'mruch.pkl')
        if path.exists(file):
            input = open(file,"rb")
            self.pool = pickle.load(input)
        self.couples = []
        self.coup_ix = 0
        file = path.joinpath(app.home_dir,'coups.pkl')
        if path.exists(file):
            input = open(file,"rb")
            self.couples = pickle.load(input)

        self.fav = []
        self.fav_ix = 0


    def is_valid(self, type):
        chart = self.charts[type]
        if not chart.date or not chart.city:
            return False
        else:
            return True

    def get_active(self,active):
        return self.charts[active]

    def newchart(self):
        return chart.Chart()

    def setchart(self):
        ch = self.charts['calc']
        if self.person.first == '':
            self.person.set_first()
            self.person.last = ''
        ch.first = self.person.first
        ch.last = self.person.last
        ch.comment = ""
        ch.category = ""

        ch.city = self.loc.city
        ch.region = self.loc.region
        ch.country = self.loc.country
        ch.latitud = self.loc.latdec
        ch.longitud = self.loc.longdec
        ch.zone = self.loc.zone
        ch.date = self.calcdt.dateforstore()
        ch.planets, ch.houses = ch.calc(self.calcdt.dateforcalc(),self.loc,self.epheflag)

    def init_nowchart(self):
        self.date.set_now()
        self.refresh_nowchart()

    def set_now(self):
        self.date.set_now()
        ch = self.now
        ch.date = self.date.dateforstore()
        ch.planets, ch.houses = ch.calc(self.date.dateforcalc(),self.loc,self.epheflag)

    def refresh_nowchart(self):
        ch = self.now
        ch.city = self.loc.city
        ch.region = self.loc.region
        ch.country = self.loc.country
        ch.latitud = self.loc.latdec
        ch.longitud = self.loc.longdec
        ch.zone = self.loc.zone
        ch.date = self.date.dateforstore()
        ch.planets, ch.houses = ch.calc(self.date.dateforcalc(),self.loc,self.epheflag)

    def setprogchart(self,chart):
        ch = self.calc
        basech = chart
        self.calcdt.settz(basech.zone)

        self.loc.country = basech.country
        self.loc.city = basech.city
        self.loc.region = basech.region
        self.loc.latdec = basech.latitud
        self.loc.longdec = basech.longitud
        self.loc.zone = basech.zone
        ch.first = basech.first
        ch.last = basech.last
        ch.comment = ""
        ch.category = ""
        ch.city = basech.city
        ch.region = basech.region
        ch.country = basech.country
        ch.latitud = basech.latitud
        ch.longitud = basech.longitud
        ch.zone = basech.zone
        ch.date = self.calcdt.dateforstore()
        ch.planets, ch.houses = ch.calc(self.calcdt.dateforcalc(),self.loc,self.epheflag)

    def setloc(self,city,code):
        fetch = self.datab.fetch_worldcity
        if self.usa:
            fetch = self.datab.fetch_usacity
        try:
            fetch(self.country, unicode(city,"utf-8"), code, self.loc)
            self.date.settz(self.loc.zone)
            self.calcdt.settz(self.loc.zone)
        except StopIteration:
            print "localidad no encontrada: %s" % city

    def set_op(self, op):
        self.curr_op = op

    def set_opdelta(self,delta,side):
        if side == 'up' and self.clickmode == 'click':
            oplist = optriplepair
        else:
            oplist = opdouble
        ix = list(oplist).index(getattr(self,'op'+side))
        oplist.rotate(-ix-delta)
        opside = oplist[0]
        setattr(self,'op'+side,opside)

        if self.opmode == 'simple':
            self.curr_op = self.opleft
            return

        if self.clickmode == 'click':
            if opside == self.opleft:
                self.opright = self.opleft
            else:
                self.opleft = self.opright

    def reset_opup(self):
        if self.clickmode == 'click':
            self.opup = optriplepair[0]
        else:
            self.opup = opdouble[0]

    def set_list(self,label):
        self.curr_list = listlabels[label]

    def format_longitud(self,kind='chart'):
        if kind == 'chart':
            chart = self.curr_chart
        else:
            chart = self.curr_click
        longitud = dectodeg(chart.longitud)[:-2]
        if longitud[0] == '-':
            let = 'W'
            longitud = longitud[1:]
        else:
            let = 'E'
        return longitud[0:-2]+let+longitud[-2:]

    def format_latitud(self,kind='chart'):
        if kind == 'chart':
            chart = self.curr_chart
        else:
            chart = self.curr_click
        lat = dectodeg(chart.latitud)[:-2]
        if lat[0] == '-':
            let = 'S'
            lat = lat[1:]
        else:
            let = 'N'
        return lat[0:-2]+let+lat[-2:]

    def load_import(self,chart, ch):
        chart.first = ch[0]
        chart.last = ch[1]
        chart.category = ch[2]
        chart.city = ch[3]
        chart.region = ch[4]
        chart.country = ch[5]
        chart.date = ch[6]
        chart.latitud = float(ch[7])
        chart.longitud = float(ch[8])
        chart.zone = ch[9]
        chart.planets = [float(p) for p in ch[10:21]]
        chart.houses = [float(h) for h in ch[21:33]]
        chart.comment = ch[33]

    def load_from_pool(self,ix,id):
        if len(self.pool) == 0:
            return False
        self.pool.rotate(-ix)
        poolch = self.pool[0]
        chart = self.charts[id]
        self.replicate(poolch,chart)
        return True

    def load_from_fav(self,ix,id):
        chart = self.charts[id]
        fav = self.fav[ix]
        self.fav_ix = ix
        self.replicate(fav,chart)
        return True

    def replicate(self,src,dest):
        dest.first = src.first
        dest.last = src.last
        dest.category = src.category
        dest.city = src.city
        dest.region = src.region
        dest.country = src.country
        dest.date = src.date
        dest.latitud = src.latitud
        dest.longitud = src.longitud
        dest.zone = src.zone
        dest.planets = src.planets
        dest.houses = src.houses
        dest.comment = src.comment

    def add_to_pool(self,chart,ow):
        if ow:
            self.pool[0] = chart
        else:
            name = " ".join([chart.first,chart.last])
            for i,ch in enumerate(list(self.pool)):
                if " ".join([ch.first,ch.last]) == name:
                    return
            self.pool.appendleft(chart)
            if len(self.pool) > 6:
                self.pool.pop()

    def save_pool(self,app):
        if len(self.pool) == 0:
            return
        file = path.joinpath(app.home_dir,'mruch.pkl')
        output = open(file, 'wb')
        pickle.dump(self.pool, output,-1)
        output.close()

    def save_couples(self,app):
        if len(self.couples) == 0:
            return
        file = path.joinpath(app.home_dir,'coups.pkl')
        output = open(file, 'wb')
        pickle.dump(self.couples, output,-1)
        output.close()

    def get_cycles(self,person2=False):
        chart = [self.curr_chart,self.curr_click][person2]
        return chart.get_cycles(self.date.dt)

    def year_regent(self):
        epheflag = self.epheflag
        pto = [4,0,3,2,1,6,5]
        year = self.date.dt.year
        dnow = pysw.julday(*self.date.dateforcalc())
        s,sunnow,e = pysw.calc(dnow,0,epheflag)
        fsols = pysw.julday(year+1,1,1,0)
        s,solstice,e = pysw.calc(fsols,0,epheflag)
        if not 0.0 <= sunnow < solstice:
            year -=1
        return pto[year%7]


    def safe_delete_chart(self,tbl,id):
        for c in self.couples:
            if (tbl == c['fem'][1] and id == c['fem'][2]) or (tbl == c['mas'][1] and id == c['mas'][2]):
                return False
        return True

    def safe_delete_table(self,tbl):
        for c in self.couples:
            if tbl == c['fem'][1] or tbl == c['mas'][1]:
                return False
        return True

    def fix_couples(self,tbl,first,last,newid):
        name = first
        if last:
            name  += " "+ last
        for c in self.couples:
            if (tbl == c['fem'][1] and name == c['fem'][0]):
                c['fem'] = c['fem'][0], c['fem'][1], newid
                break
            if (tbl == c['mas'][1] and name == c['mas'][2]):
                c['mas'] = c['mas'][0], c['mas'][1], newid
                break

    def chiron(self,ch):
        from directions import strdate_to_date
        import datetime
        from pytz import timezone
        dt = strdate_to_date(ch.date)
        dt = datetime.datetime.combine(dt.date(),dt.time())
        nxdate = NeXDate(self,dt,timezone(ch.zone))
        chi = ch.chiron_calc(nxdate.dateforcalc(),self.epheflag)
        print chi
        #return nxdate

    def vulcan(self,ch):
        from directions import strdate_to_date
        import datetime
        from pytz import timezone
        dt = strdate_to_date(ch.date)
        dt = datetime.datetime.combine(dt.date(),dt.time())
        nxdate = NeXDate(self,dt,timezone(ch.zone))
        vulc = ch.vulcan_calc(nxdate.dateforcalc(),self.epheflag)
        print vulc
        #return nxdate


class Locality(object):
    '''Data for a locality'''
    def __init__(self):
        self.country = ""
        self.country_code = ""
        self.city = ""
        self.region = ""
        self.region_code = ""
        self.latitud = ""
        self.longitud = ""
        self.latdec = None
        self.longdec = None
        self.zone = ""

