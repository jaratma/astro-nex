# -*- coding: utf-8 -*-
'''Database services'''
import sqlite3
from copy import copy
from extensions.path import path
from utils import dectodeg,degtodec
import locale
locale.setlocale(locale.LC_ALL,'')
local_conn = None
chart_conn = None
customloc_conn = None

world_schema = '''
CREATE TABLE custom.%s ( CC Text(2), AC Text(2), Ciudad Text(50), Latitud Text(10), Longitud Text(11))
'''

usa_schema = '''
CREATE TABLE custom.%s ( CC Text(2), AC Text(2), Ciudad Text(50), Latitud Real, Longitud Real )
'''

def connect(app):
    global local_conn, chart_conn, customloc_conn
    dbfile = path.joinpath(app.appath,"astronex/db/local.db")
    local_conn = sqlite3.connect(str(dbfile))
    local_conn.create_collation('westcoll', westerncollate)
    dbfile = path.joinpath(app.home_dir,"charts.db")
    chart_conn = sqlite3.connect(dbfile)
    chart_conn.create_collation('westcoll', westerncollate)
    dbfile = path.joinpath(app.home_dir,"customloc.db")
    #customloc_conn = sqlite3.connect(str(dbfile))
    sql = "attach database '%s' as custom" % (dbfile)
    local_conn.execute(sql)

def easy_connect():
    global local_conn, chart_conn, customloc_conn
    dbfile = "./db/local.db"
    local_conn = sqlite3.connect(str(dbfile))
    local_conn.create_collation('westcoll', westerncollate)
    dbfile = path.joinpath(path.expanduser(path('~')),".astronex/charts.db")
    chart_conn = sqlite3.connect(dbfile)
    chart_conn.create_collation('westcoll', westerncollate)
    dbfile = path.joinpath(path.expanduser(path('~')),".astronex/customloc.db")
    sql = "attach database '%s' as custom" % (dbfile)
    local_conn.execute(sql)


def westerncollate(s1, s2):
    return locale.strcoll(s1,s2)
    #cc1, cc2 = s1, s2
    #trans = [(u'á', 'a'),(u'é', 'e'),(u'í', 'i'),(u'ó', 'o'),(u'ú', 'u') ]
    #for acc in trans:
    #    cc1 = cc1.replace(acc[0], acc[1])
    #    cc2 = cc2.replace(acc[0], acc[1])

    #if cc1 < cc2:
    #    return -1
    #elif cc1 > cc2:
    #    return 1
    #else:
    #    return 0


def save_attached_loc(args):
    country, regcode, city, lat, long, usa = args
    if not usa:
        table =  "cust_" + country.lower()
        schema = world_schema
        insert = "insert into %s  values(:count,:code,:city,:lat,:long)"
    else:
        table = "cust_US" +  country
        schema = usa_schema
        insert = "insert into %s values(:count,:code,:city,:lat,:long)"

    sql = "select name from custom.sqlite_master where type='table'"
    att_tables = []
    for row in local_conn.execute(sql):
        att_tables.append(str(row[0]))
    if table not in att_tables:
        local_conn.execute(schema % table)

    bindings = (country,regcode,city,lat,long)
    local_conn.execute(insert % (table), bindings)
    local_conn.commit()

def fetch_all_from_custom():
    cursor = local_conn.cursor()
    sql = "select name from custom.sqlite_master where type='table'"
    att_tables = []
    for row in local_conn.execute(sql):
        table = str(row[0])
        _,code = table.split('_')
        if code.startswith('US'):
            name = get_name_from_usacode(code[2:])
        else:
            name = get_name_from_code(code)
        att_tables.append((table,name))
    locs = []
    for t,n in att_tables:
        sql = "select Ciudad, AC, Longitud, Latitud from '%s'" % (t)
        for city, ac, lg, lt in cursor.execute(sql):
            locs.append((city, ac,coalesce_geo(lg,lt),t,n))
    locs.sort()
    return locs

