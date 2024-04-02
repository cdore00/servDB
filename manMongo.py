
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
# JSON
from bson import ObjectId
import json

# MongoDB
import pymongo

import tkinter as tk
from tkinter import * 

from tkinter import messagebox, TclError, ttk
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
from tkinter import simpledialog
from tkinter import filedialog
from idlelib.tooltip import Hovertip


import cdControl as cdc
import editObject as eob
import mongoRoles
ACTIONLIST = mongoRoles.actionsList
ACTIONCLUSTER = mongoRoles.clusterResActions
BULTINROLELIST = mongoRoles.systemRole
    
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
    
##########################################################
#
#   Tab edit role
#
##########################################################      
class editRoleWin():
    def __init__(self, mainWin, roleData, pos, option = None):
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
        if option:
            self.addNewRole()
        
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

##########################################################
#
#   Tab edit user
#
##########################################################        
class editUserWin():
    def __init__(self, mainWin, userData, pos, option = None):
        self.mainObj = mainWin
        self.data = mainWin.data
        self.userData = userData
        self.pos = pos
        self.userName = self.userData["user"]
        self.rolesList = self.userData["roles"]
        self.Database = StringVar()
        self.showUserWin()
        if option:
            self.addUser()
        
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

##########################################################
#
#   Add remove existing roles
#
##########################################################
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
        self.comboBD.configure(state="readonly")
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
            #self.comboBD.config(state="normal")
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
        #pdb.set_trace()
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
            state="disable",
            values = dbList.copy()
            ) 
        if dbList:
            self.comboBD.current(0)
        self.comboBD.bind("<<ComboboxSelected>>", self.setRole)
        self.comboBD.grid( row=2, column=1, sticky=tk.W)

        ttk.Label(self.rolesFrame, text= "]").grid( row=4, column=0, sticky=tk.E, padx=1, pady=3)    


