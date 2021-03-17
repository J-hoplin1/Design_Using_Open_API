import os
import json
import shutil
import datetime
from functionModules.apiCaller import dataFromAPICall
from functionModules.smtpConnector import *
from functionModules.patternChecker import patternChecker
from functionModules.databaseConnector import SQLConnectorManager
from Datas.streamDatas import streamData
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
        # Initiate subscriber data : Generate subs.json
        self.DBManager.generateSublist()
        self.DBManager.functionDatasInitiater(streamData)
        self.apiKey = streamData.APIKEY
        self.apiURL = streamData.APIURL
        self.bitlyKey = streamData.BITLYKEY
    
    def initiateData(self):
        apiCallInstance = dataFromAPICall(self.apiKey,self.apiURL,self.bitlyKey)
        apiCallInstance.reProcessXML(apiCallInstance.buildRequests())
    
    def mainLoop(self):
        while True:
            opt = selectOpt()
            if opt == options.Service_Test:
                with open('Datas/subs.json','r') as f:
                    subs = json.load(f)
                subscriberList = subs['subscribers']
                self.initiateData()
                for i in subscriberList:
                    generateTextMime(i)
            elif opt == options.Add_Subscriber:
                with open('Datas/subs.json','r') as f:
                    subs = json.load(f)
                newSub = input("새 구독자의 이메일 입력하기 : ")
                if not self.checker.checkEmailPattern(newSub):
                    print("Fatal Error : Wrong email Pattern Please Check Again")
                    pass
                else:
                    self.DBManager.addNewSub(newSub)
                    print("구독자 추가가 정상적으로 완료되었습니다.")
    
            elif opt == options.View_Subscriber_List:
                with open('Datas/subs.json','r') as f:
                    subs = json.load(f)
                sublist = subs['subscribers']
                print('\n' + '=' * 25)
                for o,p in enumerate(sublist,start = 1):
                    print(f'{o}. {p}')
                print('=' * 25 + "\n")
    
            elif opt == options.Delete_User:
                with open('Datas/subs.json','r') as f:
                    subs = json.load(f)
                sublist = subs['subscribers']
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
            # Add backup
            elif opt == options.Backup:
                try:
                    try:
                        if not os.path.exists('Backup'):
                            os.makedirs('Backup')
                        else:
                            pass
                    except OSError as e:
                        print("Error Occured While generating directory 'Backup'")
                    shutil.copyfile('Datas/subs.json', f'Backup/subs.json')
            
                except BaseException as e:
                    print("Backup Failed.")
                    pass
            elif opt == options.Broadcast:
                title = input("Broadcast title : ")
                text = input("Broadcast content : ")
                with open('Datas/subs.json','r') as f:
                    subs = json.load(f)
                subscriberList = subs['subscribers']
                for i in subscriberList:
                    sendMail(i,text,title)
            
            else:
                print("Service Close")
                os.remove('Datas/subs.json')
                break

                
if __name__=="__main__":
    try:
        adTool = adminTool()
        adTool.mainLoop()
    except BaseException as e:
        print(f"Error Occured : {e}")
        os.remove('Datas/subs.json')
