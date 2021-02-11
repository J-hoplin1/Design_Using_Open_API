import re

class patternChecker(object):
    """
    이 클래스는 입력된 혹은 매개변수로 받은 이메일 패턴을 정규표현식(Regular Expression)검사를 통해 맞는지 틀리는지 검사해줍니다.
    
    1) checkEmailPattern(self,receiver)
    
    param1 - receiver : 검사할 메일 주소입니다
    
    parameter receiver에 대한 이메일 패턴 검사를 합니다. 틀릴경우 None을 반환합니다.
    """
    def checkEmailPattern(self,receiver):
        emailPattern = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        return emailPattern.match(receiver) != None
