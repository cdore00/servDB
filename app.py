import random
import string
import cherrypy
#import certifi
import ssl

#pdb expects a usable terminal with a TTY.
#docker run -it foo
import pdb
#pdb.set_trace()
import sys, os, io, re, cgi, csv, urllib.parse
from urllib.parse import urlparse, parse_qs
from sys import argv
#from datetime import datetime  , time
# JSON
from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads
import json

LOCAL_HOST = 'http://127.0.0.1:3000/'
HOSTserv = LOCAL_HOST
HOSTclient = 'http://localhost:8080/'
global HOSTcors
HOSTcors = 'https://cdore00.github.io'
#'*'
#'https://cdore00.github.io'

#global logPass 
logPass = ""
if os.getenv('PINFO') is not None:
    logPass = os.environ['PINFO']

if os.getenv('HOST') is not None:
    HOSTcors = os.environ['HOST']
    
# MongoDB
import pymongo
from pymongo import MongoClient

dbase = "golf"
port = 27017
uri = "mongodb://localhost"
if os.environ.get('MONGODB_USER'):
    if os.environ.get('MONGODB_PORT'):
        port = int(os.environ['MONGODB_PORT'])
    user = urllib.parse.quote_plus(os.environ['MONGODB_USER'])
    passw = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])
    domain = urllib.parse.quote_plus(os.environ['MONGODB_SERVICE'])
    #dbase = urllib.parse.quote_plus(os.environ['MONGODB_DATABASE'])
    uri = "mongodb://%s:%s@%s/%s?authSource=admin" % (user, passw, domain, "admin")
    #uri = "mongodb://%s:%s@%s/%s?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority" % (user, passw, domain, dbase)
    if 'tls' in argv and os.environ.get('MONGODB_CA'):
        argv.remove('tls')
        uri += "&tls=true&tlsCAFile=" + (os.environ['MONGODB_CA'])
        if os.environ.get('MONGODB_CERT'):
            uri += "&tlsCertificateKeyFile=" + (os.environ['MONGODB_CERT'])
        uri += "&tlsInsecure=true"
    if domain == "192.168.10.11":
        HOSTclient = 'https://cdore.ddns.net/'
        HOSTserv = 'https://cdore.ddns.net/pyt/'

    print("HOSTclient=" + HOSTclient)

#DBclient = MongoClient(uri, port, tlsCAFile=certifi.where())  
DBclient = MongoClient(uri, port)
#ssl_cert_reqs=ssl.CERT_NONE 
data = DBclient[dbase]
print("uri= " + uri)
print(str(data))
# END MongoDB
#pdb.set_trace()
""" Golf functions """
import golfFunc as gf
import logFunc as lf
gf.dataBase = data
gf.cherry = cherrypy
gf.usepdb = -1
lf.dataBase = data
lf.log_Info = gf.log_Info
lf.CLOUDpass = None
lf.init("golf.access.log")
if os.environ.get('CPASS'):
    lf.CLOUDpass = os.environ['CPASS']

#print(lf.CLOUDpass)

def exception_handler(status, message, traceback, version):
    """ EXCEPTION """
    #pdb.set_trace()
    logInfo = "ERROR " + status + " : " + message + " : Command: " +  cherrypy.request.path_info + "?" + cherrypy.request.query_string
    print(traceback)
    print(logInfo)
    gf.log_Info(logInfo)
    return logInfo

lf.except_handler = gf.except_handler

