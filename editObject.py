import pdb
import tkinter as tk
from tkinter import * 
from tkinter import messagebox, TclError, ttk
import json
from bson import ObjectId
from bson.json_util import dumps
from idlelib.tooltip import Hovertip
from decimal import *
from decimal import Decimal
from bson.decimal128 import Decimal128
import pyperclip as cp
from tkinter import simpledialog
from datetime import datetime

import cdControl as cdc
    
typList  = ['list',  'bool',   'datetime',  'Decimal128' , 'float', 'int' , 'Int64' , 'dict', 'ObjectId', 'set',     'str',  'Timestamp',  'tuple']
typListS = ['Array', 'Boolean',  'Datetime', 'Decimal', 'Float', 'Int32', 'Int64', 'Object', 'ObjectId', 'BSONset', 'String', 'Timestamp',  'Tuple']


class editJsonObject():
    def __init__(self, win, recObj, parentFrame = None, withButton = "", saveCallback = None, messObj = None, editMode = False ):
        self.win = win
        self.mainFrame = parentFrame
        self.withButton = withButton  # Options 'S' South = default, 'N' North, 'E' East, 'W' West and optionnal 'I' Icon format
        self.objMainMess = messObj
        self.initData = recObj.copy()
        self.dictObj = recObj
        self.indNew = False
        self.typeTrx = 1
        if not self.initData:    #Add new
            self.initData["_id"] = ObjectId()
            self.indNew = True
            self.typeTrx = 3
        #self.editMode = editMode
        self.saveCallback = saveCallback
        self.error = None
        self.newEl = None
        self.listOpen = []
        
        if self.mainFrame is None:
            self.mainFrame = tk.Frame(self.win, bg='blue')   #, bg='blue', borderwidth=3, relief = RIDGE
            self.mainFrame.pack(expand=1, fill=BOTH, padx = 1, pady = 10, side = TOP) #expand=1, fill=BOTH
 
        self.createFrmEdit(editMode = editMode)   
        
    def on_input_change(self, event=None):
        ctl = event.widget
        w =len(ctl.get())
        ctl.config( width=w+1)
        
    def on_text_change(self, event=None):
        #pdb.set_trace()
        ctl = event.widget
        w =len(ctl.get("1.0", "end-1c"))
        lineCnt = ctl.get("1.0", "end-1c").count('\n')
        ctl.configure(height=(lineCnt + 1))
        ctl.config( width=w+1)   #/(lineCnt+1))

    def addRecord(self, parentFrm, key, elemObj, getFocus = None):
        elemArr = []
        #pdb.set_trace()
        typ = elemObj.__class__.__name__
        #print("typ= " + typ)
        elemFrame = tk.Frame(parentFrm)  #, bg="red"
        elemFrame.pack(expand=1, fill="x", padx = 5)
        elemFrame.columnconfigure(0, weight=0)
        elemFrame.columnconfigure(1, weight=0)
        elemFrame.columnconfigure(2, weight=1)
        elemFrame.columnconfigure(3, weight=0)

        try:
            key_in = tk.Entry(elemFrame, width=len(str(key))+1)
            key_in.grid(row= 0, column=0, sticky="NW")
            key_in.insert(tk.END, str(key))
            if key.__class__.__name__ == "int" or key == "_id" or not self.editMode:
                key_in.config( relief="flat")
                key_in.config( state="disabled")
            
            if self.editMode:
                key_in.bind("<KeyPress>", self.on_input_change)
                cdc.menuEdit(self.win, key_in)
            elemArr.append(key_in)
            if getFocus :
                key_in.focus()
            lbl = tk.Label(elemFrame, text= ":")
            lbl.grid(row= 0, column=1, sticky=NW)
            
            h = 1 if typ != 'str' else int(len(elemObj) / 50) + 1
            w = 10
            if typ != "dict" and typ != "list":
                w = len(str(elemObj))+1
            text_in = tk.Text(elemFrame, wrap="word", width=w, height=h)
            text_in.grid(row= 0, column=2, sticky="W")
            if typ == "bool":
                elemObj='True' if elemObj else 'False'
            if typ == "tuple":
                elemObj = str(elemObj)
            if typ == "Timestamp":
                x=1
                #pdb.set_trace()
            if typ == "dict" or typ == "list" or (key == "_id" and not self.indNew):
                if typ == "dict":
                    text_in.insert(tk.END, "Object")
                if typ == "list":
                    text_in.insert(tk.END, "Array(" + str(len(elemObj)) + ")")
                if key == "_id":
                    text_in.insert(tk.END, elemObj) 
                #pdb.set_trace()
                if self.typeTrx != 3:
                    text_in.config( relief="flat")
                    text_in.config( state="disabled")
                    text_in.config( bg="#eee")
            else:
                text_in.insert(tk.END, elemObj)
                text_in.bind("<KeyPress>", self.on_text_change)
            
            if self.editMode:
                cdc.menuEdit(self.win, text_in)
            else:
                text_in.config( relief="flat")
                text_in.config( state="disabled")
                text_in.config( bg="#eee")            
            elemArr.append(text_in)
            #pdb.set_trace()
            comboType = None
            if self.editMode:
                comboType = ttk.Combobox(
                    elemFrame,
                    width=8,
                    state="readonly",
                    values = typListS
                    )
                comboType.grid(row= 0, column=3, padx=5)
                comboType.current(typList.index(typ))             
                elemArr.append(comboType)  #typ
                
                if key == "_id" and not self.indNew:
                    comboType.config( state="disabled")
            else:
                typeVar = StringVar()
                typeVar.set(typ)
                elemArr.append(typeVar)
                
        except Exception as ex:
            self.objMainMess.showMess(str(ex))
            
        return elemArr, comboType 

    def addFrame(self, pFrm):
        mFrm = tk.Frame(pFrm)  #, bg="red", height=2
        mFrm.columnconfigure(0, weight=0)
        mFrm.columnconfigure(1, weight=0)
        mFrm.columnconfigure(2, weight=0)
        mFrm.columnconfigure(3, weight=1)
        
        fCol1 = tk.Frame(mFrm, width=10)
        fCol1.grid(row= 0, column=0, sticky="NW")
        if self.editMode:
            delBut = tk.Label(fCol1, text= "🗑")
        else:
            delBut = tk.Label(fCol1, text= "")
        delBut.pack()
        
        fCol2 = tk.Frame(mFrm, width=10)
        fCol2.grid(row= 0, column=1, sticky="NW")
        if self.editMode:
            ctrlBut = tk.Label(fCol2, text= "➕")
        else:
            ctrlBut = tk.Label(fCol2, text= "")
        ctrlBut.pack()

        expBut = None
        
        fCol3 = tk.Frame(mFrm, width=5)
        fCol3.grid(row= 0, column=2, sticky="NW")
        expBut = tk.Label(fCol3, text= "   ")
        expBut.pack()

        mFrm.pack(expand=1, fill="x")

        return mFrm, delBut, ctrlBut, expBut

    def showHide(self, e, frm, arrP, key):
        #pdb.set_trace()
        expBut = e if isinstance(e,(Label)) else e.widget
        slavelist = frm.slaves()
        cnt = len(slavelist)
        
        def hide():
            expBut.config( text="▼")
            for ind, elem in enumerate(slavelist):
                if ind > 0:
                    if not elem in arrP:
                        arrP.append(elem)
                    elem.pack_forget()   
            
            if key in self.listOpen:
                self.listOpen.remove(key)
                #print("Hide " + key + "  self.listOpen= " + str(self.listOpen))
            
        def show():
            expBut.config( text="▲")
            for ind, elem in enumerate(arrP):
                if elem.winfo_exists():
                    elem.pack(expand=1, fill="x", padx = 5) 
            self.listOpen.append(key)
            #print("Show " + key + "  self.listOpen= " + str(self.listOpen))
            
        if not self.newEl is None:
            hide()
            arrP.insert(0,self.newEl)
            show()
            self.newEl = None
            return

        if cnt == 1:
            show()
        else:
            hide()
        #self.win.update_idletasks()

    def delElement(self, e, frm, arrP, ind):
        #pdb.set_trace()
        frm.destroy()
        self.arrToDel.append([arrP, arrP[ind]])

    def changeType(self, event, frm, elemArr):
        #pdb.set_trace()
        key = elemArr[0].get()
        elemObj = self.convertdata(elemArr)
        frm.slaves()[0].destroy()
        elArr = self.addElement(key, elemObj, elemArr, rowFrame = frm)
        res = cdc.get_parent(self.dictArr, elemArr, niv=[])
        res[0][res[1]] = elArr[0]
        self.savedata()
        #print('changeType')
        

    def addNewRecord(self, e, frm, dictArr, key, rootInd):
        el=e.widget.master.master.master
        slavelist=e.widget.master.master.master.master.slaves()
        fp = False
        arrF = []
        for ind, elem in enumerate(slavelist):
            if fp.__class__.__name__ == 'int':
                arrF.append(elem)   
                elem.pack_forget()
            if elem == el:  # Found where to insert
                fp = ind    # Index where to insert
                key = -1 if key.__class__.__name__ == 'int' else ""
                newEl = self.addElement(key, "", dictArr, el.master, getFocus = True)
        #pdb.set_trace()
        if fp < ind:
            dictArr.insert(fp+rootInd, newEl[0])
        else:
            dictArr.append(newEl[0])
        for ind, elem in enumerate(arrF):
            elem.pack(expand=1, fill="x", padx = 5)

    def addNewChildRecord(self, e, frm, dictArr, key, rootInd, expB):     
        el=e.widget.master.master.master
        slavelist=e.widget.master.master.master.master.slaves()
        #if not dictArr:
        #    dictArr=self.dictArr
        for ind, elem in enumerate(slavelist):
            if elem == el:  # Found where to insert
                #pdb.set_trace()
                key = -1 if dictArr[ind-1+rootInd][2].get() == 'Array' else ""
                dArr=(dictArr[ind-1+rootInd][0].master.master.slaves())
                nc = dictArr[ind-1+rootInd][0].master.master  #.master.master   #.master
                break

        newEl = self.addElement(key, "", dArr, nc, getFocus = True, insert = True)      #el.master
        self.newEl = newEl[1]   # For the call showHide()
        expB.event_generate("<1>", x=1, y=1)
        """
        arrF = []
        for i, elem in enumerate(dArr):
            if i > 0:
                arrF.append(elem)   
                elem.pack_forget()  
        """
        fp = 0
        dictArr[ind-1+rootInd][3].insert(fp, newEl[0])   # [3] insert first list info element
        self.win.update_idletasks()
        """
        for i, elem in enumerate(arrF):
            elem.pack(expand=1, fill="x", padx = 5)
        """

    def addListMenu(self, event = None, frm=None, dictArr=None, key=None, rootInd=None, elFrm=None, expB=None):  #, recFrame, dictArr, key, rootInd
        self.addChoiceArr = [event, frm, dictArr, key, rootInd, elFrm, expB]
        self.menuAddChoice = Menu(self.win,tearoff=0) # Create a menu
        self.menuAddChoice.add_command(label="Add after '" + key + "'.", command=self.addAfterChoice)
        self.menuAddChoice.add_command(label="Add child to '" + key + "'.", command=self.addChildChoice)

        self.menuAddChoice.tk_popup(event.x_root,event.y_root) #event.x_root,event.y_root

    
    def addAfterChoice(self):
        self.addNewRecord(self.addChoiceArr[0], self.addChoiceArr[1], self.addChoiceArr[2], self.addChoiceArr[3], self.addChoiceArr[4])
        self.menuAddChoice.destroy()
        
    def addChildChoice(self):
        self.addNewChildRecord(self.addChoiceArr[0], self.addChoiceArr[1], self.addChoiceArr[2], self.addChoiceArr[3], self.addChoiceArr[4], self.addChoiceArr[5])
        self.menuAddChoice.destroy()
   
    def addElement(self, key, elemObj, dictArr, frm = None, rowFrame = None, getFocus = None, insert = False):    # Add recurring element
        #if frm:
        #    pdb.set_trace()
        if frm is None :
            rootInd = 1
            recFrame = self.recFrame 
        else:
            rootInd = 0
            recFrame = frm
        
        if not rowFrame:
            rowFrame = tk.Frame(recFrame, height=1)  #, bg="green"
            rowFrame.pack(expand=1, fill="x")  
        rowDataFrame, delBut, ctrlBut, expBut = self.addFrame(rowFrame)
        #print(str(expBut))
        
        elemFrame = tk.Frame(rowDataFrame, height=1)
        elemFrame.grid(row= 0, column=3, sticky="EW")        
        elemArr, comboType = self.addRecord( elemFrame, key, elemObj, getFocus = getFocus)   
        if  comboType:
            comboType.bind("<<ComboboxSelected>>", lambda event, frm=rowFrame, elemArr=elemArr :self.changeType(event, frm, elemArr))

        if key != "_id" and self.editMode:  # Show remove button if edit mode and not '_id' element
            ind = 0 if insert else len(dictArr)     # ind = 0 if new element is inserted in list or object collection
            delBut.bind("<Button-1>", lambda event, frm=rowFrame, arrP=dictArr, arrInd=ind: self.delElement(event, frm, arrP, arrInd))
        else:
            delBut.config( text="    ")

        if isinstance(elemObj, (dict)):
            childArr = []
            elemArr.append(childArr)
            self.addKeys(elemObj, childArr , elemFrame)
            arrP=[]
            expBut.bind("<Button-1>", lambda event, frm=elemFrame, arrP=arrP, key=key: self.showHide(event, frm, arrP, key))
            if not key in self.listOpen:
                self.showHide(expBut, elemFrame, arrP, key)
            else:
                expBut.configure(text= "▲")
        if isinstance(elemObj, (list)):
            childArr = []
            elemArr.append(childArr)
            self.addListItems(elemObj, childArr , elemFrame)
            arrP=[]
            expBut.bind("<Button-1>", lambda event, frm=elemFrame, arrP=arrP, key=key: self.showHide(event, frm, arrP, key))
            if not key in self.listOpen:
                self.showHide(expBut, elemFrame, arrP, key)            
            else:
                expBut.configure(text= "▲")
        if self.editMode:
            if isinstance(elemObj, (dict)) or isinstance(elemObj, (list)):
                #pdb.set_trace()
                ctrlBut.bind("<Button-1>", lambda event, frm=recFrame, dictArr=dictArr, key=key, rootInd=rootInd, expB=expBut: self.addListMenu(event, frm, dictArr, key, rootInd, expB))
            else:
                ctrlBut.bind("<Button-1>", lambda event, frm=recFrame, dictArr=dictArr, key=key, rootInd=rootInd: self.addNewRecord(event, frm, dictArr, key, rootInd))
        
        return [elemArr, rowFrame]


    def addListItems(self, listObj, dictArr, frm = None):   # Add recurring lists
        for ind, elem in enumerate(listObj):
            dictArr.append(self.addElement(ind, elem, dictArr, frm)[0])      

    def addKeys(self, dictObj, dictArr, frm = None):    # Add recurring dictionnarys
        k = list(dictObj.keys())
        for ind, key in enumerate(k):
            dictArr.append(self.addElement(key, dictObj[key], dictArr, frm)[0])


    def convertdata(self, elem):
        def delDead(elemList):
            for ind, el in enumerate(elemList):
                if not el[0].winfo_exists():
                    del elemList[ind]
                    delDead(elemList)
    
        try:
            #pdb.set_trace()
            typ = typList[typListS.index(elem[2].get())]
            #print(typ)
            data = elem[1].get("1.0", END)
            nlines = data.count('\n')
            if nlines == 1:
                data = data.replace("\n", "")
            data = data.strip()
            if typ != 'str':
                if typ == 'ObjectId':
                    data = ObjectId(data)
                if typ == 'int' or typ == 'Int64':
                    data = int(data)
                if typ == 'Decimal128':
                    data = Decimal128(data)   
                if typ == 'float':
                    data = float(data)
                if typ == 'datetime':
                    data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S.%f')
                if typ ==  'Timestamp':
                    pdb.set_trace()
                if typ == 'dict' or typ == 'list':                    
                    cle = "" if typ == 'dict' else "0"
                    if len(elem) == 3:  # Change type
                        elem.append([])
                    if typ == 'dict':
                        delDead(elem[3])
                        data = self.convertToDict(elem[3])
                    if typ == 'list':
                        delDead(elem[3])
                        data = self.convertToList(elem[3], True)
                    if len(elem) == 3:
                        print("change to list")
                        #pdb.set_trace()
                if typ == 'bool':
                    data = True if eval(data) else False
                if typ == "tuple" or typ == "set":
                    data = eval(data) 
            elif len(elem) == 4:
                #print("Convert list or object to string")
                data = ""
                for ind, elem in enumerate(elem[3]):
                    data += elem[1].get("1.0", END).replace("\n", "")
                    
        except Exception as ex:
            print("Convert list or object to string2")
            if 'typ' in locals():
                self.error = str(ex) + " with '" + typ + "' data type."    
            else:
                self.error = str(ex) + " Variable typ not exist."
            #pdb.set_trace()
            return ""
        return data
            
    def convertToList(self, listObj, isList = False):
        newObj = [] 
        #pdb.set_trace()
        for ind, elem in enumerate(listObj):
            data = self.convertdata(elem)
            if data is None:
                return None
            else:
                newObj.append(data)
        return newObj
        
    def convertToDict(self, listObj, isList = False): 
        newObj = {} 
        for ind, elem in enumerate(listObj):
            if not elem[0].get():   #Empty key
                self.error = "Empty object key not allowed."

            data = self.convertdata(elem)
            #print("data= " + str(data))
            #"""
            if data is None:
                return None
            else:
                newObj[elem[0].get()] = data
            #"""
            #newObj[elem[0].get()] = data    #new

        return newObj


    def savedata(self, updType = 1):       
        
        self.error = None
        if self.typeTrx > 1:
            updType = self.typeTrx
        else:
            self.typeTrx = updType
            
        if self.editMode:            
            if updType != 2:     # Not Remove data

                for ind, elem in enumerate(self.arrToDel):  # Remove deleted elements
                    elem[0].remove(elem[1])   
                self.dictObj = self.convertToDict(self.dictArr)
                
                if self.dictObj:
                    self.clearMainFrame()
                    self.initFrmEdit(self.dictObj, editMode = True)
                    if self.error:
                        self.clearMainFrame()
                        self.initFrmEdit(self.dictObj, editMode = True)
        #pdb.set_trace()
        #print(self.dictObj)

        if self.saveCallback:
            self.saveCallback(self.dictObj, updType)
        if self.error is None:
            return True
        else:    
            self.objMainMess.showMess(self.error)
            return False

    def getData(self):
        if self.editMode:
            self.savedata()
        trx = 0 if self.error else self.typeTrx
        return self.dictObj, trx
            
            
    def delData(self):
        self.clearMainFrame()
        self.typeTrx = 2
        self.initFrmEdit({}, editMode = True) 

        
    def copyData(self):
        data = self.dictObj
        if data is None:
            data = self.initData  
        data = json.dumps(data, default=str)
        cp.copy(data)
        self.objMainMess.showMess("JSON data copied to clipboard.", "I")
        #pdb.set_trace()
        x=1

    def cloneData(self):         
        data = self.dictObj
        data["_id"] = ObjectId() 
        self.clearMainFrame()
        self.typeTrx = 3
        self.indNew = True        
        self.initFrmEdit(data, editMode = True)
        self.objMainMess.showMess("JSON data cloned to :\n _id: " + str(data["_id"]), "I")
        
    def editData(self, editMode = True):
        self.editMode = True
        self.clearMainFrame()
        self.initFrmEdit(self.dictObj, editMode = editMode)
        
        
    def canceldata(self, editMode = False):
        self.typeTrx = 1
        self.editMode = False
        self.clearMainFrame()
        self.initFrmEdit(self.initData, editMode = editMode)

    def clearMainFrame(self):
        #if self.objMainMess is None:
        #    self.objMainMess.delete()
        self.dataFrame.destroy()
        if self.withButton:
            self.butFrame.destroy()        

    def showButtons(self, editMode = False):
            self.objMainMess.clearMess()
            self.butFrame = tk.Frame(self.butZone, height=1)  #, bg="red"
            self.butFrame.pack(expand=1, anchor=N)
            
            if 'I' in self.withButton:  # 'I' = Icon
                w = 3
                txtCancel = "✕"
                txtCopy = "🗍"
                txtClone = "🗗"
                txtEdit = "🖊"
                txtSave = "💾"
                txtRemove = "🗑"
                rFont = ('Calibri 12')
            else:
                w = 10
                txtCancel = "Reset"
                txtCopy = "Copy"
                txtClone = "Clone"
                txtEdit = "Edit"
                txtSave = "Save"
                txtRemove = "Remove"
                rFont = ('Segoe 9')
 
            if editMode:              
                butSave = tk.Button(self.butFrame, text= txtSave, font= rFont, command=self.savedata, width=w)
                #Hovertip(butSave,"Save")
                cdc.tooltip(butSave,"Save", self.win)
                butCancel = tk.Button(self.butFrame, text= txtCancel, font= rFont , command=self.canceldata, width=w)
                cdc.tooltip(butCancel,"Reset", self.win)
                if self.typeTrx != 2:  # If not deleted
                    butCopy = tk.Button(self.butFrame, text= txtCopy, font= rFont, command=self.copyData, width=w)   
                    cdc.tooltip(butCopy,"Copy", self.win)
                    butClone = tk.Button(self.butFrame, text= txtClone, font= rFont, command=self.cloneData, width=w) 
                    cdc.tooltip(butClone,"Clone", self.win)
                    butDel = tk.Button(self.butFrame, text= txtRemove, font= rFont, command=self.delData, width=w)
                    cdc.tooltip(butDel,"Remove", self.win)
                if 'E' in self.withButton or 'W' in self.withButton:
                    if self.typeTrx != 2:  # If not deleted
                        butSave.pack()
                    butCancel.pack()
                    if self.typeTrx != 2:  # If not deleted
                        butCopy.pack()
                        butClone.pack()
                        butDel.pack()
                else:
                    if self.typeTrx != 2:  # If not deleted
                        butSave.grid(row= 0, column=0, sticky="EW") 
                    butCancel.grid(row= 0, column=1, sticky="EW")             
                    if self.typeTrx != 2:  # If not deleted
                        butCopy.grid(row= 0, column=2, sticky="EW")
                        butClone.grid(row= 0, column=3, sticky="EW")
                        butDel.grid(row= 0, column=4, sticky="EW")
            else:
                butEdit = tk.Button(self.butFrame, text= txtEdit, font= rFont, command=self.editData, width=w) 
                cdc.tooltip(butEdit,"Edit", self.win)
                butCopy = tk.Button(self.butFrame, text= txtCopy, font= rFont, command=self.copyData, width=w)   
                cdc.tooltip(butCopy,"Copy", self.win)
                butClone = tk.Button(self.butFrame, text= txtClone, font= rFont, command=self.cloneData, width=w) 
                cdc.tooltip(butClone,"Clone", self.win)
                butDel = tk.Button(self.butFrame, text= txtRemove, font= rFont, command=self.delData, width=w)
                cdc.tooltip(butDel,"Remove", self.win)
                if 'E' in self.withButton or 'W' in self.withButton:
                    butEdit.pack()
                    butCopy.pack()
                    butClone.pack()
                    butDel.pack()
                else:
                    butEdit.grid(row= 0, column=0, sticky="EW")
                    butCopy.grid(row= 0, column=1, sticky="EW")
                    butClone.grid(row= 0, column=2, sticky="EW")
                    butDel.grid(row= 0, column=3, sticky="EW")
                
 
    def createFrmEdit(self, dataObj = None, editMode = False):
        self.dictObj = dataObj

        self.mainFrame.columnconfigure(0, weight = 1)
        self.mainFrame.rowconfigure(0, weight = 0)
        self.mainFrame.rowconfigure(1, weight = 0)
        self.mainFrame.rowconfigure(2, weight = 1)
        self.mainFrame.rowconfigure(3, weight = 0)
        
        if self.dictObj is None:
            self.dictObj = self.initData
              
        if self.objMainMess is None:
            self.objMainMess = cdc.messageObj(self.mainFrame, height=25)

        #topItem = tk.Frame(self.mainFrame)          #, bg="red"
        #topItem.pack(expand=1, fill=X, padx = 1, pady = 1)
        mainItem = tk.Frame(self.mainFrame)
        mainItem.pack(expand=1, fill=BOTH)
        mainItem.grid_rowconfigure(0, weight = 0)
        mainItem.grid_rowconfigure(1, weight = 1)
        mainItem.grid_columnconfigure(0, weight=0)
        mainItem.grid_columnconfigure(1, weight=1)
        mainItem.grid_columnconfigure(2, weight=0)
      
        self.mainItem = mainItem
        
        topItem = tk.Frame(mainItem, bg="red")          #, bg="red"
        topItem.grid(row= 0, column=0, columnspan=3, sticky="NS") 
        leftFrame = tk.Frame(mainItem) 
        leftFrame.grid(row= 1, column=0, sticky="nsew") 

        rightFrame = tk.Frame(mainItem)   #, bg="yellow"
        rightFrame.grid(row= 1, column=2, sticky="nsew")

        if self.withButton:
            if 'N' in self.withButton:
                self.butZone = topItem
            elif 'W' in self.withButton:
                self.butZone = leftFrame
            elif 'E' in self.withButton:
                self.butZone = rightFrame        
            else :  # 'S' default
                self.butZone = self.mainFrame
            
        self.initFrmEdit( dataObj = dataObj, editMode = editMode)
        
      
    def initFrmEdit(self, dataObj = None, editMode = False):
        #pdb.set_trace()
        self.dictArr = []
        self.arrToDel = []
        self.editMode = editMode
        if not dataObj is None:
            self.dictObj = dataObj
        if self.withButton and 'N' in self.withButton:
            self.showButtons(editMode = editMode)

        self.dataFrame = tk.Frame(self.mainItem, bg="yellow")  #, bg="blue"

        self.scrollDataFrame = cdc.VscrollFrame(self.dataFrame, 150)
        self.scrollDataFrame.pack(expand= True, fill=BOTH)
        self.recFrame = self.scrollDataFrame.interior
        
        self.addKeys(self.dictObj, self.dictArr)
        self.dataFrame.grid(row= 1, column=1, sticky="nsew")   
        self.dataFrame.grid_rowconfigure(0, weight = 1)   

        if self.typeTrx == 2:
            self.dictObj = self.initData
        #pdb.set_trace()
        #self.scrollDataFrame.initW(400)
        #self.win.geometry("300x250")
        if self.withButton and not 'N' in self.withButton:
            self.showButtons(editMode = editMode)

        def scroll(self):
            self.scrollDataFrame.scroll()
        
