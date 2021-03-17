import sys
import re
import requests
import json
from typing import MutableSequence


class letsGetBitlyShortURL(object):
    '''
    1) __init__ : 두가지의 API End Point가 초기화됩니다.
    
    - self.groupGUID는 group_gguid를 얻기 위한 api end point입니다
    
    - self.getShorten는 bitly단축 url을 얻기위한 api end point입니다
    
    2) getGUID() : bitly GUID값을 반환합니다. GUID는 전역고유식별자(Global Unique Identifier)는 응용 SW에서 사용되는 유사난수입니다. 
    
    - GUID Group에 대한 Documentation : https://dev.bitly.com/api-reference#getGroups
    
    - Request HTTP Method : GET
    
    3) getshortenURL() : bitly의 단축 URL을 반환합니다
    
    - 이 부분에 대한 Documentation : https://dev.bitly.com/api-reference#createBitlink
    
    - 필수 Parameter
    
      1) long_url : 단축하고자 링크의 primitive URL
      
      2) domain : "bit.ly"
      
      3) group_guid : GUID
    
    - Request HTTP Method : POST
    
    4) urlPatternMather() : 입력된 URL 매개변수가 URL이 맞는지 확인합니다.
    
    5) autoStream() : 인스턴스 생성시 전달된 MutableSequence의 모든 URL의 bitly shorten URL을 반환합니다.
    '''
    
    #ExceptionClass Based on status code of API Call
    class bitlyAPIResCode(Exception):
        pass
    
    class urlNotMatch(Exception):
        pass
    
    def __init__(self, key) -> None:
        self.groupGUID = "https://api-ssl.bitly.com/v4/groups" 
        self.getShorten = 'https://api-ssl.bitly.com/v4/shorten'
        self.GUID = None
        self.key = key
    
    
    def getGUID(self) -> None:
        headers = {
            'Authorization' : f'Bearer {self.key}'
        }
        r = requests.get(self.groupGUID,headers = headers)
        if int(r.status_code) >= 400:
            print(f"Something went wrong while API Call : Status Code {r.status_code}")
            print("Force Close : Exception Occured")
            raise letsGetBitlyShortURL.bitlyAPIResCode
        responseJSON = r.json()
        '''
        json.dumps(): Python객체를 JSON데이터로 쓰기, 직렬화, 인코딩 (Write Python object to JSON, serialization, Encodig)
        json.loads() : JSON포맷 데이터를 Pyrhon객체로 읽기,역직렬화, 디코딩 (Read JSON to Python, Deserialization, Decoding)
        '''
        # rp = json.dumps(responseJSON,indent=4) #View JSON Structure
        self.GUID = responseJSON["groups"][0]["guid"]
    
    def getshortenURL(self, URL) -> str:
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
        }
        data = {
            "long_url" : URL ,
            "domain" : "bit.ly",
            "group_guid" : self.GUID
        }
        r = requests.post(self.getShorten, headers=headers, json = data)
        responseJSON = r.json()
        #rp = json.dumps(responseJSON,indent=4)
        return responseJSON["link"]
    
    def urlPatternMather(self,URL) -> bool:
        urlPatternRegex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        # None이 반환되는 경우 패턴 불일치
        return urlPatternRegex.match(URL) != None
    
    def autoStream(self) -> MutableSequence:
        capsule = []
        passed = 0
        success = 0
        for i in self.urlList:
            if not self.urlPatternMather(i):
                passed += 1
                raise letsGetBitlyShortURL.urlNotMatch
            else:
                capsule.append(self.getshortenURL(i))
                success += 1
        print(f'Completed! Success : {success} / Failed : {passed}')
        return capsule
