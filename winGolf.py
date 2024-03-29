# coding=utf-8

import pdb
#; pdb.set_trace()
import sys, os, io, re, cgi, csv, urllib.parse
import json
import time 
import datetime

from tkinter import *
import tkinter as tk

from tkinter import messagebox, TclError, ttk
from tkinter.messagebox import askyesno

from tkcalendar import Calendar
from tkinter import font as tkFont  
from idlelib.tooltip import Hovertip

import cdControl as cdc

# JSON
from bson import ObjectId
import json

# MongoDB
import pymongo
from pymongo import MongoClient


blocksCol = {"BOr": ["black", "gold"],
            "BArgent": ["white", "silver"],
            "BBronze": ["white", "#A67D3D"],
            "BCuivre": ["white", " #b87333"],
            "BBleu": ["white", "blue"],
            "BRouge": ["white", "red"],
            "BNoir": ["white", "black"],
            "BBlanc": ["black", "white"],
            "BVert": ["white", "forestgreen"],
            "BJaune": ["black", "yellow"],
            "BOrange": ["black", "orange"],
            "BRose": ["black", "pink"],
            "BNormale": ["black", "#eee"],
            "BHdcp": ["black", "#eee"]}

def getBlocsArr(blocColl):
    blocsArray = []
    #pdb.set_trace()
    for x in blocColl:
        if x["Bloc"] != "Normale" and x["Bloc"] != "Hdcp":
            blocsArray.append(x["Bloc"])
    return blocsArray

def calculTot(Tval, is18):
    totO, totI = 0, 0
    for tr in range(0,9):
        v = Tval[tr].get()
        if v:
            totO += int(v)       
    if is18:
        for tr in range(9,18):
            v = Tval[tr].get()
            if v:
                totI += int(v)
    return totO, totI

def getGameScore(TG, PG, LG, dat, is18):
    def isValid(v):
        if not v.isnumeric():
            return False
        else:
            return True
                
    for tr in range(0,9):
        v = TG[tr].get()
        if not isValid(v):
            return False
        dat["T" + str(tr+1)] = int(v)
        v = PG[tr].get()
        if not isValid(v):
            return False
        dat["P" + str(tr+1)] = int(v)
        v = LG[tr].get()
        if v == "":
            dat["L" + str(tr+1)] = 0
        else:
            if not isValid(v):
                return False
            dat["L" + str(tr+1)] = int(v)
    if is18:
        for tr in range(9,18):
            v = TG[tr].get()
            if not isValid(v):
                return False
            dat["T" + str(tr+1)] = int(v)
            v = PG[tr].get()
            if not isValid(v):
                return False
            dat["P" + str(tr+1)] = int(v)
            v = LG[tr].get()
            if v == "":
                dat["L" + str(tr+1)] = 0
            else:
                if not isValid(v):
                    return False
                dat["L" + str(tr+1)] = int(v)
    return True
                    
