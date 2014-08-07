# -*- coding: cp936 -*-
import cx_Oracle
import gl
#import datetime

class IOrc:
    def __init__(self):
        self.conn = gl.orcpool.connection()
        self.cur  = self.conn.cursor()
        
    def __del__(self):
        try:
            self.conn.close()
        except Exception,e:
            pass

    def getCltxBySql(self,sql):
        try:
            self.cur.execute(sql)
        except Exception,e:
            raise
        else:
            return self.rowsToDictList()
        
    def rowsToDictList(self):
        columns = [i[0] for i in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur]

    def orcCommit(self):
        self.conn.commit()

if __name__ == "__main__":
    
    orc = Orc()
    #values = []
    orc.setupOrc()
    #time = datetime.datetime(2013,3,3,01,01,01)
    #orc.addFuzzy(time,'粤L123%')
    s = orc.getCltxBySql('select TJTP from cltx where id = 190362204')
    for i in s:
        print i
    del orc
