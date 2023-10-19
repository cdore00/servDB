# coding=utf-8
#https://stackoverflow.com/questions/71677889/create-a-scrollbar-to-a-full-window-tkinter-in-python
#https://pyinstaller.org/en/stable/usage.html#cmdoption-hidden-import
#pyinstaller main.py --onefile --name test --icon test.ico --noconsole
#Mise à jour et sécurité/Sécurité Windows/Protection contre les virus/Gérer les paramètres/Protection en temps réel
#Scripts\pyinstaller win64MD.py --onefile --name golf --noconsole
#Scripts\pyinstaller  -F --add-data C:\Users\charl\AppData\Local\Programs\Python\Python39\tcl\tix8.4.3;tcl\tix8.4.3 win64MD.py
#C:\Users\charl\AppData\Local\Programs\Python\Python39\Scripts
#scripts\pyinstaller --onefile code\win64MD.py
import pdb
#; pdb.set_trace()

import sys, os, io, re, cgi, csv, urllib.parse
import json
import time 
import datetime
from sys import argv

from bson.json_util import dumps

from tkinter import *
import tkinter as tk
from tkinter import * 
from tkinter import tix

from tkinter import messagebox, TclError, ttk
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
from idlelib.tooltip import Hovertip

import urllib
import urllib.request
import dropbox, base64
from PIL import ImageTk, Image
import webbrowser

import cdControl as cdc
import winGolf as wg

# JSON
from bson import ObjectId

#from bson.json_util import dumps
#from bson.json_util import loads
import json
import phonetics

# MongoDB
import pymongo
from pymongo import MongoClient

EDITOK = False
APPICON = 'C:/Users/charl/github/cuisine/misc/favicon.ico'

