import pdb
import sys, os, io, time, re, cgi, csv
import smtplib
import phonetics
from socket import gethostname, gethostbyname
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
MAIL_USER = 'cdore07@gmail.com'

from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads
import json

import cherrypy
from cherrypy.lib import static

def millis():
   """ returns the elapsed milliseconds (1970/1/1) since now """
   dt = datetime.now() - datetime(1970, 1, 1)
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms
   
#Log file
LOG_DIR = (os.getcwd() if os.getcwd() != '/' else '') + '/log'
#pdb.set_trace()
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = LOG_DIR + '/pytServer.log'
#LOG_FILE = LOG_DIR + '/' + str(int(millis())) + '.log'
print("logfile= " + LOG_FILE)

localHost = False
cookie = ""

def except_handler(fn, e):
    """ EXCEPTION """
    #pdb.set_trace()
    info = fn + " ERROR: " + str(e)
    print( info )
    log_Info( info )
    return dumps({'ok': 0, "message": "ERROR handled" })
    
    
def getID(strID):
    if len(strID) < 5:
        return int(strID)
    else:    
        return ObjectId(strID)

def cursorTOdict(doc):
    strCur = dumps(doc)
    jsonCur = loads(strCur)
    return dict(jsonCur[0])

def checkSession(self, role = None):
    """ Session ID check for user"""
    #pdb.set_trace()
    
    print('1-Cookies = ' + str(cookie))
    if cookie and 'sessID' in cookie and 'userID' in cookie:
        sID = cookie['sessID'].value
        uID = getID(cookie['userID'].value)
        coll = dataBase.users
        #print('2-Role = ' + str(role))
        #print(cookie)
        if role is None:
            doc = coll.find({"_id": uID, "sessID": sID}, ["_id"])
        else:
            doc = coll.find({"_id": uID, "sessID": sID, "niveau":{"$in": role }}, ["_id"])
        #print('ID = ' + str(uID) + '  Session = ' + str(sID) + "  Count= " + str(doc.count()) + ' cookID = ' + str(cookie['userID'].value))
        if len(list(doc)):
            return True
        else:
            return False
    else:
        return False

def addUserIdent(param, HOSTclient, HOSTserv, self):
    """ To add new user account """
    try:
        if param.get("email") and param.get("pass"):
            email = param["email"][0]
            passw = param["pass"][0]
            user = ""
            if param.get("user"):
                user = param["user"][0]

            coll = dataBase.users
            docs = coll.find({"courriel": email})
            info = list(docs)
            #pdb.set_trace()
            if len(info):
                doc = cursorTOdict(info)
                if doc['actif'] == False:
                    if doc['motpass'] == passw:
                        sendConfMail( HOSTserv + "confInsc?data=" + email , email, doc['Nom'])
                        return dumps({"code":1, "message": "S0050"})    #existInactif(doc)
                    else:
                        return dumps({"code":3, "message": "S0051"})
                if doc['actif'] == True:
                    return dumps({"code":2, "message": "S0058"})
            else:
                res = coll.insert_one({"Nom": user , "courriel": email, "motpass": passw , "niveau": "MEM", "actif": False})

                name = user
                if name == "":
                    name = email

                sendConfMail( HOSTserv + "confInsc?data=" + email , email, name)
                log_Info("Nouveau compte créé: " + email)
                return dumps({"code":-1, "message": "S0052"})
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("addUserIdent", ex)
        
def confInsc(param, HOSTclient, self):
    """ To Confirm new account"""
    try:
        if param.get("data"):
            user = param["data"][0]
            coll = dataBase.users
            docs = coll.find({"courriel": user})
            if docs[0]['actif'] == True:
                return ("<h1>Le compte " + docs[0]['courriel'] + " est d&eacute;j&agrave; actif.</h1>")
            else:
                #activateAccount(loginUser(res, docs[0].courriel, docs[0].motpass))
                res = coll.update_one({"courriel": user}, { "$set": {"actif": True}})
                log_Info("Nouveau compte activé: " + docs[0]['courriel'])

                redir = """<html><head><script type="text/javascript" language="Javascript">function initPage(){var cliURL = "%s",user = "%s",pass = "%s";document.location.href = cliURL + "login.html?data=" + user + "$pass$" + pass;}</script></head><body onload="initPage()"><h1>Confirmation en cours...</h1></body></html>""" % (HOSTclient, docs[0]['courriel'], docs[0]['motpass'])
                return redir
        else:    
            return("Confirm" + str(param))        
    except Exception as ex:
        return except_handler("confInsc", ex)
        
def getPass(param, self):
    """ Recover password by email """
    try:
        if param.get("data"):
            email = param["data"][0]
            coll = dataBase.users
            docs = coll.find({"courriel": email, "actif": True})
            doc = list(docs)
            if len(doc):
                sendRecupPassMail(doc[0]['courriel'], doc[0]['Nom'], doc[0]['motpass'])
                return dumps({"code":-1, "message": "S0054"})
            else:
                return dumps({"code": 1, "message": "S0055"})
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getPass", ex)

def getPassForm(self):
    """ Return HTML code form to change password """
    htmlContent = '<div id="accountForm"><div id="titrePref">Edit account</div><form id="formPass"></br> <div class="prefList"><label for="passUser" class="identLbl">New password</label><div class="prefVal"><input id="passUser" type="text" size="15" maxlength="20"/></div></div> <div><input id="okPref" class="bouton" type="submit" onClick="savePass(); return false;" value="Ok" /><input id="annulePref" class="bouton" type="button" onClick="closePref(); return false;"  value="Cancel"/></div></form></div>'
    #writeCook(self,htmlContent)
    return htmlContent    

    
