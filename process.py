# -*- coding: cp936 -*-

# -------------------------------------------------
#    �벻Ҫ�����޸��ļ��еĴ���
# -------------------------------------------------

import sys
import time,datetime
import threading
import socket
import gl
import logging

import php_python

REQUEST_MIN_LEN = 10    #�Ϸ���request��Ϣ����С����    
TIMEOUT = 30           #socket����ʱ��30��

pc_dict = {}        #Ԥ�����ֵ䣬key:����ģ�顢�����������ַ�����ֵ�Ǳ������
global_env = {}     #global��������

logger = logging.getLogger('root')  #������־�ļ�����

##reload(sys) # Python2.5 ��ʼ�����ɾ�� sys.setdefaultencoding ���������������Ҫ��������   
##sys.setdefaultencoding('gbk')

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def index(bytes, c, pos=0):
    """
    ����c�ַ���bytes�е�λ��(��0��ʼ)���Ҳ�������-1
    pos: ������ʼλ��
    """
    for i in range(len(bytes)):
        if (i <= pos):
            continue
        if bytes[i] == c:
            return i
            break
    else:
        return -1


def z_encode(p):
    """
    encode param from python data
    """
    if p == None:                               #None->PHP�е�NULL
        return "N;"
    elif isinstance(p, int):                    #int->PHP����
        return "i:%d;" % p
    elif isinstance(p, str):                    #String->PHP�ַ���
        p_bytes = p.encode(php_python.CHARSET);
        ret = 's:%d:"' % len(p_bytes)
        ret = ret.encode(php_python.CHARSET)
        ret = ret + p_bytes + '";'.encode(php_python.CHARSET)
        #ret = str(ret, php_python.CHARSET)
        ret = str(ret)
        return ret
    elif isinstance(p, bool):                   #boolean->PHP����
        b=1 if p else 0
        return 'b:%d;' % b
    elif isinstance(p, float):                  #float->PHP����
        return 'd:%r;' % p
    elif isinstance(p, list) or isinstance(p, tuple):        #list,tuple->PHP����(�±�int)
        s=''
        for pos,i in enumerate(p):
            s+=z_encode(pos)
            s+=z_encode(i)
        return "a:%d:{%s}" % (len(p),s)
    elif isinstance(p, dict):                   #�ֵ�->PHP����(�±�str)
        s=''
        for key in p:
            s+=z_encode(key)
            s+=z_encode(p[key])
        return "a:%d:{%s}" % (len(p),s)
    else:                                       #����->PHP�е�NULL
        #print 'else',p
        return "N;"


def z_decode(p):
    """
    decode php param from string to python
    p: bytes
    """
    if p[0]==chr(0x4e):                      #NULL 0x4e-'N'
        return None,p[2:]
    elif p[0]==chr(0x62):                    #bool 0x62-'b'
        if p[2] == chr(0x30):                # 0x30-'0'
            return False,p[4:]
        else:
            return True,p[4:]
    elif p[0]==chr(0x69):                    #int  0x69-'i'
        i = index(p, chr(0x3b), 1)           # 0x3b-';'
        return int(p[2:i]),p[i+1:]
    elif p[0]==chr(0x64):                    #double 0x64-'d'
        i = index(p, chr(0x3b), 1)           # 0x3b-';'
        return float(p[2:i]),p[i+1:]
    elif p[0]==chr(0x73):                    #string 0x73-'s'
        len_end = index(p, chr(0x3a), 2)     # 0x3a-':'
        str_len = int(p[2:len_end])
        end = len_end + 1 + str_len + 2
        v = p[(len_end + 2) : (len_end + 2 + str_len)]
        #return str(v, php_python.CHARSET), p[end+1:]
        #return v.encode(php_python.CHARSET), p[end+1:]
        #print 'v',v
        return v, p[end+1:]
    elif p[0]==chr(0x61):                    #array 0x61-'a'
        list_=[]       #����
        dict_={}       #�ֵ�
        flag=True      #���ͣ�true-Ԫ�� false-�ֵ�
        second = index(p, chr(0x3a), 2)      # 0x3a-":"
        num = int(p[2:second])  #Ԫ������
        pp = p[second+2:]       #����Ԫ��
        for i in range(num):
            key,pp=z_decode(pp)  #key����
            if (i == 0): #�жϵ�һ��Ԫ��key�Ƿ�int 0
                if (not isinstance(key, int)) or (key != 0):
                    flag = False            
            val,pp=z_decode(pp)  #value����
            list_.append(val)
            dict_[key]=val
        return (list_, pp[2:]) if flag else (dict_, pp[2:])
    else:
        return p,''


def parse_php_req(p):
    """
    ����PHP������Ϣ
    ���أ�Ԫ�飨ģ�����������������list��
    """
    while p:
        v,p=z_decode(p)         #v��ֵ  p��bytes(ÿ��z_decode����ƫ����)
        params = v

    modul_func = params[0]      #��һ��Ԫ���ǵ���ģ��ͺ�����
    #print("ģ��ͺ�����:%s" % modul_func)
    #print("����:%s" % params[1:])    
    pos = modul_func.find("::")
    modul = modul_func[:pos]    #ģ����
    func = modul_func[pos+2:]   #������
    return modul, func, params[1:]   
    

