# coding=utf-8
#https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import
#pyinstaller main.py --onefile --name test --icon test.ico --noconsole
#Mise à jour et sécurité/Sécurité Windows/Protection contre les virus/Gérer les paramètres/Protection en temps réel
#Scripts\pyinstaller win64MD.py --onefile --name golf --noconsole
#Scripts\pyinstaller -F --add-data C:\Users\charl\AppData\Local\Programs\Python\Python312\Lib\site-packages\tkinterweb\tkhtml:. code/mongoSecur.py --collect-all tkinterweb --noconsole
#C:\Users\charl\AppData\Local\Programs\Python\Python39\Scripts
#https://pypi.org/project/jsoneditor/
#Built-In Roles
#https://www.mongodb.com/docs/manual/reference/built-in-roles/#mongodb-authrole-dbOwner
#https://www.mongodb.com/docs/v3.4/tutorial/enable-authentication/
#/etc/mongod.conf     #/data/db
#..\python mongoSecur.py
#openssl key
#cd  /etc/ssl
#sudo openssl req -newkey rsa:2048 -new -x509 -days 3650 -nodes -out mongodb-cert.crt -keyout mongodb-certcd.key
#sudo cat mongodb-certcd.key mongodb-cert.crt > mongodb.pem
#https://pymongo.readthedocs.io/en/stable/examples/tls.html#ocsp
#https://www.mongodb.com/docs/v7.0/tutorial/configure-x509-client-authentication/    *********à lire
#https://www.mongodb.com/docs/manual/core/security-x.509/
#https://dyma.fr/mongodb?campaignId=12643958796&device=c&utm_source=google&gad_source=2&gclid=EAIaIQobChMI2Njy3JLHgwMVYDfUAR1q6A_6EAAYASAAEgJHP_D_BwE

#https://stackoverflow.com/questions/41302023/how-security-in-mongodb-works-using-x-509-cert/75043317#75043317
#https://www.mongodb.com/docs/manual/tutorial/configure-ssl-clients/



"""
ÉTAPE 1
https://dev.to/ozgurozvaris/x509-certificate-authentication-tlsssl-connection-to-mongodb-1-2hik
Certificate Authority (CA)
With passphrase
openssl genrsa -des3 -out ca.key 2048
Without passphrase
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -days 3650 -subj '/CN=MyCA/OU=cd/O=cdore/L=Quebec/ST=QC/C=CA' -out ca.crt

Generating the server x.509 Certificate files. Run commands below
openssl req -newkey rsa:2048 -days 3650 -nodes -subj '/CN=localhost/OU=cd/O=cdore/L=Quebec/ST=QC/C=CA' -out server.csr -keyout server.key
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650 -extfile <(echo -e "keyUsage = digitalSignature, keyEncipherment\nextendedKeyUsage = clientAuth,serverAuth")
cat server.key server.crt > server.pem

Generating the client x.509 Certificate files. Run commands below
openssl req -newkey rsa:2048 -days 3650 -nodes -subj '/CN=x509user/OU=cd/O=cdore/L=Quebec/ST=QC/C=CA' -out client.csr -keyout client.key
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 3650 -extfile <(echo -e "keyUsage = digitalSignature, keyEncipherment\nextendedKeyUsage = clientAuth")
cat client.key client.crt > client.pem

CREATE USER
openssl x509 -in /home/cdore/CRT/server.pem -inform PEM -subject -nameopt RFC2253

https://www.mongodb.com/docs/v7.0/tutorial/enable-authentication/
https://www.mongodb.com/docs/manual/core/security-x.509/
https://www.mongodb.com/docs/manual/tutorial/configure-x509-client-authentication/#prerequisites
https://www.mongodb.com/docs/manual/tutorial/configure-x509-member-authentication/
https://www.mongodb.com/docs/drivers/go/current/fundamentals/auth/#std-label-golang-x509
https://www.mongodb.com/docs/manual/core/security-x.509/#std-label-client-x509-certificates-requirements

ÉTAPE 2

  tls:
     mode: allowTLS
     certificateKeyFile: /home/cdore/CRT/server.pem
     CAFile: /home/cdore/CRT/ca.crt


openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650 -extfile <(echo -e "keyUsage = digitalSignature, keyEncipherment\nextendedKeyUsage = clientAuth, serverAuth") -extensions v3_req -extfile <(
cat << EOF
[ v3_req ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = cdore.ddns.net
DNS.2 = cdore.servehttp.com
IP.3 = 70.52.73.58
IP.4 = 192.168.2.239
EOF
)

certutil -addstore root c:\tmp\rootca.cer
certmgr.msc
"""
import pdb
#; pdb.set_trace()
# unt [line]
import sys, os, io, re, csv, platform, urllib.parse
from urllib.parse import urlparse, parse_qs
import json
import time 
import datetime
from sys import argv

from bson.json_util import dumps
from bson.json_util import loads

#from tkinter import *
import tkinter as tk
from tkinter import * 

from tkinter import messagebox, TclError, ttk
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
from tkinter import simpledialog
from tkinter import filedialog
from idlelib.tooltip import Hovertip
#import tksvg
import pyperclip as cp
import urllib
import urllib.request
#from xml.etree import ElementTree as ET
from PIL import ImageTk, Image
from tkinterweb import HtmlFrame
#import jsoneditor

import mongoRoles
import cdControl as cdc
import editObject as eob
import mongoSecHelp as mh

# JSON
from bson import ObjectId
import json

# MongoDB
import pymongo
from pymongo import MongoClient

APPICON  = 'C:/Users/charl/AppData/Local/Programs/Python/Python39/code/mongo.ico'
#C:\Users\charl\AppData\Local\Programs\Python\Python39\
#APPICON  = "mongo.ico"
if not os.path.exists(APPICON):
    APPICON = ''

BDSYSTEMLIST = mongoRoles.bdSystemList
ACTIONLIST = mongoRoles.actionsList
ACTIONCLUSTER = mongoRoles.clusterResActions
BULTINROLELIST = mongoRoles.systemRole
FSVGCOPY = "SVGCOPY.txt"
SVGCOPY = """
<svg fill="#000000" height="800px" width="800px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
	 viewBox="0 0 330 330" xml:space="preserve">
<g>
	<path d="M35,270h45v45c0,8.284,6.716,15,15,15h200c8.284,0,15-6.716,15-15V75c0-8.284-6.716-15-15-15h-45V15
		c0-8.284-6.716-15-15-15H35c-8.284,0-15,6.716-15,15v240C20,263.284,26.716,270,35,270z M280,300H110V90h170V300z M50,30h170v30H95
		c-8.284,0-15,6.716-15,15v165H50V30z"/>
	<path d="M155,120c-8.284,0-15,6.716-15,15s6.716,15,15,15h80c8.284,0,15-6.716,15-15s-6.716-15-15-15H155z"/>
	<path d="M235,180h-80c-8.284,0-15,6.716-15,15s6.716,15,15,15h80c8.284,0,15-6.716,15-15S243.284,180,235,180z"/>
	<path d="M235,240h-80c-8.284,0-15,6.716-15,15c0,8.284,6.716,15,15,15h80c8.284,0,15-6.716,15-15C250,246.716,243.284,240,235,240z
		"/>
</g>
</svg>
"""
#https://www.svgrepo.com/svg/24801/copy
#https://www.mongodb.com/docs/manual/reference/log-messages/
"""
id
ctx
msg
"""
LOG_severity = ["", " I", " F", " E", " W"]
LOG_component = ["","ACCESS","COMMAND","CONTROL","ELECTION","FTDC","GEO","INDEX","INITSYNC","JOURNAL","NETWORK","QUERY","RECOVERY","REPL","REPL_HB","ROLLBACK","SHARDING","STORAGE","TXN","WRITE","WT","WTBACKUP","WTCHKPT","WTCMPCT","WTEVICT","WTHS","WTRECOV","WTRTS","WTSLVG","WTTIER","WTTS","WTTXN","WTVRFY","WTWRTLOG"]

CONFFILE = "mongoSecur.conf"
LOCALSERV= "localhost"
VSERV   = "Vultr"


def getID(strID):
    if len(strID) < 5:
        return int(strID)
    else:    
        return ObjectId(strID)

def winChildPos(winObj):
    winObj.mainObj.win.update_idletasks()                                                             ##update_idletasks
    w=winObj.pop.winfo_width()
    h=winObj.pop.winfo_height() + 2
    
    #pdb.set_trace()
    winObj.pop.geometry(f"{w}x{h}") 
    my = winObj.mainObj.win.winfo_x() - w - 2
    my = 0 if my < 0 else my
    mt = winObj.mainObj.win.winfo_y()
    winObj.pop.geometry(f"+{my}+{mt}")        
    #winObj.pop.geometry(f"+{my}+0")
    winObj.pop.update_idletasks()
    winObj.pop.attributes('-topmost', True)
    winObj.pop.attributes('-topmost', False)


        
class filterForm():
    def __init__(self, parent, textVar, callBack, nextcallBack = None):
        self.textVar = textVar
        self.totalCount = StringVar()
        if nextcallBack is None:
            padXform = 50
        else:
            padXform = 5
        self.formframe = Frame(parent, borderwidth=3, relief = RIDGE )  #SUNKEN
        self.formframe.pack( fill=X, padx=padXform, pady=5)
        
        self.mainBlock = Frame(self.formframe)
        self.mainBlock.pack()
        
        ttk.Label(self.mainBlock, text='Keyword :').grid(column=0, row=1, padx=5, pady=5, sticky=tk.W)
        self.keyword = tk.Entry(self.mainBlock, textvariable=textVar, width=30)
        cdc.menuEdit(parent, self.keyword )
        Hovertip(self.keyword,"Enter keyword for search")
        self.keyword.focus()
        self.keyword.grid(column=1, row=1, sticky=tk.W)  
        self.keyword.bind("<Return>", callBack)        
        
        button = cdc.RoundedButton(self.mainBlock, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.resetForm)
        button.create_text(12,11, text="x", fill="black", font=('Helvetica 15 '))
        button.grid(column=2, row=1, padx=15)
        Hovertip(button,"Clear the form")        
        self.searchBut = ttk.Button(self.mainBlock, text='Search', command=callBack)
        self.searchBut.grid(column=3, row=1, padx=5)
        Hovertip(self.searchBut,"Search in logs") 
        ttk.Label(self.mainBlock, textvariable=self.totalCount, font= ('Segoe 10 bold'), width=12).grid(column=4, row=1, padx=3, pady=5, sticky=tk.E)
        if not nextcallBack is None:
            nextBut = ttk.Button(self.mainBlock, text='>', width=3, command=nextcallBack)
            nextBut.grid(column=5, row=1)  #, padx=1
            Hovertip(nextBut,"Nexts records in logs") 
            

    def resetForm(self):
        self.keyword.delete(0, END)
        self.keyword.insert(0, "")
        
    def affTot(self, val):
        #print(val)
        self.totalCount.set(val)
        
        
