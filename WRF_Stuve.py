#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author:   Thorsten Beisiegel, info@meteocolombia.com.co
# Version 1.0, June 2015
# Feel free to debug or modify this version for your own purposes preserving this note 
###############################################################################
# Copyright (c) 2015, Meteocolombia S.A.S. (www.meteocolombia.com.co)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This programme is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import locale 
import gettext
# mkdir ./de/LC_MESSAGES
# marcar mensajes
# xgettext WRF_Stuve.py
# Corregir CHARSET=UTF-8
# msgfmt messages.po 
# mv messages.mo ./de/LC_MESSAGES
try:
    current_locale, encoding = locale.getdefaultlocale()
    print current_locale
    if 'es' in current_locale: idiom='es'
    elif 'pt' in current_locale: idiom='pt'
    elif current_locale=='de': idiom='de'
    else:  idiom='en'
except:
    idiom='en'
mensajes=gettext.translation('mensajes', localedir='./',languages=[idiom])
mensajes.install()

def namelist():
# Lee parametros del usuario sobre ubicacion archivos WRF, estacion radiosondeo
# y fechas desde el archivo "namelist"  
 
    nml=open('namelist','r')
    params={}
    for linea in nml.readlines():
	if '#' not in linea:
            try:     
		linea=linea.split('=')
	        params[linea[0].rstrip(' ').lstrip(' ')]=linea[1].rstrip('\n').rstrip(' ').lstrip(' ')
            except:
		print _('línea errónea en namelist:'),linea 
    ianho,imes,idia,ihora=int(params['ianho']),int(params['imes']),int(params['idia']),int(params['ihora'])
    eanho,emes,edia,ehora=int(params['eanho']),int(params['emes']),int(params['edia']),int(params['ehora'])
    dh=int(params['dh'])
    codigo=int(params['codigo'])
    ruta=params['ruta']

    return ianho,imes,idia,ihora,eanho,emes,edia,ehora,dh,codigo,ruta 

def ll_xy(lat0,lon0,archivo):

# Punto de grilla mas cercano a (lat,lon)
    import os
    from scipy import io

    lat0=float(lat0)
    lon0=float(lon0)
#    print 'ncrcat -O -v XLAT,XLONG -d Time,0 '+archivo+' lonlat.nc'
    os.system('ncrcat -O -v XLAT,XLONG -d Time,0 '+archivo+' lonlat.nc')   
    ll=io.netcdf.netcdf_file('lonlat.nc', 'r') 
    lat=ll.variables['XLAT'][0]
    lon=ll.variables['XLONG'][0]
    #il <-> lat s-n = y
    for il in range(1,len(lat)):
        #jl <-> lon w-e = x
        for jl in range(1,len(lon[il])):
	    if lat[il][jl]>lat0 and lat[il-1][jl]<lat0:
	        if lon[il][jl]>lon0 and lon[il][jl-1]<lon0:
                    dlat=lat[il][jl]-lat[il-1][jl]
	            dlon=lon[il][jl]-lon[il][jl-1]
                    nxmin=jl-1
                    nymin=il-1
 		    if lat[il][jl]<lat0+dlat/2.: nymin=il
                    if lon[il][jl]<lon0+dlon/2.: nxmin=jl
                    break
    print _('Punto WRF | Obs:'),nxmin,nymin,lon[nymin][nxmin],lat[nymin][nxmin],'|',lon0,lat0
    return nxmin,nymin		


def wrfout(lat0,lon0,fecha,wfecha,ruta):
# Extrae datos en altura simulados para ubicacion del radiosondeo
# Se utiliza ncrcat para minimizar los archivos .nc entes de procesarlos
# En caso de no contar con nco reemplazar ncrcat por io.netcdf.netcdf_file()
# para cargar el archivo completo

    from scipy import io
    from datetime import datetime,timedelta
    from math import log,exp
    import os,glob

    eslcon2=29.65
    eslcon1=17.67
    ezero=611.2  # Pa     # =30.0 mb - 35.0 mb
    celkel=273.15
    eps=0.622
    rcp=287./1004.