def delete_custom_loc(tbl,city,code):
    cursor = local_conn.cursor()
    sql = "delete from '%s' where Ciudad='%s' and AC='%s'" % (tbl,city,code)
    cursor.execute(sql)
    local_conn.commit()


##############################################
# locality services
##############################################
def get_states(usa=False):
    '''list state names '''
    cursor = local_conn.cursor()
    sql = "select code, name from worldnames"
    if usa:
        sql = "select alfa, name from usastates"
    state_names = {}
    for alfa, name in cursor.execute(sql):
        if not usa:
            name = t(name)
        state_names[name] = alfa
    return state_names

def get_states_tuple(usa=False):
    cursor = local_conn.cursor()
    sql = "select code, name from worldnames"
    if usa:
        sql = "select alfa, name from usastates"
    state_names = []
    for alfa, name in cursor.execute(sql):
        if not usa:
            name = t(name)
        state_names.append((name,alfa))
    return state_names

def list_regions(count, usa=False):
    '''list stae region names'''
    cursor = local_conn.cursor()
    tab = 'worldadmin'
    if usa: tab = 'usaadmin'
    sql = "select name, code from %s where alfa='%s' order by name asc" % (tab, count)
    list = []
    for name, code in cursor.execute(sql):
        list.append((name, code))
    return list

def get_name_from_code(code):
    '''Gets country name from its code.'''
    cursor = local_conn.cursor()
    sql = "select name from worldnames where code='%s'" % code.upper()
    cursor.execute(sql)
    return cursor.next()[0]

def get_regionname_from_code(alfa, code):
    '''Gets region name from countryycode and code.'''
    cursor = local_conn.cursor()
    sql = "select name from worldadmin where alfa='%s' and code='%s'" % (alfa, code)
    cursor.execute(sql)
    return cursor.next()[0]

def get_usadistrict_from_code(alfa, code):
    '''Gets region name from countryycode and code.'''
    cursor = local_conn.cursor()
    sql = "select name from usaadmin where alfa='%s' and code='%s'" % (alfa, code)
    cursor.execute(sql)
    return cursor.next()[0]

def get_name_from_usacode(code):
    '''Gets state name from its  code.'''
    cursor = local_conn.cursor()
    sql = "select name from usastates where alfa='%s'" % code.upper()
    cursor.execute(sql)
    return cursor.next()[0]

def get_code_from_name(name):
    '''Gets country code from its name.'''
    cursor = local_conn.cursor()
    sql = "select code from worldnames where name='%s'" % name
    cursor.execute(sql)
    return cursor.next()[0]

def get_usacode_from_name(name):
    '''Gets state alfa code from its name.'''
    cursor = local_conn.cursor()
    sql = "select alfa from usastates where name='%s'" % name
    cursor.execute(sql)
    return cursor.next()[0]

def fetch_all_from_country(country, usa=False):
    '''get cities from country'''
    cursor = local_conn.cursor()
    if not usa:
        main_tab = country
        custom_tab = "cust_" +  country.lower()
    else:
        main_tab = 'US' + country
        custom_tab = "cust_US" +  country

    sql = "select name from custom.sqlite_master where type='table'"
    att_tables = []
    for row in local_conn.execute(sql):
        att_tables.append(str(row[0]))

    sql = "select Ciudad, AC, Longitud, Latitud from '%s' " % (main_tab)
    if custom_tab in att_tables:
        union = " union select Ciudad, AC, Longitud, Latitud from '%s'" % (custom_tab)
    else:
        union = ""
    order = " order by Ciudad asc"
    sql += union + order
    list = []
    for city, ac, lg, lt in cursor.execute(sql):
        list.append((city, ac,coalesce_geo(lg,lt)))

    return list

