import re
import smtplib as smt
from email.mime.multipart import MIMEMultipart # 다양한 형식(text,img,audio) 중첩하여 담기위한 객체
from email import encoders # message contents to binary
from email.mime.text import MIMEText # 텍스트형식
# MIME : Multipurpose Internet Mail Extensions의 약자로 전자우편을 위한 인터넷 표준 포맷이다.
from datetime import datetime
from .patternChecker import patternChecker
from pytz import timezone
from .textMaker import makeText

# Pattern Checker Instance
checker = patternChecker()

def mailSend(smtpReqDatas, message,receiver) -> None:
    with smt.SMTP(smtpReqDatas["server"], smtpReqDatas["SMTPPort"]) as server:
        server.starttls() # Transport Layer Security Connection
        server.login(smtpReqDatas["hostersEmail"], smtpReqDatas["hostersEmailPW"]) # login to smpt server
        responseSignal = server.sendmail(message['From'], message['To'], message.as_string())
        if not responseSignal:
            print(f"MessageSend Completed to {receiver}")
        else:
            print(f'{responseSignal}')
        
def generateTextMime(receiver) -> None:
    textMakerInstance = makeText()
    if not checker.checkEmailPattern(receiver):
        print("Fatal Error : Wrong email Pattern Please Check Again")
        return
    
    smtpReqDatas = {
        "server" : 'smtp.naver.com',
        "hostersEmail" : "", # Hoster's E-mail Address here (Naver Mail)
        "hostersEmailPW" : '', # Hoster's E-mail PW here
        "SMTPPort" : 587
    }
    title = f"{datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')} 코로나 19 데이터"
    paragraph = textMakerInstance.makeText()
    hoster = "" # Hoster's E-mail Address
    reveive = receiver
    
    message = MIMEText(_text = paragraph, _charset = "utf-8")
    message['Subject'] = title
    message['From'] = hoster
    message['To'] = reveive
    mailSend(smtpReqDatas, message,receiver)