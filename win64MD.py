# coding=utf-8
#https://stackoverflow.com/questions/71677889/create-a-scrollbar-to-a-full-window-tkinter-in-python
#https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import
#pyinstaller main.py --onefile --name test --icon test.ico --noconsole
#Mise à jour et sécurité/Sécurité Windows/Protection contre les virus/Gérer les paramètres/Protection en temps réel
#Scripts\pyinstaller win64MD.py --onefile --name golf --noconsole
#Scripts\pyinstaller  -F --add-data C:\Users\charl\AppData\Local\Programs\Python\Python39\tcl\tix8.4.3;tcl\tix8.4.3 code\win64MD.py --noconsole
#C:\Users\charl\AppData\Local\Programs\Python\Python39\Scripts

import pdb
#; pdb.set_trace()

import sys, os, io, re, csv, urllib.parse
import json
import time 
import datetime
from sys import argv
import codecs

from bson.json_util import dumps
from bson.json_util import loads

from tkinter import *
import tkinter as tk
from tkinter import * 

from tkinter import messagebox, TclError, ttk
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
from idlelib.tooltip import Hovertip

import urllib
import urllib.request
import dropbox, base64
from PIL import ImageTk, Image
#import webbrowser

import cdControl as cdc
import winGolf as wg
import winRec  as wr
import winUser  as wu

# JSON
from bson import ObjectId

import json
import phonetics

# MongoDB
import pymongo
from pymongo import MongoClient

USER_ID = 0

def set_userid(USER_ID):
    wg.USER_ID = USER_ID
    wr.USER_ID = USER_ID
set_userid(USER_ID)

EDITOK  = False
wg.EDITOK = EDITOK
RECICON  = 'C:/Users/charl/github/cuisine/misc/favicon.ico'
if not os.path.exists(RECICON):
    RECICON = ''
wr.RECICON = RECICON
GOLFICON = 'C:/Users/charl/github/golf/images/golf.ico'
if not os.path.exists(GOLFICON):
    GOLFICON = ''
