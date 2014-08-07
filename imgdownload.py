# -*- coding: cp936 -*-
from ftpclient import FtpClient
from iniconf import ImgDownloadIni
from orcdb import IOrc
from helpfunc import HelpFunc
import time,datetime,os,sys
import logging
import threading
import ftplib
import zipfile
import gl

logger = logging.getLogger('root')

class Download:
    def __init__(self):
        self.orc = IOrc()

        self.hf = HelpFunc()  #辅助函数类

        self.imgdlini = ImgDownloadIni()
        sysset = self.imgdlini.getSysConf()
        self.path = sysset['path'].replace("/","\\")
        
        ftpset1 = self.imgdlini.getFtpConf(1)
        ftpset2 = self.imgdlini.getFtpConf(2)

        self.f1 = FtpClient(ftpset1['host'],ftpset1['user'],ftpset1['passwd'],ftpset1['timeout'])
        self.f2 = FtpClient(ftpset2['host'],ftpset2['user'],ftpset2['passwd'],ftpset2['timeout'])
        
        self.ftp_ip = {}
        self.storage_ip = {'HYKK-STORAGE1':'10.44.240.123','HYKK-STORAGE2':'10.44.240.121'}

    #ftp登录
    def loginFtp(self):
        try:
            self.f1.login()
            self.ftp_ip['HYKK-STORAGE1'] = self.f1
        except Exception,e:
            logger.error('10.44.240.123'+str(e))
        try:
            self.f2.login()
            self.ftp_ip['HYKK-STORAGE2'] = self.f2
        except Exception,e:
            logger.error('10.44.240.121'+str(e))

    #抓图
    def getImgs(self,sql):
        try:
            self.loginFtp()
            count = 0
            timestamp = int(time.time())
            folder = str(timestamp)+'_'+str(gl.COUNT)

            #添加队列
            gl.MYQ.put((3,timestamp,sql,os.path.join(self.path,folder)))
            #创建文件夹
            if not os.path.isdir(self.path):
                os.makedirs(self.path)
            #压缩文件
            zipname = os.path.join(self.path,folder+'.zip')
            zipfp = zipfile.ZipFile(zipname, 'w')
            
            for i in self.orc.getCltxBySql(sql):
                remotepath = i['QMTP']+'\\'+i['TJTP']
                ftpc = self.ftp_ip.get(i['TPWZ'],0)
                if ftpc!=0:
                    localpath = os.path.join(self.path,folder,self.storage_ip.get(i['TPWZ'],0),i['QMTP'],i['TJTP'])
                    try:
                        ftpc.downloadfile(remotepath,localpath)
                        zipfp.write(localpath)
                    except ftplib.all_errors,e:
                        if e[0] == '550 File not found':
                            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,self.hf.getTime()+str(e)))
                            logger.error('550 File not found'+str(localpath))
                        else:
                            raise
                count += 1
            return folder+'.zip'
        except Exception,e:
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,self.hf.getTime()+str(e)))
            logger.error(str(e))
        finally:
            try:
                zipfp.close()
            except:
                pass
            del self.orc
            del self.hf
            del self.f1
            del self.f2
        
def getImgs(sql):
    imgd = Download()
    return imgd.getImgs(sql)
    del imgd

if __name__ == "__main__":
  
    fc = FtpCenter()
    #self.diskstate.checkDisk()
    fc.getDisk()
    #print fc.activedisk
##    while True:
##        #print '123'
##        fc.checkDisk()
##        time.sleep(5)
    #fc.main()
