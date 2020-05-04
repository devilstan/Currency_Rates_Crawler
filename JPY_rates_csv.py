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
    mycrawler()
    #attempts = 0
    #while attempts < 3:
    #    try:
    #        mycrawler()
    #        break
    #    except Exception as e:
    #        attempts += 1
    #        print(e)
    #        time.sleep(2)

def BalanceCalc(currency_sym, current_rate, invested_found, filename):
    data_save_path = 'D:/00.自動化資料庫'
    with open(data_save_path + '/' + filename, 'r', newline='') as csvfile:
        csvdata = csv.reader( csvfile, delimiter=',' )
        attempts_now = 0
        while attempts_now < 3:
            try:
                balance_tbl = list( csvdata )
                break
            except Exception as e:
                attempts_now += 1
                print(e)
                time.sleep(2)
                if attempts_now == 3:
                    s.enter(60, 1, mycrawler_safe)
                    return
                    
        sum_NTD = 0
        sum_Foreign = 0
        for i in range( 2,len( balance_tbl ) ):
            sum_NTD = sum_NTD + float( balance_tbl[i][1] )
            sum_Foreign = sum_Foreign + float( balance_tbl[i][2] )
            if len( balance_tbl[i] ) < 4:
                balance_tbl[i].append( round( float( balance_tbl[i][1]) / float(balance_tbl[i][2] ), 4 ) )
            else:
                balance_tbl[i][3] = round( float( balance_tbl[i][1]) / float(balance_tbl[i][2] ), 4 )
        balance_tbl[0][1] = round( sum_NTD/sum_Foreign, 4 )
        balance_tbl[0][3] = round( (sum_Foreign * ( float(current_rate) )) - sum_NTD, 1 )
        #print( str(datetime.datetime.now().strftime('%H:%M:%S')) + ', 平均匯率: ' + str(balance_tbl[0][1]) + ', 台幣損益: ' + str(balance_tbl[0][3]) )
        invested_local = []
        invested_local.append(str(balance_tbl[0][1]) + '(' + currency_sym + ')')
        invested_local.append(balance_tbl[0][3])
        invested_found.append(invested_local)
        attempts_now = 0
        while attempts_now < 3:
            try:
                csvfile.close()
                break
            except Exception as e:
                attempts_now += 1
                print(e)
                time.sleep(2)
                
    with open( data_save_path + '/' + filename, 'w', newline='' ) as csvfile:
        mywriter = csv.writer( csvfile )
        mywriter.writerows( balance_tbl )
        attempts_now = 0
        while attempts_now < 3:
            try:
                csvfile.close()
                break
            except Exception as e:
                attempts_now += 1
                print(e)
                time.sleep(2)

def mycrawler():
    data_save_path = 'D:/00.自動化資料庫'
    #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #url = 'https://www.esunbank.com.tw/bank/iframe/widget/rate/foreign-exchange-rate'
    url = 'https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates'
    attempts = 0
    while attempts < 3:
        try:
            response = requests.get(url,verify=True)
            break
        except Exception as e:
            attempts += 1
            print(e)
            time.sleep(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    follow_list = ['美元(USD)', '日圓(JPY)', '歐元(EUR)', '英鎊(GBP)']
    currency_table = [['幣別', '即期買入', '即期賣出', '優惠買入', '優惠賣出', '現金買入', '現金賣出']]
    followed_row = []
    
    #mysh.range('A11').value = '更新時間：' + soup.findAll(id='layout_0_maincontent_0_ph_tabcontent_0_LbQuoteTime')[0].text
    try:
        mytime = soup.findAll('span', id='LbQuoteTime')[0].text.replace('年', '/').replace('月', '/').replace('日', '')
    except:
        s.enter(60, 1, mycrawler_safe)
        return
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
        attempts_now = 0
        while attempts_now < 3:
            try:
                file.close()
                break
            except Exception as e:
                attempts_now += 1
                print(e)
                time.sleep(2)
    else:
        with open(data_save_path + '/currency_rates.csv', 'w+', newline='') as csvfile:
            mywriter = csv.writer(csvfile)
            table_title = [['2', '美元(USD)', '', '日圓(JPY)', '', '歐元(EUR)', '', '英鎊(GBP)', ''],
                           ['時間', '買匯', '賣匯','買匯', '賣匯','買匯', '賣匯','買匯', '賣匯']]
            mywriter.writerows(table_title)
            attempts_now = 0
            while attempts_now < 3:
                try:
                    csvfile.close()
                    break
                except Exception as e:
                    attempts_now += 1
                    print(e)
                    time.sleep(2)

    
    #############################################################################################################
    # 歷史匯率紀錄
    #############################################################################################################
    with open(data_save_path + '/currency_rates.csv', 'r', newline='') as csvfile:
        csvdata = csv.reader(csvfile, delimiter=',')
        mycurrency2 = list(csvdata)
        mycurrency2.append(followed_row)
        mycurrency2[0][0] = str(int(mycurrency2[0][0]) + 1)
        attempts_now = 0
        while attempts_now < 3:
            try:
                csvfile.close()
                break
            except Exception as e:
                attempts_now += 1
                print(e)
                time.sleep(2)

    with open(data_save_path + '/currency_rates.csv', 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        mywriter.writerows(mycurrency2)
        attempts_now = 0
        while attempts_now < 3:
            try:
                csvfile.close()
                break
            except Exception as e:
                attempts_now += 1
                print(e)
                time.sleep(2)
    
    #############################################################################################################
    # 即時匯率
    #############################################################################################################
    with open(data_save_path + '/currency_rates_now.csv', 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        mywriter.writerows(currency_table)
        attempts_now = 0
        while attempts_now < 3:
            try:
                csvfile.close()
                break
            except Exception as e:
                attempts_now += 1
                print(e)
                time.sleep(2)

    #############################################################################################################
    # 即時損益分析
    #############################################################################################################
    invested_found = []            
    BalanceCalc('USD', currency_table[1][3], invested_found, 'currency_balance(USD).csv')
    BalanceCalc('JPY', currency_table[4][3], invested_found, 'currency_balance(JPY).csv')
    BalanceCalc('GBP', currency_table[8][3], invested_found, 'currency_balance(GBP).csv')
    BalanceCalc('EUR', currency_table[5][3], invested_found, 'currency_balance(EUR).csv')
                
    #############################################################################################################
    # 即時損益顯示
    #############################################################################################################
    #print(invested_found)
    print( str(datetime.datetime.now().strftime('%H:%M:%S')) + ', 平均匯率: ' + str([row[0] for row in invested_found]) + ', 台幣損益: ' + str(int(sum([row[1] for row in invested_found]))) )
    
    now = datetime.datetime.now()
    today10pm = now.replace(hour=23, minute=0, second=0, microsecond=0)
    if now < today10pm:
        s.enter(60, 1, mycrawler_safe)
    else:
        Current_Date = datetime.datetime.today().strftime ('%Y-%m-%d')
        os.rename(data_save_path + r'/currency_rates.csv', data_save_path + r'/currency_rates_' + str(Current_Date) + '.csv')


s.enter(0, 0, mycrawler_safe)
s.run()