# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 17:36:10 2021

@author: Qilin Zhang
"""


import xlrd
from processing_construction import ProcessCons
from processing_climate import ProcessClimate
from processing_traffic import ProcessTraffic
from processing_iri import ProcessIRI
from datetime import datetime
from xlrd import xldate_as_tuple

# merra_id , state_code, shrp_id matching
def Trans():
    filename = 'Bucket_96806/Bucket_96806.xls'
    workbook = xlrd.open_workbook_xls(filename)
    sheet1 = workbook.sheet_by_name('LTPP_Section_Reference')
    rows = sheet1.nrows
    cols = sheet1.ncols
    trans = []  
          
    for i in range(1,rows):
        data1 = []
        for j in range(cols):
            ctype = sheet1.cell(i, j).ctype  
            cell = sheet1.cell_value(i, j)
            if ctype == 2 and cell % 1 == 0:  
                cell = int(cell)
            elif ctype == 3:
                # datetime
                date = datetime(*xldate_as_tuple(cell, 0))
                cell = date.strftime('%Y')
            elif ctype == 4:
                cell = True if cell == 1 else False
            data1.append(cell)
        trans.append(data1)    
        
    return trans

# Climate fusion
def ClimateFusion():
    out_precip = ProcessClimate('MERRA_PRECIP_YEAR')
    out_temp = ProcessClimate('MERRA_TEMP_YEAR')
    out_wind = ProcessClimate('MERRA_WIND_YEAR')
    out_humid = ProcessClimate('MERRA_HUMID_YEAR')
    out_solar = ProcessClimate('MERRA_SOLAR_YEAR')
    
    out_climate = []
    for (i1,i2,i3,i4,i5) in zip(out_precip,out_temp,out_wind,out_humid,out_solar):
        o1 = []
        o2 = []
        for (j1,j2,j3,j4,j5) in zip(i1,i2,i3,i4,i5):
            o1 = [j1[0],j1[1],j1[2],j1[3],j2[3],j2[4],j2[5],j3[2],j4[2],j5[2],j5[3]]
            o2.append(o1)
        out_climate.append(o2)
    return out_climate

# matching out_iri, out_cons, out_trf, out_climate

def OutFusion(out_iri, out_trf, out_climate, trans, out_cons):
    
    # iri and construction matching
    section = []
    for i, j in zip(out_iri, out_cons):
        year = []
        for i1, j1 in zip(i, j):
            year.append([i1[0],i1[1],i1[2],i1[3],j1[3]])
        section.append(year)    
    
    # iri 与traffic matching
    k = []
    for i in section:
        k1 = []
        for i1 in i:
            for j in out_trf:
                for j1 in j:
                    if (str(i1[0]) == str (j1[2]) and int(i1[1]) == int(j1[0]) and str(i1[2]) == str(j1[1])):
                        k2 = [i1[0],i1[1],i1[2],i1[3],i1[4],j1[3],j1[4],j1[5],j1[6]]
                        k1.append(k2)
        k.append(k1)
           
    # matching climate
    out = []
    for i in k:
        out1 = []
        for i1 in i:
            for t in trans:
                if (i1[1] == t[1] and i1[2] == (t[2])): 
                    for c in out_climate:
                        for c1 in c:
                            if ((t[0]) == c1[0] and int(i1[0]) == c1[1]): 
                                
                                out2 = [i1[0],i1[1],i1[2],i1[3],i1[4],i1[5],i1[6],i1[7],i1[8],c1[2],c1[3],c1[4],c1[5],c1[6],c1[7],c1[8],c1[9],c1[10]]
                                #print(out2)
                                out1.append(out2)
        out.append(out1)
       
    # discard null
    out_final = []
    for i in out:
        if i != []:
            out_final.append(i)
           
    # discard year, state, section
    out_figure = []
    for i in out_final:
        index = []
        for j in i:
            del j[2]
            del j[1]
            del j[0]
            index.append((j))
        out_figure.append((index)) 
        
    return out_final

# Construction
out_cons = ProcessCons()

# Climate
out_climate = ClimateFusion()

# Traffic
out_trf = ProcessTraffic('TRF_TREND')

# IRI
out_iri = ProcessIRI('MON_HSS_PROFILE_SECTION')


trans = Trans()


out_final = OutFusion(out_iri, out_trf, out_climate, trans, out_cons)

  
    
