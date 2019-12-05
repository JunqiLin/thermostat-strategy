#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 18:37:23 2019

@author: linjunqi
"""

import pandas as pd
import numpy as np
import talib as ta
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

n = 30
threod = 20 
swingPrcnt1 = 0.5
swingPrcnt2 = 0.75
atrLength = 10
bollingerLengths = 30 
k = bollingerLengths 
Lots = 0
cmiVal = 0
numStdDevs = 2
trendLiqLength = 50

data = pd.read_excel("./data/zz500.xlsx")


def thermostat_strategy(data):

    close = np.array(data['close'])
    high = data['high']
    low = data['low']
    
    data['rd_zz'] = data['close'].pct_change(1).fillna(0)
    data['net_zz'] = (1+data['rd_zz']).cumprod()
    
    
    data['cmi'] = 0
    data['keyprice'] = 0 
    data['h_high'] = 0
    data['l_low'] = 0
    data['sellEasierDay'] = False
    data['buyEasierDay'] = False
    data['swingBuyPt'] = 0
    data['swingSellPt'] = 0
    data['atr'] = 0
    data['trendLokBuy'] = 0
    data['trendLokSell'] = 0
    data['swingUpTrigger'] = 0
    data['swingDnTrigger'] = 0
    data['band'] = 0
    data['upband'] = 0
    data['dnband'] = 0
    data['marketPosition'] = 0
    data['swingEntry'] = False
    
    
    data['upband'],data['band'],data['dnband'] = ta.BBANDS(close,timeperiod = bollingerLengths)
    atr = ta.ATR(high, low, close, timeperiod=atrLength)
    data['atr'] = atr
#    
    t = []
    for i in range(len(high) - k):
        
        h = np.max(high[i:i+n])
        l = np.min(low[i:i+n])
        data.loc[i+n,'h_high'] = h
        data.loc[i+n,'l_low'] = l
        
        data.loc[i+n,'trendLokBuy'] = np.sum(data.loc[i+n-2: i+n,'low'])/3
        data.loc[i+n,'trendLokSell'] = np.sum(data.loc[i+n-2: i+n,'high'])/3
        
        data.loc[i+n,'cmi'] = 100*np.abs((data.loc[i+n,'close'] - data.loc[i,'close']))/(h-l)
        data.loc[i+n,'keyprice'] = (data.loc[i+n,'close'] + data.loc[i+n,'high'] + data.loc[i+n,'low'])/3

        if data.loc[i+n,'close'] > data.loc[i+n,'keyprice']:
            data.loc[i+n,'sellEasierDay'] = True
            data.loc[i+n,'swingBuyPt'] = data.loc[i+n,'open'] + swingPrcnt2 * data.loc[i+n,'atr'] 
            data.loc[i+n,'swingSellPt'] = data.loc[i+n,'open'] - swingPrcnt1 * data.loc[i+n,'atr'] 
        else:
            data.loc[i+n,'buyEasierDay'] = True
            data.loc[i+n,'swingBuyPt'] = data.loc[i+n,'open'] + swingPrcnt1 * data.loc[i+n,'atr'] 
            data.loc[i+n,'swingSellPt'] = data.loc[i+n,'open'] - swingPrcnt2 * data.loc[i+n,'atr'] 
#        data['cmi'] = 100* np.abs(close[:-n] - close[n:])/(h_high - l_low)
        data.loc[i+n,'swingUpTrigger'] = max(data.loc[i+n,'swingBuyPt'],data.loc[i+n,'trendLokBuy'])
        data.loc[i+n,'swingDnTrigger'] = min(data.loc[i+n,'swingSellPt'],data.loc[i+n,'trendLokSell'])
   
    ##震荡
        if data.loc[i+k,'cmi'] < threod:

            if data.loc[i+k,'high'] > data.loc[i+k-1,'swingUpTrigger']:
                data.loc[i+k,'marketPosition'] = 1
                data.loc[i+k,'swingEntry'] = True
                
            elif data.loc[i+k,'low'] < data.loc[i+k-1,'swingDnTrigger'] :
#                print('here')
                data.loc[i+k,'marketPosition'] = 0
                data.loc[i+k,'swingEntry'] = False
                
            else:
                data.loc[i+k,'marketPosition'] = data.loc[i+k-1,'marketPosition']
                data.loc[i+k,'swingEntry'] = data.loc[i+k-1, 'swingEntry']
    ##趋势            
        else:
            if data.loc[i+k,'high'] > data.loc[i+k-1,'upband']:
                data.loc[i+k,'marketPosition'] = 1
            elif data.loc[i+k,'low']  < data.loc[i+k-1,'dnband'] or data.loc[i+k,'low'] < data.loc[i+k-1,'trendLokSell'] or data.loc[i+k,'high'] > data.loc[i+k-1,'trendLokBuy'] :
    
                data.loc[i+k,'marketPosition'] = 0
            else:
                data.loc[i+k,'marketPosition'] = data.loc[i+k-1,'marketPosition']
      
    data.loc[data['marketPosition'] ==1,'rd_strategy'] = data.loc[data['marketPosition'] ==1,'rd_zz']      
    data.loc[data['marketPosition'] ==0,'rd_strategy'] = 0  
    data['net_strategy'] = (1 + data['rd_strategy']).cumprod()
    return data

d = thermostat_strategy(data)
d = d[n:]
plt.plot(d['net_zz'],color = 'red',label='zz500')
plt.plot(d['net_strategy'], color = 'blue',label = 'net_strategy')
plt.xlabel('trade days')
plt.ylabel('cum_returns')
plt.legend()
plt.show()
d.to_csv('./result.csv')

