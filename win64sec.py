# coding=utf-8
#https://stackoverflow.com/questions/71677889/create-a-scrollbar-to-a-full-window-tkinter-in-python
#https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import
#pyinstaller main.py --onefile --name test --icon test.ico --noconsole
#Mise à jour et sécurité/Sécurité Windows/Protection contre les virus/Gérer les paramètres/Protection en temps réel
#Scripts\pyinstaller win64MD.py --onefile --name golf --noconsole
#Scripts\pyinstaller  -F --add-data C:\Users\charl\AppData\Local\Programs\Python\Python39\tcl\tix8.4.3;tcl\tix8.4.3 code\win64MD.py --noconsole
#C:\Users\charl\AppData\Local\Programs\Python\Python39\Scripts
#https://pypi.org/project/jsoneditor/
#Built-In Roles
#https://www.mongodb.com/docs/manual/reference/built-in-roles/#mongodb-authrole-dbOwner

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

RECICON  = 'C:/Users/charl/github/cuisine/misc/favicon.ico'
RECICON  = "mongo.ico"
if not os.path.exists(RECICON):
    RECICON = ''


CONFFILE = "mongoSecur.conf"
LSERV   = "Local"
VSERV   = "Vultr"

BDSYSTEMLIST = ["", "admin", "local", "config"]

ACTIONLIST = [
{
	"resource" : {
			"db" : "config",
			"collection" : ""
	},
	"actions" : [
			"analyzeShardKey",
			"bypassDocumentValidation",
			"changeCustomData",
			"changePassword",
			"changeStream",
			"clearJumboFlag",
			"collMod",
			"collStats",
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
			"dropRole",
			"dropUser",
			"enableSharding",
			"find",
			"getDatabaseVersion",
			"getShardVersion",
			"grantRole",
			"indexStats",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"moveChunk",
			"planCacheRead",
			"refineCollectionShardKey",
			"remove",
			"reshardCollection",
			"revokeRole",
			"setAuthenticationRestriction",
			"splitChunk",
			"splitVector",
			"update",
			"viewRole",
			"viewUser"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.js"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"dbHash",
			"dbStats",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : ""
	},
	"actions" : [
			"analyzeShardKey",
			"bypassDocumentValidation",
			"changeCustomData",
			"changePassword",
			"changeStream",
			"clearJumboFlag",
			"collMod",
			"collStats",
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
			"dropRole",
			"dropUser",
			"enableSharding",
			"find",
			"getDatabaseVersion",
			"getShardVersion",
			"grantRole",
			"indexStats",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"moveChunk",
			"planCacheRead",
			"refineCollectionShardKey",
			"remove",
			"reshardCollection",
			"revokeRole",
			"setAuthenticationRestriction",
			"splitChunk",
			"splitVector",
			"update",
			"viewRole",
			"viewUser"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "system.js"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"dbHash",
			"dbStats",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : ""
	},
	"actions" : [
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
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.sessions"
	},
	"actions" : [
			"collStats",
			"dbStats",
			"getDatabaseVersion",
			"getShardVersion",
			"indexStats"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "system.replset"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "replset.election"
	},
	"actions" : [
			"bypassDocumentValidation",
			"collMod",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dropCollection",
			"find",
			"insert",
			"updateSearchIndex",
			"remove",
			"update"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "replset.minvalid"
	},
	"actions" : [
			"bypassDocumentValidation",
			"collMod",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dropCollection",
			"find",
			"insert",
			"updateSearchIndex",
			"remove",
			"update"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : "system.profile"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"convertToCapped",
			"createCollection",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "system.healthlog"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"dbHash",
			"dbStats",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.users"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropIndex",
			"dropSearchIndex",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.roles"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropIndex",
			"dropSearchIndex",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : "system.users"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead",
			"remove",
			"update"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.version"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.backup_users"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : "system.js"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"compactStructuredEncryptionData",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"dropIndex",
			"dropSearchIndex",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead",
			"remove",
			"renameCollectionSameDB",
			"update"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "settings"
	},
	"actions" : [
			"find",
			"insert",
			"update"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "tempusers"
	},
	"actions" : [
			"find"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "temproles"
	},
	"actions" : [
			"find"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.preimages"
	},
	"actions" : [
			"find",
			"remove"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.change_collection"
	},
	"actions" : [
			"find",
			"insert",
			"remove",
			"update"
	]
}
]

systemRole = ['read','readWrite','dbAdmin','dbOwner','userAdmin','clusterAdmin','clusterManager','clusterMonitor','hostManager','backup','restore','readAnyDatabase','readWriteAnyDatabase','userAdminAnyDatabase','dbAdminAnyDatabase','dbOwner','userAdmin','userAdminAnyDatabase','root']
        