class listGames():
    def __init__(self, masterForm, *args, **kwargs):
        #pdb.set_trace()
        self.win = masterForm.win
        self.masterForm = masterForm
        #self.recData = recData
        self.data = masterForm.data.data
        self.editList = {}
        self.pop = None
        self.gridframe = None
        self.footFrame = None
        self.sortObj = None
        self.headLbl = ["Date ", "Club ", "Score "]
        self.comboClubVal = [0]
        self.skip = 0
        self.isDestroy = False
        self.showGames()
        
    def showGames(self):
    
        self.pop = tk.Toplevel(self.win)
        #self.pop.overrideredirect(True)
        #second_win.protocol('WM_DELETE_WINDOW',lambda: onclose(second_win))
        self.pop.protocol('WM_DELETE_WINDOW',self.destroyRef)

        self.pop.title("Parties")
        self.pop.iconbitmap(GOLFICON)   
        
        # Search form 
        self.formFrame = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE)
        self.formFrame.pack(fill=X)

        # Grid list frame
        self.scoreframe = cdc.VscrollFrame(self.pop)
        self.scoreframe.pack(expand= True, fill=BOTH)

        recframe = cdc.resizeFrame(self.formFrame, borderwidth = 1, relief=RIDGE, pack=False)
        recframe.pack(fill=X, padx=10, pady=10, anchor=W) 
        
        self.editFrame = recframe

        self.comboClub = ttk.Combobox( recframe, state="readonly", width=40)
        self.comboClub["values"] = ["Tous les clubs"]
        self.comboClub.current(0)
        self.comboClub.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5, pady=3) 
        self.comboClub.bind("<Button-1>", self.loadClubCombo)

        self.varDate = StringVar()
        self.varDate.set("")
        recDate = cdc.editEntry(recframe, textvariable=self.varDate, width=14, maxlen=10)
        recDate.focus()
        recDate.grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        
        calFrame = tk.Frame(recframe)
        cal = cdc.selectDate(self.pop, "Sélectionner une date de début", calFrame, 2, theDate=self.varDate)
        calFrame.grid(row=1, column=1, sticky=tk.W, padx=0, pady=3)

        self.comboTrou = ttk.Combobox( recframe, state="readonly", width=8)
        self.comboTrou["values"] = ["18 trous", "9 trous"]
        self.comboTrou.current(0)
        self.comboTrou.grid( row=1, column=2, sticky=tk.W, padx=10, pady=3)
        self.comboTrouVal = [18,9]
        self.comboTrou.bind("<<ComboboxSelected>>", self.resetComboClub)
        
        
        resetFrame = tk.Frame(recframe)
        resetFrame.grid(row=1, column=3)
        butReset = cdc.RoundedButton(resetFrame, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.resetList)
        butReset.create_text(12,11, text="🔄", fill="black", font=('Helvetica 17 '))
        butReset.grid(row=0, column=0, sticky=tk.W)
        Hovertip(butReset,"Réinitialiser la liste")
        butClear = cdc.RoundedButton(resetFrame, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.clearForm)
        butClear.create_text(12,11, text="x", fill="black", font=('Helvetica 15 '))
        butClear.grid(row=0, column=1, sticky=tk.E)
        Hovertip(butClear,"Blanchir le formulaire")        
       
        self.comboNbr = ttk.Combobox( recframe, state="readonly", width=11)
        self.comboNbr["values"] = ["5 parties", "10 parties", "20 parties H", "50 parties", "100 parties"]
        self.comboNbr.grid( row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.comboNbrVal = [5,10,20,50,100]
        self.comboNbr.current(2)

        self.varLimit = StringVar()
        recLimit = cdc.editEntry(recframe, textvariable=self.varLimit, width=3, maxlen=3)
        recLimit.grid( row=2, column=1, sticky=tk.W, padx=5, pady=3)

        butNext = ttk.Button(recframe, text="Suivant", command=self.nextGame, width=9 ) 
        butNext.grid(row=2, column=2, padx=5, sticky="WE") 
        
        butNext = ttk.Button(recframe, text="Fermer", command=self.destroyRef, width=9 ) 
        butNext.grid(row=2, column=3, padx=5, sticky="WE")
        self.nextGame()
        self.winDim()

    def listGamesScore(self, user, parc, skip, limit, is18, intDate):
        #pdb.set_trace()

        def calcScore(x):
            try:
                if 'T10' in x and not x["T10"] is None:
                    return (x["T1"] + x["T2"] + x["T3"] + x["T4"] + x["T5"] + x["T6"] + x["T7"] + x["T8"] + x["T9"] + x["T10"] + x["T11"] + x["T12"] + x["T13"] + x["T14"] + x["T15"] + x["T16"] + x["T17"] + x["T18"] )
                else:
                    return (x["T1"] + x["T2"] + x["T3"] + x["T4"] + x["T5"] + x["T6"] + x["T7"] + x["T8"] + x["T9"] )
            except Exception as ex:
                pdb.set_trace()
                return 0
            
            
        def calcStat(tot, r):
            cnt,h,m = 0,0,0
            tot.sort()
            handi = ""
            for i in tot:
                m += i
                if cnt < 10:
                    h += i
                cnt += 1
            cnt = 1 if cnt == 0 else cnt
            handi = ("Hand.: " + str(round(h/10,1)) if r==20 else "")
            return handi, ("Moy.: " + str(round(m/cnt,1)))
    
        
        # Grid score games
        #pdb.set_trace()
        if not self.gridframe is None:
            self.gridframe.destroy()
            self.gridframe = None
            self.footFrame.destroy()
        else:
            headFrame = tk.Frame(self.scoreframe.interior)
            headFrame.pack( fill=X, padx=10)
            headFrame.grid_columnconfigure(0, weight=1, uniform="True")
            headFrame.grid_columnconfigure(1, weight=2, uniform="True")
            headFrame.grid_columnconfigure(2, weight=1, uniform="True")            
            self.sortObj = cdc.sortGridObj(headFrame, headLabels = ["Date ", "Club ", "Score "], headConfig = [{"type": "C", "length": 8}, {"type": "C", "length": 15}, {"type": "N", "length": 7} ])


        dataList = self.getGameList(user, parc, skip, limit, is18, intDate)
        rowN = 0
        tot = []
        
        gridframe = tk.Frame(self.scoreframe.interior)
        gridframe.pack( fill=X, padx=10)
        self.gridframe = gridframe

        self.sortObj.setGridframe(gridframe)
        
        gridframe.grid_columnconfigure(0, weight=1, uniform="True")
        gridframe.grid_columnconfigure(1, weight=2, uniform="True")
        gridframe.grid_columnconfigure(2, weight=1, uniform="True")       
        for x in dataList:
            #print(x)
            lbl = tk.Label(gridframe, text= cdc.milliToDate(x["score_date"]), font= ('Segoe 9 underline'), fg="#0000FF", pady=1, width=8, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=0, sticky="WE")  
            lbl._values = x["_id"]
            lbl.bind("<Button-1>", self.showGame)
            lbl = tk.Label(gridframe, text= x["name"], pady=1, width=15, borderwidth = 1, relief=RIDGE, anchor=W)
            lbl.grid(row= rowN, column=1, sticky="WE")
            lbl._values = x["_id"]
            lbl.bind("<Double-Button-1>", self.showGame)
            if len(x["name"]) > 15:
                Hovertip(lbl,x["name"])
            s = int(calcScore(x))
            tot.append(s)
            lbl = tk.Label(gridframe, text= str(s), pady=1, width=7, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=2, sticky="WE")
            lbl._values = x["_id"]
            lbl.bind("<Double-Button-1>", self.showGame)
            rowN += 1        
            
        #print(str(rowN))
        if rowN < limit:
            self.skip = 0
            #print("reset rowN: " + str(rowN) + "  limit: " + str(limit))
        else:
            self.skip += limit
        
        footFrame = tk.Frame(self.scoreframe.interior)
        footFrame.pack( fill=X, padx=10)
        self.footFrame = footFrame

        footFrame.grid_columnconfigure(0, weight=1, uniform="True")
        footFrame.grid_columnconfigure(1, weight=2, uniform="True")
        footFrame.grid_columnconfigure(2, weight=1, uniform="True")        
        h,m = calcStat(tot, rowN)
        lbl = tk.Label(footFrame, text=h, font= ('Segoe 9 bold'), borderwidth = 1, relief=RIDGE )
        lbl.grid(row=0, column=0, sticky=tk.NSEW)
  
        lbl = tk.Label(footFrame, text= str(rowN) + " parties", borderwidth = 1, font= ('Segoe 9 bold'), relief=RIDGE )
        lbl.grid(row=0, column=1, sticky=tk.NSEW)            
 
        lbl = tk.Label(footFrame, text=m, borderwidth = 1, font= ('Segoe 9 bold'), relief=RIDGE )
        lbl.grid(row=0, column=2, sticky=tk.NSEW)        

        
    def nextGame(self, noskip = False):
        intDat = 0
        parcours = self.comboClubVal[self.comboClub.current()]
        trou = self.comboTrouVal[self.comboTrou.current()]
        nbr = self.comboNbrVal[self.comboNbr.current()]
        dat = self.varDate.get()
        if self.varLimit.get().isnumeric():
            nbr = nbr if self.varLimit.get() == '' else int(self.varLimit.get())
        
        if dat != '':
            dt = datetime.datetime.strptime(dat, "%Y-%m-%d")
            intDat = dt.timestamp() * 1000
        if noskip:
            self.skip -= nbr
        if self.skip < 0:
            self.skip = 0
            
        self.listGamesScore( user=USER_ID, parc=parcours, skip=self.skip, limit=nbr, is18=trou, intDate=intDat)
        
    
    def clearForm(self):
        self.varDate.set("")
        self.comboClub.current(0)
        self.comboNbr.current(2)
        self.comboTrou.current(0)
        self.varLimit.set("")

    def resetList(self):
        self.skip = 0
        self.nextGame()
        
    def resetComboClub(self, e):
        #print("resetComboClub")
        self.comboClub["values"] = ["Tous les clubs"]
        self.comboClub.current(0)
        self.comboClub.bind("<Button-1>", self.loadClubCombo)
    
    
    def loadClubCombo(self, event=None):
        
        is18 = self.comboTrou.current() == 0
        dataList = self.countUserGame(USER_ID, is18=is18)
        #pdb.set_trace()
        self.comboClubVal, clubList = [], []
        self.comboClubVal.append(0)
        clubList.append("Tous les clubs")
        
        for x in dataList:
            self.comboClubVal.append(x["_id"]["parcours"])
            clubList.append(x["_id"]["name"] + " (" + str(x["count"]) + ")")
        
        self.comboClub["values"] = clubList
       
    
    def getGameList(self, user, parc=0, skip=0, limit=20, is18=18, intDate=0):
        #pdb.set_trace()
        if intDate == 0:   # ou 0 ???
            intDate = 9999999999999

        coll = self.data.score
        
        if is18 == 18:
            qO = {"USER_ID": user, "score_date": {"$lt":intDate}, "T18": { "$exists": True, "$nin": [ 0 ] } }
        else:
            qO = {"USER_ID": user, "score_date": {"$lt":intDate}, "$or":[{"T18":0},{"T18":None}]  }  
        if parc != 0:
            qO["PARCOURS_ID"] = parc             
            
        docs = coll.find(qO).sort("score_date",-1).skip(skip).limit(limit)

        return list(docs)
        
    def countUserGame(self, user, is18=True):
        """
        param = param["data"][0]
        para = [x for x in param.split("$")]
        user = getID(para[0])
        is18 = int(para[1])
        #pdb.set_trace()
        withGroup = True if len(para) > 2 else False
        """
        #pdb.set_trace()
        withGroup = True 
        coll = self.data.score
        if is18:
            count = coll.count_documents({"USER_ID": user, "T18": { "$exists": True, "$nin": [ 0 ] }})
            if withGroup == True:
                group = coll.aggregate([ {"$match" : {"USER_ID": user, "T18": { "$exists": True, "$nin": [ 0 ] }}}, {"$group" : {"_id":{"name":"$name","parcours":"$PARCOURS_ID"}, "count":{"$sum":1}}}, { "$sort" : {"_id" : 1 } } ])
        else:
            count = coll.count_documents({"USER_ID": user, "$or":[{"T18":0},{"T18":None}]  } )
            if withGroup == True:
                group = coll.aggregate([ {"$match" : {"USER_ID": user, "$or":[{"T18":0},{"T18":None}]  }}, {"$group" : {"_id":{"name":"$name","parcours":"$PARCOURS_ID"}, "count":{"$sum":1}}}, { "$sort" : {"_id" : 1 } } ])
        
        return list(group)


    def getGame(self, gameID):
            
        def getClubID(parcID):
            coll = self.data.parcours
            blocs = coll.find({"_id": parcID })
            return blocs[0]["CLUB_ID"]
        
        def getBloc(doc):
            coll = self.data.blocs
            blocs = coll.find({"PARCOURS_ID": doc['PARCOURS_ID'] })
            for x in blocs:
                if x['Bloc'] == "Normale":
                    doc['par'] = x
            doc["clubID"] = getClubID(doc['PARCOURS_ID'])
            return doc
        
        
        if gameID.isnumeric():
            gID = int(gameID)
        else:
            gID = ObjectId(gameID)
        coll = self.data.score
        doc = coll.find({"_id":gID})
        game = list(doc)
        #pdb.set_trace()
        if len(game):
            doc = game[0]
            if doc['score_date'] != None:
                doc['score_date'] = cdc.milliToDate(doc["score_date"])    
            return(getBloc(doc))


    def winDim(self, adjustPosition = False):
        self.win.update_idletasks()                                                             ##update_idletasks
        w=self.pop.winfo_width()
        h=self.scoreframe.interior.winfo_height() + self.formFrame.winfo_height() + 5
        
        #pdb.set_trace()
        self.pop.geometry(f"{w}x{h}") 
        my = self.masterForm.win.winfo_x() - w - 5
        my = 0 if my < 0 else my
        mt = self.masterForm.win.winfo_y()
        self.pop.geometry(f"+{my}+{mt}")        
        #self.pop.geometry(f"+{my}+0")
        self.win.update_idletasks()
        self.pop.attributes('-topmost', True)
        self.pop.attributes('-topmost', False)
        
        
    def destroyRef(self, e=None):
        #print("isDestroy")
        self.isDestroy = True
        self.pop.destroy()

    
    def fun(self, event):
        print(event.keysym, event.keysym=='a')
        print(event)        
        
             
    def showGame(self, event):
        id = event.widget._values
        winGame = winShowGame(self, id)
        
        
class winShowGame():
    def __init__(self, winListGames, id):
        
        self.winListGames = winListGames
        self.blocColl = None
        Gdata = winListGames.getGame(str(id))
        #print(Gdata)
        self.gameID = Gdata["_id"]
        self.Gdata = Gdata
        is18 = "T18" in Gdata and type(Gdata["T18"]) == int
        self.is18 = is18

        self.pop = tk.Toplevel(winListGames.pop)
        self.pop.iconbitmap(GOLFICON)
        self.objMess = cdc.messageObj(self.pop, height=25)

        titleFrame = tk.Frame(self.pop)
        titleFrame.pack()
        lbl = tk.Label(titleFrame, text= Gdata['score_date'] + " : ")
        lbl.grid(row=0, column=0, sticky="WE")  
        lbl = tk.Label(titleFrame, text= Gdata['name'], font= ('Segoe 9 underline'), fg="#0000FF" )
        lbl._values = [Gdata["clubID"]]
        lbl.bind("<Button-1>", cdc.webCallClub)
        lbl.grid(row=0, column=1, sticky="WE")
        
        recframe = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE, padx=10, pady=5)
        recframe.pack(expand= True, fill=BOTH)
        self.recframe = recframe
        self.recframe.win = self.pop
        
        # Trou
        lbl = tk.Label(recframe, text= 'Trou', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=0, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= str(tr), borderwidth = 1, relief=RIDGE, width = 3 )
            lbl.grid(row=0, column=tr, sticky="WE")
        if not is18:
            lbl = tk.Label(recframe, text= "Total", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= "OUT", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= str(tr-2), borderwidth = 1, width = 3, relief=RIDGE )
                lbl.grid(row=0, column=tr-1, sticky="WE")        
            lbl = tk.Label(recframe, text= "IN", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=20, sticky="WE")  
            lbl = tk.Label(recframe, text= "Total", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=21, sticky="WE")
        
        #pdb.set_trace()
        # Par
        r = 1
        pOUT, pIN = 0, 0
        Pdat = Gdata['par']
        lbl = tk.Label(recframe, text= 'Par', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= Pdat["T" +str(tr)], borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=tr, sticky="WE")
            pOUT += int(Pdat["T" +str(tr)])
        if not is18:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= Pdat["T" +str(tr-2)], borderwidth = 1, relief=RIDGE )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += int(Pdat["T" +str(tr-2)])
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
            lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")

        # Score
        r = 2
        pOUT, pIN = 0, 0
        if not 'bloc' in Gdata:
            bn, bg, fg = "Trou#", "#eee", "#eee"
        else:
            bn, bg, fg = Gdata['bloc'][1:], blocksCol[Gdata['bloc']][1], blocksCol[Gdata['bloc']][0]
        lbl = tk.Label(recframe, text= bn, bg= bg, fg= fg , borderwidth = 1, relief=RIDGE )
        
        
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= Gdata["T" +str(tr)], borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=tr, sticky="WE")
            pOUT += int(Gdata["T" +str(tr)])
        if not is18:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= Gdata["T" +str(tr-2)], borderwidth = 1, relief=RIDGE )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += int(Gdata["T" +str(tr-2)])
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
            lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")  

         # Diff
        r = 3
        pOUT, pIN = 0, 0
        lbl = tk.Label(recframe, text= 'Diff.', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):
            diff = int(Gdata["T" +str(tr)]) - int(Pdat["T" +str(tr)])
            #print(self.getDiffColor(diff))
            Bcolor = self.getDiffColor(diff)
            lbl = tk.Label(recframe, text= str(diff), borderwidth = 1, relief=RIDGE, bg= Bcolor )
            lbl.grid(row=r, column=tr, sticky="WE")
            pOUT += diff
        if not is18:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")        
            for tr in range(12,21):
                diff = int(Gdata["T" +str(tr-2)]) - int(Pdat["T" +str(tr-2)])
                Bcolor = self.getDiffColor(diff)
                lbl = tk.Label(recframe, text= str(diff), borderwidth = 1, relief=RIDGE, bg= Bcolor )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += diff
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
            lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")
        
        # Puts
        r = 4
        pOUT, pIN = 0, 0
        lbl = tk.Label(recframe, text= 'Putts', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= Gdata["P" +str(tr)], borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=tr, sticky="WE")
            pOUT += int(Gdata["P" +str(tr)])
        if not is18:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= Gdata["P" +str(tr-2)], borderwidth = 1, relief=RIDGE )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += int(Gdata["P" +str(tr-2)])
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
            lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")  

        # Pénalité
        r = 5
        pOUT, pIN = 0, 0
        lbl = tk.Label(recframe, text= 'Pénalité', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= ("" if self.Gdata["L" +str(tr)] == 0 else self.Gdata["L" +str(tr)]), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=tr, sticky="WE")
            pOUT += int(Gdata["L" +str(tr)])
        if not is18:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= ("" if self.Gdata["L" +str(tr-2)] == 0 else self.Gdata["L" +str(tr-2)]), borderwidth = 1, relief=RIDGE )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += int(Gdata["L" +str(tr-2)])
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
            lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")
            
        r = 6
        lbl = tk.Label(recframe, text= "Carte", font= ('Segoe 9 underline'), fg="#0000FF")
        lbl._values = [Gdata["PARCOURS_ID"], Gdata['bloc']]
        lbl.bind("<Button-1>", self.showCard)
        lbl.grid(row=r, column=0, columnspan=22, sticky="WE")

        butFrame = tk.Frame(self.pop, pady=5)
        butFrame.pack(expand= True, side=LEFT, fill=X, anchor=CENTER)
        self.butEdit = tk.Frame(butFrame)
        self.butEdit.pack()
        butClose = ttk.Button(self.butEdit, text="Fermer", command=self.close, width=15) 
        butClose.grid(row=0, column=0, sticky="WE", padx=5)

        if self.winListGames.masterForm.userRole == "ADM" or self.winListGames.masterForm.userRole == "MEA"  or self.winListGames.masterForm.userRole == "MEM":        
            butEdit = ttk.Button(self.butEdit, text="Éditer", command=self.editGame, width=15) 
            butEdit.grid(row=0, column=1, sticky="WE", padx=5)

            
    def delGame(self):
        answer = askyesno(title='Suppression',
            message='Supprimer la partie')
        if answer:
            #print("Delete: " + str(self.gameID))
            coll = self.winListGames.data.score
            docr = coll.delete_one({"_id": self.gameID})
            self.winListGames.nextGame(noskip=True)
            self.close()
            
        
    def editGame(self):
        #print("Éditer")
        
        TG, PG, LG = [], [], []
        self.TG, self.PG, self.LG = TG, PG, LG
        butClose = ttk.Button(self.butEdit, text="Annuler", command=self.close, width=15) 
        butClose.grid(row=0, column=0, sticky="WE", padx=5)        
        butEdit = ttk.Button(self.butEdit, text="Enregistrer", command=self.savegame, width=15) 
        butEdit.grid(row=0, column=1, sticky="WE")       
        butDel = ttk.Button(self.butEdit, text="Supprimer", command=self.delGame, width=15) 
        butDel.grid(row=0, column=2, sticky="WE", padx=5)
        r = 2

        blocColl = self.getParcBlocs(self.Gdata['PARCOURS_ID'])
        self.blocCollVal = getBlocsArr(blocColl)
        
        self.comboBloc = ttk.Combobox( self.recframe, state="readonly", width=5)
        self.comboBloc["values"] = self.blocCollVal
        self.comboBloc.current(self.blocCollVal.index(self.Gdata['bloc'][1:]))
        self.comboBloc.grid(row=r, column=0, sticky=tk.W)         
        
        for tr in range(1,10):        
            TG.append(self.Gdata["T" +str(tr)])
            TG[tr - 1] = tk.StringVar()
            TG[tr - 1].set(self.Gdata["T" +str(tr)])
            fld = cdc.editEntry(self.recframe, width=2, textvariable= (TG[tr - 1]), isNum=True, maxlen=2)        
            fld.grid(row=r, column=tr, sticky="WE")
            fld.bind("<KeyRelease>", lambda event, Tval=TG , row=r: self.calcTot(event, Tval, row))
        if self.is18:
            for tr in range(10,19):        
                TG.append(self.Gdata["T" +str(tr)])
                TG[tr - 1] = tk.StringVar()
                TG[tr - 1].set(self.Gdata["T" +str(tr)])
                fld = cdc.editEntry(self.recframe, width=2, textvariable= (TG[tr - 1]), isNum=True, maxlen=2)        
                fld.grid(row=r, column=tr+1, sticky="WE")
                fld.bind("<KeyRelease>", lambda event, Tval=TG , row=r: self.calcTot(event, Tval, row))
            lbl = tk.Label(self.recframe, text= " ", borderwidth = 1, relief=RIDGE )
            
            lbl.grid(row=r+1, column=0, columnspan=22, sticky="WE") 

        r = 4
        for tr in range(1,10):        
            PG.append(self.Gdata["P" +str(tr)])
            PG[tr - 1] = tk.StringVar()
            PG[tr - 1].set(self.Gdata["P" +str(tr)])
            fld = cdc.editEntry(self.recframe, width=2, textvariable= (PG[tr - 1]), isNum=True, maxlen=2)        
            fld.grid(row=r, column=tr, sticky="WE")
            fld.bind("<KeyRelease>", lambda event, Tval=PG , row=r: self.calcTot(event, Tval, row))
        if self.is18:
            for tr in range(10,19):        
                PG.append(self.Gdata["P" +str(tr)])
                PG[tr - 1] = tk.StringVar()
                PG[tr - 1].set(self.Gdata["P" +str(tr)])
                fld = cdc.editEntry(self.recframe, width=2, textvariable= (PG[tr - 1]), isNum=True, maxlen=2)        
                fld.grid(row=r, column=tr+1, sticky="WE")
                fld.bind("<KeyRelease>", lambda event, Tval=PG , row=r: self.calcTot(event, Tval, row))
            lbl = tk.Label(self.recframe, text= " ", borderwidth = 1, relief=RIDGE )        
        
        r = 5
        for tr in range(1,10):        
            LG.append(self.Gdata["L" +str(tr)])
            LG[tr - 1] = tk.StringVar()
            LG[tr - 1].set(("" if self.Gdata["L" +str(tr)] == 0 else self.Gdata["L" +str(tr)]))
            fld = cdc.editEntry(self.recframe, width=2, textvariable= (LG[tr - 1]), isNum=True, maxlen=2)        
            fld.grid(row=r, column=tr, sticky="WE")
            fld.bind("<KeyRelease>", lambda event, Tval=LG , row=r: self.calcTot(event, Tval, row))
        if self.is18:
            for tr in range(10,19):        
                LG.append(self.Gdata["L" +str(tr)])
                LG[tr - 1] = tk.StringVar()
                LG[tr - 1].set(("" if self.Gdata["L" +str(tr)] == 0 else self.Gdata["L" +str(tr)]))
                fld = cdc.editEntry(self.recframe, width=2, textvariable= (LG[tr - 1]), isNum=True, maxlen=2)        
                fld.grid(row=r, column=tr+1, sticky="WE")
                fld.bind("<KeyRelease>", lambda event, Tval=LG , row=r: self.calcTot(event, Tval, row))
            lbl = tk.Label(self.recframe, text= " ", borderwidth = 1, relief=RIDGE )   


    def savegame(self):
               
        dat = {}
        dat["bloc"] = "B" + self.comboBloc.get()
        #pdb.set_trace()
        if not getGameScore(self.TG, self.PG, self.LG, dat, self.is18):
            self.objMess.showMess("Une valeur numérique est requise.")
        else:
            coll = self.winListGames.data.score
            docr = coll.update_one({"_id": self.gameID}, { "$set": dat })
            self.objMess.showMess("Enregistré!", type = "I")
        #print(dat)
        
    def calcTot(self, event, Tval, r):
        self.objMess.clearMess()
        totO, totI = calculTot(Tval, self.is18)

        lbl = tk.Label(self.recframe, text= str(totO), borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=10, sticky="WE")   
        
        if self.is18:
            lbl = tk.Label(self.recframe, text= str(totI), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")   
            lbl = tk.Label(self.recframe, text= str(totO + totI), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")            

        
    def getDiffColor(self, diff):
        color = "#AAAAAA"
        
        if diff > 2: 
            color = "#C29933"
        if diff == 2: 
            color = "#FF5D00"             
        if diff == 1:
            color = "#FFBA32"
        if diff == -1:
            color = "#91D0F7"
        if diff < -2:
            color = "#00B3E7"            
        return color

    def close(self):
        self.pop.destroy()

    def getParcBlocs(self, parcID):
        if self.blocColl is None:
            coll = self.winListGames.data.blocs
            Bdoc = coll.find({"PARCOURS_ID": parcID })
            self.blocColl = list(Bdoc) 
        return self.blocColl     
        
    def showCard(self, event):
        #pdb.set_trace()
        pid, bloc = event.widget._values[0], event.widget._values[1][1:]

        blocColl = self.getParcBlocs(pid)
        
        r = 6
        for x in blocColl:
            #x['Blocs'] = self.getBloc(x["_id"]) 
            if x['Bloc'] != 'Normale':
                bn, bg, fg = x['Bloc'][1:], blocksCol["B" + x['Bloc']][1], blocksCol["B" + x['Bloc']][0]
                #print(x)
                lbl = tk.Label(self.recframe, text= x["Bloc"], bg= bg, fg= fg , borderwidth = 1, relief=RIDGE )            
                lbl.grid(row=r, column=0, sticky="WE")            
                for tr in range(1,10):
                    lbl = tk.Label(self.recframe, text= x["T" +str(tr)], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=tr, sticky="WE")
                if not self.is18:
                    lbl = tk.Label(self.recframe, text= x["Aller"], bg= bg, fg= fg, font= ('Segoe 9 bold'), borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=10, sticky="WE")                 
                else:
                    lbl = tk.Label(self.recframe, text= x["Aller"], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=10, sticky="WE")        
                    for tr in range(12,21):
                        lbl = tk.Label(self.recframe, text= x["T" +str(tr-2)], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                        lbl.grid(row=r, column=tr-1, sticky="WE")   
                    lbl = tk.Label(self.recframe, text= x["Retour"], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=20, sticky="WE")  
                    lbl = tk.Label(self.recframe, text= x["Total"], font= ('Segoe 9 bold'), bg= bg, fg= fg, borderwidth = 1, relief=RIDGE, width = 5 )
                    lbl.grid(row=r, column=21, sticky="WE")
                r += 1


class showClubWin():
    def __init__(self, masterForm, clubID):
        #pdb.set_trace()
        self.win = masterForm.win
        self.masterForm = masterForm
        
        self.data = masterForm.data.data
        #print(str(clubID))
        self.showClub(clubID)
        

    def getBloc(self, parcID):
        coll = self.data.blocs
        Bdoc = coll.find({"PARCOURS_ID": parcID })
        return list(Bdoc)

    def getClubParc(self, clubID):

        coll = self.data.club
        docs = coll.find({"_id": clubID })
        doc = list(docs)[0]
        for x in doc["courses"]:
            x['Blocs'] = self.getBloc(x["_id"])

        return doc
        
    def showClub(self, clubID):
    
        def on_enter(e):
            e.widget.config(foreground= "red")

        def on_leave(e):
            e.widget.config(foreground= 'blue')
    
        clubData = self.getClubParc(clubID)
        #print(clubData)
        self.pop = tk.Toplevel(self.win)
        self.pop.title(clubData["nom"])
        self.pop.iconbitmap(GOLFICON)
        self.masterForm.childWin.append(self.pop)
        
        # Club info
        self.infoFrame = tk.Frame(self.pop, padx=5)
        self.infoFrame.pack(fill=X)
        
        info1 = tk.Frame(self.infoFrame, padx=5)
        info1.pack(fill=X)
        lbl = tk.Label(info1, text= "Club: ", anchor=W)
        lbl.grid(row=0, column=0, sticky=tk.W)
        if 'url_club' in clubData and clubData['url_club']:
            lbl = tk.Label(info1, text= clubData["nom"], font= ('Segoe 9 underline'), fg="#0000FF", anchor=W)
            lbl._values = clubData['_id']
            lbl.bind("<Button-1>", self.webCall)
            lbl.bind('<Enter>', on_enter)
            lbl.bind('<Leave>', on_leave)
        else:
            lbl = tk.Label(info1, text= clubData["nom"], anchor=W)
        lbl.grid(row=0, column=1, sticky=tk.W) 
        if clubData["prive"]:
            lbl = tk.Label(info1, text= "(Privé)", font= ('Segoe 9 bold'), anchor=W)
            lbl.grid(row=0, column=2, sticky=tk.W)           
        
        info2 = tk.Frame(self.infoFrame, padx=5)
        info2.pack(fill=X)
        lbl = tk.Label(info2, text= clubData["adresse"] + ", ", anchor=W)
        lbl.grid(row=0, column=0, sticky=tk.W)       
        lbl = tk.Label(info2, text= clubData["municipal"] + ", ", anchor=W)
        lbl.grid(row=0, column=1, sticky=tk.W) 
        cp = "" if not "email" in clubData else clubData["email"]
        lbl = tk.Label(info2, text= clubData["codepostal2"], anchor=W)
        lbl.grid(row=0, column=2, sticky=tk.W)    
        em = "" if not "email" in clubData else clubData["email"]
        lbl = tk.Label(info2, text= em, anchor=W, padx=5)
        lbl.grid(row=0, column=3, sticky=tk.W)
        t1 = "" if not "telephone" in clubData else clubData["telephone"]
        lbl = tk.Label(info2, text= t1, anchor=W)
        lbl.grid(row=0, column=4, sticky=tk.W)
        t2 = "" if not "telephone2" in clubData else clubData["telephone2"]
        lbl = tk.Label(info2, text= t2, anchor=W)
        lbl.grid(row=0, column=5, sticky=tk.W)
        t3 = "" if not "telephone3" in clubData else clubData["telephone2"]
        lbl = tk.Label(info2, text= t3, anchor=W)
        lbl.grid(row=0, column=6, sticky=tk.W)

        self.parcListFrame = tk.Frame(self.infoFrame, padx=15)
        self.parcListFrame.pack(fill=X)
        rNbr = 0
        b = "•"
        for Pdata in clubData["courses"]:
            titleParcFrame = tk.Frame(self.parcListFrame)
            titleParcFrame.pack(fill=X)        
            lbl = tk.Label(titleParcFrame, text= b, anchor=W)
            lbl.grid(row=0, column=0, sticky=tk.W)
            lbl = tk.Label(titleParcFrame, text= str(Pdata["PARCOURS"]), anchor=W)
            lbl.grid(row=0, column=1, sticky=tk.W)
            
            det = ("Exécutif " if str(Pdata["POINTS"]) == "E" else "") + str(Pdata["TROUS"]) + " trous"
            #det = str(Pdata["TROUS"]) + " trous"
            dep = "," if Pdata["DEPUIS"] == 0 else " depuis " + str(Pdata["DEPUIS"]) + ","
            det += dep + " normale " + str(Pdata["NORMALE"]) + ", " + str(Pdata["VERGES"]) + " verges "
            lbl = tk.Label(titleParcFrame, text= det, anchor=W)
            lbl.grid(row=0, column=2, sticky=tk.W)


        # Courses
        self.srcFrame = cdc.VscrollFrame(self.pop)
        self.srcFrame.pack(expand= True, fill=BOTH)
        
        coursesListFrame = tk.Frame(self.srcFrame.interior, padx=10, pady=5)
        coursesListFrame.pack(fill=X)    
        
        
        for Pdata in clubData["courses"]:
                
            is18 = True if Pdata["TROUS"] == 18 else False
            parcFrame = tk.Frame(coursesListFrame, borderwidth = 1, relief=RIDGE, padx=10, pady=5)
            parcFrame.pack(fill=X)
            
            titleParcFrame = tk.Frame(parcFrame)
            titleParcFrame.pack(fill=X)
            det = "Parcours: " + str(Pdata["PARCOURS"]) + " "
            det += str(Pdata["TROUS"]) + " trous"
            lbl = tk.Label(titleParcFrame, text= det, font= ('Segoe 9 bold'), anchor=W)
            lbl.grid(row=0, column=0, sticky=tk.W)
            if self.masterForm.userRole == "ADM" or self.masterForm.userRole == "MEA"  or self.masterForm.userRole == "MEM":
                butAddGame = ttk.Button(titleParcFrame, text="Ajouter une partie", command= lambda Pdata=Pdata, nom=clubData["nom"]: self.addGame(Pdata, nom)) 
                butAddGame.grid(row=0, column=1, sticky=tk.W)
            
            # Blocs

            blocsFrame = tk.Frame(parcFrame)
            blocsFrame.pack(fill=X)
            #pdb.set_trace()

            lbl = tk.Label(blocsFrame, text= "Trou" , borderwidth = 1, relief=RIDGE, bg= "#ccc" )
            lbl.grid(row=0, column=0, sticky="WE")

            # Trous 
            for tr in range(1,10):
                lbl = tk.Label(blocsFrame, text= str(tr), borderwidth = 1, relief=RIDGE, width = 3, bg= "#ccc" )
                lbl.grid(row=0, column=tr, sticky="WE")
            if not is18:
                lbl = tk.Label(blocsFrame, text= "Total", font= ('Segoe 9 bold'), borderwidth = 1, width = 4, relief=RIDGE, bg= "#ccc" )
                lbl.grid(row=0, column=10, sticky="WE")            
            else:
                lbl = tk.Label(blocsFrame, text= "OUT", borderwidth = 1, width = 4, relief=RIDGE, bg= "#ccc" )
                lbl.grid(row=0, column=10, sticky="WE")        
                for tr in range(12,21):
                    lbl = tk.Label(blocsFrame, text= str(tr-2), borderwidth = 1, width = 3, relief=RIDGE, bg= "#ccc" )
                    lbl.grid(row=0, column=tr-1, sticky="WE")        
                lbl = tk.Label(blocsFrame, text= "IN", borderwidth = 1, width = 4, relief=RIDGE, bg= "#ccc" )
                lbl.grid(row=0, column=20, sticky="WE")  
                ev = "ev" if not "Eval" in clubData else clubData["Eval"]
                lbl = tk.Label(blocsFrame, text= "Total", font= ('Segoe 9 bold'), borderwidth = 1, relief=RIDGE, width = 5, bg= "#ccc")
                lbl.grid(row=0, column=21, sticky=tk.W)            
                sl = "sl" if not "Slope" in clubData else clubData["Slope"]
                lbl = tk.Label(blocsFrame, text= "Éval.", borderwidth = 1, relief=RIDGE, width = 5, bg= "#ccc")
                lbl.grid(row=0, column=22, sticky=tk.W)
                lbl = tk.Label(blocsFrame, text= "Slope", borderwidth = 1, relief=RIDGE, width = 5, bg= "#ccc")
                lbl.grid(row=0, column=23, sticky=tk.W)

            #pdb.set_trace()
            
            # Bloc collection
            r = 1
            for Bdata in Pdata["Blocs"]:
                
                bn, bg, fg = Bdata['Bloc'], blocksCol['B' + Bdata['Bloc']][1], blocksCol['B' + Bdata['Bloc']][0]
                if Bdata['Bloc'] == 'Normale':
                    bn = "Par"
                lbl = tk.Label(blocsFrame, text= bn, bg= bg, fg= fg , borderwidth = 1, relief=RIDGE )            
                lbl.grid(row=r, column=0, sticky="WE")  
                for tr in range(1,10):
                    lbl = tk.Label(blocsFrame, text= Bdata["T" +str(tr)], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=tr, sticky="WE")
                if not is18:
                    lbl = tk.Label(blocsFrame, text= Bdata["Aller"], font= ('Segoe 9 bold'), bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=10, sticky="WE") 
                    #pdb.set_trace()
                else:
                    lbl = tk.Label(blocsFrame, text= Bdata["Aller"], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=10, sticky="WE")        
                    for tr in range(12,21):
                        lbl = tk.Label(blocsFrame, text= Bdata["T" +str(tr-2)], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                        lbl.grid(row=r, column=tr-1, sticky="WE")   
                    lbl = tk.Label(blocsFrame, text= Bdata["Retour"], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE )
                    lbl.grid(row=r, column=20, sticky="WE")  
                    lbl = tk.Label(blocsFrame, text= Bdata["Total"], font= ('Segoe 9 bold'), bg= bg, fg= fg, borderwidth = 1, relief=RIDGE, width = 5 )
                    lbl.grid(row=r, column=21, sticky="WE")
                    lbl = tk.Label(blocsFrame, text= Bdata["Eval"], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE, width = 5)
                    lbl.grid(row=r, column=22, sticky=tk.W)
                    lbl = tk.Label(blocsFrame, text= Bdata["Slope"], bg= bg, fg= fg, borderwidth = 1, relief=RIDGE, width = 5)
                    lbl.grid(row=r, column=23, sticky=tk.W)
                r += 1
        
        
        self.srcFrame.update()


        butFrame = tk.Frame(self.pop, pady=5)
        butFrame.pack(expand= True, side=LEFT, fill=X)
        butClose = ttk.Button(butFrame, text="Fermer", command=self.close, width=15 ) 
        butClose.pack()

        
        self.gameWinDim()
        x=1
        #print(clubData)

    def addGame(self, Pdata, nom):
        addGameWin(self, Pdata, nom)
        #print(str(parcID) + nom)
        
    def close(self):
        self.pop.destroy()
        
    def webCall(self, e, val = 0):
        url = "https://cdore.ddns.net/ficheClub.html?data=" + str(e.widget._values)
        cdc.showWebURL(url)        
        
    def gameWinDim(self):
        #self.pop.update_idletasks()                                                             ##update_idletasks
        self.infoFrame.update()
        self.srcFrame.update()
        wt = self.pop.winfo_width()
        hi = self.infoFrame.winfo_height()
        hb = self.srcFrame.interior.winfo_height()
        
        ht = hi + hb + 35
        #print(" hi=" + str(hi) + " hb=" + str(hb) + " ht=" + str(ht))
        self.pop.geometry(f"{wt}x{ht}")    
       

class addGameWin():
    def __init__(self, masterForm, Pdata, nom):
        self.win = masterForm.win
        self.masterForm = masterForm.masterForm
        
        self.data = masterForm.data
        #print(str(Pdata) + nom)
        
        self.showAddGame(Pdata, nom)
        

    def showAddGame(self, Pdata, nom):
        TG, PG, LG = [], [], []
        self.TG, self.PG, self.LG = TG, PG, LG
        
        self.pop = tk.Toplevel(self.win)
        self.pop.title("Ajouter une partie")
        self.pop.iconbitmap(GOLFICON)
        self.masterForm.childWin.append(self.pop)
        self.nomClub = nom
        self.parcID = Pdata["_id"]
        self.objMess = cdc.messageObj(self.pop, height=25)
        
        # Club info
        self.infoFrame = tk.Frame(self.pop, padx=5)
        self.infoFrame.pack(fill=X)
               
        infoParc = tk.Frame(self.infoFrame)
        infoParc.pack(fill=X)
        lbl = tk.Label(infoParc, text= "Club: ", anchor=W)
        lbl.grid(row=0, column=0, sticky=tk.W)
        lbl = tk.Label(infoParc, text= nom, anchor=W)
        lbl.grid(row=0, column=1, sticky=tk.W)
        if Pdata['PARCOURS'] != "":
            lbl = tk.Label(infoParc, text= " - Parcours: " + Pdata['PARCOURS'], anchor=W)
            lbl.grid(row=0, column=2, sticky=tk.W)

        lbl = tk.Label(infoParc, text= "Date: ", anchor=W)
        lbl.grid(row=1, column=0, sticky=tk.W)
        self.varDate = StringVar()
        self.varDate.set(time.strftime("%Y-%m-%d"))
        recDate = Entry(infoParc, textvariable=self.varDate, width=14)
        recDate.focus()
        recDate.grid(row=1, column=1, sticky=tk.W, pady=3)
        recDate.bind("<Button-1>", self.objMess.clearMess)
        
        calFrame = tk.Frame(infoParc)
        cal = cdc.selectDate(self.pop, "Sélectionner la date de la partie", calFrame, 2, theDate=self.varDate)
        calFrame.grid(row=1, column=2, sticky=tk.W, padx=0, pady=3)
        
        self.blocCollVal = getBlocsArr(Pdata['Blocs'])

        lbl = tk.Label(infoParc, text= "Bloc: ", anchor=W)
        lbl.grid(row=2, column=0, sticky=tk.W)        
        self.comboBloc = ttk.Combobox( infoParc, state="readonly", width=10)
        self.comboBloc["values"] = self.blocCollVal
        self.comboBloc.current(0)
        self.comboBloc.grid(row=2, column=1, sticky=tk.W)
        self.comboBloc.bind("<<ComboboxSelected>>", self.setBloc)
        

        #Game info
        is18 = True if Pdata["TROUS"] == 18 else False
        self.is18 = is18

        recframe = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE, padx=10, pady=5)
        recframe.pack(expand= True, fill=BOTH)
        self.recframe = recframe
        self.recframe.win = self.pop
        
        # Trou
        lbl = tk.Label(recframe, text= 'Trou', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=0, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= str(tr), borderwidth = 1, relief=RIDGE, width = 3 )
            lbl.grid(row=0, column=tr, sticky="WE")
        if not is18:
            lbl = tk.Label(recframe, text= "Total", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= "OUT", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= str(tr-2), borderwidth = 1, width = 3, relief=RIDGE )
                lbl.grid(row=0, column=tr-1, sticky="WE")        
            lbl = tk.Label(recframe, text= "IN", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=20, sticky="WE")  
            lbl = tk.Label(recframe, text= "Total", borderwidth = 1, width = 4, relief=RIDGE )
            lbl.grid(row=0, column=21, sticky="WE")

        # Par
        r = 1
        pOUT, pIN = 0, 0
        Pdat = Pdata['Blocs']
        #pdb.set_trace()
        Pdat = self.getBloc(Pdata['Blocs'], 'Normale')
        lbl = tk.Label(recframe, text= 'Par', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= Pdat["T" +str(tr)], borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=tr, sticky="WE")
            pOUT += int(Pdat["T" +str(tr)])
        if not is18:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= Pdat["T" +str(tr-2)], borderwidth = 1, relief=RIDGE )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += int(Pdat["T" +str(tr-2)])
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
            lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")

        # Score
        r = 2
        self.lblScore = tk.Label(recframe, text= 'Score', borderwidth = 1, relief=RIDGE )
        self.lblScore.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):        
            TG.append(Pdat["T" +str(tr)])
            TG[tr - 1] = tk.StringVar()
            TG[tr - 1].set(Pdat["T" +str(tr)])
            fld = cdc.editEntry(self.recframe, width=2, textvariable= (TG[tr - 1]), isNum=True, maxlen=2)        
            fld.grid(row=r, column=tr, sticky="WE")
            fld.bind("<KeyRelease>", lambda event, Tval=TG , row=r: self.calcTot(event, Tval, row))
        lbl = tk.Label(recframe, text= Pdat["Aller"], borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=10, sticky="WE")
        if is18:
            for tr in range(10,19):        
                TG.append(Pdat["T" +str(tr)])
                TG[tr - 1] = tk.StringVar()
                TG[tr - 1].set(Pdat["T" +str(tr)])
                fld = cdc.editEntry(self.recframe, width=2, textvariable= (TG[tr - 1]), isNum=True, maxlen=2)        
                fld.grid(row=r, column=tr+1, sticky="WE")
                fld.bind("<KeyRelease>", lambda event, Tval=TG , row=r: self.calcTot(event, Tval, row))
            lbl = tk.Label(recframe, text= Pdat["Retour"], borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")
            lbl = tk.Label(recframe, text= Pdat["Total"], borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")
        self.setBloc()

        # Putts
        r = 3
        lbl = tk.Label(recframe, text= 'Putts', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):        
            PG.append("2")
            PG[tr - 1] = tk.StringVar()
            PG[tr - 1].set("2")
            fld = cdc.editEntry(self.recframe, width=2, textvariable= (PG[tr - 1]), isNum=True, maxlen=2)        
            fld.grid(row=r, column=tr, sticky="WE")
            fld.bind("<KeyRelease>", lambda event, Tval=PG , row=r: self.calcTot(event, Tval, row))
        lbl = tk.Label(recframe, text= "18", borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=10, sticky="WE")
        if is18:
            for tr in range(10,19):        
                PG.append("2")
                PG[tr - 1] = tk.StringVar()
                PG[tr - 1].set("2")
                fld = cdc.editEntry(self.recframe, width=2, textvariable= (PG[tr - 1]), isNum=True, maxlen=2)        
                fld.grid(row=r, column=tr+1, sticky="WE")
                fld.bind("<KeyRelease>", lambda event, Tval=PG , row=r: self.calcTot(event, Tval, row))
            lbl = tk.Label(recframe, text= "18", borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")
            lbl = tk.Label(recframe, text= "36", borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")

        # Pénalité
        r = 4
        lbl = tk.Label(recframe, text= 'Pénalité', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):        
            LG.append("0")
            LG[tr - 1] = tk.StringVar()
            LG[tr - 1].set("")
            fld = cdc.editEntry(self.recframe, width=2, textvariable= (LG[tr - 1]), isNum=True, maxlen=2)        
            fld.grid(row=r, column=tr, sticky="WE")
            fld.bind("<KeyRelease>", lambda event, Tval=LG , row=r: self.calcTot(event, Tval, row))
        lbl = tk.Label(recframe, text= "0", borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=10, sticky="WE")
        if is18:
            for tr in range(10,19):        
                LG.append("0")
                LG[tr - 1] = tk.StringVar()
                LG[tr - 1].set("")
                fld = cdc.editEntry(self.recframe, width=2, textvariable= (LG[tr - 1]), isNum=True, maxlen=2)        
                fld.grid(row=r, column=tr+1, sticky="WE")
                fld.bind("<KeyRelease>", lambda event, Tval=LG , row=r: self.calcTot(event, Tval, row))
            lbl = tk.Label(recframe, text= "0", borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")
            lbl = tk.Label(recframe, text= "0", borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE")

        butFrame = tk.Frame(self.pop, pady=5)
        butFrame.pack(expand= True, side=LEFT, fill=X, anchor=CENTER)
        self.butEdit = tk.Frame(butFrame)
        self.butEdit.pack()
        butClose = ttk.Button(self.butEdit, text="Fermer", command=self.close, width=15) 
        butClose.grid(row=0, column=0, sticky="WE", padx=5)
        butEdit = ttk.Button(self.butEdit, text="Enregistrer", command=self.saveGame, width=15) 
        butEdit.grid(row=0, column=1, sticky="WE", padx=5)        

    def saveGame(self):
        dat = {}
        
        dat["USER_ID"] = USER_ID
        dat["PARCOURS_ID"] = self.parcID
        dat["bloc"] = "B" +self.comboBloc.get()
        dat["name"] = self.nomClub
        gameDate = self.varDate.get()
        if gameDate == '':
            self.objMess.showMess("La date de la partie est requise.")
            return
        else:
            try:
                dt = datetime.datetime.strptime(gameDate, "%Y-%m-%d")
                dat["score_date"] = dt.timestamp() * 1000
            except ValueError:
                self.objMess.showMess("Le format de la date de la partie est invalide: AAAA-MM-JJ.")
                return
                
        if not getGameScore(self.TG, self.PG, self.LG, dat, self.is18):
            self.objMess.showMess("Une valeur numérique est requise.")
        else:
            coll = self.data.score
            doc = coll.update_one({"score_date": dat["score_date"]}, { "$set": dat },  upsert=True )
            self.objMess.showMess("Enregistré!", type = "I")
            
        #print(dat)
        
    def calcTot(self, event, Tval, r):
        #self.objMess.clearMess()
        totO, totI = calculTot(Tval, self.is18)

        lbl = tk.Label(self.recframe, text= str(totO), borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=10, sticky="WE")   
        
        if self.is18:
            lbl = tk.Label(self.recframe, text= str(totI), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")   
            lbl = tk.Label(self.recframe, text= str(totO + totI), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=21, sticky="WE") 

    def setBloc(self, event = None):
        color = blocksCol["B" + self.comboBloc.get()]
        #print(color)
        self.lblScore.config(foreground= color[0])
        self.lblScore.config(background= color[1])
        self.objMess.clearMess()
            
    def close(self):
        self.pop.destroy()
        
    def getBloc(self, blocColl, blocName):
        #pdb.set_trace()
        for x in blocColl:
            if x["Bloc"] == blocName:
                return x
                break