class ProcessThread(threading.Thread):
    """
    preThread �����߳�
    """
    def __init__(self, socket):
        threading.Thread.__init__(self)

        #�ͻ�socket
        self._socket = socket

    def run(self):

        #---------------------------------------------------
        #    1.������Ϣ
        #---------------------------------------------------
        
        try:  
            self._socket.settimeout(TIMEOUT)                  #����socket��ʱʱ��
            firstbuf = self._socket.recv(16 * 1024)           #���յ�һ����Ϣ��(bytes)
            if len(firstbuf) < REQUEST_MIN_LEN:               #������Ϣ��С����
                #print ("�Ƿ�����С����С����: %s" % firstbuf)
                #print 'error message,less than minimum length:',firstbuf
                logger.error('error message,less than minimum length:%s'%str(firstbuf))
                gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+'error message,less than minimum length:'+str(firstbuf)))
                self._socket.close()
                return

            firstComma = index(firstbuf, chr(0x2c))                #���ҵ�һ��","�ָ��
            #firstComma = index(firstbuf, ',')
            print firstbuf
            totalLen = int(firstbuf[0:firstComma])            #��Ϣ���ܳ���
            #print("��Ϣ����:%d" % totalLen)
            #print 'message length:',totalLen
            logger.info('message length:%s'%str(totalLen))
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_blue,getTime()+'message length:'+str(totalLen)))
            reqMsg = firstbuf[firstComma+1:]
            #print 'reqMsg:',reqMsg
            logger.info('reqMsg:%s'%reqMsg)
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_blue,getTime()+'reqMsg:'+reqMsg))
            while (len(reqMsg) < totalLen):    
                reqMsg = reqMsg + self._socket.recv(16 * 1024)

            #����
            #print ("�������%s" % reqMsg)

        except Exception,e:  
            #print ('������Ϣ�쳣', e)
            #print 'getMessage error',str(e)
            logger.error(str(e))
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+'getMessage error'+str(e)))
            self._socket.close()
            return

        #---------------------------------------------------
        #    2.����ģ�顢������飬Ԥ���롣
        #---------------------------------------------------

        #����Ϣ���н�����ģ�����������������list
        modul, func, params = parse_php_req(reqMsg)
        #print 'module:',modul,'func:',func,'parmas:',params

        if (modul not in pc_dict):   #Ԥ�����ֵ���û�д˱���ģ��
            #���ģ�顢�����Ƿ����
            try:
                callMod = __import__ (modul)    #����module���������module
                pc_dict[modul] = callMod        #Ԥ�����ֵ仺���ģ��
            except Exception,e:
                #print 'module not exist:',modul
                #print ('ģ�鲻����:%s' % modul)
                logger.error(str(e))
                gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+'module not exist:'+modul))
                self._socket.sendall(("F" + "module '%s' is not exist!" % modul).encode(php_python.CHARSET)) #�쳣
                self._socket.close()
                return
        else:
            callMod = pc_dict[modul]            #��Ԥ�����ֵ��л��ģ�����

        try:
            callMethod = getattr(callMod, func)
        except Exception,e:
            #print 'function not exist:',func
            #print ('����������:%s' % func)
            logger.error(str(e))
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+'function not exist:'+func))
            self._socket.sendall(("F" + "function '%s()' is not exist!" % func).encode(php_python.CHARSET)) #�쳣
            self._socket.close()
            return

        #---------------------------------------------------
        #    3.Python��������
        #---------------------------------------------------

        try: 
            params = ','.join([repr(x) for x in params])         
            #print ("���ú�����������%s(%s)" % (modul+'.'+func, params) )
            
            #���غ���
            compStr = "import %s\nret=%s(%s)" % (modul, modul+'.'+func, params)
            #print("�������ô���:%s" % compStr)
            rpFunc = compile(compStr, "", "exec")
            
            if func not in global_env: 
                global_env[func] = rpFunc   
            local_env = {}
            exec (rpFunc, global_env, local_env)     #��������
            #print (global_env)
            #print (local_env)
        except Exception,e:  
            #print ('����Pythonҵ�����쳣', e )
            #print 'call python error:',str(e)
            logger.error(str(e))
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+'call python error:'+str(e)))
            raise
            errType, errMsg, traceback = sys.exc_info()
            self._socket.sendall(("F%s" % errMsg).encode(php_python.CHARSET)) #�쳣��Ϣ����
            self._socket.close()
            return

        #---------------------------------------------------
        #    4.������ظ�PHP
        #---------------------------------------------------
        #retType = type(local_env['ret'])
        #print ("�������أ�%s" % retType)
        rspStr = z_encode(local_env['ret'])  #���������װΪPHP���л��ַ���
        #print 'local_env[ret]',local_env['ret']

        try:  
            #���ϳɹ�ǰ׺'S'
            rspStr = "S" + rspStr
            #����
            #print ("���ذ���%s" % rspStr)
            logger.info('return��%s'%rspStr)
            gl.TRIGGER.emit("<font %s>return��%s</font>"%(gl.style_blue,getTime()+rspStr))
            self._socket.sendall(rspStr.encode(php_python.CHARSET))
        except Exception,e:
            #print 'send message error:',str(e)
            #print ('������Ϣ�쳣', e)
            logger.error('send message error:%s'%str(e))
            gl.TRIGGER.emit("<font %s>%s</font>"%(gl.style_red,getTime()+'send message error:'+str(e)))
            errType, errMsg, traceback = sys.exc_info()
            self._socket.sendall(("F%s" % errMsg).encode(php_python.CHARSET)) #�쳣��Ϣ����
        finally:
            self._socket.close()
            return


