import json
from functionModules.apiCaller import dataFromAPICall
from functionModules.smtpConnector import generateTextMime
from functionModules.patternChecker import patternChecker
from Datas.streamDatas import streamData
from enum import Enum
from urllib.parse import unquote

options = Enum('option',['Service_Test','Add_Subscriber','Delete_User','View_Subscriber_List','End'])

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
        
        
apiKey = streamData.APIKEY
apiURL = streamData.APIURL
checker = patternChecker()

def initiateData():
    apiCallInstance = dataFromAPICall(apiKey,apiURL)
    apiCallInstance.reProcessXML(apiCallInstance.buildRequests())

while True:
    opt = selectOpt()
    if opt == options.Service_Test:
        with open('Datas/subs.json','r') as f:
            subs = json.load(f)
        subscriberList = subs['subscribers']
        initiateData()
        for i in subscriberList:
            generateTextMime(i)
    elif opt == options.Add_Subscriber:
        with open('Datas/subs.json','r') as f:
            subs = json.load(f)
        newSub = input("새 구독자의 이메일 입력하기 : ")
        if not checker.checkEmailPattern(newSub):
            print("Fatal Error : Wrong email Pattern Please Check Again")
            pass
        else:
            subs['subscribers'].append(newSub)
            subs['subscribers'] = list(set(subs['subscribers']))
            print("구독자 추가가 정상적으로 완료되었습니다.")
            with open('Datas/subs.json','w') as f:
                json.dump(subs,f,indent = 4)
    
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
            elif not checker.checkEmailPattern(deleteSub):
                print("올바르지 않은 이메일 형식입니다. 다시 입력해주시기 바랍니다.")
                pass
            else:
                try:
                    sublist.remove(deleteSub)
                    subs['subscribers'] = sublist
                    print("삭제가 정상적으로 완료되었습니다.")
                    with open('Datas/subs.json','w') as f:
                        json.dump(subs,f,indent = 4)
                    loop = False
                except ValueError:
                    print("해당 이메일은 구독자 목록에 없습니다.")
                    loop = False
    else:
        print("Service Close")
        break
