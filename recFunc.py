import pdb
import sys, os, io, time, re, cgi, csv
import smtplib
import phonetics
import dropbox, base64
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
   
#Log file
LOG_DIR = (os.getcwd() if os.getcwd() != '/' else '') + '/log'
#pdb.set_trace()
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = LOG_DIR + '/pytServer.log'
print("logfile= " + LOG_FILE)

IMG_DIR = LOG_DIR + "/"
IMG_URL = "file:///" + IMG_DIR

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

def getCurrentUser():
    """ Return current userID in cookie"""
    #pdb.set_trace()
    cookie = cherrypy.request.cookie
    if cookie and 'sessID' in cookie and 'userID' in cookie:
        return getID(cookie['userID'].value)
    else:
        return None

def checkSession(self, role = None):
    """ Session ID check for user"""
    
    cookie = cherrypy.request.cookie
    print('1-Cookies = ' + str(cookie))
    if usepdb == 0:
        pdb.set_trace()
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
                res = coll.insert_one({"Nom": user , "courriel": email, "motpass": passw , "niveau": "MEM", "actif": False}, {"new":True})

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


def sendRecetMail(param, self):
    """ Send recette by email """
    try:
        if param.get("data"):
            data = (param["data"][0])
            ids = [x for x in data.split("$")]
            email = (ids[0])
            recetID = ObjectId(ids[1])
            url = ids[2]
            
            coll = dataBase.recettes
            doc = coll.find({"_id": recetID})
            docs = list(doc)
            #pdb.set_trace()
            strRecet = ""
            if len(docs):
                ingLi = ['<li>' + x + '</li>' for x in docs[0]['ingr']]
                htm = '<b>Ingrédients</b></br><ol>' + ''.join(ingLi) + '</ol>'
                ingLi = ['<li>' + x + '</li>' for x in docs[0]['prep']]
                htm += '</br><b>Préparation</b></br><ol>' + ''.join(ingLi) + '</ol>'
                htm += '<p></br></br>' + url + '</p>'
                sendRecet(email, docs[0]['nom'], htm)
                return dumps({"code":-1, "message": "S0063"})
            else:
                return dumps({"code": 1, "message": "S0055"})
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("sendRecetMail", ex)


def getPassForm(self):
    """ Return HTML code form to change password """
    htmlContent = '<div id="accountForm"><div id="titrePref">Edit account</div><form id="formPass"></br> <div class="prefList"><label for="passUser" class="identLbl">New password</label><div class="prefVal"><input id="passUser" type="text" size="15" maxlength="20"/></div></div> <div><input id="okPref" class="bouton" type="submit" onClick="savePass(); return false;" value="Ok" /><input id="annulePref" class="bouton" type="button" onClick="closePref(); return false;"  value="Cancel"/></div></form></div>'
    #writeCook(self,htmlContent)
    return htmlContent    

    
def authUser(param, self, cookie):
    """ To Authenticate or return user info to modify """
    try:    
        
        if param:
            if not isinstance(param, (list)) and param.get("user"):
                user = param["user"][0]
                #print("1- user= " + str(user))
                coll = dataBase.users
                doc = coll.find({"courriel": user, "actif": True}, ["_id","Nom", "courriel", "motpass", "niveau"])
                userDoc = list(doc)
                if usepdb == 3:
                    pdb.set_trace()               
                def setSessID(mess, userID):
                    if usepdb == 3:
                        pdb.set_trace()
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
                        res = coll.update_one({"courriel": user}, { "$set": {"sessID": ""}})
                        key = 'sessID'
                        cherrypy.response.cookie[key] = ''
                        cherrypy.response.cookie[key]['expires'] = 0
                        cherrypy.response.cookie[key]['max-age'] = 0 
                        return dumps({'resp': {"result": 0} })    # Authenticate fail
                        #cookie['sessID']['max-age'] = 0
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
                doc = coll.find({"_id": o_id}, ["_id", "Nom", "courriel", "niveau", "actif", "note", "imgUser"])
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

