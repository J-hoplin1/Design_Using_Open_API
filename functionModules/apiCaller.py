import requests
import json
import re
import ssl
from pytz import timezone
from typing import Any, MutableSequence
from bs4 import BeautifulSoup
from .getBitlyLink import letsGetBitlyShortURL
from urllib.parse import urlencode, quote_plus, unquote
from urllib.request import Request, urlopen
from datetime import datetime, timedelta
from lxml import html, etree
import xml.etree.ElementTree as et
from xml.dom import minidom # To save XML Data Pretty

class dataFromAPICall(object):
    """
    이 클래스는 Open API로 Request한 후 Response로 받아오는 XML을 전처리하여 JSON파일로 정리합니다.
    
    1) __init__(self,apiKey,apiCall)
    
    인스턴스 기본값을 초기화 합니다.
    
    param1 - apiKey : apiKey값을 저장합니다
    param2 - apiCall : api 호출 URL을 받습니다.
    
    2) buildRequests(self)
    
    request를 위한 기본 URL 쿼리문을 만듭니다.
    시작범위는 어제날짜로, 끝범위는 내일 날짜로 합니다. 오늘 데이터와 어제 데이터를 비교하여 금일 확진자 증가량을 파악합니다
    
    3) reProcessXML(self,stringXML : str)
    
    XML을 BeautifulSoup 객체로 만든 후 lxml-xml 파서를 이용해서 XML데이터를 파싱합니다. 그 후 필요한 데이터들로 딕셔너리를 만듭니다.
    
    param1 - stringXML : string타입 XML을 매개변수로 받습니다.
    
    4) def dumpToJSON(self, dicInstance : MutableSequence)
    
    reProcessXML()메소드로부터 받은딕셔너리를 JSON으로 dump합니다.
    
    
    """
    
    def __init__(self,apiKey,apiCall,bitlyKey):
        self.apiKey = apiKey
        self.apiCall = apiCall
        self.bitlyKey = bitlyKey
        self.getShortLink = letsGetBitlyShortURL(bitlyKey)
        # initiate instance's GUID while initiate api class
        self.getShortLink.getGUID()

    def buildRequests(self) -> BeautifulSoup: 
        # 코드 실행한 시점
        executedPoint = datetime.now(timezone('Asia/Seoul'))
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
        res = BeautifulSoup(response, 'lxml-xml')
        return res

    def addMainNews(self) -> MutableSequence:
        # ssl 인증문제에 대한 해결
        context = ssl._create_unverified_context()
        covidSite = "http://ncov.mohw.go.kr/index.jsp"
        covidNotice = "http://ncov.mohw.go.kr"
        html = urlopen(covidSite,context=context)
        bs = BeautifulSoup(html, 'html.parser')
        # Bug fix 2021 03 02 : 파싱 구역 지정을 조금 더 구체화하였습니다 -> 카드 뉴스로 인한 방해
        bs = bs.find('div',{'class' : 'm_news'})
        sounds = []
        briefTasks = dict()
        hotIssues = dict()
        mainbrief = bs.findAll('a',{'href' : re.compile('\/tcmBoardView\.do\?contSeq=[0-9]*')})
        for brf in mainbrief:
            briefTasks[brf.text] = self.getShortLink.getshortenURL(covidNotice + brf['href'])
        sounds.append(briefTasks)
        hotIssue = bs.findAll('a',{'href' : re.compile('https\:\/\/www\.korea\.kr\/[\w?=]+')})
        for u in hotIssue:
            hotIssues[u.text] = u['href']
        sounds.append(hotIssues)
        return sounds
        
    def reProcessXML(self,BSXML : BeautifulSoup) -> bool:
        res = BSXML# lxml-xml 매우빠르고 유일하게 지원되는 XML파서이다.
        item = res.findAll('item')
        if len(item) < 2:
            return False
        else:
            print("API data updated successfully. Progress process")
            dayBefore = item[1]
            today = item[0]
        news = self.addMainNews()

        # 브리핑 관련 데이터
        briefings = news[0]
        briefTopics = list(briefings.keys())
        #주요 이슈관련 데이터
        hotIssues = news[1]
        issueTopics = list(hotIssues.keys())
        dataDictionary = {
            'dataDate' : datetime.strptime(today.find('stateDt').text,"%Y%m%d").date().strftime("%Y-%m-%d"),
            'data' : {
                'totalDecidedPatient' : today.find('decideCnt').text,
                'todayDecidedPatient' : str(int(today.find('decideCnt').text) - int(dayBefore.find('decideCnt').text)),
                'totalDeath' : today.find('deathCnt').text,
                'increasedDeath' : str(int(today.find('deathCnt').text) - int(dayBefore.find('deathCnt').text)),
                'CumulatedConfirmPercentage' : today.find('accDefRate').text 
            },
            'briefing' : {},
            'hotIssue' : {}
        }
        for i,o in enumerate(briefTopics, start = 1):
            dataDictionary['briefing']['briefTopics{}'.format(i)] = [o , briefings[o]]
        for i,o in enumerate(issueTopics, start = 1):
            dataDictionary['hotIssue']['issueTopics{}'.format(i)] = [o , hotIssues[o]]
        self.dumpToJSON(dataDictionary)
        return True
    
    def dumpToJSON(self, dicInstance : MutableSequence) -> None:
        with open('../Datas/smtpSendDatas.json','w') as f:
            json.dump(dicInstance,f,ensure_ascii=False, indent = 4)
