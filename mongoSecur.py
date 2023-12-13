# coding=utf-8
#https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import
#pyinstaller main.py --onefile --name test --icon test.ico --noconsole
#Mise à jour et sécurité/Sécurité Windows/Protection contre les virus/Gérer les paramètres/Protection en temps réel
#Scripts\pyinstaller win64MD.py --onefile --name golf --noconsole
#Scripts\pyinstaller  -F --add-data C:\Users\charl\AppData\Local\Programs\Python\Python39\tcl\tix8.4.3;tcl\tix8.4.3 code\win64MD.py --noconsole
#C:\Users\charl\AppData\Local\Programs\Python\Python39\Scripts
#https://pypi.org/project/jsoneditor/
#Built-In Roles
#https://www.mongodb.com/docs/manual/reference/built-in-roles/#mongodb-authrole-dbOwner
#https://www.mongodb.com/docs/v3.4/tutorial/enable-authentication/
#/etc/mongod.conf     #/data/db
#security:
#	authorization: "enabled"

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
from tkinter import simpledialog
#from idlelib.tooltip import Hovertip

import urllib
import urllib.request

#import jsoneditor

import mongoRoles
import cdControl as cdc

# JSON
from bson import ObjectId
import json

# MongoDB
import pymongo
from pymongo import MongoClient

APPICON  = 'C:/Users/charl/github/cuisine/misc/favicon.ico'
APPICON  = "mongo.ico"
if not os.path.exists(APPICON):
    APPICON = ''

BDSYSTEMLIST = mongoRoles.bdSystemList
ACTIONLIST = mongoRoles.actionsList
BULTINROLELIST = mongoRoles.systemRole

