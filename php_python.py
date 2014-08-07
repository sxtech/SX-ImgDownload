# -*- coding: cp936 -*-
import signal
import sys,os,time,datetime
import socket
import sqlite3
import cx_Oracle
import threading
import logging
import Queue
import gl
from sqlitedb import Sqlite
from iniconf import ImgDownloadIni
#from imgdownload import Download
from helpfunc import HelpFunc
from cleaner import Cleaner
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB
import decimal
decimal.__version__

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    
# -------------------------------------------------
# 基本配置
# -------------------------------------------------
##LISTEN_PORT = 21231     #服务侦听端口
CHARSET = "gbk"       #设置字符集（和PHP交互的字符集）

logger = logging.getLogger('root')

# -------------------------------------------------
# sqlite3 线程池
# -------------------------------------------------
def sqlitePool(db,maxu=1000):
    gl.sqlitepool = PersistentDB(
        sqlite3,
        maxusage = maxu,
        database = db)

# -------------------------------------------------
# Oracle 线程池
# -------------------------------------------------
def orcPool(h,u,ps,pt,s,minc=5,maxc=20,maxs=10,maxcon=100,maxu=1000):
    gl.orcpool = PooledDB(
        cx_Oracle,
        user = u,
        password = ps,
        dsn = "%s:%s/%s"%(h,pt,s),
        mincached=minc,
        maxcached=maxc,
        maxshared=maxs,
        maxconnections=maxcon,
        maxusage=maxu)
    
# -------------------------------------------------
# 主程序
#    请不要随意修改下面的代码
# -------------------------------------------------

def imgDownloadServer():
    try:      
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,'-------------------------------------------'))
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,"- ImgDownload Service"))
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,"- Time: %s" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,'-------------------------------------------'))
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #TCP/IP
        sock.bind(('', gl.LISTEN_PORT))
        sock.listen(5)

        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,"Listen port: %d" % gl.LISTEN_PORT))
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,"charset: %s" % gl.CHARSET))
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,"Server startup..."))

        import process

        gl.MYLOCK = threading.Lock()
        
        while 1:
            connection,address = sock.accept()  #收到一个请求
            gl.COUNT += 1
            #print ("client's IP:%s, PORT:%d" % address)
            if gl.QTFLAG == False:
                gl.DCFLAG = False
                break
            
            # 处理线程
            try:
                process.ProcessThread(connection).start()
            except:
                pass
    except Exception,e:
        logger.error(str(e))
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+str(e)))

def mainCleaner():
    clCount = 0
    while 1:
        if not gl.QTFLAG:    #退出检测
            gl.DCFLAG = False
            break
        else:
            try:
                if clCount>30:
                    clCount = 0
                    gl.MYQ.put((7,0))
            except Exception,e:
                logger.error(str(e))
                gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+str(e)))
        clCount += 1
        time.sleep(1)


def sqliteCustomer():
    sqlite = Sqlite()
    sqlite.createTable()     #创建表
    cl = Cleaner(sqlite)
    
    while 1:
        if not gl.QTFLAG:    #退出检测
            gl.DCFLAG = False
            break
        try:
            data = gl.MYQ.get()
            if data[0]==3:
                addImg(sqlite,data)
            elif data[0]==7:
                print 'clear'
                cl.cleanOTImg()
        except Queue.Empty:
            time.sleep(1)
        except Exception,e:
            logger.error(str(e))
            raise
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+str(e)))

    del sqlite
    del cl

def addImg(sqlite,data):
    try:
        sqlite.addImgdownload(data[1],data[2].decode('gbk'),data[3])
    except sqlite3.Error as e:
        logger.error(str(e))
        gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+str(e)))
        try:
            sqlite.addImgdownload(data[1],'',data[3])
        except Exception,e:
            logger.error(data[2])

        
class Php2Python:
    def __init__(self):
        self.imgdIni   = ImgDownloadIni()
        self.sqliteset = self.imgdIni.getSqliteConf()
        self.orcset    = self.imgdIni.getOrcConf()
        self.sysset    = self.imgdIni.getSysConf()

        self.hf = HelpFunc()

        gl.ORCLOGIN = False

        self.orcCount = 1
        
        self.loginOrc()

        
    #登录oracle
    def loginOrc(self):
        
        try:
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,self.hf.getTime()+'Start to login oracle...'))
            orcPool(self.orcset['host'],self.orcset['user'],self.orcset['passwd'],self.orcset['port'],self.orcset['sid'],self.orcset['mincached'],self.orcset['maxcached'],self.orcset['maxshared'],self.orcset['maxconnections'],self.orcset['maxusage'])
            gl.ORCLOGIN = True
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_green,self.hf.getTime()+'Login oracle success!'))
            self.orcCount = 0
        except Exception,e:
            gl.ORCLOGIN = False
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,self.hf.getTime()+str(e)))
            self.orcCount = 1
            
    def main(self):
        logger.info('Logon System')
        try:        
            sqlitePool(self.sqliteset['db'],self.sqliteset['maxusage'])

            while 1:
                if not gl.QTFLAG:    #退出检测
                    gl.DCFLAG = False
                    return
                elif gl.ORCLOGIN:    #oracle登录检测
                    break
                else:
                    if self.orcCount == 0 or self.orcCount >= 15:
                        self.loginOrc()
                    else:
                        self.orcCount += 1
                time.sleep(1)
                
            
            gl.LISTEN_PORT = self.sysset['port']
            gl.CHARSET     = 'gbk'
            gl.MYQ         = Queue.Queue(0)
            
            t1 = threading.Thread(target=imgDownloadServer, args=(),kwargs={})
            t2 = threading.Thread(target=mainCleaner, args=(),kwargs={})
            t3 = threading.Thread(target=sqliteCustomer, args=(),kwargs={})
            t1.start()
            time.sleep(1)
            t2.start()
            t3.start()
            t1.join()
            t2.join()
            t3.join()
            
        except Exception,e:
            logger.error(str(e))
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,self.hf.getTime()+str(e)))
            time.sleep(1)
        finally:
            logger.warning('Logout System')
            del self.hf
            del self.imgdIni
    
if __name__ == '__main__':
    imgdIni   = ImgDownloadIni()
    sqliteset = imgdIni.getSqliteConf()
    orcset    = imgdIni.getOrcConf()

    sqlitePool(sqliteset['db'],sqliteset['maxusage'])
    orcPool(orcset['host'],orcset['user'],orcset['passwd'],orcset['port'],orcset['sid'],orcset['mincached'],orcset['maxcached'],orcset['maxshared'],orcset['maxconnections'],orcset['maxusage'])
    
    t1 = threading.Thread(target=imgDownloadServer, args=(),kwargs={})
    t2 = threading.Thread(target=mainCleaner, args=(),kwargs={})
    t1.start()
    time.sleep(1)
    t2.start()
    t1.join()
    t2.join()