#    archivo=datetime.strftime(fecha,ruta+"%Y/%m/wrfout_d03_%Y-%m-%d_%H:00:*")
    archivo=datetime.strftime(wfecha,ruta+"/wrfout*%Y-%m-%d_%H:00*")
    archivo=glob.glob(archivo)[0]
    print _('Archivo WRF:'),archivo

    nxmin,nymin=ll_xy(lat0,lon0,archivo)		

    os.system('ncrcat -O -v Times,XLAT '+archivo+' tiempos.nc')
    t=io.netcdf.netcdf_file('tiempos.nc', 'r')
    paso=0
    # Busca fecha y hora del radiosondeo (=fecha) dentro del archivo WRF
    data=False
    for times in t.variables['Times']:
        ts=''
	for tc in times: ts=ts+tc 
	tt=datetime.strptime(ts,"%Y-%m-%d_%H:%M:%S")
        if fecha==tt:
            data=True
            print _('sondeo WRF:'),fecha 
 	    break
        paso=paso+1

    hgt=[]
    prs=[]
    td=[]
    tc=[]
    hr=[]
    qv=[]
    if data:   
#        print 'ncrcat -O -v PSFC,Q2,T2,HGT,PB,P,PH,PHB,T,QVAPOR,Times -d west_east,'+str(nxmin)+' -d south_north,'+str(nymin)+' -d bottom_top,0,26 -d Time,'+str(paso)+' '+archivo+' wrftmp.nc'
        os.system('ncrcat -O -v PSFC,Q2,T2,HGT,PB,P,PH,PHB,T,QVAPOR,Times -d west_east,'+str(nxmin)+' -d south_north,'+str(nymin)+' -d bottom_top,0,26 -d Time,'+str(paso)+' '+archivo+' wrftmp.nc')
    # Sin nco: Comentar linea superior y cambiar en la siguiente 'wrftmp.nc' por "archivo".
        a=io.netcdf.netcdf_file('wrftmp.nc', 'r')
        p=a.variables['P'][0]
        pb=a.variables['PB'][0]
        ph=a.variables['PH'][0]
        phb=a.variables['PHB'][0]
        tp=a.variables['T'][0]
        qvl=a.variables['QVAPOR'][0]
        hsfc=a.variables['HGT'][0]
        psfc=a.variables['PSFC'][0]
        q2=a.variables['Q2'][0]
        t2=a.variables['T2'][0]
        #superficie
        prs.append(psfc)
        ev=psfc*q2/(0.622+q2) #Pa
        td.append((eslcon2*log(ev/ezero)-eslcon1*celkel) / (log(ev/ezero)-eslcon1) - 273.16)
        tc.append(t2-273.16)
        es=611.2*exp(eslcon1*(t2-celkel)/(t2-eslcon2)) #Pa,t2(K)
        hr.append((ev/es)*100.)
        hgt.append(hsfc)
        qv.append(q2)
        for i in range(len(qvl)): qv.append(qvl[i])
        print _('Altura Superf. WRF:'),float(hsfc)
        for lev in range(1,len(p)):
            hgt.append((phb[lev]+ph[lev])/9.81)
            prs.append(pb[lev]+p[lev]) #Pa
            ev=prs[lev]*qv[lev]/(0.622+qv[lev]) #Pa	
            td.append((eslcon2*log(ev/ezero)-eslcon1*celkel) / (log(ev/ezero)-eslcon1) - 273.16)
            tc.append((tp[lev]+300.)*pow((prs[lev]/100000.),rcp*(1.-0.251*qv[lev])) - 273.16) # prs(Pa),tp(K),tc(C)
            if td[lev]>tc[lev]: print td[lev],'>',tc[lev]
            es=611.2*exp(eslcon1*tc[lev]/(tc[lev]+celkel-eslcon2)) #Pa,tc(C)
            hr.append((ev/es)*100.)

    return prs,hgt,tc,td,hr,qv,data

