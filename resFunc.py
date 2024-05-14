import pdb
import sys, os, io, time, re, cgi, csv
import smtplib
import phonetics
import time, pytz
import datetime as datetimeLib
from socket import gethostname, gethostbyname
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from dateutil import tz
from zoneinfo import ZoneInfo
MAIL_USER = 'cdore07@gmail.com'

from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads
import json

import cherrypy
from cherrypy.lib import static

#https://stackoverflow.com/questions/11823296/mongodb-find-subdocument-in-array-matching-parameters
#https://stackoverflow.com/questions/1134290/cookies-on-localhost-with-explicit-domain
#datetime.now(tz=pytz.timezone('America/New_York'))


"""
utc=datetime.now(tz=pytz.timezone('UTC'))
utc
to_zone = tz.gettz('America/New_York')
central = utc.astimezone(to_zone)
central
"""


def localTime(dtTime, zone = None):
    #pdb.set_trace()
    dt = dtTime
    isUTC = str(datetime.utcnow().astimezone().tzinfo) == 'UTC'
    #print('UCT' + str(isUTC))
    #print('TIMEZONE' + str(datetime.utcnow().astimezone().tzinfo))
    if isUTC:
        local_tz = ZoneInfo("America/New_York")
        utc_tz = ZoneInfo("UTC")
        dt = dtTime.replace(tzinfo=local_tz)    # Force UTC to local timezone
        #print(dt.strftime("%Y-%m-%d %H:%M:%S"))

    return dt

    
    
def millis():
   """ returns the elapsed milliseconds (1970/1/1) since now """
   dt = datetime.now() - datetime(1970, 1, 1)
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms
#time.time()
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
    pdb.set_trace()
    
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

def subStartCal(param, self):

    if not param.get("ci" or param["ci"][0] == 'null'):
        return dumps({'error': 101, 'mess': "Club ID required."})    # No clubID
    if not param.get("dt"):
        return dumps({'error': 102, 'mess': "Start date required."})    # No date
    if not param.get("fr"):
        return dumps({'error': 104, 'mess': "Frequency is required."})    # No param frequency
    else:
        freq = param["fr"][0]
        if not freq.isnumeric():
            return dumps({'error': 106, 'mess': "Frequency in number of second is required."})    # No param frequency
    
    #pdb.set_trace()
    ci = int(param["ci"][0])
    dt = param["dt"][0]
    
    start = param["dt"][0] + " " + param["ft"][0]
    end = param["dt"][0] + " " + param["tt"][0]
    freq = int(freq)
    delta = datetimeLib.timedelta(seconds=freq)
    #pdb.set_trace()
    
    start = datetimeLib.datetime.strptime( start, '%Y-%m-%d %H:%M' )
    end = datetimeLib.datetime.strptime( end, '%Y-%m-%d %H:%M' )
    
    start=localTime(start, 'NY')
    end=localTime(end, 'NY')
    
    
    timeStart = datetime.timestamp(start)
    timeEnd = datetime.timestamp(end)
    coll = dataBase.departs
    res = coll.find( { 'club_id': ci, 'startTime': { '$gte': timeStart, '$lt': timeEnd } })
    docs=list(res)
    #pdb.set_trace()
    if len(docs):
        tm = docs[0]['startTime']
        tm = localTime(datetime.fromtimestamp(tm, tz=None))
        mess = "Tee Times exists on " + datetimeLib.datetime.strftime( tm, '%Y-%m-%d ') + "from" + datetimeLib.datetime.strftime( tm, ' %H:%M ') + "to"
        tm = docs[len(docs) - 1]['startTime']
        tm = localTime(datetime.fromtimestamp(tm, tz=None))
        mess += datetimeLib.datetime.strftime( tm, ' %H:%M') + "."
        return dumps({'error': 120, 'mess': mess}) 
    
    t = start
    coll = []
    lTime = time.time()
    while t <= end :
         ts = datetime.timestamp(t)
         coll.append({"club_id": ci,"startTime": ts, "lockTime": lTime, "available": True, "players": 0})
         t += delta
    
    return dumps({'error': 0, 'data': coll})    # Succes


def findStart(club_id, timeStart, timeEnd, actTime, npl):
    coll = dataBase.departs
    doc = coll.find( { 'club_id': club_id, 'players': { '$lte': (4 - npl)}, 'available': True, 'lockTime': {'$lt': actTime } , 'startTime': { '$gte': timeStart, '$lt': timeEnd } }).sort("startTime", 1)
    return doc

def getStart(param, self):

    if not param.get("ci")  or param["ci"][0] == 'null':
        return dumps({'error': 101, 'mess': "Club ID required."})    # No clubID
    if not param.get("dt"):
        return dumps({'error': 107, 'mess': "Tee time date required."})    # No date    

    #checkSession(self);
    
    club_id = getID(param["ci"][0])
    dt = param["dt"][0]

    start = datetimeLib.datetime.strptime( dt, '%Y-%m-%d' )
    start=localTime(start)
    timeStart = datetime.timestamp(start)
    #pdb.set_trace()
    
    delta = datetimeLib.timedelta(days=1)
    end = start + delta
    timeEnd = datetime.timestamp(end)
    
    coll = dataBase.departs 
    ex = coll.find({ 'club_id': club_id, 'startTime': { '$gte': timeStart, '$lt': timeEnd } }).sort("startTime", -1)     #  + date
    docs = list(ex)

    coll = dataBase.club
    doc = coll.find({"_id": club_id }, ["_id","nom", "courses"])
    club = list(doc)
    
    return dumps({'error': 0, 'club': club, 'data':docs})    # Succes    
    
