#-*- encoding: gb2312 -*-
import ConfigParser
import string, os, sys

class ImgDownloadIni:
    def __init__(self,confpath = 'imgdownload.conf'):
        self.path = ''
        self.confpath = confpath
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(confpath)

    def getSysConf(self):
        sysconf = {}
        sysconf['path'] = self.cf.get('SYSSET','path')
        sysconf['port'] = self.cf.getint('SYSSET','port')
        return sysconf
        
    def getSqliteConf(self):
        sqliteconf = {}
        sqliteconf['db']       = self.cf.get('SQLITESET','db')
        sqliteconf['maxusage'] = self.cf.getint('SQLITESET','maxusage')
        return sqliteconf

    def getOrcConf(self):
        orcconf = {}
        orcconf['host']   = self.cf.get('ORCSET','host')
        orcconf['user']   = self.cf.get('ORCSET','user')
        orcconf['passwd'] = self.cf.get('ORCSET','passwd')
        orcconf['port']   = self.cf.get('ORCSET','port')
        orcconf['sid']    = self.cf.get('ORCSET','sid')
        orcconf['mincached']      = self.cf.getint('ORCSET','mincached')
        orcconf['maxcached']      = self.cf.getint('ORCSET','maxcached')
        orcconf['maxshared']      = self.cf.getint('ORCSET','maxshared')
        orcconf['maxconnections'] = self.cf.getint('ORCSET','maxconnections')
        orcconf['maxusage']       = self.cf.getint('ORCSET','maxusage')
        return orcconf

    def getFtpConf(self,num):
        ftpset = {}
        strnum = str(num)
        ftpset['host']    = self.cf.get('FTPSET'+strnum,'host')
        ftpset['user']    = self.cf.get('FTPSET'+strnum,'user')
        ftpset['passwd']  = self.cf.get('FTPSET'+strnum,'passwd')
        ftpset['port']    = self.cf.getint('FTPSET'+strnum,'port')
        ftpset['timeout'] = self.cf.getint('FTPSET'+strnum,'timeout')
        ftpset['sername'] = self.cf.get('FTPSET'+strnum,'sername')
        return ftpset

     
if __name__ == "__main__":

    try:
        img = ImgDownloadIni()
        s= img.getSysConf()
        print (s['path'].replace("/","\\"),1)
        #s = imgIni.getPlateInfo(PATH2)
        #i = s['host'].split(',')
        #print s
        #disk = s['disk'].split(',')
        #print disk
        #del i
    except ConfigParser.NoOptionError,e:
        print e
        time.sleep(10)
