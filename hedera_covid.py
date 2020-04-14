#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 19:48:10 2020

@author: caiazzo
"""

# +
# Preliminaries
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

class DataHandlerBerlin:
    def __init__(self,path=None):
        if path==None:
            path = '/Users/caiazzo/HEDERA/CODES/covid-19-toolkit/DE-Data/data-fIw01.csv'
        self.data = pd.read_csv(path)
        self.data.columns = ['dates','confirmed','stationary','intensive','deaths']
        
        N = len(self.data['dates'])
        dates = []
        for d in self.data['dates']:
            dt = datetime.datetime(int(d[6:10]),int(d[3:5]),int(d[0:2]))
            dates.append(dt.strftime('%d %b'))
        self.data['dates']=dates
        confirmed_daily = []
        deaths_daily = []
        
        confirmed_daily.append(0)
        deaths_daily.append(0)

        for i in range(0,N-1):
            confirmed_daily.append(self.data['confirmed'][i+1]-
                                   self.data['confirmed'][i])
            deaths_daily.append(self.data['deaths'][i+1]-
                                self.data['deaths'][i])
            
        self.data['confirmed_daily'] = confirmed_daily
        self.data['deaths_daily'] = deaths_daily


class DataHandlerItaly:
    def __init__(self,path=None):
        if path==None:
            path = '/Users/caiazzo/HEDERA/CODES/covid-19-toolkit/IT-Data/dati-regioni/dpc-covid19-ita-regioni.csv'
        self.data = pd.read_csv(path)
        dates = []
        for d in self.data['data']:
            t = datetime.datetime.fromisoformat(d)
            dates.append(t.strftime('%b %d'))

        self.data['dates'] = dates

    def get_region_by_code(self,code):
        return self.get_region(code=code)
    
    def get_region_by_name(self,name):
        return self.get_region(name=name)
        
    def get_region(self,name=None,code=None):
        if name==None:
            select = self.data['codice_regione']==code
        else:
            select = self.data['denominazione_regione']==name
        
        return self.data[select]
    
    def get_all_region_names(self):
        
        r = self.data['denominazione_regione']
        return np.unique(r)
        
    def get_all_variables(self):
        labels = ['ricoverati_con_sintomi', 'terapia_intensiva',
                      'totale_ospedalizzati', 'isolamento_domiciliare', 
                      'totale_positivi','variazione_totale_positivi', 
                      'nuovi_positivi', 'dimessi_guariti','deceduti', 
                      'totale_casi', 'tamponi']
        return labels
    
    def get_plot_data(self,region_name,label,
                      n_smooth =0,
                      plot_type='scatter'):
        
        region = self.get_region_by_name(region_name)
        N = len(region['dates'])
        cases = smooth_data(region[label],n_smooth)
        x = region['dates'][0:N]
        plot_data = {
                "type": plot_type,
                "name": region_name + '(' + label +')',
                "x": x,
                "y": cases
            }
        return plot_data
    
    def get_region_overview_plot_data(self,name,labels=None,
                                      start_date = 0,
                                      n_smooth = 0,
                                      rescale = False,
                                      plot_type='scatter'):
        
        
        region = self.get_region_by_name(name)
        N = len(region['dates'])
        ind = np.arange(N)

        plot_data = []
        if labels == None:
            labels = ['ricoverati_con_sintomi', 'terapia_intensiva',
                      'totale_ospedalizzati', 'isolamento_domiciliare', 
                      'totale_positivi','variazione_totale_positivi', 
                      'nuovi_positivi', 'dimessi_guariti','deceduti', 
                      'totale_casi', 'tamponi']
        
        for l in labels:
        
            if rescale:
                start_date = 0
                s0 = 0
                x = ind[s0:N-1]-s0
            else:
                s0 = start_date
                x = region['dates'][s0:N-1]
                
            smoothed = smooth_data(region[l],n_smooth)
            cases = smoothed[s0:N-1]
    
            plots = {
                "type": plot_type,
                "name": name + '(' + l +')',
                "x": x,
                "y": cases
            }
            plot_data.append(plots)
        
        return plot_data
        

# a class to handle the data (JHU)
class DataHandler:
    def __init__(self,data_confirmed_path,data_death_path):
        
        # dataframe of confirmed data
        self.confirmed = pd.read_csv(data_confirmed_path)
        self.death = pd.read_csv(data_death_path)
        self.countries = []
                       
    # get data related to single country
    def get_country(self,name):
        # confirmed cases
        select = self.confirmed['Country/Region']==name
        d = self.confirmed[select].iloc[:,4:]
        if len(self.confirmed[select])>1:
            country_confirmed = d.sum(axis=0)
            #print(name,self.confirmed)
        else:
            country_confirmed = self.confirmed[select].iloc[0,4:]
        
        # confirmed deaths
        select = self.death['Country/Region']==name
        d = self.death[select].iloc[:,4:]
        if len(self.confirmed[select])>1:
            country_deaths = d.sum(axis=0)
            #print(name,self.confirmed)
        else:
            country_deaths = self.death[select].iloc[0,4:]
        
        # list of dates
        dates = []
        names = self.confirmed.columns
        for k in range(4,len(names)):
            d = datetime.datetime.strptime(names[k],'%x')
            dates.append(d.strftime('%d %b'))
        
        daily_new_cases = []
        daily_deaths = []
        start = 0
        start_death = 0
        for k in range(0,len(country_confirmed)-1):
            daily_new_cases.append(country_confirmed[k+1]-country_confirmed[k])
            daily_deaths.append(country_deaths[k+1]-country_deaths[k])
            if country_confirmed[k+1]>100 and country_confirmed[k]<=100:
                start = k
            if country_deaths[k+1]>10 and country_deaths[k]<=10:
                start_death = k
            
        
        return {
            'name': name,
            'dates': np.array(dates),
            'confirmed': np.array(country_confirmed),
            'deaths': np.array(country_deaths),
            'daily_new_cases': np.array(daily_new_cases),
            'daily_deaths': np.array(daily_deaths),
            'start': start,
            'start_death': start_death
        }

    def add_country(self,c_name):
        c = self.get_country(c_name)
        self.countries.append(c)
        
    # return data structures to be used with plotly
    def get_confirmed_data(self,start_date=0,n_smooth=7,rescale=True,plot_type="scatter"):
        
        N = len(self.countries[0]['confirmed'])
        ind = np.arange(len(self.countries[0]['dates']))
        plotly_data = []
        
        for c in self.countries:
        
            if rescale:
                start_date = 0
                s0 = c['start']
                x = ind[s0:N-1]-s0
            else:
                s0 = start_date
                x = c['dates'][s0:len(c['dates'])-1]
                
            smoothed = smooth_data(c['confirmed'],n_smooth)
            cases = smoothed[s0:N-1]
    
            plots = {
                "type": plot_type,
                "name": c['name'],
                "x": x,
                "y": cases
            }
            plotly_data.append(plots)
        
        return plotly_data
                
    # return data structures to be used with plotly
    def get_deaths_data(self,start_date=0,n_smooth=7,rescale=True,plot_type="scatter"):
        
        N = len(self.countries[0]['deaths'])
        ind = np.arange(len(self.countries[0]['dates']))
        plotly_data = []
        
        for c in self.countries:
        
            if rescale:
                start_date = 0
                s0 = c['start_death']
                x = ind[s0:N-1]-s0
            else:
                s0 = start_date
                x = c['dates'][s0:len(c['dates'])-1]
                
            smoothed = smooth_data(c['deaths'],n_smooth)
            cases = smoothed[s0:N-1]
    
            plots = {
                "type": plot_type,
                "name": c['name'],
                "x": x,
                "y": cases
            }
            plotly_data.append(plots)
        
        return plotly_data
    
    # return data structures to be used with plotly
    def get_daily_confirmed_data(self,start_date=0,n_smooth=7,rescale=True,plot_type="scatter"):
        
        N = len(self.countries[0]['confirmed'])
        ind = np.arange(len(self.countries[0]['dates']))
        plotly_data = []
        
        for c in self.countries:
        
            if rescale:
                start_date = 0
                s0 = c['start']
                x = ind[s0:N-1]-s0
            else:
                s0 = start_date
                x = c['dates'][s0:len(c['dates'])-1]
                
            smoothed = smooth_data(c['daily_new_cases'],n_smooth)
            cases = smoothed[s0:N-1]
    
            plots = {
                "type": plot_type,
                "name": c['name'],
                "x": x,
                "y": cases
            }
            plotly_data.append(plots)
        
        return plotly_data
    
    # return data structures to be used with plotly
    def get_daily_deaths_data(self,start_date=0,n_smooth=7,rescale=True,plot_type="scatter"):
        
        N = len(self.countries[0]['deaths'])
        ind = np.arange(len(self.countries[0]['dates']))
        plotly_data = []
        
        for c in self.countries:
        
            if rescale:
                start_date = 0
                s0 = c['start_death']
                x = ind[s0:N-1]-s0
            else:
                s0 = start_date
                x = c['dates'][s0:len(c['dates'])-1]
                
            smoothed = smooth_data(c['daily_deaths'],n_smooth)
            cases = smoothed[s0:N-1]
    
            plots = {
                "type": plot_type,
                "name": c['name'],
                "x": x,
                "y": cases
            }
            plotly_data.append(plots)
        
        return plotly_data
    
    # return data structures to be used with plotly
    def get_death_rate_data(self,start_date=0,n_smooth=7,rescale=True,plot_type="scatter"):
        
        N = len(self.countries[0]['confirmed'])
        ind = np.arange(len(self.countries[0]['dates']))
        plotly_data = []
        
        for c in self.countries:
        
            if rescale:
                start_date = 0
                s0 = c['start']
                x = ind[s0:N-1]-s0
            else:
                s0 = start_date
                x = c['dates'][s0:len(c['dates'])-1]
             
            drate = c['deaths']/(c['confirmed']+0.1)
            smoothed = smooth_data(drate,n_smooth)
            cases = smoothed[s0:N-1]
    
            plots = {
                "type": plot_type,
                "name": c['name'],
                "x": x,
                "y": cases
            }
            plotly_data.append(plots)
        
        return plotly_data
                        
####################################################################
# plot an array of dict
# plot_data should contain: x,y,name,type
            
def plot_structure(plot_data,title=None):
    
    fig, ax = plt.subplots(figsize=(13,7))  
    
    ind = np.arange(len(plot_data[0]['x']))
    for p in plot_data:
        plt.plot(p['x'],p['y'],label=p['name'])
    
    plt.xticks(ind, plot_data[0]['x'], rotation=90) 
    
    plt.legend(framealpha=1,frameon=False,bbox_to_anchor=(1.15,0.3),
                       loc='upper center').set_draggable(True)
    if not title == None:
        plt.title(title)
    #plt.xlim(start_date,ind[len(ind)-1])
    plt.show()

    
    
    
####################################################################
# simple function to smooth recorded data over n days
def smooth_data(array_in,n):
    smoothed = []
    
    if n==0:
        return np.array(array_in)
    N = len(array_in)

    for k in range(0,n):
        smoothed.append(sum(array_in[0:k+1])/(k+1))
        
    for k in range(n,N):
        smoothed.append(sum(array_in[k-n:k])/n)
        
    return np.array(smoothed)



####################################################################
# OLD FUNCTIONS

# plot the ration deaths/confirmed
def plot_death_rate(countries,start_date=0):
    
    fig, ax = plt.subplots(figsize=(13,7))  
    ind = np.arange(len(countries[0]['dates']))
    
    for c in countries:
        ax.semilogy(c['deaths']/(c['confirmed']+0.1),label=c['name'])
    plt.xticks(ind, c['dates'], rotation=90) 
    
    plt.title('Official mortality rate: # Death/# Confirmed')
    plt.legend(framealpha=1,frameon=False,bbox_to_anchor=(1.15,0.3),
                       loc='upper center').set_draggable(True)
    
    plt.xlim(start_date,ind[len(ind)-1])
    plt.show()
    
def plot_daily_cases(countries,start_date=0,n_smooth=0,rescale=False):
    
    
    fig, ax = plt.subplots(figsize=(13,7))
    ind = np.arange(len(countries[0]['dates']))
    N = len(countries[0]['confirmed'])
    if rescale:
        start_date = 0
        
    for c in countries:
        cases = smooth_data(c['daily_new_cases'][0:N-1],n_smooth)
        
        if rescale :
            plt.plot(ind[c['start']:len(c['dates'])-1]-c['start'],
                     cases[c['start']:len(c['confirmed'])-1],
                     label=(c['name'] + ' (Total  = ' + str(c['confirmed'][-1]) +')'),
                     linewidth=2)
        else:
            plt.plot(ind[1:],cases,
                     label=(c['name'] + ' (Total  = ' + str(c['confirmed'][-1]) +')'),
                     linewidth=2)
    if rescale:
        plt.xticks(ticks=ind,labels=ind) 
        plt.xlim(start_date,65)
    
    else:
        plt.xticks(ticks=ind,labels=countries[0]['dates'], rotation=90) 
        plt.xlim(start_date,ind[-1])
    
    plt.title(' # Reported cases per day ')
    plt.legend(framealpha=1,frameon=False,bbox_to_anchor=(.8,0.9),
                       loc='upper center').set_draggable(True)
    plt.show()
    
def plot_confirmed_cases(countries,start_date=0,n_smooth=0,rescale=False,log_scale=False):
    
    fig, ax = plt.subplots(figsize=(13,7))
    ind = np.arange(len(countries[0]['dates']))
    N = len(countries[0]['confirmed'])
    
    for c in countries:
        
        if rescale:
            start_date = 0
            s0 = c['start']
            smoothed = smooth_data(c['confirmed'],n_smooth)
            cases = smoothed[s0:N-1]
    
            if log_scale:
                ax.semilogy(ind[s0:len(c['dates'])-1]-s0,cases,
                     label=c['name'] + ' (Total cases = ' + str(c['confirmed'][-1]) + ')')
            else:
                plt.plot(ind[s0:len(c['dates'])-1]-s0,cases,
                         label=c['name'] + ' (Total cases = ' + str(c['confirmed'][-1]) + ')')
        
        else:
            
            s0 = 0
            smoothed = smooth_data(c['confirmed'],n_smooth)
            cases = smoothed[s0:N-1]
            if log_scale:
                ax.semilogy(ind[s0:len(c['dates'])-1]-s0,cases,
                     label=c['name'] + ' (Total cases = ' + str(c['confirmed'][-1]) + ')')
            else:
                plt.plot(ind[s0:len(c['dates'])-1]-s0,cases,
                         label=c['name'] + ' (Total cases = ' + str(c['confirmed'][-1]) + ')')
            
    plt.xticks(ind, rotation=90) 
    plt.title(' Total number of (reported) cases')
    plt.legend(framealpha=1,frameon=False,bbox_to_anchor=(1.2,0.8),
                        loc='upper center').set_draggable(True)
    plt.xlim(start_date,ind[len(ind)-1])
    plt.show()
    
    
def plot_deaths(countries,start_date=0,n_smooth=0,rescale=False,log_scale=False):
    
    fig, ax = plt.subplots(figsize=(13,7))
    ind = np.arange(len(countries[0]['dates']))
    N = len(countries[0]['deaths'])
    
    for c in countries:
        
        if rescale:
            start_date = 0
            s0 = c['start_death']
            smoothed = smooth_data(c['deaths'],n_smooth)
            cases = smoothed[s0:N-1]
    
            if log_scale:
                ax.semilogy(ind[s0:len(c['dates'])-1]-s0,cases,
                     label=c['name'] + ' (Total deaths = ' + str(c['deaths'][-1]) + ')')
            else:
                plt.plot(ind[s0:len(c['dates'])-1]-s0,cases,
                         label=c['name'] + ' (Total deaths = ' + str(c['confirmed'][-1]) + ')')
        
        else:
            
            s0 = 0
            smoothed = smooth_data(c['deaths'],n_smooth)
            cases = smoothed[s0:N-1]
            if log_scale:
                ax.semilogy(ind[s0:len(c['dates'])-1]-s0,cases,
                     label=c['name'] + ' (Total deaths = ' + str(c['deaths'][-1]) + ')')
            else:
                plt.plot(ind[s0:len(c['dates'])-1]-s0,cases,
                         label=c['name'] + ' (Total deaths = ' + str(c['deaths'][-1]) + ')')
            
    plt.xticks(ind, rotation=90) 
    plt.title(' Total number of (reported) deaths')
    plt.legend(framealpha=1,frameon=False,bbox_to_anchor=(1.2,0.8),
                        loc='upper center').set_draggable(True)
    plt.xlim(start_date,ind[len(ind)-1])
    plt.show()

####################################################################   
    