def getStartCal(param, self):

    if not param.get("ci")  or param["ci"][0] == 'null':
        return dumps({'error': 101, 'mess': "Club ID required."})    # No clubID
    if not param.get("dt"):
        return dumps({'error': 102, 'mess': "Starting date required."})    # No date
    if not param.get("pl"):
        return dumps({'error': 105, 'mess': "Players is required."})    # No Players 
    if not param.get("ui"):
        return dumps({'error': 106, 'mess': "User is required."})    # No user     

    #checkSession(self);
    #pdb.set_trace()
    ci = getID(param["ci"][0])
    dt = param["dt"][0]
    user = getID(param["ui"][0])
    reserv = checkReservExist(ci, dt, user)    
    
    dt = dt + " " + param["ft"][0]
    start = datetimeLib.datetime.strptime( dt, '%Y-%m-%d %H:%M' )
    start=localTime(start)
    dt = datetime.timestamp(start)
    pl = int(param["pl"][0])
    timeStart = dt
    timeEnd = dt
    actTime = time.time()
    while start.day == datetime.fromtimestamp(timeStart, tz=None).day:
        #pdb.set_trace()
        timeStart -= 3600
        timeEnd += 3600
        res = findStart(ci, timeStart, timeEnd, actTime, pl)
        docs=list(res)
        if len(docs) > 0:
            break
    
    return dumps({'error': 0, 'resExist': reserv['date'], 'data':docs})    # Succes
    
def creStartCal(param, self):

    if not param.get("data"):
        return dumps({'error': 301, 'mess': "No data."})    # No param
    
    data = param["data"][0]
    data=loads(data)
    #pdb.set_trace()
    coll = dataBase.departs
    res = coll.insert_many(data)
    
    return dumps({'error': 0})    # Succes

def getPlayList(param):
    playList = []
    for x in range(4):
        if param.get("P" + str(x)):
            playList.append(param["P" + str(x)][0])
            print("P" + str(x))
    return playList
    
def reservStart(param, self):

    #pdb.set_trace()
    uid = (param["uid"][0])
    rid = (param["rid"][0])
    npl = (param["npl"][0])
    unm = (param["unm"][0])

    checkRes = checkStartAvailable( {'id': [rid], 'npl': [npl]}, self )
    
    playList = getPlayList(param)
    
    uid = getID(uid)
    rid = getID(rid)
    npl = int(npl)
    
    if not checkRes['error']:
        coll = dataBase.departs
        res = coll.update_one( { '_id': rid},{ "$set": {"lockTime": time.time()}, '$inc': { 'players': npl }, '$push': {'reserv':{ 'time': time.time(), 'user': uid, 'capName': unm, 'players': npl, "playList": playList }}})
        if res.raw_result['n'] == 1:
            return dumps({'error': 0, 'mess': ""})
        else:
            return dumps({'error': 100, 'mess': "Une erreur est survenue."})
    else:
        return dumps(checkRes)


def updateStart(param, self):

    #pdb.set_trace()
    uid = (param["uid"][0])
    rid = (param["rid"][0])
    npl = (param["npl"][0])
    apl = (param["apl"][0])
    itm = (param["itm"][0])

    npl = int(npl)
    apl = int(apl)
    itm = float(itm)
    
    checkRes = checkStartAvailable( {'id': [rid], 'npl': [apl - npl]}, self )
 
    uid = getID(uid)
    rid = getID(rid)
       
    playList = []
    for x in range(4):
        if param.get("P" + str(x)):
            playList.append(param["P" + str(x)][0])

    if not checkRes['error']:
        coll = dataBase.departs
        #delete start
        res = coll.update_one( { '_id': rid},{ '$inc': { 'players': (npl * -1) }, '$pull': {'reserv':{ 'user': uid}}})
        
        res = coll.update_one( { '_id': rid},{ "$set": {"lockTime": time.time()}, '$inc': { 'players': apl }, '$push': {'reserv':{ 'time': itm, 'timeM': time.time(), 'user': uid, 'players': apl, "playList": playList }}})
        if res.raw_result['n'] == 1:
            return dumps({'error': 0, 'mess': ""})
        else:
            return dumps({'error': 100, 'mess': "Une erreur est survenue."})
    else:
        return dumps(checkRes)


