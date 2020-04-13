#!/usr/bin/env python
# coding: utf-8

import requests
import csv
import urllib.request
import urllib3
import time
from bs4 import BeautifulSoup
#
from datetime import datetime, timedelta
import datetime
#
import csv
import os.path
import os

import sched, time
s = sched.scheduler(time.time, time.sleep)
def mycrawler_safe():
    attempts = 0
    while attempts < 3:
        try:
            mycrawler()
            break
        except:
            attempts += 1
            time.sleep(1)
    
def mycrawler():
    data_save_path = 'D:/00.自動化資料庫'
    #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #url = 'https://www.esunbank.com.tw/bank/iframe/widget/rate/foreign-exchange-rate'
    url = 'https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates'
    response = requests.get(url,verify=True)
    if response.status_code != 200:
        s.enter(60, 1, mycrawler_safe)
        print(response)
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    follow_list = ['美元(USD)', '日圓(JPY)', '歐元(EUR)', '英鎊(GBP)']
    currency_table = [['幣別', '即期買入', '即期賣出', '優惠買入', '優惠賣出', '現金買入', '現金賣出']]
    followed_row = []
    
    #mysh.range('A11').value = '更新時間：' + soup.findAll(id='layout_0_maincontent_0_ph_tabcontent_0_LbQuoteTime')[0].text
    mytime = soup.findAll('span', id='LbQuoteTime')[0].text.replace('年', '/').replace('月', '/').replace('日', '')
    followed_row.append(datetime.datetime.strptime(mytime, '%Y/%m/%d %H:%M:%S').time())
    for tb in soup.find_all('table', id='inteTable1'):
        row = 0
        for td in tb.find_all('td'):
            if '\n' in td.text:
                currency_table.append([])
                row = row + 1
            currency_table[row].append(td.text.replace('\n', ''))
    currency_table.append(['報價時間', mytime])
    
    #currency talbe data check
    if sum(len(row) for row in currency_table) < 100:
        print(currency_table)
        s.enter(60, 1, mycrawler_safe)
        return
    
    for row in currency_table:
        if row[0] in follow_list:
            followed_row.append(row[1])
            followed_row.append(row[2])
    
    if os.path.isfile(data_save_path + '/currency_rates.csv'):
        file = open(data_save_path + '/currency_rates.csv', 'r')
        file.close()
    else:
        with open(data_save_path + '/currency_rates.csv', 'w+', newline='') as csvfile:
            mywriter = csv.writer(csvfile)
            table_title = [['2', '美元(USD)', '', '日圓(JPY)', '', '歐元(EUR)', '', '英鎊(GBP)', ''],
                           ['時間', '買匯', '賣匯','買匯', '賣匯','買匯', '賣匯','買匯', '賣匯']]
            mywriter.writerows(table_title)

    
    #############################################################################################################
    # 歷史匯率紀錄
    #############################################################################################################
    with open(data_save_path + '/currency_rates.csv', 'r', newline='') as csvfile:
        csvdata = csv.reader(csvfile, delimiter=',')
        mycurrency2 = list(csvdata)
        mycurrency2.append(followed_row)
        mycurrency2[0][0] = str(int(mycurrency2[0][0]) + 1)
        csvfile.close()

    with open(data_save_path + '/currency_rates.csv', 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        mywriter.writerows(mycurrency2)
        csvfile.close()
    
    #############################################################################################################
    # 即時匯率
    #############################################################################################################
    with open(data_save_path + '/currency_rates_now.csv', 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        mywriter.writerows(currency_table)
        #csvfile.close()

    #############################################################################################################
    # 即時損益分析
    #############################################################################################################
    with open(data_save_path + '/currency_balance.csv', 'r', newline='') as csvfile:
        csvdata = csv.reader( csvfile, delimiter=',' )
        balance_tbl = list( csvdata )
        sum_NTD = 0
        sum_JPY = 0
        for i in range( 2,len( balance_tbl ) ):
            sum_NTD = sum_NTD + int( balance_tbl[i][1] )
            sum_JPY = sum_JPY + int( balance_tbl[i][2] )
            if len( balance_tbl[i] ) < 4:
                balance_tbl[i].append( round( int( balance_tbl[i][1]) / int(balance_tbl[i][2] ), 4 ) )
            else:
                balance_tbl[i][3] = round( int( balance_tbl[i][1]) / int(balance_tbl[i][2] ), 4 )
        balance_tbl[0][1] = round( sum_NTD/sum_JPY, 4 )
        balance_tbl[0][3] = round( (sum_JPY * ( float(currency_table[4][3]) )) - sum_NTD, 1 )
        print( str(datetime.datetime.now().strftime('%H:%M:%S')) + ', 平均匯率: ' + str(balance_tbl[0][1]) + ', 台幣損益: ' + str(balance_tbl[0][3]) )
        csvfile.close()

    with open( data_save_path + '/currency_balance.csv', 'w', newline='' ) as csvfile:
        mywriter = csv.writer( csvfile )
        mywriter.writerows( balance_tbl )
        csvfile.close()
    
    now = datetime.datetime.now()
    today10pm = now.replace(hour=23, minute=0, second=0, microsecond=0)
    if now < today10pm:
        s.enter(60, 1, mycrawler_safe)
    else:
        Current_Date = datetime.datetime.today().strftime ('%Y-%m-%d')
        os.rename(data_save_path + r'/currency_rates.csv', data_save_path + r'/currency_rates_' + str(Current_Date) + '.csv')


s.enter(0, 0, mycrawler_safe)
s.run()