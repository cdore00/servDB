import pdb
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os, time, urllib.parse
from urllib.parse import urlparse, parse_qs

from bson.json_util import dumps
from bson.json_util import loads
from random import random

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

DBclient = MongoClient(uri, port)
dataBase = DBclient[dbase]
coll = dataBase.chat

# END MongoDB

userOnPage = []
connectUser = []

def cntUser(uID):
    """ returns the elapsed milliseconds (1970/1/1) since now """
    pdb.set_trace()
    if uID not in userOnPage:
        userOnPage.append(uID)

    print(str(userOnPage) + "   Tot: " + str(len(userOnPage)))
    return len(userOnPage)

app = Flask(__name__)
#app.config['SERVER_NAME'] = 'loupop.ddns.net/pyt/8080'

def millis():
    """ returns the elapsed milliseconds (1970/1/1) since now """
    obj = time.gmtime(0)
    epoch = time.asctime(obj)
    return round(time.time()*1000)


@app.route('/updChat', methods=['POST', 'GET'])
def handle_data():
    #pdb.set_trace()
    data = dict(loads(request.form.get('info')))
    #data = request.json
    data['time'] = int(millis())
    data['IP'] = request.remote_addr
    if data["stat"] == "D":
        res = delMessage(data)  # Supprimer message
    if data["stat"] == "A":
        res = reaMessage(data)  # Réafficher message 
    if data["stat"] == "M" or data["stat"] == "R":
        res = addMessage(data)  # gérer res
        data["ok"] = res["Ok"]
        #pdb.set_trace()
        res = jsonify(data)
    print(res)             #PRINT
    return res

def addMessage(data):
    
    coll = dataBase.chat
    res = coll.insert_one({'cID': data['cID'], 'time': data['time'], 'status': data['stat'], 'IP': data['IP'], 'user': data['user'], 'data': data['data'], 'messR': data['messR']})
    
    #pdb.set_trace()
    return {"Ok": res.acknowledged  , "oID": res.inserted_id}
    
def reaMessage(data):
    #pdb.set_trace()
    coll = dataBase.chat
    res = coll.update_one({'cID': data['cID'], 'time': data['mID']}, { "$set": { 'IP': data['IP'], 'user': data['user'], 'Mtime': data['time'], 'status': data['stat'] } } )
    result = int(res.raw_result["ok"])
    Rdata = res.raw_result
    if result == 1:
        docs = coll.find({'cID': data['cID'], 'time': data['mID']}) 
        Rdata = dict(loads(dumps(docs))[0])
        Rdata["ok"] = result
    
    return dumps(Rdata)

def delMessage(data):
    
    coll = dataBase.chat
    res = coll.update_one({'cID': data['cID'], 'time': data['mID']}, { "$set": { 'IP': data['IP'], 'user': data['user'], 'Mtime': data['time'], 'status': data['stat'] } } )
    Rdata = res.raw_result
    Rdata["status"] = data['stat']
    #pdb.set_trace()
    return dumps(Rdata)
    
    
@app.route('/chat', methods=['GET'])
def chat():
    result = {}
    sleepInterv = 2
    maxPollTime = 20
    pollTime = 0
    lastTime = int(request.args.get('lastTime', '-1'))
    cID  = int(request.args.get('cID', '-1'))
    coID  = request.args.get('coID', '')
    uID  = request.args.get('uID', '')
    rN  = int(request.args.get('rN', '-1'))
    
    uID = uID if uID != '' else ("T" + str(int(1000000 / random())))    # Si l'utilisateur l'a pas d'indentitiant, on en crée un 
    if uID not in userOnPage:
        userOnPage.append(uID)                                          # On ajoute l'utilisateur à la liste sur la page
    result["uID"] = uID
    #pdb.set_trace()
    if coID != '' and coID not in connectUser:
        connectUser.append(coID)
    
    messages = []

    # wait for new messages to arrive
    if rN > 0:
        messages = list(get_new_messages(cID, lastTime))
    else:
        while len(messages) == 0:
            time.sleep(sleepInterv)
            if pollTime == 2 or pollTime == 10:
                #pdb.set_trace()
                ts = lastTime / 1000
                print( uID + " Connect: " + coID + "  Time:" + str(datetime.fromtimestamp(time.time()).strftime(' %HH%M:%S')) + "  Last:" + str(datetime.fromtimestamp(lastTime/1000).strftime(' %HH%M:%S')))
           
            messages = list(get_new_messages(cID, lastTime))
            pollTime += sleepInterv
            if pollTime > maxPollTime:
                break

    print(str(connectUser) + " connecté  Tot: " + str(len(connectUser)))
    print(str(userOnPage) + "   Tot: " + str(len(userOnPage)))            
    pollTime = 0
    result["uNbr"] = len(userOnPage)
    if uID in userOnPage:
        userOnPage.remove(uID)              # On supprime l'utilisateur, au cas où il n'est plus en ligne
    result["cNbr"] = len(connectUser)
    if coID != '' and coID in connectUser:
        connectUser.remove(coID)            # On supprime l'utilisateur, au cas où il n'est plus en ligne
    result["mess"] = messages

    print("Time:" + str(datetime.fromtimestamp(time.time()).strftime(' %HH%M:%S')) + "  Last:" + str(datetime.fromtimestamp(lastTime/1000).strftime(' %HH%M:%S')) + "   Messages : " + str(len(messages)))
    return dumps(result)

def get_new_messages(id, lastTime):
    # query the database since the last_message_time, return the new messages
    
    coll = dataBase.chat
    docs = coll.find({'cID': id, 'time': { '$gt': lastTime }}) 
    #pdb.set_trace()
    return docs

@app.route('/fetchHisto', methods=['GET'])
def fetchHisto():
    limitCnt = 20
    lastTime = int(request.args.get('lastTime', '-1'))
    cID  = int(request.args.get('cID', '-1'))
    
    docs = coll.find({'cID': cID , 'time': {'$gte':lastTime}})
    cnt = len(list(docs))
    histdocs = coll.find({'cID': cID}).sort("time",-1).skip(cnt).limit(limitCnt)
    print("Time:" + str(lastTime) + "  cID:" + str(cID) + "  SKIP : " +  str(cnt))
    return dumps(histdocs)

if __name__ == '__main__':
    CORS(app)
    #app.run()
    app.run(debug=True, host="127.0.0.1", port=3000)
    #app.run(debug=True, host="172.17.0.4", port=8080)