def getUserIdent(o_id):
    """ Get user identity"""
    data = {"nom":"","email":"","imgUser":""}
    coll = dataBase.users
    doc = coll.find({"_id": o_id}, ["_id", "Nom", "courriel", "imgUser"])
    info = list(doc)
    if len(info):
        data["nom"] = info[0]["Nom"]
        data["email"] = info[0]["courriel"]
        data["imgUser"] = info[0]["imgUser"]
    return data
    
    
def getUsersIdent(o_id):
    """ Get user identity"""
    coll = dataBase.users

    doc = coll.find({"_id":{"$in": o_id }},["_id","Nom", "courriel", "imgUser"])
    info = list(doc)

    return info    
  
    
def updateUser(param, self):
    """ To modify user account info by administrator"""
    try:
        if localHost or checkSession(self, role = ['ADM']):
            if param.get("id"):
                o_id = getID(param["id"][0])
                user = param["user"][0]
                #pdb.set_trace()
                if "name" in param:
                    name = param["name"][0]
                else:
                    name = ""
                if "imgUser" in param:
                    imgUser = param["imgUser"][0]
                else:
                    imgUser = ""            
                    
                role = param["role"][0]
                active = param["active"][0]
                active = True if active == '1' else False
                
                coll = dataBase.users
                docr = coll.update_one({"_id": o_id}, { "$set": {'Nom': name, 'courriel': user, "niveau": role, "actif": active, "imgUser": imgUser } })
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


def getCategorieList():
    #pdb.set_trace()
    col = dataBase.categorie
    docs = col.find({})
    res = dumps(docs)
    return res
    
    
C_WA = "àâäôóéèëêïîçùûüÿÀÂÄÔÉÈËÊÏÎŸÇÙÛÜ()"
C_NA = "aaaooeeeeiicuuuyAAAOEEEEIIYCUUU  "    
def scanName(name):
    for car in name:
        if (C_WA.find(car)) > -1:
            pos = C_WA.find(car)
            name = name.replace(car, C_NA[pos:pos+1], 1)
    return name.upper()
    
def getUserRole():
    if usepdb == 3:
        pdb.set_trace()
    cookie = cherrypy.request.cookie
    userRole = ""
    if 'userRole' in  cookie:
        userRole = cookie['userRole'].value    
    return userRole
    
def searchResult(param, self):

    try:
        def concatWord(field, word):
            req = []
            for w in word.split():
                req.append({field: {"$regex": '.*' + w + '.*'} })
            return {"$and": req }
            #{"$and": {"$elemMatch": req }}
        
        def searchString(qNom, qIngr, qCat, mode = 0):
            qT = []
            #pdb.set_trace()
            
            Fnom, Fingr = 'nom','ingr'
            if mode == 1:
                Fnom, Fingr = 'nomU','ingrU'
                qNom, qIngr = scanName(qNom), scanName(qIngr)
            if mode == 2:
                Fnom, Fingr = 'nomP','ingrP'
                qNom, qIngr = phonetics.metaphone(qNom), phonetics.metaphone(qIngr)
            #regxN = re.compile(qNom, re.IGNORECASE)
            #regxI = re.compile(qIngr, re.IGNORECASE)
            if qNom != '' and qIngr != '':
                q1 = {"$or": [ concatWord(Fnom, qNom) , concatWord(Fingr, qIngr) ]}
                #q1 = {"$or": [ {Fnom: {"$regex": regxN } } , {Fingr: {"$regex": regxI} } ]}
                qT.append(q1)
            else:
                if qNom != '':
                    q1 = concatWord(Fnom, qNom)
                if qIngr != '':
                    q1 = concatWord(Fingr, qIngr) 
                if 'q1' in locals():
                    qT.append(q1)
            
            if qCat != None:
                q2 = {'cat._id': qCat}
                qT.append(q2)

            userRole = getUserRole()
            if not (localHost or userRole == 'ADM' or userRole == 'MEA'):
                qT.append({"state": 1 })

            return { "$and": qT }

        # Begin function
        #pdb.set_trace()
        qNom, qIngr, qCat = '', '', None
        if param.get("qn"):
            qNom = param["qn"][0]  if (param["qn"][0] != "xxxxx") else ''
            qIngr = param["qv"][0] if (param["qv"][0] != "xxxxx") else ''
        if param.get("qr"):
            qCat = int(param["qr"][0])

        col = dataBase.recettes
        query = searchString(qNom, qIngr, qCat)
        fields = {"_id": 1,"nom": 1, "cat": 1, "temp": 1, "cuis": 1, "port": 1, "state": 1}
        docs = col.find(query, fields).collation({"locale": "fr","strength": 1}).sort("nom")

        li = list(docs)
        res={}
        res["ph"] = False
        if not len(li) and qNom + qIngr != "":
            query = searchString(qNom, qIngr, qCat, 1)
            docs = col.find(query, fields).sort("nom")
            li = list(docs)
            if not len(li) and qNom != "":
                query = searchString(qNom, qIngr, qCat, 2)
                docs = col.find(query, fields).collation({"locale": "fr","strength": 1}).sort("nom")
                li = list(docs)
                res["ph"] = True
        #pdb.set_trace()
        res["data"]=li
        col = dataBase.regions
        res["regions"] = col.find({})
        return dumps(res)
        
    except Exception as ex:
        return except_handler("searchResult", ex)


