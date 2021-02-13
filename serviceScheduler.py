import schedule
import json,time
from functionModules.apiCaller import dataFromAPICall
from functionModules.smtpConnector import generateTextMime
from functionModules.patternChecker import patternChecker
from Datas.streamDatas import streamData
from enum import Enum
from urllib.parse import unquote
from datetime import datetime
from pytz import timezone

class scheduler(object):
    
    def __init__(self):
        self.apiKey = streamData.APIKEY
        self.apiUrl = streamData.APIURL
        self.apiCallInstance = dataFromAPICall(self.apiKey, self.apiUrl)
    
    def initiateData(self):
        self.apiCallInstance.buildRequests() # Generate smtpSendDatas

    def writeStreamHistory(self):
        dateObj = datetime.now(timezone('Asia/Seoul'))
        with open('Datas/streamStartHistory.txt','a') as t:
            t.write('New Stream Generated at : {}\n'.format(dateObj.strftime("%Y/%m/%d %H : %M : %S")))
        t.close()
        
    def startStream(self):
        while True:
            BSXML = self.apiCallInstance.buildRequests()
            item = res.findAll('item')[0]
            if sif str(item.find('createDt').text.split()[0]) != datetime.now().strftime("%Y-%m-%d"):
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
                break

def start():
    schedulerInstance = scheduler()
    schedulerInstance.startStream()
            
schedule.every().day.at("10:00").do(start)
#schedule.every(10).seconds.do(start)

while True:
    schedule.run_pending() # 실행예약된 작업을 실행한다.
    time.sleep(5)
