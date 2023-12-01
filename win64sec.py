# coding=utf-8
#https://stackoverflow.com/questions/71677889/create-a-scrollbar-to-a-full-window-tkinter-in-python
#https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import
#pyinstaller main.py --onefile --name test --icon test.ico --noconsole
#Mise à jour et sécurité/Sécurité Windows/Protection contre les virus/Gérer les paramètres/Protection en temps réel
#Scripts\pyinstaller win64MD.py --onefile --name golf --noconsole
#Scripts\pyinstaller  -F --add-data C:\Users\charl\AppData\Local\Programs\Python\Python39\tcl\tix8.4.3;tcl\tix8.4.3 code\win64MD.py --noconsole
#C:\Users\charl\AppData\Local\Programs\Python\Python39\Scripts
#https://pypi.org/project/jsoneditor/

import pdb
#; pdb.set_trace()

import sys, os, io, re, cgi, csv, urllib.parse
import json
import time 
import datetime
from sys import argv

from bson.json_util import dumps
from bson.json_util import loads

from tkinter import *
import tkinter as tk
from tkinter import * 
from tkinter import tix

from tkinter import messagebox, TclError, ttk
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
#from idlelib.tooltip import Hovertip

import urllib
import urllib.request

#import jsoneditor

import cdControl as cdc

# JSON
from bson import ObjectId
import json

# MongoDB
import pymongo
from pymongo import MongoClient

USER_ID = 0

RECICON  = 'C:/Users/charl/github/cuisine/misc/favicon.ico'
if not os.path.exists(RECICON):
    RECICON = ''

GOLFICON = 'C:/Users/charl/github/golf/images/golf.ico'
if not os.path.exists(GOLFICON):
    GOLFICON = ''

CONFFILE = "winApp.conf"
APPG    = "Golf"
APPGBD  = "golf"
APPR    = "Recettes"
APPRBD  = "resto"
LSERV   = "Local"
VSERV   = "Vultr"