def coalesce_geo(plg,plt):
    if isinstance(plg,float):
        lg = dectodeg(plg)
        lt = dectodeg(plt)
    else:
        lg = plg.strip()
        lt = plt.strip()

    lg = lg[:-2]
    lt = lt[:-2]

    if lg.startswith('-'):
        lg = lg[1:]
        lg = lg[:-2].rjust(1,'0')+"W"+lg[-2:].rjust(2,'0')
    else:
        lg = lg[:-2].rjust(1,'0')+"E"+lg[-2:]

    if lt.startswith('-'):
        lt = lt[1:]
        lt = lt[:-2].rjust(1,'0')+"S"+lt[-2:].rjust(2,'0')
    else:
        lt = lt[:-2].rjust(1,'0')+"N"+lt[-2:]

    return lg+" "+lt

def fetch_all_from_country_and_region(country, reg, usa=False):
    '''get cities from country and region'''
    cursor = local_conn.cursor()
    tab = ''
    if usa: tab = 'US'
    sql = "select Ciudad, AC from '%s' where AC='%s' order by Ciudad asc" % (tab+country, reg)
    list = []
    for city, ac in cursor.execute(sql):
        list.append((city, ac))
    return list

def fetch_blindly(country, city, loc):
    '''get city data'''
    cursor = local_conn.cursor()
    if ("'") in city:
        city = city.replace("'","''")
    sql = "select CC, AC, Ciudad, Latitud, Longitud from '%s' where Ciudad=='%s'" % (country, city)
    cursor.execute(sql)
    try:
        loc.country_code, loc.region_code, loc.city, loc.latitud, loc.longitud = cursor.next()
    except StopIteration:
        return "localidad no encontrada: %s" % city

    loc.latdec = degtodec(loc.latitud)
    loc.longdec = degtodec(loc.longitud)

    fetch_region(cursor, loc)
    fetch_country(cursor, loc)
    fetch_zone(cursor, loc)
    return loc

def fetch_blindly_usacity(country, city, loc):
    '''get usa city data'''
    cursor = local_conn.cursor()
    sql = "select CC, AC, Ciudad, Latitud, Longitud from US%s where Ciudad == '%s'" % (country, city)
    cursor.execute(sql)
    try:
        loc.country, loc.region_code, loc.city, loc.latdec, loc.longdec = cursor.next()
    except StopIteration:
        return "localidad no encontrada: %s" % city
    loc.latitud = dectodeg(float(loc.latdec))
    loc.longitud = dectodeg(float(loc.longdec))
    sql = "select state, name from usaadmin where alfa == '%s' and code == '%s'" % (loc.country, loc.region_code)
    cursor.execute(sql)
    loc.country_code, loc.region = cursor.next()

    sql = "select name from usastates where alfa == '%s'" % loc.country
    cursor.execute(sql)
    loc.country = cursor.next()[0]
    loc.region += " (" + loc.country + ")"
    loc.country = "USA"

    sql = "select zones, name from zonetab where alfa == 'US'"
    for z, n in cursor.execute(sql):
        zz = z.split(";")
        for code in zz:
            if code.startswith(loc.country_code):
                if len(code) == len(loc.country_code):
                    loc.zone = n
                    break
                code = code[2:]
                if code.startswith('-'):
                    code = code[1:].split(',')
                    if loc.region_code not in code:
                        loc.zone = n
                        break
                else:   # +
                    code = code[1:].split(',')
                    if loc.region_code in code:
                        loc.zone = n
                        break
        if loc.zone:
            break
    return loc


def fetch_blindly_zone_usa(state, cc, loc):
    cursor = local_conn.cursor()
    sql = "select code, name from usaadmin where alfa == '%s' and state == '%s'" % (state, cc)
    for code, reg in cursor.execute(sql):
        loc.region, loc.region_code = reg, code
        break
    sql = "select name from usastates where alfa == '%s'" %  state
    cursor.execute(sql)
    loc.country = cursor.next()[0]
    loc.region += " (" + loc.country + ")"
    loc.country = "USA"
    loc.country_code = cc

    sql = "select zones, name from zonetab where alfa == '%s'" % 'US'
    for z, n in cursor.execute(sql):
        zz = z.split(";")
        for code in zz:
            if code.startswith(loc.country_code):
                if len(code) == len(loc.country_code):
                    loc.zone = n
                    break
                code = code[2:]
                if code.startswith('-'):
                    code = code[1:].split(',')
                    if loc.region_code not in code:
                        loc.zone = n
                        break
                else:   # +
                    code = code[1:].split(',')
                    if loc.region_code in code:
                        loc.zone = n
                        break
        if loc.zone:
            break

