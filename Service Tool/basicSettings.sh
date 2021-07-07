#!/bin/bash

#install require packages
echo `pip3 install -r requirements.txt`

echo "Change server time standard at KST."
#서버 시간을 KST로 재설정
echo `sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime`
echo `clear`
echo "Required Settings Complete!"