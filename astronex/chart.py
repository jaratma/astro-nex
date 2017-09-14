#!/usr/bin/python
import pysw
from math import sqrt,cos,sin,pi
from datetime import datetime,timedelta,time
from pytz import timezone
from utils import parsestrtime, strdate_to_date
from nexdate import NeXDate
from drawing import roundedcharts 
boss = None
RAD = pi / 180
PHI = 1 / ((1+sqrt(5))/2)
points = [12,12,8,8,8,8,12,6,6,6,4]
planames = ['sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto','node']
zodnames =  ['aries', 'tauro', 'geminis', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagitario', 'capricornio', 'acuario', 'piscis' ]
aspnames = ['conj','semi','sext','cuad','trig','quinc','opos','quinc','trig','cuad','sext','semi']
conj_class = [[(0,4),(0,6),(0,9),(3,4),(3,9),(4,6),(4,7),(4,8),(4,9),(6,7),(7,9)],
            [(0,1),(0,3),(0,5),(0,7),(0,8),(1,3),(1,5),(1,6),(2,6),(2,7),(3,5),(3,6),(3,9),(5,7),(5,9),(6,8),(6,9)],
            [(0,2),(1,2),(1,4),(1,7),(1,8),(1,9),(2,3),(2,4),(2,5),(2,8),(2,9),(3,7),(4,5),(5,6),(5,8),(7,8),(8,9)]] 
plan_class = [[0,4,9],[3,6,7],[1,2,5,8]]

orbs = []

planclass = [0,0,1,1,2,1,2,3,3,3,4] # related to
aspclass = [4,0,1,2,3,1,4,1,3,2,1,0]    # orbs table

class Chart(object):

    def __init__(self,id=None):
        self.id = id
        self.first = ""
        self.last = ""
        self.category = ""
        self.city = ""
        self.region = ""
        self.country = ""
        self.date = ""
        self.latitud = ""
        self.longitud = ""
        self.zone = ""
        self.planets = []
        self.houses = []
        self.comment = ""

    def __repr__(self):
        person = ",".join([self.first,self.last,self.category])
        country = ",".join([self.city,self.region,self.country])
        geo = ",".join([self.date,str(self.latitud),str(self.longitud),self.zone])
        planets = ",".join((str(p) for p in self.planets))
        houses = ",".join((str(h) for h in self.houses))
        return ",".join([person,country,geo,planets,houses,self.comment])

    def calc(self,date,loc,epheflag): 
        d = pysw.julday(*date)
        lt = loc.latdec
        lg = loc.longdec
        p = pysw.planets(d,epheflag)
        h = pysw.houses(d,lt,lg)
        #print h[0]
        return p,h
    
    def chiron_calc(self,date,epheflag): 
        d = pysw.julday(*date)
        chi = pysw.calc(d,15,epheflag)
        return chi

    def vulcan_calc(self,date,epheflag): 
        d = pysw.julday(*date)
        vulc = pysw.calc_ut(d,55)
        return vulc
    
    def calc_plan_with_retrogression(self,epheflag=4):
        dt = strdate_to_date(self.date)
        dt = NeXDate(self,dt,timezone(self.zone))
        d = pysw.julday(*dt.dateforcalc())
        signs = []
        for i in range(12):
            if i == 10:
                continue
            err,l,s,mes = pysw.calc_ut_with_speed(d,i,epheflag)
            if err < 0:
                print("error: %s" % mes)
                return None
            sg = self.which_sign(l)
            sg['speed'] = s
            signs.append((sg))
        return signs

    
    def calc_localhouses(self):
        curr = boss.get_state()
        d = pysw.julday(*curr.calcdt.dateforcalc())
        lt = curr.loc.latdec
        lg = curr.loc.longdec
        h = pysw.local_houses(d,lg,lt,curr.epheflag)
        return h
    
    def soulplan(self):
        sizes = self.sizes()
        splan = []
        for p in iter(self.planets):
            s = int(p/30)
            dh = (p - s*30) * sizes[s]/30
            pos = self.houses[s] + dh
            if pos > 360: pos -= 360
            splan.append(pos)
        return splan 

    def urnodplan(self):
        sizes = self.sizes()
        plans = self.planets[:]
        plans[10] = self.houses[0]
        nod = self.planets[10]
        n = nod % 30.0
        uplan = []
        for p in iter(plans):
            h = 11 - int(((p-nod)/30.0)%12)
            dist = (n - p % 30.0) % 30.0
            uplan.append((self.houses[h] + dist*sizes[h]/30.0) % 360)
        return uplan

    
    def aspects(self,kind='radix'):
        if kind == 'house':
            pl= self.house_plan_long()
        elif kind == 'soul':
            pl= self.soulplan()
        else: 
            pl= self.planets[:]
        if kind == 'nodal':
            pl[10] = self.houses[0]
        chart_orbs = []
        for i in range(len(pl)):
            for j in range(i+1,len(pl)):
                pci = planclass[i]
                if j != 10:
                    pcj = planclass[j] 
                else:
                    pcj = planclass[i]
                dis = abs(pl[i] - pl[j])
                nsig = int(dis/30)
                orb = dis - nsig*30
                if orb > 20.0:
                    nsig += 1; orb = 30.0 - orb
                acl = aspclass[nsig%12]
                if orb <= 9.0:
                    orb1 = orbs[pci][acl]
                    orb2 = orbs[pcj][acl]
                    if orb <= orb1 or orb <= orb2:
                        f1 = orb / orb1
                        f2 = orb / orb2
                        chart_orbs.append({ "p1":i,"p2":j,"a":nsig%12,"f1":f1,"f2":f2,'gw':False })
                    elif orb <= orb1*1.1 or orb <= orb2*1.1:
                        chart_orbs.append({ "p1":i,"p2":j,"a":nsig%12,"f1":0,"f2":0,'gw':True })
        return chart_orbs

    def calc_aspects(self,pl,click=None):
        aspects = []
        class asp_obj(object): 
            def __init__(self,**kargs): self.__dict__ = kargs
        lencl = len(pl)
        pairpl = pl
        if click:
            lencl = len(click)
            pairpl = click

        for i in range(len(pl)):
            for j in range(not click and i+1 or 0,lencl):
                dis = abs(pl[i] - pairpl[j])
                nsig,orb = divmod(dis,30)
                if orb > 20.0:  nsig += 1; orb = 30.0 - orb
                nsig = int(nsig%12)
                pc1 = planclass[i]
                if click or not click and j != 10:
                    pc2 = planclass[j]
                else: 
                    pc2 = planclass[i]
                acl = aspclass[nsig]
                orb1,orb2 = orbs[pc1][acl],orbs[pc2][acl] 
                if orb <= orb1*1.1 or orb <= orb2*1.1:
                    pos1 = cos(pl[i]*RAD),sin(pl[i]*RAD)
                    pos2 = cos(pairpl[j]*RAD),sin(pairpl[j]*RAD)
                    aspects.append(asp_obj(p1=i,p2=j,d1=pos1,d2=pos2,a=nsig,f1=orb/orb1,f2=orb/orb2)) 
        return aspects

    def sizes(self):
        hs = self.houses[0:7]
        sizes = [0] * 6
        for i in range(6):
            s = hs[(i+1)] - hs[i]
            if s < 0: s += 360 
            sizes[i] = s
        return sizes*2

    def house_plan_long(self):
        '''House chart planet longitud, from asc.'''
        plinh = self.plan_in_house()
        factor = [30/s for s in iter(self.sizes())]
        hspl = [0]*11
        for i in range(11):
            h = plinh[i]
            dist = self.planets[i] - self.houses[h]
            if dist < 0: dist += 360 
            hspl[i] = h*30 + dist*factor[h]
        return hspl

    def invert_house_plan(self,hspl):
        factor = [s/30 for s in iter(self.sizes())]
        ipl = [0]*11
        for i,hp in enumerate(hspl):
            h, deg = divmod(hp,30)
            ipl[i] = self.houses[int(h)] + deg * factor[int(h)]
        return ipl

    def invert_house_sign(self,hssg):
        factor = [s/30 for s in iter(self.sizes())]
        isg = [0]*12
        for i,hp in enumerate(hssg):
            h, deg = divmod(hp,30)
            isg[i] = self.houses[int(h)] + deg * factor[int(h)]
        return isg

    def nod_plan_long(self):
        factor = [s/30 for s in self.sizes()]
        plan = self.planets[:]
        asc = self.houses[0]
        plan[10],asc = asc,plan[10]
        ndpl = []
        for p in plan:
            dist = 360 - (p-asc)%360
            h,d = divmod(dist,30) 
            h = int(h)
            ndpl.append(self.houses[h] + d * factor[h])
        return ndpl

    def plan_in_house(self):
        plinh = [0]*11
        for i,plan in enumerate(self.planets):
            for j in range(len(self.houses)):
                h1 = self.houses[j]
                h2 = self.houses[(j+1)%12]
                if h1 > h2:
                    #planet between 0 and h2
                    if plan < h1 and plan < h2: plan += 360 
                    h2 += 360
                if plan > h1 and plan < h2:
                    plinh[i] = j
                    break
        return plinh

    def get_low_points(self):
        pr = []
        sz = self.sizes()
        for h in range(len(self.houses)):
            d = self.houses[h]
            g = sz[h]*PHI 
            l = d + g 
            pr.append(l)
        return pr

######### draw houses
    def sign_sizes(self):
        ss = self.house_sign_long()
        sizes = [0] * 12
        for i in range(len(ss)):
            s = ss[(i+1)%12] - ss[i]
            if s < 0: s += 360 
            sizes[i] = s
        return sizes

    def invert_sign_sizes(self,cusps):
        sizes = [0] * 12
        for i in range(len(cusps)):
            s = cusps[(i+1)%12] - cusps[i]
            if s < 0: s += 360 
            sizes[i] = s
        return sizes

    def house_sign_long(self):
        signinh = self.sign_in_house()
        factor = [30/s for s in self.sizes()]
        hssg = []
        for i in range(12):
            h = signinh[i]
            dist = (i*30 - self.houses[h]) % 360
            res = h*30 + dist*factor[h]
            hssg.append(res)
        return hssg

    def sign_in_house(self):
        signinh = []
        for i in range(12):
            sign = 30*i
            for j in range(len(self.houses)):
                h1 = self.houses[j]
                h2 = self.houses[(j+1)%12]
                if h1 > h2:
                    if sign < h1 and sign < h2: sign += 360 
                    h2 += 360
                if sign > h1 and sign < h2:
                    signinh.append(j)
                    break
        return signinh

    def which_house_from_geo(self,geodeg):
        zoddeg = (180+self.houses[0]-geodeg)%360
        house = self.which_house(zoddeg)
        dist = zoddeg - self.houses[house]
        if dist < 0: dist += 360
        return house,dist/self.sizes()[house]

######### node special
    def nod_sign_long(self):
        nod = self.planets[10]
        asc = self.houses[0]
        sizes = self.sizes()
        sign,deg = divmod(nod,30)
        factor = [s/30 for s in sizes]
        hssg = []
        for i in range(12):
            res = self.houses[i] + deg*factor[i]
            #print res-asc,deg*factor[i]
            hssg.append(res-asc)
        return hssg
    
    def nodal_cusp_degrees(self):
        nodasc = self.planets[10]
        hn = []
        for i in range(12):
            c = nodasc - 30*i
            if c < 0: c += 360.0
            hn.append(c)
        return hn

######### cross points
    def calc_cross_points(self,cross=None):
        sizes = self.sizes()
        hasc = self.houses[0]
        nnode = self.planets[10]
        h = 0
        hn = self.which_house(nnode)
        while hn > h:
            if hn - h == 1 and hn < self.which_house((nnode - 30) % 360):
                break
            if h == 0 and hn == 1:
                break
            h = (h+1)%12
            hasc = self.houses[h]
            nnode = (nnode - 30) % 360
            hn = self.which_house(nnode)
        dist = nnode - hasc

        if dist < 0:
            if dist < -30: # aries pisces
                dist += 360 
            else:
                h = (h-1)%12 # cp in prev h.
        else:
            if h > hn:
                dist -= 360
                h = (h-1)%12 # cp in prev h.


        va = sizes[h] / 6
        vn = 5.0
        la = dist * va / (va + vn)
        
        if not cross:
            #print (hasc + la) % 360
            return (hasc + la) % 360 # h+1
        
        r = {}
        r['cp1'] = self.which_sign((hasc+la)%360)
        r['cp2'] = self.which_sign((hasc+la+180)%360)

        h += [0,1][la < 0] # 
        r['dat1'] = self.cp_time_lapsus(h,la)
        r['dat2'] = self.cp_time_lapsus((h+6)%12,la)
        return r

    def calc_pe_houses(self):
        sizes = self.sizes()
        asc = self.houses[0]
        cp1 = self.calc_cross_points()
        node = self.planets[10]
        desc = (asc+180) % 360
        cp2 = (cp1+180) % 360
        above = self.which_house(node) >= 6 
        seq = [cp1,node,desc,cp2,asc]
        hseq = [self.which_house(s) for s in seq]
        hseq[2] = 6
        hseq[4] = 0
        if above:
            seq[1],seq[2] = seq[2],seq[1] 
            hseq[1],hseq[2] = hseq[2],hseq[1] 
        ix = 0
        housez = []
        for i,h in enumerate(self.houses):
            lh = []
            if i != 6: lh.append((ix,0))
            while i == hseq[ix]:
                frac = (seq[ix] - h)%30 / sizes[i]
                ix += 1 #(ix + 1) % 5
                lh.append((ix,frac))
            housez.append(lh)
        return housez 

    def which_sign(self,d):
        deg = d
        name = int(deg/30)%12
        col = int(deg/30)%12
        deg = deg - 30*int(deg/30)
        mint = int(60*(deg - int(deg)))
        mint = str(mint).rjust(2,'0')
        deg = int(deg)
        deg = str(deg).rjust(2,'0')
        return { 'deg': u"%s\u00b0 %s\u00b4" % (deg,mint), 'name': name , 'col': col}

    def which_house(self,p):
        point = p
        for i in range(12):
            h1 = self.houses[i]
            h2 = self.houses[(i+1)%12]
            if h1 > h2: # piscis - aries
                if point < h1 and point < h2: point += 360
                h2 += 360
            if point > h1 and point <= h2:
                return i
        return None

    def which_house_nodal(self,p):
        point = p
        house = self.planets[10]
        for i in range(12):
            h1 = (house + 30.0 * i) % 360.0
            h2 = (house + 30*(i+1)) % 360.0
            if h1 > h2: # piscis - aries
                if point < h1 and point < h2: point += 360
                h2 += 360
            if point > h1 and point <= h2:
                return (11 - i)
        return None

    def planline(self):
        return [ (p%30)*12 for p in self.planets ]
            

###########################################
#dynamics
###########################################

    def signdyn(self):
        sum1 = 0
        signs = [0] * 12
        hou = [0] * 12
        for h in (0,3,6,9):
            hou[h] = int(self.houses[h]/30)
        for i in range(len(self.planets)):
            p = self.planets[i]
            sign = int(p/30)
            deg = p - sign*30
            point = points[i]
            if deg < 2 or deg >= 27:
                point -= 3
            elif deg >= 7 and deg <= 18:
                point += 3
            
            signs[sign] += point
            if sign == hou[0]:
                sum1 += 1

            if deg >= 29 and deg < 30:
                signs[(sign+1)%12] += int(point/2)
            elif deg >= 0 and deg < 1:
                signs[(sign+11)%12] += int(point/2) 
            
        if  sum1 == 1:
            signs[hou[0]] += 5 
        else:
            signs[hou[0]] += 3*sum1
        return self.resolve_dyn(signs)
	
    def housedyn(self):
        magick = [0.206, 0.412, 0.6847, 0.745, 0.8727, 0.966]
        houses = [0] * 12
        plinh = self.plan_in_house()
        sizes = self.sizes()
        for i in range(11):
            point = points[i]
            hou = plinh[i]
            houplus = (hou+1)%12
            if hou % 3 == 0:
                plus = 5
            else:
                plus = 3
            p = self.planets[i] - self.houses[hou]
            if p < 0: p += 360
            zone = [0] * 6
            for j in range(6):
                zone[j] = sizes[hou]*magick[j]
            if p < zone[0]:
                houses[hou] += (point + plus)
            elif p < zone[1]:
                houses[hou] += point
            elif p < zone[2]:
                houses[hou] += (point - 3)
            elif p < zone[3]:
                houses[hou] += (point - 3)
                houses[houplus] += (point - 3)
            elif p < zone[4]:
                houses[hou] += point
                houses[houplus] += point
            elif p < zone[5]:
                if houplus % 3 == 0:
                    plus = 5
                else:
                    plus = 3
                houses[hou] += (point + plus)
                houses[houplus] += (point + plus)
            else:
                if houplus % 3 == 0:
                    plus = 5
                else:
                    plus = 3
                houses[houplus] += (point + plus)
        return self.resolve_dyn(houses) 

	
    def resolve_dyn(self,dinary):
        elem = { 'fire': 0, 'earth': 0, 'air': 0, 'water': 0 }
        cross = { 'card': 0, 'fix': 0, 'mut': 0 }

        for i in range(len(self.houses)):
            if i%4 == 3:
                elem['water'] += dinary[i]
            elif i%4 == 0: 
               elem['fire'] += dinary[i]
            elif i%4 == 1: 
               elem['earth']	+= dinary[i]
            elif i%4 == 2: 
               elem['air'] += dinary[i]

            if i%3 == 2:
               cross['mut'] += dinary[i]
            elif i%3 == 0: 
               cross['card'] += dinary[i]
            elif i%3 == 1: 
               cross['fix'] += dinary[i] 
        return { 'elem': elem, 'cross': cross }

    def dyncalc_stress(self):
        ds = self.signdyn()
        dh = self.housedyn()
        tots = ds['cross']['card']+ds['cross']['fix']+ds['cross']['mut']
        toth = dh['cross']['card']+dh['cross']['fix']+dh['cross']['mut']
        return toth - tots

    def dyncalc_list(self):
        ds = self.signdyn()
        dh = self.housedyn()
        tots = ds['cross']['card']+ds['cross']['fix']+ds['cross']['mut']
        toth = dh['cross']['card']+dh['cross']['fix']+dh['cross']['mut']
        cr = ds['cross']; el = ds['elem']
        srow = tots,cr['card'],cr['fix'],cr['mut'],el['fire'],el['earth'],el['air'],el['water']
        cr = dh['cross']; el = dh['elem']
        hrow = toth,cr['card'],cr['fix'],cr['mut'],el['fire'],el['earth'],el['air'],el['water'] 
        whole = zip(hrow,srow)
        dif = []
        for pair in whole:
            dif.append(reduce(lambda x,y:x-y,pair))
        srow = [str(s) for s in srow]
        hrow = [str(s) for s in hrow]
        dif = [str(s) for s in dif ]
        return srow,hrow,dif

    def dynstar_signs(self):
        d = self.signdyn()
        dyn = [0]*12
        el = d['elem']
        cr = d['cross']
        dyn[0] = cr['card'] + el['fire']
        dyn[1] = cr['fix'] + el['earth']
        dyn[2] = cr['mut'] + el['air']
        dyn[3] = cr['card'] + el['water']
        dyn[4] = cr['fix'] + el['fire']
        dyn[5] = cr['mut'] + el['earth']
        dyn[6] = cr['card'] + el['air']
        dyn[7] = cr['fix'] + el['water']
        dyn[8] = cr['mut'] + el['fire']
        dyn[9] = cr['card'] + el['earth']
        dyn[10] = cr['fix'] + el['air']
        dyn[11] = cr['mut'] + el['water']
        return dyn

    def dynstar_houses(self):
        d = self.housedyn()
        dyn = [0]*12
        el = d['elem']
        cr = d['cross']
        dyn[0] = cr['card'] + el['fire']
        dyn[1] = cr['fix'] + el['earth']
        dyn[2] = cr['mut'] + el['air']
        dyn[3] = cr['card'] + el['water']
        dyn[4] = cr['fix'] + el['fire']
        dyn[5] = cr['mut'] + el['earth']
        dyn[6] = cr['card'] + el['air']
        dyn[7] = cr['fix'] + el['water']
        dyn[8] = cr['mut'] + el['fire']
        dyn[9] = cr['card'] + el['earth']
        dyn[10] = cr['fix'] + el['air']
        dyn[11] = cr['mut'] + el['water']
        return dyn

    def dyn_span_diff(self):
        ds = self.signdyn()
        dh = self.housedyn()
        scr = ds['cross']; sel = ds['elem']
        hcr = dh['cross']; hel = dh['elem']
        dyn = [0]*12
        dyn[0] = (hcr['card'] + hel['fire'] ) - ( scr['card'] + sel['fire'])
        dyn[1] = (hcr['fix'] + hel['earth'] ) - ( scr['fix'] + sel['earth'])
        dyn[2] = (hcr['mut'] + hel['air']   ) - ( scr['mut'] + sel['air'])
        dyn[3] = (hcr['card'] + hel['water']) - ( scr['card'] + sel['water'])
        dyn[4] = (hcr['fix'] + hel['fire']  ) - ( scr['fix'] + sel['fire'])
        dyn[5] = (hcr['mut'] + hel['earth'] ) - ( scr['mut'] + sel['earth'])
        dyn[6] = (hcr['card'] + hel['air']  ) - ( scr['card'] + sel['air'])
        dyn[7] = (hcr['fix'] + hel['water'] ) - ( scr['fix'] + sel['water'])
        dyn[8] = (hcr['mut'] + hel['fire']  ) - ( scr['mut'] + sel['fire'])
        dyn[9] = (hcr['card'] + hel['earth']) - ( scr['card'] + sel['earth'])
        dyn[10] =(hcr['fix'] + hel['air']   ) - ( scr['fix'] + sel['air'])
        dyn[11] =(hcr['mut'] + hel['water'] ) - ( scr['mut'] + sel['water'])
        return dyn

##############################################
# Age progression
##############################################

    def house_degree(self):
        degs = []
        for h in self.houses:
            sign = int(h/30)
            degs.append(h - sign * 30)
        return degs
	
    def pl_midpoints(self,plans): #sorted plan
        all_midpoints = []
        for i in range(len(plans)):
            midpoint = plans[(i+1)%11]['degree'] - plans[i]['degree']
            if midpoint < 0: midpoint += 360
            midpoint = plans[i]['degree'] + midpoint/2
            if midpoint > 360: midpoint -= 360
            name = planames[plans[i]['ix']] + "/" + planames[plans[(i+1)%11]['ix']]
            pair = (plans[i]['ix'],plans[(i+1)%11]['ix'])
            for j in range(len(self.houses)):
                h1 = self.houses[j]
                h2 = self.houses[(j+1)%12]
                if h1 > h2:
                    if midpoint < h1 and midpoint < h2: midpoint += 360
                    h2 += 360
                if midpoint > h1 and midpoint < h2:
                    sign = int(midpoint/30)
                    midpoint = midpoint - 30*int(midpoint/30)
                    all_midpoints.append({'degree':midpoint, 'sign':sign,
                        'house':j, 'name':name, 'pair':pair})
                    break
        return all_midpoints

    
    def nodal_pl_midpoints(self,plans):
        house = self.planets[10]
        all_midpoints = []
        
        for i in range(len(plans)):
            midpoint = plans[(i+1)%11]['degree'] - plans[i]['degree']
            if midpoint < 0: midpoint += 360
            midpoint = plans[i]['degree'] + midpoint/2
            if midpoint > 360: midpoint -= 360
            name = planames[plans[i]['ix']] + "/" + planames[plans[(i+1)%11]['ix']]
            pair = (plans[i]['ix'],plans[(i+1)%11]['ix'])
            for j in range(12):
                h1 = house - 30*j
                if h1 < 0: h1 += 360 
                h2 = house - 30*(j+1)
                if h2 < 0: h2 += 360 
                if h1 < h2:
                    if midpoint < h1 and midpoint < h2: midpoint += 360
                    h1 += 360
                if midpoint < h1 and midpoint > h2:
                    sign = int(midpoint/30)
                    midpoint = midpoint - 30*int(midpoint/30)
                    all_midpoints.append({'degree':midpoint, 'sign':sign,
                        'house':j, 'name':name, 'pair':pair })
                    break
        return all_midpoints

    def calc_nodal_agep(self,plan):
        phi = 30*PHI
        pho = 30 - phi
        house = self.planets[10]
        sign = int(house/30)
        house -= sign*30
        ageProg = []
        mids = self.nodal_pl_midpoints(plan)

        for i in range(12):
            events = []
            timeObj = self.house_time_lapsus(i)
            d = timeObj['begin']
            day = str(d.day).rjust(2,'0')
            month = str(d.month).rjust(2,'0')
            year = d.year
            ageProg.append({'day':day, 'mon':month, 'year':year, 'lab':"Cc %s" % str(i+1),
                'cl':'txt_cp'})
            events.append({'scusp':house,'sname': zodnames[(12+sign-1-i)%12],'cl':"sign" })
            events.append({'scusp':phi,'sname': "Pr. %s" % str(i+1),'cl':"pr" })
            events.append({'scusp':pho,'sname': "Pi. %s" % str(i+1),'cl':"pi" })

            for p in plan:
                pl_lg = p["degree"]
                pl_sg = int(pl_lg/30)
                pl_lg = pl_lg - 30*pl_sg
                lg = house -  pl_lg
                if lg <0: 
                    lg += 30 
                    pl_sg += 1
                label = aspnames[(24+sign-pl_sg-i)%12]+"/" + planames[p["ix"]]
                events.append({'scusp':lg,'sname':label,'cl':'asp'})

            for m in mids:
                lg = house - m['degree']
                if lg < 0: lg += 30
                if m['house'] == i:
                    events.append({'scusp':lg,'sname':m['name'],'cl':"mid"})

            events.sort(cmp=evcmp)
            for e in events:
                fac = e['scusp'] / 30
                days = timeObj['lapsus'].days*fac
                dat = timeObj['begin'] + timedelta(days)
                hday = str(dat.day).rjust(2,'0')
                hmonth = str(dat.month).rjust(2,'0')
                hyear = dat.year
                ageProg.append({'day':hday,'mon':hmonth,'year':hyear,'lab':e['sname'],
                    'cl':e['cl']})
        return ageProg
    
    def calc_agep(self,plan,local=False):
        if local:
            oldhouses = self.houses[:]
            self.houses = self.calc_localhouses()
        degs = self.house_degree()
        sizes = self.sizes()
        mids = self.pl_midpoints(plan)
        ageProg = []

        for i in range(12):
            events = []
            timeObj = self.house_time_lapsus(i)
            d = timeObj['begin']
            day = str(d.day).rjust(2,'0')
            month = str(d.month).rjust(2,'0')
            year = d.year
            ageProg.append({'day':day, 'mon':month, 'year':year, 'lab':"Cc %s" % str(i+1),'cl':'txt_cp'})
            house = self.houses[i]
            s = 0; scusp = 30.0 - degs[i]
            sign = int(house/30)
            while scusp < sizes[i]:
                events.append({'scusp':scusp,'sname': zodnames[(sign+1+s)%12],'cl':"sign" })
                s += 1; scusp += s*30

            for m in mids:
                dif = abs(sign - m['sign'])
                lg = m['degree'] + 30*dif - degs[i]
                if lg < 0: lg += 30
                if m['house'] == i:
                    events.append({'scusp':lg,'sname':m['name'],'cl':"mid"})
                   
            for p in plan:
                pl_lg = p["degree"]
                pl_sign = int(pl_lg/30)
                pl_lg = pl_lg - 30*pl_sign
                lg = pl_lg - degs[i]
                if lg < 0: lg += 30 
                c = 0
                while lg + 30*c < sizes[i]:
                    aspsign = int((house+lg+30*c)/30)%12
                    realasp = abs(pl_sign - aspsign)
                    label = aspnames[realasp]+"/" + planames[p["ix"]]
                    events.append({'scusp':lg+30*c,'sname':label,'cl':'asp'})
                    c += 1
                   
            pr = sizes[i]*PHI
            pi = sizes[i]-pr
            events.append({'scusp':pr,'sname':"Pr %s" % str(i+1),'cl':"pr"})
            events.append({'scusp':pi,'sname':"Pi %s" % str(i+1),'cl':"pi"})
            events.sort(cmp=evcmp)
            for e in events:
                fac = e['scusp'] / sizes[i]
                days = timeObj['lapsus'].days*fac
                dat = timeObj['begin'] + timedelta(days)
                hday = str(dat.day).rjust(2,'0')
                hmonth = str(dat.month).rjust(2,'0')
                hyear = dat.year
                ageProg.append({'day':hday,'mon':hmonth,'year':hyear,'lab':e['sname'],
                    'cl':e['cl']})

        if local:
            self.houses = oldhouses[:] 
        return ageProg
    
    def birthday_frac(self):
        date,_,time = self.date.partition('T')
        date = [int(d) for d in reversed(date.split('-'))]
        time = time.split(":")
        day, month, year = date
        hour = int(time[0]); minutes = int(time[1])
        birhdate = datetime(year,month,day,hour,minutes,0)
        byear = datetime(year,1,1,0,0,0)
        eyear = datetime(year+1,1,1,0,0,0)
        ylapsus = eyear - byear
        bdlapsus = birhdate - byear
        return bdlapsus.days/float(ylapsus.days)

    def house_time_lapsus(self,h,playagain=False):
        date,_,time = self.date.partition('T')
        date = [int(d) for d in reversed(date.split('-'))]
        time = time.split(":")
        day, month, year = date
        hour = int(time[0]); minutes = int(time[1])
        if playagain: year += playagain*72
        try:
            bbegin = datetime((year+h*6),month,day,hour,minutes,0)
            eend = datetime((year+(h+1)*6),month,day,hour,minutes,0)
        except ValueError: # leap years
            bbegin = datetime((year+h*6),month,day-1,hour,minutes,0)
            eend = datetime((year+(h+1)*6),month,day-1,hour,minutes,0) 
        lapsus = eend - bbegin
        return { 'begin': bbegin, 'lapsus': lapsus }
    
    def cp_time_lapsus(self,h,off):
        sizes = self.sizes()
        timeObj = self.house_time_lapsus(h)
        off = off /sizes[h]
        days = timeObj['lapsus'].days*off
        d = timeObj['begin'] + timedelta(days) 
        day = d.day
        day = str(day).rjust(2,'0')
        month = d.month
        month = str(month).rjust(2,'0')
        year = str(d.year)
        return "%s.%s.%s" % (day,month,year)

    def which_degree_today(self,now,cycles,kind='radix'):
        for h in range(12):
            t = self.house_time_lapsus(h,playagain=cycles)
            if (now - t['begin']) < t['lapsus']:
                wh = h
                break
        else:
            print now,t['begin'],'playagain'
            for h in range(12):
                t = self.house_time_lapsus(h,playagain=cycles)
                if (now - t['begin']) < t['lapsus']:
                    wh = h; 
                    break
            else:
                wh = 0
        frac = (now - t['begin']).days/float(t['lapsus'].days)
        if kind == 'nodal':
            off = 30*frac
            deg = self.planets[10]-wh*30-off
            if deg < 0: deg += 360
            return  deg
        else:
            off = self.sizes()[wh]*frac
            return (self.houses[wh]+off)%360

    def which_degree_today_simple(self,now,kind='radix'):
        for h in range(12):
            t = self.house_time_lapsus(h)
            if (now - t['begin']) < t['lapsus']:
                wh = h
                break
        else:
            wh = 0
        frac = (now - t['begin']).days/float(t['lapsus'].days)
        if kind == 'nodal':
            off = 30*frac
            deg = self.planets[10]-wh*30-off
            if deg < 0: deg += 360
            return  deg
        else:
            off = self.sizes()[wh]*frac
        return (self.houses[wh]+off)%360

    def when_angle(self,cycles,angle,local=False):
        if local:
            oldhouses = self.houses[:]
            self.houses = self.calc_localhouses()
        h = self.which_house(angle)
        size = self.sizes()[h]
        dif = angle - self.houses[h]
        if dif < 0: dif += 360
        frac = dif / size
        t = self.house_time_lapsus(h,playagain=cycles)
        days = t['lapsus'].days*frac
        delta = timedelta(days=days)
        newdt = t['begin'] + delta
        if local:
            self.houses = oldhouses
        return newdt

    def when_angle_nodal(self,cycles,angle):
        h = self.which_house_nodal(angle)
        size = 30.0
        house0 = self.planets[10]
        hinf = house0 - 30.0 * h
        dif = hinf - angle
        if dif < 0: dif += 360
        frac = dif / size
        t = self.house_time_lapsus(h,playagain=cycles)
        days = t['lapsus'].days*frac
        delta = timedelta(days=days)
        newdt = t['begin'] + delta
        return newdt


######## dynchart
    def cuad_plan(self):
        pl = self.plan_conflicts()
        low = 30 - 30*PHI
        ii = []
        try:
            while pl[-1]['degree'] > (330-low):
                ii.insert(0,pl.pop())
        except IndexError:
            pass
        ind = []
        try:
            while pl[-1]['degree'] > (240-low):
                ind.insert(0,pl.pop())
        except IndexError:
            pass
        you = []
        try:
            while pl[-1]['degree'] > (150-low):
                you.insert(0,pl.pop())
        except IndexError:
            pass
        col = []
        try:
            while pl[-1]['degree'] > (60-low):
                col.insert(0,pl.pop())
        except IndexError:
            pass
        ii = ii+pl
        return (ind,you,col,ii)

    def plan_conflicts(self):
        pl = []
        for i,p in enumerate(self.house_plan_long()):
            pl.append( { 'degree': p, 'ix': i, 'conflict': None } )
        pl = sorted(pl)
        for i in range(len(pl)):
            dif = pl[(i+1)%11]["degree"] - pl[i]["degree"]
            if dif < 0: dif += 360.0 
            if dif <= 6.5:
                pl[i]["conflict"] = pl[(i+1)%11]["conflict"] = True 
        return pl

######## data sheets
    def housepos_and_sector(self):
        zones= [30*x for x in [0.206, 0.412, 0.6847, 0.745, 0.8727, 0.966, 1.0]]
        hspl = self.house_plan_long()
        secs = []
        for i in range(len(hspl)):
            l = hspl[i]
            d = int(l)
            h = int(d/30)
            m = int(60*(l-d))
            ll = l-h*30
            i = 0
            while ll > zones[i]:
                i += 1
                continue
            if i == 6 and h < 11:
                h += 1
            l = d - h*30
            secs.append((l,m,h,(i%6)+1))
        return secs 
    
    def which_all_houses(self):
        hh = []
        sz = self.sizes()
        for h in range(len(self.houses)):
            d = self.houses[h]
            g = sz[h]*PHI 
            l = d + g 
            i = d + sz[h] - g 
            d = self.which_sign(d)
            l = self.which_sign(l)
            i = self.which_sign(i)
            hh.append((d,i,l))
        return hh

    def which_all_signs(self):
        signs = []
        for p in self.planets:
            signs.append(self.which_sign(p))
        return signs

####### biography
    def which_house_today(self,now):
        wh = 0
        wi = 0.5
        cycles = self.get_cycles(now)
        for h in range(12):
            t = self.house_time_lapsus(h,cycles)
            if (now - t['begin']) < t['lapsus']:
                wh = h 
                wi = (now-t['begin']).days/float(t['lapsus'].days)
                break
        return wh,wi

#######
    def rays_calc(self):
        pertab = [ 1, 4, 6, 5, 2] 
        minortab = [6, 7, 5, 4]
        mayortab = [1, 3, 2]
        asc = self.houses[0]
        mc = self.houses[9]
        
        lim1 = asc - int(asc/30) * 30 
        lim2 = mc - int(mc/30) * 30 
        pasc = int(asc/30)%3
        pmc = int(mc/30)%3
        
        rpers = 0 
        if lim1 > 29.0 or lim1 < 1.0 or lim2 > 29.0 or lim2 < 1.0:
            rpers = 7
        else:
            rpers = pasc + pmc
            if rpers == 2 and pasc == pmc:
                rpers = 3
            else:
                rpers = pertab[rpers]

        rays = []
        rays.append(rpers)
        
        asc = int(asc/30)%12
        mc = int(mc/30)%12 
        for i in [0,1,6,7,8,9]:
            pl = int(self.planets[i]/30)%12
            if pl == asc or (pl+6)%12 == asc or pl == mc or (pl+6)%12 == mc:
                rays.append(mayortab[pl%3])
            else:
                rays.append(minortab[pl%4])
        
        nd = int(self.planets[10]/30)%12
        rays.append(mayortab[nd%3])

        return rays 

#############
    def get_cycles(self,nowdt=None): 
        date,_ = parsestrtime(self.date)
        _,_,year = date.split("/")
        if not nowdt:
            nowdt = datetime.now()
        nowyear = nowdt.year
        cycles,_ = divmod(nowyear-int(year),72)
        return cycles

#######
    def calc_house_agep(self,plan,h,local=False):
        if local:
            oldhouses = self.houses[:]
            self.houses = self.calc_localhouses()
        degh = self.house_degree()[h]
        sizeh = self.sizes()[h]
        mids = self.pl_midpoints(plan)
        ageProg = []

        events = []
        cycles = self.get_cycles(boss.get_state().date.dt)
        timeObj = self.house_time_lapsus(h,cycles)
        d = timeObj['begin']
        ageProg.append({'day':d.day,'mon':d.month,'year':d.year,'cl':'txt_cp'})
        
        house = self.houses[h]
        s = 0; scusp = 30.0 - degh
        sign = int(house/30)
        while scusp < sizeh:
            events.append({'scusp':scusp,'sname': (sign+1+s)%12,'cl':"sign" })
            #s += 1; scusp += s*30
            s += 1; scusp += 30
        
        for m in mids:
            dif = abs(sign - m['sign'])
            lg = m['degree'] + 30*dif - degh
            if lg < 0: lg += 30
            if m['house'] == h:
                events.append({'scusp':lg,'sname':m['pair'],'cl':"mid"})
        
        for p in plan:
            pl_lg = p["degree"]
            pl_sign = int(pl_lg/30)
            pl_lg = pl_lg - 30*pl_sign
            lg = pl_lg - degh
            if lg < 0: lg += 30 
            c = 0
            while lg + 30*c < sizeh:
                aspsign = int((house+lg+30*c)/30)%12
                realasp = abs(pl_sign - aspsign)
                label = (realasp,p["ix"])
                events.append({'scusp':lg+30*c,'sname':label,'cl':'asp'})
                c += 1
        
        events.sort(cmp=evcmp)
        for e in events:
            fac = e['scusp'] / sizeh
            days = timeObj['lapsus'].days*fac
            d = timeObj['begin'] + timedelta(days)
            ageProg.append({'day':d.day,'mon':d.month,'year':d.year,'lab':e['sname'], 'cl':e['cl']})

        if local:
            self.houses = oldhouses[:] 
        return ageProg

    def calc_house_nodal_agep(self,plan,h):
        house = self.planets[10]
        sign = int(house/30)
        house -= sign*30
        mids = self.nodal_pl_midpoints(plan)
        ageProg = []

        events = []
        cycles = self.get_cycles(boss.get_state().date.dt)
        timeObj = self.house_time_lapsus(h,cycles)
        d = timeObj['begin']
        ageProg.append({'day':d.day, 'mon':d.month, 'year':d.year, 'cl':'txt_cp'})
        events.append({'scusp':house,'sname': (12+sign-1-h)%12,'cl':"sign" })
        
        for m in mids:
            lg = house - m['degree']
            if lg < 0: lg += 30
            if m['house'] == h:
                events.append({'scusp':lg,'sname':m['pair'],'cl':"mid"})
        
        for p in plan:
            pl_lg = p["degree"]
            pl_sg = int(pl_lg/30)
            pl_lg = pl_lg - 30*pl_sg
            lg = house -  pl_lg
            if lg <0: 
                lg += 30 
                pl_sg += 1
            label = ((24+sign-pl_sg-h)%12,p["ix"])
            events.append({'scusp':lg,'sname':label,'cl':'asp'})

        events.sort(cmp=evcmp)
        for e in events:
            fac = e['scusp'] / 30
            days = timeObj['lapsus'].days*fac
            d = timeObj['begin'] + timedelta(days)
            ageProg.append({'day':d.day,'mon':d.month,'year':d.year,'lab':e['sname'],'cl':e['cl']})
        return ageProg
#######
    def plagram_asp_analysis(self):
        asp = self.aspects()
        colkeys = [0,2,1,0,1,2,0,2,1,0,1,2]
        nasp = [0] * 11
        coleval = []
        for i in range(11):
            coleval.append([0,0,0])
        for a in asp:
            if a["gw"]:
                continue
            f1 = a["f1"]
            f2 = a["f2"]
            if f1 > 1: f1 = 0.95
            if f2 > 1: f2 = 0.95
            f1 =  2-2*f1
            f2 =  2-2*f2

            nasp[a['p1']] += 1
            nasp[a['p2']] += 1
            if a['a'] > 0:
                k = colkeys[a['a']]
                coleval[a['p1']][k] += f1
                coleval[a['p2']][k] += f2
            else:
                for ij,cj in enumerate(conj_class):
                    if (a['p1'],a['p2']) in cj:
                        coleval[a['p1']][ij] += f1
                        coleval[a['p2']][ij] += f2
                        break
        ceval = [ s.index(max(s)) for s in coleval ]
        #ceval = [ (3 - n) % 3 for n in ceval ] # rbg 
        return nasp, ceval

    def plagram_cusps_analysis(self):
        hh = { 'c':[0]*12, 'l': [0]*12 }
        sz = self.sizes()
        for h in range(len(self.houses)):
            c = self.houses[h]
            g = sz[h]*PHI 
            l = c + g 
            c = int(c/30) % 12
            hh['c'][c] += 1
            l = int(l/30) % 12
            hh['l'][l] += 1
        return hh

#######
    def pers_house_force(self):
        hspl = self.house_plan_long()
        pl = []
        for l in [hspl[0], hspl[1], hspl[6]]:
            f = l - int(l)
            p = int(l) % 30 + f
            if p > 22.35: p = 30 - p 
            pl.append(p)
        tups = [(pl[0],"sun"),(pl[1],"moon"),(pl[2],"sat")]
        tups.sort()
        phforce = {}
        for i,t in enumerate(tups):
            phforce[t[1]] = 3 - i
        return phforce
    
    def house_force_all(self):
        hspl = self.house_plan_long()
        n = 30 * PHI
        pl = []
        for l in hspl:
            f = l - int(l)
            p = int(l) % 30 + f
            if p <= n:
                force = n - p
            else:
                force = (p - n) * (PHI+1)
            pl.append(force)
        lw_fac = 3.6 / n
        lw = []
        for w in pl:
            lw.append(w * lw_fac + 1.4)
        return lw
        
    def sign_force_all(self):
        n = 30 - 30*PHI
        fac = n * (PHI - 1)
        sl = self.planets[:]
        pl = []
        for l in sl:
            f = l - int(l)
            p = int(l) % 30 + f
            if p > n:
                p = 2*n - ((p * PHI ) - fac)
            pl.append(p)
        lw_fac = 6.0 / n
        lw = []
        for w in pl:
            lw.append(w * lw_fac + 2.2)
        return lw

    def pers_sign_force(self):
        n = 30 - 30*PHI
        # m = 30*PHI; n/m = PHI
        # (pl-n)*PHI + n =  pl*PHI - n*(PHI - 1)
        fac = n * (PHI - 1)
        sl = self.planets[:]
        pl = []
        for l in [sl[0], sl[1], sl[6]]:
            f = l - int(l)
            p = int(l) % 30 + f
            if p > n:
                p = (p * PHI ) - fac
            pl.append(abs(n-p))
        tups = [(pl[0],"sun"),(pl[1],"moon"),(pl[2],"sat")]
        tups.sort()
        phforce = {}
        for i,t in enumerate(tups):
            phforce[t[1]] = 3 - i
        return phforce

    def pers_aspects_force(self):
        asp = self.aspects()
        pl = [0]*11
        for a in asp:
            if a["gw"]:
                continue
            f1 = a["f1"]
            f2 = a["f2"]
            if f1 > 1: f1 = 0.95
            if f2 > 1: f2 = 0.95
            f1 =  2-2*f1
            f2 =  2-2*f2
            if a["p1"] == 10 or a["p2"] == 10:
                f1 /= 2
                f2 /= 2
            pl[a["p1"]] += f1
            pl[a["p2"]] += f2
        tups = [(pl[0],"sun"),(pl[1],"moon"),(pl[6],"sat")]
        tups.sort()
        phforce = {}
        for i,t in enumerate(tups):
            phforce[t[1]] = i + 1
        return phforce

    def pers_zone_force(self):
        pl = self.house_plan_long()
        sun = abs(270 - pl[0])
        if sun > 180: sun = 360 - sun
        sat = abs(90 - pl[6])
        if sat > 180: sat = 360 - sat
        moon = pl[1]
        if moon > 90 and moon <= 270:
            moon = abs(180 - moon)
        elif moon > 270:
            moon = 360 - moon
        tups = [(sun,"sun"),(moon,"moon"),(sat,"sat")]
        tups.sort()
        phforce = {}
        for i,t in enumerate(tups):
            phforce[t[1]] = 3 - i
        return phforce

    def pers_force(self):
        h = self.pers_house_force()
        s = self.pers_sign_force()
        a = self.pers_aspects_force()
        z = self.pers_zone_force()
        sun = h["sun"]*1.5 + s["sun"] + a["sun"]*0.75 + z["sun"]*0.5
        moon = h["moon"]*1.5 + s["moon"] + a["moon"]*0.75 + z["moon"]*0.5
        sat = h["sat"]*1.5 + s["sat"] + a["sat"]*0.75 + z["sat"]*0.5
        #print h,s,a,z
        return (sun, moon, sat)

#######
def evcmp(a,b):
    ac = a['scusp']; bc = b['scusp']
    if ac == bc: 
        return 0
    elif ac < bc: 
        return -1 
    else: return 1
