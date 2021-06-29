'''
Code Written By hoplin

Latest update : 2021/03/29
License : MIT License(Open Source)
'''
import re
import yaml
import pymysql as sql
import json
from enum import Enum

class dataBaseInitiator(object):
    '''
    DataBaseInitiator Document

    Classify : System tool - Database
    Using SQL Type : RDBMS - MySQL, Query Lang
    What for? : This code is Database structure initiator before service start

    Exception Class

    1. connectionExceptions : Return error Message if connection fails or connection not maintained

    Methods

    1. __init__ : Initiate Essential Variables for methods. Make basic connection.

    2. getConnectionAndCursor : Make a Connection with MySQL Server and Initiate MySQL Remote Cursor

    3. initiateEssentialDatabase : Have variable "essentialDBList". This variables contains essential database name and it's 'tablename' and 'tableQuery'. Just revise this dictionary if you want to change service Database structure
    
    4. initateServiceDatas : Initiate Essential Values for this service
    
        - Public API Key (for data.go.kr)
        - Public API URL
        - Bitly API Key
        - Hoster Email
        - Hoster PW

    '''
    class connectionExceptions(Exception):
        pass

    def __init__(self) -> None:
        self.sqlConnection = None # Variable : Save Connection Instance
        self.cursor = None # Variable : Save SQL Cursor
        self.ymlIns = None
        '''
        Read configuration yaml file
        '''
        with open('../config.yml','r') as f:
            self.ymlIns = yaml.load(f,yaml.FullLoader)
        self.ymlIns['sqlConnection']['db'] = 'covid19MailServiceData'
        self.getConnectionAndCursor()
        '''
        save yaml file after get Connection -> save database name
        '''
        with open('../config.yml','w') as f:
            yaml.dump(self.ymlIns,f,default_flow_style=False)
        
    def getConnectionAndCursor(self) -> None:
        self.sqlConnection = sql.connect(
            user=f"{self.ymlIns['sqlConnection']['user']}",
            password=f"{self.ymlIns['sqlConnection']['password']}",
            host=f"{self.ymlIns['sqlConnection']['host']}"
        )
        self.cursor = self.sqlConnection.cursor(sql.cursors.DictCursor)

    def initiateEssentialDatabase(self) -> None:
        essentialDBList = {
            'covid19MailServiceData' : {
                "subsList" : """
                CREATE TABLE subslist(
                    ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                    email VARCHAR(70) NOT NULL
                );
                """,
                "serviceExecuteDatas" : """
                CREATE TABLE adminDatas(
                    APIKEY VARCHAR(150),
                    APIURL VARCHAR(300),
                    HOSTERMAIL VARCHAR(100),
                    HOSTERMAILPW VARCHAR(100),
                    BITLYKEY VARCHAR(100)
                );
                """
            }
        }
        print(f"\nInitiating Database 'covid19MailServiceData'\n")
        #Create database
        self.cursor.execute(f"CREATE DATABASE covid19MailServiceData")
        #Make Cursor to use new generated Database : To initiate tables
        self.cursor.execute(f"USE covid19MailServiceData")
        print("=" * 50)
        for up in list(essentialDBList['covid19MailServiceData']):
            print(f"Initiating table covid19MailServiceData - {up}")
            self.cursor.execute(essentialDBList['covid19MailServiceData'][up])
        print("=" * 50)
        self.initateServiceDatas()
    
    def initateServiceDatas(self) -> None:
        print("\nInitiating Service Datas.")
        self.cursor.execute("USE covid19MailServiceData")
        publicAPIKey = input("Public API Key 입력하기 : ")
        apiURL = input("Public API End Point주소를 입력하기 : ")
        hostermail = input("송신 Email 입력하기 : ")
        hosteremailPW = input("송신 Email의 PW 입력하기 : ")
        bitlykey = input("bitly API Key 입력하기 : ")
        sqlState = f"""
            INSERT INTO adminDatas (APIKEY,APIURL,HOSTERMAIL,HOSTERMAILPW,BITLYKEY)
            VALUES (\'{publicAPIKey}\',\'{apiURL}\',\'{hostermail}\',\'{hosteremailPW}\',\'{bitlykey}\');
        """
        self.cursor.execute(sqlState)
        self.sqlConnection.commit()
        print("DataBase 초기화 완료!")
    
    def changeValues(self,opts) -> None:
        selected = {
            keys.Public_API_Key : 'APIKEY',
            keys.Public_API_EndPoint : 'APIURL',
            keys.HosterMail : 'HOSTERMAIL',
            keys.HosterMailPW : 'HOSTERMAILPW',
            keys.BitlyKey : 'BITLYKEY'
        }
        def executeState(slt):
            newValue = input(f"변경할 {slt}입력하기 : ")
            self.cursor.execute(f"USE covid19MailServiceData")
            self.cursor.execute(f"UPDATE adminDatas SET {slt}=\'{newValue}\'")
            self.sqlConnection.commit()
        
        if opts == keys.Public_API_Key:
            executeState(selected[opts])
        elif opts == keys.Public_API_EndPoint:
            executeState(selected[opts])
        elif opts == keys.HosterMail:
            executeState(selected[opts])
        elif opts == keys.HosterMailPW:
            executeState(selected[opts])
        elif opts == keys.BitlyKey:
            executeState(selected[opts])
        else:
            pass
        
    def checkConnectionStatus(self):
        if self.sqlConnection:
            print("Still Connected!")
        else:
            print("Connection Failed. Reconnect to MySQL")
            self.getConnectionAndCursor()
    
    def deleteDatabase(self):
        self.cursor.execute("DROP DATABASE covid19MailServiceData")
    

option = Enum('option',["Initiate_Database_Structure",
                        "Delete_Database",
                        "Edit_Keys",
                        "Close"])
keys = Enum('keys',["Public_API_Key",
                   "Public_API_EndPoint",
                   "HosterMail",
                   "HosterMailPW",
                   "BitlyKey",
                   "Close"])

def selectOpt(enums) -> Enum:
    options = [f'{p.value}. {p.name}' for p in enums]
    while True:
        print('-' * 20)
        for i in options:
            print(i)
        print('-' * 20)
        try:
            select = int(input(">> "))
            if 1 <= select <= len(options):
                return enums(select)
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("비정상적인 종료입니다\n")
            pass

def loop() -> None:
    initiator = dataBaseInitiator()
    while True:
        opt = selectOpt(option)
        if opt == option.Initiate_Database_Structure:
            initiator.initiateEssentialDatabase()
        elif opt == option.Edit_Keys:
            opts = selectOpt(keys)
            initiator.changeValues(opts)
        elif opt == option.Delete_Database:
            initiator.deleteDatabase()
        else:
            print("Initiator Close")
            break

if __name__ == "__main__":
    try:
        loop()
    except sql.err.ProgrammingError as e:
        print("Database already exist! Please check again.")
