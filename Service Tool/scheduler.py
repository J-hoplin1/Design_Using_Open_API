import schedule
import json,time,os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from functionModules.apiCaller import dataFromAPICall
from functionModules.smtpConnector import generateTextMime
from functionModules.patternChecker import patternChecker
from functionModules.databaseConnector import SQLConnectorManager
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
        getDatas = self.DBManager.functionDatasInitiater()[0]
        self.apiKey = getDatas['APIKEY']
        self.apiURL = getDatas['APIURL']
        self.bitlyKey = getDatas['BITLYKEY']
        self.apiCallInstance = dataFromAPICall(self.apiKey, self.apiURL,self.bitlyKey)
    
    def initiateData(self):
        return self.apiCallInstance.reProcessXML(self.apiCallInstance.buildRequests()) # Generate smtpSendDatas

    def writeStreamHistory(self):
        dateObj = datetime.now(timezone('Asia/Seoul'))
        with open('../Datas/streamStartHistory.txt','a') as t:
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
                emailInfos = self.DBManager.returnMailInfo()[0]
                subscriberList = self.DBManager.returnSubscribers()
                apiUpdate = self.initiateData()
                if not apiUpdate:
                    pass
                else:
                    for i in subscriberList:
                        generateTextMime(i,emailInfos['HOSTERMAIL'],emailInfos['HOSTERMAILPW'])
                    latestAPIUpdatedTime = str(item.find('createDt').text)
                    break

schedulerInstance = scheduler()
def start():
    try:
        
        schedulerInstance.startStream()
    except BaseException as e:
        print(e)
        with open('../Datas/ErrorLog.txt','a') as t:
            t.write('Exception Occured at {}\nException msg : {}\n\n'.format(datetime.now(timezone('Asia/Seoul')).strftime("%Y/%m/%d %H : %M : %S"),e))
        t.close()
            
schedule.every().day.at("10:00").do(start)


while loop:
    try:
        schedule.run_pending() # 실행예약된 작업을 실행한다.
        time.sleep(5)
    except BaseException as e:
        print("Service Forecly Closed")
        loop = False
