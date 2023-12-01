# coding=utf-8

import pdb
#; pdb.set_trace()
import sys, os, io, re, cgi, csv, urllib.parse
import json
import time 
import datetime
#from re import compile, IGNORECASE

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

                    
class listUsers():
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
        self.headLbl = ["ID ", "Nom ", "Rôle ", "Publié"]
        self.headConfig = [{"type": "C", "length": 20}, {"type": "C", "length": 15}, {"type": "C", "length": 4}, {"type": "C", "length": 2} ]
        self.comboNiveauVal = [0]
        self.skip = 0
        self.isDestroy = False
        self.showUsers()
        
    def showUsers(self):
    
        self.pop = tk.Toplevel(self.win)
        #self.pop.overrideredirect(True)
        #second_win.protocol('WM_DELETE_WINDOW',lambda: onclose(second_win))
        self.pop.protocol('WM_DELETE_WINDOW',self.destroyRef)

        self.pop.title("Utilisateurs")
        self.pop.iconbitmap(APPICON)   
        
        # Search form 
        self.formFrame = tk.Frame(self.pop, borderwidth = 1, relief=RIDGE)
        self.formFrame.pack(fill=X)
        self.formFrame.grid_columnconfigure(0, weight=1)

        
        # Grid list frame
        self.scoreframe = cdc.VscrollFrame(self.pop)
        self.scoreframe.pack(expand= True, fill=BOTH)
        
        recframe = cdc.resizeFrame(self.formFrame, pack=False)
        #recframe.pack(fill=X, padx=10, pady=10, anchor=W) 
        recframe.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
        
        self.varMot = StringVar()
        self.varMot.set("")
        txtMot = cdc.editEntry(recframe, textvariable=self.varMot, maxlen=20)
        txtMot.focus()
        txtMot.bind("<Return>", self.resetList)
        txtMot.pack(expand= True, fill=BOTH, padx=5, pady=3)        
        
        butFrame = tk.Frame(self.formFrame)
        butFrame.grid(row=0, column=1, padx=5, pady=5)
        butReset = cdc.RoundedButton(butFrame, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.resetList)
        butReset.create_text(12,11, text="🔄", fill="black", font=('Helvetica 17 '))
        butReset.grid(row=1, column=1, sticky=tk.W)
        Hovertip(butReset,"Réinitialiser la liste")        

        butNext = ttk.Button(butFrame, text="Suivant", command=self.nextUsers, width=9 ) 
        butNext.grid(row=1, column=2, padx=5, sticky="WE") 
        
        butNext = ttk.Button(butFrame, text="Fermer", command=self.destroyRef, width=9 ) 
        butNext.grid(row=1, column=3, padx=5, sticky="WE")
        self.nextUsers()
        self.winDim()

    def listUsers(self, mot, skip, limit):
        #pdb.set_trace()
        
        # Grid users
        #pdb.set_trace()
        if not self.gridframe is None:
            self.gridframe.destroy()
            self.gridframe = None
        else:
            headFrame = tk.Frame(self.scoreframe.interior)
            headFrame.pack( fill=X, padx=10)
            headFrame.grid_columnconfigure(0, weight=4, uniform="True")
            headFrame.grid_columnconfigure(1, weight=3, uniform="True")
            headFrame.grid_columnconfigure(2, weight=1, uniform="True")       
            headFrame.grid_columnconfigure(3, weight=1, uniform="True")
            self.sortObj = cdc.sortGridObj(headFrame, headLabels = self.headLbl, headConfig = self.headConfig)

        #pdb.set_trace()
        dataList = self.getUsersList(mot, skip, limit)
        rowN = 0
        
        gridframe = tk.Frame(self.scoreframe.interior)
        gridframe.pack( fill=X, padx=10)
        self.gridframe = gridframe

        self.sortObj.setGridframe(gridframe)
        
        gridframe.grid_columnconfigure(0, weight=4, uniform="True")
        gridframe.grid_columnconfigure(1, weight=3, uniform="True")
        gridframe.grid_columnconfigure(2, weight=1, uniform="True")
        gridframe.grid_columnconfigure(3, weight=1, uniform="True")
        for x in dataList:
            #print(x)
            lbl = tk.Label(gridframe, text= x["courriel"], font= ('Segoe 9 underline'), fg="#0000FF", pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
            lbl.grid(row= rowN, column=0, sticky="WE")  
            lbl._values = x["_id"]
            lbl.bind("<Button-1>", self.showUser)
            lbl = tk.Label(gridframe, text= x["Nom"], pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
            lbl.grid(row= rowN, column=1, sticky="WE")
            lbl._values = x["_id"]
            lbl.bind("<Double-Button-1>", self.showUser)
            lbl = tk.Label(gridframe, text= x["niveau"], pady=1, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=2, sticky="WE")
            lbl._values = x["_id"]
            lbl.bind("<Double-Button-1>", self.showUser)
            bgc = "#EEEEEE" if (x["actif"]) else "#FFFF00"
            lbl = tk.Label(gridframe, text= "", pady=1, bg= bgc, borderwidth = 1, relief=RIDGE, anchor=CENTER)
            lbl.grid(row= rowN, column=3, sticky="WE")
            lbl._values = x["_id"]
            lbl.bind("<Double-Button-1>", self.showUser)            
            rowN += 1        
            
        #print(str(rowN))
        if rowN < limit:
            self.skip = 0
            #print("reset rowN: " + str(rowN) + "  limit: " + str(limit))
        else:
            self.skip += limit
                
        
    def nextUsers(self, noskip = False):
        nbr = 20
        mot = self.varMot.get()
        
        if noskip:
            self.skip -= nbr
        if self.skip < 0:
            self.skip = 0
                   
        self.listUsers( mot=mot, skip=self.skip, limit=nbr)
        
   
    def clearForm(self):
        self.varMot.set("")
        self.comboNiveau.current(0)
        self.comboNbr.current(2)
        self.comboTrou.current(0)
        self.varLimit.set("")

    def resetList(self, e = None):
        self.skip = 0
        self.nextUsers()
       
    
    def getUsersList(self, mot, skip, limit):
        #pdb.set_trace()
        coll = self.data.users

        reqRegx, req = {}, {}
        if mot:
            reqRegx = {"$or": [ {"Nom": {"$regex": '.*' + mot + '.*'} } , {"courriel": {"$regex": '.*' + mot + '.*'} } ]}
            req = {"$or": [ {"Nom": mot } , {"courriel": mot}   ]}

        docs = coll.find(req).collation({"locale": "fr","strength": 1}).sort("courriel",1).skip(skip).limit(limit)
        res = list(docs)
        if len(res) == 0:
            docs = coll.find(reqRegx).sort("courriel",1).skip(skip).limit(limit)
            return list(docs)
        else:
            return res

    def getUser(self, userID):
        
        if userID.isnumeric():
            gID = int(userID)
        else:
            gID = ObjectId(userID)
        coll = self.data.users
        doc = coll.find({"_id":gID})
        return list(doc)[0]

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
        self.win.update_idletasks()
        #self.pop.attributes('-topmost', True)
        #self.pop.attributes('-topmost', False)        
        
    def destroyRef(self, e=None):
        #print("isDestroy")
        self.isDestroy = True
        self.pop.destroy()
        
             
    def showUser(self, event):
        id = event.widget._values
        winUser = winShowUser(self, id)

    def deleteUser(self, oID):
        col = self.data.users
        doc = col.delete_one({"_id": oID })
        self.nextUsers(True)
        return (doc.raw_result)

    def saveUser(self, oRec):
        col = self.data.users
        oID = oRec["_id"]
        doc = col.update_one({ '_id': oID}, { '$set': oRec },  upsert=True )
        self.nextUsers(True)
        return (doc.raw_result)

    def addUser(self, oRec):
        col = self.data.users
        doc = col.insert_one(oRec)
        self.nextUsers(True)
        return (doc.inserted_id)
        
        
class winShowUser():
    def __init__(self, winListUsers, id):
        self.win = winListUsers.win      
        self.winListUsers = winListUsers
        self.masterForm = winListUsers.masterForm
        self.roleList = ['ADM', 'MEA', 'MEM']
        self.editUser(id)

        
    def editUser(self, id):
        self.recData = self.winListUsers.getUser(str(id))
        #print(self.recData)
        
        editArr = []
        self.pop = tk.Toplevel(self.winListUsers.pop)
        self.pop.title("Éditer utilisateur")
        self.pop.iconbitmap(APPICON)
        self.masterForm.childWin.append(self.pop)

        self.objMess = cdc.messageObj(self.pop, height=25)
        
        recframe = cdc.resizeFrame(self.pop, borderwidth = 1, relief=RIDGE, pack=False)
        recframe.pack(fill=X, padx=10)
        self.editFrame = recframe


        sdc = cdc.milliToDate(self.recData["dateC"])
        ttk.Label(recframe, text="Créé: " + sdc, font=('Calibri 8')).grid(column=0, row=0, sticky=tk.W, padx=5, pady=3)
        sdc = cdc.milliToDate(self.recData["dateM"])
        ttk.Label(recframe, text="Modifié : " + sdc, font=('Calibri 8')).grid(column=1, row=0, sticky=tk.W, padx=5, pady=3)
        #pdb.set_trace()
        self.imgframe = tk.Frame(recframe, borderwidth = 1, relief=RIDGE)
        self.imgframe.grid(row=0, column=2, rowspan=6, sticky=tk.E, padx=25)
        
        if not "imgUser" in self.recData or self.recData["imgUser"] == '' or self.recData["imgUser"] == 'undefined':
            imgUser = ""
        else:
            imgUser = self.recData["imgUser"]
            
        self.imageObj = cdc.imageObj(self.pop, self.imgframe, imgUser, (12,4))        
        self.imageObj.editImgage()
        
        ttk.Label(recframe, text='Courriel:').grid(column=0, row=1, sticky=tk.W, padx=5, pady=3)
        varMail = StringVar()
        varMail.set(self.recData["courriel"])
        recMail = cdc.editEntry(recframe, textvariable=varMail, width=30, maxlen=50)
        recMail.grid(column=1, row=1, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varMail", varMail))
        recMail.focus()
        
        ttk.Label(recframe, text='Nom:').grid(column=0, row=2, sticky=tk.W, padx=5, pady=3)
        self.varNom = StringVar()
        self.varNom.set(self.recData["Nom"])
        recName = cdc.editEntry(recframe, textvariable=self.varNom, width=30, maxlen=50)
        recName.grid(column=1, row=2, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varNom", self.varNom))
        
        ttk.Label(recframe, text='Rôle:').grid(column=0, row=3, sticky=tk.W, padx=5, pady=3) 
        comboRole = ttk.Combobox( recframe, state="readonly")
        comboRole["values"] = self.roleList
        comboRole.current(self.roleList.index(self.recData["niveau"]))
        comboRole.grid(column=1, row=3, sticky=tk.W, padx=5, pady=3) 
        editArr.append(("varRole", comboRole))
        #pdb.set_trace()
        
        ttk.Label(recframe, text='Mot de passe:').grid(column=0, row=4, sticky=tk.W, padx=5, pady=3)
        varPass = StringVar()
        varPass.set(self.recData["motpass"])
        recPass = cdc.editEntry(recframe, textvariable=varPass, width=20, maxlen=15)
        recPass.grid(column=1, row=4, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varPass", varPass))

        ttk.Label(recframe, text='Publié:').grid(column=0, row=5, sticky=tk.W, padx=5, pady=3)
        self.indActif = tk.BooleanVar()
        self.indActif.set(self.recData["actif"])      
        indActif_check = ttk.Checkbutton(
            recframe,
            text='',
            variable=self.indActif)
        editArr.append(("indActif", self.indActif))
        #indActif_check.instate(['selected'])
        indActif_check.grid(column=1, row=5, sticky=tk.W, padx=5, pady=3)
        
        self.editList = dict(editArr)
        
        self.butframe = tk.Frame(self.pop, pady=5)
        self.butframe.pack(expand= True, side=LEFT, fill=X, anchor=CENTER)
        self.butEdit = tk.Frame(self.butframe)
        self.butEdit.pack()

        butAnn = ttk.Button(self.butEdit, text="Annuler", command=self.annuler, width=15 ) 
        butAnn.grid(row=0, column=0, padx=5, sticky="WE")        
        butMod = ttk.Button(self.butEdit, text="Enregister", command=self.saveUser, width=15 ) 
        butMod.grid(row=0, column=1, padx=5, sticky="WE") 
        butNew = ttk.Button(self.butEdit, text="Ajouter", command=self.newUser, width=15 ) 
        butNew.grid(row=0, column=2, padx=5, sticky="WE") 
        butDel = ttk.Button(self.butEdit, text="Supprimer", command=self.delUser, width=15 ) 
        butDel.grid(row=0, column=3, padx=5, sticky="WE")                         
        
    def annuler(self):   
        self.pop.destroy()

    def saveUser(self):   
        #pdb.set_trace()
        self.recData["courriel"] = self.editList["varMail"].get()
        self.recData["Nom"] =      self.editList["varNom"].get()
        self.recData["niveau"] =   self.editList["varRole"].get()
        self.recData["motpass"] = self.editList["varPass"].get()
        self.recData["actif"] =    self.editList["indActif"].get()
        dt = datetime.datetime.now()    #Date actuelle
        self.recData["dateM"] = dt.timestamp() * 1000
        #self.recData["dateC"] = 1500600000000
        #pdb.set_trace()
        #self.recData["userID"] = self.masterForm.user[0]
        
        ref = self.imageObj.saveImage()
        if ref:
            self.recData["imgUser"] = ref

        if self.recData["courriel"] == "" or self.recData["Nom"] == "" or self.recData["motpass"] == "" :
            messagebox.showinfo(
            title="Valeurs obligatoires",
            message=f"Toutes les valeurs sont obligatoires.") 
        else:
            if not "_id" in self.recData:
                self.recData["dateC"] = dt.timestamp() * 1000
                self.winListUsers.addUser(self.recData)
                self.objMess.showMess("Utilisateur ajouté.", "I")                
            else:
                self.winListUsers.saveUser(self.recData)
                self.objMess.showMess("Enregistré.", "I")

    def newUser(self):  
        self.pop.title("Ajouter un utilisateur")
        self.editList["varMail"].set("")
        self.editList["varNom"].set("")
        self.editList["varPass"].set("")
        self.editList["indActif"].set(False)
        self.recData["imgUser"] = ""
        self.recData.pop("_id")
        self.imageObj = cdc.imageObj(self.pop, self.imgframe, "", (12,4)) 
        
    def delUser(self):   
        answer = askyesno(title='Suppression',
            message="Supprimer l'utilisateur : " + self.recData['courriel'])
        if answer:
            self.winListUsers.deleteUser(self.recData["_id"])        
            self.pop.destroy()      
        