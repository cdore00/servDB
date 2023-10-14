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
from tkinter.tix import *
from tkinter.scrolledtext import ScrolledText
from tkcalendar import Calendar
from tkinter import font as tkFont  
from idlelib.tooltip import Hovertip
from collections import defaultdict

import cdControl as cdc

# JSON
from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads
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
        #self.pop.iconbitmap(APPICON)

        
        
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
        self.comboClub.bind("<<ComboboxSelected>>", self.selectClub)
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
        #self.masterForm.winGame = self
        print("skip:" + str(skip) + " limit: " + str(limit))
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
        dataList = self.getGameList(user, parc, skip, limit, is18, intDate)
        gridframe = tk.Frame(self.scoreframe.interior)
        gridframe.pack(expand= True, side=LEFT, fill=X, padx=10)
        self.gridframe = gridframe
   
        gridframe.grid_columnconfigure(0, weight=1, uniform="True")
        gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
        lbl = tk.Label(gridframe, text="Date", bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE )
        lbl.grid(row=0, column=0, sticky=tk.NSEW)
        #Hovertip(lbl,colB[0])

        gridframe.grid_columnconfigure(1, weight=2, uniform="True")
        gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
        lbl = tk.Label(gridframe, text="Club", bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE )
        lbl.grid(row=0, column=1, sticky=tk.NSEW)            

        gridframe.grid_columnconfigure(1, weight=1, uniform="True")
        gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
        lbl = tk.Label(gridframe, text="Score", bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE )
        lbl.grid(row=0, column=2, sticky=tk.NSEW)

        rowN = 0
        tot = []
        for x in dataList:
            rowN += 1        
            lbl = tk.Label(gridframe, text= cdc.milliToDate(x["score_date"]), pady=1, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=0, sticky="WE")        
            #lbl._values = x["_id"]
            #lbl.bind("<Button-1>", self.gridCall)
            lbl = tk.Label(gridframe, text= x["name"], pady=1, width=20, borderwidth = 1, relief=RIDGE, anchor=W)
            lbl.grid(row= rowN, column=1, sticky="WE")
            if len(x["name"]) > 25:
                Hovertip(lbl,x["name"])
            #lbl._values = x["_id"]
            s = int(calcScore(x))
            tot.append(s)
            lbl = tk.Label(gridframe, text= str(s), pady=1, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=2, sticky="WE")
        
        print(str(rowN))
        if rowN < limit:
            self.skip = 0
            print("reset rowN: " + str(rowN) + "  limit: " + str(limit))
        else:
            self.skip += limit
            
        h,m = calcStat(tot, rowN)
        #pdb.set_trace()
        rowN += 1
        lbl = tk.Label(gridframe, text=h, font= ('Segoe 9 bold'), borderwidth = 1, relief=RIDGE )
        lbl.grid(row=rowN, column=0, sticky=tk.NSEW)
  
        lbl = tk.Label(gridframe, text= str(rowN-1) + " parties", borderwidth = 1, font= ('Segoe 9 bold'), relief=RIDGE )
        lbl.grid(row=rowN, column=1, sticky=tk.NSEW)            
 
        lbl = tk.Label(gridframe, text=m, borderwidth = 1, font= ('Segoe 9 bold'), relief=RIDGE )
        lbl.grid(row=rowN, column=2, sticky=tk.NSEW)        

        
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
        #pdb.set_trace()
        print(self.comboClubVal)
        #countUserGame
    
    def selectClub(self, event=None):
        print(event)        
    
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
        """
        if withGroup == True:
            return ('{"count":' + str(count) + ',"group":' + dumps(group) + '}')
        else:
            return ('{"count":' + str(count) + '}')
        """


    def winDim(self, adjustPosition = False):
        self.win.update_idletasks()                                                             ##update_idletasks
        w=self.pop.winfo_width()
        h=self.scoreframe.interior.winfo_height() + 5
        """
        if (self.win.winfo_screenheight() - 80) < h:
            h = self.win.winfo_screenheight() - 80
            if adjustPosition:
                self.pop.geometry("+50+0")
        """
        
        #pdb.set_trace()
        self.pop.geometry(f"{w}x{h}") 
        my = self.masterForm.win.winfo_x() - w - 5
        my = 0 if my < 0 else my
        self.pop.geometry(f"+{my}+0")
        self.win.update_idletasks()
        self.pop.attributes('-topmost', True)
        #self.pop.update()
        self.pop.attributes('-topmost', False)
        x=2
        
        
    def destroyRef(self, e=None):
        #print("isDestroy")
        self.isDestroy = True
        self.pop.destroy()
        
    def sortGrid(self):
        
        #get data
        list_of_labels_0 = self.gridframe.grid_slaves(column=0)
        list_of_labels_1 = self.gridframe.grid_slaves(column=1)
        label_values=[]
        data=defaultdict(list)
        for idx,_ in enumerate(list_of_labels_0):
            label=self.gridframe.grid_slaves(row=idx,column=0)[0]
            data[label].append(label['text'])
            label_values.append(label['text'])
        pdb.set_trace()
        #use data
        sort=sorted(label_values,key=str.lower)
        for idx,value in enumerate(sort):
            for label, v in data.items():
                if v[0] == value:
                    label.grid(row=idx, column=0)       

    def sortGrid2(self):
        #get data
        list_of_labels = self.gridframe.grid_slaves(column=0)
        label_values=[]
        data=defaultdict(list)
        for idx,_ in enumerate(list_of_labels):
            label=self.gridframe.grid_slaves(row=idx,column=0)[0]
            data[label].append(label['text'])
            label_values.append(label['text'])
        #use data
        sort=sorted(label_values,key=str.lower)
        for idx,value in enumerate(sort):
            for label, v in data.items():
                if v[0] == value:
                    label.grid(row=idx, column=0)
        
    def fun(self, event):
        print(event.keysym, event.keysym=='a')
        print(event)        