actionsList = [
"analyze",
"analyzeShardKey",
"bypassDocumentValidation",
"changeCustomData",
"changePassword",
"changeStream",
"clearJumboFlag",
"collMod",
"collStats",
"compact",
"compactStructuredEncryptionData",
"configureQueryAnalyzer",
"convertToCapped",
"createCollection",
"createIndex",
"createRole",
"createSearchIndexes",
"createUser",
"dbHash",
"dbStats",
"dropCollection",
"dropDatabase",
"dropIndex",
"dropRole",
"dropSearchIndex",
"dropUser",
"enableProfiler",
"enableSharding",
"find",
"getDatabaseVersion",
"getShardVersion",
"grantRole",
"indexStats",
"insert",
"killCursors",
"listCachedAndActiveUsers",
"listCollections",
"listIndexes",
"listSearchIndexes",
"updateSearchIndex",
"moveChunk",
"planCacheIndexFilter",
"planCacheRead",
"planCacheWrite",
"refineCollectionShardKey",
"reIndex",
"remove",
"renameCollectionSameDB",
"reshardCollection",
"revokeRole",
"setAuthenticationRestriction",
"splitChunk",
"splitVector",
"storageDetails",
"update",
"validate",
"viewRole",
"viewUser"
]
        
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

        app = cdc.logonWin(self.win)
        res = app.showLogonBD()
        isConnected = False
        if not res is None:
            isConnected = self.data.connectTo(serv, appName, res)

        #isConnected = self.data.connectTo(serv, appName)
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
            
        self.getRoles()
        
        if self.actApp == APPR:
            self.win.geometry("550x500")
        if self.actApp == APPG:
            self.win.geometry("600x500")        

    
    def afficherTitre(self):
        self.win.title(self.actApp + " - " + self.actServ + " : Connecté " + ( "" if len(self.user) == 1 else " - " + self.userName))
    


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
        #self.keyword.bind("<Return>", self.do)
        #self.keyword.bind('<Button-3>',popup) # Bind a func to right click
        cdc.menuEdit(self.win, self.keyword)

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
            initInfo = self.readConfFile()
            #self.setDefault(initInfo)

        for widget in formframe.winfo_children():
            widget.grid(padx=5, pady=5)
            
        ttk.Button(formframe, text='Role', command=self.getRoles).grid(column=2, row=4)

        return formframe

    def getUsers(self):
        #pdb.set_trace()
        dat = self.data.data.system.users
        res=dat.find()
        self.dataList=list(res)
        #pdb.set_trace()
        
        gridframe = tk.Frame(self.gridFrame.interior)
        gridframe.pack(expand= True, side=LEFT, fill=X, padx=10)

        for index in range(len(self.dataList)):
            data = self.dataList[index]
            data.pop("userId")
            data.pop("credentials")
            #pdb.set_trace()
            Button(gridframe, text=' ... ', command= lambda index=index: self.editUser(index), font=('Calibri 15 bold')).grid(row=index, column=0)
            text_box = tk.Text(gridframe)
            text_box.grid(row= index, column=1, sticky="WE") 
            formatted_data = json.dumps(data, indent=4)
            text_box.insert(tk.END, formatted_data)
            text_box.config( state="disabled")
        #jsoneditor.editjson(data)
        print('getUsers')
        
    def getRoles(self):
        
        dat = self.data.data.system.roles
        res=dat.find()
        self.dataList=list(res)
        #pdb.set_trace()
        slavelist = self.gridFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy()        
        gridframe = tk.Frame(self.gridFrame.interior)
        gridframe.pack(expand= True, side=LEFT, fill=X, padx=10)

        for index in range(len(self.dataList)):
            data = self.dataList[index]
            #pdb.set_trace()
            Button(gridframe, text=' ... ', command= lambda index=index: self.editRole(index), font=('Calibri 15 bold')).grid(row=index, column=0)
            text_box = tk.Text(gridframe)
            text_box.grid(row= index, column=1, sticky="WE") 
            formatted_data = json.dumps(data, indent=4)
            text_box.insert(tk.END, formatted_data)
            text_box.config( state="disabled")
        #jsoneditor.editjson(data)
        print('getRoles')

    def editRole(self, index = None):
        #pdb.set_trace()
        
        userActionsList = self.dataList[index]["privileges"][0]["actions"]
        roleName = self.dataList[index]["role"]
        
        def selectAction(index, task):
            print(str(task))
        
        def close():
            self.pop.destroy()

        def save(roleName):
            db = self.data.data
            revokeArr = []
            for act in userActionsList:
                #print(str(self.var_list[actionsList.index(act)].get()))
                if self.var_list[actionsList.index(act)].get() == 0:
                    revokeArr.append(act)
            print(revokeArr)
            
            res = None
            if len(revokeArr):
                res = db.command({"revokePrivilegesFromRole": roleName, "privileges": [{"resource": {"db":"", "collection" : ""}, "actions": revokeArr}]})

            grantArr = []
            for act in actionsList:
                if self.var_list[actionsList.index(act)].get() == 1:
                    grantArr.append(act)
            print(grantArr)

            if len(grantArr):
                res = db.command({"grantPrivilegesToRole": roleName, "privileges": [{"resource": {"db":"", "collection" : ""}, "actions": grantArr}]})            

            if res["ok"]:
                self.objMess.showMess("Enregistré!", type = "I")
            else:
                self.objMess.showMess(str(res))
                
            #pdb.set_trace()
            self.getRoles()
            print("save")
            
        print(self.dataList[index])

        self.pop = tk.Toplevel(self.win)
        #self.pop.protocol('WM_DELETE_WINDOW',self.destroyRef)
        self.pop.geometry("250x500")
        self.pop.title("Parties")
        #self.pop.iconbitmap(GOLFICON)   
        
        self.objMess = cdc.messageObj(self.pop, height=25)

        # Form frame
        mainFrame = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE)
        mainFrame.pack( fill=X, padx=10, pady=10)        
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)

        # Input
        self.formFrame = tk.Frame(mainFrame)
        #self.formFrame.pack(fill=X, padx=5)
        self.formFrame.grid(column=0, row=0)        
        ttk.Label(self.formFrame, text="role : ").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(self.formFrame, text=roleName).grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)       
        ttk.Label(self.formFrame, text="actions : ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)

        # Button        
        self.butFrame = tk.Frame(mainFrame)
        self.butFrame.grid(column=1, row=0)

        ttk.Button(self.butFrame, text='Enregistrer', command= lambda roleName=roleName: save(roleName)).grid(row=0, column=0)        
        ttk.Button(self.butFrame, text='Annuler', command=close).grid(row=1, column=0, pady=5)
        
        # Grid list frame
        self.actionsFrame = cdc.VscrollFrame(self.pop)
        self.actionsFrame.pack(expand= True, fill=BOTH)
        
        self.var_list = []

        for ind, task in enumerate(actionsList):
            #print(str(ind))
            self.var_list.append(IntVar())
            if (task in userActionsList):
                self.var_list[ind].set(1)  
            ttk.Checkbutton(self.actionsFrame.interior, variable=self.var_list[ind],
                        text=task).pack(anchor=W)
 
        

    def editUser(self, index = None):
        #pdb.set_trace()
        db = self.data.data
        #res = db.command("grantRolesToUser", "cdore", roles=["makebup"])
        res = db.command("revokeRolesFromUser", "cdore", roles=["makebup"])
        
        print(self.dataList[index])
 
    def do(self):
        x=2
        
    def add_button_frame(self, mainFrame):

        formframe = tk.Frame(mainFrame)
        ttk.Button(formframe, text='Rechercher', command=self.do).grid(column=0, row=0)
        ttk.Button(formframe, text='Fermer', command=self.closeRec).grid(column=0, row=4)
        ttk.Button(formframe, text="Quitter", command=mainFrame.quit).grid(column=0, row=5)

        for widget in formframe.winfo_children():
            widget.grid(padx=5, pady=5)

        return formframe

    def closeRec(self):
        for winR in self.childWin:
            winR.destroy()
        #self.destroy()

    def login(self):
        dial = loginDialog(self.win, "Connecter : app - location", self)
        dial.showDialog()

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
        res = app.showChangePassdialog(USER_ID)
        


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
        #self.dbase = self.appdbName[appName]
        self.dbase = 'admin'
        if userPass is None:
            uri = self.server[Server]
        else:
            uri = """mongodb://%s:%s@cdore.ddns.net:6600/?authSource=admin&ssl=false"""  % ("")
            globals()["USER_ID"] = "CDadmin"
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

    win = tix.Tk()
    win.minsize(480,300)
    #win.resizable(0, 0)

    l = int(win.winfo_screenwidth() / 2)
    win.geometry(f"+{l}+100")

    master_form_find(win)
    win.mainloop()

if __name__ == "__main__": 
                
    create_main_window()
    