def authUser(param, self, cookie):
    """ To Authenticate or return user info to modify """
    try:    

        if param:
            #pdb.set_trace()
            if not isinstance(param, (list)) and param.get("user"):
                user = param["user"][0]
                #print("1- user= " + str(user))
                coll = dataBase.users
                doc = coll.find({"courriel": user, "actif": True}, ["_id","Nom", "courriel", "motpass", "niveau"])
                userDoc = list(doc)
                if usepdb == 3:
                    pdb.set_trace()                
                def setSessID(mess, userID):
                    #pdb.set_trace()
                    coll = dataBase.users
                    sessID = str(ObjectId())
                    res = coll.update_one({"courriel": user}, { "$set": {"sessID": sessID}})
                    cookie['sessID'] = sessID
                    cookie['sessID']['max-age'] = 31536000
                    cookie['userID'] = userID
                    cookie['userID']['max-age'] = 31536000
                    cookie['userRole'] = userDoc[0]["niveau"]
                    cookie['userRole']['max-age'] = 31536000
                    return mess
                    
                if not len(userDoc):
                    return dumps({'resp': {"result": 0} })    # Authenticate fail
                else:
                    dic = cursorTOdict(userDoc)
                    dic['_id'] = str(dic['_id'])
                if param.get("pass") and not isinstance(param, (list)):
                    passw = param["pass"][0]
                    if str(dic['motpass']) == passw:
                        del dic['motpass']
                        docs = {"resp": {"result":True, "user": dic} }
                        res = dumps(docs)    # Authenticated
                        return setSessID(res, dic['_id'])
                    else:
                        return dumps({'resp': {"result": 0} })    # Authenticate fail
                else:
                    if param.get("action"):
                        action = int(param["action"][0])
                        if action > 0:    # To modifiy account
                            del dic['motpass']
                        return dumps(dic)  # To modifiy
                    else:
                        return dumps({'resp': {"result": 0} })    # Authenticate fail password empty
            else:
                return dumps({'resp': {"result": 0} })    # User is empty
        else:
            return dumps({'resp': {"result": 0} })    # No param
    except Exception as ex:
        return except_handler("authUser", ex)
        
def saveUser(param, self):
    """ To modify user account info"""
    try:
        if param.get("cour") and param.get("pass") and param.get("id"):
            user = param["cour"][0]
            passw = param["pass"][0]
            id = param["id"][0]
            name = param["name"][0]

            coll = dataBase.users
            
            def updUser(doc):
                if str(doc['motpass']) == passw:
                    if param.get("newpass"):
                        Npass = param["newpass"][0]
                        coll.update_one({"_id": o_id, "actif": True}, { "$set": {'Nom': name, 'courriel': user, 'motpass': Npass } })
                    else:
                        coll.update_one({"_id": o_id, "actif": True}, { "$set": {'Nom': name, 'courriel': user} })
                    return dumps({"resp": {"result":True, "email": user} })
                else:
                    return dumps({"resp": {"result":False, "message": "S0059"} }) # Invalid password
            
            def checkEmailExist(doc):
                docs = coll.find({"courriel": user, "_id": {"$ne": o_id}})
                if len(list(docs)):
                    return dumps({"resp": {"result":False, "message": "S0056"} }) # The new email allredy exist
                else:
                    return updUser(doc)
            
            o_id = getID(id)
            docs = coll.find({"_id": o_id, "actif": True})
            userDoc = list(docs)
            if len(userDoc):
                dic = cursorTOdict(userDoc)
                return checkEmailExist(dic);
            else:
                return dumps({resp: {"result":False, "message": "S0057"} }) # The new email allredy exist
        
            return dumps({ })    # modified
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("saveUser", ex)    

def getUserInfo(param, self):
    """ Get user account info by administrator"""
    try:
        if localHost or checkSession(self, role = ['ADM']):
            coll = dataBase.users
            if param.get("id"):
                o_id = getID(param["id"][0])
                doc = coll.find({"_id": o_id}, ["_id", "Nom", "courriel", "niveau", "actif", "note"])
                dic = cursorTOdict(doc)
                dic['role']    = ["MEM", "MEA", "ADM"]
                return dumps(dic)
            else:
                word = param["word"][0]
                if word == "xxxxx":
                    doc = coll.find({}, ["_id", "Nom", "courriel", "actif"])
                else:
                    doc = coll.find({"courriel": {'$regex': word}}, ["_id", "Nom", "courriel", "actif"]) 
                return dumps(doc)    
        else: 
            return ('{"n":0,"ok":0, "message": "S0062"}')    
    except Exception as ex:
        return except_handler("", ex)
        
def updateUser(param, self):
    """ To modify user account info by administrator"""
    try:
        if localHost or checkSession(self, role = ['ADM']):
            if param.get("id"):
                o_id = getID(param["id"][0])
                user = param["user"][0]
                if "name" in param:
                    name = param["name"][0]
                else:
                    name = ""
                role = param["role"][0]
                active = param["active"][0]
                active = True if active == '1' else False
                
                coll = dataBase.users
                docr = coll.update_one({"_id": o_id}, { "$set": {'Nom': name, 'courriel': user, "niveau": role, "actif": active } })
                return dumps(docr.raw_result)
            else:
                return dumps({'ok': 0})    # No param
        else: 
            return ('{"n":0,"ok":0, "message": "S0062"}')
    except Exception as ex:
        return except_handler("updateUser", ex)            
        
        
def savePassword(param, self):
    """ To modify password account by administrator"""
    try:

        if localHost or checkSession(self, role = ['ADM']):
            if param.get("id") and param.get("pass"):
                
                o_id = getID(param["id"][0])
                passw = param["pass"][0]
                                
                coll = dataBase.users
                docr = coll.update_one({"_id": o_id}, { "$set": {'motpass': passw } })
                if param.get("user_mail"):
                    email = param["user_mail"][0]
                    name = param["user_name"][0] if param.get("user_name") else "" 
                    sendRecupPassMail(email, name, passw)
                return dumps(docr)
            else:
                return dumps({'ok': 0})    # No param
        else: 
            return ('{"n":0,"ok":0, "message": "S0062"}')
    except Exception as ex:
        return except_handler("savePassword", ex)                


def getRegionList():
    #pdb.set_trace()
    col = dataBase.regions
    docs = col.find({})
    res = dumps(docs)
    return res
    
    
def getParcInfo(param, self):
    try:
        if param.get("data"):
            parcID = getID(param["data"][0])
            coll = dataBase.parcours
            docs = coll.find({"_id": parcID})
            pBlc = {}
            pBlc['data'] = [str(parcID)]

            #pdb.set_trace()
            oData = {}
            gps = getGolfGPS(pBlc, self, True)
            oData["courseInfo"] = (gps)
            #getBloc(pBlc, self)
            return dumps(oData)
        else:
            return dumps({'ok': 0})    # No param    
    except Exception as ex:
        return except_handler("getParcInfo", ex)            
    
C_WA = "àâäôóéèëêïîçùûüÿÀÂÄÔÉÈËÊÏÎŸÇÙÛÜ"
C_NA = "aaaooeeeeiicuuuyAAAOEEEEIIYCUUU"    
def scanName(name):
    for car in name:
        if (C_WA.find(car)) > 0:
            pos = C_WA.find(car)
            name = name.replace(car, C_NA[pos:pos+1], 1)
    return name.upper()
    