def get_usa_state_code(name):
    cursor = local_conn.cursor()
    sql = "select alfa, code from usastates where name='%s'" % name
    cursor.execute(sql)
    return cursor.next()

def fetch_worldcity(country, city, code, loc):
    cursor = local_conn.cursor()
    if ("'") in city:
        city = city.replace("'","''")

    custom_tab = "cust_" +  country.lower()

    sql = "select name from custom.sqlite_master where type='table'"
    att_tables = []
    for row in local_conn.execute(sql):
        att_tables.append(str(row[0]))

    sql = "select CC, AC, Ciudad, Latitud, Longitud from '%s' where Ciudad == '%s' and AC == '%s' " % (country, city, code)

    if custom_tab in att_tables:
        union = " union select CC, AC, Ciudad, Latitud, Longitud from '%s' where Ciudad == '%s' and AC == '%s' " % (custom_tab, city, code)
    else:
        union = ""
    sql += union

    cursor.execute(sql)
    loc.country_code, loc.region_code, loc.city, loc.latitud, loc.longitud = cursor.next()

    loc.latdec = degtodec(loc.latitud.strip())
    loc.longdec = degtodec(loc.longitud.strip())

    fetch_region(cursor, loc)
    fetch_country(cursor, loc)
    fetch_zone(cursor, loc)

def fetch_region(cursor, loc):
    sql = """select name from worldadmin where alfa == '%s' and code == '%s'
    """ % (loc.country_code, loc.region_code)
    cursor.execute(sql)
    loc.region = cursor.next()[0]

def fetch_country(cursor, loc):
    sql = "select name from worldnames where code == '%s'" % loc.country_code
    cursor.execute(sql)
    loc.country = cursor.next()[0]

def fetch_zone(cursor, loc):
    sql = "select zones, name from zonetab where alfa == '%s'" % loc.country_code
    for zone, name in cursor.execute(sql):
        if zone.startswith('*'):
            loc.zone = name
            break
        if zone.startswith('-'):
            nozone = zone[1:].split(',')
            if loc.region_code not in nozone:
                loc.zone = name
                break
        else:
            okzone = zone.split(',')
            if loc.region_code in okzone:
                loc.zone = name
                break

def fetch_blindly_zone(loc):
    cursor = local_conn.cursor()
    sql = """select name, code from worldadmin where alfa='%s'
    """ % (loc.country_code)
    for reg, code in cursor.execute(sql):
        loc.region, loc.region_code = reg, code
        break
    fetch_zone(cursor, loc)

def fetch_usacity(country, city, code, loc):
    cursor = local_conn.cursor()

    custom_tab = "cust_US" +  country

    sql = "select name from custom.sqlite_master where type='table'"
    att_tables = []
    for row in local_conn.execute(sql):
        att_tables.append(str(row[0]))

    sql = "select CC, AC, Ciudad, Latitud, Longitud from US%s where Ciudad == '%s' and AC == '%s'" % (country, city, code)

    if custom_tab in att_tables:
        union = " union select CC, AC, Ciudad, Latitud, Longitud from cust_US%s where Ciudad == '%s' and AC == '%s' " % (country, city, code)
    else:
        union = ""

    sql += union
    cursor.execute(sql)
    loc.country, loc.region_code, loc.city, loc.latdec, loc.longdec = cursor.next()

    loc.latitud = dectodeg(float(loc.latdec))
    loc.longitud = dectodeg(float(loc.longdec))

    sql = "select state, name from usaadmin where alfa == '%s' and code == '%s'" % (loc.country, loc.region_code)
    cursor.execute(sql)
    loc.country_code, loc.region = cursor.next()

    sql = "select name from usastates where alfa == '%s'" % loc.country
    cursor.execute(sql)
    loc.country = cursor.next()[0]
    loc.region += " (" + loc.country + ")"
    loc.country = "USA"

    fetch_zone_usa(cursor, loc)