def checkReservExist(club_id, date, user):
    
    start = datetimeLib.datetime.strptime( date, '%Y-%m-%d')
    td = datetime.timestamp(start)
    delta = datetimeLib.timedelta(days=1)
    #pdb.set_trace()
    start += delta
    te = datetime.timestamp(start)
    dateRes = None
    coll = dataBase.departs 
    ex = coll.find({ 'club_id': club_id, 'startTime': { '$gte': td, '$lt': te }, 'reserv': { '$elemMatch' : { 'user': user }} })     #  + date
    resu = list(ex)
    if len(resu):
        dtRes = datetime.fromtimestamp(resu[0]['startTime'], tz=None)
        dateRes = datetimeLib.datetime.strftime( dtRes, '%Y-%m-%d %H:%M')
    #pdb.set_trace()
    return ({'date': dateRes,'resList': resu}) 


def checkStartAvailable(param, self):

    cid = None
    doc = None
    rid = getID(param["id"][0])
    if param.get("cid"):
        cid = getID(param["cid"][0])
    npl = int(param["npl"][0])
    
    coll = dataBase.departs 
    res = coll.update_one( { '_id': rid, 'players': { '$lte': (4 - npl)} }, { "$set": {"lockTime": (time.time() + 60)}})

    if cid is None:
        #pdb.set_trace()
        #ex = coll.find({ 'reserv': { '$elemMatch' : { 'user': 80 }} })     #  + date
        #resu = list(ex)
        if res.raw_result['n'] == 1:
            return {'error': 0, 'mess': ""}
        else:
            return {'error': 201, 'mess': "Ce départ n'est plus disponible."}
    else:
        if res.raw_result['n'] == 1:
            coll = dataBase.club
            doc = coll.find({"_id": cid }, ["_id","nom", "courses"])
            return dumps({'error': 0, 'club': doc[0]})
        else:
            return dumps({'error': 201, 'mess': "Ce départ n'est plus disponible."})
    #return dumps(res.raw_result)
    
    
def getUserStarts(param, self):
   
    if not param.get("ci") or param["ci"][0] == 'null':
        return dumps({'error': 105, 'mess': "Club ID required."})    # No clubID
    if not param.get("ui") :
        return dumps({'error': 106, 'mess': "User is required."})    # No user     

    
    #pdb.set_trace()
    club_id = getID(param["ci"][0])
    user = getID(param["ui"][0])
    
    coll = dataBase.departs 
    ex = coll.find({ 'club_id': club_id, 'reserv': { '$elemMatch' : { 'user': user }} }).sort("startTime", -1)     #  + date
    docs = list(ex)
    
    coll = dataBase.club
    doc = coll.find({"_id": club_id }, ["_id","nom", "courses"])
    club = list(doc)
    
    return dumps({'error': 0, 'club': club, 'data':docs})    # Succes

def deleteStart(param, self):

    #pdb.set_trace()
    uid = (param["uid"][0])
    rid = (param["rid"][0])
    npl = (param["npl"][0])
    
    uid = getID(uid)
    rid = getID(rid)
    npl = int(npl)
    
    coll = dataBase.departs
    res = coll.update_one( { '_id': rid},{ '$inc': { 'players': (npl * -1) }, '$pull': {'reserv':{ 'user': uid}}})

    return dumps({'ok': 0})


        
def saveResUser(param, self):
    """ To modify user account info"""
    try:
        #pdb.set_trace()
        name, tel, npassw, cpassw = '', '', '', ''
        if not param.get("ci")  or param["ci"][0] == 'null':
            return dumps({'error': 101, 'mess': "Club ID required."})    # No clubID        
        if param.get("ui") and param.get("pw") and param.get("id"):
            o_id = getID(param["id"][0])
            ci = getID(param["ci"][0])
            user = param["ui"][0]
            passw = param["pw"][0]
            if param.get("nm"):
                name = param["nm"][0]
            if param.get("te"):
                tel = param["te"][0]
            if param.get("np"):
                npassw = param["np"][0]
            if param.get("cp"):
                cpassw = param["cp"][0]
        else:
            return dumps({'error': 110, 'mess': "Utilisateur et mot de pass requis."})    # No email or password 
                 
        coll = dataBase.users
        
        def updUser(doc):
            #pdb.set_trace()
            if str(doc['motpass']) == passw:
                pw = passw
                if npassw:
                    if npassw == cpassw:
                        pw = npassw
                    else:
                        return dumps({"error": 116, "mess": "Confirmation du mot de passe différent du nouveau mot de passe."}) # Invalid password
                res = coll.update_one({"_id": o_id}, { "$set": {'Nom': name, 'courriel': user, 'motpass': pw, 'phone': tel } })
                print(res.raw_result)
                return dumps({"error":0, "email": user})
            else:
                return dumps({"error": 112, "messID": "S0059"}) # Invalid password
        
        
        
        doc = coll.find({"_id": o_id, "actif": True})
        userDoc = list(doc)
        #pdb.set_trace()
        docs = coll.find({"clubID": ci, "courriel": user, "_id": {"$ne": o_id}})
        if len(list(docs)):
            return dumps({"error": 111, "messID": "S0056"}) # The new email allredy exist        
        
        if len(userDoc):
            dic = cursorTOdict(userDoc)
            return updUser(dic);
    
        return dumps({ })    # modified

    except Exception as ex:
        return except_handler("saveUser", ex)    
    

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