def searchResult(param, self):
    
    try:   
        def concatWord(field, word, cond = 0):
            req = []
            if cond == 0:
                cond = "$or"
                for wd in word.split():
                    regxV = re.compile(wd, re.IGNORECASE)
                    req.append({field: {"$regex": regxV} })
            else:
                for w in word.split():
                    req.append({field: {"$regex": '.*' + w + '.*'} })
            return {cond: req }
            
        def searchString(qNom, qVille, qReg, dist, lng, lat, mode = 0):
            qT = []
            #pdb.set_trace()
            Fnom, FVille = 'nom', 'municipal'
            if mode == 1:
                Fnom = 'nomU'
                qNom = scanName(qNom)
            if mode == 2:
                Fnom = 'nomP'
                qNom = phonetics.metaphone(qNom)           

            if qNom != '' and qVille != '':
                regxN = re.compile(qNom, re.IGNORECASE)
                regxV = re.compile(qVille, re.IGNORECASE)               
                q1 = {"$or": [ {"nom": {"$regex": regxN } } , {"municipal": {"$regex": regxV} }, concatWord(Fnom, qNom, "$and") , concatWord(FVille, qVille) ]}
                #q1 = {"$or": [ {Fnom: {"$regex": regxN } } , {FVille: {"$regex": regxI} } ]}
                qT.append(q1)
            else:
                if qNom != '':
                    q1 = concatWord(Fnom, qNom, "$and")
                if qVille != '':
                    q1 = concatWord(FVille, qVille) 
                if 'q1' in locals():
                    qT.append(q1)
            
            if qReg != None:
                q2 = {'region': qReg}
                qT.append(q2)

            if dist != None:
                q3 = {"location": { "$near" : {"$geometry": { "type": "Point",  "coordinates": [ lng , lat ] }, "$maxDistance": dist }}};
                qT.append(q3)
            
            return { "$and": qT }

        # Begin function
        #print(" BEGIN SEARCH")
        
        qNom, qVille, qReg, dist, lng, lat = '', '', None, None, None, None
        if param.get("qn"):
            qNom = param["qn"][0]  if (param["qn"][0] != "xxxxx") else ''
            qVille = param["qv"][0] if (param["qv"][0] != "xxxxx") else ''
        if param.get("qr"):
            qReg = int(param["qr"][0])
        if param.get("qd"):
            dist = float(param["qd"][0])
            lng = float(param["qlt"][0])
            lat = float(param["qln"][0])

        col = dataBase.club
        
        query = searchString(qNom, qVille, qReg, dist, lng, lat)
        #pdb.set_trace()
        docs = col.find(query).collation({"locale": "fr","strength": 1}).sort("nom")
        print("MODE = 0 " + str(query))
        li = list(docs)
        res={}
        res["ph"] = False
        if not len(li) and qNom != "":
            query = searchString(qNom, qVille, qReg, dist, lng, lat, 1)
            docs = col.find(query).sort("nom")
            print("MODE = 1 " + str(query))
            li = list(docs)
            if not len(li) and qNom != "":
                query = searchString(qNom, qVille, qReg, dist, lng, lat, 2)
                docs = col.find(query).collation({"locale": "fr","strength": 1}).sort("nom")
                li = list(docs)
                print("MODE = 2 " + str(query))
                res["ph"] = True
        res["data"]=li
        col = dataBase.regions
        res["regions"] = col.find({})
        res["posList"] = {}
        res["posList"]["lat"] = lat
        res["posList"]["lng"] = lng
        res["posList"]["dist"] = dist
        return dumps(res)
        
    except Exception as ex:
        return except_handler("searchResult", ex)


def getFav(param, self):
    try:
        if param.get("data"):
            userID = getID(param["data"][0])
            coll = dataBase.userFavoris
            docs = coll.find({"USER_ID": userID}, ["CLUB_ID"])
            
            def getClubNameList(clubList):
                coll = dataBase.club
                favDocs = coll.find({"_id":{"$in": clubList }},["_id","nom"]).sort("nom")
                return dumps(favDocs)
            
            ids = []
            for x in docs:
                ids.append(x['CLUB_ID'])            

            return getClubNameList(ids)
        else:
            return dumps({'ok': 0})    # No param        
    except Exception as ex:
        return except_handler("getFav", ex)
        
def updateFav(param, self):
    """ Add club to user favorite list"""
    try:
        if param.get("data"):
            clubList = param["data"][0]
            ids = [x for x in clubList.split("$")]
            clubID = int(ids[0])
            userID = getID(ids[1])
            action = int(ids[2])

            coll = dataBase.userFavoris

            if action == 1:
                docs = coll.insert_one({"CLUB_ID": clubID , "USER_ID": userID})
                if docs.acknowledged:
                    r = {'n': 0, 'ok': 1.0}
                else:
                    r = {'n': 0, 'ok': 0}
            else:
                docs = coll.delete_one({"CLUB_ID": clubID , "USER_ID": userID})
                r = docs
            return dumps(r)
        else:
            return dumps({'ok': 0})    # No param    
    except Exception as ex:
        return except_handler("updateFav", ex)
        
            
def getClubList(param, self):
    """ To get clubs list info"""
    if param.get("data"):
        clubList = param["data"][0]
        ids = [int(x) for x in clubList.split(",")]
        
        coll = dataBase.club
        docs = coll.find({"_id": {"$in": ids }}, {"_id": 1,"nom": 1, "adresse": 1, "municipal": 1, "telephone": 1, "telephone2": 1, "telephone3": 1, "location": 1, "courses.TROUS": 1}).sort("nom")
        
        return dumps(docs)
    else:
        return dumps({'ok': 0})    # No param

def getClubData(param, self):
    try:
        if param.get("data"):
            oData = []
            oData.append(getRegionList())
            clb = getClubParc(param, self)
            oData.append(clb)
            clb = loads(clb)

            strParc = ""
            for x in clb[0]['courses']:
                strParc += str(int(x['_id'])) + "$"
            strParc=strParc[0:len(strParc)-1]
            pBlc = {}
            pBlc['data'] = [strParc]
            oData.append(getBloc(pBlc, self))
            
            return dumps(oData)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getClubData", ex)        
        
