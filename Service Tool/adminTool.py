import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import json
import shutil
import datetime
from functionModules.apiCaller import dataFromAPICall
from functionModules.smtpConnector import *
from functionModules.patternChecker import patternChecker
from functionModules.databaseConnector import SQLConnectorManager
from enum import Enum
from urllib.parse import unquote


options = Enum('option',['Service_Test','Add_Subscriber','Delete_User','View_Subscriber_List','Backup','Broadcast','End'])

def selectOpt() -> options:
    opt = [f'{p.value}. {p.name}' for p in options]
    while True:
        print('-' * 15)
        for i in  opt:
            print(i)
        print('-' * 15)
        try:
            select = int(input(">> "))
            if 1<= select <= len(opt):
                return options(select)
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\n비정상적인 종료입니다.")
            pass

class adminTool(object):
    def __init__(self):
        self.checker = patternChecker()
        # Declar SQL Manager
        self.DBManager = SQLConnectorManager()
        '''
        아래 부분에서 subs.json을 초기화합니다.
        '''
        getDatas = self.DBManager.functionDatasInitiater()[0]
        self.apiKey = getDatas['APIKEY']
        self.apiURL = getDatas['APIURL']
        self.bitlyKey = getDatas['BITLYKEY']
        self.apiCallInstance = dataFromAPICall(self.apiKey,self.apiURL,self.bitlyKey)
    
    def initiateData(self):
        return self.apiCallInstance.reProcessXML(self.apiCallInstance.buildRequests())
        
    def mainLoop(self):
        while True:
            opt = selectOpt()
            if opt == options.Service_Test:
                apiUpdate = self.initiateData()
                if not apiUpdate:
                    print("API not updated Yet!")
                else:
                    subscriberList = self.DBManager.returnSubscribers()
                    if not subscriberList:
                        print("Subscriber not Exist!")
                    else:
                        emailInfos = self.DBManager.returnMailInfo()[0]
                        for i in subscriberList:
                            generateTextMime(i,emailInfos['HOSTERMAIL'],emailInfos['HOSTERMAILPW'])
            elif opt == options.Add_Subscriber:
                newSub = input("새 구독자의 이메일 입력하기 : ")
                if not self.checker.checkEmailPattern(newSub):
                    print("Fatal Error : Wrong email Pattern Please Check Again")
                    pass
                else:
                    self.DBManager.addNewSub(newSub)
                    print("구독자 추가가 정상적으로 완료되었습니다.")
    
            elif opt == options.View_Subscriber_List:
                sublist = self.DBManager.returnSubscribers()
                print('\n' + '=' * 25)
                for o,p in enumerate(sublist,start = 1):
                    print(f'{o}. {p}')
                print('=' * 25 + "\n")
    
            elif opt == options.Delete_User:
                loop = True
                while loop:
                    deleteSub = input("삭제하고자 하는 구독자의 이메일 입력하기('exit'을 입력하면 종료합니다) : ")
                    if deleteSub == "exit":
                        loop = False
                    elif not self.checker.checkEmailPattern(deleteSub):
                        print("올바르지 않은 이메일 형식입니다. 다시 입력해주시기 바랍니다.")
                        pass
                    else:
                        try:
                            self.DBManager.deleteSub(deleteSub)
                            loop = False
                        except ValueError:
                            print("해당 이메일은 구독자 목록에 없습니다.")
                            loop = False
                            
            elif opt == options.Broadcast:
                title = input("Broadcast title : ")
                text = input("Broadcast content : ")
                subscriberList = self.DBManager.returnSubscribers()
                emailInfos = self.DBManager.returnMailInfo()[0]
                for i in subscriberList:
                    sendMail(i,text,title,emailInfos['HOSTERMAIL'],emailInfos['HOSTERMAILPW'])
            
            else:
                print("Service Close")
                break

                
if __name__=="__main__":
    try:
        adTool = adminTool()
        adTool.mainLoop()
    except BaseException as e:
        print(f"Error Occured : {e}")