def fetch_zone_usa(cursor, loc):
    loc.zone = ''
    sql = "select zones, name from zonetab where alfa == 'US'"
    for zones, name in cursor.execute(sql):
        zone = zones.split(";")
        for code in zone:
            if code.startswith(loc.country_code):
                if len(code) == len(loc.country_code):
                    loc.zone = name
                    break
                code = code[2:]
                if code.startswith('-'):
                    code = code[1:].split(',')
                    if loc.region_code not in code:
                        loc.zone = name
                        break
                else:   # +
                    code = code[1:].split(',')
                    if loc.region_code in code:
                        loc.zone = name
                        break
        if loc.zone:
            break

##############################################
# chart services
##############################################

def create_table(tblname):
    cursor = chart_conn.cursor()
    sql = '''drop table if exists "%s"''' % (tblname)
    cursor.execute(sql)
    sql = '''create table "%s" (first Text NOT NULL default '',
    last Text NOT NULL default '',
    category Text NOT NULL default '',
    date Text NOT NULL default '',
    city Text NOT NULL default '',
    region Text NOT NULL default '',
    country Text NOT NULL default '',
    longitud Real NOT NULL default '0.0000000',
    latitud Real NOT NULL default '0.0000000',
    zone Text NOT NULL default '',
    sun Real NOT NULL default '0.0000000',
    moo Real NOT NULL default '0.0000000',
    mer Real NOT NULL default '0.0000000',
    ven Real NOT NULL default '0.0000000',
    mar Real NOT NULL default '0.0000000',
    jup Real NOT NULL default '0.0000000',
    sat Real NOT NULL default '0.0000000',
    ura Real NOT NULL default '0.0000000',
    nep Real NOT NULL default '0.0000000',
    plu Real NOT NULL default '0.0000000',
    nod Real NOT NULL default '0.0000000',
    h1 Real NOT NULL default '0.0000000',
    h2 Real NOT NULL default '0.0000000',
    h3 Real NOT NULL default '0.0000000',
    h4 Real NOT NULL default '0.0000000',
    h5 Real NOT NULL default '0.0000000',
    h6 Real NOT NULL default '0.0000000',
    h7 Real NOT NULL default '0.0000000',
    h8 Real NOT NULL default '0.0000000',
    h9 Real NOT NULL default '0.0000000',
    h10 Real NOT NULL default '0.0000000',
    h11 Real NOT NULL default '0.0000000',
    h12 Real NOT NULL default '0.0000000',
    comment Text NOT NULL default '',
    UNIQUE (first, last))''' % (tblname)
    cursor.execute(sql)

def delete_table(tblname):
    cursor = chart_conn.cursor()
    sql = "drop table if exists %s" % tblname
    cursor.execute(sql)
    chart_conn.commit()

def rename_chart(old, new):
    cursor = chart_conn.cursor()
    sql = 'alter table %s rename to %s' % (old, new)
    cursor.execute(sql)
    chart_conn.commit()

def store_chart(tbl, c):
    cursor = chart_conn.cursor()
    sql = '''insert into %s values(:f,:l,:c,:d,:ct,:r,:cy,:lg,:lt,:z,
            :s,:m,:my,:v,:mr,:j,:st,:u,:n,:p,:nd,
            :h1,:h2,:h3,:h4,:h5,:h6,:h7,:h8,:h9,:h10,:h11,:h12,:cm)''' % tbl
    p = c.planets
    h = c.houses
    bindings = (c.first, c.last, c.category, c.date, c.city, c.region, c.country,
        c.longitud, c.latitud, c.zone, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8],
        p[9], p[10], h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7], h[8], h[9], h[10], h[11],
        c.comment)
    cursor.execute(sql, bindings)
    chart_conn.commit()
    return cursor.lastrowid