class editerRecette():
    def __init__(self, masterForm, recData, *args, **kwargs):
        self.INGR = "Ingrédients"
        self.PREP = "Préparation"
        self.win = masterForm.win
        self.masterForm = masterForm
        self.recData = recData
        self.editList = {}
        self.pop = None
        self.focusElem = None
        self.ingrFrame = None
        self.imageObj = None
        
        self.showRecette()
        
    def saveNew(self):
        self.recData.pop("_id")
        self.masterForm.data.addRecette(self.recData)        
        self.masterForm.getDataList()
        
        
    def save(self):
       
        self.recData["nom"] = self.editList["varNom"].get()
        self.recData["temp"] = self.editList["varPrep"].get()
        self.recData["cuis"] = self.editList["varCuis"].get()
        self.recData["port"] = self.editList["varPort"].get()
        self.recData["url"] = self.editList["varURL"].get()
        cat = self.editList["varCat"].get()
        self.recData["cat"]["desc"] = cat
        self.recData["cat"]["_id"] = self.masterForm.comboList[cat]
        self.recData["state"] = int(self.editList["indPublie"].get())
        
        self.recData["nomU"] = cdc.scanName(self.recData["nom"])
        self.recData["nomP"] = phonetics.metaphone(self.recData["nom"])
        self.pop.title(self.recData["nom"])
        
        #Ingrédients
        #pdb.set_trace()
        ingArr = []
        rown = 0
        for ing in self.recData["ingr"]:
            ingArr.append(self.editList["ingr"][rown].get())
            rown += 1            

        self.recData["ingr"] = ingArr
        
        Uvals = []  #ingrédients upper case
        Pvals = []  #ingrédients phonetic
        for x in ingArr:
            Uval = cdc.scanName(x)
            Uvals.append(Uval)
            mots = Uval.split()
            Pmots = ''
            for m in mots:
                if m.isnumeric() == False and len(m) > 2:
                    Pmots = Pmots + phonetics.metaphone(m) + ' '
            Pvals.append(Pmots)
        self.recData["ingrU"] = Uvals
        self.recData["ingrP"] = Pvals
 
        #pdb.set_trace()
        
        #Préparation
        prepArr = []
        rown = 0
        for elem in self.editList["prep"]:
            if elem[1].winfo_exists():
                prepArr.append(elem[1].get("1.0", END))
            
        self.recData["prep"] = prepArr
        
        ref = self.imageObj.saveImage()
        if ref:
            self.recData["imgURL"] = ref

        if self.recData["_id"] == "NEW":
            self.saveNew()
            return
            
        self.masterForm.data.saveRecette(self.recData)        
        self.masterForm.getDataList()
        
        self.objMess.showMess("Enregistré!")
        self.winDim()


    def delRec(self):
        #pdb.set_trace()
        answer = askyesno(title='Suppression',
            message='Supprimer la recette : ' + self.recData['nom'])
        if answer:
            self.masterForm.data.deleteRecette(self.recData["_id"])        
            self.masterForm.getDataList()
            self.pop.destroy()
        
        
    def modify(self, forNew = False):
        #pdb.set_trace()
        self.butEdit.pack_forget()
        self.butModif = tk.Frame(self.butframe)
        self.butModif.pack()
        butAnn = ttk.Button(self.butModif, text="Annuler", command=self.annuler, width=20 )  #.pack()
        butAnn.grid(row=0, column=0, padx=5, sticky="WE")        
        butEnr = ttk.Button(self.butModif, text="Enregistrer", command=self.save, width=20 )  #.pack()
        butEnr.grid(row=0, column=1, padx=5, sticky="WE")
        
        self.modifControl(self.editFrame.grid_slaves())
        self.modifControl(self.ingrFrame.slaves()) 

        slavelist = self.prepFrame.slaves()
        for elem in slavelist:
            elem.destroy()
        #pdb.set_trace()
        if not forNew:
            self.editList["prep"] = self.add_prep()
        else:
            self.add_prep(forNew)
        self.winDim()

        self.butPing.grid(column=1, row=0, sticky=tk.W, padx=5)
        self.butMing.grid(column=2, row=0, sticky=tk.W, padx=5)
        self.butEditIngr.grid(column=3, row=0, sticky=tk.W, padx=5)
        self.butPprep.grid(column=1, row=0, sticky=tk.W, padx=5)
        self.butMprep.grid(column=2, row=0, sticky=tk.W, padx=5)
        self.butEditprep.grid(column=3, row=0, sticky=tk.W, padx=5)
        
        self.imageObj.editImgage()
        self.winDim()

   
    def modifControl(self, slavelist):
        for elem in slavelist:
            if isinstance(elem, tk.Entry) or isinstance(elem, ttk.Checkbutton) or isinstance(elem, ttk.Combobox) :
                elem['state'] = 'normal'
                elem.bind("<FocusIn>", self.handle_focus)
                if isinstance(elem, ttk.Combobox):
                    elem.config(state="readonly")

    
    def newRec(self):
        
        self.modify(True)
        self.pop.title("Nouvelle recette")
        
        slavelist = self.ingrFrame.slaves()
        for elem in slavelist:
            if not isinstance(elem, tk.Frame):
                elem.destroy()


        self.editList["varNom"].set("")
        self.editList["varPrep"].set("")
        self.editList["varPort"].set("")
        self.editList["varCuis"].set("")
        self.editList["indPublie"].set(0)

        self.editList["varURL"].set("")
        
        k=self.masterForm.comboList.keys()
        for key in k:
            x=key
            break

        self.editList["varCat"].set(x)

        self.recData["_id"] = "NEW"
        self.recData["ingr"] = []
        self.editList["ingr"] = []
        self.recData["prep"] = []
        self.editList["prep"] = []   
        if "hist" in self.recData:
            self.recData.pop("hist")
        self.imageObj.deleteImage()
        
        self.winDim()

                
    def annuler(self):   
        self.pop.destroy()
        

    def handle_focus(self, event):
        if event.widget == self.pop:
            #print("Focus on POP:   Widget=" + str(event.widget))
            self.focusElem = None
        else:
            self.focusElem = event.widget
            #print("I have gained the focus:   Widget=" + str(event.widget))
        self.objMess.clearMess()

    def addElem(self, section):
        #pdb.set_trace()
        if section == self.INGR:
            parentframe = self.ingrFrame
            edList = "ingr"
            elem = tk.Entry(parentframe)
            self.editList["ingr"].append(elem)
            self.recData["ingr"].append("")
        else:
            parentframe = self.prepFrame
            edList = "prep"
            elem = ScrolledText(parentframe, height=1)
        
        
        self.editList[edList].append(["", elem])
        
        elem.pack(expand= True, fill=BOTH, padx=5, pady=3)
        elem.bind("<FocusIn>", self.handle_focus)     
        self.winDim()
        
        
    def deleteElem(self, section):

        isChild = False
        if not self.focusElem is None:
            if section == self.INGR:
                isChild = self.focusElem.nametowidget(self.focusElem.winfo_parent()) == self.ingrFrame
                objToDestroy = self.focusElem
            else:
                obj = self.focusElem.nametowidget(self.focusElem.winfo_parent())
                isChild = obj.nametowidget(obj.winfo_parent()) == self.prepFrame
                objToDestroy = obj
        
        if isChild:
             if section == self.INGR:
                self.recData["ingr"].pop(self.recData["ingr"].index(objToDestroy.get()))     
             objToDestroy.destroy()
             self.focusElem = None
        else:
            messagebox.showinfo(
                title="Suppression de quelle ligne ?",
                message=f"Veuillez sélectionner une ligne dans la section " + section + ".")     

    def editListElem(self, section):
        if section == self.INGR:
            winEdit = editWin(self.pop, "Éditer " + section, [self, self.recData["ingr"], self.INGR])
        else:
            winEdit = editWin(self.pop, "Éditer " + section, [self,self.recData["prep"], self.PREP])
        winEdit.showDialog()
        

 
    def showRecette(self):

        #valMax20 = (self.win.register(self.validate), '%P', 10)
        editArr = []

        self.pop = tk.Toplevel(self.win)
        #self.pop.attributes('-fullscreen', True)
        self.masterForm.recetteWin.append(self.pop)
        self.pop.title(self.recData["nom"])
        if os.path.exists(APPICON):
            self.pop.iconbitmap(APPICON)
  
        self.scrollframe = cdc.VscrollFrame(self.pop)
        self.scrollframe.pack(expand= True, fill=BOTH) 

        self.objMess = cdc.messageObj(self.scrollframe.interior)
        
              
        #recframe = tk.Frame(self.scrollframe.interior, borderwidth = 1, relief=RIDGE)
        #recframe.pack(expand= True, fill=BOTH)
        
        recframe = cdc.resizeFrame(self.scrollframe.interior, borderwidth = 1, relief=RIDGE)
        #recframe.pack(expand= True, fill=BOTH)
        
        self.editFrame = recframe
        
        sdc = cdc.milliToDate(self.recData["dateC"])
        ttk.Label(recframe, text="Créé: " + sdc, font=('Calibri 8')).grid(column=0, row=0, sticky=tk.W, padx=5, pady=3)
        sdc = cdc.milliToDate(self.recData["dateM"])
        ttk.Label(recframe, text="Modifié :" + sdc, font=('Calibri 8')).grid(column=1, row=0, sticky=tk.W, padx=5, pady=3)
        #pdb.set_trace()
        self.imgframe = tk.Frame(recframe, borderwidth = 1, relief=RIDGE)
        self.imgframe.grid(row=0, column=2, rowspan=6, sticky=tk.E, padx=25)
        
        if not "imgURL" in self.recData or self.recData["imgURL"] == '' or self.recData["imgURL"] == 'undefined':
            imgURL = ""
        else:
            imgURL = self.recData["imgURL"]
            
        self.imageObj = cdc.imageObj(self.pop, self.imgframe, imgURL, (12,4))
        
        
        ttk.Label(recframe, text='Nom:').grid(column=0, row=1, sticky=tk.W, padx=5, pady=3)
        self.varNom = StringVar()
        self.varNom.set(self.recData["nom"])
        #recName = tk.Entry(recframe, textvariable=self.varNom, state="readonly", width=30)
        recName = cdc.editEntry(recframe, textvariable=self.varNom, state="readonly", width=30, maxlen=50)
        recName.focus()
        recName.grid(column=1, row=1, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varNom", self.varNom))
        #cdc.menuEdit(self.win, recName)
        
        ttk.Label(recframe, text='Categorie:').grid(column=0, row=2, sticky=tk.W, padx=5, pady=3) 
        varCat = StringVar()
        varCat.set(self.recData["cat"]["desc"])
        comboCat = ttk.Combobox( recframe, textvariable=varCat, state="disable")
        self.masterForm.loadCombo(comboCat, self.recData["cat"]["desc"])
        comboCat.grid(column=1, row=2, sticky=tk.W, padx=5, pady=3) 
        editArr.append(("varCat", varCat))

                
        ttk.Label(recframe, text='Préparation:').grid(column=0, row=3, sticky=tk.W, padx=5, pady=3)
        varPrep = StringVar()
        varPrep.set(self.recData["temp"])
        #recPrep = tk.Entry(recframe, textvariable=varPrep, state="readonly", width=20, validate="key", validatecommand=(self.win.register(self.validate), '%P', 10))
        recPrep = cdc.editEntry(recframe, textvariable=varPrep, state="readonly", width=20, validate="key", maxlen=15)
        recPrep.grid(column=1, row=3, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varPrep", varPrep))
        #cdc.menuEdit(self.win, recPrep)
        
        ttk.Label(recframe, text='Temps de cuisson:').grid(column=0, row=4, sticky=tk.W, padx=5, pady=3)
        varCuis = StringVar()
        varCuis.set(self.recData["cuis"])
        recCuis = cdc.editEntry(recframe, textvariable=varCuis, state="readonly", width=20, maxlen=15)
        recCuis.grid(column=1, row=4, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varCuis", varCuis))
        #cdc.menuEdit(self.win, recCuis)
        
        ttk.Label(recframe, text='Portions:').grid(column=0, row=5, sticky=tk.W, padx=5, pady=3)
        varPort = StringVar()
        varPort.set(self.recData["port"])
        recPort = cdc.editEntry(recframe, textvariable=varPort, state="readonly", width=20, maxlen=15)
        recPort.grid(column=1, row=5, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varPort", varPort))
        #cdc.menuEdit(self.win, recPort)
        
        ttk.Label(recframe, text='Source URL:').grid(column=0, row=6, sticky=tk.W, padx=5, pady=3)
        varURL = StringVar()
        varURL.set(self.recData["url"])
        recURL = cdc.editEntry(recframe, textvariable=varURL, state="readonly", width=90, maxlen=200)
        recURL.grid(column=1, row=6, columnspan=2, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varURL", varURL))
        #cdc.menuEdit(self.win, recURL)
        
        ttk.Label(recframe, text='Publié:').grid(column=0, row=7, sticky=tk.W, padx=5, pady=3)
        indPublie = tk.StringVar()
        indPublie_check = ttk.Checkbutton(
            recframe,
            text='',
            variable=indPublie,
            state="disable",
            onvalue=1,
            offvalue=0)
        indPublie.set(self.recData["state"])
        indPublie_check.grid(column=1, row=7, sticky=tk.W, padx=5, pady=3)
        editArr.append(("indPublie", indPublie))

        editArr.append( ( "ingr", self.add_ingr() ) )
        
        self.prepFrame = tk.Frame(self.scrollframe.interior, borderwidth = 1, relief=RIDGE)
        lbl = ttk.Label(self.prepFrame, text=self.PREP, font=('Calibri 15 bold'))
        lbl.pack(expand= True, fill=BOTH, padx=10, anchor=W)
        
        rown = 1
        for pre in self.recData["prep"]:
            val = self.recData["prep"][rown - 1]
            th = int(len(val)/90) + 1
            var = tk.StringVar()
            var.set(val)
            prep = Text(self.prepFrame, width=50, height= th)
            
            prep.insert(INSERT, self.recData["prep"][rown - 1])
            prep.config(state="disabled", bg="#EEEEEE")
            prep.pack(expand= True, fill=BOTH, anchor=NW, padx=5, pady=3)
            rown += 1
        
        self.prepFrame.pack(expand= True, fill=BOTH, padx=10, pady=10)
        
        
        self.butframe = tk.Frame(self.scrollframe.interior)
        self.butframe.pack(expand= True, fill=BOTH, anchor=CENTER)
        self.butEdit = tk.Frame(self.butframe)
        self.butEdit.pack()
        if EDITOK:
            butAnn = ttk.Button(self.butEdit, text="Annuler", command=self.annuler, width=15 ) 
            butAnn.grid(row=0, column=0, padx=5, sticky="WE")        
            butMod = ttk.Button(self.butEdit, text="Modifier", command=self.modify, width=15 ) 
            butMod.grid(row=0, column=1, padx=5, sticky="WE") 
            butNew = ttk.Button(self.butEdit, text="Ajouter", command=self.newRec, width=15 ) 
            butNew.grid(row=0, column=2, padx=5, sticky="WE") 
            butDel = ttk.Button(self.butEdit, text="Supprimer", command=self.delRec, width=15 ) 
            butDel.grid(row=0, column=3, padx=5, sticky="WE") 
        else:
            butAnn = ttk.Button(self.butEdit, text="Fermer", command=self.annuler, width=15 ) 
            butAnn.grid(row=0, column=0, padx=5, sticky="WE")            

        self.editList = dict(editArr)
        
        #Positionner la fenêtre de consulation/édition de la recette
        self.winDim(True)

        
    def winDim(self, adjustPosition = False):
        self.win.update_idletasks()                                                             ##update_idletasks
        #w=self.scrollframe.interior.winfo_width()
        w=self.pop.winfo_width()
        h=self.scrollframe.interior.winfo_height() + 20
        if (self.win.winfo_screenheight() - 80) < h:
            h = self.win.winfo_screenheight() - 80
            if adjustPosition:
                self.pop.geometry("+50+0")
        self.pop.geometry(f"{w}x{h}")        

        
    def add_ingr(self, listIngr = None):
    
        if not listIngr is None:        # From Class editWin.saveListElem()
            
            self.recData["ingr"] = listIngr
            if self.ingrFrame:
                for elem in self.ingrFrame.slaves():
                    if isinstance(elem, tk.Entry):
                        elem.destroy()
                #pdb.set_trace()
                self.modifControl(self.ingrFrame.slaves()) 
        else:               # Premier appel
            self.ingrFrame = cdc.resizeFrame(self.scrollframe.interior, borderwidth = 1, relief=RIDGE, pack=False)
            #self.ingrFrame = tk.Frame(self.scrollframe.interior, borderwidth = 1, relief=RIDGE)
            self.ingrFrame.pack(expand= True, fill=BOTH, padx=10, pady=10)
        
            headFrm = tk.Frame(self.ingrFrame)
            headFrm.pack(expand= True, fill=X, padx=10, anchor=W)
            lbl=ttk.Label(headFrm, text=self.INGR, font=('Calibri 15 bold'), width=10)
            lbl.grid(column=0, row=0, sticky=tk.W, padx=5)
            self.butPing = Button(headFrm, text='  +  ', command= lambda: self.addElem(self.INGR), font=('Calibri 15 bold'))
            self.butMing = Button(headFrm, text='  -  ', command= lambda: self.deleteElem(self.INGR), font=('Calibri 15 bold'))   
            self.butEditIngr = Button(headFrm, text='Éditer', command= lambda: self.editListElem(self.INGR), font=('Calibri 15 bold')) 
        
        ingVal = []
        rown = 1
        for ing in self.recData["ingr"]:
            ingVal.append(self.recData["ingr"][rown - 1])
            ingVal[rown - 1] = tk.StringVar()
            ingVal[rown - 1].set(self.recData["ingr"][rown - 1])
            ingr = cdc.editEntry(self.ingrFrame, textvariable= (ingVal[rown - 1]), state="readonly", maxlen=100)
            #ingr = tk.Entry(self.ingrFrame, textvariable= (ingVal[rown - 1]), state="readonly")
            ingr.pack(expand= True, fill=BOTH, padx=5, pady=3)
            ingr.bind("<FocusIn>", self.handle_focus)
            #cdc.menuEdit(self.win, ingr)
            rown += 1

        
        return ingVal
        
    def add_prep(self, forNew = False):
        #self.prepFrame = tk.Frame(self.scrollframe.interior, borderwidth = 1, relief=RIDGE)

        headFrm = tk.Frame(self.prepFrame)
        headFrm.pack(expand= True, fill=X, padx=10, anchor=W)
        lbl=ttk.Label(headFrm, text=self.PREP, font=('Calibri 15 bold'), width=10)
        lbl.grid(column=0, row=0, sticky=tk.W, padx=5)
        self.butPprep = Button(headFrm, text='  +  ', command= lambda: self.addElem(self.PREP), font=('Calibri 15 bold'))
        self.butMprep = Button(headFrm, text='  -  ', command= lambda: self.deleteElem(self.PREP), font=('Calibri 15 bold'))
        self.butEditprep = Button(headFrm, text='Éditer', command= lambda: self.editListElem(self.PREP), font=('Calibri 15 bold')) 
        
        if forNew:
            return
        else:
            return self.add_prepElem()


    def add_prepElem(self):
        prepVal = []
        rown = 1
        for x in self.recData["prep"]:
            prepVal.append(self.recData["prep"][rown - 1])
            prep = ScrolledText(self.prepFrame, height=1)
            prep.insert('1.0',self.recData["prep"][rown - 1])
            prepVal[rown - 1] = [ self.recData["prep"][rown - 1], prep]
            prep.pack(expand= True, fill=BOTH, padx=5, pady=3)
            prep.bind("<FocusIn>", self.handle_focus)
            cdc.menuEdit(self.win, prep)
            rown += 1
        
        self.prepFrame.pack(expand= True, fill=BOTH, padx=10, pady=10)
        return prepVal    
    
class master_form_find():
    def __init__(self, mainApp, *args, **kwargs):
        self.mainApp = mainApp
        self.win = self.mainApp.win
        self.frame = self.mainApp.masterForm
        self.data = self.mainApp.dbObj
        self.winGame = None
        self.recetteWin = []
        self.comboList = {}
        self.comboData = {}
        self.comboCat = None
        self.gridFrame = None
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        if "Recettes"  in self.mainApp.actAppDB:
            self.isRec = True
        else:
            self.isRec = False   

        
            
        formframe = self.add_input_frame()
        formframe.grid(column=0, row=0)
        formframe = self.add_button_frame()
        formframe.grid(column=1, row=0)      


    def loadCombo(self, comboObj = None, val = None):
        if self.data.isConnect:    
            if comboObj != None:
                 cat_list = list(self.comboList.keys())
                 comboObj["values"] = cat_list
                 if val != None:
                    comboObj.current(cat_list.index(val))
            else:
                if self.isRec:
                    li = (self.data.getCat())
                    fld = "desc"
                else:
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
                if self.isRec:
                    self.comboCat.current(1)
                else:
                    self.comboCat.current(0)
            return True
        else:
            return False
        
    def getDataList(self, event = None):
        if self.data.isConnect:        
            wrd = self.keyword.get()
            indI = int(self.indIngr.get())
            cat = self.comboCat.get()


            if cat == "Toutes":
                cat = 0
            else:
                cat = self.comboList[cat]
                
            if wrd == '' and cat == 0 and not self.isRec:
                messagebox.showinfo(
                    title="Recherche",
                    message=f"Veuillez sélectionner critère ")             
                return
                
                
            if self.isRec:
                oData = (self.data.searchRecettes(wrd, indI, cat))
                listItems = oData["data"]
                colW = [10, 3, 3, 3, 3, 1]
                colH = ["Nom", "Catégorie", "Temps prép.", "Cuisson", "Portion", "Publié"]
                colB = ["Nom de la recette", "Catégorie de la recette", "Temps de préparation", "Temps de cuission", "Nombre de portions", "Non publié"]
            else:         
                oData = (self.data.searchClubs(wrd, indI, cat))
                listItems = oData["data"]                             
                colW = [4, 1, 1, 7, 3, 3]
                colH = ["Club", "Parc.", "Trous", "Adresse", "Ville", "Région"]
                colB = ["Nom du club", "Nombre de parcours", "Nombre de trous", "Adresse du club", "Ville du club", "Région du club"]

            mess = str(len(listItems)) + (" recettes trouvées " if self.isRec else " clubs trouvés ")
            if len(listItems) <= 1:
                mess = str(len(listItems)) + (" recette trouvé " if self.isRec else " club trouvé ")
            if wrd:
                mess += "où"
                if oData["ph"]:
                    mess += " la phonétique"
                mess += " « " + wrd + " » est contenu dans le nom " + ("de la recette" if self.isRec else "du club")
                if indI:
                    mess += (" ou les ingrédients de la recette" if self.isRec else " ou la ville du club")                   
            #pdb.set_trace()
            if cat:
                mess += (" dans la catégorie " if self.isRec else " dans la région ") + self.comboCat.get()
            mess += "."
            self.mainApp.win.objMainMess.showMess(mess, '#0c0')    

            if len(self.gridFrame.interior.slaves()) > 0:
                self.gridFrame.interior.slaves()[0].destroy()
            
            gridframe = tk.Frame(self.gridFrame.interior)
            gridframe.pack(expand= True, side=LEFT, fill=X, padx=10)

            gridframe.grid_columnconfigure(0, weight=colW[0], uniform="True")
            gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
            lbl = tk.Label(gridframe, text=colH[0], bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE )
            lbl.grid(row=0, column=0, sticky=tk.NSEW)
            Hovertip(lbl,colB[0])
            #tip1.bind_widget(lbl,balloonmsg=colB[0])

            gridframe.grid_columnconfigure(1, weight=colW[1], uniform="True")
            gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
            lbl = tk.Label(gridframe, text=colH[1], bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE)
            lbl.grid(row=0, column=1, sticky=tk.NSEW)   
            Hovertip(lbl,colB[1])
            #tip2.bind_widget(lbl,balloonmsg=colB[1])

            gridframe.grid_columnconfigure(2, weight=colW[2], uniform="True")
            gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
            lbl = tk.Label(gridframe, text=colH[2], bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE)
            lbl.grid(row=0, column=2, sticky=tk.NSEW)     
            Hovertip(lbl,colB[2])       
            #tip3.bind_widget(lbl,balloonmsg=colB[2])

            gridframe.grid_columnconfigure(3, weight=colW[3], uniform="True")
            gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
            lbl = tk.Label(gridframe, text=colH[3], bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE)
            lbl.grid(row=0, column=3, sticky=tk.NSEW)  
            Hovertip(lbl,colB[3])      
            #tip4.bind_widget(lbl,balloonmsg=colB[3])

            gridframe.grid_columnconfigure(4, weight=colW[4], uniform="True")
            gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
            lbl = tk.Label(gridframe, text=colH[4], bg="lightgrey", padx=5, pady=10, borderwidth = 1, relief=RIDGE)
            lbl.grid(row=0, column=4, sticky=tk.NSEW) 
            Hovertip(lbl,colB[4])      
            #tip5.bind_widget(lbl,balloonmsg=colB[4])

            gridframe.grid_columnconfigure(5, weight=colW[5], uniform="True")
            gridframe.grid_rowconfigure(0, weight=1, uniform="True")  
            lbl = tk.Label(gridframe, text=colH[5], bg="lightgrey", padx=1, pady=10, borderwidth = 1, relief=RIDGE, anchor=W)
            lbl.grid(row=0, column=5, sticky=tk.NSEW) 
            Hovertip(lbl,colB[5]) 
            #tip6.bind_widget(lbl,balloonmsg=colB[5])
            
            
            rowN = 1
            if self.isRec:
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
            else:
                for x in listItems:
                    if x["url_club"] != "":
                        lbl = tk.Label(gridframe, text= x["nom"], font= ('Segoe 9 underline'), fg="#0000FF", pady=1, borderwidth = 1, relief=RIDGE, anchor=W)
                        lbl.grid(row= rowN, column=0, sticky="WE")        
                        lbl._values = [x["_id"], x["url_club"]]
                        lbl.bind("<Button-1>", lambda event, val=1: self.webCall(event, val))
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
        else:
            messagebox.showinfo(
                title="Non connecté",
                message=f"Veuillez sélectionner une autre connexion.")  

    def webCall(self, e, val = 0):
        id = e.widget._values
        if val:
            url = id[val]
        else:
            url = "https://cdore.ddns.net/ficheClub.html?data=" + str(id[val])
        
        webbrowser.open_new_tab(url)

        
    def gridCall(self, e):
        id = e.widget._values
        #print(str(id))
        rec = self.data.getReccette(id)
        winEdit = editerRecette(self, (rec)[0])

    def resetForm(self):
        self.keyword.delete(0, END)
        self.keyword.insert(0, "")
        self.indIngr.set(1)
        self.comboCat.current(0)
        self.keyword.focus()
        
    def add_input_frame(self):

        formframe = tk.Frame(self.frame)
        
        if self.isRec:
            comboLbl = 'Catégorie:'
            ind_lbl = '(rechercher parmi les ingrédients)'
        else:
            comboLbl = 'Région:'
            ind_lbl = '(rechercher parmi les villes)'
        

        # Mots clés recherche
        ttk.Label(formframe, text='Mots clés:').grid(column=0, row=0, sticky=tk.W)
        self.keyword = ttk.Entry(formframe, width=30)
        self.keyword.focus()
        self.keyword.grid(column=1, row=0, sticky=tk.W)
        self.keyword.bind("<Return>", self.getDataList)
        #self.keyword.bind('<Button-3>',popup) # Bind a func to right click
        cdc.menuEdit(self.win, self.keyword)
        
        button = cdc.RoundedButton(formframe, 25, 25, 10, 2, 'lightgrey', "#EEEEEE", command=self.resetForm)
        button.create_text(12,11, text="x", fill="black", font=('Helvetica 15 '))
        button.grid(column=2, row=0)
        Hovertip(button,"Blanchir le formulaire")

        
        self.indIngr = tk.StringVar()
        self.indIngr.set(1)
        ind_check = ttk.Checkbutton(
            formframe,
            text=ind_lbl,
            variable=self.indIngr,
            onvalue=1,
            offvalue=0)
        
        ind_check.grid(column=1, row=1, sticky=tk.W, padx=5, pady=3)
        
        # Combo Categorie

        ttk.Label(formframe, text= comboLbl).grid(column=0, row=4, sticky=tk.W)
        combo = ttk.Combobox(
            formframe,
            state="readonly",
            values=[""]
            )

        combo.grid(column=1, row=4, sticky=tk.W)
        self.comboCat = combo
        self.loadCombo()
        
        for widget in formframe.winfo_children():
            widget.grid(padx=5, pady=5)
            
        if not self.isRec:
            ttk.Button(formframe, text='Parties', command=self.getGames).grid(column=2, row=4)

        return formframe

    def getGames(self):
        #pdb.set_trace()
        if self.winGame is None or self.winGame.isDestroy:
            self.winGame = wg.listGames(self)
        else:
            self.winGame.winDim()

 
    def add_button_frame(self):

        formframe = tk.Frame(self.frame)
        ttk.Button(formframe, text='Rechercher', command=self.getDataList).grid(column=0, row=0)
        ttk.Button(formframe, text='Connecter', command=self.login).grid(column=0, row=3)
        
        ttk.Button(formframe, text='Fermer', command=self.closeRec).grid(column=0, row=4)
        ttk.Button(formframe, text="Quitter", command=self.quitForm).grid(column=0, row=5)

        for widget in formframe.winfo_children():
            widget.grid(padx=5, pady=5)

        return formframe

    def closeRec(self):
        for winR in self.recetteWin:
            winR.destroy()
    
    def quitForm(self):
        self.frame.quit()

    def login(self):
        dial = loginDialog(self.win, "Connecter : app - location", self.mainApp)
        dial.showDialog()
        
    def setGrid(self, listFrame):
        self.gridFrame = listFrame
        if self.isRec:
            self.getDataList()

 
class dbaseObj():
    def __init__(self, *args, **kwargs):
        self.data = None
        self.dbase = ""
        self.server = {
            "Local": "mongodb://localhost:27017",
            "Vultr": ""
            }
        self.isConnect = False

    def connectTo(self, Server = "Local", dbName = "resto"):
        #pdb.set_trace()
        self.dbase = dbName
        uri = self.server[Server]
        try:
            DBclient = MongoClient(uri)
            
            DBclient.server_info()
            self.data = DBclient[self.dbase]
            self.isConnect = True
        except:
            self.isConnect = False

        
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

class editWin(cdc.modalDialogWin):
    def createWidget(self):
        self.parent = self.obj[0]
        self.dataElem = self.obj[1]
        self.section = self.obj[2]
        
        editList = ScrolledText(self.dframe)
        cdc.menuEdit(self.win, editList)
        
        elemList = ""

        for elem in self.dataElem:
            elemList += elem + "\n"
        editList.insert('1.0',elemList)
        editList.pack( padx=5, pady=3)  #fill=BOTH,     expand= True, fill=X, anchor=CENTER, padx=5, pady=3
        editList.focus()

        butframe = tk.Frame(self.dframe, pady=5, padx=5)
        butframe.pack(fill=X)
        butEdit = tk.Frame(butframe)
        butEdit.pack( padx=15)
        buttonC = ttk.Button(butEdit, text="Ok", command=  lambda: self.saveListElem(editList), width=10) 
        buttonC.grid(row=1, column=0, padx=5, sticky="WE") 
        buttonC = ttk.Button(butEdit, text="Annuler", command=self.close, width=10)
        buttonC.grid(row=1, column=1, padx=5, sticky="WE")


    def saveListElem(self, elemData):
        #pdb.set_trace()
 
        dat=elemData.get("1.0", END)
        datArr = dat.split("\n")
        while '' in datArr:
            datArr.remove('')

        if self.section == self.parent.INGR:
            self.parent.editList["ingr"] = self.parent.add_ingr(datArr)
        if self.section == self.parent.PREP:
            slavelist = self.parent.prepFrame.slaves()
            rown = 0
            for elem in slavelist:
                if rown > 0:
                    elem.destroy() 
                rown += 1

            self.parent.recData["prep"] = datArr
            self.parent.editList["prep"] = self.parent.add_prepElem()
        self.parent.winDim()
        self.close()
        
class loginDialog(cdc.modalDialogWin):
    def createWidget(self):
        self.mainApp = self.obj
        self.pop.resizable(0, 0)
        self.actApp  = "Recettes"
        self.actServ = "Local"
        #pdb.set_trace()
        self.labAct = Label(self.dframe, text="Actuel : " + self.mainApp.actAppDB, font=('Calibri 12 bold'), pady=5)
        self.labAct.grid(row=0, column=0, columnspan=2, sticky=EW)
        button1 = Button(self.dframe, text="Recettes - Local", command= lambda: self.selectAppDB("Recettes", "Local"), width=30, cursor="hand2")
        button1.grid(row=1, column=0, columnspan=2)
        button2 = Button(self.dframe, text="Recettes - Vultr", command= lambda: self.selectAppDB("Recettes", "Vultr"), width=30, cursor="hand2")
        button2.grid(row=2, column=0, columnspan=2)
        button3 = Button(self.dframe, text="Golf - Local", command= lambda: self.selectAppDB("Golf", "Local"), width=30, cursor="hand2")
        button3.grid(row=3, column=0, columnspan=2)
        button4 = Button(self.dframe, text="Golf - Vultr", command= lambda: self.selectAppDB("Golf", "Vultr"), width=30, cursor="hand2")
        button4.grid(row=4, column=0, columnspan=2)
        
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

    def selectAppDB(self, app = "Recettes", serv = "Local"):
        self.actApp  = app
        self.actServ = serv
        self.labAct.config(text="Actuel = " + app + " - " + serv)
        
    def setAppDB(self):  
        self.close()
        self.mainApp.setApp(self.actServ, self.actApp)
        


class createMasterForm():
    def __init__(self, win, connectOn = True, *args, **kwargs):
        self.win = win
        self.dbObj = dbaseObj()
        self.appdbName = { "Golf": "golf",
                            "Recettes": "resto"}
        self.listRecettes = None
        self.mForm = None

        self.setApp(connectApp = connectOn)
    
    def setApp(self, serv = "Vultr", appName = "Recettes", connectApp = True):
        self.actAppDB = appName + " - " + serv
        self.win.update_idletasks()       
        self.win.title(self.actAppDB)
        
        if not self.mForm is None:
            self.mForm.closeRec()
        slavelist = self.win.slaves()
        for elem in slavelist:
            elem.destroy()
            
        self.win.objMainMess = cdc.messageObj(self.win)
        self.win.objMainMess.showMess("Connexion...")
        self.win.update_idletasks() 
        #pdb.set_trace()
        if connectApp:
            self.dbObj.connectTo(serv, self.appdbName[appName])
        self.win.objMainMess.clearMess()

        if appName == "Recettes":
            self.win.geometry("550x500")
        else:
            self.win.geometry("600x500")
 
        self.masterForm = tk.Frame(self.win, borderwidth = 1, relief=RIDGE)
        self.masterForm.pack( fill=X, padx=10, pady=10)
                
        self.mForm = master_form_find(self)        
        self.listRecettes = cdc.VscrollFrame(self.win)
        self.listRecettes.pack(expand= True, fill=BOTH)
        self.mForm.setGrid(self.listRecettes)
        

def create_main_window():

    win = tix.Tk()
    win.minsize(480,300)
    #win.resizable(0, 0)
    if os.path.exists(APPICON):
        win.iconbitmap(APPICON)
    l = int(win.winfo_screenwidth() / 2)
    win.geometry(f"+{l}+100")
    
    createMasterForm(win, connectOn = True)

    win.mainloop()

if __name__ == "__main__": 
    if len(argv) > 1:
        arg = [x for x in argv]
        param = arg[1]
        if param.isnumeric():
            Pvalid = 260658 + datetime.datetime.today().day
            if int(param) == Pvalid:
                EDITOK = True
              
    create_main_window()
    
