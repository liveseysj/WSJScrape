# -*- coding: utf-8 -*-
"""
Created on Sat May 23 14:01:58 2020

@author: Admin
"""


import pandas as pd
import datetime as dt
from datetime import datetime, timedelta

import json
import urllib
from urllib.request import urlopen   
from bs4 import BeautifulSoup
from pandas_datareader import data as wb
import requests
#import math  
from IPython.display import HTML
import random
import pandas_market_calendars as mcal

from lxml import etree
import lxml.html

from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.firefox.options import Options
#%% Consider Removing as replaced with the close value table in the section below

'''
#------------ Get data from WSJ site
url = 'https://www.wsj.com/market-data/stocks?id=%7B%22application%22%3A%22WSJ%22%2C%22marketsDiaryType%22%3A%22overview%22%7D&type=mdc_marketsdiary'
# put a header on the request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
req = urllib.request.Request(url=url, headers=headers)
with urlopen(req) as response:
    page_html = response.read()
df = pd.DataFrame()    
data = json.loads(page_html).get('data')
for instrumentSets in data.get('instrumentSets'):
    for k,v in instrumentSets.items():
        if k == 'instruments':
            df = df.append(pd.DataFrame(v))
df=df.rename(columns = {'name':'Issues'})
df=df.reset_index()
#-----------------
'''
print('Script is working')
def main():
    print("Main Executed")
    #%% 
    site = 'https://www.wsj.com/market-data/stocks/marketsdiary'

    # options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument('--disable-gpu') 
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # driver=webdriver.Chrome(executable_path='E:\Trading\Quant\chromedriver.exe', options=options)
    display = Display(visible=0,size=(1366,768))

    options = Options()

    fire_profile = webdriver.FirefoxProfile()
    fire_profile.set_preference("browser.cache.disk.enable", False)
    fire_profile.set_preference("browser.cache.memory.enable", False)
    fire_profile.set_preference("browser.cache.offline.enable", False)
    fire_profile.set_preference("network.http.use-cache", False) 

    options.headless = True

    display.start()
    driver = webdriver.Firefox(options=options, firefox_profile = fire_profile)


    driver.get(site)
    delay=30
    html=driver.page_source
    soup=BeautifulSoup(html, "lxml")
    #table=soup.find_all('tbody')
    #table=table[0]
    div=soup.find('div', id='root')
    df=pd.read_html(str(soup))[0]

    driver.close()
    driver.quit()
    display.stop()

    df_NYSE=df.iloc[:14,:2]
    df_NYSE.columns=['Data','Value']
    df_NASDAQ=df.iloc[14:25,:2]
    df_NASDAQ.columns=['Data','Value']
    #%% 
    #------------get data from AAII sentiment site
    url = 'https://www.aaii.com/sentimentsurvey/sent_results?'
    page=requests.get(url)
    soup=BeautifulSoup(page.content,'html.parser')

    for tr in soup.find_all('tr')[1:2]:
        tds=tr.find_all('td')
        bulls=tds[1].text
        neutral=tds[2].text
        bears=tds[3].text

    bulls=float(bulls.replace('%',''))
    neutral=float(neutral.replace('%',''))
    bears=float(bears.replace('%',''))

    AAII_NET_BULLS=bulls-bears-neutral

    NYSE_UPV=df_NYSE['Value'][6]/1000000

    NYSE_DNV=df_NYSE['Value'][7]/1000000

    NYSE_ADV=df_NYSE['Value'][1]

    NYSE_DEC=df_NYSE['Value'][2]


    ticker=wb.DataReader('^GSPC', data_source='yahoo')
    SPX=ticker[-1:]['Close'][0]

    NYSE_TOTAL=df_NYSE['Value'][0]

    NYSE_LOWS=100*df_NYSE['Value'][5]/NYSE_TOTAL

    NYSE_HIGHS=100*df_NYSE['Value'][4]/NYSE_TOTAL

    ticker=wb.DataReader('^VIX', data_source='yahoo')
    VIX=ticker[-1:]['Close'][0]

    today_data={'UPV':NYSE_UPV, 'DNV':NYSE_DNV, 'ADV':NYSE_ADV,'DEC':NYSE_DEC, 'SPX':SPX, 'Lows':NYSE_LOWS, 'Highs':NYSE_HIGHS, 'VIX':VIX, 'AAII':AAII_NET_BULLS}
    today=pd.to_datetime('today').tz_localize('Asia/Singapore').tz_convert('US/Eastern')
    today=today.replace(tzinfo=None,hour=0, minute=0,second=0, microsecond=0)

    nyse = mcal.get_calendar('NYSE')
    is_holiday=nyse.valid_days(start_date=today,end_date=today)

    if len(is_holiday) >0:
        #take yesterday's CSV and add to it
        df_raw_data=pd.read_csv('raw data.csv', index_col=0)
        #append today's data to yesterday's
        df_raw_data=df_raw_data.append(pd.DataFrame(today_data,index=[today]))
        
        df_raw_data=df_raw_data.reset_index()
        df_raw_data=df_raw_data.rename(columns={'index':'Date'})
        #save a copy of today's and update the main csv to be added to tomorrow


        df_raw_data.to_csv(str(today.date()) + ' raw data.csv', index=False)
        df_raw_data.to_csv('raw data.csv', index=False)
        
        #update SPX close
        spx_price={'Last Price':SPX}
        df_spx=pd.read_csv('SPX 1930 Daily.csv', index_col=0)
        df_spx=df_spx.append(pd.DataFrame(spx_price,index=[today]))
        df_spx=df_spx.reset_index()
        df_spx=df_spx.rename(columns={'index':'Date'})
        df_spx.to_csv('SPX 1930 Daily.csv',index=False)
    print("Main Complete")
import schedule 
import time 
def check():
    print("executed")
# schedule.every().day.at("01:30").do(main) 
schedule.every(5).minutes.do(main) 

while True: 
  
    # Checks whether a scheduled task  
    # is pending to run or not 
    schedule.run_pending() 
    time.sleep(1) 