def wget(anho,mes,dia,hora,codigo):
# Descarga radiosondeos desde wyoming con wget. 
# Lee sondeo e indicadores de estabilidad atmosferica desde el archivo de texto descargado 
  
    import os

    lp=7
    
    anho=str(anho)
    mes=str(mes).rjust(2,'0')
    diahora=str(dia)+str(hora)
    codigo=str(codigo)
    nome=str(codigo)+'_'+mes+'_'+diahora+'Z'
    oprs=[]
    ohgt=[]
    otc=[]
    otd=[]
    ohr=[]
    oqv=[]

    os.system('wget -c -O '+nome+' "http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+anho+'&MONTH='+mes+'&FROM='+diahora+'&TO='+diahora+'&STNM='+codigo+'" > /dev/null')
#    print 'wget -c -O '+nome+' "http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+anho+'&MONTH='+mes+'&FROM='+diahora+'&TO='+diahora+'&STNM='+codigo+'"'
    obs=open(nome,'r')
    indices={}
    for linea in obs.readlines():
      try:
    	var=[linea[0+i:lp+i] for i in range(0,len(linea),lp)]
        #En vez de usar expr regulares se convierte a float. Si no es numero sigue a la siguiente linea:
        prs=float(var[0])
        hgt=int(var[1])
        tc=float(var[2])
        td=float(var[3])
        hr=float(var[4])
        qv=float(var[5])
        oprs.append(prs)
    	ohgt.append(hgt)	
    	otc.append(tc)
    	otd.append(td)
    	ohr.append(hr)
    	oqv.append(qv*1000.)
      except:
        if 'Station latitude' in linea: lat=linea.split(':')[1].rstrip('\n')
        elif 'Station longitude' in linea: lon=linea.split(':')[1].rstrip('\n')
        elif 'Lifted index' in linea: indices['lift']=linea.split(':')[1].rstrip('\n') 
	elif 'Convective Available Potential Energy' in linea: indices['cape']=linea.split(':')[1].rstrip('\n')
        elif 'Temp [K] of the Lifted Condensation Level' in linea: indices['tlcl']=str(float(linea.split(':')[1])-273.16)
        elif 'Pres [hPa] of the Lifted Condensation Level' in linea: indices['plcl']=linea.split(':')[1].rstrip('\n')
        elif 'Level of Free Convection' in linea: indices['plfc']=linea.split(':')[1].rstrip('\n')  
	elif 'Mean mixed layer mixing ratio' in linea: indices['mlmr']=linea.split(':')[1].rstrip('\n')
	continue	

    return oprs,ohgt,otc,otd,ohr,oqv,indices,lat,lon

def cape(oprs,ohgt,otc,otd,ohr,oqv):
# Integra Cape a lo largo del radiosondeo simulado:
# tca temperatura ascenso adiabatico y pseudoadiabatico
# tas temperatura ascenso adiabatico seco
# qvc Razon de mezcla promedia (sfc - 500m)
# tda Punto de rocio con qv=const=qvc
# es  presion de saturacion con qv ambiente
# ev  presion de vapor con qv ambiente
# evc presione de vapor qv=qvc
#dtah gradiente adiabatico humedo
# c1  dhgt entre lev-1 y punto de cruce


    from math import log,exp

    eslcon2=29.65
    eslcon1=17.67
    ezero=611.2  #Pa     # =30.0 mb - 35.0 mb
    celkel=273.15
    eps=0.622
    alfa=1004./287.
    xlv=2.4522e6    

    cap=0.
    tlcl=-9999.
    hlcl=-9999.
    plcl=-9999.
    tlfc=-9999.
    hlfc=-9999.
    plfc=-9999.
    tlnb=-9999.
    hlnb=-9999.
    plnb=-9999.
    tca=[]
    tda=[]    
    top=min(len(oprs),len(otc),len(otd),len(ohr),len(oqv))
    qvc=oqv[0]
#    tda=9999.
    tas=9999.
    tca.append(otc[0])
    tda.append(otd[0])
    qsum=oqv[0]
    for lev in range(1,top):
        dz=ohgt[lev]-ohgt[lev-1]
	#ascenso adiabatico seco
        task0=tas
	tas=(otc[0]+celkel)*pow((oprs[lev]/oprs[0]),(1/alfa))-celkel          # gradC
#	tas=otc[0]-9.81/1004.*dz                                          # gradC
	tca.append(tas)                                                   # gradC
	#TD ascenso adiabatico con qvc=avg(qv(500m)):        
	es=611.2*exp(eslcon1*(otc[lev])/(otc[lev]+celkel-eslcon2))        # Pa
    	qs=0.622*es/(oprs[lev]-es)                                        # kg/kg 
	ev=oqv[lev]*oprs[lev]/(eps+oqv[lev])                              # Pa
    	tv=otc[lev]/(1-ev/oprs[lev]*(1-eps)) + celkel                     # Kelvin
	if (ohgt[lev]-ohgt[0]) <= 500.:
	    qsum=qsum+oqv[lev]
	    qvc=qsum/(lev+1)                                              # kg/kg
	evc=oprs[lev]*qvc/(eps+qvc)                                       # Pa                                  
    	tda.append((eslcon1*celkel-eslcon2*log(evc/ezero)) / (eslcon1-log(evc/ezero)) - 273.16)
        #LCL:
        if tda[lev] >= tas:
	    if tda[lev-1] < task0:
		rdt= (tca[lev-1]-tda[lev-1])/(tda[lev]-tca[lev])
		c1=rdt*dz/(1+rdt)
                hlcl=ohgt[lev-1]+c1
		tlcl=c1/dz*(tca[lev]-tca[lev-1])+tca[lev-1]
		plcl=c1/dz*(oprs[lev]-oprs[lev-1])+oprs[lev-1]
	    #ascenso adiabatico humedo
		tk=tca[lev-1]+celkel
		dtah=-9.81/1004. * (1.+ xlv*qs/(287.*tk)) / (1+ xlv*xlv*eps*qs/(287.*1004.*tk*tv))
		tca[lev]=tlcl+dtah*(ohgt[lev]-hlcl)
	    else:
	    	dtah=-9.81/1004. * (1.+ xlv*qs/(287.*tk)) / (1+ xlv*xlv*eps*qs/(287.*1004.*tk*tv))
            	tca[lev]=tca[lev-1]+dtah*(ohgt[lev]-ohgt[lev-1])

#caso I): \|
#          |\
            if tca[lev] >= otc[lev] and tca[lev-1] < otc[lev-1]:
		rdt=(otc[lev-1]-tca[lev-1])/(tca[lev]-otc[lev])
		c1=rdt*dz/(1+rdt)
		hlfc=ohgt[lev-1]+c1
		tlfc=otc[lev]+dtah*c1
		plfc=c1/dz*(oprs[lev]-oprs[lev-1])+oprs[lev-1]
		cap=cap+(((tlfc-otc[lev]))*(dz-c1)/2) - ((tlfc-tca[lev])*(dz-c1)/2)
                cap=cap*2./max((otc[lev-1]+otc[lev]+celkel),1.e-12)
#caso II): \ \
#           \ \
            elif tca[lev] >= otc[lev] and tca[lev-1] > otc[lev-1]:
		cap=cap+(tca[lev-1]-otc[lev])*dz + (otc[lev]-otc[lev-1])*dz/2 - (tca[lev-1]-tca[lev])*dz/2
                cap=cap*2./max((otc[lev-1]+otc[lev]+celkel),1.e-12)
#caso III): _\__
#             \
            elif tca[lev] < otc[lev] and tca[lev-1] >= otc[lev-1]:
                rdt=(tca[lev-1]-otc[lev-1])/(otc[lev]-tca[lev])
                c1=rdt*dz/(1+rdt)
                hlnb=ohgt[lev-1]+c1
                tlnb=otc[lev-1]+dtah*c1
                plnb=c1/dz*(oprs[lev]-oprs[lev-1])+oprs[lev-1]
                cap=cap+((tca[lev-1]-tlnb)*c1/2) - ((otc[lev-1]-tlnb)*c1/2)
                cap=cap*2./max((otc[lev-1]+otc[lev]+celkel),1.e-12)

            if oprs[lev] < 50000 and oprs[lev-1] > 50000:
                ts500 = tca[lev-1]-((oprs[lev-1]-50000)/(oprs[lev-1]-oprs[lev]))*(tca[lev-1]-tca[lev])
                ta500 = otc[lev-1]-((oprs[lev-1]-50000)/(oprs[lev-1]-oprs[lev]))*(otc[lev-1]-otc[lev])
                lift = ts500 - ta500
            
    print 'MLMR',float(qvc)*1000.
    print 'CAPE',float(cap)
    print 'LIFT',float(lift)
    print 'HLCL',float(hlcl)
    print 'TLCL',float(tlcl)
    print 'PLCL',float(plcl)/100.
    print 'HLFC',float(hlfc)
    print 'TLFC',float(tlfc)
    print 'PLFC',float(plfc)/100.
    print 'HLNB',float(hlnb)
    print 'TLNB',float(tlnb)
    print 'PLNB',float(plnb)

    indices={}
    indices['mlmr']=float(qvc)*1000.
    indices['cape']=float(cap)
    indices['lift']=float(lift)
    indices['hlcl']=float(hlcl)
    indices['tlcl']=float(tlcl)
    indices['plcl']=float(plcl)/100.
    indices['hlfc']=float(hlfc)
    indices['tlfc']=float(tlfc)
    indices['plfc']=float(plfc)/100.
    indices['hlnb']=float(hlnb)
    indices['tlnb']=float(tlnb)
    indices['plnb']=float(plnb)
    
	
    return oprs,ohgt,otc,otd,tca,tda,indices

def stuve(oprs,ohgt,otc,otd,tca,tda,sprs,stc,std,shgt,nome):
# Grafica con matplotlib radiosondeo observado y simulado en una solo grafica 

    from matplotlib import pyplot as plt, ticker
  
    prs=[]
    hgt=[]
    tc=[]
    td=[]
    ta=[]
    tdc=[]
    for lev in range(len(oprs)):
	prs.append(float(oprs[lev])/100.)      #mb
        hgt.append(float(ohgt[lev]))
	tc.append(float(otc[lev]))
	td.append(float(otd[lev]))
	ta.append(float(tca[lev]))
        tdc.append(float(tda[lev]))
    tmin=-100
    tmax=50
    limit=ticker.FixedLocator(range(tmin,tmax,10))
    fig, ax1 = plt.subplots()
    ax1.xaxis.set_major_locator(limit)
    ax1.set_xlim(tmin,tmax)
    ax1.set_ylim(min(hgt),max(hgt))
    ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter("%5.0fm"))

    # 2. y-axis con presion en mb
    #Se usa set_yticks() y set_yticklabels() en vez de ticker. ..
    stnivel,p0=phoriz(tc,prs,hgt)
    stnivel.sort()
    ax2=ax1.twinx()
    ax2.set_xlim(tmin,tmax)
    ax2.set_ylim(min(hgt),max(hgt))
    ax2.spines['right'].set_position(('axes', 0.0))
    sp0=[]
    ax2.set_yticks(stnivel)
    for i in range(len(p0)): p0[i]=str(p0[i])+'mb'
    ax2.set_yticklabels(p0)

    # Los sondeos:
    ax1.plot(tc, hgt, 'b-', td, hgt,'r-', ta, hgt, 'y-', tdc, hgt, 'g-', stc, shgt,'0.5', std, shgt,'0.3')

    # El diagrama de Stueve:
    # Niveles de presion estandar: 
    stnivel,p0=phoriz(tc,prs,hgt)
    for hh in stnivel: ax1.axhline(y=hh, xmin=min(td), xmax=max(tc), linewidth=0.5, color = 'b', alpha=0.5)
    # Adiabaticos secos:
    for ts in aas(prs[0],hgt,tc).values(): ax1.plot(ts, hgt, linewidth=0.5, color='g', alpha=0.5)    
    # Punto Rocio constante:
    for prc in prconst(prs).values(): ax1.plot(prc, hgt, '--', linewidth=0.5, color='r', alpha=0.5)    
    # Adiabaticos humedos
    for th in aah(prs,hgt).values(): ax1.plot(th, hgt, linewidth=0.5, color='r', alpha=0.5) 
