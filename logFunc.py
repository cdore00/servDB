import pdb
#; pdb.set_trace()
import os, re, time, datetime, subprocess
from bson.json_util import dumps
import requests as req

NGINX_LOG_DIR = "/data/log/"
#NGINX_LOG_DIR = "C:/Users/cdore/AppData/Local/Programs/Python/Python36-32/code/file/"
fileName = "golf.access.log"
actFile = NGINX_LOG_DIR + fileName
archFile = NGINX_LOG_DIR + fileName + ".dat"    

def except_handler(fn, e):
    """ EXCEPTION """
    #pdb.set_trace()
    info = fn + " ERROR: " + str(e)
    print( info )
    log_Info( info )
    return dumps({'ok': 0, "message": "ERROR handled" })

def getLocation(param):
    try:
        if param.get("ip"):
            ip = param["ip"][0]
            apiURL = "http://api.ipstack.com/"
            key =  "?access_key=34aab071ddd6df722a40aab13400a403"
            resp = req.get(apiURL + ip + key)

            return resp.text
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getLocation", ex)
            
def getState():

    isAct = os.path.exists(actFile)
    isArch = os.path.exists(archFile)
    #pdb.set_trace()
    dt2 = 0
    if isArch:
        dt2=os.path.getmtime(archFile)
        last = time.strftime('%Y-%m-%d %H:%M',  time.gmtime(dt2)) + "   "
        #'2019-03-29 15:36   13.1 Ko'
    else:
        last = "Unknow   "
        
    if isAct:
        size = str(round(os.path.getsize(actFile)/1000,1)) + " Ko"
        dt = os.path.getmtime(actFile)
    else:
        size = "0 Ko"
        
    if isAct and isArch:
        day = str(round((dt-dt2)/86400,1)) + " day(s), "
    else:
        day = ""

    return dumps({'last': dt2, 'mess': last + day + size + " to load."})

    
def getLogs(param):
    try:
        #if localHost or checkSession(self, role = ['ADM']):
            if param:
                maxItem = 500
                pd = int(param['prefDate'][0]) if param.get('prefDate') else None
                pde = int(param['prefDateEnd'][0]) if param.get('prefDateEnd') else None
                pne = int(param['prefNotIp'][0]) if param.get('prefNotIp') else None
                ph = param['prefHost'][0] if param.get('prefHost') else None
                pr = param['prefReq'][0] if param.get('prefReq') else None
                ps = int(param['prefStat'][0]) if param.get('prefStat') else None
                exl = param['exList'][0] if param.get('exList') else None
                if exl:
                    exl = [x for x in exl.split("$")]
                
                qT = []
                coll = dataBase.log
                
                #pdb.set_trace()
                
                if pd:
                    q1 = {'time': { '$gte': pd }}
                if pde:
                    q1 = {'time': { '$gte': pd, '$lte': pde }}
                if pd:
                    qT.append(q1)
                
                q2 = None
                if ph:
                    q2 = {'ip': ph }
                if pne == 1:
                    q2 = {"ip": {"$nin": exl } }
                if pne == 2:
                    q2 = {"ip": {"$in": exl } }
                if q2:
                    qT.append(q2)

                if pr:
                    regxR = re.compile(pr, re.IGNORECASE)
                    q3 = {"request": {"$regex": regxR } }
                    qT.append(q3)

                if ps:
                    q4 = {"status": {"$ne": 200 } }
                    qT.append(q4)
                    
                query = { "$and": qT }
                #count = coll.find(query).count()
                count = coll.count_documents(query)
                print(str(count))
                doc = coll.find(query).sort("time",-1).limit(maxItem)

                """
                file = open('logData.txt', 'w')
                file.write(dumps(doc))
                file.close()
                """
                
                return dumps({"cnt": count, "max": maxItem, "logList": doc})
            else:
                return dumps({'ok': 0})    # No param
        #else: 
            #return ('{"n":0,"ok":0, "message": "S0062"}')
    except Exception as ex:
        return except_handler("getLogs", ex)            


def subCall(p):
    #pdb.set_trace()
    res = subprocess.run(["sh", "/tmp/ssdoc", p])
    result = str(res.returncode)
    return result

def loadLog():
    #pdb.set_trace()
    isAct = os.path.exists(actFile)
    isArch = os.path.exists(archFile)
    isSuccess = 1
    if isArch and isAct:
        try:
            dt=round(os.path.getmtime(archFile))
            #time.strftime('%Y-%m-%d %H:%M',  time.gmtime(dt)) + "   " + str(round(os.path.getsize(NGINX_LOG_DIR + fileName)/1000,1)) + " Ko"
            os.rename(archFile, archFile + str(dt))
            isSuccess = 1
        except OSError as e:
            if e.errno == 13:    #Fichier utilisé
                isSuccess = 0
                res = {"ok": isSuccess , "mess": str(e)}    

    if isSuccess:
        if isAct:
            tryCnt = 0
            #pdb.set_trace()
            while True:
                try:
                    os.rename(actFile, archFile)
                    res = (loadFile())
                    break
                except OSError as e:
                    isSuccess = 0
                    res = {"ok": isSuccess , "mess": str(e)}
                    tryCnt += 1
                    if tryCnt > 5:
                        break
                    time.sleep(1)
                    
            if (isSuccess):
                print("CLOUDpass=" + CLOUDpass)
                result = subCall(CLOUDpass)
                #pdb.set_trace()
                return result
        else:         
            isSuccess = 0
            res = {"ok": isSuccess , "mess": "No file to load"}    

    return dumps(res)

    
def loadFile():

    lines = [line.rstrip('\n') for line in open(archFile)]
    cnt = 1
    cnt50 = 0
    arrList = []
    for line in lines:

        try:
            fields = [x.strip() for x in line.split("|")]
            date, status, ip, request, user_agent, referer = fields
            #print(request)
            if len(referer) > 5:
                status_code = int(status)
                sd = date
                para = [x for x in date.split(" ")]
                sd = para[0]
                dif = int(para[1])/100
                dt = datetime.datetime.strptime(sd, "%d/%b/%Y:%H:%M:%S")
                dt = time.mktime(dt.timetuple())*1000
                #print(date + str(dt))
                elLog = { "time": dt, "date": date, "status": status_code, "ip": ip, "request": request, "referer": referer, "user_agent": user_agent}
                arrList.append(elLog)
                cnt += 1
        except (ValueError, IndexError) as e:
            # Not good, print it!
            print("WARNING: parsing log failed", e)
            print(line)
            continue
        #if not harmless(status_code, ip, request, user_agent):
            #print(line)
        
        if cnt > 50:
            insertLogList(arrList)
            arrList = []
            cnt50 += 1
            cnt = 1
    if cnt > 1:
        insertLogList(arrList)
    #print(str(cnt))
    return ({'ok': 1, 'mess': str(( cnt50*50)+cnt) + " loaded."})

def harmless(status_code, ip, request, user_agent):
     # ... some checks using ip and user agent ...

    if status_code >= 200 and status_code < 400:
        return True

    # used by nginx
    if status_code == 499:
        return True

    # We've filtered all the goodness:
    return False

def insertLogList(listLog):
    """ To insert log items list"""
    try:
        if listLog:
            #print(str(listLog))
            coll = dataBase.log
            doc = coll.insert(listLog)
            #print(str(doc))
        else:    
            return("No param")        
    except Exception as ex:
        #return except_handler("confInsc", ex)
        print("error " + str(doc))
        x=1
        