def getFav(param, self):
    try:
        if param.get("data"):
            userID = getID(param["data"][0])
            coll = dataBase.userFavoris
            docs = coll.find({"USER_ID": userID}, ["REC_ID"])
            
            def getRecNameList(recList):
                coll = dataBase.recettes
                favDocs = coll.find({"_id":{"$in": recList }},["_id","nom"]).sort("nom")
                return dumps(favDocs)
            
            ids = []
            for x in docs:
                ids.append(x['REC_ID'])            

            return getRecNameList(ids)
        else:
            return dumps({'ok': 0})    # No param        
    except Exception as ex:
        return except_handler("getFav", ex)
        
def updateFav(param, self):
    """ Add recipe to user favorite list"""
    try:
        if param.get("data"):
            recList = param["data"][0]
            ids = [x for x in recList.split("$")]

            recID = ObjectId(ids[0])
            userID = getID(ids[1])
            action = int(ids[2])

            coll = dataBase.userFavoris

            if action == 1:
                docs = coll.insert_one({"REC_ID": recID , "USER_ID": userID})
                if docs.acknowledged:
                    r = {'n': 0, 'ok': 1.0}
                else:
                    r = {'n': 0, 'ok': 0}
            else:
                docs = coll.delete_one({"REC_ID": recID , "USER_ID": userID})
                r = docs.raw_result
            return dumps(r)
        else:
            return dumps({'ok': 0})    # No param    
    except Exception as ex:
        return except_handler("updateFav", ex)
        
            
def getRecList(param, self):
    """ To get clubs list info"""
    if param.get("data"):
        recList = param["data"][0]
        ids = [ObjectId(x) for x in recList.split(",")]
        #pdb.set_trace()
        #state = 1
        request = {"_id": {"$in": ids }}
        userRole = getUserRole()
        if not (localHost or userRole == 'ADM' or userRole == 'MEA'):
            request["state"] = 1
        coll = dataBase.recettes
        docs = coll.find( request, {"_id": 1,"nom": 1, "cat": 1, "temp": 1, "cuis": 1, "port": 1, "state": 1}).sort("nom")
        
        return dumps(docs)
    else:
        return dumps({'ok': 0})    # No param
    
        
def getRecette(param, self):
    """ To get recette info"""
    
    def isFavorite(recetID, userID):
    
        if userID is not None:
            coll = dataBase.userFavoris
            favDoc = coll.find({"REC_ID": recetID , "USER_ID": userID}, ["REC_ID"])
            if len(list(favDoc)):
                return True
            else:
                return False
        return False    

    try:
        if usepdb == 0:
            pdb.set_trace()
        if param.get("data"):
            recList = param["data"][0]
            ids = [x for x in recList.split("$")]
            userID = None
            if len(ids) > 1:
                userID = None if (ids[1] == 'null' or ids[1] == '') else ids[1]
            docs = None
            ret={}
            if len(ids) == 1 or ids[1] != "NEW":
                recetID = ObjectId(ids[0])
                coll = dataBase.recettes
                docs = coll.find({"_id": recetID })
                ret["user"] = getUserIdent(docs[0]["userID"])
                if  userID != None and len(userID) != 3:
                    ret["isFav"] = isFavorite(recetID, ObjectId(userID))
                rec = cursorTOdict(docs)
                ret["rec"]= [rec]
                
                Hids = []
                Hids.append(rec['userID'])
                if "hist" in rec:
                    for x in rec["hist"]:
                        Hids.append(x['userID'])
                ret["histUser"] = getUsersIdent(Hids)
                
            if len(ids) > 1:
                col = dataBase.categorie
                docCats = col.find({})
                ret["cat"]=docCats

            return dumps(ret)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("getRecette", ex)