class webServer(object):
    """ Serve Golf functions """
    def __init__(self):
        gf.logPass = logPass
        #print('logPass=' + logPass)
        
    @cherrypy.expose
    def index(self, info = False):
        randId = ''.join(random.sample(string.hexdigits, 8))
        return 'Call ID: ' + randId

    @cherrypy.expose
    def getRegions(self, info = False):
        #pdb.set_trace()
        """ cookies = cherrypy.request.cookie        
        cookie = cherrypy.response.cookie
        cookie['tcookie'] = 'testcookieValue'
        cookie['tcookie']['max-age'] = 3600 """

        col = gf.dataBase.regions
        docs = col.find({})
        res = dumps(docs)
        return res

    @cherrypy.expose
    def getFav(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getFav(param, self)

    @cherrypy.expose
    def updateFav(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.updateFav(param, self)
        
    @cherrypy.expose
    def searchResult(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.searchResult(param, self)

    @cherrypy.expose
    def getClubList(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getClubList(param, self)

    @cherrypy.expose
    def getClubData(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getClubData(param, self)

    @cherrypy.expose
    def getClubParc(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getClubParc(param, self)

    @cherrypy.expose
    def getParcInfo(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getParcInfo(param, self)
        
    @cherrypy.expose
    def setGolfGPS(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.setGolfGPS(param, self)

    @cherrypy.expose
    def saveClub(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.saveClub(param, self)
        
    @cherrypy.expose
    def getClubParcTrous(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getClubParcTrous(param, self)
        
    @cherrypy.expose
    def getBloc(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getBloc(param, self)

    @cherrypy.expose
    def identUser(self, info = False, user = False, passw = False):
        if user:
           info = "user=" + user + "&pass=" + passw
        cookieOut = cherrypy.response.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.authUser(param, self, cookieOut)

    @cherrypy.expose
    #@cherrypy.tools.json_in()
    def listLog(self, passw = ""): 
        return gf.listLog(passw, logPass)
        
    @cherrypy.expose
    def showLog(self, name = ''):
        #pdb.set_trace()
        if "?" in name:
            param = parse_qs(urlparse(name).query)
            param = param['name'][0]
        else:
            param = name
        return gf.showLog(param)        

    @cherrypy.expose
    def getUser(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getUserInfo(param, self)

    @cherrypy.expose
    def saveUser(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.saveUser(param, self)

    @cherrypy.expose
    def getPassForm(self):
        return gf.getPassForm(self)

    @cherrypy.expose
    def savePass(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.savePassword(param, self)
        
    @cherrypy.expose
    def addUserIdent(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.addUserIdent(param, HOSTclient, HOSTserv, self)

    @cherrypy.expose
    def updUser(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.updateUser(param, self)
        
    @cherrypy.expose
    def confInsc(self, data = False):
        pos = cherrypy.request.query_string.find('?')
        info = cherrypy.request.query_string[pos+1:]
        param = parse_qs(urlparse('url?' + info).query)
        return gf.confInsc(param, HOSTclient, self)

    @cherrypy.expose
    def getPass(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getPass(param, self)        
    
    @cherrypy.expose
    def updateUser(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.updateUser(param, self)
    
    @cherrypy.expose
    def savePassword(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.savePassword(param, self)        

    @cherrypy.expose
    def endDelGame(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.endDelGame(param, self)    

    @cherrypy.expose
    def getGolfGPS(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getGolfGPS(param, self)

    @cherrypy.expose
    def getGame(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getGame(param, self)        

    @cherrypy.expose
    def countUserGame(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.countUserGame(param, self)

    @cherrypy.expose
    def getGameList(self, info = False, user = False, parc = False, skip = False, limit = False, is18 = False, date = False, tele = False, rand = False):
        #pdb.set_trace() 
        if user and isinstance(parc, (list)):
            pos = cherrypy.request.query_string.find('?')
            info = cherrypy.request.query_string[pos+1:]
        elif user:
            info = "user=" + user + "&parc=" + parc + "&skip=" + skip + "&limit=" + limit + "&is18=" + is18  + "&date=" + date + "&tele=" + tele
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getGameList(param, cherrypy)
        
    @cherrypy.expose
    def updateGame(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.updateGame(param, self)
        
    @cherrypy.expose
    def getGameTab(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getGameTab(param, self)

    @cherrypy.expose
    def endDelGame(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.endDelGame(param, self)
        
    @cherrypy.expose
    def delClub(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.delClub(param, self)

    @cherrypy.expose
    def setPosition(self, info = False, data= False):
        if (data):
           info = "data=" + data
        param = parse_qs(urlparse('url?' + info).query)
        return gf.setPosition(param, self)

    @cherrypy.expose
    def delPosition(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.delPosition(param, self)

    @cherrypy.expose
    def setBallPosition(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.setBallPosition(param, self)

    @cherrypy.expose
    def getPosition(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getPosition(param, self)

    @cherrypy.expose
    def getLogState(self, info = False):
        return lf.getState()
        
    @cherrypy.expose
    def loadLog(self, info = False):
        return lf.loadLog()
    
    @cherrypy.expose    
    def getLogs(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return lf.getLogs(param)

    @cherrypy.expose    
    def getLocation(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return lf.getLocation(param)
        
# Start server listening request
def run( args):
   #global HOSTcors
   port = int(args[0])
   domain = args[1]
   print('HOSTcors=' + HOSTcors + ' Domain=' + domain + ' Port=' + str(port) + ("  -Debug= " + str(gf.usepdb) if (gf.usepdb >= 0) else "") )

   config = {'server.socket_host': domain,
             'server.socket_port': port,   
             'tools.response_headers.on': True, 
             'tools.response_headers.headers': [ ('Access-Control-Allow-Origin', HOSTcors), ('Access-Control-Allow-Credentials', 'true')],
             'error_page.default': exception_handler,
             'engine.autoreload.on' : False,
             'log.screen': True,
             'log.access_file': '',
             'log.error_file': ''}
   cherrypy.config.update(config)
   gf.log_Info('Starting Web server...(' + HOSTserv + ":" + str(port) + ')') 
   print('Starting Web server...(' + HOSTserv + ":" + str(port) + ')')   
   if HOSTserv == LOCAL_HOST:
        gf.localHost = True
   cherrypy.quickstart(webServer())    


def build_arg_dict(arg):
    argd = dict()
    def add_dict(item):
        i = 0
        for x in arg:
            if x == item:
              argd[x] = arg[i+1]
            else:
              i+= 1

    if "port" in arg:
        add_dict("port")
    if "domain" in arg:
        add_dict("domain")
    if "pass" in arg:
        add_dict("pass")
    if "cors" in arg:
        add_dict("cors")
    if "cpass" in arg:
        add_dict("cpass")
    if "deb" in arg:
        add_dict("deb")
    #pdb.set_trace()
    if (len(arg) / 2) != len(argd):
        return False
    else:
        return argd

if __name__ == "__main__":
    #print(argv[0])
    #pdb.set_trace()
    if len(argv) > 1:
        arg = [x for x in argv]
        del arg[0]
        param = build_arg_dict(arg)
        if param:
            args = []
            if "deb" in param:
                gf.usepdb = int(param["deb"])
                print(str(gf.usepdb))
            if "cors" in param:
                #global HOSTcors
                HOSTcors = param["cors"]
            if "cpass" in param:
                lf.CLOUDpass = param["cpass"]
            if "serv" in param:
                HOSTserv = param["serv"]
            #print(str(len(argv)))
            if "pass" in param:
                #global logPass 
                logPass = param["pass"]
                print("pass= " + logPass)
            if "port" in param: 
                args.append(param["port"])
            else:
                args.append(8080)
            if "domain" in param: 
                args.append(param["domain"])
            else:
                args.append("0.0.0.0")
            run(args)
        else:
            run( [8080,"0.0.0.0"] )
            print("[cors VALUE] [domain VALUE] [port VALUE] [pass VALUE]")
    else:
        run([8080,"0.0.0.0"])
        
# Python39>python code/app.py port 3000 pass xxxxxxxx cors *