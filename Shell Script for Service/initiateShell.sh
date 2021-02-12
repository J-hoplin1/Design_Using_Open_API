#!/bin/bash

# This Shell is written standard at Ubuntu

echo "Check packages version and update."
#설치된 패키지들 새로운 버전확인
`sudo apt-get update`
#패키지 최신버전 업그레이드
`sudo apt-get upgrade`


#pip install
`sudo apt-get install python3-pip`
#install require packages
`pip3 install -r requirements.txt`

echo "Change server time standard at KST."
#서버 시간을 KST로 재설정
`sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime`
echo "Start Service Scheduler"
`python3 serviceScheduler.py`
#스케줄러 Background로
`bash processToBackground.sh`
#최종적으로 백그라운드 프로세스 확인
`ps -ef | grep python`
