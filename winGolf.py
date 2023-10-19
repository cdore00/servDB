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
#from collections import defaultdict  #Non requis

import cdControl as cdc

# JSON
from bson import ObjectId
import json

# MongoDB
import pymongo
from pymongo import MongoClient


APPICON = 'C:/Users/charl/github/cuisine/misc/favicon.ico'

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
        #second_win.protocol('WM_DELETE_WINDOW',lambda: onclose(second_win))
        self.pop.protocol('WM_DELETE_WINDOW',self.destroyRef)
        #self.pop.bind('<Destroy>', self.destroyRef)

        self.pop.title("Parties")
        if os.path.exists(APPICON):
            self.pop.iconbitmap(APPICON)

        
        
        # Search form
        self.scoreframe = cdc.VscrollFrame(self.pop)
        self.scoreframe.pack(expand= True, fill=BOTH) 


        recframe = cdc.resizeFrame(self.scoreframe.interior, borderwidth = 1, relief=RIDGE, pack=False)
        recframe.pack(fill=X, padx=10, pady=10, anchor=W)        
        self.editFrame = recframe

        self.comboClub = ttk.Combobox( recframe, state="readonly", width=40)
        self.comboClub["values"] = ["Tous les clubs"]
        self.comboClub.current(0)
        self.comboClub.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5, pady=3) 
        #self.comboClub.bind("<<ComboboxSelected>>", self.selectClub)
        self.comboClub.bind("<Button-1>", self.loadClubCombo)

        self.varDate = StringVar()
        self.varDate.set("")
        recDate = cdc.editEntry(recframe, textvariable=self.varDate, width=15, maxlen=10)
        recDate.focus()
        recDate.grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        
        calFrame = tk.Frame(recframe)
        cal = cdc.selectDate(self.pop, "Sélectionner une date de début", calFrame, 2, theDate=self.varDate)
        calFrame.grid(row=1, column=1, sticky=tk.W, padx=0, pady=3)

        self.comboTrou = ttk.Combobox( recframe, state="readonly", width=10)
        self.comboTrou["values"] = ["18 trous", "9 trous"]
        self.comboTrou.current(0)
        self.comboTrou.grid( row=1, column=2, columnspan=2, sticky=tk.W, padx=10, pady=3)
        self.comboTrouVal = [18,9]
        
        self.comboNbr = ttk.Combobox( recframe, state="readonly", width=12)
        self.comboNbr["values"] = ["5 parties", "10 parties", "20 parties H", "50 parties", "100 parties"]
        self.comboNbr.current(0)
        self.comboNbr.grid( row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.comboNbrVal = [5,10,20,50,100]
        self.comboNbr.current(2)

        self.varLimit = StringVar()
        #self.varLimit.set("20")
        recLimit = tk.Entry(recframe, textvariable=self.varLimit, width=5)
        recLimit.grid( row=2, column=1, sticky=tk.W, padx=5, pady=3)

        butNext = ttk.Button(recframe, text="Suivant", command=self.nextGame, width=15 ) 
        butNext.grid(row=2, column=2, padx=5, sticky="WE") 
        
        butClear = cdc.RoundedButton(recframe, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.resetForm)
        butClear.create_text(12,11, text="x", fill="black", font=('Helvetica 15 '))
        butClear.grid(row=2, column=3, sticky=tk.W)
        Hovertip(butClear,"Blanchir le formulaire")
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

            handi = ("Hand.: " + str(round(h/10,1)) if r==20 else "")
            return handi, ("Moy.: " + str(round(m/cnt,1)))    
    
        
        # Grid score games
        if not self.gridframe is None:
            self.gridframe.destroy()
            self.gridframe = None
            self.footFrame.destroy()
        else:
            headFrame = tk.Frame(self.scoreframe.interior)
            headFrame.pack( fill=X, padx=10)
            headFrame.grid_columnconfigure(0, weight=1, uniform="True")
            headFrame.grid_columnconfigure(1, weight=2, uniform="True")
            headFrame.grid_columnconfigure(1, weight=1, uniform="True")            
            #self.sortHead(headFrame, headLabels = ["Date ", "Club ", "Score "], headConfig = [{"type": "C", "length": 8}, {"type": "C", "length": 15}, {"type": "N", "length": 7} ])
            self.sortObj = cdc.sortGridObj(headFrame, headLabels = ["Date ", "Club ", "Score "], headConfig = [{"type": "C", "length": 8}, {"type": "C", "length": 15}, {"type": "N", "length": 7} ])


        dataList = self.getGameList(user, parc, skip, limit, is18, intDate)
        rowN = 0
        tot = []
        
        gridframe = tk.Frame(self.scoreframe.interior)
        gridframe.pack( fill=X, padx=10)

        self.sortObj.setGridframe(gridframe)
        
        gridframe.grid_columnconfigure(0, weight=1, uniform="True")
        gridframe.grid_columnconfigure(1, weight=2, uniform="True")
        gridframe.grid_columnconfigure(1, weight=1, uniform="True")       
        for x in dataList:

            lbl = tk.Label(gridframe, text= cdc.milliToDate(x["score_date"]), pady=1, width=8, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=0, sticky="WE")  
            lbl._values = x["_id"]
            lbl.bind("<Button-1>", self.showGame)
            lbl = tk.Label(gridframe, text= x["name"], pady=1, width=15, borderwidth = 1, relief=RIDGE, anchor=W)
            lbl.grid(row= rowN, column=1, sticky="WE")
            if len(x["name"]) > 15:
                Hovertip(lbl,x["name"])
            #lbl._values = x["_id"]
            s = int(calcScore(x))
            tot.append(s)
            lbl = tk.Label(gridframe, text= str(s), pady=1, width=7, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=2, sticky="WE")
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
        footFrame.grid_columnconfigure(1, weight=1, uniform="True")        
        h,m = calcStat(tot, rowN)
        lbl = tk.Label(footFrame, text=h, font= ('Segoe 9 bold'), borderwidth = 1, relief=RIDGE )
        lbl.grid(row=0, column=0, sticky=tk.NSEW)
  
        lbl = tk.Label(footFrame, text= str(rowN) + " parties", borderwidth = 1, font= ('Segoe 9 bold'), relief=RIDGE )
        lbl.grid(row=0, column=1, sticky=tk.NSEW)            
 
        lbl = tk.Label(footFrame, text=m, borderwidth = 1, font= ('Segoe 9 bold'), relief=RIDGE )
        lbl.grid(row=0, column=2, sticky=tk.NSEW)        

        
    def nextGame(self):
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
        #pdb.set_trace()
        
        
        self.listGamesScore( user=80, parc=parcours, skip=self.skip, limit=nbr, is18=trou, intDate=intDat)
        
        #self.sortGrid(2)
        #self.sortGrid()
        x=2
    
    def resetForm(self):
        self.varDate.set("")
        self.comboClub.current(0)
        self.comboNbr.current(2)
        self.comboTrou.current(0)
        self.varLimit.set("")

    def loadClubCombo(self, event=None):
    
        dataList = self.countUserGame()
        
        self.comboClubVal, clubList = [], []
        self.comboClubVal.append(0)
        clubList.append("Tous les clubs")
        
        for x in dataList:
            self.comboClubVal.append(x["_id"]["parcours"])
            clubList.append(x["_id"]["name"] + " (" + str(x["count"]) + ")")
        
        self.comboClub["values"] = clubList
       
    
    def getGameList(self, user=80, parc=0, skip=0, limit=20, is18=18, intDate=0):
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
        
    def countUserGame(self, user=80, is18=18):
        """
        param = param["data"][0]
        para = [x for x in param.split("$")]
        user = getID(para[0])
        is18 = int(para[1])
        #pdb.set_trace()
        withGroup = True if len(para) > 2 else False
        """
        withGroup = True 
        coll = self.data.score
        if (is18 == 18):
            count = coll.count_documents({"USER_ID": user, "T18": { "$exists": True, "$nin": [ 0 ] }})
            if withGroup == True:
                group = coll.aggregate([ {"$match" : {"USER_ID": user, "T18": { "$exists": True, "$nin": [ 0 ] }}}, {"$group" : {"_id":{"name":"$name","parcours":"$PARCOURS_ID"}, "count":{"$sum":1}}} ])
        else:
            count = coll.count_documents({"USER_ID": user, "$or":[{"T18":0},{"T18":None}]  } )
            if withGroup == True:
                group = coll.aggregate([ {"$match" : {"USER_ID": user, "$or":[{"T18":0},{"T18":None}]  }}, {"$group" : {"_id":{"name":"$name","parcours":"$PARCOURS_ID"}, "count":{"$sum":1}}} ])
                
        return list(group)


    def getGame(self, gameID):
            
        def getBloc(doc):
            coll = self.data.blocs
            blocs = coll.find({"PARCOURS_ID": doc['PARCOURS_ID'] })
            for x in blocs:
                if x['Bloc'] == "Normale":
                    doc['par'] = x
            return doc 
        
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
        h=self.scoreframe.interior.winfo_height() + 5
        
        #pdb.set_trace()
        self.pop.geometry(f"{w}x{h}") 
        my = self.masterForm.win.winfo_x() - w - 5
        my = 0 if my < 0 else my
        self.pop.geometry(f"+{my}+0")
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
        #pdb.set_trace()
        dat = self.getGame(id)
        winGame = showGame(self.pop, dat)
        
        
class showGame():
    def __init__(self, winListGames, Gdata):
        
        is18 = "T18" in Gdata and type(Gdata["T18"]) == int
        #print("CLASSshowGame : " + str(Gdata))
        self.pop = tk.Toplevel(winListGames)
        
        titleFrame = tk.Frame(self.pop)
        titleFrame.pack()
        lbl = tk.Label(titleFrame, text= Gdata['score_date'] + " : ")
        lbl.grid(row=0, column=0, sticky="WE")  
        lbl = tk.Label(titleFrame, text= Gdata['name'] )
        lbl.grid(row=0, column=1, sticky="WE")
        
        recframe = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE, padx=10, pady=5)
        recframe.pack(expand= True, fill=BOTH)
        
        # Trou
        lbl = tk.Label(recframe, text= Gdata['bloc'], borderwidth = 1, relief=RIDGE )
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
        lbl = tk.Label(recframe, text= 'Score', borderwidth = 1, relief=RIDGE )
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
                lbl = tk.Label(recframe, text= Gdata["T" +str(tr-2)], borderwidth = 1, relief=RIDGE, bg= Bcolor )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += diff
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
        lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=21, sticky="WE")
        
        # Pénalité
        r = 4
        pOUT, pIN = 0, 0
        lbl = tk.Label(recframe, text= 'Pénalité', borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=0, sticky="WE")        
        for tr in range(1,10):
            lbl = tk.Label(recframe, text= Gdata["L" +str(tr)], borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=tr, sticky="WE")
            pOUT += int(Gdata["L" +str(tr)])
        if not is18:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")            
        else:
            lbl = tk.Label(recframe, text= str(pOUT), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=10, sticky="WE")        
            for tr in range(12,21):
                lbl = tk.Label(recframe, text= Gdata["L" +str(tr-2)], borderwidth = 1, relief=RIDGE )
                lbl.grid(row=r, column=tr-1, sticky="WE")   
                pIN += int(Gdata["L" +str(tr-2)])
            lbl = tk.Label(recframe, text= str(pIN), borderwidth = 1, relief=RIDGE )
            lbl.grid(row=r, column=20, sticky="WE")                
        lbl = tk.Label(recframe, text= str(pOUT + pIN), borderwidth = 1, relief=RIDGE )
        lbl.grid(row=r, column=21, sticky="WE")  

        butClose = ttk.Button(self.pop, text="Fermer", command=self.close, width=15 ) 
        butClose.pack()
        x=2
        
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
