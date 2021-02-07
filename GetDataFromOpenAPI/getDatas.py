import requests
from typing import AnyStr
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
from urllib.request import Request
from datetime import datetime, timedelta
from lxml import html
from xml.etree.ElementTree import ElementTree

apiKey = ''
apiEndPoint = 'http://openapi.data.go.kr/openapi/service/rest/Covid19'


def buildRequests(): 
    # 코드 실행한 시점
    executedPoint = datetime.today()
    endDate = executedPoint + timedelta(days = 1)
    #시작범위
    searchStart = executedPoint.strftime("%Y%m%d") # strftime으로 포맷을 맞추어준다."%Y%m%d" : YYYYMMDD형태로 출력
    #끝범위
    searchEnd = endDate.strftime("%Y%m%d")

    #Request
    queryParameter = '?' + urlencode({
        quote_plus('serviceKey') : apiKey,
        quote_plus('numOfRows') : 1,
        quote_plus('pageNo') : 10,
        quote_plus('startCreateDt') : searchStart,
        quote_plus('endCreateDt') : searchEnd
    })
    response = requests.get(apiEndPoint + queryParameter).text.encode('utf-8')
    xmlResponse = BeautifulSoup(response, 'lxml-xml')

buildRequests()