CONFFILE = "mongoSecur.conf"
LOCALSERV= "localhost"
VSERV   = "Vultr"

        
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
        self.actServ  = None
        self.servers = []
        self.keyWordRole = StringVar()
        self.keyWordUser = StringVar() 

        initInfo = self.readConfFile()
        if "init" in initInfo: 
            self.actServ  = initInfo["init"] 

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
        self.win.iconbitmap(APPICON)
        
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

        isConnected = False
        """
        app = cdc.logonWin(self.win)
        res = app.showAdminUserBD()
        if not res is None:
            self.userPass = res
            self.setConfFile()
            isConnected = self.data.connectTo(self.actServ, res)
            #pdb.set_trace()
        """
        defInfo = self.setDefault()
        hostName = defInfo["host"] if "host" in defInfo else ""
        port = defInfo["port"] if "port" in defInfo else ""
        isConnected = self.data.connectTo(self.actServ, self.userPass, hostName=hostName, port=port)
        self.afficherTitre(isConnected)

        self.win.objMainMess.clearMess()    

        # Onglets
        tab_setup = ttk.Notebook(self.win)
        
        tabUsers = LabelFrame(tab_setup, text = " Users ", font=('Calibri 12 bold'))
        tab_setup.add(tabUsers, text = "    Users    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)           

        tabRoles = LabelFrame(tab_setup, text = " Roles ", font=('Calibri 12 bold'))
        tab_setup.add(tabRoles, text = "    Roles    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)

        filterForm(tabUsers, self.keyWordUser, self.getUsers)        
        self.usersFrame = cdc.VscrollFrame(tabUsers)
        self.usersFrame.pack(expand= True, fill=BOTH)            
        self.getUsers()     
        
        filterForm(tabRoles, self.keyWordRole, self.getRoles)
        self.gridFrame = cdc.VscrollFrame(tabRoles)
        self.gridFrame.pack(expand= True, fill=BOTH)            
        self.getRoles()
        
        self.win.geometry("550x500")        

    
    def afficherTitre(self, isConnected):
        if isConnected:
            self.win.title( self.actServ + " : Connected - " + self.userPass[0])
        else:
            self.win.title( self.actServ + " : Not connected.")
    

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
        if not self.actServ in initInfo:
            initInfo[(self.actServ)] = {}
            print("NEW-NEW-NEW")
        initInfo[(self.actServ)]["roleKeyword"] = self.keyWordRole.get()
        initInfo[(self.actServ)]["userKeyword"] = self.keyWordUser.get()
        initInfo[(self.actServ)]["userPass"] = self.userPass
        self.writeConfFile(initInfo)

    def writeConfFile(self, initInfo):
        with open(CONFFILE, 'w', encoding='utf-8') as f:
            f.write(str(initInfo))
            f.close()

    def setServerConfFile(self, param = None):
        #pdb.set_trace()
        initInfo = (self.readConfFile())
        if param["server"] is None:
            #pdb.set_trace()
            del initInfo[param["delServ"]]
            if initInfo["init"] == param["delServ"]:
                del initInfo["init"]
        else:
            if param["server"] != self.actServ and param["server"] not in initInfo:
                print("NEW")
                initInfo[param["server"]] = {}
                initInfo[param["server"]]["roleKeyword"] = ""
                initInfo[param["server"]]["userKeyword"] = ""
                initInfo[param["server"]]["userPass"] = ["", ""]
        
            initInfo[param["server"]]["host"] = param["host"]
            initInfo[param["server"]]["port"] = param["port"]
        self.writeConfFile(initInfo)
        print(initInfo)
        
    def setDefault(self, initInfo = None):
        actInfo = {}
        if initInfo is None:
            initInfo = (self.readConfFile())
        if self.actServ is None:
            self.actServ = LOCALSERV
        if not initInfo is None and self.actServ in initInfo:
            actInfo = initInfo[(self.actServ)]
            self.userPass = actInfo["userPass"]
            self.keyWordRole.set(actInfo["roleKeyword"])
            self.keyWordUser.set(actInfo["userKeyword"])
        return actInfo    
            
    def getUsers(self, userName = None, pos = None):
        #pdb.set_trace()
        slavelist = self.usersFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy() 
            
        if not self.data.isConnect or self.data.data is None:
            return   

        self.setConfFile()            
        dat = self.data.data.system.users
        res=dat.find()
        self.usersDataList=list(res)
        
        usersframe = tk.Frame(self.usersFrame.interior)
        usersframe.pack(expand= True, side=LEFT, fill=X, padx=10)

        if len(self.usersDataList) == 0:
            Button(usersframe, text='Create root user', command= self.createRoot, font=('Calibri 12 bold')).pack()
            #grid(row=0, column=0)
            
        userNameIndex = -1
        for index in range(len(self.usersDataList)):
            data = self.usersDataList[index]
            #print(data)
            if "userId" in data and "credentials" in data :
                data.pop("userId")
                data.pop("credentials")
            else:
                print("NOT userID and credentials")
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

    def createRoot(self):
        #pdb.set_trace()
        app = cdc.logonWin(self.win)
        res = app.showAdminUserBD()   
        
        if res:
            db = self.data.data
            result = db.command({"createUser": res[0], "pwd": res[1], "roles": [ {'role': 'root', 'db': 'admin'} ] } )
            #result = db.command({"updateUser": res[0], "pwd": res[1]})
            if result["ok"]:
                self.win.objMainMess.showMess("Root user created : " + res[0], "I") 
                self.getUsers()
    
    def getRoles(self, userRole = None, pos = None):

        slavelist = self.gridFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy()
        #pdb.set_trace()
        
        if not self.data.isConnect or self.data.data is None:
            return
        dat = self.data.data.system.roles
        res=dat.find()
        if res is None:
            return
        self.setConfFile()
        self.rolesDataList=list(res)
            
        gridframe = tk.Frame(self.gridFrame.interior)
        gridframe.pack(expand= True, side=LEFT, fill=X, padx=10)

        if len(self.rolesDataList) == 0:
            Button(gridframe, text='Create role', command= self.createRole, font=('Calibri 12 bold')).pack()

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

    def createRole(self):
        db = self.data.data
        result = db.command({"createRole": "Read", "privileges": [{"resource": {"db": "", "collection": ""}, "actions": ["find", "listCollections"]}], "roles": []})
        if result["ok"]:
            self.win.objMainMess.showMess("Role created : 'Read'" , "I") 
            self.getRoles()

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
        initInfo = (self.readConfFile())
        info = initInfo.keys()
        self.servers = []
        for k in info:
            if k != "init":
                self.servers.append(k)
        dial = loginDialog(self.win, "Connecter : app - location", self)
        dial.showDialog()

    def authentif(self):
        """
        app = cdc.logonWin(self.win, self.data.data)
        userIdent = "" if self.userPass[0] == "" else self.userPass[0]
        res = app.showAPPdialog(userIdent)
        if not res is None:
            self.user, self.userName, self.userRole, USER_ID = [res[0], res[1]], res[2], res[3], res[4]
            self.setConfFile()
            self.afficherTitre()
        """
        app = cdc.logonWin(self.win)
        res = app.showAdminUserBD(self.userPass[0])
        if not res is None:
            self.userPass = res
            self.setConfFile()
            self.setApp(self.actServ)

                
    
class editRoleWin():
    def __init__(self, mainWin, roleData, pos):
        self.mainObj = mainWin
        self.data = mainWin.data
        self.roleData = roleData
        self.pos = pos
        self.roleName = self.roleData["role"]
        self.actionsList = None
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
        answer = askyesno(title='Remove',
            message='Remove role : ' + self.roleName)
        if answer:       
            db = self.data.data
            res = db.command({"dropRole": self.roleName})
            if res["ok"]:
                self.objMess.showMess(self.roleName + " removed!", type = "I")
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
        answer = askyesno(title='Remove',
            message='Remove privilege : {' + "db: " + self.comboBD.get() + ", collection: " + self.comboCol.get() + " }")
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

        ttk.Button(self.butFrame, text='Save', command=self.save).grid(row=0, column=0)        
        ttk.Button(self.butFrame, text='Cancel', command=self.close).grid(row=1, column=0, pady=5)
        
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
        answer = askyesno(title='Remove',
            message="Remove user : " + self.userName)
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
        answer = askyesno(title='Remove role',
            message="Remove role : " + str(role))
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
    
        ttk.Button(self.butFrame, text='Cancel', command=self.close).grid(row=1, column=0, pady=5)
        ttk.Button(self.butFrame, text='Test', command=self.test).grid(row=5, column=0, pady=5)
        
    def changeRoleList(self, event= None):
        if self.sysRole.get():
            self.comboRole.config(values=self.mainObj.roleList)
        else:
            self.comboRole.config(values=BULTINROLELIST)

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
        self.DBconnect = None
        self.isConnect = False

    def connectTo(self, Server = LOCALSERV, userPass = None, hostName = "", port = ""):
        #pdb.set_trace()

        self.dbase = 'admin'
        
        uri = """mongodb://%s:%s@"""  % (userPass[0], userPass[1])
        uri += hostName + ":" + port + "/?authSource=admin&ssl=false"
        if userPass[0] == "":
            uri = "mongodb://" + hostName + ":" + port + "/"
        if hostName == LOCALSERV:
            uri = "mongodb://" + LOCALSERV + ":27017/"
            
        print(uri)
        if Server == LOCALSERV or hostName == LOCALSERV:
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
                for db in BDSYSTEMLIST:
                    if db != "" and db in dbs:
                        dbs.remove(db)                
                for db in dbs:
                    theDB = self.DBconnect[db]
                    self.colList[db] = theDB.list_collection_names()
                dbs.insert(0, "")
                self.dbList = dbs
                self.data = self.DBconnect[self.dbase]
                self.isConnect = True
        except Exception as ex:
            print(ex)
            self.isConnect = False
        return self.isConnect

        
class loginDialog(cdc.modalDialogWin):
    def createWidget(self):
        self.mainApp = self.obj
        self.pop.resizable(0, 0)
        self.actServ = self.mainApp.actServ
        #pdb.set_trace()
        self.labAct = Label(self.dframe, text="Actuel : " + self.actServ, font=('Calibri 12 bold'), pady=5)
        self.labAct.grid(row=0, column=0, columnspan=3, sticky=EW)
        
        if len(self.mainApp.servers) == 0:
            self.mainApp.servers.append(LOCALSERV)
        for ind, serv in enumerate(self.mainApp.servers):
            globals()["but" + str(ind)] = Button(self.dframe, text= serv, command= lambda serv=serv: self.selectAppDB(serv), width=30, cursor="hand2")
            globals()["but" + str(ind)].grid(row=ind+1, column=0, columnspan=3)
            globals()["but" + str(ind)].bind("<Double-Button-1>", self.setAppDB) 
        
        lab1 = Label(self.dframe, text=" ", font=('Calibri 1'))
        lab1.grid(row=5, column=0, columnspan=2)

        self.dframe.columnconfigure(0, weight=1)
        self.dframe.columnconfigure(1, weight=1)
        buttonC = ttk.Button(self.dframe, text="Ok", command=self.setAppDB, width=10)
        buttonC.grid(row=6, column=0) 
        buttonC = ttk.Button(self.dframe, text="Modify", command=self.modifyServ, width=10)
        buttonC.grid(row=6, column=1)
        buttonC = ttk.Button(self.dframe, text="Cancel", command=self.close, width=10)
        buttonC.grid(row=6, column=2)         
        lab1 = Label(self.dframe, text=" ", font=('Calibri 1'))
        lab1.grid(row=7, column=0, columnspan=2)

    def selectAppDB(self, serv):
        self.actServ = serv
        self.labAct.config(text="Actuel = " + serv)
        
    def setAppDB(self, e = None):  
        self.close()
        self.mainApp.setApp(self.actServ)
 
    def modifyServ(self, e = None):
        initInfo = self.mainApp.readConfFile()
        servInfo = {}
        servInfo[self.actServ] = initInfo[self.actServ]
        custom_dialog = modifyServerDialog(self.pop, servInfo)
        res = custom_dialog.result #Retourner les valeurs par le bouton Ok, sinon None 
        if not res is None:
            self.mainApp.setServerConfFile(res)
            self.close()


class modifyServerDialog(simpledialog.Dialog):
    def __init__(self, parent, optionalObject = None):
        self.parent = parent
        self.actServ = list(optionalObject.keys())[0]
        self.servInfo = optionalObject
        self.server = StringVar()
        self.host = StringVar()
        self.port = StringVar()
        self.servToRemove = ""
        
        simpledialog.Dialog.__init__(self, parent)

        
    def body(self, master):
        #pdb.set_trace()
        if "host" in self.servInfo[self.actServ]:
            self.host.set(self.servInfo[self.actServ]["host"])
        if "port" in self.servInfo[self.actServ]:
            self.port.set(self.servInfo[self.actServ]["port"])
        self.formframe = tk.Frame(master, borderwidth = 1, relief=RIDGE, padx=10, pady=10)
        self.formframe.grid(row=1)
        tk.Label(self.formframe, text="Server :").grid(row=0, column=0, sticky=E)
        tk.Label(self.formframe, text= self.actServ, font=('Calibri 12 bold')).grid(row=0, column=1, sticky=W)
        tk.Label(self.formframe, text= "Host : ").grid(row=1, column=0, sticky=E)
        self.entry = tk.Entry(self.formframe, textvariable = self.host, width=30)
        self.entry.grid(row=1, column=1)        
        tk.Label(self.formframe, text= "Port : ").grid(row=2, column=0, sticky=E)
        port = tk.Entry(self.formframe, textvariable = self.port, width=10)
        port.grid(row=2, column=1, sticky=W)        
        
        butframe = tk.Frame(self.formframe, padx=10, pady=10)
        butframe.grid(row=3, column=0, columnspan=2) 
        buttonC = ttk.Button(butframe, text="Add server", command=self.addServer, width=15)
        buttonC.grid(row=0, column=0, pady=5, padx=5) 
        buttonC = ttk.Button(butframe, text="Remove server", command=self.removeServer, width=15)
        buttonC.grid(row=0, column=1, pady=5, padx=5) 


    def addServer(self):
        serv = tk.Entry(self.formframe, textvariable = self.server, width=10)
        serv.grid(row=0, column=1, sticky=W)
        self.port.set("27017")

    def removeServer(self):
        answer = askyesno(title='Remove',
            message='Remove server : ' + self.actServ)
        if answer:
            self.servToRemove = self.actServ
            self.actServ = None
            self.apply()
            self.destroy()
    
    def validate(self):
        #self.connectArr.append(self.entry.get())
        #self.connectArr.append(self.passentry.get()) 
        if self.server.get() != "":
            self.actServ = self.server.get()
        
        return True
            
    def apply(self):
        # Cette méthode est appelée lorsque le bouton "OK" est cliqué
        resObj = {"server": self.actServ, "host": self.host.get(), "port": self.port.get()}
        if self.servToRemove != "":
            resObj["delServ"] = self.servToRemove
        self.result = resObj
        
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
    