def delete_chart(tbl, id):
    cursor = chart_conn.cursor()
    sql = "delete from %s where rowid='%s'" % (tbl, id)
    cursor.execute(sql)
    chart_conn.commit()

def delete_chart_from_name(tbl, fi, la):
    cursor = chart_conn.cursor()
    sql = "delete from %s where first='%s' and last='%s'" % (tbl, fi, la)
    cursor.execute(sql)
    chart_conn.commit()

def load_chart(tbl, id, chart):
    cursor = chart_conn.cursor()
    sql = "select * from %s where rowid='%s'" % (tbl, id)
    ch = cursor.execute(sql).next()
    setchart(chart, ch)

def retrieve_chart(tbl, id, chart):
    cursor = chart_conn.cursor()
    sql = "select * from %s where rowid='%s'" % (tbl, id)
    ch = cursor.execute(sql).next()
    return ch

def retrieve_all_charts(tbl,chart):
    cursor = chart_conn.cursor()
    sql = "select rowid from %s" % (tbl)
    charts = []
    for row in cursor.execute(sql):
        ch = copy(chart)
        load_chart(tbl,row[0],ch)
        charts.append(ch)
    return charts

def load_chart_from_name(tbl, fi, la, chart):
    cursor = chart_conn.cursor()
    sql = "select * from %s where first='%s' and last='%s'" % (tbl, fi, la)
    ch = cursor.execute(sql).next()
    setchart(chart, ch)

def setchart(chart, ch):
    chart.first = ch[0]
    chart.last = ch[1]
    chart.category = ch[2]
    chart.date = ch[3]
    chart.city = ch[4]
    chart.region = ch[5]
    chart.country = ch[6]
    chart.longitud = ch[7]
    chart.latitud = ch[8]
    chart.zone = ch[9]
    chart.planets = list(ch[10:21])
    chart.houses = list(ch[21:33])
    chart.comment = ch[33]

def get_databases():
    cursor = chart_conn.cursor()
    sql = "select tbl_name from sqlite_master where type='table' order by tbl_name"
    tables = []
    for tbl in cursor.execute(sql):
        tables.append(tbl[0])
    return tables

def get_chartlist(tbl):
    cursor = chart_conn.cursor()
    #sql = "select rowid, first, last, category from %s" % tbl
    sql = "select rowid, first, last from %s order by last, first collate westcoll" % tbl
    charts = []
    for row in cursor.execute(sql):
        charts.append(row)
    return charts

def get_favlist(tbl,lim,chart):
    cursor = chart_conn.cursor()
    sql = "select rowid, first, last from %s limit %s" % (tbl,lim)
    charts = []

    for row in cursor.execute(sql):
        ch = copy(chart)
        load_chart(tbl,row[0],ch)
        charts.append(ch)
    return charts

def vacuum():
    cursor = chart_conn.cursor()
    sql = "pragma vacuum"
    cursor.execute(sql)

def get_datum(tbl,datum):
    cursor = chart_conn.cursor()
    sql = "select %s from %s" % (datum,tbl)
    data = []
    for row in cursor.execute(sql):
        data.append(row[0])
    return data

def search_by_name_all_tables(name):
    cursor = chart_conn.cursor()
    sql = "select name from sqlite_master where type='table'"
    tables = []
    for row in cursor.execute(sql):
        table = str(row[0])
        tables.append(table)
    nm = name + "%"
    results = []
    for tbl in tables:
        sql = """select rowid, first, last from %s where first like '%s' or
        last like '%s' order by last, first collate westcoll""" % (tbl,nm,nm)
        for row in cursor.execute(sql):
            results.append([tbl] + list(row))
    return results
