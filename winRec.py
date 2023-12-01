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
from tkinter.scrolledtext import ScrolledText

from tkcalendar import Calendar
from tkinter import font as tkFont  
from idlelib.tooltip import Hovertip

import cdControl as cdc

# JSON
from bson import ObjectId
import json
import phonetics
import webbrowser


class editerRecette():
    def __init__(self, masterForm, recData, EDITOK):
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
        self.EDITOK = EDITOK
        
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

        self.butPing.grid(column=1, row=0, sticky=tk.W, padx=5)
        self.butMing.grid(column=2, row=0, sticky=tk.W, padx=5)
        self.butEditIngr.grid(column=3, row=0, sticky=tk.W, padx=5)
        self.butPprep.grid(column=1, row=0, sticky=tk.W, padx=5)
        self.butMprep.grid(column=2, row=0, sticky=tk.W, padx=5)
        self.butEditprep.grid(column=3, row=0, sticky=tk.W, padx=5)
        
        self.imageObj.editImgage()

   
    def modifControl(self, slavelist):
        #pdb.set_trace()
        for elem in slavelist:
            if isinstance(elem, tk.Entry) or isinstance(elem, ttk.Checkbutton) or isinstance(elem, ttk.Combobox) :
                elem['state'] = 'normal'
                elem['cursor'] = ''
                if isinstance(elem, tk.Entry):
                    elem['foreground'] = 'black'
                    elem['font'] = ('Segoe 9 normal')
                    elem.unbind('<Enter>')
                    elem.unbind('<Leave>')
                elem.bind("<FocusIn>", self.handle_focus)
                elem.unbind('<Button-1>')
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
        elem.focus()
        if edList == "prep":
            self.scrollframe.scroll()
        
        
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

        def on_enter(e):
            e.widget.config(foreground= "red")

        def on_leave(e):
            e.widget.config(foreground= 'blue')
            
        #valMax20 = (self.win.register(self.validate), '%P', 10)
        editArr = []


        self.pop = tk.Toplevel(self.win)
        #self.pop.attributes('-fullscreen', True)
        self.masterForm.childWin.append(self.pop)
        self.pop.title(self.recData["nom"])
        self.pop.iconbitmap(RECICON)

        self.objMess = cdc.messageObj(self.pop, height=25)
        
        recframe = cdc.resizeFrame(self.pop, borderwidth = 1, relief=RIDGE, pack=False)
        recframe.pack(fill=X, padx=10)
        self.editFrame = recframe

        self.scrollframe = cdc.VscrollFrame(self.pop)
        self.scrollframe.pack(expand= True, fill=BOTH) 

        
        sdc = cdc.milliToDate(self.recData["dateC"])
        ttk.Label(recframe, text="Créé: " + sdc, font=('Calibri 8')).grid(column=0, row=1, sticky=tk.W, padx=5, pady=3)
        sdc = cdc.milliToDate(self.recData["dateM"])
        ttk.Label(recframe, text="Modifié :" + sdc, font=('Calibri 8')).grid(column=1, row=1, sticky=tk.W, padx=5, pady=3)
        #pdb.set_trace()
        self.imgframe = tk.Frame(recframe, borderwidth = 1, relief=RIDGE)
        self.imgframe.grid(row=1, column=2, rowspan=6, sticky=tk.E, padx=25)
        
        if not "imgURL" in self.recData or self.recData["imgURL"] == '' or self.recData["imgURL"] == 'undefined':
            imgURL = ""
        else:
            imgURL = self.recData["imgURL"]
            
        self.imageObj = cdc.imageObj(self.pop, self.imgframe, imgURL, (12,4))
        
        
        ttk.Label(recframe, text='Nom:').grid(column=0, row=2, sticky=tk.W, padx=5, pady=3)
        self.varNom = StringVar()
        self.varNom.set(self.recData["nom"])
        recName = cdc.editEntry(recframe, textvariable=self.varNom, state="readonly", width=30, maxlen=50)
        recName.focus()
        recName.grid(column=1, row=2, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varNom", self.varNom))
        
        ttk.Label(recframe, text='Categorie:').grid(column=0, row=3, sticky=tk.W, padx=5, pady=3) 
        varCat = StringVar()
        varCat.set(self.recData["cat"]["desc"])
        comboCat = ttk.Combobox( recframe, textvariable=varCat, state="disable")
        self.masterForm.loadCombo(comboCat, self.recData["cat"]["desc"])
        comboCat.grid(column=1, row=3, sticky=tk.W, padx=5, pady=3) 
        editArr.append(("varCat", varCat))

                
        ttk.Label(recframe, text='Préparation:').grid(column=0, row=4, sticky=tk.W, padx=5, pady=3)
        varPrep = StringVar()
        varPrep.set(self.recData["temp"])
        recPrep = cdc.editEntry(recframe, textvariable=varPrep, state="readonly", width=20, validate="key", maxlen=15)
        recPrep.grid(column=1, row=4, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varPrep", varPrep))
        
        ttk.Label(recframe, text='Temps de cuisson:').grid(column=0, row=5, sticky=tk.W, padx=5, pady=3)
        varCuis = StringVar()
        varCuis.set(self.recData["cuis"])
        recCuis = cdc.editEntry(recframe, textvariable=varCuis, state="readonly", width=20, maxlen=15)
        recCuis.grid(column=1, row=5, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varCuis", varCuis))
        
        ttk.Label(recframe, text='Portions:').grid(column=0, row=6, sticky=tk.W, padx=5, pady=3)
        varPort = StringVar()
        varPort.set(self.recData["port"])
        recPort = cdc.editEntry(recframe, textvariable=varPort, state="readonly", width=20, maxlen=15)
        recPort.grid(column=1, row=6, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varPort", varPort))
        
        ttk.Label(recframe, text='Source URL:').grid(column=0, row=7, sticky=tk.W, padx=5, pady=3)
        
        varURL = StringVar()
        varURL.set(self.recData["url"])
        recURL = cdc.editEntry(recframe, textvariable=varURL, state="readonly", width=90, maxlen=200, font= ('Segoe 9 underline'), fg="#0000FF")
        recURL.grid(column=1, row=7, columnspan=2, sticky=tk.W, padx=5, pady=3)
        editArr.append(("varURL", varURL))
        if self.recData["url"]:
            recURL.bind("<Button-1>", lambda event, url=self.recData["url"]: self.webCall(event, url))
            recURL.config(cursor="hand2")
            recURL.bind('<Enter>', on_enter)
            recURL.bind('<Leave>', on_leave)

        ttk.Label(recframe, text='Publié:').grid(column=0, row=8, sticky=tk.W, padx=5, pady=3)
        indPublie = tk.StringVar()
        indPublie_check = ttk.Checkbutton(
            recframe,
            text='',
            variable=indPublie,
            state="disable",
            onvalue=1,
            offvalue=0)
        indPublie.set(self.recData["state"])
        indPublie_check.grid(column=1, row=8, sticky=tk.W, padx=5, pady=3)
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
        
        
        self.butframe = tk.Frame(self.pop, pady=5)
        self.butframe.pack(expand= True, side=LEFT, fill=X, anchor=CENTER)
        self.butEdit = tk.Frame(self.butframe)
        self.butEdit.pack()
        #print(self.masterForm.userRole)
        if self.masterForm.userRole == "ADM" or self.masterForm.userRole == "MEA" :
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
        self.winDim()

        
    def winDim(self):
        self.win.update_idletasks()                                                             ##update_idletasks
        w=self.pop.winfo_width()
        h=self.scrollframe.interior.winfo_height() + 300
        if (self.win.winfo_screenheight() - 80) < h :
            h = self.win.winfo_screenheight() - 80
            self.pop.geometry("+50+0")  #Placer au top
        else:
            #print(str(self.win.winfo_screenheight() - 80) + "   H = " + str(h + self.pop.winfo_y()))
            if self.win.winfo_screenheight() - 80  < h + self.pop.winfo_y():
                adj = (h + self.pop.winfo_y()) - (self.win.winfo_screenheight() - 80)
                h -= adj
                #print( str(adj) + "   H = " + str(h ))
                
        self.pop.geometry(f"{w}x{h}")

        
    def add_ingr(self, listIngr = None):
        #pdb.set_trace()
        if not listIngr is None:        # From Class editWin.saveListElem()
            self.recData["ingr"] = listIngr
            if self.ingrFrame:
                for elem in self.ingrFrame.slaves():
                    if isinstance(elem, tk.Entry):
                        elem.destroy()

        else:               # Premier appel
            self.ingrFrame = cdc.resizeFrame(self.scrollframe.interior, borderwidth = 1, relief=RIDGE, pack=False)
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
            ingr.pack(expand= True, fill=BOTH, padx=5, pady=3)
            ingr.bind("<FocusIn>", self.handle_focus)
            rown += 1
        
        if not listIngr is None:
            self.modifControl(self.ingrFrame.slaves())
            
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

    def webCall(self, e, url):
        if url:
            webbrowser.open_new_tab(url)           


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
