import schedule
import json,time,os
from functionModules.apiCaller import dataFromAPICall
from functionModules.smtpConnector import generateTextMime
from functionModules.patternChecker import patternChecker
from functionModules.databaseConnector import SQLConnectorManager
from Datas.streamDatas import streamData
from enum import Enum
from urllib.parse import unquote
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup

loop = True

class scheduler(object):
    
    def __init__(self):
        # Declar SQL Manager
        self.DBManager = SQLConnectorManager()
        # Initiate subscriber data : Generate subs.json
        self.DBManager.generateSublist()
        self.DBManager.functionDatasInitiater(streamData)
        self.apiKey = streamData.APIKEY
        self.apiUrl = streamData.APIURL
        self.bitlykey = streamData.BITLYKEY
        self.apiCallInstance = dataFromAPICall(self.apiKey, self.apiUrl,self.bitlykey)
    
    def initiateData(self):
        self.apiCallInstance.reProcessXML(self.apiCallInstance.buildRequests()) # Generate smtpSendDatas

    def writeStreamHistory(self):
        dateObj = datetime.now(timezone('Asia/Seoul'))
        with open('Datas/streamStartHistory.txt','a') as t:
            t.write('New Stream Generated at : {}\n'.format(dateObj.strftime("%Y/%m/%d %H : %M : %S")))
        t.close()
        
    def startStream(self):
        while True:
            BSXML = self.apiCallInstance.buildRequests()
            item = BSXML.findAll('item')[0]
            if str(item.find('createDt').text.split()[0]) != datetime.now().strftime("%Y-%m-%d"):
                time.sleep(60)
                pass
            else:
                self.writeStreamHistory()
                with open('Datas/subs.json','r') as f:
                    subs = json.load(f)
                subscriberList = subs['subscribers']
                self.initiateData()
                for i in subscriberList:
                    generateTextMime(i)
                latestAPIUpdatedTime = str(item.find('createDt').text)
                break

schedulerInstance = scheduler()
def start():
    try:
        
        schedulerInstance.startStream()
    except BaseException as e:
        with open('Datas/ErrorLog.txt','a') as t:
            t.write('Exception Occured at {}\nException msg : {}\n\n'.format(datetime.now(timezone('Asia/Seoul')).strftime("%Y/%m/%d %H : %M : %S"),e))
        t.close()
            
#schedule.every().day.at("10:00").do(start)
schedule.every(10).seconds.do(start)

while loop:
    try:
        schedule.run_pending() # 실행예약된 작업을 실행한다.
        time.sleep(5)
    except BaseException as e:
        print("Service Forecly Closed")
        os.remove('Datas/subs.json')
        loop = False
