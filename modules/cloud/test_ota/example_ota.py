import Qth
import _thread
import dataCall
import utime
import log
import gc
from quectel import Log
OTA_PUBKEY = """-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAELJWlbA7dWY4sWTCe3RVGa9KpD7X91Cyi
rRSo7b1mFI3lrS+w1zk1OGBeZgUa0+uzIoBiM73HRVEBgaT6HDjQWMaAPu4OJ7/D
iLmUm3ZIGTABmJdGk2lWz+wJRUSZ2t/M
-----END PUBLIC KEY-----"""

logApp = log.getLogger("examp")
log = Log()
log.set_level(Log.NONE)
def App_devEventCb(event, result):
    logApp.info('dev event:{} result:{}'.format(event, result))
    if(2== event and 0 == result):
        pass
        Qth.otaRequest()

def App_cmdRecvTransCb(value):
    ret = Qth.sendTrans(1, value)
    logApp.info('recvTrans value:{} ret:{}'.format(value, ret))

def App_cmdRecvTslCb(value):
    logApp.info('recvTsl:{}'.format(value))
    for cmdId, val in value.items():
        logApp.debug('recvTsl {}:{}'.format(cmdId, val))
def App_cmdReadTslCb(ids, pkgId):
    logApp.info('readTsl ids:{} pkgId:{}'.format(ids, pkgId))
    value=dict()
    for id in ids:
        if 1 == id:
            value[1]=180.25
        elif 2 == id:
            value[2]=30
        elif 3 == id:
            value[3]=True
    Qth.ackTsl(1, value, pkgId)

def App_cmdRecvTslServerCb(serverId, value, pkgId):
    logApp.info('recvTslServer serverId:{} value:{} pkgId:{}'.format(serverId, value, pkgId))
    Qth.ackTslServer(1, serverId, value, pkgId)

def App_otaPlanCb(plans):
    logApp.info('otaPlan:{}'.format(plans))
    Qth.otaAction(1)

def App_fotaResultCb(comp_no, result):
    logApp.info('fotaResult comp_no:{} result:{}'.format(comp_no, result))
    
def App_sotaInfoCb(comp_no, version, url,fileSize, md5, crc):   # fileSize是可选参数
    logApp.info('sotaInfo comp_no:{} version:{} url:{} fileSize:{} md5:{} crc:{}'.format(comp_no, version, url,fileSize, md5, crc))
    # 当使用url下载固件完成，且MCU更新完毕后，需要获取MCU最新的版本信息，并通过setMcuVer进行更新
    Qth.setMcuVer('MCU1', 'V1.0.0', App_sotaInfoCb, App_sotaResultCb)

def App_sotaResultCb(comp_no, result):
    logApp.info('sotaResult comp_no:{} result:{}'.format(comp_no, result))


def app_start():
    Qth.init()
    Qth.setProductInfo('p11yq3','emcxQnJBV0VKZ0l1')
    Qth.setDK("123600000000000")
    Qth.setServer('mqtt://iot-south.quectelcn.com:1883')
    #Qth.setBsEt('tls')
    Qth.setOtaKey(OTA_PUBKEY)

    eventOtaCb={
            'otaPlan':App_otaPlanCb,
            'fotaResult':App_fotaResultCb
            }
    eventCb={
        'devEvent':App_devEventCb, 
        'recvTrans':App_cmdRecvTransCb, 
        'recvTsl':App_cmdRecvTslCb, 
        'readTsl':App_cmdReadTslCb, 
        'readTslServer':App_cmdRecvTslServerCb,
        'ota':eventOtaCb
        }
    Qth.setEventCb(eventCb)
    Qth.setVer('v2.0.0')
    try:
        Qth.start()
        count = 0
        while True:
            count += 1
            if (count >= 5):
                count = 0
                gc.collect()
                free_mem = gc.mem_free()
                print(f"Free memory: {free_mem} bytes")    
            utime.sleep(1)

    except KeyboardInterrupt:
        logApp.info("KeyboardInterrupt, stopping...")
        try:
            Qth.stop()
        except Exception as e:
            logApp.error("Qth.stop exception:{}".format(e))
        logApp.info("app stopped")