class filterLogForm(filterForm):
    def __init__(self, parent, textVar, callBack, nextcallBack, parentWin):
        filterForm.__init__(self, parent, textVar, callBack, nextcallBack)
        self.win = parentWin
        self.callBack = callBack
        self.nextcallBack = nextcallBack
        self.sEqu = StringVar()
        self.sRes = StringVar()
        self.cEqu = StringVar()
        self.cRes = StringVar()
        self.chxID = IntVar()
        self.chxCtx = IntVar()
        self.chxMes = IntVar()
        self.foundMes = StringVar()
        
        secondBlock = Frame(self.formframe)
        secondBlock.pack()
        
        ttk.Label(secondBlock, text='Severity').grid(row=0, column=0, padx=2, pady=3, sticky=tk.W)
        self.sEqu.set("==")
        self.s_Equ = tk.Label(secondBlock, textvariable=self.sEqu, borderwidth=2, relief = RAISED)
        self.s_Equ.grid(row=0, column=1, sticky=tk.W, padx=0, pady=3) 
        self.s_Equ._values = 1
        Hovertip(self.s_Equ," == : equal \n <> : not equal ")
        self.s_Equ.bind("<Button-1>", self.changeEqual)
        
        self.comboSev = ttk.Combobox(
            secondBlock,
            width=2,
            textvariable=self.sRes,
            state="readonly",
            values = LOG_severity
            )
        Hovertip(self.comboSev," I : Informational \n F : Fatal\n E : Error\n W : Warning")
        self.comboSev.current(0)
        self.comboSev.grid(row=0, column=2, sticky=tk.W, padx=0, pady=3)
        
        ttk.Label(secondBlock, text='Comp.').grid(row=0, column=3, padx=2, pady=3, sticky=tk.W)
        self.cEqu.set("==")
        self.c_Equ = tk.Label(secondBlock, textvariable=self.cEqu, borderwidth=2, relief = RAISED)
        self.c_Equ.grid(row=0, column=4, sticky=tk.W, padx=0, pady=3) 
        self.c_Equ._values = 1
        Hovertip(self.c_Equ," == : equal \n <> : not equal ")
        self.c_Equ.bind("<Button-1>", self.changeEqual)     
        
        self.comboComp = ttk.Combobox(
            secondBlock,
            width=11,
            textvariable=self.cRes,
            state="readonly",
            values = LOG_component
            )
        Hovertip(self.comboComp," component : category of logged event ")
        self.comboComp.current(0)
        self.comboComp.grid(row=0, column=5, sticky=tk.W, padx=0, pady=3) 

        checkID = ttk.Checkbutton(
            secondBlock,
            text="id",
            variable=self.chxID,
            onvalue=1,
            offvalue=0)
        checkID.grid(row=0, column=6, sticky=tk.W, padx=0, pady=3)
        Hovertip(checkID," Keyword == specific log events id  ")
        checkCtx = ttk.Checkbutton(
            secondBlock,
            text="context",
            variable=self.chxCtx,
            onvalue=1,
            offvalue=0)
        checkCtx.grid(row=0, column=7, sticky=tk.W, padx=0, pady=3) 
        Hovertip(checkCtx," Keyword is IN Thread's name of log's statement ")
        checkMes = ttk.Checkbutton(
            secondBlock,
            text="message",
            variable=self.chxMes,
            onvalue=1,
            offvalue=0)
        checkMes.grid(row=0, column=8, sticky=tk.W, padx=0, pady=3) 
        Hovertip(checkMes," Keyword is IN Log output message  ")
        
        foundLabel = tk.Label(secondBlock, textvariable=self.foundMes, font= ('Segoe 9 bold'), fg="#0000FF", width=11)
        foundLabel.grid(row=0, column=9, padx=0, pady=3, sticky=tk.EW)
        Hovertip(foundLabel," Click to show search criteria  ")
        foundLabel.bind("<Button-1>", self.getLogCritere)
        
        ttk.Button(self.mainBlock, text='Search', command=self.execCallBack).grid(column=3, row=1, padx=5)
        nextB = ttk.Button(self.mainBlock, text='>', width=3, command=self.execNextcallBack)
        nextB.grid(column=5, row=1)  #, padx=1
        Hovertip(nextB,"Next results")
        #command= lambda index=index: self.editUser(index)
        
    def execCallBack(self):
        #pdb.set_trace()
        self.callBack(sRes=self.sRes.get().strip() , sEqu=self.s_Equ, cRes=self.cRes.get(), cEqu=self.c_Equ, chxCtx = self.chxCtx.get(), chxMes = self.chxMes.get(), chxID = self.chxID.get())

    def execNextcallBack(self):
        self.nextcallBack(sRes=self.sRes.get(), sEqu=self.s_Equ, cRes=self.cRes.get(), cEqu=self.c_Equ, chxCtx = self.chxCtx.get(), chxMes = self.chxMes.get(), chxID = self.chxID.get())

    def getLogCritere(self, event):
        txtLog = ""
        if self.sRes.get():
            txtLog += "\t" + "severity " + self.sEqu.get() + " '" + self.sRes.get() + "'\n"
        if self.cRes.get(): 
            txtLog += "\t" + ("and \n\t" if len(txtLog) else "") + "component " + self.cEqu.get() + " '" + self.cRes.get() + "'\n"
        if self.chxID.get(): 
            txtLog += "\t" + ("and \n\t" if len(txtLog) else "") + self.textVar.get() + " == id\n"                 
        if self.chxCtx.get(): 
            txtLog += "\t" + ("and \n\t" if len(txtLog) else "") + "'" + self.textVar.get() + "' IN ctx\n"
        if self.chxMes.get(): 
            txtLog += "\t" + ("and \n\t" if len(txtLog) else "") + "'" + self.textVar.get() + "' IN msg\n" 
        if not txtLog :
            txtLog = "\tNo criteria"
        showLogCritere(self.win, "Search Criteria : ", txtLog, geometry = "300x250", modal = False)

    def changeEqual(self, event):
        var=str(event.widget['textvariable'])
        if event.widget._values:
            tk.StringVar(name=var, value='<>')
            event.widget._values = 0
        else:
            tk.StringVar(name=var, value='==')
            event.widget._values = 1
        #print(str(event.widget._values))

    def affFound(self, val = None):
        #print(val)
        if val is None:
            self.foundMes.set("no filter")
        else:
            self.foundMes.set(str(val) + " found")

    def resetForm(self):
        self.keyword.delete(0, END)
        self.keyword.insert(0, "")
        self.comboSev.current(0)
        self.comboComp.current(0)
        self.chxCtx.set(0)
        self.chxMes.set(0)
        self.chxID.set(0)
        self.objMainMess.clearMess()
        
