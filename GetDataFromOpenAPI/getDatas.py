import requests
import json
from typing import Any, MutableSequence
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus, unquote
from urllib.request import Request
from datetime import datetime, timedelta
from lxml import html, etree
import xml.etree.ElementTree as et
from xml.dom import minidom # To save XML Data Pretty

class dataFromAPICall(object):
    
    
    def __init__(self,apiKey,apiCall):
        self.apiKey = apiKey
        self.apiCall = apiCall

    def buildRequests(self) -> str: 
        # 코드 실행한 시점
        executedPoint = datetime.today()
        endDate = executedPoint + timedelta(days = 1)# 하루뒤의 시간을 의미한다.
        executedPoint = executedPoint + timedelta(days = -1)
        #시작범위
        searchStart = executedPoint.strftime("%Y%m%d") # strftime으로 포맷을 맞추어준다."%Y%m%d" : YYYYMMDD형태로 출력
        #끝범위
        searchEnd = endDate.strftime("%Y%m%d") # 끝범위를 다음날로 해줘야 오늘 날짜에 대한 값만 나온다.

        #Request Query를 만든다.
        queryParameter = '?' + urlencode({
            quote_plus('serviceKey') : self.apiKey,
            quote_plus('pageNo') : 1,
            quote_plus('numOfRows') : 10,
            quote_plus('startCreateDt') : searchStart,
            quote_plus('endCreateDt') : searchEnd
        })
        response = requests.get(self.apiCall + queryParameter).text.encode('utf-8') # 기본적으로 requests를 인코딩한 반환값은 Byte String이 나오게 된다.
        response = response.decode('utf-8') # bytestring to Normal String
        self.reProcessXML(response)

    def reProcessXML(self,stringXML : str) -> None:
        res = BeautifulSoup(stringXML, 'lxml-xml') # lxml-xml 매우빠르고 유일하게 지원되는 XML파서이다.
        item = res.findAll('item')
    
        dayBefore = item[1]
        today = item[0]
    
        dataDictionary = {
            'dataDate' : datetime.strptime(today.find('stateDt').text,"%Y%m%d").date().strftime("%Y-%m-%d"),
            'data' : {
                'totalDecidedPatient' : today.find('decideCnt').text,
                'todayDecidedPatient' : str(int(today.find('decideCnt').text) - int(dayBefore.find('decideCnt').text)),
                'totalDeath' : today.find('deathCnt').text,
                'CumulatedConfirmPercentage' : today.find('accDefRate').text 
            }   
        }
        self.dumpToJSON(dataDictionary)
    
    def dumpToJSON(self, dicInstance : MutableSequence):
        with open('smtpSendDatas.json','w') as f:
            json.dump(dicInstance,f,indent=4)
    
    
if __name__ == "__main__":
    apiCalls = dataFromAPICall(unquote('bj9OInFd8JfcavWNdVhUfOLalfpaYG1N6wqkFTbKVzPwR0EkEj5pL55HrsPX6Nye4gREdN3InXTi2pv39h%2FgTQ%3D%3D'),'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson')
    apiCalls.buildRequests()