def getClubParc(param, self):
    """ To get club and his courses info"""
    try:
        if param.get("data"):
            clubList = param["data"][0]
            ids = [x for x in clubList.split("$")]
            clubID = int(ids[0])
            userID = None if ids[1] == 'null' else ids[1]

            if userID:
                if len(userID) < 5:
                    userID = int(userID)
                else:    
                    userID = ObjectId(userID)
            
            def isFavorite(doc):
                if userID is not None and len(str(userID)) > 0:
                    coll = dataBase.userFavoris
                    favDoc = coll.find({"CLUB_ID": clubID , "USER_ID": userID}, ["CLUB_ID"])
                    if len(list(favDoc)):
                        doc['isFavorite'] = True
                    else:
                        doc['isFavorite'] = False
                return doc
                
            coll = dataBase.club
            docs = coll.find({"_id": clubID })
            dic = cursorTOdict(docs)

            return (dumps([(isFavorite(dic))]))
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getClubParc", ex)
        
def getBloc(param, self):
    try:    
        if param.get("data"):
            
            blocList = param["data"][0]
            ids = [int(x) for x in blocList.split("$")]
            coll = dataBase.blocs 
            docs = coll.find({"PARCOURS_ID":{"$in": ids }}).sort("PARCOURS_ID")
            return dumps(docs)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getBloc", ex)    
        
def getClubParcTrous(param, self):
    try:
        
        if param.get("data"):
            param = param["data"][0]
            ids = [int(x) for x in param.split("$")]
            clubID = ids[0]
            courseID = ids[1]
            #pdb.set_trace()
            coll = dataBase.club
            doc = coll.find({"_id": clubID }, ["_id","nom", "courses", "latitude", "longitude"])
            leDoc = list(doc)
            if len(leDoc):
                coll = dataBase.golfGPS
                docs = coll.find({"Parcours_id": courseID }).sort([['Parcours_id', 1], ['trou', 1]])
                lesTrous = list(docs)
                if len(lesTrous):
                    dic = cursorTOdict(leDoc)
                    res = [dic]                
                    res[0]['trous'] = lesTrous
                    return dumps(res)
                else:
                    return dumps(leDoc)

        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getClubParcTrous", ex)

        
def setGolfGPS(param, self):
    try:
        if param.get("data"):
            
            param = param["data"][0]
            para = [x for x in param.split("$")]
            courseId = int(para[0])
            trou = int(para[1])
            lat = float(para[2])
            lng = float(para[3])
            toInit = int(para[4])
            clubId = int(para[5])

            coll = dataBase.golfGPS
            if localHost or checkSession(self, role = ['ADM','MEA']):
                if toInit == 0:
                    docr = coll.update_one({ 'Parcours_id': courseId, 'trou': trou }, { '$set': {'Parcours_id': courseId, 'trou': trou, 'latitude': lat, 'longitude': lng } },  upsert=True )
                    return dumps(docr.raw_result)
                else:
                    for i in range(toInit):
                        holeNo = i + 1
                        resp = coll.update_one({ 'Parcours_id': courseId, 'trou': holeNo }, { '$set': {'Parcours_id': courseId, 'trou': holeNo, 'latitude': lat, 'longitude': lng } },  upsert=True)
                        if holeNo == toInit:
                            #pdb.set_trace()
                            coll = dataBase.parcours
                            pRep = coll.update_one({"_id":courseId}, {"$set":{"GPS": True }})
                            pa = coll.find({'CLUB_ID': clubId})
                            strCur = dumps(pa)
                            cur = loads(strCur)
                            coll = dataBase.club
                            res = coll.update_one({'_id': clubId}, {'$set':{"courses": cur }})
                            return dumps(res.raw_result)
            else: 
                return ('{"n":0,"ok":0, "message": "S0062"}')
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("setGolfGPS", ex)
        
def countUserGame(param, self):
    try:
        if param.get("data"):
            param = param["data"][0]
            para = [x for x in param.split("$")]
            user = getID(para[0])
            is18 = int(para[1])
            #pdb.set_trace()
            withGroup = True if len(para) > 2 else False
            
            coll = dataBase.score
            if (is18 == 18):
                count = coll.count_documents({"USER_ID": user, "T18": { "$exists": True, "$nin": [ 0 ] }})
                if withGroup == True:
                    group = coll.aggregate([ {"$match" : {"USER_ID": user, "T18": { "$exists": True, "$nin": [ 0 ] }}}, {"$group" : {"_id":{"name":"$name","parcours":"$PARCOURS_ID"}, "count":{"$sum":1}}}, { "$sort" : {"_id" : 1 } } ])
            else:
                count = coll.count_documents({"USER_ID": user, "$or":[{"T18":0},{"T18":None}]  } )
                if withGroup == True:
                    group = coll.aggregate([ {"$match" : {"USER_ID": user, "$or":[{"T18":0},{"T18":None}]  }}, {"$group" : {"_id":{"name":"$name","parcours":"$PARCOURS_ID"}, "count":{"$sum":1}}}, { "$sort" : {"_id" : 1 } } ])
            if withGroup == True:
                return ('{"count":' + str(count) + ',"group":' + dumps(group) + '}')
            else:
                return ('{"count":' + str(count) + '}')
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("countUserGame", ex)        