class master_form_find():
    def __init__(self, mainWin, *args, **kwargs):
        self.win = mainWin
        self.data = dbaseObj()
        self.userPass = ["", ""]
        self.userRole = ""
        self.roleList = [] 
        self.actServ  = None
        self.servers = []
        self.Database = StringVar()
        self.keyWordRole = StringVar()
        self.keyWordUser = StringVar() 
        self.keyWordLog = StringVar()
        self.keyWordEdit = StringVar()        
        self.hostInfo = False

        initInfo = self.readConfFile()
        if "init" in initInfo: 
            self.actServ  = initInfo["init"] 

        self.childWin = []

        self.gridRolesFrame = None
        self.gridUsersFrame = None
        self.usersDataList = None
        self.rolesDataList = None
        self.rolesNamesList = None
        self.logsDataList = None

        self.setApp(self.actServ)

    def changeDatabase(self, event = None):
        self.getUsers()
        self.getRoles()
        if self.tabSelection == 4:
            self.editData()
        #print( "Change to : "  + self.Database.get()) 

    def quitter(self, e):
        self.win.quit

    def readDBcolList(self):
        self.DBlist = []
        self.COLlist = {}
        try:
            dbs=self.data.DBconnect.list_database_names()
            for db in BDSYSTEMLIST:
                if db != "" and db in dbs:
                    dbs.remove(db)   
            #pdb.set_trace()
            for db in dbs:
                theDB = self.data.DBconnect[db]
                #pdb.set_trace()
                colList = theDB.list_collection_names()
                colList.sort()
                self.COLlist[db] = colList
            dbs.insert(0, "")
            self.DBlist = dbs
        except pymongo.errors.OperationFailure as ex1:
            self.objMainMess.showMess(ex1.details.get('errmsg', ''))
            self.objMainMess.addMess("\n\nUser with listCollections action on database privilege is required.")
            return        
    
    def setApp(self, serv, userPass = None):

        self.actServ  = serv
        self.win.title(self.actServ)
        self.win.iconbitmap(APPICON)
        self.win.geometry("600x500")
        self.win.minsize(width = 600, height = 500)
        self.tabSelection = 0

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


        menubar = tk.Menu()
        self.edit_menu = tk.Menu(menubar, tearoff=False)
        

        
        menu_file = Menu(menuFichier, tearoff = 0)
        menu_file.add_command(label='Connect to...', command = self.login)   #, activebackground='lightblue', activeforeground='black'
        menu_file.add_separator()
        menu_file.add_command(label='Sign in...', command = self.authentif)
        menu_file.add_separator()
        menu_file.add_command(label='Connection string...', command = self.showURI)
        
        menu_file.add_separator()
        menu_file.add_cascade(menu=self.edit_menu, label="Edit")
        
        menu_file.add_separator()
        menu_file.add_command(label='Help...', command = self.showHelp)
        
        menuFichier.configure(menu=menu_file) 
        self.menu_file = menu_file
        
        #menu_file.entrycget("Edit", "state")
        #menu_file.entryconfigure("Edit", state="disabled")
        #menu_file.insert_cascade(2,menu=edit_menu, label="Edit")
        #pdb.set_trace()
 
        # Progress bar frame
        self.pbFrame = tk.Frame(self.win)
        self.pbFrame.pack(fill=X)

        # Zone de message
        self.objMainMess = cdc.messageObj(self.win, height=25)
        self.objMainMess.showMess("Connecting...")
        isConnected = False

        servInfo = self.setDefault()
        #print(str(servInfo))
        userPassword = userPass
        if userPass is None:
            userPass = self.userPass
        tmpFrame = tk.Frame(self.win)  #, bg="red"
        tmpFrame.pack(expand=1, fill=BOTH)
        self.win.update_idletasks()
        
        self.userPass = userPass
        isConnected = self.data.connectTo(self.actServ, userPass, servInfo)
        self.objMainMess.clearMess() 
        if userPassword:    # New authentication
            if isConnected:
                self.objMainMess.showMess(str(userPass[0]) + " connected on " + self.actServ, "I")
            else:
                self.objMainMess.showMess(str(userPass[0]) + " not connected.")  
        self.afficherTitre(isConnected, servInfo)
        
        tmpFrame.pack_forget()
        # Database form
        dbFrame = tk.Frame(self.win)
        dbFrame.pack(fill=X)
        dbForm = tk.Frame(dbFrame)
        dbForm.pack()
        
        #pdb.set_trace()
        dt = ttk.Label(dbForm, text= "Database : ", font=('Calibri 12 bold'))
        dt.grid( row=0, column=0, padx=5, sticky="WE")

        self.comboDatabase = ttk.Combobox(
            dbForm,
            textvariable=self.Database,
            state="readonly"
            )

        self.comboDatabase.grid( row=0, column=1)        
        self.initDBcombo()
 
        # Onglets
        tab_setup = ttk.Notebook(self.win)
        tab_setup.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.tabObject = tab_setup
        
        tabUsers = LabelFrame(tab_setup, text = " Users ", font=('Calibri 12 bold'))
        tab_setup.add(tabUsers, text = "    Users    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)           

        tabRoles = LabelFrame(tab_setup, text = " Roles ", font=('Calibri 12 bold'))
        tab_setup.add(tabRoles, text = "    Roles    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)

        tabLogs = LabelFrame(tab_setup, text = " Logs ", font=('Calibri 12 bold'))
        tab_setup.add(tabLogs, text = "    Logs    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)

        tabHost = LabelFrame(tab_setup, text = " Host ", font=('Calibri 12 bold'))
        tab_setup.add(tabHost, text = "    Host    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)

        tabEdit = LabelFrame(tab_setup, text = " Edit ", font=('Calibri 12 bold'))
        tab_setup.add(tabEdit, text = "    Edit    ")
        tab_setup.pack(expand=1, fill = "both", padx = 10)
        
        self.usersFilter = filterForm(tabUsers, self.keyWordUser, self.getUsers)        
        self.gridUsersFrame = cdc.VscrollFrame(tabUsers)
        self.gridUsersFrame.pack(expand= True, fill=BOTH)            
        self.getUsers()
        
        self.rolesFilter = filterForm(tabRoles, self.keyWordRole, self.getRoles)
        self.gridRolesFrame = cdc.VscrollFrame(tabRoles)
        self.gridRolesFrame.pack(expand= True, fill=BOTH)            
        self.getRoles()

        self.logsFilter = filterLogForm(tabLogs, self.keyWordLog, self.getLogs, self.nextLogList, self.win)
        self.gridLogsFrame = cdc.VscrollFrame(tabLogs)
        self.gridLogsFrame.pack(expand= True, fill=BOTH)            
        
        self.gridHostFrame = cdc.VscrollFrame(tabHost)
        self.gridHostFrame.pack(expand= True, fill=BOTH)        

        self.editDataObj = editDatabase( self, tabEdit)
        self.editFilter = filterForm(tabEdit, self.keyWordEdit, self.editDataObj.showRecReset, self.editDataObj.showRec)
        secondBlock = Frame(tabEdit)
        secondBlock.pack()       
        self.editDataObj.initObj(self.editFilter)
        self.addBut = ttk.Button(secondBlock, text='Add data ➕', command=self.editDataObj.addNewRecord, width=15)    #, command=addNewRecord
        self.addBut.grid(column=0, row=0, padx=5) 
        self.importBut = ttk.Button(secondBlock, text='Import data 📥', command=self.editDataObj.importRecords, width=15)   
        self.importBut.grid(column=1, row=0, padx=5)
        self.exportBut = ttk.Button(secondBlock, text='Export data 📤', command=self.editDataObj.exportRecords, width=15)  
        self.exportBut.grid(column=2, row=0, padx=5)
        self.removeBut = ttk.Button(secondBlock, text='Remove data 🗑', command=self.editDataObj.delAllRecord, width=15)
        self.removeBut.grid(column=3, row=0, padx=5)
        
        self.edit_menu.add_command(label='Create database', command=lambda: self.editAction(1) )
        self.edit_menu.add_command(label='Remove database', command=lambda: self.editAction(2) ) #command = self.editAction(2) )   #
        self.edit_menu.add_command(label='Create collection', command=lambda: self.editAction(3) )
        self.edit_menu.add_command(label='Remove collection', command=lambda: self.editAction(4) )
        self.edit_menu.add_command(label='Rename collection', command=lambda: self.editAction(5) )

    def editAction(self, action):
        #pdb.set_trace()
        if self.tabObject.index(self.tabObject.select()) != 4:
            self.tabObject.select(4)
        if action == 1:
            self.editDataObj.createDatabase()
        elif action == 2:
            self.editDataObj.dropDatabase()
        elif action == 3:
            self.editDataObj.createCollection()
        elif action == 4:
            self.editDataObj.dropCollection()            
        elif action == 5:
            self.editDataObj.renameCollection()            

    def initDBcombo(self, dbName = None):
        self.comboDatabase.unbind("<<ComboboxSelected>>")
        dbList = self.DBlist.copy()
        if dbList:
            dbList[0] = "admin"
            dbList.insert(0, "All")
            self.comboDatabase.configure(values=dbList) 
            self.comboDatabase.current(0)
            self.comboDatabase.bind("<<ComboboxSelected>>", self.changeDatabase)        
            if dbName:
                self.comboDatabase.current(dbList.index(dbName))
                self.changeDatabase()
        
    def afficherTitre(self, isConnected, servInfo):
        #pdb.set_trace()
        self.DBlist = []
        typ = "TLS" if "tls" in servInfo else ""
        if isConnected:
            auth = self.data.data.command({"connectionStatus" : 1})
            #db.set_trace()
            if len(auth['authInfo']['authenticatedUsers']):
                userObj = auth['authInfo']['authenticatedUsers'][0]
            else:
                userObj = {}
            if 'db' in userObj and 'external' in  userObj['db']:
                self.userPass[0] = userObj['user']
                self.menu_file.delete(2)
                self.menu_file.delete(1)
            self.win.title( self.actServ + " : " + typ + " Connected - " + self.userPass[0])
            self.readDBcolList()
        else:
            self.win.title( self.actServ + " : " + typ + " Not connected.")
            
    def on_tab_change(self, event):
        self.tabSelection = event.widget.index(event.widget.select())
        if self.tabSelection == 3:
            if not self.hostInfo:
                self.hostInfo = True
                self.getHost()
        if self.tabSelection == 4:
            self.editData()
            #event.widget.unbind("<<NotebookTabChanged>>")

    def editData(self):
        self.editDataObj.showDatabase(self.Database.get())
        
    def showHelp(self):
        
        showHelpWin(self.win, "Manage MongoDB security - Help", None, geometry = "800x600", modal = False)
        
    def showURI(self):
        txtURI = self.data.uri
        #pdb.set_trace()
        showConnString(self.win, "Connection string ", txtURI, geometry = "520x100", modal = False)
        
    
    def getHost(self):
        self.version = 'MongoDB version: '
        if not self.data.isConnect or self.data.data is None:
            return   
        #pdb.set_trace()
        gridHostFrame = tk.Frame(self.gridHostFrame.interior)
        gridHostFrame.pack(expand= True, side=LEFT, fill=X, padx=10)   
        messFrame = tk.Frame(gridHostFrame)
        messFrame.pack(fill=X, expand=1)
        objMess = cdc.messageObj(gridHostFrame)
        
        #self.messframe.winfo_width() 
        try:
            db = self.data.data      
            self.version += self.data.DBconnect.server_info()["version"]
            res = db.command(({ "hostInfo": 1 }))
        except pymongo.errors.OperationFailure as ex1:
            objMess.showMess(ex1.details.get('errmsg', ''))
            objMess.addMess("\n\nUser with hostInfo action on Cluster privilege is required.")
            return
        except Exception as ex:
            self.objMainMess.showMess(str(ex))
            return        
        #cle = list(res)
        #print("cle= " + str(cle))
        da=res['system']['currentTime']
        res['system']['currentTime'] = str(da)
        data=res
        #pdb.set_trace()

        formatted_data = json.dumps(data, indent=4)  #, indent=4
        nlines = formatted_data.count('\n')
        text_box = tk.Text(gridHostFrame) #, height= nlines+1
        text_box.pack(expand= True, fill=X)
        cdc.menuEdit(self.win, text_box, options = [0,1,0,1])
        #text_box.grid(row= 0, column=1, sticky="WE")   
        formatted_data = self.version + '\n' + formatted_data
        text_box.insert(tk.END, formatted_data)
        text_box.config( state="disabled")
            
    def getLogs(self, sRes = None, sEqu = None, cRes = None, cEqu = None, chxCtx = None, chxMes = None, chxID = None):
        
        #db.command(({ "hostInfo": 1 }))
        #sudo cat /var/log/mongodb/mongod.log
        """
            ls ~/.mongodb/mongosh/
            https://www.mongodb.com/docs/manual/reference/log-messages/
          "t": <Datetime>, // timestamp
          "s": <String>, // severity
          "c": <String>, // component
          "id": <Integer>, // unique identifier
          "ctx": <String>, // context
          "msg": <String>, // message body
          "attr": <Object> // additional attributes (optional)
          "tags": <Array of strings> // tags (optional)
          "truncated": <Object> // truncation info (if truncated)
          "size": <Object> // original size of entry (if truncated)        
        """
        if not self.data.isConnect or self.data.data is None:
            return   
        objMess = cdc.messageObj(self.gridLogsFrame.interior)
        try:
            db = self.data.data
            res = db.command(({ "getLog": "global" }))
        except pymongo.errors.OperationFailure as ex1:
            objMess.showMess(ex1.details.get('errmsg', ''))
            objMess.addMess("\n\nUser with hostInfo action on Cluster privilege is required.")
            self.gridLogsFrame.scroll(0)
            return
        except Exception as ex:
            objMess.showMess(str(ex))
            return 
        
        self.logsDataList=list(res["log"])
        self.logCnt = len(self.logsDataList)
        self.rangeLog = self.logCnt
        self.foundLog = 0
        #pdb.set_trace()
        self.nextLogList(sRes = sRes, sEqu = sEqu, cRes = cRes, cEqu = cEqu, chxCtx = chxCtx, chxMes = chxMes, chxID = chxID)
        
    def nextLogList(self, sRes = None, sEqu = None, cRes = None, cEqu = None, chxCtx = None, chxMes = None, chxID = None):
        if self.logsDataList is None:
            self.getLogs(sRes = sRes, sEqu = sEqu, cRes = cRes, cEqu = cEqu, chxCtx = chxCtx, chxMes = chxMes, chxID = chxID)
            return
            
        self.filterSearch = False
        self.objMainMess.clearMess()
        self.logsFilter.affFound()
        if sRes or cRes or (self.keyWordLog and (chxCtx or chxMes or chxID)):
            if not self.keyWordLog.get() and (chxCtx or chxMes or chxID):
                self.objMainMess.showMess("What keyword is being searched for.")
                self.keyword.focus()
                return
            if chxID and not self.keyWordLog.get().isnumeric():
                self.objMainMess.showMess("Keyword must be numeric to search for an id.")
                return
            self.filterSearch = True
            
        def showLog(data):
            formatted_data = data  #json.dumps(data, indent=4)  #, indent=4
            #nlines = formatted_data.count('\n')
            text_box = tk.Text(gridLogsFrame, height=5) #, height= nlines+1
            text_box.pack(expand= True, fill=X)  
            cdc.menuEdit(self.win, text_box, options = [0,1,0,1])
            text_box.insert(tk.END, formatted_data)
            text_box.config( state="disabled")
            text_box.bind("<Double-Button-1>", self.getLogDetail)
            self.foundLog += 1
            
        def evalLog(index, data):
            if self.filterSearch:
                obj = json.loads(data)
                exp = True
                if sRes:
                    sExp = '"' + obj['s'] + '"' + ('==' if sEqu._values else '!=') + '"' + sRes + '"'
                    exp = exp and eval(sExp)
                if cRes:
                    cExp = '"' + obj['c'] + '"' + ('==' if cEqu._values else '!=') + '"' + cRes + '"'
                    exp = exp and eval(cExp)
                if chxID:
                    #pdb.set_trace()
                    id = int(self.keyWordLog.get())
                    idExp = (id == obj['id'])
                    exp = exp and idExp 
                else:
                    if chxCtx:
                        ctxExp = '"' + self.keyWordLog.get() + '" in "' + obj['ctx'] + '"' 
                        exp = exp and eval(ctxExp)
                    else:
                        if chxMes:
                            mesExp = '"' + self.keyWordLog.get() + '" in "' + obj['msg'] + '"' 
                            exp = exp and eval(mesExp)                
                if exp:
                    showLog(data)       #str(index) +             
            else:    
                showLog(data)  #str(index) +

        slavelist = self.gridLogsFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy() 

        gridLogsFrame = tk.Frame(self.gridLogsFrame.interior)
        gridLogsFrame.pack(expand= True, side=LEFT, fill=X, padx=10)               

        if self.rangeLog == self.logCnt:
            self.foundLog = 0
        stepCnt = self.logCnt - self.rangeLog
        index = 0
        #print(self.logsDataList[0])
                
        for i in range(self.rangeLog-1,0,-1):
            data = self.logsDataList[i]
            index += 1

            evalLog(index, data)
            if self.foundLog > 299 + stepCnt:
                self.rangeLog -= index 
                break

        stepCnt += index
        #pdb.set_trace()
        #print( "Range = " + str(self.rangeLog) + " step = " + str(stepCnt) + " self.logCnt = " + str(self.logCnt))
        if stepCnt == (self.logCnt - 1):
            index += 1
            stepCnt += 1
            evalLog(index, self.logsDataList[0])
            #pdb.set_trace()
            self.rangeLog = self.logCnt

        tot = str(stepCnt) + " / " + str(self.logCnt)
        if (stepCnt == self.logCnt):
            tot = str(stepCnt) + " records"


        self.logsFilter.affTot(tot)
        if self.filterSearch:
            self.logsFilter.affFound(self.foundLog)

            
    def getLogDetail(self, event):
        #pdb.set_trace()
        txtLog=event.widget.get("1.0",END)
        showLogRec(self.win, "Log detail : ", txtLog, geometry = "400x450", modal = False)        
    

    def readConfFile(self):
        if os.path.exists(CONFFILE):
            #pdb.set_trace()
            with open(CONFFILE, encoding='utf8') as f:
                js = eval(f.read())
                return (js)            
        else:
            return {'init': 'localhost', 'localhost': {'roleKeyword': '', 'userKeyword': '', 'userPass': ['', ''], 'host': 'localhost', 'port': '27017'}}

    def setConfFile(self, param = None):
        #pdb.set_trace()
        initInfo = (self.readConfFile())
        
        initInfo["init"] = self.actServ
        if not self.actServ in initInfo:
            initInfo[(self.actServ)] = {}
        initInfo[(self.actServ)]["roleKeyword"] = self.keyWordRole.get()
        initInfo[(self.actServ)]["userKeyword"] = self.keyWordUser.get()
        
        #pdb.set_trace()
        if not param is None:
            initInfo[(self.actServ)]["userPass"] = self.userPass
            if not param[0]:
                self.userPass[0] = ""
            if not param[1]:
                self.userPass[1] = ""                
            initInfo[(self.actServ)]["userPass"] = self.userPass
        self.writeConfFile(initInfo)

    def writeConfFile(self, initInfo):
        with open(CONFFILE, 'w', encoding='utf-8') as f:
            f.write(str(initInfo))
            f.close()

    def setServerConfFile(self, param = None):
        #print(str(param))
        initInfo = (self.readConfFile())
        #pdb.set_trace()
        if param["server"] is None:     # Delete server
            #pdb.set_trace()
            del initInfo[param["delServ"]]
            if initInfo["init"] == param["delServ"]:
                del initInfo["init"]
        else:                           # Modify or Add new server
            upass = ""
            actualModified = False
            if "delServ" in param:      # Modify server name
                upass = initInfo[(self.actServ)]["userPass"]
                del initInfo[param["delServ"]]
                if initInfo["init"] == param["delServ"]:
                    initInfo["init"] = param["server"]
                    actualModified = True
            if param["server"] != self.actServ and param["server"] not in initInfo: # Add new server
                initInfo[param["server"]] = {}
                initInfo[param["server"]]["roleKeyword"] = ""
                initInfo[param["server"]]["userKeyword"] = ""
                initInfo[param["server"]]["userPass"] = ["", ""]
                if upass:               # set userPass for Modify server name
                    initInfo[param["server"]]["userPass"] = upass
            else:
                if initInfo["init"] == param["server"]:
                    actualModified = True

            initInfo[param["server"]]["host"] = param["host"]
            initInfo[param["server"]]["port"] = param["port"]
            if 'caFile' in param:
                initInfo[param["server"]]["tls"] = {}
                initInfo[param["server"]]["tls"]["caFile"] = param["caFile"]
                if 'caFile' in param:
                    initInfo[param["server"]]["tls"]["keyFile"] = param["keyFile"]
                if 'keyPass' in param:
                    initInfo[param["server"]]["tls"]["keyPass"] = param["keyPass"]                    
                if 'indAccNoSec' in param:
                    initInfo[param["server"]]["tls"]["indAccNoSec"] = param["indAccNoSec"]  
                if 'indHostNoVal' in param:
                    initInfo[param["server"]]["tls"]["indHostNoVal"] = param["indHostNoVal"] 
                if 'indCertNoVal' in param:
                    initInfo[param["server"]]["tls"]["indCertNoVal"] = param["indCertNoVal"]  
                if 'indx509Cli' in param:
                    initInfo[param["server"]]["tls"]["indx509Cli"] = param["indx509Cli"]   
                    
            else:
                if "tls" in initInfo[param["server"]] :
                    del initInfo[param["server"]]["tls"]
        self.writeConfFile(initInfo)
        if actualModified:         
            self.setApp(param["server"])
        
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
            
    def getUsers(self, userNameDB = None, pos = None):
        #pdb.set_trace()
        slavelist = self.gridUsersFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy() 
        objMess = cdc.messageObj(self.gridUsersFrame.interior)
        if not self.data.isConnect or self.data.data is None:
            return   
        try:                      
            dat = self.data.data.system.users
            res=dat.find()
            self.setConfFile()
            self.usersDataList=list(res)
        except pymongo.errors.OperationFailure as ex1:
            objMess.showMess(ex1.details.get('errmsg', ''))
            objMess.addMess("\n\nUser with userAdmin role on database is required.")
            self.gridUsersFrame.scroll(0)
            return

        
        gridUsersFrame = tk.Frame(self.gridUsersFrame.interior)
        gridUsersFrame.pack(expand= True, side=LEFT, fill=X, padx=10)

        if len(self.usersDataList) == 0:
            Button(gridUsersFrame, text='Create root user', command= self.createRoot, font=('Calibri 12 bold')).pack()
            #grid(row=0, column=0)
            
        userNameIndex = -1
        cnt = 0
        index = 0
        for index, data in enumerate(self.usersDataList):

            if (self.Database.get() == "All" or self.Database.get() == data["db"]):
                #print(str(data))
                if "userId" in data and "credentials" in data :
                    data.pop("userId")
                    data.pop("credentials")

                if not userNameDB is None and data["user"] == userNameDB[0] and data["db"] == userNameDB[1]:
                    userNameIndex = index
                #pdb.set_trace()
                if not self.keyWordUser.get() or self.keyWordUser.get().upper() in data["user"].upper():   
                    cnt += 1
                    Button(gridUsersFrame, text=' ... ', command= lambda index=index: self.editUser(index), font=('Calibri 15 bold')).grid(row=index, column=0)
                    formatted_data = json.dumps(data, indent=4)
                    nlines = formatted_data.count('\n')
                    text_box = tk.Text(gridUsersFrame, height= nlines+1)
                    cdc.menuEdit(self.win, text_box, options = [0,1,0,1])
                    text_box.grid(row= index, column=1, sticky="WE")             
                    text_box.insert(tk.END, formatted_data)
                    
                    #pdb.set_trace()
                    text_box.config( state="disabled")
                    
        self.usersFilter.affTot(str(cnt) + "/" + str(index+1))
        self.gridUsersFrame.scroll(0)
        if userNameIndex > -1:
            self.editUser(userNameIndex, pos)
        #jsoneditor.editjson(data)

    def createRoot(self):
        
        app = cdc.logonWin(self.win)
        res = app.showAdminUserBD(self.userPass)   
        res = res[0]
        if not res[0] or not res[1]:
            self.objMainMess.showMess("User name and password must be non-empty.")
            return
        if res:
            db = self.data.data
            result = db.command({"createUser": res[0], "pwd": res[1], "roles": [ {'role': 'root', 'db': 'admin'} ] } )
            if result["ok"]:
                self.objMainMess.showMess("Root user created : " + res[0], "I") 
                self.getUsers()
    
    def getRoles(self, userRole = None, pos = None):

        slavelist = self.gridRolesFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy()
        #pdb.set_trace()
        objMess = cdc.messageObj(self.gridRolesFrame.interior)
        if not self.data.isConnect or self.data.data is None:
            return
        try:
            dat = self.data.data.system.roles
            res=dat.find()
            self.setConfFile()
            self.rolesDataList = list(res)
        except pymongo.errors.OperationFailure as ex1:
            objMess.showMess(ex1.details.get('errmsg', ''))
            objMess.addMess("\n\nUser with userAdmin role on database is required.")
            self.gridRolesFrame.scroll(0)
            return
            
        gridRolesFrame = tk.Frame(self.gridRolesFrame.interior)
        gridRolesFrame.pack(expand= True, side=LEFT, fill=X, padx=10)

        if len(self.rolesDataList) == 0:
            Button(gridRolesFrame, text='Create role', command= self.createRole, font=('Calibri 12 bold')).pack()

        self.rolesNamesList = []
        userRoleIndex = -1
        cnt, index = 0, 0
        for index, data in enumerate(self.rolesDataList):
            #data = self.rolesDataList[index]
            self.rolesNamesList.append(data["role"])
            if (self.Database.get() == "All" or self.Database.get() == data["db"]):
                self.roleList.append(data["role"])
                #pdb.set_trace()
                if not userRole is None and data["role"] == userRole[0] and data["db"] == userRole[1]:
                    userRoleIndex = index     
                if not self.keyWordRole.get() or self.keyWordRole.get().upper() in data["role"].upper():
                    cnt += 1
                    Button(gridRolesFrame, text=' ... ', command= lambda index=index: self.editRole(index), font=('Calibri 15 bold')).grid(row=index, column=0)
                    formatted_data = json.dumps(data, indent=4)
                    nlines = formatted_data.count('\n')            
                    text_box = tk.Text(gridRolesFrame, height= nlines+1)
                    text_box.grid(row= index, column=1, sticky="WE") 
                    cdc.menuEdit(self.win, text_box, options = [0,1,0,1])
                    text_box.insert(tk.END, formatted_data)
                    text_box.config( state="disabled")
        
        self.rolesFilter.affTot(str(cnt) + "/" + str(index+1))
        self.gridRolesFrame.scroll(0)
        if userRoleIndex > -1:
            self.editRole(userRoleIndex, pos)
        #print(self.rolesNamesList)
        return len(self.rolesDataList)

    def createRole(self):
        db = self.data.data
        result = db.command({"createRole": "Read", "privileges": [{"resource": {"db": "", "collection": ""}, "actions": ["find", "listCollections"]}], "roles": []})
        if result["ok"]:
            self.objMainMess.showMess("Role created : 'Read'" , "I") 
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
        self.servers, tmpServ = [], []
        for k in info:
            if k != "init":
                tmpServ.append(k.upper())
        tmpServ.sort()
        for s in tmpServ:
            self.servers.append(next(x for x in info if x.upper() == s ))
        loginDialog(self.win, self.win.title(), self)


    def authentif(self):
        app = cdc.logonWin(self.win)
        result = app.showAdminUserBD(self.userPass)
        if not result is None:
            res = result[0]
            self.userPass = res.copy()
            self.setConfFile([result[1],result[2]])
            self.setApp(self.actServ, userPass = res)            
            

    def checkRoleExist(self, name, db):
        exist = False
        for role in self.rolesDataList:
            #print(role)
            if role["role"] == name and role["db"] == db:
                exist = True
        return exist
    
    
class editRoleWin():
    def __init__(self, mainWin, roleData, pos):
        self.mainObj = mainWin
        self.data = mainWin.data
        self.roleData = roleData
        self.pos = pos
        self.roleName = self.roleData["role"]
        self.Database = StringVar()
        self.clusterRes = IntVar()
        
        self.actionsList = None
        self.userActionsList = []
        if self.roleData["privileges"]:
            self.userActionsList = self.roleData["privileges"][0]["actions"]
        self.addSystemPriv = False
        self.addRoleFlag = False
        self.newRoleName = None
        self.showRoleWin()
    
        
    def close(self):
        self.pop.destroy()

    def cancel(self):
        #pdb.set_trace()
        self.mainObj.getRoles([self.roleName, self.Database.get()], [self.pop.winfo_x(), self.pop.winfo_y()])
        self.pop.destroy()
        
    def save(self):
        #pdb.set_trace()
        res = None
        db=self.data.DBconnect[self.Database.get()]
        role = self.rolesObj.getRole()   
        if role["role"]:  #Save role if exist
            if not self.rolesObj.checkRole():
                self.objMess.showMess("Role not exist!")
                return
            else:
                role = self.rolesObj.getRole()
                #print(str(role))
                try:
                    res = db.command("grantRolesToRole", self.roleName, roles=[role])
                except pymongo.errors.OperationFailure as ex1:
                    self.objMess.showMess(ex1.details.get('errmsg', ''))
                    return
                except Exception as ex:
                    self.objMess.showMess(str(ex))
                    return

        # Save Privilege and actions
        if self.clusterRes.get():
            ressouce = {"cluster" : True}
        else:
            ressouce = {"db": self.comboBD.get(), "collection" : self.comboCol.get()}
        
        revokeArr = []
        try:
            for act in self.userActionsList:
                if self.var_list[self.actionsList.index(act)].get() == 0:
                    revokeArr.append(act)      
        except pymongo.errors.OperationFailure as ex1:
            self.objMess.showMess(ex1.details.get('errmsg', ''))
            return
        if len(revokeArr):
            try:
                res = db.command({"revokePrivilegesFromRole": self.roleName, "privileges": [{"resource": ressouce, "actions": revokeArr}]})
            except pymongo.errors.OperationFailure as ex1:
                self.objMess.showMess(ex1.details.get('errmsg', ''))
                return

        grantArr = []
        for act in self.actionsList:
            if self.var_list[self.actionsList.index(act)].get() == 1:
                grantArr.append(act)
                
        #pdb.set_trace()
        #print(str(ressouce) + "  grantArr : " + str(grantArr))
        if len(grantArr):
            try:    
                res = db.command({"grantPrivilegesToRole": self.roleName, "privileges": [{"resource": ressouce, "actions": grantArr}]})            
            except pymongo.errors.OperationFailure as ex1:
                #ex1.details.get('errmsg', '')
                #pdb.set_trace()
                self.objMess.showMess(ex1.details.get('errmsg', ''))
            except Exception as ex:
                #pdb.set_trace()
                self.objMess.showMess(str(ex))
                return
        if res:
            self.refreshRoles(res)

    def delete(self):
        #pdb.set_trace()
        if self.mainObj.userPass[0]:    #If authentication active with user
            curRole = next(x["roles"] for x in self.mainObj.usersDataList if x["user"] == self.mainObj.userPass[0] )
            for x in curRole:
                if x["role"] == self.roleName:
                    #print(self.roleName + " used by current user : " + self.mainObj.userPass[0])
                    self.objMess.showMess("Role «" + self.roleName + "» is used by current user : " + self.mainObj.userPass[0])
                    return
            
        #roleUsed = next(x for x in reg if x["role"] == self.roleName )
        answer = askyesno(title='Remove',
            message='Remove role : ' + self.roleName)
        if answer:       
            try:
                db=self.data.DBconnect[self.Database.get()]
                res = db.command({"dropRole": self.roleName})
            except pymongo.errors.OperationFailure as ex1:
                self.objMess.showMess(ex1.details.get('errmsg', ''))
                return            
            if res:
                self.mainObj.getUsers()
                self.refreshRoles(res, notShow = True)             

    def addRole(self):
        self.objMess.addMess("\nAdd role to roles.", "I")
        self.addRoleFlag = True

    def delRole(self):

        if self.roleData["roles"]:
            role = self.rolesObj.getRole()
            answer = askyesno(title='Remove role',
                message="Remove role : " + str(role))
            if answer:         
                try:
                    db=self.data.DBconnect[self.Database.get()]
                    res = db.command("revokeRolesFromRole", self.roleName, roles=[role])  
                except pymongo.errors.OperationFailure as ex1:
                    self.objMess.showMess(ex1.details.get('errmsg', ''))
                    return
                
                if res:
                    self.refreshRoles(res)       
        else:
            self.objMess.showMess("No role to remove.")
        
    def addNewRole(self):
        #pdb.set_trace()
        self.menuFichier.destroy()
        self.pop.title("Add Role")
        self.newRoleTxt = StringVar()
        self.newRoleTxt.trace('w', self.changeDatabase)
        self.newRoleName = ttk.Entry(self.formFrame, textvariable=self.newRoleTxt, width=20)
        self.newRoleName.focus()
        self.newRoleName.grid(column=1, row=0, sticky=tk.W)
        ttk.Button(self.butFrame, text='Save', command=self.createRole).grid(row=0, column=0) 
        self.comboBD.current(0)
        self.comboCol.current(0)
        self.rolesObj.init()
        self.roleData["privileges"] = []
        self.setPriv()
        
        dbList = self.mainObj.DBlist.copy()
        dbList[0] = "admin"
        self.comboDatabase = ttk.Combobox(
            self.formFrame,
            textvariable=self.Database,
            state="readonly",
            values = dbList
            )
        self.comboDatabase.current(0)
        self.comboDatabase.bind("<<ComboboxSelected>>", self.changeDatabase)
        self.comboDatabase.grid( row=1, column=1, sticky=tk.W, pady=3) 
        self.submenu_priv.delete(1)

        
    
    def createRole(self):
        #pdb.set_trace()
        if not self.newRoleName.get():
            self.objMess.showMess("Role name must be non-empty.")
            return
            
        grantArr = []
        for act in self.actionsList:
            if self.var_list[self.actionsList.index(act)].get() == 1:
                grantArr.append(act)

        priv = {}
        if self.clusterRes.get():
            ressouce = {"cluster" : True}
        else:
            ressouce = {"db": self.comboBD.get(), "collection" : self.comboCol.get()}        
        priv["resource"] = ressouce
        priv["actions"] = grantArr
        #pdb.set_trace()
        if len(grantArr):
            priv = [priv]
        else:
            priv = []
        
        role = self.rolesObj.getRole()
        if role["role"]:
            role = [role]
        else:
            role = []            
        
        try:
            db=self.data.DBconnect[self.Database.get()]
            res = db.command({"createRole": self.newRoleName.get(), "privileges": priv, "roles": role})
        except pymongo.errors.OperationFailure as ex1:
            self.objMess.showMess(ex1.details.get('errmsg', '')) 
            return
        if res:
            if res["ok"]:
                self.roleName = self.newRoleName.get()
                self.refreshRoles(res)
        
    def changeDatabase(self, *args, message=None):
        #pdb.set_trace()
        mess = "Add role : «" + self.newRoleName.get() + "» to «" + self.Database.get() + "» database"
        if not message is None:
            mess += ("\n" + str(message))
        self.objMess.showMess(mess, "I")
        
    def refreshRoles(self, res, notShow = False):
        #pdb.set_trace()
        if res["ok"]:
            if notShow:
                self.mainObj.getRoles()
            else:
                self.mainObj.getRoles([self.roleName, self.Database.get()], [self.pop.winfo_x(), self.pop.winfo_y()])
                #self.mainObj.getRoles(self.roleName, [self.pop.winfo_x(), self.pop.winfo_y()])
            self.close()
        else:
            self.objMess.showMess(str(res)) 

    def delPriv(self):
        #pdb.set_trace()
        if self.roleData["privileges"]:  
            if self.clusterRes.get():
                ressouce = {"cluster" : True}
            else:
                ressouce = {"db": self.comboBD.get(), "collection" : self.comboCol.get()}
            answer = askyesno(title='Remove',
                message='Remove privilege : { "resource":' + str(ressouce) + " }")
            if answer:    
                try:
                    db=self.data.DBconnect[self.Database.get()]
                    res = db.command({"revokePrivilegesFromRole": self.roleName, "privileges": [{"resource": ressouce, "actions": self.actionsList}]})
                except pymongo.errors.OperationFailure as ex1:
                    self.objMess.showMess(ex1.details.get('errmsg', ''))
                    return                
                
                self.refreshRoles(res)
        else:
            self.objMess.showMess("No privilege to remove.")


    def addSystemPrivilege(self, event = None):
        self.addSystemPriv = True
        ttk.Label(self.formFrame, text="System privilege").grid(row=2, column=1, sticky=tk.W, padx=5, pady=3) 
        self.comboBD.current(0)
        self.menuPriv.destroy()
        self.setPriv(setCol = True)
        self.objMess.addMess("\nAdd system privilege", "I")            
    
    def setKeyWordRole(self):
        self.mainObj.keyWordRole.set(self.roleName) 
        self.mainObj.getRoles()
    
    def showRoleWin(self):
        #print(self.roleData)

        self.pop = tk.Toplevel(self.mainObj.win)
        self.pop.geometry("400x800")
        self.pop.title("Modify Role")
        self.pop.iconbitmap(APPICON)   
        self.mainObj.childWin.append(self.pop)

        if not self.pos is None:
            self.pop.geometry(f"+{self.pos[0]}+{self.pos[1]}")
            
        self.objMess = cdc.messageObj(self.pop, height=45)

        # Form frame
        mainFrame = tk.Frame(self.pop)
        mainFrame.pack( fill=X, padx=10, pady=10)        
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)

        # Input

        self.formFrame = tk.Frame(mainFrame)
        self.formFrame.grid(column=0, row=0)        
        ttk.Label(self.formFrame, text=" role : ").grid(row=0, column=0, sticky=tk.W)
        self.identFrame = tk.Frame(self.formFrame)
        self.identFrame.grid(row=0, column=1, sticky=tk.W, padx=1, pady=3)
        ttk.Label(self.identFrame, text=self.roleName, font= ('Segoe 9 bold')).grid(row=0, column=0, sticky=tk.W, padx=1, pady=3)  
        button = cdc.RoundedButton(self.identFrame, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.setKeyWordRole)
        button.create_text(12,11, text=" >", fill="black", font=('Helvetica 15 '))
        button.grid(row=0, column=1, padx=30, pady=5)
        #Hovertip(button,"Blanchir le formulaire")

        # Création du menu
        self.menuFichier = Menubutton(self.formFrame, text='role :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuFichier.grid(row=0,column=0, sticky=tk.W)
        menu_file = Menu(self.menuFichier, tearoff = 0)
        menu_file.add_command(label='Add role...', command = self.addNewRole) 
        menu_file.add_command(label='Remove role...', command = self.delete) 
        self.menuFichier.configure(menu=menu_file)                 

        self.Database.set(self.roleData["db"])
        ttk.Label(self.formFrame, text="db :                        ").grid(row=1, column=0, sticky=tk.E, padx=5, pady=3)
        ttk.Label(self.formFrame, textvariable=self.Database).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(self.formFrame, text="privileges :    [").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        
        # Création du menu privileges
        self.menuPriv = Menubutton(self.formFrame, text='privileges :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuPriv.grid(row=2,column=0, sticky=tk.W)
        self.submenu_priv = Menu(self.menuPriv, tearoff = 0)
        self.submenu_priv.add_command(label='Add system', command = self.addSystemPrivilege) 
        self.submenu_priv.add_command(label='Remove...', command = self.delPriv) 
        self.menuPriv.configure(menu=self.submenu_priv)        
        
        ttk.Label(self.formFrame, text="{  resources : { ").grid(row=3, column=0, sticky=tk.E, padx=30, pady=3)
        cluster_check = ttk.Checkbutton(
            self.formFrame,
            text="cluster : true",
            variable=self.clusterRes,
            onvalue=1,
            offvalue=0)
        cluster_check.grid(row=3, column=1, sticky=tk.W, padx=5, pady=3) 
         
        
        dbList = self.mainObj.DBlist.copy()
        # self.Database.get() != self.data.dbase:

        objResBDFrame = tk.Frame(self.formFrame)
        objResBDFrame.grid(row=4, column=0, columnspan=2)
        self.objResBD = tk.Frame(objResBDFrame)
        self.objResBD.pack()
        
        ttk.Label(self.objResBD, text= "db : ").grid( row=0, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboBD = ttk.Combobox(
            self.objResBD,
            state="readonly",
            values = dbList
            )
        self.comboBD.bind("<<ComboboxSelected>>", self.setPriv)
        self.comboBD.grid( row=0, column=1, sticky=tk.W)
        
        if self.roleData["privileges"] and "db" in self.roleData["privileges"][0]["resource"]:
            if self.roleData["privileges"][0]["resource"]["db"] in self.mainObj.DBlist:
                self.comboBD.current( self.mainObj.DBlist.index(self.roleData["privileges"][0]["resource"]["db"]) )
        else:
            if self.roleData["privileges"] and "cluster" in self.roleData["privileges"][0]["resource"]:
                self.clusterRes.set(1)
            self.comboBD.current(0)
        self.clusterRes.trace('w', self.changeCluster)     
            
        ttk.Label(self.objResBD, text= "collection : ").grid( row=1, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboCol = ttk.Combobox(
            self.objResBD,
            state="readonly",
            values=[""]
            )
        self.comboCol.bind("<<ComboboxSelected>>", self.setPriv)
        self.comboCol.grid( row=1, column=1, sticky=tk.W) 
        #Fin obj Res BD
        
        ttk.Label(self.formFrame, text="} , ").grid(row=6, column=0, sticky=tk.W, padx=45, pady=3)
        ttk.Label(self.formFrame, text="actions : [").grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=50, pady=3)
        
        
        #pdb.set_trace()

        # Button        
        self.butFrame = tk.Frame(mainFrame)
        self.butFrame.grid(column=1, row=0)

        ttk.Button(self.butFrame, text='Save', command=self.save).grid(row=0, column=0)    
        ttk.Button(self.butFrame, text='Cancel', command=self.cancel).grid(row=1, column=0, pady=3)
        ttk.Button(self.butFrame, text='Close', command=self.close).grid(row=2, column=0, pady=5)
        
        # Grid list frame
        self.actionsFrame = cdc.VscrollFrame(self.pop)
        self.actionsFrame.pack(expand= True, fill=BOTH)


        footFrame = tk.Frame(self.pop)
        footFrame.pack( fill=X )
        ttk.Label(footFrame, text="]").grid(row=0, column=0, sticky=tk.W, padx=70, pady=0)
        ttk.Label(footFrame, text="}").grid(row=1, column=0, sticky=tk.W, padx=45, pady=0)       
        ttk.Label(footFrame, text="]").grid(row=2, column=0, sticky=tk.W, padx=25, pady=0)
        # Création de l'objet Roles
        #pdb.set_trace()
        #self.rolesList = self.roleData["roles"].copy()
        rolesFrame = tk.Frame(footFrame)
        rolesFrame.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=25, pady=3)
        self.rolesObj = rolesSelect(self, rolesFrame, self.roleData["roles"].copy()) 
        
        self.setPriv(setCol = True)
        if self.pos is None:
            winChildPos(self)

    def changeCluster(self, *args):
        self.pop.update_idletasks() 
        self.setPriv()
        if self.clusterRes.get():
            self.objResBD.pack_forget() 
        else:
            self.objResBD.pack()
            
        
    def setPriv(self, event = None, setCol = False):
        self.userActionsList = []                           #Empty user action list
        slavelist = self.actionsFrame.interior.slaves()     #Empty checkbox action list
        for elem in slavelist:
            elem.destroy()

        colList = []
        if self.comboBD.get() not in BDSYSTEMLIST:          # Si valeur "bd" n'est pas dans la liste system
            #colList = self.data.colList[self.comboBD.get()].copy()
            colList = self.mainObj.COLlist[self.comboBD.get()].copy()
        if not "" in colList:
            colList.insert(0,"")
        self.comboCol.config(values=colList) 
            
        privileges = self.roleData["privileges"]
        if not self.clusterRes.get() and privileges and setCol and len(colList) and not self.addSystemPriv and self.roleData["privileges"][0]["resource"]["collection"] in colList: 
        # Si on est pas en mode Cluster ou ajout de privilège system et la collection à initialiser existe
            self.comboCol.current( colList.index(self.roleData["privileges"][0]["resource"]["collection"]) )        
        
        privObj = {"db" : "", "collection" : ""}          
        if self.addSystemPriv:                              # Si ajout d'un privilege build in system
            dbList = BDSYSTEMLIST.copy()
            self.comboBD.config(values=dbList)          
            colList = self.getSystemColl(self.comboBD.get())
            self.comboCol.config(values=colList)
            if setCol:
                self.comboCol.current(0)
            privObj = {"db" : self.comboBD.get(), "collection" : self.comboCol.get()}
        else:
            dbList = self.mainObj.DBlist.copy()
            self.comboBD.config(values=dbList.copy())      
        if self.clusterRes.get():                        # Si privilege Cluster
            dbList = []
            privObj = {"cluster" : True } 
            self.comboBD.config(values=[""])
            self.comboBD.current(0)
            self.comboCol.config(values=[""]) 
            self.comboCol.current(0)
                
        existPriv = False
        #print(privileges)
        for priv in privileges:
            if not self.clusterRes.get() and "db" in priv["resource"]:
                if priv["resource"]["db"] == self.comboBD.get() and priv["resource"]["collection"] == self.comboCol.get():
                    existPriv = True
                    self.userActionsList = priv["actions"]
                if not priv["resource"]["db"] in dbList:
                    dbList.append(priv["resource"]["db"])
                    self.comboBD.config(values=dbList)
                if not priv["resource"]["db"] in self.mainObj.DBlist and priv["resource"]["db"] == self.comboBD.get():
                    colList.append(priv["resource"]["collection"])
                    self.comboCol.config(values=colList)
            else:
                if self.clusterRes.get() and "cluster" in priv["resource"]:
                    existPriv = True
                    self.userActionsList = priv["actions"]
                    break
            
        if not self.comboCol.get() in colList: # Si la collection n'est pas dans la liste
            self.comboCol.current(0)
        if self.clusterRes.get():
            actPriv = privObj
        else:
            actPriv = '{ ' + 'db: "' + self.comboBD.get() + '" , collection: "' + self.comboCol.get() + '" }' 
        mess = ("Modify" if existPriv else "Add") + " privilege :\n" + str(actPriv)  #actPriv
        if self.newRoleName is None: # If not adding new role
            self.objMess.showMess(mess, "I")
        else:
            self.changeDatabase(message=mess)
        
        if self.clusterRes.get():
            #print("cluster= " + str(self.clusterRes.get()))
            self.actionsList = ACTIONCLUSTER
        else:
            self.actionsList = self.getActionList(privObj)
        self.setActionList()
        
    def setActionList(self):    
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
        self.rolesList = self.userData["roles"]
        self.Database = StringVar()
        self.showUserWin()
        
    def close(self):
        self.pop.destroy()

    def changePass(self):
        app = cdc.logonWin(self.pop)
        res = app.showChangeBDpass(self.userName)   
        if res:
            try:
                db=self.data.DBconnect[self.Database.get()]
                result = db.command({"updateUser": res[0], "pwd": res[1]})
            except pymongo.errors.OperationFailure as ex1:
                self.objMess.showMess(ex1.details.get('errmsg', ''))
                return              
            
            if result["ok"]:
                self.objMess.showMess("Password changed for " + res[0], "I") 

    def delete(self):
        if self.userName == self.mainObj.userPass[0]:
            self.objMess.showMess("Can't remove current user : " + self.userName + ".") 
            reg = next(x["roles"] for x in self.mainObj.usersDataList if x["user"] == self.userName )
            #self.mainObj.usersDataList
            #self.userName
            return
            
        answer = askyesno(title='Remove',
            message="Remove user : " + self.userName + "  db : " + self.Database.get())
        if answer:      
            try:
                db=self.data.DBconnect[self.Database.get()]
                res = db.command({"dropUser": self.userName})  
                self.refreshUsers(res, notShow = True) 
            except pymongo.errors.OperationFailure as ex1:
                self.objMess.showMess(ex1.details.get('errmsg', ''))
                return              

    def addUser(self):
        #pdb.set_trace()
        self.menuFichier.destroy()
        self.pop.title("Add User")
        self.userLbl.config(text="")
        self.newUserTxt = StringVar()
        self.newUserTxt.trace('w', self.changeDatabase)
        self.newUserName = ttk.Entry(self.identFrame, textvariable=self.newUserTxt, width=30)
        self.newUserName.focus()
        self.newUserName.grid(column=1, row=0, sticky=tk.W)
        self.rolesObj.addRole()
        ttk.Label(self.identFrame, text=" Password : ").grid(row=1, column=0, sticky=tk.W)
        self.newUserPass = ttk.Entry(self.identFrame, width=30)
        self.newUserPass.grid(row=1, column=1, sticky=tk.W)
        ttk.Button(self.butFrame, text='Save', command=self.createUser).grid(row=0, column=0)  
        self.changeDatabase()
        dbList = self.mainObj.DBlist.copy()
        dbList.append("$external")
        dbList[0] = "admin"
        self.comboDatabase = ttk.Combobox(
            self.dbFrame,
            textvariable=self.Database,
            state="readonly",
            values = dbList
            )
        self.comboDatabase.current(0)
        self.comboDatabase.bind("<<ComboboxSelected>>", self.changeDatabase)
        self.comboDatabase.grid( row=0, column=1, sticky=tk.W, pady=3, padx=1) 

    def changeDatabase(self, *args, message=None):
        mess = "Add user : «" + self.newUserName.get() + "» to «" + self.Database.get() + "» database"
        if not message is None:
            mess += ("\n" + str(message))
        self.objMess.showMess(mess, "I")
        
    def createUser(self):
        if not self.newUserName.get():
            self.objMess.showMess("User name must be non-empty.")
            return       
        if not self.newUserPass.get() and not "external" in self.Database.get():
            self.objMess.showMess("Password must be non-empty.")
            return 
        if not self.rolesObj.checkRole():
            return
        else:
            role = self.rolesObj.getRole()
        try:
            db=self.data.DBconnect[self.Database.get()]
            self.userName = self.newUserName.get()
            #pdb.set_trace()
            if "external" in self.Database.get():
                res = db.command({"createUser": self.userName, "roles": [ role ] } )
            else:
                res = db.command({"createUser": self.userName, "pwd": self.newUserPass.get(), "roles": [ role ] } )
                
            #res = db.command("grantRolesToUser", self.userName, roles=[role])
            self.userName = self.newUserName.get()
            self.refreshUsers(res)
        except pymongo.errors.OperationFailure as ex1:
            self.objMess.showMess(ex1.details.get('errmsg', ''))       
                
    def addRole(self):
        ttk.Button(self.butFrame, text='Save', command=self.grantRole).grid(row=0, column=0) 
        ttk.Button(self.butFrame, text='Cancel', command=self.cancel).grid(row=1, column=0, pady=3)

    def delRole(self):
        role = self.rolesObj.getRole()
        answer = askyesno(title='Remove role',
            message="Remove role : " + str(role))
        if answer:    
            try:
                db=self.data.DBconnect[self.Database.get()]
                res = db.command("revokeRolesFromUser", self.userName, roles=[role])   
                self.refreshUsers(res)
            except pymongo.errors.OperationFailure as ex1:
                self.objMess.showMess(ex1.details.get('errmsg', '')) 
            
    def grantRole(self):
        if not self.rolesObj.checkRole():
            return
        else:
            try:
                role = self.rolesObj.getRole()
                db=self.data.DBconnect[self.Database.get()]                
                res = db.command("grantRolesToUser", self.userName, roles=[role])
                self.refreshUsers(res)
            except Exception as ex:
                self.objMess.showMess(str(ex))
 
    def refreshUsers(self, res, notShow = False):
        #pdb.set_trace()
        if res["ok"]:
            if notShow:
                self.mainObj.getUsers()
            else:
                self.mainObj.getUsers([self.userName, self.Database.get()], [self.pop.winfo_x(), self.pop.winfo_y()])
            self.close()
        else:
            self.objMess.showMess(str(res))    

    def cancel(self):
        self.mainObj.getUsers([self.userName, self.Database.get()], [self.pop.winfo_x(), self.pop.winfo_y()])
        self.pop.destroy()
        
    def showUserWin(self):
        #print(self.userData)

        self.pop = tk.Toplevel(self.mainObj.win)
        #self.pop.geometry("370x270")
        self.pop.minsize(370,270)
        self.pop.title("Modify User")
        self.pop.iconbitmap(APPICON)   
        self.mainObj.childWin.append(self.pop)
        #pdb.set_trace()
        
        if not self.pos is None:
            self.pop.geometry(f"+{self.pos[0]}+{self.pos[1]}")  
        
        self.objMess = cdc.messageObj(self.pop, height=25)

        # Form frame
        mainFrame = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE)
        mainFrame.pack( fill=X, padx=10, pady=10)        
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)

        # Input

        self.formFrame = tk.Frame(mainFrame)
        self.formFrame.grid(column=0, row=0)        
        self.formFrame.columnconfigure(0, weight=1)
        self.formFrame.columnconfigure(1, weight=1)
        
        self.identFrame = tk.Frame(self.formFrame)
        self.identFrame.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=1, pady=3)
        ttk.Label(self.identFrame, text=" User : ").grid(row=0, column=0, sticky=tk.W)
        self.userLbl = ttk.Label(self.identFrame, text=self.userName, font= ('Segoe 9 bold')) 
        self.userLbl.grid(row=0, column=1, sticky=tk.W, padx=10) 
        button = cdc.RoundedButton(self.identFrame, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.setKeyWordUser)
        button.create_text(12,11, text=" >", fill="black", font=('Helvetica 15 '))
        button.grid(row=0, column=2, padx=10)
        #Hovertip(button,"Blanchir le formulaire")

        # Création du menu user
        self.menuFichier = Menubutton(self.identFrame, text='User :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuFichier.grid(row=0,column=0, sticky=tk.W)
        menu_file = Menu(self.menuFichier, tearoff = 0) 
        self.Database.set(self.userData["db"])
        if not "external" in self.Database.get():
            menu_file.add_command(label='Change password...', command = self.changePass) 
        menu_file.add_command(label='Add user...', command = self.addUser) 
        menu_file.add_command(label='Remove user...', command = self.delete) 
        self.menuFichier.configure(menu=menu_file) 

        self.dbFrame = tk.Frame(self.formFrame)
        self.dbFrame.grid(row=2, column=0, sticky=tk.W, pady=3, padx=30)
        
        ttk.Label(self.dbFrame, text="db :").grid(row=0, column=0, sticky=tk.E, padx=5, pady=3)
        ttk.Label(self.dbFrame, textvariable=self.Database).grid(row=0, column=1, sticky=tk.W)
        
        # Création de l'objet Roles
        rolesFrame = tk.Frame(self.formFrame)
        rolesFrame.grid(row=3, column=0, sticky=tk.W, padx=1, pady=3)
        self.rolesObj = rolesSelect(self, rolesFrame, self.rolesList)

        # Button        
        self.butFrame = tk.Frame(self.formFrame)
        self.butFrame.grid(row=1, column=1, rowspan=3, padx=15)
        ttk.Button(self.butFrame, text='Close', command=self.close).grid(row=2, column=0, pady=5)
        if self.pos is None:
            winChildPos(self)

    def setKeyWordUser(self):
        self.mainObj.keyWordUser.set(self.userName)
        self.mainObj.getUsers()

class rolesSelect():
    def __init__(self, parent, rolesFrame, rolesList):
        self.parent = parent
        self.mainObj = parent.mainObj
        self.objMess = self.parent.objMess
        self.data = self.mainObj.data
        self.rolesFrame = rolesFrame
        self.rolesList = rolesList
        self.Database = self.parent.Database
        self.comboRoleText = StringVar()
        self.comboBDText = StringVar()
        self.sysRole = IntVar()
        self.addRoleFlag = False
        self.showRolesSelect()
        #print("rolesSelect.rolesList=" + str(self.rolesList))

    def addRole(self):
        sys_check = ttk.Checkbutton(
            self.rolesFrame,
            text="Built-In Roles",
            variable=self.sysRole,
            onvalue=1,
            offvalue=0)
        sys_check.grid(row=3, column=1, sticky=tk.W, padx=5, pady=3)  
        sys_check.bind("<Button-1>", self.changeRoleList)
        #pdb.set_trace()
        self.comboRole.config(values=self.mainObj.rolesNamesList.copy())
        self.comboRole.unbind("<<ComboboxSelected>>")
        self.comboRole.current(0)
        bdList = self.mainObj.DBlist.copy()
        bdList[0]='admin'
        self.comboBD.config(values=bdList)
        self.comboBD.unbind("<<ComboboxSelected>>")
        self.menuBut.destroy()
        self.menuRole = None
        self.addRoleFlag = True
        self.parent.addRole()
        
    def changeRoleList(self, event= None):
        if self.sysRole.get():
            self.comboRole.config(values=self.mainObj.roleList.copy())
            self.comboBD.config(state="readonly")
        else:
            self.comboRole.config(values=BULTINROLELIST)
            self.comboBD.config(state="normal")
        self.comboRole.current(0)

    def init(self):
        self.comboRole.config(values=[])
        self.comboBD.config(values=[])
        self.comboRoleText.set("")
        self.comboBDText.set("") 
        if not self.menuRole is None:
            self.menuRole.delete(1)

    def delRole(self):
        self.parent.delRole()
        
    def setRole(self, event = None):
        index = event.widget.current()
        self.comboRole.current(index)
        self.comboBD.current(index)

    def getRole(self):
        return {"role": self.comboRoleText.get(), "db": self.comboBDText.get()}
        
    #def clearMenu(self):
    #    self.menuBut.destroy()
        
    def checkRole(self):
        role = self.comboRoleText.get()
        db = self.comboBDText.get()
        exist = False
        if self.addRoleFlag:
            if self.sysRole.get():  # If Built-in role
                if BULTINROLELIST.index(role) < 6:  # Database Built-in role
                    if BULTINROLELIST.index(role) == 5:
                        self.objMess.showMess(role + " is not a role.")
                    else:
                        exist = True
                else:               # Admin Built-in role
                    if self.comboBD.current() != 0:
                        self.objMess.showMess(role + " is an admin role. \ndb: «admin» must be selected.")
                    else:
                        exist = True
            else:   # pre-defined role
                exist = self.mainObj.checkRoleExist(role, db)
                if not exist:
                    #messagebox.showinfo(  title="The role does not exist ",  message=
                    self.objMess.showMess("Role «" + self.comboRoleText.get() + "», bd : «" + self.comboBDText.get() + "» not exist. \nCheck existence in the role tab of the main window.")         
        else:
            exist = True
        return exist
        
    def showRolesSelect(self):

        ttk.Label(self.rolesFrame, text= "roles : ").grid( row=0, column=0, sticky=tk.E, padx=1, pady=3) 
        ttk.Label(self.rolesFrame, text= "[").grid( row=0, column=1, sticky=tk.W, padx=1, pady=3) 
        
        # Création du menu roles
        self.menuBut = Menubutton(self.rolesFrame, text='roles :', width='8', font= ('Segoe 9 bold'), borderwidth=2, relief = RAISED)  #, activebackground='lightblue'
        self.menuBut.grid(row=0,column=0)
        self.menuRole = Menu(self.menuBut, tearoff = 0)
        self.menuRole.add_command(label='Add...', command = self.addRole) 
        self.menuRole.add_command(label='Remove...', command = self.delRole) 
        self.menuBut.configure(menu=self.menuRole)        
        
        roleList = []
        dbList = []
        for role in self.rolesList:
            roleList.append(role["role"])
            dbList.append(role["db"])
        
        ttk.Label(self.rolesFrame, text= "role : ").grid( row=1, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboRole = ttk.Combobox(
            self.rolesFrame,
            textvariable=self.comboRoleText,
            width = 22,
            state="readonly",
            values = roleList.copy()
            )   #self.mainObj.roleList
        if roleList:
            self.comboRole.current(0)
        self.comboRole.bind("<<ComboboxSelected>>", self.setRole)
        self.comboRole.grid( row=1, column=1, sticky=tk.W)         
        ttk.Label(self.rolesFrame, text= "db : ").grid( row=2, column=0, sticky=tk.E, padx=1, pady=3)
        self.comboBD = ttk.Combobox(
            self.rolesFrame,
            textvariable=self.comboBDText,
            width = 22,
            state="readonly",
            values = dbList.copy()
            ) 
        if dbList:
            self.comboBD.current(0)
        self.comboBD.bind("<<ComboboxSelected>>", self.setRole)
        self.comboBD.grid( row=2, column=1, sticky=tk.W)

        ttk.Label(self.rolesFrame, text= "]").grid( row=4, column=0, sticky=tk.E, padx=1, pady=3)    
        
class dbaseObj():
    def __init__(self, *args, **kwargs):
        self.data = None
        self.dbList = []
        self.colList = {}
        self.dbase = ""
        self.DBconnect = None
        self.isConnect = False
        self.uri = None

    
    def getURI(self, userPass, servInfo):
        #pdb.set_trace()
        self.hostName = servInfo["host"] if "host" in servInfo else ""
        port = servInfo["port"] if "port" in servInfo else ""        
              
        uri = """mongodb://%s:%s@"""  % (userPass[0], userPass[1])        
        
        uri += self.hostName
        if port:
            uri += ":" + port 
            
        uri += "/?authSource=admin"
        isx509auth = False
        if "tls" in servInfo:
            if "indx509Cli" in servInfo["tls"]:
                uri = "mongodb://" + self.hostName + ":" + port + "/?authMechanism=MONGODB-X509&authSource=%24external"
                isx509auth = True
            uri += "&tls=true&tlsCAFile=" + servInfo["tls"]["caFile"]
            if "keyFile" in servInfo["tls"]:
                uri += "&tlsCertificateKeyFile=" + servInfo["tls"]["keyFile"]
            if "keyPass" in servInfo["tls"]:
                uri += "&tlsCertificateKeyFilePassword=" + servInfo["tls"]["keyPass"]
            if "indAccNoSec" in servInfo["tls"]:
                uri += "&tlsInsecure=true"
            if "indHostNoVal" in servInfo["tls"]:
                uri += "&tlsAllowInvalidHostnames=true"
            if "indCertNoVal" in servInfo["tls"]:
                uri += "&tlsAllowInvalidCertificates=true"               

               
                #https://www.mongodb.com/docs/manual/reference/program/mongod/#std-option-mongod.--tlsCertificateKeyFilePassword
        else:
            uri += "&tls=false" 
            
        if not isx509auth and userPass[0] == "":
            uri = "mongodb://" + self.hostName + ":" + port + "/"

        #uri = """mongodb+srv://%s:%s@"""  % (userPass[0], userPass[1])        
        #uri += self.hostName
        #Atlas connection
        #uri = "mongodb+srv://cdore00:925045@cluster0.qlggbka.mongodb.net/?retryWrites=true&w=majority"

        return uri
    
    def connectTo(self, Server = LOCALSERV, userPass = None, servInfo = None):
        #pdb.set_trace()
        
        #print(str(servInfo))
        self.dbase = 'admin'
        self.uri = self.getURI( userPass, servInfo)
            
        #print(uri)
        if Server == LOCALSERV or self.hostName == LOCALSERV:
            timeout = 2000
        else:
            timeout = 15000

        if self.isConnect:
            self.DBconnect.close()
            self.isConnect = False
        try:
            self.DBconnect = MongoClient(self.uri,socketTimeoutMS=timeout,
                        connectTimeoutMS=timeout,
                        serverSelectionTimeoutMS=timeout,)
            #pdb.set_trace()
            #auth = self.DBconnect["admin"].command({"connectionStatus" : 1})
            if "ok" in self.DBconnect.server_info():
                self.data = self.DBconnect[self.dbase]
                self.isConnect = True
            else:
                self.dbList = []
        except Exception as ex:
            print(ex)
            self.dbList = []
            self.isConnect = False
        return self.isConnect

class showLogRec(cdc.modalDialogWin):
    def createWidget(self):
        objLog = json.loads(self.obj)
        format_log = json.dumps(objLog, indent=4)
        text_box = tk.Text(self.dframe) #, height=5
        text_box.pack(expand= True, fill=BOTH)
        text_box.pack() 
        cdc.menuEdit(self.win, text_box, options = [0,1,0,1])
        text_box.insert(tk.END, format_log)
        text_box.config( state="disabled")        

class showLogCritere(cdc.modalDialogWin):
    def createWidget(self):
        
        format_log = self.obj
        text_box = tk.Text(self.dframe) #, height=5
        text_box.pack(expand= True, fill=BOTH)
        text_box.pack() 
        text_box.insert(tk.END, format_log)
        text_box.config( state="disabled") 

class showHelpWin(cdc.modalDialogWin):
    def createWidget(self):
        self.pop.minsize(500,400)
        import mongoSecHelp as mh
        self.htmlFrame = HtmlFrame(self.dframe, messages_enabled = False) #create HTML browser
        self.htmlFrame.load_html(mh.htmlHelp) #load a website
        self.htmlFrame.add_css(mh.cssTxt)
        self.htmlFrame.pack(fill="both", expand=True) 
        self.htmlFrame.on_link_click(self.load_new_page)
                
    def load_new_page(self, url, e = None):
        ## Do stuff - insert code here
        if "ServicesConsole" in url:
            #pdb.set_trace()
            if os.name == 'nt' :
                os.system("services.msc")
            else:
                messagebox.showinfo(
                        title="OS System",
                        message=f"You run " + str(platform.platform())) 
            return
        if "file:///" in url:
            self.htmlFrame.load_url(url) #Go to tag
        else:
            cdc.showWebURL(url) #load the new website in a browser
        #print("CALL=" + url)        

class showConnString(cdc.modalDialogWin):
    def createWidget(self):
        self.pop.minsize(520,100)
        self.connStr = self.obj
        
        #svg_image = tksvg.SvgImage( data = SVGCOPY, scaletoheight = 50 )
        #tk.Label( image = svg_image ).pack()
        #pdb.set_trace()
        self.objMess = cdc.messageObj(self.pop, height=12)
        self.formframe = tk.Frame(self.dframe, borderwidth = 1, relief=RIDGE, padx=10, pady=3)
        self.formframe.pack(expand= True, fill=X)
        self.formframe.grid_columnconfigure(0, weight=12)
        self.formframe.grid_columnconfigure(0, weight=1)
        self.col_1 = tk.Frame(self.formframe)
        self.col_1.grid(row=0, column=0, sticky=W)
        self.uri = ttk.Entry(self.col_1, width=120)
        self.uri.insert(0, self.connStr)
        self.uri.config(state="readonly")
        self.uri.pack(expand= True, fill=X)
        #https://stackoverflow.com/questions/55943631/putting-svg-images-into-tkinter-frame
        self.col_2 = tk.Frame(self.formframe, width=20, height=20)
        self.col_2.grid(row=0, column=1, sticky=W)
        #self.pop.update_idletasks()
        """
        svg_image = tksvg.SvgImage( data = SVGCOPY) #, scaletoheight = 20  
        tree = ET.parse(FSVGCOPY)
        root = tree.getroot()
        width = int(root.attrib["width"].replace("px", ""))
        height = int(root.attrib["height"].replace("px", ""))
        # Calculer la nouvelle taille pour le redimensionnement
        new_width = int(width / 20)
        new_height = int(height / 20)        
        image = tk.PhotoImage(width=new_width, height=new_height)
        image.tk.call(image, "copy", svg_image, "-subsample", new_width, new_height)
        
        self.buttonCopy = tk.Label( self.col_2, image = image ) #ou directement =svg_image à la place de =image et avec , scaletoheight = 20 
        self.buttonCopy.pack() 
        self.pop.update_idletasks()
        pdb.set_trace()
        """
        
        self.buttonCopy = Label(self.col_2, text="📋", font=('Segoe 13 bold'), pady=1)
        self.buttonCopy.pack()

        self.buttonCopy.bind('<Button-1>', self.copyToClipboard)
        
        buttonC = ttk.Button(self.dframe, text="Close", command=self.close, width=10)
        buttonC.pack(pady=3)        
        
    def copyToClipboard(self, e = None):
        
        self.objMess.showMess("Connection string copied to clipboard.", "I")
        cp.copy(self.connStr)
        
class loginDialog(cdc.modalDialogWin):
    def createWidget(self):
        self.mainApp = self.obj
        self.pop.resizable(0, 0)
        self.actServ = self.mainApp.actServ
        #pdb.set_trace()
        self.labAct = Label(self.dframe, text=self.actServ + " selected", font=('Calibri 12 bold'), borderwidth=3, relief = SUNKEN, pady=5)
        self.labAct.grid(row=0, column=0, columnspan=3, sticky=EW, pady=5, padx=5)
        
        if len(self.mainApp.servers) == 0:
            self.mainApp.servers.append(LOCALSERV)
        for ind, serv in enumerate(self.mainApp.servers):
            globals()["but" + str(ind)] = Button(self.dframe, text= serv, command= lambda serv=serv: self.selectAppDB(serv), width=30, cursor="hand2")
            globals()["but" + str(ind)].grid(row=ind+1, column=0, columnspan=3)
            globals()["but" + str(ind)].bind("<Double-Button-1>", self.setAppDB) 
        
        lab1 = Label(self.dframe, text=" ", font=('Calibri 1'))
        lab1.grid(row=ind+2, column=0, columnspan=2)

        self.dframe.columnconfigure(0, weight=1)
        self.dframe.columnconfigure(1, weight=1)
        buttonC = ttk.Button(self.dframe, text="Ok", command=self.setAppDB, width=10)
        buttonC.grid(row=ind+3, column=0) 
        buttonC = ttk.Button(self.dframe, text="Modify", command=self.modifyServ, width=10)
        buttonC.grid(row=ind+3, column=1)
        buttonC = ttk.Button(self.dframe, text="Cancel", command=self.close, width=10)
        buttonC.grid(row=ind+3, column=2)         
        lab1 = Label(self.dframe, text=" ", font=('Calibri 1'))
        lab1.grid(row=ind+4, column=0, columnspan=2)

    def selectAppDB(self, serv):
        self.actServ = serv
        self.labAct.config(text=serv + " selected")
        
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
        self.caFile = StringVar()
        self.keyFile = StringVar()
        self.keyPass = StringVar()
        self.indAccNoSec = IntVar()
        self.indHostNoVal = IntVar()
        self.indCertNoVal = IntVar()
        self.indx509Cli = IntVar()
        self.indAddServer = 0
        self.servToRemove = ""      
        simpledialog.Dialog.__init__(self, parent)
    
    def body(self, master):
        #pdb.set_trace()
        if "host" in self.servInfo[self.actServ]:
            self.host.set(self.servInfo[self.actServ]["host"])
        if "port" in self.servInfo[self.actServ]:
            self.port.set(self.servInfo[self.actServ]["port"])
        if "tls" in self.servInfo[self.actServ]:
            self.caFile.set(self.servInfo[self.actServ]["tls"]["caFile"])            
            if "keyFile" in self.servInfo[self.actServ]["tls"]:
                self.keyFile.set(self.servInfo[self.actServ]["tls"]["keyFile"])
            if "keyPass" in self.servInfo[self.actServ]["tls"]:
                self.keyPass.set(self.servInfo[self.actServ]["tls"]["keyPass"])
            if "indAccNoSec" in self.servInfo[self.actServ]["tls"]:
                self.indAccNoSec.set(self.servInfo[self.actServ]["tls"]["indAccNoSec"])                
            if "indHostNoVal" in self.servInfo[self.actServ]["tls"]:
                self.indHostNoVal.set(self.servInfo[self.actServ]["tls"]["indHostNoVal"])
            if "indCertNoVal" in self.servInfo[self.actServ]["tls"]:
                self.indCertNoVal.set(self.servInfo[self.actServ]["tls"]["indCertNoVal"])
            if "indx509Cli" in self.servInfo[self.actServ]["tls"]:
                self.indx509Cli.set(self.servInfo[self.actServ]["tls"]["indx509Cli"])
                
        self.formframe = tk.Frame(master, borderwidth = 1, relief=RIDGE, padx=10, pady=10)
        self.formframe.grid(row=1)
        tk.Label(self.formframe, text="Server :").grid(row=0, column=0, sticky=E)
        #tk.Label(self.formframe, text= self.actServ, font=('Calibri 12 bold')).grid(row=0, column=1, sticky=W)
        tk.Label(self.formframe, text= "Host : ").grid(row=1, column=0, sticky=E)
        tk.Label(self.formframe, text= "Port : ").grid(row=2, column=0, sticky=E)    
        tk.Label(self.formframe, text= "CA file : ").grid(row=3, column=0, sticky=E)
        tk.Label(self.formframe, text= "Key file : ").grid(row=4, column=0, sticky=E)
        tk.Label(self.formframe, text= "Key pass : ").grid(row=5, column=0, sticky=E)
        
        self.server.set(self.actServ)
        serv = tk.Entry(self.formframe, textvariable = self.server, width=30)
        serv.grid(row=0, column=1, sticky=W)        
        self.entry = tk.Entry(self.formframe, textvariable = self.host, width=30)
        self.entry.grid(row=1, column=1)      
        Hovertip(self.entry," Host name or ip address. ")
        port = tk.Entry(self.formframe, textvariable = self.port, width=10)
        port.grid(row=2, column=1, sticky=W)
        Hovertip(port," Communication port.\n 27017 = MongoDB default.")
        ca = tk.Entry(self.formframe, textvariable = self.caFile, width=30)
        ca.grid(row=3, column=1, sticky=W)
        butCA = ttk.Button(self.formframe, text="...", command=self.selFCA, width=3)
        butCA.grid(row=3, column=2, pady=5, padx=5)         
        Hovertip(ca," Certificate authority (CA).")
        
        key = tk.Entry(self.formframe, textvariable = self.keyFile, width=30)
        key.grid(row=4, column=1, sticky=W)
        Hovertip(key," Certificate key file (private key)\n Required for self-signed certificate as x509 auth.")
        butFK = ttk.Button(self.formframe, text="...", command=self.selFK, width=3)
        butFK.grid(row=4, column=2, pady=5, padx=5)        

        passw = tk.Entry(self.formframe, textvariable = self.keyPass, width=30)
        passw.grid(row=5, column=1, sticky=W)
        Hovertip(passw," Passphrase to decrypt private key.")
        #port = tk.Entry(self.formframe, textvariable = self.indAccNoSec, width=10)
        #port.grid(row=6, column=1, sticky=W)
        chkInsec = ttk.Checkbutton(
            self.formframe,
            text="tls Insecure",
            variable=self.indAccNoSec,
            onvalue=1,
            offvalue=0)
        chkInsec.grid(row=6, column=1, sticky=tk.W, padx=0, pady=3)
        Hovertip(chkInsec," This includes tlsAllowInvalidHostnames and tlsAllowInvalidCertificates.\n Ex. x509: certificate signed by unknown authority. ")
        chkInsec = ttk.Checkbutton(
            self.formframe,
            text="tlsAllowInvalidHostnames",
            variable=self.indHostNoVal,
            onvalue=1,
            offvalue=0)
        chkInsec.grid(row=7, column=1, sticky=tk.W, padx=0, pady=3)
        Hovertip(chkInsec," Disable the validation of the hostnames in the certificate presented by the mongod/mongos instance. ")
        chkInsec = ttk.Checkbutton(
            self.formframe,
            text="tlsAllowInvalidCertificates",
            variable=self.indCertNoVal,
            onvalue=1,
            offvalue=0)
        chkInsec.grid(row=8, column=1, sticky=tk.W, padx=0, pady=3)
        Hovertip(chkInsec," Disable the validation of the server certificates. ")  
        chkx509 = ttk.Checkbutton(
            self.formframe,
            text="x509 client authenticate ",
            variable=self.indx509Cli,
            onvalue=1,
            offvalue=0)
        chkx509.grid(row=9, column=1, sticky=tk.W, padx=0, pady=3)
        Hovertip(chkx509," Authenticate client with a x.509 Certificate. ")
        
        butframe = tk.Frame(self.formframe, padx=10, pady=10)
        butframe.grid(row=10, column=0, columnspan=3) 
        buttonC = ttk.Button(butframe, text="Add server", command=self.addServer, width=15)
        buttonC.grid(row=0, column=0, pady=5, padx=5) 
        buttonC = ttk.Button(butframe, text="Remove server", command=self.removeServer, width=15)
        buttonC.grid(row=0, column=1, pady=5, padx=5) 

    def selFK(self):
        file_path = filedialog.askopenfilename( title="Select Certificat key file")
        if file_path:
            self.keyFile.set(file_path)
    def selFCA(self):
        file_path = filedialog.askopenfilename( title="Select Certificat authority file")
        if file_path:
            self.caFile.set(file_path)
        
    def addServer(self):

        self.server.set("")
        self.host.set("")
        self.port.set("27017")
        self.keyFile.set("")
        self.caFile.set("")
        self.keyPass.set("")
        self.indAccNoSec.set(0) 
        self.indHostNoVal.set(0) 
        self.indCertNoVal.set(0) 
        self.indx509Cli.set(0) 
        self.indAddServer = 1

    def removeServer(self):
        answer = askyesno(title='Remove',
            message='Remove server : ' + self.actServ)
        if answer:
            self.servToRemove = self.actServ
            self.actServ = None
            self.apply()
            self.destroy()
    
    def validate(self):
        if self.indAccNoSec.get() and (self.indHostNoVal.get() or self.indCertNoVal.get()):
            messagebox.showinfo(
                    title="Options selection",
                    message="Options tlsInsecure and tlsAllowInvalidHostnames cannot be specified simultaneously.")
            return False        
        if not self.indAddServer and self.server.get() != self.actServ:
            self.servToRemove = self.actServ
        if self.server.get() != "":
            self.actServ = self.server.get()
        return True
    
    def apply(self):
        # Cette méthode est appelée lorsque le bouton "OK" est cliqué
        resObj = {"server": self.actServ, "host": self.host.get(), "port": self.port.get()}
        if self.caFile.get():
            resObj["caFile"] = self.caFile.get()        
        if self.keyFile.get():
            resObj["keyFile"] = self.keyFile.get()
        if self.keyPass.get():
            resObj["keyPass"] = self.keyPass.get()
        if self.indAccNoSec.get():
            resObj["indAccNoSec"] = self.indAccNoSec.get()
        if self.indHostNoVal.get():
            resObj["indHostNoVal"] = self.indHostNoVal.get()   
        if self.indCertNoVal.get():
            resObj["indCertNoVal"] = self.indCertNoVal.get()  
        if self.indx509Cli.get():
            resObj["indx509Cli"] = self.indx509Cli.get()             
        if self.servToRemove != "":
            resObj["delServ"] = self.servToRemove
        self.result = resObj


class editDatabase():
    def __init__(self, parent, editFrame):
        self.mainObj = parent
        #self.editFrame = editFrame
        self.editFrame = tk.Frame(editFrame)  #, bg="red"
        self.editFrame.columnconfigure(0, weight=1) 
        self.editFrame.columnconfigure(1, weight=20)
        self.editFrame.rowconfigure(0, weight=1)
        self.recList = []
        self.recTot = 0
        self.recCnt = 0
        self.recSkip = 0
        self.recLimit = 20
        self.databaseName = ""
        self.colNameSelect = None
        self.collections = []
        self.keyObj = ""
        
        self.menuCollection = Menu(self.mainObj.win,tearoff=0) # Create a menu
        self.menuCollection.add_command(label="Remove", command=self.dropCollection, accelerator="🗑") 
        self.menuCollection.add_command(label="Rename", command=self.renameCollection, accelerator="A")
        
        self.menuCollCre = Menu(self.mainObj.win,tearoff=0) # Create a menu
        self.menuCollCre.add_command(label="Create", command=self.createCollection, accelerator="🛢") 
        
        self.menuDBDel = Menu(self.mainObj.win,tearoff=0) # Create a menu
        self.menuDBDel.add_command(label="Remove", command=self.dropDatabase, accelerator="🗑") 
        
    def initObj(self, editFilter):
        self.editFrame.pack(expand=1, fill=BOTH) 
        self.editFilter = editFilter


    def popMenu(self, event):
        self.menuDBDel.tk_popup(event.x_root,event.y_root)
    
    def dropDatabase(self):
        self.mainObj.objMainMess.clearMess()
        #pdb.set_trace()
        if self.databaseName == 'All' or self.databaseName == '':
            self.mainObj.objMainMess.showMess( "Select a database first.")    
            return
        elif self.databaseName == 'admin':
            self.mainObj.objMainMess.showMess( "Can't remove admin database.")    
            return        

        answer = askyesno(title='Remove ?',
            message='Remove database : ' + self.databaseName)
        if answer:    
            #pdb.set_trace()
            self.mainObj.data.DBconnect.drop_database(self.databaseName)
            self.mainObj.readDBcolList()
            self.mainObj.initDBcombo()  
            self.showDatabase('All')

    def createDatabase(self):
        dbName = cdc.getInput.string(self.mainObj.win, "New database", "Database name")
        if dbName:
            #pdb.set_trace()
            dbObj = self.mainObj.data.DBconnect[dbName]
            #dblist = self.mainObj.data.DBconnect.list_database_names()
            dbObj.create_collection("test", codec_options=None, read_preference=None, write_concern=None, read_concern=None, session=None)
            self.mainObj.readDBcolList()
            self.mainObj.initDBcombo(dbName)
            #print( db.list_collection_names())

    def renameCollection(self):
        if not self.isCollSelected():
            return
        collName = cdc.getInput.string(self.mainObj.win, "Rename collection: "  + self.colNameSelect, "Collection name")
        if collName:        
            collection=self.dbObj[self.colNameSelect]
            collection.rename(collName, dropTarget = True)
            self.mainObj.readDBcolList()
            self.showDatabase(self.databaseName, refresh = True)            
            print('renameCollection')
            
    def dropCollection(self):
        if not self.isCollSelected():
            return
        answer = askyesno(title='Remove collection',
            message='Remove collection : ' + self.colNameSelect)
        if answer:
            print("dropCollection: " + self.colNameSelect)
            res=self.dbObj[self.colNameSelect].drop()
            #pdb.set_trace()
            self.mainObj.COLlist[self.databaseName].remove(self.colNameSelect)
            iid = self.colltreeview.selection()[0]
            self.colltreeview.delete(iid)
            #pdb.set_trace()
            slavelist = self.scrollrecFrame.interior.slaves()
            for elem in slavelist:
                elem.destroy() 
            self.colNameSelect = None
            self.editFilter.affTot("")   

    def createCollection(self):
        if not self.isCollSelected():
            return        
        colName = cdc.getInput.string(self.mainObj.win, "Add new collection", "Collection name")
        if colName:
            self.dbObj.create_collection(colName, codec_options=None, read_preference=None, write_concern=None, read_concern=None, session=None)
            self.mainObj.COLlist[self.databaseName].append(colName)
            colList = self.mainObj.COLlist[self.databaseName]
            colList.sort()
            self.mainObj.COLlist[self.databaseName] = colList.copy()
            self.showDatabase(self.databaseName, refresh = True)
            print("New Collection: " + colName)
            
    def showDatabase(self, dbName, refresh = False):
        
        #pdb.set_trace()
        
        if (self.databaseName != dbName ) or refresh :
            
            for widget in self.editFrame.winfo_children():  # Delete collections list and records list
                widget.destroy()                
                
            self.databaseName = dbName

            collFrame = tk.Frame(self.editFrame)  
            collFrame.grid(row=0, column=0, sticky='NSWE', padx=0, pady=3)
            collFrame.rowconfigure(0, weight=1)

            butAddBD = ttk.Button(collFrame, text='Create DB', command=self.createDatabase, width=17)
            butAddBD.pack(anchor=W, padx=10)   
            
            if dbName != "admin" and dbName != "All":
            
                self.dbObj=self.mainObj.data.DBconnect[self.databaseName]
                self.collections = self.mainObj.COLlist[dbName]             
                lblDBname = ttk.Label(collFrame, text=dbName, font= ('Segoe 11 bold'), borderwidth=1, relief = RIDGE, width=14) #, relief = SOLID
                lblDBname.pack(anchor=W, padx=11) 
                lblDBname.bind("<Button-3>", self.popMenu)
                
                self.scrollCollFrame = cdc.VscrollFrame(collFrame)
                self.scrollCollFrame.pack(expand= True, fill=BOTH)     
                      

                
                self.colltreeview = ttk.Treeview(self.scrollCollFrame.interior, height=len(self.collections))
                self.colltreeview.column("#0",anchor=W, stretch=NO, width=110)
                self.colltreeview.heading("#0", text= "Collections")
                
                self.colltreeview.tag_bind("selecttag", "<<TreeviewSelect>>", self.showColl)
                self.colltreeview.bind("<Button-3>", self.popup)
                
                for ind, coll in enumerate(self.collections):   # Set collections list
                    self.colltreeview.insert('', 'end',text=coll,values=(coll), tags=("selecttag"))  #,values=('1','C++')
                self.colltreeview.pack()
                
                style = ttk.Style()
                style.configure('Treeview.Heading', foreground='#559', font=('Segoe',10))  

            self.recFrame = tk.Frame(self.editFrame)  # Reset records frame
            self.recFrame.grid(row=0, column=1, sticky='NSWE', padx=5, pady=3)            
            self.recFrame.rowconfigure(0, weight=1)            
            self.editFilter.affTot("")
            self.colNameSelect = None
            self.scrollrecFrame = cdc.VscrollFrame(self.recFrame)
            self.scrollrecFrame.pack(expand= True, fill=BOTH)            


    def popup(self, event):
        """action in event of button 3 on tree view"""
        # select row under mouse
        #pdb.set_trace()
        iid = self.colltreeview.identify_row(event.y)
        if iid == '':
            #print("Create")
            self.menuCollCre.tk_popup(event.x_root,event.y_root)
        if iid and self.colltreeview.selection():
            # mouse pointer over item
            #self.colltreeview.selection_set(iid)
            if iid == self.colltreeview.selection()[0]:
                self.menuCollection.tk_popup(event.x_root,event.y_root)

    
    def showColl(self, e = None):
        #pdb.set_trace()
        #print("event = " + str(e))
        self.mainObj.objMainMess.clearMess()
        if self.colltreeview.selection():
            self.resetList()
            self.colNameSelect = self.colltreeview.item( self.colltreeview.selection()[0], option="text")
            self.dataObj = self.dbObj[self.colNameSelect]
            self.showRec(newRec=True) #newRec=True

    def showRecReset(self):
        self.showRec(newRec=True)

    def isCollSelected(self):
        if self.colNameSelect is None:
            messagebox.showinfo(  title="Collection ?",  message="Select a Database and a Collection first.")
            return False
        else:
            return True

    def showRec(self, newRec=False):  #, newRec=False
        #pdb.set_trace()
        if not self.isCollSelected():
            return

        if self.recCnt == self.recTot:
            tot = self.recTot
            self.resetList()
            self.recTot = tot
        
        self.getdata(newRec)
        slavelist = self.scrollrecFrame.interior.slaves()
        for elem in slavelist:
            elem.destroy() 

        for ind, coll in enumerate(self.recList):
            self.addElemToList(coll)
            self.recCnt += 1          

        self.editFilter.affTot(str(self.recCnt) + "/" + str(self.recTot))
        #self.mainObj.objMainMess.clearMess()

    def addNewRecord(self): 
            if not self.isCollSelected():
                return            
            custom_dialog = eob.editModalObj(self.mainObj.win, {}, title="Add JSON Object", editMode = True)
            res = custom_dialog.result        
            if res:
                self.addElemToList(res[0])  
                coll = self.dbObj[self.colNameSelect] 
                doc = coll.insert_one(res[0])
                self.updAffCnt(recCnt = 1, totCnt = 1)

    def addElemToList(self, coll, recFrame = None):
        if recFrame is None:
            recFrame = tk.Frame(self.scrollrecFrame.interior, padx=2)
            recFrame.columnconfigure(0, weight=30) 
            recFrame.columnconfigure(1, weight=1) 
            recFrame.pack(expand=1, fill=BOTH)            
        else:
            slavelist = recFrame.slaves()
            for elem in slavelist:
                elem.destroy()
        
        self.addRecToListObj(recFrame, coll)
        
        butFrame = tk.Frame(recFrame)
        butFrame.grid(row= 0, column=1, sticky="N")
        
        butEdit = tk.Button(butFrame, text= "🖍", font= ('Calibri 12'), command= lambda listObj=recFrame, obj = coll: self.editRec( listObj, obj)) 
        butEdit.pack()
        Hovertip(butEdit,"Edit")
        butDel = tk.Button(butFrame, text="🗑", font= ('Calibri 9'), command= lambda listObj=recFrame, rec_id=coll["_id"]: self.delRecord(listObj, rec_id))  #, command=self.selFK  🗑  🗑
        butDel.pack()
        Hovertip(butDel,"Remove")


    def addRecToListObj(self, recFrame, coll):
        formatted_data = json.dumps(coll, indent=4, default=str, ensure_ascii=False)
        #pdb.set_trace()
        nlines = formatted_data.count('\n')
        text_box = tk.Text(recFrame, height=nlines+1) #, height= nlines+1
        text_box.grid(row= 0, column=0, sticky="WE")
        cdc.menuEdit(self.mainObj.win, text_box, options = [0,1,0,1])
        text_box.insert(tk.END, formatted_data)
        text_box.config( state="disabled")  
        text_box.bind("<Double-Button-1>", lambda listObj=recFrame, obj = coll: self.editRec(listObj, obj))

    def delRecord(self, listObj, rec_id):
        answer = askyesno(title='Remove record ?',
            message='Remove record : "_id": "' + str(rec_id) + '"')
        if answer:
            res=self.dbObj[self.colNameSelect]
            res.delete_one({"_id": rec_id})
            listObj.destroy()
            self.updAffCnt(recCnt = -1, totCnt = -1)

    def delAllRecord(self):
        if not self.isCollSelected():
            return    
        answer = askyesno(title='Remove records ?',
            message='Remove all (' + str(self.recTot) + ') collection\'s records.')
        if answer:
            res=self.dbObj[self.colNameSelect]
            res.delete_many({})
            self.showRec(newRec=True)
        
    def getdata(self, newRec):
 
            keyObj=self.mainObj.keyWordEdit.get()
            if len(keyObj) and keyObj[0:1] != "{":
                keyObj = '{ ' + keyObj + ' }'
            isValid = True
            try:
                keyObj = loads( keyObj ) if keyObj else {}
                if "_id" in keyObj:
                    keyObj['_id']=getID(keyObj['_id'])
            except Exception as ex:
                messagebox.showinfo(
                    title="Keyword error",
                    message=f"Keyword is not a valid json object.\n" + str(keyObj) + "\n" + str(ex))
                isValid = False            
            
            if not isValid:                              # If keyword is not valid, return with empty records list
                self.resetList()
                self.recList = []
                return
            if self.keyObj != keyObj or newRec:          # Clear records list if filter change and count records
                self.keyObj = keyObj
                self.resetList()
                self.recTot = self.dataObj.count_documents(keyObj)             

            res = self.dataObj.find(keyObj).skip(self.recSkip).limit(self.recLimit)  
            self.recList = list(res) 
            self.recSkip += len(self.recList)

    def updAffCnt(self, recCnt = 0, totCnt = 0):
        self.recCnt += recCnt
        self.recTot += totCnt
        #self.recCnt = max(0, self.recCnt)
        #self.recTot = max(0, self.recTot)
        self.editFilter.affTot(str(self.recCnt) + "/" + str(self.recTot))   

    def importRecords(self):
        if not self.isCollSelected():
            return     
        files = [("JSON file","*.json"),("all files","*.*")]
        try:        
            file_path = filedialog.askopenfilename( title="Select file to import", filetypes = files)
            if file_path: 
                with open(file_path, encoding='utf8') as f:
                    objColl = eval(f.read())     
                coll = self.dbObj[self.colNameSelect]   # Set data object collection)
                doc = coll.insert_many(objColl)
                self.showRecReset()
                self.mainObj.objMainMess.showMess( "File data imported to collection: " + file_path, "I")
        except Exception as ex:
            self.mainObj.objMainMess.showMess(str(ex))

    def exportRecords(self):
        if not self.isCollSelected():
            return     
        files = [("JSON file","*.json"),("all files","*.*")]
        try:        
            file_path = filedialog.asksaveasfile( title="Select file path and name", initialfile = self.colNameSelect, filetypes = files, defaultextension = files )
            if file_path: 
                with open(file_path.name, 'w', encoding='utf-8') as f:
                    f.write(str(self.recList))
                    f.close()     
                    self.mainObj.objMainMess.showMess( "Collection data exported in file: " + file_path.name, "I")
        except Exception as ex:
            self.mainObj.objMainMess.showMess(str(ex))

            
    def editRec(self, listObj, obj):
        #txtLog=event.widget.get("1.0",END)
        custom_dialog = eob.editOntopObj(self.mainObj.win, obj, title="Edit JSON Object", editMode = True)
        res = custom_dialog.result 
        
        if res:
            obj = res[0]
            typTrx = res[1]
            #pdb.set_trace()
            print(obj)
            coll = self.dbObj[self.colNameSelect]   # Set data object collection
            if typTrx == 1:
                #print("update")
                objCopy = obj.copy()
                ID = objCopy['_id']   #getID
                del objCopy['_id']
                self.addElemToList(obj, recFrame = listObj)
                doc = coll.delete_one({ '_id': obj['_id']})
                obj['_id'] = ID
                doc = coll.insert_one(obj)
                
            elif typTrx == 2:
                #print("delete")
                pdb.set_trace()
                doc = coll.delete_one({ '_id': obj['_id']})
                listObj.destroy()
                self.updAffCnt(recCnt = -1, totCnt = -1)
            elif typTrx == 3:
                #print("insert")
                doc = coll.insert_one(obj)
                self.addElemToList(obj)
                self.updAffCnt(recCnt = 1, totCnt = 1)
              
            return res
    
    def resetList(self):
        self.recTot = 0
        self.recCnt = 0
        self.recSkip = 0      



   
def create_main_window():

    win = tk.Tk()
    #win.resizable(0, 0)

    l = int(win.winfo_screenwidth() / 2)
    win.geometry(f"+{l}+100")

    master_form_find(win)
    win.mainloop()

if __name__ == "__main__": 
                
    create_main_window()
    