##########################################################
#
#   Tab edit databases
#
##########################################################
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
            try:
                self.mainObj.data.DBconnect.drop_database(self.databaseName)
                self.mainObj.readDBcolList()
                self.mainObj.initDBcombo()  
                self.showDatabase('All')
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return
                
    def createDatabase(self):
        dbName = cdc.getInput.string(self.mainObj.win, "New database", "Database name")
        if dbName:
            #pdb.set_trace()
            try:
                dbObj = self.mainObj.data.DBconnect[dbName]
                dbObj.create_collection("test", codec_options=None, read_preference=None, write_concern=None, read_concern=None, session=None)
                self.mainObj.readDBcolList()
                self.mainObj.initDBcombo(dbName)
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return

    def renameCollection(self):
        if not self.isCollSelected():
            return
        collName = cdc.getInput.string(self.mainObj.win, "Rename collection: "  + self.colNameSelect, "Collection name")
        if collName:  
            try:
                collection=self.dbObj[self.colNameSelect]
                collection.rename(collName, dropTarget = True)
                self.mainObj.readDBcolList()
                self.showDatabase(self.databaseName, refresh = True)            
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return
                
    def dropCollection(self):
        if not self.isCollSelected():
            return
        answer = askyesno(title='Remove collection',
            message='Remove collection : ' + self.colNameSelect)
        if answer:
            try:
                res=self.dbObj[self.colNameSelect].drop()
                self.mainObj.COLlist[self.databaseName].remove(self.colNameSelect)
                iid = self.colltreeview.selection()[0]
                self.colltreeview.delete(iid)
                slavelist = self.scrollrecFrame.interior.slaves()
                for elem in slavelist:
                    elem.destroy() 
                self.colNameSelect = None
                self.editFilter.affTot("")   
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return
                
    def createCollection(self):
        if not self.isCollSelected():
            return        
        colName = cdc.getInput.string(self.mainObj.win, "Add new collection", "Collection name")
        if colName:
            try:
                self.dbObj.create_collection(colName, codec_options=None, read_preference=None, write_concern=None, read_concern=None, session=None)
                self.mainObj.COLlist[self.databaseName].append(colName)
                colList = self.mainObj.COLlist[self.databaseName]
                colList.sort()
                self.mainObj.COLlist[self.databaseName] = colList.copy()
                self.showDatabase(self.databaseName, refresh = True)
            except pymongo.errors.OperationFailure as ex1:
                
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return
                
    def showDatabase(self, dbName, refresh = False):
        
        #pdb.set_trace()
        self.mainObj.objMainMess.clearMess()
        if (self.databaseName != dbName ) or refresh :
            
            for widget in self.editFrame.winfo_children():  # Delete collections list and records list
                widget.destroy()                
                
            self.databaseName = dbName

            collFrame = tk.Frame(self.editFrame)  
            collFrame.grid(row=0, column=0, sticky='NSWE', padx=0, pady=3)
            collFrame.rowconfigure(0, weight=1)
            
            if dbName != "admin" and dbName != "All":
            
                self.dbObj=self.mainObj.data.DBconnect[self.databaseName]
                self.collections = self.mainObj.COLlist[dbName]             
                lblDBname = tk.Label(collFrame, text=dbName, font= ('Segoe 11 bold'), borderwidth=3, relief = SUNKEN, width=14, padx=1) #, relief = SOLID
                lblDBname.pack(anchor=W, padx=6) 
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
                self.colltreeview.pack(anchor=W, padx=6)
                
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
            self.addElemToList(coll, ind = self.recCnt  + 1)
            self.recCnt += 1          

        self.editFilter.affTot(str(self.recCnt) + "/" + str(self.recTot))
        #self.mainObj.objMainMess.clearMess()
        self.scrollrecFrame.scroll( scrollTo = '0')

    def addNewRecord(self): 
            if not self.isCollSelected():
                return            
            custom_dialog = eob.editOntopObj(self.mainObj.win, {}, title="Add JSON Object", editMode = True)
            res = custom_dialog.result        
            if res:
                try:
                    self.addElemToList(res[0], ind = self.recCnt  + 1)  
                    coll = self.dbObj[self.colNameSelect] 
                    doc = coll.insert_one(res[0])
                    self.updAffCnt(recCnt = 1, totCnt = 1)
                except pymongo.errors.OperationFailure as ex1:
                    self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                    return
                
    def addElemToList(self, coll, recFrame = None, ind = None):
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
        
        indLbl = Label(butFrame, text=str(ind), font=('Segoe 8 bold'), pady=1)
        indLbl.pack()
        
        butEdit = tk.Button(butFrame, text= "🖍", font= ('Calibri 11'), command= lambda listObj=recFrame, obj = coll, ind = ind: self.editRec( listObj, obj, ind)) 
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
            try:
                res=self.dbObj[self.colNameSelect]
                res.delete_one({"_id": rec_id})
                listObj.destroy()
                self.updAffCnt(recCnt = -1, totCnt = -1)
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return
                
    def delAllRecord(self):
        if not self.isCollSelected():
            return    
        answer = askyesno(title='Remove records ?',
            message='Remove all (' + str(self.recTot) + ') collection\'s records.')
        if answer:
            try:
                res=self.dbObj[self.colNameSelect]
                res.delete_many({})
                self.showRec(newRec=True)
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return        
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

            try:            
                if not isValid:                              # If keyword is not valid, return with empty records list
                    self.resetList()
                    self.recList = []
                    return
                if self.keyObj != keyObj or newRec:          # Clear records list if filter change and count records
                    self.keyObj = keyObj
                    self.resetList()
                    self.recTot = self.dataObj.count_documents(keyObj)             

                res = self.dataObj.find(keyObj).sort("_id",-1).skip(self.recSkip).limit(self.recLimit)  
                self.recList = list(res) 
                self.recSkip += len(self.recList)
                
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return
                
    def updAffCnt(self, recCnt = 0, totCnt = 0):
        self.recCnt += recCnt
        self.recTot += totCnt
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
        except pymongo.errors.OperationFailure as ex1:  
            self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
            return

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

            
    def editRec(self, listObj, obj, ind = None):
        #txtLog=event.widget.get("1.0",END)
        #pdb.set_trace()
        custom_dialog = eob.editOntopObj(self.mainObj.win, obj, title="Edit JSON Object", editMode = True)
        res = custom_dialog.result 
        self.mainObj.objMainMess.clearMess()
        if res:
            obj = res[0]
            typTrx = res[1]
            #pdb.set_trace()
            coll = self.dbObj[self.colNameSelect]   # Set data object collection
            try:
                if typTrx == 1:
                    objCopy = obj.copy()
                    ID = objCopy['_id']   #getID
                    del objCopy['_id']
                    doc = coll.delete_one({ '_id': obj['_id']})
                    obj['_id'] = ID
                    doc = coll.insert_one(obj)
                    self.addElemToList(obj, recFrame = listObj, ind = ind)                
                elif typTrx == 2:
                    #print("delete")
                    #pdb.set_trace()
                    doc = coll.delete_one({ '_id': obj['_id']})
                    listObj.destroy()
                    self.updAffCnt(recCnt = -1, totCnt = -1)
                    #self.scrollrecFrame.scroll()
                elif typTrx == 3:
                    #print("insert")
                    doc = coll.insert_one(obj)
                    self.addElemToList(obj, ind = ind)
                    self.updAffCnt(recCnt = 1, totCnt = 1)
            except pymongo.errors.OperationFailure as ex1:
                self.mainObj.objMainMess.showMess(ex1.details.get('errmsg', ''))
                return
            except Exception as ex:
                self.mainObj.objMainMess.showMess(str(ex))
                return              
            return res
    
    def resetList(self):
        self.recTot = 0
        self.recCnt = 0
        self.recSkip = 0      