def getGameList(param, cpy):
    """Return game list result """
    try:
        if param.get("user"):
            user = int(param["user"][0])
            skip = int(param["skip"][0])
            limit = int(param["limit"][0])
            is18 = int(param["is18"][0])
            intDate = int(param["date"][0])
            if param.get("parc"):
                parc = int(param["parc"][0])
            else:
                parc = 0
            if param.get("tele"):
                intTele = int(param["tele"][0])
            else:
                intTele = 0

            if intDate == 0:   # ou 0 ???
                intDate = 9999999999999

            cur = []
            coll = dataBase.score

            def addCur(doc):
                #pdb.set_trace()
                for x in doc:
                    if intTele != 2:     # If not JSON format Date
                        ts = x['score_date'] / 1000
                        x['score_date'] = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    if intTele != 1:    # If CSV format _id
                        x['_id'] = str(x['_id'])
                        rd = x
                    else:                  # If CSV then personalize column head
                        rd = {'Course': x['name'], 'Date':x['score_date'], 'Hole1':int(x['T1']), 'Put1':int(x['P1']), 'Pen1':int(x['L1']), 'Hole2':int(x['T2']), 'Put2':int(x['P2']), 'Pen2':int(x['L2']), 'Hole3':int(x['T3']), 'Put3':int(x['P3']), 'Pen3':int(x['L3']), 'Hole4':int(x['T4']), 'Put4':int(x['P4']), 'Pen4':int(x['L4']), 'Hole5':int(x['T5']), 'Put5':int(x['P5']), 'Pen5':int(x['L5']), 'Hole6':int(x['T6']), 'Put6':int(x['P6']), 'Pen6':int(x['L6']), 'Hole7':int(x['T7']), 'Put7':int(x['P7']), 'Pen7':int(x['L7']), 'Hole8':int(x['T8']), 'Put8':int(x['P8']), 'Pen8':int(x['L8']), 'Hole9':int(x['T9']), 'Put9':int(x['P9']), 'Pen9':int(x['L9']), 'Hole10':int(x['T10']), 'Put10':int(x['P10']), 'Pen10':int(x['L10']), 'Hole11':int(x['T11']), 'Put11':int(x['P11']), 'Pen11':int(x['L11']), 'Hole12':int(x['T12']), 'Put12':int(x['P12']), 'Pen12':int(x['L12']), 'Hole13':int(x['T13']), 'Put13':int(x['P13']), 'Pen13':int(x['L13']), 'Hole14':int(x['T14']), 'Put14':int(x['P14']), 'Pen14':int(x['L14']), 'Hole15':int(x['T15']), 'Put15':int(x['P15']), 'Pen15':int(x['L15']), 'Hole16':int(x['T16']), 'Put16':int(x['P16']), 'Pen16':int(x['L16']), 'Hole17':int(x['T17']), 'Put17':int(x['P17']), 'Pen17':int(x['L17']), 'Hole18':int(x['T18']), 'Put18':int(x['P18']), 'Pen18':int(x['L18'])}
                        #, 'others': ''
                        #if 'others' in x:
                        #    rd['others'] = x['others']
                    cur.append(rd)
                
                if (intTele > 0):    # Request for download result in file

                    if (intTele == 2):    # JSON file
                        cpy.response.headers['Content-type'] = 'text/plain'
                        cpy.response.headers['Content-disposition'] = 'attachment; filename=myScore.json'
                        return bytes(dumps(cur), "utf8")

                    if (intTele == 1):    # CSV file
                        outFile = io.StringIO()
                        output = csv.writer(outFile, delimiter=';')
                        output.writerow(cur[0].keys())    #Column names
                        for x in cur:
                            output.writerow(x.values())

                        contents = outFile.getvalue()
                        outFile.close()

                        cpy.response.headers['Content-type'] = 'text/plain'
                        cpy.response.headers['Content-disposition'] = 'attachment; filename=myScore.csv'                        
                        return bytes(contents, "utf8")
                        
                else:                # Request for HTML page
                    return dumps(cur)

            if is18 == 18:
                qO = {"USER_ID": user, "score_date": {"$lt":intDate}, "T18": { "$exists": True, "$nin": [ 0 ] } }
                #doc = coll.find({"USER_ID": user, "PARCOURS_ID": parc, "score_date": {"$lt":intDate}, "T18": { "$exists": True, "$nin": [ 0 ] } }).sort("score_date",-1).skip(skip).limit(limit)
            else:
                qO = {"USER_ID": user, "score_date": {"$lt":intDate}, "$or":[{"T18":0},{"T18":None}]  }
                #doc = coll.find({"USER_ID": user, "score_date": {"$lt":intDate}, "$or":[{"T18":0},{"T18":None}]  } ).sort("score_date",-1).skip(skip).limit(limit)            

            if parc != 0:
                qO["PARCOURS_ID"] = parc                

            #qF = ["_id","USER_ID","PARCOURS_ID","name","score_date","T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12","T13","T14","T15","T16","T17","T18","others"]
            #qF = ["name","score_date","T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12","T13","T14","T15","T16","T17","T18"]
            doc = coll.find(qO).sort("score_date",-1).skip(skip).limit(limit)
            return addCur(doc)
            
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getGameList intTele=" + str(intTele), ex)
        
def getGameTab(param, self):
    try:
        if param.get("data"):
            
            gID = getID(param["data"][0])

            def getBloc(doc):
                coll = dataBase.blocs
                blocs = coll.find({"PARCOURS_ID": doc['PARCOURS_ID'] })
                for x in blocs:
                    if x['Bloc'] == "Normale":
                        doc['par'] = x
                return dumps([doc]) 
            
            coll = dataBase.score
            doc = coll.find({"_id":gID})
            game = list(doc)
            if len(game):
                doc = cursorTOdict(game)
                if doc['score_date'] != None:
                    ts = doc['score_date'] / 1000
                    doc['score_date'] = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')    
                return(getBloc(doc))
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getGameTab", ex)        

def endDelGame(param, self):
    try:
        if param.get("data"):
            param = param["data"][0]
            para = [x for x in param.split("$")]
            gID = para[0]
            o_id = getID(gID)
            action = int(para[1])
            resErr = '{"n":0,"ok":0, "message":'
            
            coll = dataBase.score
            if checkSession(self):
                if action == 0:    # Delete game
                   res = coll.delete_many({"_id":o_id})

                if action == 1:  # End Game
                    dateTime = int(millis())
                    log_Info("End game: " + gID)
                    res = coll.update_one({"_id":o_id}, { "$set": { "score_date": dateTime} })
                return dumps(res.raw_result)
            else: 
                resErr += "\"S0061\"}" if action == 0 else "\"S0060\"}"
                return (resErr)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("endDelGame", ex)
        
def updateGame(param, self):
    try:
        if param.get("data"):
            param = param["data"][0]
            para = [x for x in param.split("$")]
            user = int(para[0])
            parc = int(para[1])
            hole = int(para[2])
            stroke = int(para[3])
            put = int(para[4])
            lost = int(para[5])
            name = (para[6])
            bloc = (para[7])
            if stroke == 0:    #Delete score hole
                stroke = None
                put = None
                lost = None
            Tno = "T" + str(hole)
            Pno = "P" + str(hole)
            Lno = "L" + str(hole)
            
            coll = dataBase.score
            if len(para) > 8:
                sData = (para[8])
                sData = loads(sData)
                sField = dict()
                sField["USER_ID"] = user
                sField["PARCOURS_ID"] = parc
                sField["score_date"] = None
                sField["name"] = name
                sField["bloc"] = bloc
                sField[Tno] = stroke
                sField[Pno] = put
                sField[Lno] = lost
                #pdb.set_trace()
                hn = 1
                for sH in sData:
                    if len(sH) > 0:
                        Tno = "T" + str(hn)
                        Pno = "P" + str(hn)
                        Lno = "L" + str(hn)
                        sField[Tno] = None if sH["T"] == None else int(sH["T"])
                        sField[Pno] = None if sH["P"] == None else int(sH["P"])
                        sField[Lno] = None if sH["L"] == None else int(sH["L"])
                    hn+= 1
                
                if len(para) > 9:
                    oData = (para[9])
                    oData = loads(oData)
                    others = []
                    for oD in oData:
                        others.append(oD)
                    sField["others"] = others

                res = coll.update_one({ "USER_ID": user, "PARCOURS_ID": parc, "score_date": None }, { "$set": sField },  upsert=True)
            else:
                res = coll.update_one({ "USER_ID": user, "PARCOURS_ID": parc, "score_date": None }, { "$set": {"USER_ID": user, "PARCOURS_ID": parc, "score_date": None, "name": name, Tno: stroke, Pno: put, Lno: lost} },  upsert=True)
            
            return getGame(None, self, userID = user, parcID = parc)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("updateGame", ex)
        
