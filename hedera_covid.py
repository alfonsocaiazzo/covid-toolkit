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

# a class to handle the data
class DataHandler:
    def __init__(self,data_confirmed_path,data_death_path):
        
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
    def get_confirmed_data(self,start_date=0,n_smooth=7,rescale=True):
        
        N = len(self.countries[0]['confirmed'])
        ind = np.arange(len(self.countries[0]['dates']))
        plotly_data = []
        
        for c in self.countries:
        
            if rescale:
                start_date = 0
                s0 = c['start']
                x = ind[s0:len(c['dates'])-1]
            else:
                s0 = 0
                x = c['dates'][s0:len(c['dates'])-1]
                
            smoothed = smooth_data(c['confirmed'],n_smooth)
            cases = smoothed[s0:N-1]
    
            plots = {
                "type": "bar",
                "name": c['name'],
                "x": x,
                "y": cases
            }
            plotly_data.append(plots)
        
        return plotly_data
                
                        
            
    
        
    
class Plotter:
    def __init__(self, handler):
        self.n_countries = 0
        self.countries = []
        self.handler = handler
    
    def add_country(self,c_name):
        c = self.handler.get_country(c_name)
        self.countries.append(c)
        self.n_countries += 1
    
####################################################################
# simple function to smooth recorded data over n days
def smooth_data(array_in,n):
    smoothed = []
    
    if n==0:
        return np.array(array_in)
    N = len(array_in)

    for k in range(0,n):
        smoothed.append(sum(array_in[k:k+n])/n)
        
    for k in range(n,N):
        smoothed.append(sum(array_in[k-n:k])/n)
        
    return np.array(smoothed)

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
    