class filterForm():
    def __init__(self, parent, textVar, callBack):
        formframe = Frame(parent, borderwidth=3, relief = SUNKEN)
        formframe.pack( fill=X, padx=50, pady=5)
        ttk.Label(formframe, text='Keyword:').grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
        self.keyword = tk.Entry(formframe, textvariable=textVar, width=20)
        self.keyword.focus()
        self.keyword.grid(column=1, row=0, sticky=tk.W)  
        self.keyword.bind("<Return>", callBack)        
        
        button = cdc.RoundedButton(formframe, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.resetForm)
        button.create_text(12,11, text="x", fill="black", font=('Helvetica 15 '))
        button.grid(column=2, row=0, padx=30, pady=5)
        #Hovertip(button,"Blanchir le formulaire")        
        ttk.Button(formframe, text='Search', command=callBack).grid(column=3, row=0, padx=5, pady=5)
        
    def resetForm(self):
        self.keyword.delete(0, END)
        self.keyword.insert(0, "")

class master_form_find():
    def __init__(self, mainWin, *args, **kwargs):
        self.win = mainWin
        self.data = dbaseObj()
        self.userPass = ["", ""]
        self.userRole = ""
        self.roleList = [] 
        self.actServ  = LSERV
        self.keyWordRole = StringVar()
        self.keyWordUser = StringVar() 
        """
        initInfo = self.readConfFile()
        if "init" in initInfo: 
            self.actServ  = initInfo["init"] 
        """
        self.childWin = []

        self.gridFrame = None
        self.usersFrame = None

        self.setApp(self.actServ)

    def quitter(self, e):
        self.win.quit
    
    def setApp(self, serv):

        self.actServ  = serv
        #self.win.update_idletasks() 
        self.win.title(self.actServ)
            
        self.closeRec()
        slavelist = self.win.slaves()
        for elem in slavelist:
            elem.destroy()
        
        
        # Création du menu
        zoneMenu = Frame(self.win)
        zoneMenu.pack(fill=X, anchor=W)
        menuFichier = Menubutton(zoneMenu, text='File', width='10', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        menuFichier.grid(row=0,column=0)
        menuEdit = Button(zoneMenu, text='Close', width='10', font= ('Segoe 9 bold'), pady=1, borderwidth=2, relief = RAISED, command=self.closeRec)  
        menuEdit.grid(row=0,column=1)    
        menuEdit = Button(zoneMenu, text='Quit', width='10', font= ('Segoe 9 bold'), pady=1, borderwidth=2, relief = RAISED, command=self.win.quit)  #, command=self.win.quit  , Postcommand=self.win.quit
        menuEdit.grid(row=0,column=2)
        
        menu_file = Menu(menuFichier, tearoff = 0)
        menu_file.add_cascade(label='Connect to...', command = self.login)   #, activebackground='lightblue', activeforeground='black'
        menu_file.add_separator()
        menu_file.add_cascade(label='Sign in...', command = self.authentif)

        menuFichier.configure(menu=menu_file)            
        
        # Progress bar frame
        self.pbFrame = tk.Frame(self.win)
        self.pbFrame.pack(fill=X)

        # Zone de message
        self.win.objMainMess = cdc.messageObj(self.win)
        self.win.objMainMess.showMess("Conecting...")
        self.win.update_idletasks() 

        app = cdc.logonWin(self.win)
        res = app.showAdminUswerBD()
        isConnected = False
        if not res is None:
            self.userPass = res
            self.setConfFile()
            isConnected = self.data.connectTo(self.actServ, res)
            #pdb.set_trace()

        self.win.objMainMess.clearMess()    

        if isConnected:
            self.afficherTitre()
        else:
            messagebox.showinfo(
                title="Not connected",
                message=f"Please select another connection.")
            self.win.title(self.actServ + " : Not connected.")

        # Onglets
        tab_setup = ttk.Notebook(self.win)

        tabRoles = LabelFrame(tab_setup, text = " Roles ", font=('Calibri 12 bold'))
        tab_setup.add(tabRoles, text = "    Roles    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)

        tabUsers = LabelFrame(tab_setup, text = " Users ", font=('Calibri 12 bold'))
        tab_setup.add(tabUsers, text = "    Users    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)        
        

        filterForm(tabRoles, self.keyWordRole, self.getRoles)
        self.gridFrame = cdc.VscrollFrame(tabRoles)
        self.gridFrame.pack(expand= True, fill=BOTH)            
        self.getRoles()
        
        filterForm(tabUsers, self.keyWordUser, self.getUsers)        
        self.usersFrame = cdc.VscrollFrame(tabUsers)
        self.usersFrame.pack(expand= True, fill=BOTH)            
        self.getUsers()
        
        self.win.geometry("550x500")        

    
    def afficherTitre(self):
        self.win.title( self.actServ + " : Connected " + self.userPass[0])
    

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
        
        initInfo["init"] = self.actServ
        initInfo[(self.actServ)] = {}
        initInfo[(self.actServ)]["roleKeyword"] = self.keyWordRole.get()
        initInfo[(self.actServ)]["userKeyword"] = self.keyWordUser.get()

        initInfo[(self.actServ)]["userPass"] = self.userPass
        
      

        with open(CONFFILE, 'w', encoding='utf-8') as f:
            f.write(str(initInfo))
            #f.close()
        

    def getUsers(self, userName = None, pos = None):
        #pdb.set_trace()
        if self.data.data is None:
            return        
        dat = self.data.data.system.users
        res=dat.find()
        self.usersDataList=list(res)
        slavelist = self.usersFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy()         
        usersframe = tk.Frame(self.usersFrame.interior)
        usersframe.pack(expand= True, side=LEFT, fill=X, padx=10)
        
        userNameIndex = -1
        for index in range(len(self.usersDataList)):
            data = self.usersDataList[index]
            #print(data)
            data.pop("userId")
            data.pop("credentials")
            if data["user"] == userName:
                userNameIndex = index
            #pdb.set_trace()
            if not self.keyWordUser.get() or self.keyWordUser.get().upper() in data["user"].upper():            
                Button(usersframe, text=' ... ', command= lambda index=index: self.editUser(index), font=('Calibri 15 bold')).grid(row=index, column=0)
                formatted_data = json.dumps(data, indent=4)
                nlines = formatted_data.count('\n')
                text_box = tk.Text(usersframe, height= nlines+1)
                text_box.grid(row= index, column=1, sticky="WE")             
                text_box.insert(tk.END, formatted_data)
                text_box.config( state="disabled")
        self.usersFrame.scroll(0)
        if userNameIndex > -1:
            self.editUser(userNameIndex, pos)
        #jsoneditor.editjson(data)

        
    def getRoles(self, userRole = None, pos = None):
        
        if self.data.data is None:
            return
        dat = self.data.data.system.roles
        res=dat.find()
        if res is None:
            return
        self.rolesDataList=list(res)
        #pdb.set_trace()
        slavelist = self.gridFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy()      
            
        gridframe = tk.Frame(self.gridFrame.interior)
        gridframe.pack(expand= True, side=LEFT, fill=X, padx=10)

        userRoleIndex = -1
        for index in range(len(self.rolesDataList)):
            data = self.rolesDataList[index]
            self.roleList.append(data["role"])
            #pdb.set_trace()
            if data["role"] == userRole:
                userRoleIndex = index            
            if not self.keyWordRole.get() or self.keyWordRole.get().upper() in data["role"].upper():
                Button(gridframe, text=' ... ', command= lambda index=index: self.editRole(index), font=('Calibri 15 bold')).grid(row=index, column=0)
                formatted_data = json.dumps(data, indent=4)
                nlines = formatted_data.count('\n')            
                text_box = tk.Text(gridframe, height= nlines+1)
                text_box.grid(row= index, column=1, sticky="WE") 
                text_box.insert(tk.END, formatted_data)
                text_box.config( state="disabled")
        self.gridFrame.scroll(0)
        if userRoleIndex > -1:
            self.editRole(userRoleIndex, pos)
            
        return len(self.rolesDataList)

    def editRole(self, index = None, pos = None):
        #pdb.set_trace()
        editRoleWin(self, self.rolesDataList[index], pos)

    def editUser(self, index = None, pos = None):
        #pdb.set_trace()
        editUserWin(self, self.usersDataList[index], pos)
    

    def closeRec(self):
        for winR in self.childWin:
            winR.destroy()
        #self.destroy()

    def login(self):
        dial = loginDialog(self.win, "Connecter : app - location", self)
        dial.showDialog()

    def authentif(self):
        app = cdc.logonWin(self.win, self.data.data)
        userIdent = "" if self.userPass[0] == "" else self.userPass[0]
        res = app.showAPPdialog(userIdent)
        if not res is None:
            self.user, self.userName, self.userRole, USER_ID = [res[0], res[1]], res[2], res[3], res[4]
            self.setConfFile()
            self.afficherTitre()

    
class editRoleWin():
    def __init__(self, mainWin, roleData, pos):
        self.mainObj = mainWin
        self.data = mainWin.data
        self.roleData = roleData
        self.pos = pos
        self.roleName = self.roleData["role"]
        self.actionsList = None
        #self.bdSystemCollections = None
        self.userActionsList = self.roleData["privileges"][0]["actions"]
        self.addSystemPriv = False
        self.showRoleWin()
      
        
    def close(self):
        self.pop.destroy()

    def save(self):
        res = None
        db = self.data.data
        
        revokeArr = []
        for act in self.userActionsList:
            if self.var_list[self.actionsList.index(act)].get() == 0:
                revokeArr.append(act)
        if len(revokeArr):
            res = db.command({"revokePrivilegesFromRole": self.roleName, "privileges": [{"resource": {"db": self.comboBD.get(), "collection" : self.comboCol.get()}, "actions": revokeArr}]})

        grantArr = []
        for act in self.actionsList:
            if self.var_list[self.actionsList.index(act)].get() == 1:
                grantArr.append(act)
        if len(grantArr):
            res = db.command({"grantPrivilegesToRole": self.roleName, "privileges": [{"resource": {"db": self.comboBD.get(), "collection" : self.comboCol.get()}, "actions": grantArr}]})            

        self.refreshRoles(res)

    def delete(self):
        answer = askyesno(title='Suppression',
            message='Supprimer le rôle : ' + self.roleName)
        if answer:       
            db = self.data.data
            res = db.command({"dropRole": self.roleName})
            if res["ok"]:
                self.objMess.showMess("Enregistré!", type = "I")
                self.mainObj.getRoles()
                self.close()
            else:
                self.objMess.showMess(str(res))             

    def addRole(self):
        self.menuFichier.destroy()
        self.menuPriv.destroy()
        self.newRoleName = ttk.Entry(self.formFrame, width=20)
        self.newRoleName.focus()
        self.newRoleName.grid(column=1, row=0, sticky=tk.W)
        ttk.Button(self.butFrame, text='Enregistrer', command=self.createRole).grid(row=0, column=0) 
        self.comboBD.current(0)
        self.comboCol.current(0)
        self.setPriv()

    def createRole(self):
        #roleData = {}
        grantArr = []
        for act in self.actionsList:
            if self.var_list[self.actionsList.index(act)].get() == 1:
                grantArr.append(act)
        
        priv = {}
        priv["resource"] = { "db": self.comboBD.get(), "collection": self.comboCol.get() }
        priv["actions"] = grantArr

        db = self.data.data
        res = db.command({"createRole": self.newRoleName.get(), "privileges": [priv], "roles": []})
        if res["ok"]:
            self.objMess.showMess("Enregistré!", type = "I")
            ind = self.mainObj.getRoles()
            self.mainObj.editRole(ind-1)
            self.close()
        else:
            self.objMess.showMess(str(res))        

    def delPriv(self):
        answer = askyesno(title='Suppression',
            message='Supprimer le privilege : {' + "db: " + self.comboBD.get() + ", collection: " + self.comboCol.get() + " }")
        if answer:     
            db = self.data.data
            res = db.command({"revokePrivilegesFromRole": self.roleName, "privileges": [{"resource": {"db": self.comboBD.get(), "collection" : self.comboCol.get()}, "actions": self.actionsList}]})
            self.refreshRoles(res)
    
    def refreshRoles(self, res):
        if res["ok"]:
            self.mainObj.getRoles(self.roleName, [self.pop.winfo_x(), self.pop.winfo_y()])
            self.close()
        else:
            self.objMess.showMess(str(res))         
    
    def do(self):
        self.mainObj.keyWordRole.set(self.roleName) 
    
    def showRoleWin(self):
        #print(self.roleData)

        self.pop = tk.Toplevel(self.mainObj.win)
        self.pop.geometry("400x560")
        self.pop.title("Modifier Role")
        #self.pop.iconbitmap(GOLFICON)   
        self.mainObj.childWin.append(self.pop)

        if not self.pos is None:
            self.pop.geometry(f"+{self.pos[0]}+{self.pos[1]}")
            
        self.objMess = cdc.messageObj(self.pop, height=15)

        # Form frame
        mainFrame = tk.Frame(self.pop)
        mainFrame.pack( fill=X, padx=10, pady=10)        
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)

        # Input

        self.formFrame = tk.Frame(mainFrame)
        self.formFrame.grid(column=0, row=0)        
        ttk.Label(self.formFrame, text=" role : ").grid(row=0, column=0, sticky=tk.W)
        identFrame = tk.Frame(self.formFrame)
        identFrame.grid(row=0, column=1, sticky=tk.W, padx=1, pady=3)
        ttk.Label(identFrame, text=self.roleName).grid(row=0, column=0, sticky=tk.W, padx=1, pady=3)  
        button = cdc.RoundedButton(identFrame, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.do)
        button.create_text(12,11, text=" >", fill="black", font=('Helvetica 15 '))
        button.grid(row=0, column=1, padx=30, pady=5)
        #Hovertip(button,"Blanchir le formulaire")

        # Création du menu
        self.menuFichier = Menubutton(self.formFrame, text='role :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuFichier.grid(row=0,column=0, sticky=tk.W)
        menu_file = Menu(self.menuFichier, tearoff = 0)
        menu_file.add_cascade(label='Ajouter...', command = self.addRole) 
        menu_file.add_cascade(label='Supprimer...', command = self.delete) 
        self.menuFichier.configure(menu=menu_file)                 

        ttk.Label(self.formFrame, text="db :                        ").grid(row=1, column=0, sticky=tk.E, padx=5, pady=3)
        ttk.Label(self.formFrame, text="admin ").grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(self.formFrame, text="privileges :    [").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        
        # Création du menu privileges
        self.menuPriv = Menubutton(self.formFrame, text='privileges :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuPriv.grid(row=2,column=0, sticky=tk.W)
        menu_priv = Menu(self.menuPriv, tearoff = 0)
        menu_priv.add_cascade(label='Add system', command = self.addSystemPrivilege) 
        menu_priv.add_cascade(label='Supprimer...', command = self.delPriv) 
        self.menuPriv.configure(menu=menu_priv)        
        
        ttk.Label(self.formFrame, text="{  resources : { ").grid(row=3, column=0, sticky=tk.E, padx=30, pady=3)
        
        ttk.Label(self.formFrame, text= "db : ").grid( row=4, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboBD = ttk.Combobox(
            self.formFrame,
            state="readonly",
            values = self.data.dbList
            )
        self.comboBD.bind("<<ComboboxSelected>>", self.setPriv)
        self.comboBD.grid( row=4, column=1, sticky=tk.W)
        #pdb.set_trace()
        self.comboBD.current( self.data.dbList.index(self.roleData["privileges"][0]["resource"]["db"]) )
        
        ttk.Label(self.formFrame, text= "collection : ").grid( row=5, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboCol = ttk.Combobox(
            self.formFrame,
            state="readonly",
            values=[""]
            )
        self.comboCol.bind("<<ComboboxSelected>>", self.setPriv)
        self.comboCol.grid( row=5, column=1, sticky=tk.W)      
        ttk.Label(self.formFrame, text="} , ").grid(row=6, column=0, sticky=tk.W, padx=45, pady=3)
        ttk.Label(self.formFrame, text="actions : [").grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=50, pady=3)
        #pdb.set_trace()


        
        # Button        
        self.butFrame = tk.Frame(mainFrame)
        self.butFrame.grid(column=1, row=0)

        ttk.Button(self.butFrame, text='Enregistrer', command=self.save).grid(row=0, column=0)        
        ttk.Button(self.butFrame, text='Annuler', command=self.close).grid(row=1, column=0, pady=5)
        
        # Grid list frame
        self.actionsFrame = cdc.VscrollFrame(self.pop)
        self.actionsFrame.pack(expand= True, fill=BOTH)
        
        

        footFrame = tk.Frame(self.pop)
        footFrame.pack( fill=X )
        ttk.Label(footFrame, text="]").grid(row=0, column=0, sticky=tk.W, padx=70, pady=0)
        ttk.Label(footFrame, text="}").grid(row=1, column=0, sticky=tk.W, padx=45, pady=0)
        ttk.Label(footFrame, text="]").grid(row=2, column=0, sticky=tk.W, padx=25, pady=0)
        self.setPriv(setCol = True)

    def addSystemPrivilege(self, event = None):
        self.addSystemPriv = True
        ttk.Label(self.formFrame, text="System privilege").grid(row=2, column=1, sticky=tk.W, padx=5, pady=3) 
        self.comboBD.current(0)
        self.menuPriv.destroy()
        self.setPriv(setCol = True)
        self.objMess.showMess("Add system privilege", "I")
        
    def setPriv(self, event = None, setCol = False):

        colList = []
        if self.comboBD.get() not in BDSYSTEMLIST: # Si valeur "bd" n'est pas dans la liste system
            colList = self.data.colList[self.comboBD.get()].copy()
        if not "" in colList:
            colList.insert(0,"")
        self.comboCol.config(values=colList) 
            
        privileges = self.roleData["privileges"]
        if setCol and len(colList)  and not self.addSystemPriv: # Si la collection est à initialiser et qu'on est pas en mode ajout de privilège system
            self.comboCol.current( colList.index(self.roleData["privileges"][0]["resource"]["collection"]) )        
        
        slavelist = self.actionsFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy() 
        
        privObj = {"db" : "", "collection" : ""}          
        if self.addSystemPriv:  # Si ajout d'un privilege build in system
            #pdb.set_trace()
            dbList = BDSYSTEMLIST.copy()
            self.comboBD.config(values=dbList)
            #if setCol:
            #    self.comboBD.current(1)            
            colList = self.getSystemColl(self.comboBD.get())
            self.comboCol.config(values=colList)
            if setCol:
                self.comboCol.current(0)
            privObj = {"db" : self.comboBD.get(), "collection" : self.comboCol.get()}
        else:
            dbList = self.data.dbList.copy()
            self.comboBD.config(values=dbList)      
       
        existPriv = False
        self.userActionsList = []
        for priv in privileges:
            if priv["resource"]["db"] == self.comboBD.get() and priv["resource"]["collection"] == self.comboCol.get():
                existPriv = True
                self.userActionsList = priv["actions"]
            if not priv["resource"]["db"] in dbList:
                dbList.append(priv["resource"]["db"])
                self.comboBD.config(values=dbList)
            if not priv["resource"]["db"] in self.data.dbList and priv["resource"]["db"] == self.comboBD.get():
                colList.append(priv["resource"]["collection"])
                self.comboCol.config(values=colList)

        if not self.comboCol.get() in colList: # Si la collection n'est pas dans la liste
            self.comboCol.current(0)
            
        actPriv = '{ ' + 'db: "' + self.comboBD.get() + '" , collection: "' + self.comboCol.get() + '" }' 
        mess = ("Modify" if existPriv else "Add") + " privilege :\n" + actPriv
        self.objMess.showMess(mess, "I")
        
        self.actionsList = self.getActionList(privObj)
        self.var_list = []
        for ind, task in enumerate(self.actionsList):
            self.var_list.append(IntVar())
            if (task in self.userActionsList):
                self.var_list[ind].set(1)  
            ttk.Checkbutton(self.actionsFrame.interior, variable=self.var_list[ind], text=task).pack(anchor=W, padx=80) 

    def getActionList(self, resourceObj):
        privList = []
        for privObj in ACTIONLIST:
            if privObj["resource"] == resourceObj:
                privList = privObj["actions"]
        return privList

    def getSystemColl(self, sysBD):
        colList = []
        for privObj in ACTIONLIST:
            if privObj["resource"]["db"] == sysBD:
                colList.append(privObj["resource"]["collection"])
        return colList

class editUserWin():
    def __init__(self, mainWin, userData, pos):
        self.mainObj = mainWin
        self.data = mainWin.data
        self.userData = userData
        self.pos = pos
        self.userName = self.userData["user"]
        self.userRolesList = self.userData["roles"]
        self.showUserWin()
        
    def close(self):
        self.pop.destroy()

    def changePass(self):
        app = cdc.logonWin(self.pop)
        res = app.showChangeBDpass(self.userName)   
        if res:
            db = self.data.data
            result = db.command({"updateUser": res[0], "pwd": res[1]})
            if result["ok"]:
                self.objMess.showMess("Password changed for " + res[0], "I") 

    def delete(self):
        answer = askyesno(title='Suppression',
            message="Supprimer l'utilisateur : " + self.userName)
        if answer:       
            db = self.data.data
            res = db.command({"dropUser": self.userName})  
            self.refreshUsers(res)           

    def addUser(self):
        self.menuFichier.destroy()
        
        self.newUserName = ttk.Entry(self.formFrame, width=20)
        self.newUserName.focus()
        self.newUserName.grid(column=1, row=0, sticky=tk.W)
        self.addRole()
        ttk.Label(self.formFrame, text=" Password : ").grid(row=1, column=0, sticky=tk.W)
        self.newUserPass = ttk.Entry(self.formFrame, width=20)
        self.newUserPass.grid(row=1, column=1, sticky=tk.W)
        ttk.Button(self.butFrame, text='Enregistrer', command=self.createUser).grid(row=0, column=0)        

    def createUser(self):
        role = {"role": self.comboRole.get(), "db": self.comboBD.get()}
        db = self.data.data
        res = db.command({"createUser": self.newUserName.get(), "pwd": self.newUserPass.get(), "roles": [ role ] } )
        try:
            res = db.command("grantRolesToUser", self.userName, roles=[role])
            self.refreshUsers(res)
        except Exception as ex:
            self.objMess.showMess(str(ex))       

    def delRole(self):
        roleIndex = self.comboRole.current()
        role = {"role": self.comboRole.get(), "db": self.comboBD.get()}
        answer = askyesno(title='Suppression role',
            message="Supprimer le role : " + str(role))
        if answer:         
            db = self.data.data
            res = db.command("revokeRolesFromUser", self.userName, roles=[role])   
            self.refreshUsers(res)
                
    def addRole(self):

        sys_check = ttk.Checkbutton(
            self.formFrame,
            text="Built-In Roles",
            variable=self.sysRole,
            onvalue=1,
            offvalue=0)
        sys_check.grid(row=6, column=1, sticky=tk.W, padx=5, pady=3)  
        sys_check.bind("<Button-1>", self.changeRoleList)
        #pdb.set_trace()
        self.comboRole.config(values=self.mainObj.roleList)
        self.comboRole.unbind("<<ComboboxSelected>>")
        bdList = self.data.dbList
        bdList[0]='admin'
        self.comboBD.config(values=bdList)
        self.comboBD.unbind("<<ComboboxSelected>>")
        ttk.Button(self.butFrame, text='Enregistrer', command=self.grantRole).grid(row=0, column=0)    
        self.menuRole.destroy()

    def grantRole(self):
        role = self.comboRole.get()
        #pdb.set_trace()
        role = {"role": self.comboRole.get(), "db": self.comboBD.get()}
        db = self.data.data
        try:
            res = db.command("grantRolesToUser", self.userName, roles=[role])
            self.refreshUsers(res)
        except Exception as ex:
            self.objMess.showMess(str(ex))
    
    def refreshUsers(self, res):
        if res["ok"]:
            self.mainObj.getUsers(self.userName, [self.pop.winfo_x(), self.pop.winfo_y()])
            self.close()
        else:
            self.objMess.showMess(str(res))    
 
    def showUserWin(self):
        #print(self.userData)

        self.pop = tk.Toplevel(self.mainObj.win)
        self.pop.geometry("350x250")
        self.pop.title("Modifier User")
        #self.pop.iconbitmap(GOLFICON)   
        self.mainObj.childWin.append(self.pop)
        #pdb.set_trace()
        
        if not self.pos is None:
            self.pop.geometry(f"+{self.pos[0]}+{self.pos[1]}")  
        
        self.objMess = cdc.messageObj(self.pop, height=15)

        # Form frame
        mainFrame = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE)
        mainFrame.pack( fill=X, padx=10, pady=10)        
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)

        # Input

        self.formFrame = tk.Frame(mainFrame)
        self.formFrame.grid(column=0, row=0)        
        ttk.Label(self.formFrame, text=" User : ").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(self.formFrame, text=self.userName).grid(row=0, column=1, sticky=tk.W, padx=1, pady=3)  

        # Création du menu user
        self.menuFichier = Menubutton(self.formFrame, text='User :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuFichier.grid(row=0,column=0)
        menu_file = Menu(self.menuFichier, tearoff = 0)  
        menu_file.add_cascade(label='Change password...', command = self.changePass) 
        menu_file.add_cascade(label='Add user...', command = self.addUser) 
        menu_file.add_cascade(label='Remove user...', command = self.delete) 
        self.menuFichier.configure(menu=menu_file) 
        
        ttk.Label(self.formFrame, text="db :").grid(row=2, column=0, sticky=tk.E, padx=5, pady=3)
        ttk.Label(self.formFrame, text="admin ").grid(row=2, column=1, sticky=tk.W)

        ttk.Label(self.formFrame, text= "roles : ").grid( row=3, column=0, sticky=tk.E, padx=1, pady=3) 
        ttk.Label(self.formFrame, text= "[").grid( row=3, column=1, sticky=tk.W, padx=1, pady=3) 
        
        # Création du menu roles
        self.menuRole = Menubutton(self.formFrame, text='roles :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuRole.grid(row=3,column=0)
        menu_role = Menu(self.menuRole, tearoff = 0)
        menu_role.add_cascade(label='Ajouter...', command = self.addRole) 
        menu_role.add_cascade(label='Supprimer...', command = self.delRole) 
        self.menuRole.configure(menu=menu_role)        
        
        roleList = []
        dbList = []
        for role in self.userRolesList:
            roleList.append(role["role"])
            dbList.append(role["db"])
        
        ttk.Label(self.formFrame, text= "role : ").grid( row=4, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboRole = ttk.Combobox(
            self.formFrame,
            state="readonly",
            values = roleList
            )   #self.mainObj.roleList
        if roleList:
            self.comboRole.current(0)
        self.comboRole.bind("<<ComboboxSelected>>", self.setRole)
        self.comboRole.grid( row=4, column=1, sticky=tk.W)         
        ttk.Label(self.formFrame, text= "db : ").grid( row=5, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboBD = ttk.Combobox(
            self.formFrame,
            state="readonly",
            values = dbList
            )   #self.data.dbList
        if dbList:
            self.comboBD.current(0)
        self.comboBD.bind("<<ComboboxSelected>>", self.setRole)
        self.comboBD.grid( row=5, column=1, sticky=tk.W)

        self.sysRole = IntVar()

        ttk.Label(self.formFrame, text= "]").grid( row=7, column=0, sticky=tk.E, padx=1, pady=3) 
        
        # Button        
        self.butFrame = tk.Frame(mainFrame)
        self.butFrame.grid(column=1, row=0)
    
        ttk.Button(self.butFrame, text='Annuler', command=self.close).grid(row=1, column=0, pady=5)
        ttk.Button(self.butFrame, text='Test', command=self.test).grid(row=5, column=0, pady=5)
        
    def changeRoleList(self, event= None):
        if self.sysRole.get():
            self.comboRole.config(values=self.mainObj.roleList)
        else:
            self.comboRole.config(values=systemRole)

    def setRole(self, event = None):
        index = event.widget.current()
        self.comboRole.current(index)
        self.comboBD.current(index)

    def test(self):
        print(str(self.pop.winfo_x()) + "   y=" + str(self.pop.winfo_y()))
        
class dbaseObj():
    def __init__(self, *args, **kwargs):
        self.data = None
        self.dbList = []
        self.colList = {}
        self.dbase = ""
       
        self.server = {
            "Local": "mongodb://localhost:27017/",
            VSERV: "mongodb://cdore:925@cdore.ddns.net:6600/?authSource=admin&ssl=false"
            }
        self.DBconnect = None
        self.isConnect = False

    def connectTo(self, Server = "Local", userPass = None):
        #pdb.set_trace()

        self.dbase = 'admin'
        print(userPass)
        if userPass is None:
            uri = self.server[Server]
        else:
            uri = """mongodb://%s:%s@cdore.ddns.net:6600/?authSource=admin&ssl=false"""  % ("userAdmin", "111")

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

            if "ok" in self.DBconnect.server_info():
                dbs=self.DBconnect.list_database_names()
                dbs.remove('admin')
                dbs.remove('config')
                dbs.remove('local')                
                for db in dbs:
                    theDB = self.DBconnect[db]
                    self.colList[db] = theDB.list_collection_names()
                dbs.insert(0, "")
                self.dbList = dbs
                self.data = self.DBconnect[self.dbase]
                self.isConnect = True
        except:
            self.isConnect = False
        return self.isConnect

        
class loginDialog(cdc.modalDialogWin):
    def createWidget(self):
        self.mainApp = self.obj
        self.pop.resizable(0, 0)
        self.actServ = self.mainApp.actServ
        #pdb.set_trace()
        self.labAct = Label(self.dframe, text="Actuel : " + self.actServ, font=('Calibri 12 bold'), pady=5)
        self.labAct.grid(row=0, column=0, columnspan=2, sticky=EW)
        button1 = Button(self.dframe, text= LSERV, command= lambda: self.selectAppDB(LSERV), width=30, cursor="hand2")
        button1.grid(row=1, column=0, columnspan=2)
        button1.bind("<Double-Button-1>", self.setAppDB)  
        button2 = Button(self.dframe, text= VSERV, command= lambda: self.selectAppDB(VSERV), width=30, cursor="hand2")
        button2.grid(row=2, column=0, columnspan=2)
        button2.bind("<Double-Button-1>", self.setAppDB) 
        
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
    """    
    def getPass(self):
        self.passf = tk.Frame(self.dframe)
        lab1 = Label(self.passf, text="Password: ", bg="white")
        lab1.grid(row=0, column=0)
        txt1 = ttk.Entry(self.passf)
        txt1.grid(row=0, column=1)
        txt1.config(show="*");
        self.passf.grid(row=3, column=0, columnspan=2, pady=5)
        txt1.focus_set()
    """
    def selectAppDB(self, serv):
        self.actServ = serv
        self.labAct.config(text="Actuel = " + serv)
        
    def setAppDB(self, e = None):  
        self.close()
        self.mainApp.setApp(self.actServ)
        

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
    