def getGolfGPS(param, self, noDump = False):
    try:
        if param.get("data"):
            courseID = int(param["data"][0])
            coll = dataBase.golfGPS
            
            def getBlocGPS(gData):
                coll = dataBase.blocs
                doc = coll.find({"PARCOURS_ID": courseID })
                Pdoc =dumps(gData)
                Pdoc=loads(Pdoc)
                Pdoc[0]['parc'] = doc
                if noDump:
                    return (Pdoc)
                else:
                    return dumps(Pdoc)

            doc = coll.find({"Parcours_id": courseID }).sort("trou")

            return getBlocGPS(doc)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getGolfGPS", ex)
        
def getGame(param, self, userID = False, parcID = False):
    try:
        def getG(user, parc):
            coll = dataBase.score
            doc = coll.find({ "USER_ID": user, "PARCOURS_ID": parc, "score_date": None })
            game = list(doc)
            if len(game):
                cur = cursorTOdict(game)
                cur['_id'] = str(cur['_id'])
                return dumps([cur]) 
            else:
                return dumps([]) 
            
        if param:
            if param.get("data"):
                param = param["data"][0]
                para = [x for x in param.split("$")]
                user = int(para[0])
                parc = int(para[1])
                return getG(user, parc)
        else:
            return getG(userID, parcID)
    except Exception as ex:
        return except_handler("getGame", ex)

        
def saveClub(param, self):
    """ Save Club, courses and blocs data """

    try:
        if param.get("data"):
            
            #pdb.set_trace()
            obj = loads(param['data'][0])
            def saveBlocs(tupC, Bids):
                """ Save blocs data for the courses """
                blocRes = []
                coll = dataBase.blocs
                def getBlocID():
                    docID = coll.find({}).sort("_id",-1).limit(1)
                    return int(docID[0]["_id"] + 1)
                
                for bloc in oBlocs:
                    res=dict()
                    
                    if len(str(bloc["_id"])) < 9 and int(bloc["_id"]) > 1000000:    # Not ObjectID and new attributed bloc ID 
                        res["oldID"] = bloc["_id"]
                        bloc["_id"] =  ObjectId()  #getBlocID()
                        res["newID"] = str(bloc["_id"])
                        for y in tupC:
                            if bloc["PARCOURS_ID"] in y:
                                bloc["PARCOURS_ID"] = y[1]    # Replace PARCOURS_ID by res["newID"] attributed
                    else:
                        bloc["_id"] = getID(str(bloc["_id"]))
                        if bloc["_id"] in Bids:
                            Bids.remove(bloc["_id"])
                    #print("save id " + str(bloc["_id"]) + "  PARCOURS_ID " + str(bloc["PARCOURS_ID"]))
                    doc = coll.update_one({ '_id': bloc["_id"]}, { '$set': {'PARCOURS_ID': bloc["PARCOURS_ID"], 'Bloc': bloc["Bloc"], 'T1': bloc["T1"], 'T2': bloc["T2"], 'T3': bloc["T3"], 'T4': bloc["T4"], 'T5': bloc["T5"], 'T6': bloc["T6"], 'T7': bloc["T7"], 'T8': bloc["T8"], 'T9': bloc["T9"], 'T10': bloc["T10"], 'T11': bloc["T11"], 'T12': bloc["T12"], 'T13': bloc["T13"], 'T14': bloc["T14"], 'T15': bloc["T15"], 'T16': bloc["T16"], 'T17': bloc["T17"], 'T18': bloc["T18"], 'Aller': bloc["Aller"], 'Retour': bloc["Retour"], 'Total': bloc["Total"], 'Eval': bloc["Eval"], 'Slope': bloc["Slope"] } },  upsert=True )

                    res["result"]=doc.raw_result
                    res["result"]["_id"] = bloc["_id"]
                    blocRes.append(res)

                docs = coll.delete_many({"_id": {"$in": Bids } })
                return blocRes, Bids
                
            def saveCourses(clubID, tupC, Pids):
                """ Save courses data for the Club """
                courseRes = []
                coll = dataBase.parcours
                def getCourseID():
                    docID = coll.find({}).sort("_id",-1).limit(1)
                    return int(docID[0]["_id"] + 1)
                def removeCourse(Pids):
                    collB = dataBase.blocs
                    docs = coll.delete_many({"_id": {"$in": Pids } })            # Remove Courses
                    docs = collB.delete_many({"PARCOURS_ID": {"$in": Pids } })    # Remove Bloc Courses
                    collG = dataBase.golfGPS
                    docs = collG.delete_many({"Parcours_id": {"$in": Pids } })    # Remove GPS Courses   À TESTER
                    return

                for parc in oCourses:
                    res=dict()
                    if parc["_id"] > 1000000:
                        res["oldID"] = parc["_id"]
                        parc["_id"] = getCourseID()
                        res["newID"] = parc["_id"]
                        tupC = tupC,(res["oldID"],res["newID"])
                    #removeBloc(parc["_id"])
                    #print("save courses " + str(parc["_id"]))
                    doc = coll.update_one({ '_id': parc["_id"]}, { '$set': {'CLUB_ID': parc["CLUB_ID"], 'POINTS': parc["POINTS"], 'PARCOURS': parc["PARCOURS"], 'DEPUIS': parc["DEPUIS"], 'TROUS': parc["TROUS"], 'NORMALE': parc["NORMALE"], 'VERGES': parc["VERGES"], 'GPS': parc["GPS"] } },  upsert=True )
                    res["result"]=doc.raw_result
                    res["result"]["_id"] = parc["_id"]
                    courseRes.append(res)
                    if parc["_id"] in Pids:
                        Pids.remove(parc["_id"])
                
                if len(Pids) > 0:
                    removeCourse(Pids)
                return courseRes, tupC, Pids
                #[{'_id': '39', 'CLUB_ID': 47, 'POINTS': '24', 'PARCOURS': '', 'DEPUIS': '1990', 'TROUS': '18', 'NORMALE': '72', 'VERGES': '6322', 'GPS': True}, {'_id': 61, 'CLUB_ID': 47, 'POINTS': 'E', 'PARCOURS': '', 'DEPUIS': 0, 'TROUS': 9, 'NORMALE': 27, 'VERGES': 815, 'GPS': False}]
            
            """ Save Club data """

            if localHost or checkSession(self, role = ['ADM','MEA']):
            #if True:
                coll = dataBase.club
                def getClubID():
                    docID = coll.find({}).sort("_id",-1).limit(1)
                    return int(docID[0]["_id"] + 1)

                tupC = (0,0),(0,0)    # For new PARCOURS_ID in blocs
                oClub = obj["club"]
                oCourses = obj["course"]
                if 'blocs' in obj:
                    oBlocs = obj["blocs"]
                #Postal code
                cp = oClub["codp"]
                cp = cp.upper()
                cp = re.sub(r" ", "", cp)
                cps = cp
                matchObj = re.match("^(?!.*[DFIOQU])[A-VXY][0-9][A-Z]●?[0-9][A-Z][0-9]$"  ,cp)
                if (matchObj):
                    cps = cp[0:3] + " " + cp[3:6]

                clubID = oClub["ID"]
                if clubID > 1000000:    # New club
                    clubID = getClubID()
                
                nomU = scanName(oClub["name"])
                nomP = phonetics.metaphone(oClub["name"])
                doc = coll.update_one({ '_id': clubID}, { '$set': {'nom': oClub["name"], 'nomU': nomU, 'nomP': nomP, 'prive': oClub["prive"], 'adresse': oClub["addr"], 'municipal': oClub["ville"], 'codepostal': cp, 'codepostal2': cps, 'url_club': oClub["urlc"], 'url_ville': oClub["urlv"], 'telephone': oClub["tel1"], 'telephone2': oClub["tel2"], 'telephone3': oClub["tel3"], 'email': oClub["email"], 'region': oClub["region"], 'latitude': oClub["lat"], 'longitude': oClub["lng"] } },  upsert=True )
                #pdb.set_trace()
                res=doc.raw_result
                doc = res
                Pids = getCourseColl(clubID)
                Bids = getBlocColl(Pids)
                courseRes, tupC, cRem = saveCourses(clubID, tupC, Pids)
                if 'oBlocs' in locals():
                    blocRes, bRem = saveBlocs(tupC, Bids)
                else:
                    blocRes = []
                    bRem = []
                upd=coll.update_one({'_id':clubID}, {'$set':{"courses": oCourses, "location": {'type': "Point", 'coordinates': [ oClub["lng"], oClub["lat"] ]} }});
                doc["courses"] = courseRes
                doc["blocs"] = blocRes
                doc["removedC"] = cRem
                doc["removedB"] = bRem
                return dumps(doc)
            else: 
                return ('{"n":0,"ok":0, "message": "S0062"}')    # Check Session error
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("saveClub", ex)