class editOntopObj():
    def __init__(self, parent, obj, title=None, callBack = None, editMode = False):
        self.obj, self.trx = None, None
        self.obj = obj
        self.trx = 1
        self.editMode = editMode        
        self.result = None
        self.callBack = callBack
        self.winEdit = tk.Toplevel(parent)
        self.winEdit.title("Edit JSON Object")
        self.winEdit.geometry("500x250")
        self.winEdit.minsize(width = 400, height = 250)
        
        self.showWin(parent)
        
    def showWin(self, parent):
    
        self.editClass = editJsonObject(self.winEdit, self.obj, withButton = 'EI', saveCallback = self.saveData, editMode = self.editMode)

        # OK and Cancel buttons
        box = tk.Frame(self.winEdit)
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.winEdit.bind("<Return>", self.ok)
        self.winEdit.bind("<Escape>", self.cancel)
        box.pack()

        self.winEdit.grab_set()  # Catch events until the window is closed
        parent.wait_window(self.winEdit)  # Wait until the window is closed

        #self.pop.iconbitmap(APPICON)  
        
    def saveData(self, obj, trx):
        self.obj = obj
        self.trx = trx
        
    def ok(self, event=None):
        res = self.editClass.savedata()
        if res:
            self.result = [self.obj, self.trx]
            if self.callBack is not None:
                self.callBack(self.obj, self.trx)
            self.winEdit.grab_release()
            self.winEdit.destroy()

    def cancel(self, event=None):
        self.result = None
        self.winEdit.grab_release()
        self.winEdit.destroy()  