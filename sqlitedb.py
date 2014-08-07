# -*- coding: cp936 -*-

import sqlite3
import gl

def sqlitePool(db,maxu=1000):
    gl.sqlitepool = PersistentDB(
        sqlite3,
        maxusage = maxu,
        database = db)

##def unix2datetime(unix):   
##    return datetime.datetime.fromtimestamp(unix)

class Sqlite:
    def __init__(self):
        self.conn = gl.sqlitepool.connection()
        self.cur  = self.conn.cursor()
            
    def __del__(self):
        try:
            self.conn.close()
            self.cur.colse()
        except Exception,e:
            pass

    def createTable(self):
        sql = '''CREATE TABLE IF NOT EXISTS "imgdownload" (
                "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                "timeflag"  INTEGER,
                "sqlstr"  TEXT,
                "path"  TEXT,
                "banned"  INTEGER NOT NULL DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS "index_banned"
                ON "imgdownload" ("banned" ASC);
                
                CREATE INDEX IF NOT EXISTS "index_timeflag"
                ON "imgdownload" ("timeflag" ASC);
                '''

        self.cur.executescript(sql)
        self.conn.commit()

    def executeSql(self,sql):
        try:
            self.cur.execute(sql)
            s = self.cur.fetchall()
        except sqlite3.Error as e:
            raise
        else:
            self.conn.commit()
            return s

    #1
    #根据条件获取图片下载记录
    def getImgdownload(self,_time,banned=0):
        try:
            self.cur.execute("select * from imgdownload where banned=%s and timeflag<=%s"%(banned,_time))
            s = self.cur.fetchall()
        except sqlite3.Error as e:
            raise
        else:
            self.conn.commit()
            return s

    #2
    #根据ID更新图片下载记录
    def updateImgdownloadByID(self,id,banned=1):
        try:
            self.cur.execute("update imgdownload set banned=%s where id=%s"%(banned,id))
            self.conn.commit()
        except sqlite3.Error as e:
            raise

    #3
    #添加一条图片下载记录并返回ID
    def addImgdownload(self,_time,_sql,path=''):
        try:
            sql = _sql.replace("'","''")
            self.cur.execute("INSERT INTO imgdownload(timeflag,sqlstr,path) VALUES(%s,'%s','%s')"%(_time,sql,path))
            self.cur.execute("SELECT last_insert_rowid()")
            self.conn.commit()
            s = self.cur.fetchone()
        except sqlite3.Error as e:
            raise
        else:
            return s

    def test(self):
        try:
            self.cur.execute("SELECT last_insert_rowid()")
            self.conn.commit()
            s = self.cur.fetchone()
        except sqlite3.Error as e:
            raise
        else:
            return s
        
    def endOfCur(self):
        self.conn.commit()
        
    def sqlCommit(self):
        self.conn.commit()
        
    def sqlRollback(self):
        self.conn.rollback()
            
if __name__ == "__main__":
    from DBUtils.PersistentDB import PersistentDB
    sqlitePool('imgdownload.db')
    sl = Sqlite()
    #print sl.test()
    try:
        s = sl.getImgdownload(10000,1)
        for i in s:
            print i[2].encode('gbk')
    except sqlite3.Error as e:
        print 'sqlite3',e
    #sl.createTable_imgdownload()
    #sl.addImgdownload(int(time.time()),'show me the money')

##    for i in sl.getImgdownload():
##        print i

    del sl