wg.GOLFICON = GOLFICON
CONFFILE = "winApp.conf"
APPG    = "Golf"
APPGBD  = "golf"
APPR    = "Recettes"
APPRBD  = "resto"
LSERV   = "Local"
VSERV   = "Vultr"
BUPDIR  = "./bupdata/"

        
class master_form_find():
    def __init__(self, mainWin, *args, **kwargs):
        self.win = mainWin
        self.data = dbaseObj()
        self.user = [""]
        self.userName = ""
        self.userRole = ""
        self.actApp   = APPR 
        self.actServ  = LSERV
        initInfo = self.readConfFile()
        if "init" in initInfo:
            self.actApp   = initInfo["init"][0] 
            self.actServ  = initInfo["init"][1]                             
        self.winGame = None
        self.winUsers = None
        self.childWin = []
        self.comboList = {}
        self.comboData = {}
        self.comboCat = None
        self.gridFrame = None

        self.setApp(self.actServ, self.actApp)

    def quitter(self, e):
        print("Quit")
        self.win.quit
    
    def setApp(self, serv, appName):
        self.actApp   = appName 
        self.actServ  = serv
        self.win.update_idletasks() 
        actAppDB = appName + " - " + serv
        self.win.title(actAppDB)
        if self.actApp == APPR:
            self.win.iconbitmap(RECICON)
        if self.actApp == APPG:
            self.win.iconbitmap(GOLFICON)
            
        self.closeRec()
        slavelist = self.win.slaves()
        for elem in slavelist:
            elem.destroy()
        
        
        # Création du menu
        zoneMenu = Frame(self.win)
        zoneMenu.pack(fill=X, anchor=W)
        menuFichier = Menubutton(zoneMenu, text='Fichier', width='10', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        menuFichier.grid(row=0,column=0)
        menuEdit = Button(zoneMenu, text='Quitter', width='10', font= ('Segoe 9 bold'), pady=1, borderwidth=2, relief = RAISED, command=self.win.quit)  #, command=self.win.quit  , Postcommand=self.win.quit
        menuEdit.grid(row=0,column=1)    

        menu_file = Menu(menuFichier, tearoff = 0)
        menu_file.add_cascade(label='Connecter...', command = self.login)   #, activebackground='lightblue', activeforeground='black'
        menu_file.add_separator()
        menu_file.add_cascade(label='Authentifier...', command = self.authentif)
        menu_file.add_cascade(label='Changer mot de passe...', command = self.changePass)

        menuFichier.configure(menu=menu_file)            
        
        # Progress bar frame
        self.pbFrame = tk.Frame(self.win)
        self.pbFrame.pack(fill=X)

        # Zone de message
        self.win.objMainMess = cdc.messageObj(self.win)
        self.win.objMainMess.showMess("Connexion...")
        self.win.update_idletasks() 

        isConnected = self.data.connectTo(serv, appName)
        self.win.objMainMess.clearMess()    
        
        mainFrame = tk.Frame(self.win, borderwidth = 1, relief=RIDGE)
        mainFrame.pack( fill=X, padx=10, pady=10)        
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)
        
        self.gridFrame = cdc.VscrollFrame(self.win)
        self.gridFrame.pack(expand= True, fill=BOTH)        
            
        formframe = self.add_input_frame(mainFrame)
        formframe.grid(column=0, row=0)
        formframe = self.add_button_frame(mainFrame)
        formframe.grid(column=1, row=0) 

        if isConnected:
            self.afficherTitre()
        else:
            messagebox.showinfo(
                title="Non connecté",
                message=f"Veuillez sélectionner une autre connexion.")
            self.win.title(actAppDB + " : Non connecté.")
        if not self.user:
            menu_file.delete(3)
        if self.userRole == "ADM":
            menu_file.add_cascade(label='Gérer les utilisateurs...', command = self.getUsers)
            menu_file.add_separator()
            menu_file.add_command(label='Exporter...', command = self.makeBackup_db)
            menu_file.add_command(label='Importer...', command = self.loadBackup_db)            
            
        self.getDataList()
        
        if self.actApp == APPR:
            self.win.geometry("550x500")
        if self.actApp == APPG:
            self.win.geometry("600x500")        

    
    def afficherTitre(self):
        self.win.title(self.actApp + " - " + self.actServ + " : Connecté " + ( "" if len(self.user) == 1 else " - " + self.userName))
    
    def loadCombo(self, comboObj = None, val = None):
        if self.data.isConnect:    
            if comboObj != None:
                 #pdb.set_trace()
                 cat_list = list(self.comboList.keys())
                 comboObj["values"] = cat_list
                 if val != None:
                    comboObj.current(cat_list.index(val))
            else:
                if self.actApp == APPR:
                    li = (self.data.getCat())
                    fld = "desc"
                if self.actApp == APPG:
                    li = (self.data.getReg())
                    fld = "Nom"
                #pdb.set_trace()
                self.comboData = li
                arg, lst = [], []
                arg.append("Toutes")
                for x in li:
                    arg.append(x[fld])
                    lst.append( (  x[fld] , x["_id"] ) )
                    
                self.comboList = dict(lst)
                self.comboCat["values"] = arg
                self.comboCat.current(1)
            return True
        else:
            return False

    def readConfFile(self):
        if os.path.exists(CONFFILE):
            #pdb.set_trace()
            with open(CONFFILE, encoding='utf8') as f:
                js = eval(f.read())
                return (js)            
        else:
            return {}

    def setConfFile(self, param = None):        
        #pdb.set_trace()
        initInfo = (self.readConfFile())
        
        initInfo["init"] = [self.actApp, self.actServ]
        initInfo[(self.actApp+self.actServ)] = {} 
        initInfo[(self.actApp+self.actServ)]["keyword"] = self.keyword.get()
        initInfo[(self.actApp+self.actServ)]["indIngr"] = self.indIngr.get()
        initInfo[(self.actApp+self.actServ)]["comboCat"] = self.comboCat.current()
        #if self.user != "":
        initInfo[(self.actApp+self.actServ)]["user"] = self.user
        #if param:
        #    ke=list(param.keys())
        #    initInfo[(self.actApp+self.actServ)][ke[0]] = param[ke[0]]       

        with open(CONFFILE, 'w', encoding='utf-8') as f:
            f.write(str(initInfo))
            #f.close()


    def setDefault(self, initInfo = None):
        if (not initInfo is None and self.actApp+self.actServ) in initInfo:
            actInfo = initInfo[(self.actApp+self.actServ)]
            self.keyword.delete(0,END)
            self.keyword.insert(0,actInfo["keyword"])
            self.indIngr.set(actInfo["indIngr"])
            self.comboCat.current(actInfo["comboCat"]) 
            #pdb.set_trace()
            if "user" in actInfo:
                dt = datetime.datetime.now()    #Date actuelle
                dtAct = dt.timestamp() * 1000
                dt2day = (dtAct + 172800000)  #Date actuelle + 2 jours
                
                if len(actInfo["user"]) == 1 or actInfo["user"][1] < dtAct or dt2day < actInfo["user"][1]:
                    del actInfo['user']
                    self.user, self.userName, self.userRole = [""], "", ""
                    return
                else:
                    self.user = actInfo["user"]
                    userInfo = self.data.getUserInfo(self.user[0])
                    self.userName = userInfo["Nom"]
                    self.userRole = userInfo["niveau"]
                    set_userid(userInfo["_id"])
                    #print(userInfo)
            else:
                self.user, self.userName, self.userRole = [""], "", ""
        
    def getDataList(self, event = None):
        
        if self.data.isConnect:
            wrd = self.keyword.get()
            indI = int(self.indIngr.get())
            cat = self.comboCat.get()

            self.setConfFile()
            
            if cat == "Toutes":
                cat = 0
            else:
                cat = self.comboList[cat]
                
            if wrd == '' and cat == 0 and self.actApp == APPG:
                messagebox.showinfo(
                    title="Recherche",
                    message=f"Veuillez soumettre un critère ")             
                return               
                
            if self.actApp == APPR:
                oData = (self.data.searchRecettes(wrd, indI, cat))
                listItems = oData["data"]
                colW = [10, 3, 3, 3, 3, 1]
                colH = ["Nom", "Catégorie", "Préparation", "Cuisson", "Portion", "Pub."]
                colB = ["Nom de la recette", "Catégorie de la recette", "Temps de préparation", "Temps de cuission", "Nombre de portions", "Non publié"]
                colT = [{"type": "C", "length": 20}, {"type": "C", "length": 5}, {"type": "C", "length": 5}, {"type": "C", "length": 5}, {"type": "C", "length": 5}, {"type": "C", "length": 2} ]
            if self.actApp == APPG:       
                oData = (self.data.searchClubs(wrd, indI, cat))
                listItems = oData["data"]                             
                colW = [4, 1, 1, 7, 3, 3]
                colH = ["Club", "Parc.", "Trous", "Adresse", "Ville", "Région"]
                colB = ["Nom du club", "Nombre de parcours", "Nombre de trous", "Adresse du club", "Ville du club", "Région du club"]
                colT = [{"type": "C", "length": 15}, {"type": "C", "length": 4}, {"type": "C", "length": 4}, {"type": "C", "length": 20}, {"type": "C", "length": 5}, {"type": "C", "length": 5} ]

            slavelist = self.gridFrame.interior.slaves()
            for elem in slavelist:
                elem.destroy()


            headFrame = tk.Frame(self.gridFrame.interior)
            headFrame.pack( fill=X, padx=10)
            headFrame.grid_columnconfigure(0, weight=colW[0], uniform="True")
            headFrame.grid_columnconfigure(1, weight=colW[1], uniform="True")
            headFrame.grid_columnconfigure(2, weight=colW[2], uniform="True")  
            headFrame.grid_columnconfigure(3, weight=colW[3], uniform="True")
            headFrame.grid_columnconfigure(4, weight=colW[4], uniform="True")
            headFrame.grid_columnconfigure(5, weight=colW[5], uniform="True")            
            self.sortObj = cdc.sortGridObj(headFrame, headLabels = colH, headConfig = colT, toolTip = colB)            


            mess = str(len(listItems)) + (" recettes trouvées " if self.actApp == APPR else " clubs trouvés ")
            if len(listItems) <= 1:
                mess = str(len(listItems)) + (" recette trouvé " if self.actApp == APPR else " club trouvé ")
            if wrd:
                mess += "où"
                if oData["ph"]:
                    mess += " la phonétique"
                mess += " « " + wrd + " » est contenu dans le nom " + ("de la recette" if self.actApp == APPR else "du club")
                if indI:
                    mess += (" ou les ingrédients de la recette" if self.actApp == APPR else " ou la ville du club")                   
            #pdb.set_trace()
            if cat:
                mess += (" dans la catégorie " if self.actApp == APPR else " dans la région ") + self.comboCat.get()
            mess += "."
            self.win.objMainMess.showMess(mess, 'I')    
           
            gridframe = tk.Frame(self.gridFrame.interior)
            gridframe.pack(expand= True, side=LEFT, fill=X, padx=10)
            self.sortObj.setGridframe(gridframe)
            
            gridframe.grid_columnconfigure(0, weight=colW[0], uniform="True")
            gridframe.grid_columnconfigure(1, weight=colW[1], uniform="True")
            gridframe.grid_columnconfigure(2, weight=colW[2], uniform="True")  
            gridframe.grid_columnconfigure(3, weight=colW[3], uniform="True")
            gridframe.grid_columnconfigure(4, weight=colW[4], uniform="True")
            gridframe.grid_columnconfigure(5, weight=colW[5], uniform="True")             
            rowN = 0
            if self.actApp == APPR:
                for x in listItems:
                    lbl = tk.Label(gridframe, text= x["nom"], font= ('Segoe 9 underline'), fg="#0000FF", pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                    #lbl = tk.Label(gridframe, text= x["nom"], pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                    lbl.grid(row= rowN, column=0, sticky="WE")        
                    lbl._values = x["_id"]
                    lbl.bind("<Button-1>", self.gridCall)
                    lbl = tk.Label(gridframe, text= x["cat"]["desc"], pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                    lbl.grid(row= rowN, column=1, sticky="WE")        
                    lbl._values = x["_id"]
                    lbl.bind("<Double-Button-1>", self.gridCall)  
                    lbl = tk.Label(gridframe, text= x["temp"], pady=1, borderwidth = 1, relief=RIDGE)
                    lbl.grid(row= rowN, column=2, sticky="WE")        
                    lbl._values = x["_id"]
                    lbl.bind("<Double-Button-1>", self.gridCall)  
                    lbl = tk.Label(gridframe, text= x["cuis"], pady=1, borderwidth = 1, relief=RIDGE)
                    lbl.grid(row= rowN, column=3, sticky="WE")        
                    lbl._values = x["_id"]
                    lbl.bind("<Double-Button-1>", self.gridCall)
                    lbl = tk.Label(gridframe, text= x["port"], pady=1, borderwidth = 1, relief=RIDGE)
                    lbl.grid(row= rowN, column=4, sticky="WE")        
                    lbl._values = x["_id"]
                    lbl.bind("<Double-Button-1>", self.gridCall)
                    bgc = "#FFFF00" if (x["state"] == 0) else "#EEEEEE"  
                    lbl = tk.Label(gridframe, text= "", bg= bgc, pady=1, borderwidth = 1, relief=RIDGE)
                    lbl.grid(row= rowN, column=5, sticky="WE")
                    rowN += 1
            if self.actApp == APPG:
                for x in listItems:
                    if x["_id"]:
                        lbl = tk.Label(gridframe, text= x["nom"], font= ('Segoe 9 underline'), fg="#0000FF", pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                        lbl.grid(row= rowN, column=0, sticky="WE")        
                        lbl._values = x["_id"]
                        lbl.bind("<Button-1>", self.showClub)
                    else:
                        lbl = tk.Label(gridframe, text= x["nom"], pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                        lbl.grid(row= rowN, column=0, sticky="WE")
                        lbl._values = [x["_id"]]
                        lbl.bind("<Double-Button-1>", self.webCall)
                    
                    lbl = tk.Label(gridframe, text= str(len(x["courses"])), pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                    lbl.grid(row= rowN, column=1, sticky="WE")        
                    lbl._values = [x["_id"]]
                    lbl.bind("<Double-Button-1>", self.webCall)
                    nT = 0
                    for t in x["courses"]:
                        nT += t["TROUS"]
                    lbl = tk.Label(gridframe, text= str(nT), pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                    lbl.grid(row= rowN, column=2, sticky="WE")        
                    lbl._values = [x["_id"]]
                    lbl.bind("<Double-Button-1>", self.webCall)
                    lbl = tk.Label(gridframe, text= x["adresse"], pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                    lbl.grid(row= rowN, column=3, sticky="WE")        
                    lbl._values = [x["_id"]]
                    lbl.bind("<Double-Button-1>", self.webCall)
                    if x["url_ville"] != "":
                        lbl = tk.Label(gridframe, text= x["municipal"], font= ('Segoe 9 underline'), fg="#0000FF", pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                        lbl.grid(row= rowN, column=4, sticky="WE")        
                        lbl._values = [x["_id"], x["url_ville"]]
                        lbl.bind("<Button-1>", lambda event, val=1: self.webCall(event, val))
                    else:
                        lbl = tk.Label(gridframe, text= x["municipal"], pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                        lbl.grid(row= rowN, column=4, sticky="WE")  
                        lbl._values = [x["_id"]]
                        lbl.bind("<Double-Button-1>", self.webCall)
                    
                    rid=x["region"]
                    reg = next(x for x in self.comboData if x["_id"] == rid )
                    
                    lbl = tk.Label(gridframe, text= reg["Nom"], pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                    lbl.grid(row= rowN, column=5, sticky="WE")   
                    lbl._values = [x["_id"]]
                    lbl.bind("<Double-Button-1>", self.webCall)
                    #pdb.set_trace()
                    rowN += 1                
  

    def webCall(self, e, val = 0):
        id = e.widget._values
        if val:
            url = id[val]
        else:
            url = "https://cdore.ddns.net/ficheClub.html?data=" + str(id[val])
        
        cdc.showWebURL(url)
        

        
    def gridCall(self, e):
        id = e.widget._values
        #print(str(id))
        rec = self.data.getReccette(id)
        winEdit = wr.editerRecette(self, (rec)[0], EDITOK)

    def resetForm(self):
        self.keyword.delete(0, END)
        self.keyword.insert(0, "")
        self.indIngr.set(1)
        self.comboCat.current(0)
        self.keyword.focus()
        
    def add_input_frame(self, mainFrame):

        formframe = tk.Frame(mainFrame)
        #pdb.set_trace()
        if self.actApp == APPR:
            comboLbl = 'Catégorie:'
            ind_lbl = '(rechercher parmi les ingrédients)'
        if self.actApp == APPG:
            comboLbl = 'Région:'
            ind_lbl = '(rechercher parmi les villes)'
        

        # Mots clés recherche
        ttk.Label(formframe, text='Critères', font=('Segoe 10 bold')).grid(column=0, row=0, sticky=tk.W)
        
        ttk.Label(formframe, text='Mots clés:').grid(column=0, row=1, sticky=tk.W)
        self.keyword = ttk.Entry(formframe, width=30)
        self.keyword.focus()
        self.keyword.grid(column=1, row=1, sticky=tk.W)
        self.keyword.bind("<Return>", self.getDataList)
        #self.keyword.bind('<Button-3>',popup) # Bind a func to right click
        cdc.menuEdit(self.win, self.keyword)
        
        button = cdc.RoundedButton(formframe, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.resetForm)
        button.create_text(12,11, text="x", fill="black", font=('Helvetica 15 '))
        button.grid(column=2, row=1)
        Hovertip(button,"Blanchir le formulaire")
        
        self.indIngr = IntVar()
        self.indIngr.set(1)
        ind_check = ttk.Checkbutton(
            formframe,
            text=ind_lbl,
            variable=self.indIngr,
            onvalue=1,
            offvalue=0)
        
        ind_check.grid(column=1, row=2, sticky=tk.W, padx=5, pady=3)
        
        # Combo Categorie

        ttk.Label(formframe, text= comboLbl).grid(column=0, row=4, sticky=tk.W)
        combo = ttk.Combobox(
            formframe,
            state="readonly",
            values=[""]
            )

        combo.grid(column=1, row=4, sticky=tk.W)
        self.comboCat = combo
        
        if self.data.isConnect:
            self.loadCombo()
            initInfo = self.readConfFile()
            self.setDefault(initInfo)

        for widget in formframe.winfo_children():
            widget.grid(padx=5, pady=5)
            
        if self.actApp == APPG and self.data.isConnect:
            ttk.Button(formframe, text='Parties', command=self.getGames).grid(column=2, row=4)

        return formframe

    def makeBackup_db(self):
        answer = False        
        collections = []
        if self.actServ == VSERV :
            app = cdc.logonWin(self.win)
            res = app.showLogonBD()
            #print("makeBackup_db" + str(res))
            if not res is None:
                answer = self.data.connectTo(self.actServ, self.actApp, res)
                if answer:
                    database = self.data.data
                    collections = database.list_collection_names()
                else:
                    self.win.objMainMess.showMess("Échec de l'authentification!")
                self.data.connectTo(self.actServ, self.actApp)
        else:
            answer = askyesno(title='Exporter', message='Exporter les données ? ')
        database = self.data.data
        if answer:
            self.pb = cdc.progressBarObj(self.pbFrame)
            self.pb.showBar()
            self.win.objMainMess.showMess("Exportation des données: \n", "I")
            
            #pdb.set_trace()
            if len(collections) == 0:
                collections = database.list_collection_names()
            percent = int(100 / len(collections))
            cwd = os.getcwd()
            buppath = cwd + "/" + BUPDIR            
            if not os.path.exists(BUPDIR):
                os.makedirs(buppath)

            for i, collection_name in enumerate(collections):
                self.pb.progress(percentVal = percent)
                time.sleep(0.5)
                #pdb.set_trace()
                col = getattr(database,collections[i])
                collection = col.find()
                data = list(collection)
                jsonName = collection_name + ".json"
                jsonpath = BUPDIR + jsonName
                with io.open(jsonpath, 'w', encoding='utf-8-sig') as fout:
                    fout.write(str(data))
                    fout.close()
                self.win.objMainMess.addMess(jsonName + ", ", "I")
            self.win.objMainMess.addMess("\nCOMPLÉTÉ: " + buppath, "I")
            self.pb.kill()

    def loadBackup_db(self):
        answer = False        
        collections = []
        if self.actServ == VSERV :
            app = cdc.logonWin(self.win)
            res = app.showLogonBD()
            #pdb.set_trace()
            if not res is None:
                answer = self.data.connectTo(self.actServ, self.actApp, res)
                #answer = self.data.connectTo(self.actServ, self.actApp)
                if answer:
                    database = self.data.data
                    collections = database.list_collection_names()
                else:
                    self.win.objMainMess.showMess("Échec de l'authentification!")
                self.data.connectTo(self.actServ, self.actApp)
        else:    
            answer = askyesno(title='Importer', message='Importer les données ? ')
        database = self.data.data
        
        if answer:
            self.pb = cdc.progressBarObj(self.pbFrame)
            self.pb.showBar()
            if len(collections) == 0:
                collections = database.list_collection_names()
            percent = int(100 / len(collections))
            if not os.path.exists(BUPDIR):
                self.win.objMainMess.showMess("Répertoire des fichiers absent: " + BUPDIR)
            else:
                self.win.objMainMess.showMess("Importation des données: \n", "I")
                for i, collection_name in enumerate(collections):
                    self.pb.progress(percentVal = percent)
                    time.sleep(0.5)
                    col = getattr(database,collections[i])
                    jsonName = collection_name + ".json"
                    jsonpath = BUPDIR + jsonName
                    if os.path.exists(jsonpath):
                        try:
                            f = open(jsonpath, encoding='utf-8-sig')
                            cache = f.read()
                            f.close()
                            #pdb.set_trace()
                            data = eval(cache)
                            res = col.delete_many({})
                            res = col.insert_many(data)
                            self.win.objMainMess.addMess(jsonName + ", ", "I")
                        except ValueError:
                            
                            return
                    else:
                        self.win.objMainMess.addMess(jsonName + " ABSENT, ", "I")
                self.win.objMainMess.addMess("\nCOMPLÉTÉ", "I")
                self.pb.kill()

        
    def getGames(self):
        #pdb.set_trace()
        if self.winGame is None or self.winGame.isDestroy:
            self.winGame = wg.listGames(self)
        else:
            self.winGame.winDim()

    def getUsers(self):
        #pdb.set_trace()
        if self.winUsers is None or self.winUsers.isDestroy:
            if self.actApp == APPG:
                wu.APPICON = GOLFICON
            if self.actApp == APPR:
                wu.APPICON = RECICON
            self.winUsers = wu.listUsers(self)
        else:
            self.winUsers.winDim()

    def showClub(self, e):
        id = e.widget._values
        wg.showClubWin(self, id)

        
    def add_button_frame(self, mainFrame):

        formframe = tk.Frame(mainFrame)
        ttk.Button(formframe, text='Rechercher', command=self.getDataList).grid(column=0, row=0)
        ttk.Button(formframe, text='Fermer', command=self.closeRec).grid(column=0, row=4)
        ttk.Button(formframe, text="Quitter", command=mainFrame.quit).grid(column=0, row=5)

        for widget in formframe.winfo_children():
            widget.grid(padx=5, pady=5)

        return formframe

    def closeRec(self):
        for winR in self.childWin:
            winR.destroy()

    def login(self):
        dial = loginDialog(self.win, "Connecter : app - location", self)
        #dial.showDialog()

    def authentif(self):
        app = cdc.logonWin(self.win, self.data.data)
        userIdent = "" if self.user == "" else self.user[0]
        res = app.showAPPdialog(userIdent)
        if not res is None:
            self.user, self.userName, self.userRole, USER_ID = [res[0], res[1]], res[2], res[3], res[4]
            self.setConfFile()
            self.afficherTitre()
            set_userid(USER_ID)

    def changePass(self):
        app = cdc.logonWin(self.win, self.data.data)
        userIdent = "" if self.user == "" else self.user[0]
        res = app.showChangePassdialog(userIdent)
        
    def setGrid(self, listFrame):
        self.gridFrame = listFrame
        self.getDataList()


class dbaseObj():
    def __init__(self, *args, **kwargs):
        self.data = None
        self.dbase = ""
        self.appdbName = { APPG: APPGBD,
                            APPR: APPRBD}        
        self.server = {
            "Local": "mongodb://localhost:27017/",
            VSERV: ""
            }
        self.DBconnect = None
        self.isConnect = False

    def connectTo(self, Server = "Local", appName = APPR, userPass = None):
        #pdb.set_trace()
        self.dbase = self.appdbName[appName]
        if userPass is None:
            uri = self.server[Server]
        else:
            uri = """mongodb://%s:%s@cdore.ddns.net:6600/?authSource=admin&ssl=false"""  % (userPass[0], userPass[1])
        if Server == "Local":
            timeout = 2000
        else:
            timeout = 15000

        if self.isConnect:
            self.DBconnect.close()
            self.isConnect = False
        try:
            
            self.DBconnect = MongoClient(uri,socketTimeoutMS=timeout,
                        connectTimeoutMS=timeout,
                        serverSelectionTimeoutMS=timeout,)

            self.DBconnect.server_info()
            #print(str(self.DBconnect.server_info()))
            if "ok" in self.DBconnect.server_info():
                self.data = self.DBconnect[self.dbase]
                self.isConnect = True
        except:
            self.isConnect = False
        return self.isConnect

    def getUserInfo(self, ident):
        col = self.data.users
        dat = col.find({"courriel": ident})
        return list(dat)[0]

        
    def getCat(self, info = False):    
        col = self.data.categorie
        docs = col.find({})
        #res = (docs)
        return list(docs)

    def getReg(self, info = False):    
        col = self.data.regions
        docs = col.find({})
        #res = (docs)
        return list(docs)

    def searchRecettes(self, wrd = '', ingr = 0, cat = 0):

        def concatWord(field, word):
            req = []
            for w in word.split():
                req.append({field: {"$regex": '.*' + w + '.*'} })
            return {"$and": req }
            #{"$and": {"$elemMatch": req }}
        
        def searchString(qNom, qIngr, qCat, mode = 0):
            qT = []
            
            Fnom, Fingr = 'nom','ingr'
            if mode == 1:
                Fnom, Fingr = 'nomU','ingrU'
                qNom, qIngr = cdc.scanName(qNom), cdc.scanName(qIngr)
            if mode == 2:
                Fnom, Fingr = 'nomP','ingrP'
                qNom, qIngr = phonetics.metaphone(qNom), phonetics.metaphone(qIngr)

            if qNom != '' and qIngr != '':
                q1 = {"$or": [ concatWord(Fnom, qNom) , concatWord(Fingr, qIngr) ]}
                qT.append(q1)
            else:
                if qNom != '':
                    q1 = concatWord(Fnom, qNom)
                if qIngr != '':
                    q1 = concatWord(Fingr, qIngr) 
                if 'q1' in locals():
                    qT.append(q1)
            
            if qCat != 0:
                q2 = {'cat._id': qCat}
            else:
                q2 = {"_id": {"$ne": 0}}
            qT.append(q2)

            #qT.append({"state": 1 })

            return { "$and": qT }

        # Begin function

        qNom, qIngr, qCat = '', '', None
        qNom = wrd
        if ingr == 1:
            qIngr = wrd
        qCat = cat

        col = self.data.recettes
        query = searchString(qNom, qIngr, qCat)
        
        fields = {"_id": 1,"nom": 1, "cat": 1, "temp": 1, "cuis": 1, "port": 1, "state": 1}
        docs = col.find(query, fields).collation({"locale": "fr","strength": 1}).sort("nom")
        #print(query)
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
        #res=li
        res["data"]=li
        return (res)

    def searchClubs(self, wrd = '', ville = 0, region = 0):
       
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
            
        def searchString(qNom, qVille, qReg, mode = 0):
            qT = []

            Fnom, FVille = 'nom', 'municipal'
            if mode == 1:
                Fnom = 'nomU'
                qNom = cdc.scanName(qNom)
            if mode == 2:
                Fnom = 'nomP'
                qNom = phonetics.metaphone(qNom)           

            if qNom != '' and qVille != '':
                regxN = re.compile(qNom, re.IGNORECASE)
                regxV = re.compile(qVille, re.IGNORECASE)               
                q1 = {"$or": [ {"nom": {"$regex": regxN } } , {"municipal": {"$regex": regxV} }, concatWord(Fnom, qNom, "$and") , concatWord(FVille, qVille) ]}
                qT.append(q1)
            else:
                if qNom != '':
                    q1 = concatWord(Fnom, qNom, "$and")
                if qVille != '':
                    q1 = concatWord(FVille, qVille) 
                if 'q1' in locals():
                    qT.append(q1)
            
            if qReg != 0:
                q2 = {'region': qReg}
            else:
                q2 = {"region": {"$ne": 0}}
            qT.append(q2)

            #if dist != None:
            #    q3 = {"location": { "$near" : {"$geometry": { "type": "Point",  "coordinates": [ lng , lat ] }, "$maxDistance": dist }}};
            #    qT.append(q3)
            #print(qT)
            return { "$and": qT }

        # Begin function
        
        qNom, qVille, qReg = '', '', None
        qNom = wrd
        if ville == 1:
            qVille = wrd
        qReg = region        
        col = self.data.club
        
        query = searchString(qNom, qVille, qReg)

        docs = col.find(query).collation({"locale": "fr","strength": 1}).sort("nom")
        #print("MODE = 0 " + str(query))
        li = list(docs)
        res={}
        res["ph"] = False
        if not len(li) and qNom != "":
            query = searchString(qNom, qVille, qReg, 1)
            docs = col.find(query).sort("nom")
            #print("MODE = 1 " + str(query))
            li = list(docs)
            if not len(li) and qNom != "":
                query = searchString(qNom, qVille, qReg, 2)
                docs = col.find(query).collation({"locale": "fr","strength": 1}).sort("nom")
                li = list(docs)
                #print("MODE = 2 " + str(query))
                res["ph"] = True
        res["data"]=li
        return (res)
        
        
    def getRecList(self, info = ""): 
        col = self.data.recettes
        query = {}
        if info != "":
            query = {'$and': [{'cat.desc': info}]}
        fields = {"_id": 1,"nom": 1, "cat": 1, "temp": 1, "cuis": 1, "port": 1, "state": 1}
        docs = col.find(query, fields).collation({"locale": "fr","strength": 1}).sort("nom")

        res = (docs)
        return res        

    def getReccette(self, info = ""): 
        col = self.data.recettes
        query = {}
        if info != "":
            query = {'_id': info}
        #fields = {"_id": 1,"nom": 1, "cat": 1, "temp": 1, "cuis": 1, "port": 1, "state": 1}
        docs = col.find(query).collation({"locale": "fr","strength": 1}).sort("nom")

        res = (docs)
        return res      

    def saveRecette(self, oRec):
        col = self.data.recettes
        oID = oRec["_id"]
        doc = col.update_one({ '_id': oID}, { '$set': oRec },  upsert=True )
        return (doc.raw_result)

    def addRecette(self, oRec):
        col = self.data.recettes

        doc = col.insert_one(oRec, {"new":True})
        return ({'n': 0, 'ok': 1.0})
        
    def deleteRecette(self, oID):
        col = self.data.recettes

        doc = col.delete_one({"_id": oID })
        return (doc.raw_result)

        
class loginDialog(cdc.modalDialogWin):
    def createWidget(self):
        self.mainApp = self.obj
        self.pop.resizable(0, 0)
        self.actApp  = self.mainApp.actApp
        self.actServ = self.mainApp.actServ
        #pdb.set_trace()
        self.labAct = Label(self.dframe, text="Actuel : " + self.actApp + " - " + self.actServ, font=('Calibri 12 bold'), pady=5)
        self.labAct.grid(row=0, column=0, columnspan=2, sticky=EW)
        button1 = Button(self.dframe, text=APPR + " - " + LSERV, command= lambda: self.selectAppDB(APPR, LSERV), width=30, cursor="hand2")
        button1.grid(row=1, column=0, columnspan=2)
        button1.bind("<Double-Button-1>", self.setAppDB)  
        button2 = Button(self.dframe, text=APPR + " - " + VSERV, command= lambda: self.selectAppDB(APPR, VSERV), width=30, cursor="hand2")
        button2.grid(row=2, column=0, columnspan=2)
        button2.bind("<Double-Button-1>", self.setAppDB) 
        button3 = Button(self.dframe, text=APPG + " - " + LSERV, command= lambda: self.selectAppDB(APPG, LSERV), width=30, cursor="hand2")
        button3.grid(row=3, column=0, columnspan=2)
        button3.bind("<Double-Button-1>", self.setAppDB) 
        button4 = Button(self.dframe, text=APPG + " - " + VSERV, command= lambda: self.selectAppDB(APPG, VSERV), width=30, cursor="hand2")
        button4.grid(row=4, column=0, columnspan=2)
        button4.bind("<Double-Button-1>", self.setAppDB) 
        
        lab1 = Label(self.dframe, text=" ", font=('Calibri 1'))
        lab1.grid(row=5, column=0, columnspan=2)

        self.dframe.columnconfigure(0, weight=1)
        self.dframe.columnconfigure(1, weight=1)
        buttonC = ttk.Button(self.dframe, text="Ok", command=self.setAppDB, width=10)
        buttonC.grid(row=6, column=0) 
        buttonC = ttk.Button(self.dframe, text="Annuler", command=self.close, width=10)
        buttonC.grid(row=6, column=1) 
        lab1 = Label(self.dframe, text=" ", font=('Calibri 1'))
        lab1.grid(row=7, column=0, columnspan=2)
        
    def getPass(self):
        self.passf = tk.Frame(self.dframe)
        lab1 = Label(self.passf, text="Password: ", bg="white")
        lab1.grid(row=0, column=0)
        txt1 = ttk.Entry(self.passf)
        txt1.grid(row=0, column=1)
        txt1.config(show="*");
        self.passf.grid(row=3, column=0, columnspan=2, pady=5)
        txt1.focus_set()

    def selectAppDB(self, app, serv):
        self.actApp  = app
        self.actServ = serv
        self.labAct.config(text="Actuel = " + app + " - " + serv)
        
    def setAppDB(self, e = None):  
        self.close()
        self.mainApp.setApp(self.actServ, self.actApp)
        

def create_main_window():

    win = Tk()
    win.minsize(480,300)
    #win.resizable(0, 0)

    l = int(win.winfo_screenwidth() / 2)
    win.geometry(f"+{l}+100")

    master_form_find(win)
    win.mainloop()

if __name__ == "__main__": 
    if len(argv) > 1:
        arg = [x for x in argv]
        param = arg[1]
        if param.isnumeric():
            Pvalid = 260658 + datetime.datetime.today().day
            if int(param) == Pvalid:
                EDITOK = True
                wg.EDITOK = True
                
    create_main_window()
    
