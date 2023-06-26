import pdb
import sys, os, io, time

from socket import gethostname, gethostbyname
from datetime import datetime

from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads
import json

from random import random
userOnPage = []
connectUser = []



def millis():
    """ returns the elapsed milliseconds (1970/1/1) since now """
    obj = time.gmtime(0)
    epoch = time.asctime(obj)
    return round(time.time()*1000)

def addMessage(data):
    coll = dataBase.chat
    res = coll.insert_one({'cID': data['cID'], 'time': data['time'], 'status': data['stat'], 'IP': data['IP'], 'uID': data['uID'], 'user': data['user'], 'data': data['data'], 'messR': data['messR']})
    return {"Ok": res.acknowledged  , "oID": res.inserted_id}

def reaMessage(data):
    #pdb.set_trace()
    coll = dataBase.chat
    res = coll.update_one({'cID': data['cID'], 'time': data['mID']}, { "$set": { 'IP': data['IP'], 'uID': data['uID'], 'user': data['user'], 'Mtime': data['time'], 'status': data['stat'] } } )
    result = int(res.raw_result["ok"])
    Rdata = res.raw_result
    if result == 1:
        docs = coll.find({'cID': data['cID'], 'time': data['mID']}) 
        Rdata = dict(loads(dumps(docs))[0])
        Rdata["ok"] = result
    return dumps(Rdata)

def delMessage(data):
    # Suppression logique d'un message
    coll = dataBase.chat
    res = coll.update_one({'cID': data['cID'], 'time': data['mID']}, { "$set": { 'IP': data['IP'], 'uID': data['uID'], 'user': data['user'], 'Mtime': data['time'], 'status': data['stat'] } } )
    Rdata = res.raw_result
    Rdata["status"] = data['stat']
    return dumps(Rdata)

def get_new_messages(id, lastTime):
    # extrait les nouveaux messages depuis "lastTime" 
    coll = dataBase.chat
    docs = coll.find({'cID': id, 'time': { '$gt': lastTime }}) 
    return docs

def sendConfirmMail(self, data):
    try:
        email = data['email']
        code = str(int(100000 / random()))
        coll = dataBase.chatUser
        doc = coll.update_one({ 'email': email}, { '$set': {'code': code} },  upsert=True )
        sendChatCode(email, code)   # Envoie du code par courriel
        return dumps({"res": 0, "email": email, "message": "S0010"})
    except Exception as ex:
        return except_handler("sendConfirmMail", ex)
        
def validChatUserCode(data):
    # valider le code avec l'adresse courriel
    try:
        #pdb.set_trace()
        email = data['email']
        code = data['code']
        coll = dataBase.chatUser
        doc = coll.find({ 'email': email})
        data = dict(loads(dumps(doc))[0])
        if data["code"] == code:
            doc = coll.update_one({ 'email': email}, { '$set': {'time': millis()} })
            return dumps({"res": 0, "email": email, "message": "S0012"})
        else:
            return dumps({"res": 1, "email": email, "code": code, "message": "S0011"})
    except Exception as ex:
        return except_handler("validChatUserCode", ex)
        
def updChat(self, data):
    try:
        #pdb.set_trace()
        #data = json.loads(info)
        data['time'] = int(millis())
        data['IP'] = gethostbyname(gethostname()) 
        if data["stat"] == "D":
            res = delMessage(data)  # Supprimer message
        if data["stat"] == "A":
            res = reaMessage(data)  # Réafficher message 
        if data["stat"] == "M" or data["stat"] == "R":
            res = addMessage(data)  # Ajouter un message ou répondre au message
            data["ok"] = res["Ok"]
            #pdb.set_trace()
            res = dumps(data)
        print(res)             #PRINT
        return res
    except Exception as ex:
        return except_handler("updChat", ex)
        
def chat(self, lastTime, cID, uID, coID, rN):
    try:
        #pdb.set_trace()
        lastTime = int(lastTime)
        cID = int(cID)
        rN  = int(rN)
        result = {}
        sleepInterv = 2
        maxPollTime = 20
        pollTime = 0
        
        uID = uID if uID != '' else ("T" + str(int(1000000 / random())))    # Si l'utilisateur l'a pas d'indentitiant, on en crée un 
        if uID not in userOnPage:
            userOnPage.append(uID)                                          # On ajoute l'utilisateur à la liste sur la page
        result["uID"] = uID
        
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
    except Exception as ex:
        return except_handler("chat", ex)

def fetchHisto(self, lastTime, cID):
    try:
        limitCnt = 20
        #pdb.set_trace()))
        coll = dataBase.chat

        lastTime = int(lastTime)
        cID  = int(cID)
        
        docs = coll.find({'cID': cID , 'time': {'$gte':lastTime}})
        cnt = len(list(docs))
        histdocs = coll.find({'cID': cID}).sort("time",-1).skip(cnt).limit(limitCnt)
        print("Time:" + str(lastTime) + "  cID:" + str(cID) + "  SKIP : " +  str(cnt))
        return dumps(histdocs)
    except Exception as ex:
        return except_handler("fetchHisto", ex)