#    plt.show()
    plt.savefig(nome) 

def aas(p0,hgt,tc):
# Ascenso adiabatico seco
    from math import exp
 
    Rcp=287./1004.
    taas={}
    tmin=int(min(tc)/10.)*10
    tmax=int(max(tc)/10.)*10+10
    for t0 in range(-50,100,10):
        pp0=p0
        taas[t0]=[]
        taas[t0].append(float(t0))
        tkn=float(t0)+273.16
    	for lev in range(1,len(hgt)):
	    hprs=pp0*exp(-(hgt[lev]-hgt[lev-1])*9.81/(287.*tkn))
	    tkn=(t0+273.16)*pow((hprs/1000.),Rcp)
    	    taas[t0].append(tkn-273.16)
            pp0=hprs
    return taas

def aah(prs,hgt):
# Ascenso adiabatico humedo
    from math import exp

    eslcon2=29.65
    eslcon1=17.67
    celkel=273.15
    eps=0.622
    xlv=2.4522e6

    qvc=[0.1+i/10. for i in range(10)]+[1.2,1.6,2.,2.5,3.,3.5,4.,4.5,]+range(5,20)+range(20,30,4)+[30,35,40] #g/kg
    taah={}
    for qv in qvc:
        taah[qv]=[]
        prc=prconst(prs)
        tk=prc[qv][0] +celkel
        taah[qv].append(tk-celkel)
    	for lev in range(1,len(hgt)):
            pp=prs[lev]*100.
            es=611.2*exp(eslcon1*(tk-celkel)/(tk-eslcon2))        # Pa
            qs=0.622*es/(pp-es)                                        # kg/kg
            tv=tk/(1-es/pp*(1-eps)) 
    	    dtah=-9.81/1004. * (1.+ xlv*qs/(287.*tk)) / (1+ xlv*xlv*eps*qs/(287.*1004.*tk*tv))
            tk=tk+dtah*(hgt[lev]-hgt[lev-1])
	    taah[qv].append(tk-celkel)        
    return taah