def saveRecet(param, self):
    """ Save Recette data """

    try:
        if param.get("data"):
            
            if usepdb == 0:
                pdb.set_trace()
            obj = loads(param['data'][0])
            imgURL = ""
            if param.get("imgURL"):
                imgURL = param['imgURL'][0]
            #print(str(imgURL))

            """ Save Recette data """
            cookie = cherrypy.request.cookie

            if localHost or checkSession(self, role = ['ADM','MEA']):
            #if True:
                if "dropbox" not in imgURL and len(imgURL) != 0:
                    imgURL = saveImg(imgURL, self)
                
                coll = dataBase.recettes
                
                oIngr = obj["ingr"]
                oPrep = obj["prep"]
                
                nomU = scanName(obj["nom"])
                nomP = phonetics.metaphone(obj["nom"])
                Cuser = getCurrentUser()
                state = 1 if obj["state"] else 0
                actTime = int(time.time() * 1000)

                Uvals = []  #ingrédients upper case
                Pvals = []  #ingrédients phonetic
                for x in oIngr:
                    Uval = scanName(x)
                    Uvals.append(Uval)
                    mots = Uval.split()
                    Pmots = ''
                    for m in mots:
                        if m.isnumeric() == False and len(m) > 2:
                            Pmots = Pmots + phonetics.metaphone(m) + ' '
                    Pvals.append(Pmots)

                
                editData = ""
                if param.get("editor"):
                    editData = param['editor'][0]

                if obj["ID"] == "NEW":    # Nouvelle recette
                    oID = ObjectId()
                    doc = coll.update_one({ '_id': oID}, { '$set': {'nom': obj["nom"], 'nomU': nomU, 'nomP': nomP, "dateC": actTime, "dateM": actTime, 'userID': Cuser, 'temp': obj["temp"], 'port': obj["port"], 'cuis': obj["cuis"], 'cat': obj["cat"], 'url': obj["url"], "state": state, 'imgURL': imgURL, 'ingr': oIngr, 'prep': oPrep, 'edit': editData } },  upsert=True )
                else:
                    oldDoc = loads(getRecette({'data':[ obj["ID"] ]}, self))['rec'][0]
                    oID = ObjectId(obj["ID"])
                    doc = coll.update_one({ '_id': oID}, { '$set': {'nom': obj["nom"], 'nomU': nomU, 'nomP': nomP, "dateM": actTime, 'userID': Cuser, 'temp': obj["temp"], 'port': obj["port"], 'cuis': obj["cuis"], 'cat': obj["cat"], 'url': obj["url"], "state": state, 'imgURL': imgURL, 'ingr': oIngr, 'ingrU': Uvals, 'ingrP': Pvals, 'prep': oPrep, 'edit': editData } },  upsert=True )
                    
                    newDoc = loads(getRecette({'data':[ obj["ID"] ]}, self))['rec'][0]
                    obj={'time': oldDoc['dateM'], 'userID': oldDoc['userID']}

                    for key in newDoc:
                        if key != "_id" and key != "hist" and key != "dateM" and key != "userID" and key != "nomU" and key != "nomP" and key != 'ingrP' and key != 'ingrU':
                            if newDoc[key] != oldDoc[key]:
                                #print(key + " = " + str(newDoc[key]))
                                obj[key] = oldDoc[key]

                    if usepdb > 0:
                        pdb.set_trace()

                    if oldDoc['state'] == 1 and len(obj) > 2 and ((actTime - oldDoc['dateM'] > 86400000 or oldDoc['userID'] != Cuser)): # If modified add history
                        doc = coll.update_one( { '_id': oID}, {'$push': {'hist': obj  }},  upsert=True )
                    
                return dumps(doc.raw_result)
            else: 
                return ('{"n":0,"ok":0, "message": "S0062"}')    # Check Session error
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("saveRecet", ex)

