import shutil
import datetime,time
import logging
import gl
from sqlitedb import Sqlite

logger = logging.getLogger('root')
    
class Cleaner:
    def __init__(self,sqliteobj):
        self.sqlite = sqliteobj
        self.delta = 0.5

    def cleanFile(self,filename):
        try:
            shutil.rmtree(filename)
        except Exception,e:
            logger.error(str(e))
        try:
            shutil.rmtree(filename+'.zip')
        except Exception,e:
            logger.error(str(e))
    
    def cleanOTImg(self):
        _time = time.time()-datetime.timedelta(hours=self.delta).total_seconds()
        s = self.sqlite.getImgdownload(int(_time),0)
        
        if s != []:
            for i in s:
                if i[3]!=None and i[3]!='':
                    print i[3]
                    self.cleanFile(i[3])
                self.sqlite.updateImgdownloadByID(i[0])

    def main(self):
        while True:
            try:
                self.cleanOTImg()
            except Exception,e:
                logger.error(str(e))
                pass
            time.sleep(60)

if __name__ == "__main__":
    import sqlite3
    from DBUtils.PersistentDB import PersistentDB

    #print u2time(1403114803)
    sqlitePool('imgdownload.db')
    cl = Cleaner()
    cl.main()
    cl.cleanOTImg()
