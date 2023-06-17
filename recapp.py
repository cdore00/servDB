import random
import string
import cherrypy
import dropbox, base64

import pdb
#; pdb.set_trace()
import sys, os, io, re, cgi, csv, urllib.parse
from urllib.parse import urlparse, parse_qs
from sys import argv
#from datetime import datetime  , time
# JSON
from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads
import json

from os.path import abspath  # For upload

LOCAL_HOST = 'http://127.0.0.1:3000/'
HOSTserv = LOCAL_HOST
HOSTclient = 'http://localhost:8080/'
HOSTcors = 'https://cdore00.github.io'
DATA_DIR = ""
IMG_DIR = ""

#global logPass 
logPass = ""

if os.getenv('PINFO') is not None:
    logPass = os.environ['PINFO']

if os.getenv('HOST') is not None:
    HOSTcors = os.environ['HOST']
    
# MongoDB
import pymongo
from pymongo import MongoClient

dbase = "resto"
port = 27017
uri = "mongodb://localhost"
if os.environ.get('MONGODB_USER'):
    port = int(os.environ['MONGODB_PORT'])
    user = urllib.parse.quote_plus(os.environ['MONGODB_USER'])
    passw = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])
    domain = urllib.parse.quote_plus(os.environ['MONGODB_SERVICE'])
    dbase = urllib.parse.quote_plus(os.environ['MONGODB_DATABASE'])
    uri = "mongodb://%s:%s@%s/%s?authSource=admin" % (user, passw, domain, dbase)
    #uri = "mongodb://%s:%s@%s/%s?authMechanism=SCRAM-SHA-1, authSource=admin" % (user, passw, domain, dbase)
    DATA_DIR = "/data/"
    IMG_DIR = DATA_DIR + "lou/photos/"
    #IMG_URL = HOSTclient + "/photos/"
    if domain == "192.168.10.11":
        HOSTclient = 'https://loupop.ddns.net/'
        HOSTserv = 'https://loupop.ddns.net/pyt/'
    else:
        HOSTclient = 'https://cdore00.github.io/golf/'
        HOSTserv = 'https://pytgolf-cd-serv.1d35.starter-us-east-1.openshiftapps.com/'
        #HOSTclient = 'https://pytgolf-cdore2.a3c1.starter-us-west-1.openshiftapps.com/'
    IMG_URL = HOSTclient + "/photos/"
    print("HOSTclient=" + HOSTclient + " IMG_URL=" + IMG_URL)

#client = "host=%s, username=%s, password=%s, authSource=%s" % (domain, user, passw, "admin")
#pdb.set_trace()
DBclient = MongoClient(uri, port)
data = DBclient[dbase]

# END MongoDB

""" App functions """
import recFunc as gf
import logFunc as lf
gf.dataBase = data
gf.DATA_DIR = DATA_DIR
gf.cherry = cherrypy
gf.usepdb = -1
if (IMG_DIR != "" ):
    gf.IMG_DIR = IMG_DIR
    gf.IMG_URL = IMG_URL
else:
    IMG_DIR = gf.IMG_DIR
    IMG_URL = gf.IMG_URL
    
lf.dataBase = data
lf.log_Info = gf.log_Info
lf.CLOUDpass = None


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
    """ Serve Recettes functions """
    def __init__(self):
        gf.logPass = logPass
        #print('logPass=' + logPass)
        
    @cherrypy.expose
    def index(self, info = False):
        randId = ''.join(random.sample(string.hexdigits, 8))
        return 'Call ID: ' + randId

    @cherrypy.expose
    def getCat(self, info = False):
        """ cookies = cherrypy.request.cookie        
        cookie = cherrypy.response.cookie
        cookie['tcookie'] = 'testcookieValue'
        cookie['tcookie']['max-age'] = 3600 """     
        #pdb.set_trace()
        col = gf.dataBase.categorie
        docs = col.find({})
        res = dumps(docs)
        return res

    @cherrypy.expose
    def identUser(self, info = False, user = False, passw = False):
        if user:
           info = "user=" + user + "&pass=" + passw
        cookieOut = cherrypy.response.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.authUser(param, self, cookieOut)

    @cherrypy.expose
    def getPass(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getPass(param, self)

    @cherrypy.expose
    def confInsc(self, data = False):
        pos = cherrypy.request.query_string.find('?')
        info = cherrypy.request.query_string[pos+1:]
        param = parse_qs(urlparse('url?' + info).query)
        return gf.confInsc(param, HOSTclient, self)

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
    def getRecList(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getRecList(param, self)

    @cherrypy.expose
    def getRecette(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getRecette(param, self)

    @cherrypy.expose
    def saveRecet(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.saveRecet(param, self)

    @cherrypy.expose
    def delRecet(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.delRecet(param, self)


    @cherrypy.expose
    def sendRecetMail(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.sendRecetMail(param, self)    


    @cherrypy.expose
    def addFile(self, upfile, type):
        #pdb.set_trace()
        if (hasattr(upfile, 'file')):    #File type image   
            upload_filename = upfile.filename
            upload_file = os.path.normpath(
                os.path.join(gf.IMG_DIR, upload_filename))
            size = 0
            with open(upload_file, 'wb') as out:
                while True:
                    data = upfile.file.read(8192)
                    if not data:
                        break
                    out.write(data)
                    size += len(data)
            out = ""
            print('1 - IMG_DIR=' + IMG_DIR + ' upload_file=' + upload_file + ' IMG_URL=' + IMG_URL + ' HOSTclient' + HOSTclient)
            
        else:    # Camera image Base64 PNG
            upload_filename = getattr(upfile, 'filename', str(ObjectId()) + ".png")
            fileData = getattr(upfile, 'file', upfile)
            upload_file = os.path.normpath(
                os.path.join(gf.IMG_DIR, upload_filename))
            content = fileData.split(';')[1]
            image_encoded = content.split(',')[1]
            with open(upload_file, 'wb') as out:
                out.write(base64.decodebytes(image_encoded.encode('utf-8')))
            out = ""
            print('2 - IMG_DIR=' + IMG_DIR + ' upload_file=' + upload_file + ' IMG_URL=' + IMG_URL + ' HOSTclient' + HOSTclient)

        file_to = IMG_URL + upload_filename

        return dumps({"ok": 1, "url": file_to})

        
    @cherrypy.expose
    def getPassForm(self):
        return gf.getPassForm(self)

    @cherrypy.expose
    def savePass(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.savePassword(param, self)

    @cherrypy.expose
    def getUser(self, info = False):
        gf.cookie = cherrypy.request.cookie
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getUserInfo(param, self)

    @cherrypy.expose
    def updUser(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.updateUser(param, self)

    @cherrypy.expose
    def addUserIdent(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.addUserIdent(param, HOSTclient, HOSTserv, self)
     
    @cherrypy.expose
    def delUser(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.delUser(param, self)
     
    @cherrypy.expose
    def listNews(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.listNews(param, self)
        
    @cherrypy.expose
    def getNews(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.getNews(param, self)

    @cherrypy.expose
    def writeNews(self, info = False):
        param = parse_qs(urlparse('url?' + info).query)
        return gf.writeNews(param, self)
        
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
   global HOSTcors
   port = int(args[0])
   domain = args[1]
   print('HOSTcors=' + HOSTcors + ' Domain=' + domain + ' Port=' + str(port) + ("  -Debug= " + str(gf.usepdb) if (gf.usepdb >= 0) else "")  )
        
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
        #print(str(arg))
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
                logPass = param["pass"]
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
        
        