def prconst(prs):    
# Punto de rocio en altura con qv=qvc constante
# Utilizado para el diagrama Stuve

    from math import log 

    eslcon2=29.65
    eslcon1=17.67
    ezero=6.112 # hPa      # =30.0 mb - 35.0 mb
    celkel=273.15
    eps=0.622
    alfa=1004./287.
    xlv=2.4522e6

    qvc=[0.1+i/10. for i in range(10)]+[1.2,1.4,1.6,1.8,2.,2.5,3.,3.5,4.,4.5,]+range(5,20)+range(20,30,2)+[30,35,40] #g/kg
    tdas={}
    for qv in qvc:
        tdas[qv]=[]
	for pp in prs:
	    evc=pp*qv*.001/(eps+qv*.001)  #mb
	    tda=(eslcon1*celkel-eslcon2*log(evc/ezero)) / (eslcon1-log(evc/ezero)) - 273.16
	    tdas[qv].append(tda)
    return tdas	

def phoriz(tc,prs,hgt):
# Niveles de presion mandatorios 

    from math import log

    p0=range(1000,0,-50)
    hpl={}
    pn=[]
    for pl in p0:    
    	for lev in range(1,len(tc)):
	    if prs[lev-1] > pl and prs[lev] < pl:
		hpl[pl]=hgt[lev-1]+log(prs[lev-1]/pl)*287.*(tc[lev]+273.16)/9.81
		pn.append(pl)
	        break
    return hpl.values(),pn 

