'''
Code Written By hoplin

Latest update : 2021/03/29
License : MIT License(Open Source)
'''

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

    4. moveDataJsonToSQL : This method is for user who wants to upgrade version 'WithoutSQL'(https://github.com/J-hoplin1/Covid19_Mail_Service/tree/WithoutSQLVersion) to 'WithSQL'(https://github.com/J-hoplin1/Covid19_Mail_Service/tree/Server-Operating-Code-ver1). Helps to move json data to save SQL
        -> Please revise your json location before execute

    5. checkConnectionStatus : Check Status if this process(Code) connected with MySQL
    
    6. initateServiceDatas : Initiate Service executive Datas with reading yml file
    
    7. deleteDatabase : Delete Service Database

    '''
    class connectionExceptions(Exception):
        pass

    def __init__(self) -> None:
        self.sqlConnection = None # Variable : Save Connection Instance
        self.cursor = None # Variable : Save SQL Cursor
        self.ymlIns = None
        with open('config.yml') as f:
            self.ymlIns = yaml.load(f,yaml.FullLoader)
        self.getConnectionAndCursor()

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
        for ip in list(essentialDBList.keys()):
            print(f"\nInitiating Database {ip}\n")
            #Create database
            self.cursor.execute(f"CREATE DATABASE {ip}")
            #Make Cursor to use new generated Database : To initiate tables
            self.cursor.execute(f"USE {ip}")
            print("=" * 50)
            for up in list(essentialDBList[ip]):
                print(f"Initiating table {ip} - {up}")
                self.cursor.execute(essentialDBList[ip][up])
            print("=" * 50)
            self.initateServiceDatas()
    
    def initateServiceDatas(self) -> None:
        print("\nInitiating Service Datas. Please revise yml file after this work(sqlConnection - db).")
        self.cursor.execute("USE covid19MailServiceData")
        sqlState = f"""
            INSERT INTO adminDatas (APIKEY,APIURL,HOSTERMAIL,HOSTERMAILPW,BITLYKEY)
            VALUES (\'{self.ymlIns['serviceExecuteData']['apiKey']}\',\'{self.ymlIns['serviceExecuteData']['apiURL']}\',\'{self.ymlIns['serviceExecuteData']['hostermail']}\',\'{self.ymlIns['serviceExecuteData']['hostermailpw']}\',\'{self.ymlIns['serviceExecuteData']['bitlykey']}\');
        """
        self.cursor.execute(sqlState)
        self.sqlConnection.commit()

    def moveDataJsonToSQL(self):
        with open('Datas/subs.json', 'r') as f:
            subs = json.load(f)
        self.cursor.execute("USE covid19MailServiceData;")
        for mail in list(subs['subscribers']):
            self.cursor.execute(f'INSERT INTO subslist(email) VALUES(\'{mail}\')')
            self.sqlConnection.commit()

    def checkConnectionStatus(self):
        if self.sqlConnection:
            print("Still Connected!")
        else:
            print("Connection Failed. Reconnect to MySQL")
            self.getConnectionAndCursor()
    
    def deleteDatabase(self):
        self.cursor.execute("DROP DATABASE covid19MailServiceData")
    

option = Enum('option',["Initiate_Database_And_Move_Data","Only_Initiate_Database_Structure", "Only_Move_JSON_to_Database","Connection_Check","Delete_Database","Close"])

def selectOpt() -> Enum:
    opt = [f'{p.value}. {p.name}' for p in option]
    while True:
        print('-' * 20)
        for i in opt:
            print(i)
        print('-' * 20)
        try:
            select = int(input(">> "))
            if 1 <= select <= len(opt):
                return option(select)
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("비정상적인 종료입니다\n")
            pass

def loop() -> None:
    initiator = dataBaseInitiator()
    while True:
        opt = selectOpt()
        if opt == option.Initiate_Database_And_Move_Data:
            initiator.initiateEssentialDatabase()
            print("\nMove existing data to SQL\n")
            initiator.moveDataJsonToSQL()
        elif opt == option.Only_Initiate_Database_Structure:
            initiator.initiateEssentialDatabase()
        elif opt == option.Only_Move_JSON_to_Database:
            initiator.moveDataJsonToSQL()
        elif opt == option.Connection_Check:
            initiator.checkConnectionStatus()
        elif opt == option.Delete_Database:
            initiator.deleteDatabase()
        else:
            print("Initiator Close")
            break

if __name__ == "__main__":
    loop()
