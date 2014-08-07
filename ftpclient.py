# -*- coding: cp936 -*-
import ftplib
import socket
import time,datetime,os

class FtpClient:
    def __init__(self,host='127.0.0.1',username='fire',password='yqlfire',timeout=2):
        self.host       = host
        self.username   = username
        self.password   = password
        self.port       = 21
        self.bufsize    = 1024
        self.timeout    = timeout
        
        self.localpath  = ''
        self.remotepath = ''
        self.dir_path   = ''
        
        self.ftp = ftplib.FTP()
        self.ftp.set_pasv(True)
        #self.ftp.set_debuglevel(2)
        
    def __del__(self):
        try:
            self.ftp.quit()
        except:
            pass

    def login(self):
        self.ftp.connect(self.host ,self.port,self.timeout)
        self.ftp.login(self.username,self.password)

    def downloadfile(self,remotepath,localpath):
        self.localpath = localpath
        self.remotepath = remotepath
        try:
            fp = open(self.localpath,'wb')
            self.ftp.retrbinary('RETR '+self.remotepath, fp.write, self.bufsize)
        except IOError,e:
            if e[0] == 2:
                self.makedirs(os.path.dirname(localpath))
                self.downloadfile(self.remotepath, self.localpath)
            else:
                raise
        except Exception,e:
            raise
        finally:
            if 'fp' in dir():
                fp.close()

    def uploadfile(self,remotepath,localpath):
        self.localpath = localpath
        self.remotepath = remotepath
        fp = open(self.dir_path+self.localpath,'rb')
        try:
            #fp = open(self.dir_path+self.localpath,'rb')
            self.ftp.storbinary('STOR '+self.remotepath, fp, self.bufsize)
        except ftplib.all_errors,e:
            print 'FTP',e
            if e[0] == '550 Filename invalid':
                #print os.path.splitext(remotepath)[0]
                self.ftp.mkd(os.path.split(remotepath)[0])
                self.uploadfile(self.remotepath,self.localpath)
            else:
                raise
        except Exception,e:
            print e
            print 'uploadfile error'
            #fp.close()
            raise
        else:
            pass
        finally:
            fp.close()
    
    def makedirs(self,path):
        try:
            if not os.path.isdir(path):
                os.makedirs(path)
        except IOError,e:
            raise

    def test(self):
        self.ftp.retrlines('LIST')
            
if __name__ == "__main__":
    #imgMysql = ImgMysql('localhost','root','')
    #imgMysql.login()
    ftpClient = FtpClient('127.0.0.1','kakou','kakou')
    #ftpClient2 = FtpClient('127.0.0.1','kakou','kakou')
    #ftpClient.login()
    
##    try:
##        ftpClient.downloadfile('girl.gif','f:/GitHub/test.gif')
##    except ftplib.all_errors,e:
##        print e
##        if e[0] == '550 File not found':
##            print '123'
    #ftpClient.downloadfile('girl.gif','f:/GitHub/test.gif')
    #time.sleep(300)
    try:
        ftpClient.login()
    
        ftpClient.downloadfile('girl.gif','f:/GitHub/test.gif')
    except ftplib.all_errors,e:
        print e[0]
##    for name in list:  
##        print(name)

    del ftpClient



