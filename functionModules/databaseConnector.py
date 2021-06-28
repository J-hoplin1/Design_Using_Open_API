from urllib.parse import unquote
import pymysql as sql
import json
import yaml


class SQLConnectorManager(object):
    def __init__(self):
        with open('../config.yml') as f:
            self.ymlIns = yaml.load(f,yaml.FullLoader)
        # Connect to MySQL and read Sub list
        self.sqlCNT = sql.connect(
            user=f"{self.ymlIns['sqlConnection']['user']}",
            password=f"{self.ymlIns['sqlConnection']['password']}",
            host=f"{self.ymlIns['sqlConnection']['host']}",
            db = f"{self.ymlIns['sqlConnection']['db']}"
        )
        # Define SQL Cursor 
        self.cursor = self.sqlCNT.cursor(sql.cursors.DictCursor)
    
    # Initiate streamDatas.py
    def functionDatasInitiater(self):
        sqlState = "SELECT * FROM adminDatas"
        self.cursor.execute(sqlState)
        return self.cursor.fetchall()
    
    def returnSubscribers(self):
        sqlState = f'SELECT * FROM subslist'
        self.cursor.execute(sqlState)
        datas = self.cursor.fetchall()
        li = []
        for i in datas:
            li.append(i['email'])
        return li
    
    def returnMailInfo(self):
        sqlState = f'SELECT HOSTERMAIL,HOSTERMAILPW FROM adminDatas'
        self.cursor.execute(sqlState)
        return self.cursor.fetchall()
    
    def addNewSub(self, mail):
        # SQL statement : Register new subscriber to database
        sqlState = f'INSERT INTO subslist(email) VALUES(\'{mail}\')'
        self.cursor.execute(sqlState)
        # Commit change to SQL
        self.sqlCNT.commit()
        
    def deleteSub(self, mail):
        # SQL statement : Delete subscribers from database
        sqlState = f'DELETE FROM subslist WHERE email = \'{mail}\''
        self.cursor.execute(sqlState)
        self.sqlCNT.commit()

if __name__=="__main__":
    a = SQLConnectorManager()
    print(a.returnMailInfo()[0])