def getCourseColl(clubID):
    collP = dataBase.parcours
    Pdocs = collP.find({"CLUB_ID": clubID })
    Pids = []
    for x in Pdocs:
        Pids.append(x['_id'])
    return Pids

def getBlocColl(courseColl):
    collB = dataBase.blocs
    Bdocs = collB.find({"PARCOURS_ID":{"$in": courseColl }})
    Bids = []
    for x in Bdocs:
        Bids.append(x['_id'])
    return Bids
    
def delClub(param, self):
    try:
        if param.get("data"):
            clubID = int(param["data"][0])
            if usepdb == 3:
                pdb.set_trace()            
            collC = dataBase.club
            collP = dataBase.parcours
            collB = dataBase.blocs
            
            # Course collection
            Pids = getCourseColl(clubID)
                
            #Remove data
            doc = collB.delete_many({"PARCOURS_ID":{"$in": Pids }})
            doc = collP.delete_many({"CLUB_ID":clubID})
            doc = collC.delete_many({"_id": clubID })
            
            return dumps(doc.raw_result)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("delClub", ex)

def setPosition(param, self):
    try:
        if param.get("data"):
            param = param["data"][0]
            para = [x for x in param.split("$")]
            coll = dataBase.trajet
            #pdb.set_trace()
            userId = getID(para[0])
            timeStart = int(para[1])
            locTime = int(para[2])
            locLat = float(para[3])
            locLng = float(para[4])
            locAcc = int(float(para[5]))
            #print('SAVE...' + str(param))
            if (len(para) > 6):
                hotSpot = int(para[6])
                if (len(para) > 7):
                    alt = int(para[7])
                    #print('Para8-' + str(para[7]))
                else:
                    alt = 0
                if (len(para) > 8 and int(para[8]) != 0):
                    oldTime = int(para[8])
                    doc = coll.update_one( { 'USER_ID': userId, 'startTime': timeStart, 'locList.time': oldTime}, {'$set':{'locList.$.time': locTime, 'locList.$.lat': locLat, 'locList.$.lng': locLng, 'locList.$.acc': locAcc, 'locList.$.hot': hotSpot, 'locList.$.alt': alt}},  upsert=True )
                else:
                    doc = coll.update_one( { 'USER_ID': userId, 'startTime': timeStart}, {'$push': {'locList': {'time': locTime, 'lat': locLat, 'lng': locLng, 'acc': locAcc, 'hot': hotSpot, 'alt': alt}}},  upsert=True )
            else:
                doc = coll.update_one( { 'USER_ID': userId, 'startTime': timeStart}, {'$push': {'locList': {'time': locTime, 'lat': locLat, 'lng': locLng, 'acc': locAcc}}},  upsert=True )
            #doc = coll.update_one( { 'USER_ID': userId, 'startTime': { '$gte': timeStart, '$lte': timeEnd }, {'$push': {'locList': {'time': locTime, 'lat': locLat, 'lng': locLng, 'acc': locAcc}}},  upsert=True )
            return dumps(doc)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("setPosition", ex)


def delPosition(param, self):
    try:
        if param.get("data"):
            param = param["data"][0]
            para = [x for x in param.split("$")]
            coll = dataBase.trajet
            #pdb.set_trace()
            userId = getID(para[0])
            timeStart = int(para[1])
            locTime = int(para[2])
            
            doc = coll.update_one( { 'USER_ID': userId, 'startTime': timeStart}, {'$pull': {'locList': {'time': locTime}}} )
            
            return dumps(doc)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("delPosition", ex)            