def saveImg(param, self):
    try:
        if param:
 
            def readFile(fName):
                f = open(fName, "r")
                return f.read()
    
            #pdb.set_trace()
            upload_filename = ""
            pos = param.rfind('/')
            upload_filename=param[pos+1:]
            upload_file = os.path.normpath(os.path.join(IMG_DIR, upload_filename))
 
            dbx = dropbox.Dropbox(readFile(DATA_DIR + "info"))
     
            file_to = "/" + upload_filename
     
            while True:
                try:
                    with open(upload_file, 'rb') as f:
                        dbx.files_upload(f.read(), file_to)
                    break
                except Exception as ex:
                    if 'WriteConflictError' in str(ex):
                        x = str(ObjectId())
                        p = file_to.rfind(".")
                        file_to = file_to[0:p] + x[-2:] + file_to[p:]
                    else:
                        break
                        return except_handler("addFile Dropbox", ex)
            
            link = dbx.sharing_create_shared_link(file_to)
            dl_url = re.sub(r"\?dl\=0", "?raw=1", link.url)
            #os.remove(upload_file) 
            
            return dl_url
        else:
            return ""    # No param
    except Exception as ex:
        return except_handler("saveImg", ex)

def delRecet(param, self):
    try:
        if param.get("data"):
            recetID = ObjectId(param["data"][0])
            
            coll = dataBase.recettes

            doc = coll.delete_one({"_id": recetID })
            
            return dumps(doc.raw_result)
        else:
            return dumps({'ok': 0})    # No param
    except Exception as ex:
        return except_handler("delRecet", ex)

def getUserInfo(param, self):
    """ Get user account info by administrator"""
    try:
        if localHost or checkSession(self, role = ['ADM']):
            coll = dataBase.users
            if param.get("id"):
                o_id = getID(param["id"][0])
                doc = coll.find({"_id": o_id}, ["_id", "Nom", "courriel", "niveau", "actif", "note", "imgUser" ])
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
        return except_handler("getUserInfo", ex)
        
def updateUser_to_delete(param, self):
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
  
def delUser(param, self):
    try:
        if param.get("id"):
            #pdb.set_trace()
            userID = getID(param["id"][0])
            coll = dataBase.users

            docs = coll.delete_one({"_id": userID })
            r = docs.raw_result        

            return dumps(r)
        else:
            return dumps({'ok': 0})    # No param        
    except Exception as ex:
        return except_handler("getFav", ex)

  
def listNews(param, self):
    """ Return news list """
    coll = dataBase.news
    #pdb.set_trace()
    if param and param.get("data"):
        actif = int(param['data'][0])
        docs = coll.find({"active": actif}).sort("dateC", -1)
    else:
        docs = coll.find({},["title","date","dateC"]).sort("dateC", -1)
    return dumps(docs)

def getNews(param, self):
    """ Return news data for ID provided """
    #pdb.set_trace()
    if param:
        if param.get("id"):
            coll = dataBase.news
            o_id = ObjectId(param['id'][0])
            doc = coll.find({'_id': o_id})
            return dumps(doc[0])
        else:
            return dumps({'resp': {"result": 0} })    # No ID
    else:
        return dumps({'resp': {"result": 0} })    # No param

def writeNews(param, self):
    """ To add news to BD """
    if param:
        #print("Params= " + str(param))
        coll = dataBase.news
        if param.get("id") is None:
            docr = coll.insert_one({"title": param['title'][0] , "active": int(param['active'][0]), "date": param['date'][0] , "dateC": int(time.time() * 1000), "dateM": int(time.time() * 1000), "contentL": param['contentL'][0], "contentR": param['contentR'][0]}, {"new":True})
            o_id = str(ObjectId(docr))
            return dumps({"ok": 1, "id": o_id})
        else:
            o_id = ObjectId(param['id'][0])
            docr = coll.update_one({ '_id': o_id}, { '$set': {"title": param['title'][0] , "active": int(param['active'][0]), "date": param['date'][0], "dateM": int(time.time() * 1000) , "contentL": param['contentL'][0], "contentR": param['contentR'][0]}},  upsert=True )
            
            #doc=coll.update_one({"title": "tit3"}, {"$set": {"title": "tit4"}}, upsert=True)

            return dumps(docr.raw_result)
        #id_elem + "&title=" + f_title + "&active=" + ((f_active) ? "1":"0" ) + "&date=" + f_img_name + + "&content=" + htmlContent
        
    else:
        return dumps({'resp': {"result": 0} })    # No param


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