def main():
	
    from datetime import datetime,timedelta
    import re,glob

    ianho,imes,idia,ihora,eanho,emes,edia,ehora,dh,codigo,ruta=namelist()

    ifecha=datetime(ianho,imes,idia,ihora)
    efecha=datetime(eanho,emes,edia,ehora)
    fecha=ifecha
    wfecha=ifecha
    while fecha <= efecha:
        print _('Sondeo'),codigo,fecha
    	anho=fecha.year
    	mes=fecha.month
    	dia=fecha.day
    	hora=fecha.hour
	nfecha=[]
        for wfile in glob.glob(ruta+'/wrfout*'):
            a=re.search("\d{4}-\d{2}-\d{2}_\d{2}",wfile)
            if a==None: 
		print _('Nombre del archivo %s no cumple formato de fecha'%wfile)
	        continue	
	    nfecha.append(datetime.strptime(a.group(0),"%Y-%m-%d_%H"))
        nfecha.sort()
        for nf in range(len(nfecha)-1):
            if nfecha[nf+1] > fecha and nfecha[nf] <= fecha:
                #procesa el archivo anterior:
                wfecha=nfecha[nf]
		print _('Procesando archivo '),wfecha 
		break
        #Si la fecha coincide con el ultimo archivo:
        nf=len(nfecha)-1
        if nfecha[nf] == fecha:
	    wfecha=nfecha[nf]
            print _('Procesando archivo '),wfecha
        sounding=str(codigo)+fecha.strftime("_%d.%m.csv")
        sprs,shgt,stc,std,shr,sqv,sindices,lat,lon=wget(anho,mes,dia,hora,codigo)
	oprs,ohgt,otc,otd,ohr,oqv,data=wrfout(lat,lon,fecha,wfecha,ruta)
        if data:
            oprs,ohgt,otc,otd,tca,tda,windices=cape(oprs,ohgt,otc,otd,ohr,oqv)	
            # La tabla de los indices
            indices=open(sounding,'w')
            for ii in windices.keys():
                 if ii in sindices.keys(): 
                    indices.write(str(ii)+';'+str(windices[ii])+';'+str(sindices[ii])+'\n') 
                 else:
                    indices.write(str(ii)+';'+str(windices[ii])+'; \n')
            nome=sounding[:-3]+'png'
            stuve(oprs,ohgt,otc,otd,tca,tda,sprs,stc,std,shgt,nome)
        else:
	    print _('No hay datos WRF para la fecha'),fecha,'\n'
	fecha=fecha+timedelta(hours=dh)

if __name__ == "__main__":
    main()