def setBallPosition(param, self):
    try:
        if param.get("data"):
            param = param["data"][0]
            para = [x for x in param.split("$")]
            userId = getID(para[0])
            timeStart = int(para[1])

            coll = dataBase.trajet
            result = 1
            mess = ""
            #pdb.set_trace()
            if timeStart == 0:
                doc = coll.find({"USER_ID": userId}).sort("startTime",-1).limit(1)
                if round(time.time() * 1000) - doc[0]["startTime"] < 21600000:  # Moins que 6 heures
                    param = param.replace("$0$", "$" + str(doc[0]["startTime"]) + "$")
                    timeStart = doc[0]["startTime"]
                    res = loads(setPosition({'data': [param]}, self))
                else:
                    result = 0
                    mess = "No GPS"
                    return dumps({'ok': 0, 'startTime': timeStart, "message": mess })
            else:
                res = loads(setPosition({'data': [param]}, self))
            
            res["startTime"] = timeStart
            return dumps(res)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("setBallPosition", ex)
        
def getPosition(param, self):
    try:
        if param.get("data"):
            param = param["data"][0]
            para = [x for x in param.split("$")]
            userId = getID(para[0])
            timeStart = int(para[1])

            timeEnd = timeStart + 86400000    # + 24hre

            coll = dataBase.trajet
            pdb.set_trace()
            if timeStart == 0:
                doc = coll.find( { 'USER_ID': userId}).sort("_id",-1).limit(1)
            else:
                if len(para) > 2:
                    doc = coll.find( { 'USER_ID': userId, 'startTime': timeStart })
                else:
                    doc = coll.find( { 'USER_ID': userId, 'startTime': { '$gte': timeStart, '$lt': timeEnd } })
                if not len(list(doc)):
                    doc = coll.find( { 'USER_ID': userId, 'startTime': { '$gte': timeStart}}).sort("_id").limit(5)
            pos = list(doc)
            if len(pos):
                return dumps(pos)
            else:
                return dumps({'length': 0, 'timeStart': timeStart})
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getPosition", ex)
        
# Manage logs

def log_Info(mess):
    #pdb.set_trace()
    ip = gethostbyname(gethostname()) 
    if 'X-Real-Ip' in cherry.request.headers:
        ip = cherry.request.headers['X-Real-Ip']
    t = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    mess = re.sub(r"<|>", " ", mess)    # Remplace tags < > by space
    strMess = t + " | " + ip + " | " + mess + "\n"
    with open(LOG_FILE,'a') as f:
        f.write(strMess)

def listLog(param, logPass):
    """ For typing password """
    if param:

        if logPass == param:
            return(listLogs())
        else:
            log_Info('listLog Unauthorized: ' + param)
            return('<h2>Unauthorized</h2>')
    else:
        htmlCode = '<!DOCTYPE html><html lang="en-CA"><head><meta name="viewport" content="width=device-width" /></head><body><form action="listLog" method="post"><input id="passw" name="passw" type="password" /><input type="submit"/></form></body></html>'
        return(htmlCode)

def listLogs():
    """ List file in log directory"""
    fileList = os.listdir(LOG_DIR)
    cont = '<h2>Log files</h2>'
    for line in fileList:
        f = os.stat(LOG_DIR + '/' + line)
        t = time.ctime(f.st_ctime)
        s = f.st_size
        cont = cont + '<a target="_blank" href="./showLog?name=' + line + '">' + line + "\t" + t + "\t" + str(int(s/1024) + 1) + " ko" '</a></br>'
    #print(fileList)
    return(str(cont))
    
def showLog(param):
    """ Display log file"""
    try:
        #pdb.set_trace()
        fileName = param
        lines = [line.rstrip('\n') for line in open(LOG_DIR + "/" + fileName)]
        f = os.stat(LOG_DIR + '/' + fileName)
        cont = '<h2>' + fileName + "  " + time.ctime(f.st_ctime) + '</h2>'
        for line in lines:
            cont = cont + line + '</br>'
        return(str(cont))
    except Exception as ex:
        return except_handler("showLog", ex)
    

# Send mail
def sendRecupPassMail(eMail, name, passw):
    """ Send email to retreive password"""
    text = ''
    name = name if name != '' else eMail
    html = """\
    <html><body><div style="text-align: center;"><div style="background-color: #3A9D23;height: 34px;"><div style="margin: 3px;float:left;"><img alt="Image Golf du Québec" width="25" height="25" src="https://cdore00.github.io/golf/images/golf.png" /></div><div style="font-size: 22px;font-weight: bold;color: #ccf;padding-top: 5px;">Golfs du Qu&eacute;bec</div></div></br><p style="width: 100; text-align: left;">Bonjour %s,</p><p></p><p style="width: 100; text-align: left;">Votre mot de passe est : %s </p><p></p><p><div id="copyright">Copyright &copy; 2005-2017</div></p></div></body></html>
    """  % (name, passw)
    fromuser = "Golf du Québec"
    subject = "Golf du Québec - Récupérer mot de passe de " + name 
    log_Info("Récupérer mot de passe de " + name + " : " + eMail)
    send_email(fromuser, eMail, subject, text, html)

def sendConfMail(HOSTclient, email, name):

    recipient = email
    subject = "Golf du Québec - Confirmer l'inscription de cdore00@yahoo.com"
    
    fromuser = "Golf du Québec"

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi %s!\nCliquer ce lien pour confirmer l\'inscription de votre compte:\n%s\n\nGolf du Québec" % (name, HOSTclient)
    html = """\
    <html><body><div style="text-align: center;"><div style="background-color: #3A9D23;height: 40px;"><div style="margin: 3px;float:left;"><img alt="Image Golf du Québec" width="25" height="25" src="https://cdore00.github.io/golf/images/golf.png" /></div><div style="font-size: 22px;font-weight: bold;color: #ccf;padding-top: 5px;">Golfs du Qu&eacute;bec</div></div></br><a href="%s" style="font-size: 20px;font-weight: bold;">Cliquer ce lien pour confirmer l\'inscription de votre compte:<p>%s</p> </a></br></br></br><p><div id="copyright">Copyright &copy; 2005-2020</div></p></div></body></html>
    """ % (HOSTclient, email)
    send_email(fromuser, recipient, subject, text, html)

def send_email(fromuser, recipient, subject, text, html):
    """ Send email"""
    # Create message container - the correct MIME type is multipart/alternative.
    #pdb.set_trace()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromuser
    msg['To'] = recipient 

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    #pdb.set_trace()
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(MAIL_USER, logPass)
    mail.sendmail(fromuser, recipient, msg.as_string())
    mail.quit()