def sendChatCode(eMail, code):
    """ Send code to confirm email"""
    text = ''
    html = """\
    <html><body><div style="text-align: center;"><div style="background-color: #3A9D23;height: 34px;"><div style="margin: 3px;float:left;"><img alt="Image recettes" width="25" height="25" src="https://loupop.ddns.net/misc/favicon.gif" /></div><div style="font-size: 22px;font-weight: bold;color: #ccf;padding-top: 5px;">Recettes</div></div></br><p style="width: 100; text-align: left;">Bonjour,</p><p></p><p style="width: 100; text-align: left;">Voici votre code de confirmation : %s </p><p></p><p><div id="copyright">Copyright &copy; 2023</div></p></div></body></html>
    """  % (code)
    fromuser = "Recettes"
    subject = "Code de confirmation pour utiliser le chat " 
    log_Info("Confirmer chat courriel : " + eMail)
    send_email(fromuser, eMail, subject, text, html)

def sendRecet(eMail, nomRecet, htm):
    """ Envoie une recette par courriel """
    text = ''

    fromuser = "Recettes"
    subject = "Recettes - " + nomRecet 
    log_Info("Recette envoyé par courriel " + nomRecet + " : " + eMail)
    send_email(fromuser, eMail, subject, htm, htm)

def sendRecupPassMail(eMail, name, passw):
    """ Send email to retreive password"""
    text = ''
    name = name if name != '' else eMail
    html = """\
    <html><body><div style="text-align: center;"><div style="background-color: #3A9D23;height: 34px;"><div style="margin: 3px;float:left;"><img alt="Image recettes" width="25" height="25" src="https://loupop.ddns.net/misc/favicon.gif" /></div><div style="font-size: 22px;font-weight: bold;color: #ccf;padding-top: 5px;">Recettes</div></div></br><p style="width: 100; text-align: left;">Bonjour %s,</p><p></p><p style="width: 100; text-align: left;">Votre mot de passe est : %s </p><p></p><p><div id="copyright">Copyright &copy; 2023</div></p></div></body></html>
    """  % (name, passw)
    fromuser = "Recettes"
    subject = "Recettes - Récupérer mot de passe de " + name 
    log_Info("Récupérer mot de passe de " + name + " : " + eMail)
    send_email(fromuser, eMail, subject, text, html)

def sendConfMail(HOSTclient, email, name):

    recipient = email
    subject = "Recettes - Confirmer l'inscription de cdore00@yahoo.com"
    
    fromuser = "Recettes"

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi %s!\nCliquer ce lien pour confirmer l\'inscription de votre compte:\n%s\n\nGolf du Québec" % (name, HOSTclient)
    html = """\
    <html><body><div style="text-align: center;"><div style="background-color: #3A9D23;height: 40px;"><div style="margin: 3px;float:left;"><img alt="Image Golf du Québec" width="25" height="25" src="https://loupop.ddns.net/misc/favicon.gif" /></div><div style="font-size: 22px;font-weight: bold;color: #ccf;padding-top: 5px;">Recettes</div></div></br><a href="%s" style="font-size: 20px;font-weight: bold;">Cliquer ce lien pour confirmer l\'inscription de votre compte:<p>%s</p> </a></br></br></br><p><div id="copyright">Copyright &copy; 2023</div></p></div></body></html>
    """ % (HOSTclient, email)
    send_email(fromuser, recipient, subject, text, html)

def send_email(fromuser, recipient, subject, text, html):
    """ Send email"""
    # Create message container - the correct MIME type is multipart/alternative.
    #pdb.set_trace()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromuser + " <" + fromuser + ">"   #fromuser
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
