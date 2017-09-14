# -*- coding: utf-8 -*-
import  database
from chart import Chart

def process_zodiac_data():
    data = database.get_datum("personal", "h1")
    zod = [0] * 12

    for d in data:
        z = int(d/30)
        zod[z] +=1

    print zod

def retrieve_charts():
    chart = Chart()
    data = database.retrieve_all_charts("personal",chart)
    return data

def main_survey():
    charts = retrieve_charts()

    suns = [0] * 12
    moons = [0] * 12
    sats = [0] * 12
    ascs = [0] * 12

    for ch in charts:
        suns[int(ch.planets[0]/30)] += 1
        moons[int(ch.planets[1]/30)] += 1
        sats[int(ch.planets[6]/30)] += 1
        ascs[int(ch.houses[0]/30)] += 1

    print suns
    print moons
    print sats
    print ascs

    



