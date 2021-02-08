import requests
from typing import AnyStr
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus, unquote
from urllib.request import Request
from datetime import datetime, timedelta
from lxml import html, etree
import xml.etree.ElementTree as et


'''
urllib.parse.unquote(string, encoding='utf-8', errors='replace')¶
%xx 이스케이프를 동등한 단일 문자로 대체합니다. 선택적 encoding과 errors 매개 변수는 bytes.decode() 메서드에서 받아들이는 것처럼 퍼센트 인코딩된 시퀀스를 유니코드 문자로 디코딩하는 방법을 지정합니다.

string은 str이나 bytes 객체일 수 있습니다.

encoding의 기본값은 'utf-8'입니다. errors의 기본값은 'replace'로, 유효하지 않은 시퀀스는 자리 표시자 문자(placeholder character)로 대체됩니다.

예: unquote('/El%20Ni%C3%B1o/')는 '/El Niño/'를 산출합니다.
'''


apiKey = unquote('bj9OInFd8JfcavWNdVhUfOLalfpaYG1N6wqkFTbKVzPwR0EkEj5pL55HrsPX6Nye4gREdN3InXTi2pv39h%2FgTQ%3D%3D')
apiCall = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson'


def buildRequests(): 
    # 코드 실행한 시점
    executedPoint = datetime.today()
    endDate = executedPoint + timedelta(days = 1)
    #시작범위
    searchStart = executedPoint.strftime("%Y%m%d") # strftime으로 포맷을 맞추어준다."%Y%m%d" : YYYYMMDD형태로 출력
    #끝범위
    searchEnd = endDate.strftime("%Y%m%d") # 끝범위를 다음날로 해줘야 오늘 날짜에 대한 값만 나온다.

    #Request Query를 만든다.
    queryParameter = '?' + urlencode({
        quote_plus('serviceKey') : apiKey,
        quote_plus('pageNo') : 1,
        quote_plus('numOfRows') : 10,
        quote_plus('startCreateDt') : searchStart,
        quote_plus('endCreateDt') : searchEnd
    })
    response = requests.get(apiEndPoint + queryParameter).text.encode('utf-8')
    response = response.decode('utf-8') # bytestring to Normal String
    res = et.ElementTree(et.fromstring(response))  # Make string xml value to xml tree
    res.write('Result.xml') # save xml
    
    
buildRequests()
