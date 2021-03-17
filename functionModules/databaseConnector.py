from urllib.parse import unquote
import pymysql as sql
import json


class SQLConnectorManager(object):
    def __init__(self):
        # Connect to MySQL and read Sub list
        self.sqlCNT = sql.connect(
            user = '', # SQL Access User 
            password = '', # SQL User Password
            host = '', # SQL location address
            db = '',
        )
        # Define SQL Cursor 
        self.cursor = self.sqlCNT.cursor(sql.cursors.DictCursor)
    
    def generateSublist(self):
        # SQL Statement : Get subscriber list 
        sqlState = "SELECT email FROM subslist"
        # Execute SQL Statement with cursor
        self.cursor.execute(sqlState)
        # Get List Value :  Each value has type of dictionary value
        emailList = self.cursor.fetchall()
        emailList = [x['email'] for x in emailList]
        
        # Basic JSON prototype
        jsonProto = {
            "subscribers" : emailList
        }
        # Save subs.json
        with open('Datas/subs.json','w') as i:
            json.dump(jsonProto,i,indent = 4)
    
    # Initiate streamDatas.py
    def functionDatasInitiater(self,instance):
        sqlState = "SELECT * FROM adminDatas"
        self.cursor.execute(sqlState)
        datas = self.cursor.fetchall()
        instance.APIKEY = unquote(datas[0]['APIKEY'])
        instance.APIURL = datas[0]['APIURL']
        instance.HOSTEREMAIL = datas[0]['HOSTERMAIL']
        instance.HOSTEREMAILPW = datas[0]['HOSTERMAILPW']
        instance.BITLYKEY = datas[0]['BITLYKEY']
    
    def addNewSub(self, mail):
        # SQL statement : Register new subscriber to database
        sqlState = f'INSERT INTO subslist(email) VALUES(\'{mail}\')'
        self.cursor.execute(sqlState)
        # Commit change to SQL
        self.sqlCNT.commit()
        # Reload subs.json
        self.generateSublist()
        
    def deleteSub(self, mail):
        # SQL statement : Delete subscribers from database
        sqlState = f'DELETE FROM subslist WHERE email = \'{mail}\''
        self.cursor.execute(sqlState)
        self.sqlCNT.commit()
        # Reload subs.json
        self.generateSublist()
