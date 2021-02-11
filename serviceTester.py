import json
from functionModules.apiCaller import dataFromAPICall
from functionModules.smtpConnector import generateTextMime
from functionModules.patternChecker import patternChecker
from Datas.streamDatas import streamData
from enum import Enum
from urllib.parse import unquote

options = Enum('option',['Service_Test','Add_Subscriber','End'])

def selectOpt():
    opt = [f'{p.value}. {p.name}' for p in options]
    while True:
        print('-' * 15)
        for i in  opt:
            print(i)
        print('-' * 15)
        select = int(input(">> "))
        if 1<= select <= len(opt):
            return options(select)
apiKey = streamData.APIKEY
apiURL = streamData.APIURL
checker = patternChecker()

def initiateData():
    apiCallInstance = dataFromAPICall(unquote(apiKey),apiURL)
    apiCallInstance.buildRequests()

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
            print("구독자 추가가 정상적으로 완료되었습니다.")
            with open('Datas/subs.json','w') as f:
                json.dump(subs,f,indent = 4)
            
    else:
        print("Service Close")
        break
