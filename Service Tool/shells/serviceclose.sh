#!/bin/bash


getPID=`ps -ef | grep 'scheduler.py' | grep -v 'grep' | awk '{print $2}'`
echo `kill -15 $getPID`