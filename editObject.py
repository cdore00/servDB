import pdb
import tkinter as tk
from tkinter import * 
from tkinter import messagebox, TclError, ttk
import json
from bson import ObjectId
from bson.json_util import dumps
from idlelib.tooltip import Hovertip
#import tkinter.ttk as ttk
#from tktooltip import ToolTip
import pyperclip as cp
from tkinter import simpledialog
from datetime import datetime
#from dateutil import parser
#from tkinter import (Tk, Frame, Button, Entry, Canvas, Text, LEFT, DISABLED, NORMAL, RIDGE, END)

import cdControl as cdc
    
typList  = ['list',  'bool',   'datetime',   'Int64'  ,  'float', 'int'    , 'dict',   'ObjectId', 'set',     'str',  'Timestamp',  'tuple']
typListS = ['Array', 'Boolean',  'Datetime', 'Double', 'Float', 'Integer', 'Object', 'ObjectId', 'BSONset', 'String', 'Timestamp',  'Tuple']


class editJsonObject():
    def __init__(self, win, recObj, parentFrame = None, withButton = "", saveCallback = None, messObj = None, editMode = False ):
        self.win = win
        self.mainFrame = parentFrame
        self.withButton = withButton  # Options 'S' South = default, 'N' North, 'E' East, 'W' West and optionnal 'I' Icon format
        self.objMainMess = messObj
        self.initData = recObj
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
        self.adjustHeight = 120
        self.winHeight = 0
        self.winWidht = 0
        self.load = False
        
        if self.mainFrame is None:
            self.mainFrame = tk.Frame(self.win, bg='blue')   #, borderwidth=3, relief = RIDGE
            self.mainFrame.pack(expand=1, fill=BOTH, padx = 1, pady = 10, anchor=NW) #expand=1, fill=BOTH
 
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

    def addRecord(self, parentFrm, key, elemObj):
        elemArr = []
        #typ = type(elemObj)
        #pdb.set_trace()
        typ = elemObj.__class__.__name__
        
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
            if self.editMode:
                comboType = ttk.Combobox(
                    elemFrame,
                    width=8,
                    state="readonly",
                    values = typListS
                    )
                comboType.grid(row= 0, column=3)
                comboType.current(typList.index(typ))       
                elemArr.append(comboType)  #typ
                if key == "_id" and not self.indNew:
                    comboType.config( state="disabled")
            else:
                typeVar = StringVar()
                typeVar.set(typ)
                elemArr.append(typeVar)
                
        except Exception as ex:
            pdb.set_trace()
            self.objMainMess.showMess(str(ex))
            
        return elemArr     

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

    def showHide(self, e, frm, arrP):
        #pdb.set_trace()
        expBut = e if isinstance(e,(Label)) else e.widget
        slavelist = frm.slaves()
        cnt = len(slavelist)
        if cnt == 1:
            expBut.config( text="▲")
            for ind, elem in enumerate(arrP):
                elem.pack(expand=1, fill="x", padx = 5)
        else:
            expBut.config( text="▼")
            for ind, elem in enumerate(slavelist):
                if ind > 0:
                    arrP.append(elem)
                    elem.pack_forget()
        #self.win.update_idletasks()

    def delElement(self, e, frm, arrP, ind):
        self.arrToDel.append([arrP, arrP[ind]])
        frm.destroy()

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
                newEl = self.addElement(key, "", dictArr, el.master)
        #pdb.set_trace()
        if fp < ind:
            dictArr.insert(fp+rootInd, newEl)
        else:
            dictArr.append(newEl)
        for ind, elem in enumerate(arrF):
            elem.pack(expand=1, fill="x", padx = 5)
        
    def addElement(self, key, elemObj, dictArr, frm = None):    # Add recurring element
        #pdb.set_trace()
        if frm is None :
            rootInd = 1
            recFrame = self.recFrame 
        else:
            rootInd = 0
            recFrame = frm
        
        rowFrame = tk.Frame(recFrame, height=1)  #, bg="green"
        rowFrame.pack(expand=1, fill="x")  
        rowDataFrame, delBut, ctrlBut, expBut = self.addFrame(rowFrame)
        #print(str(expBut))
        if self.editMode:
            ctrlBut.bind("<Button-1>", lambda event, frm=recFrame, dictArr=dictArr, key=key, rootInd=rootInd: self.addNewRecord(event, frm, dictArr, key, rootInd))
        
        elemFrame = tk.Frame(rowDataFrame, height=1)
        elemFrame.grid(row= 0, column=3, sticky="EW")        
        elemArr = self.addRecord( elemFrame, key, elemObj)
        if key != "_id" and self.editMode:
            delBut.bind("<Button-1>", lambda event, frm=rowFrame, arrP=dictArr, arrInd=len(dictArr): self.delElement(event, frm, arrP, arrInd))
        else:
            delBut.config( text="    ")

        if isinstance(elemObj, (dict)):
            childArr = []
            elemArr.append(childArr)
            self.addKeys(elemObj, childArr , elemFrame)
            arrP=[]
            expBut.bind("<Button-1>", lambda event, frm=elemFrame, arrP=arrP: self.showHide(event, frm, arrP))
            self.showHide(expBut, elemFrame, arrP)           
        if isinstance(elemObj, (list)):
            childArr = []
            elemArr.append(childArr)
            self.addListItems(elemObj, childArr , elemFrame)
            arrP=[]
            expBut.bind("<Button-1>", lambda event, frm=elemFrame, arrP=arrP: self.showHide(event, frm, arrP))
            self.showHide(expBut, elemFrame, arrP)            
        #print("elemArr=" + str(elemArr))
        return elemArr

    def addListItems(self, listObj, dictArr, frm = None):   # Add recurring lists
        for ind, elem in enumerate(listObj):
            dictArr.append(self.addElement(ind, elem, dictArr, frm))       

    def addKeys(self, dictObj, dictArr, frm = None):    # Add recurring dictionnarys
        k = list(dictObj.keys())
        for ind, key in enumerate(k):
            dictArr.append(self.addElement(key, dictObj[key], dictArr, frm))


    def convertdata(self, elem):
        try:
            #pdb.set_trace()
            typ = typList[typListS.index(elem[2].get())]
            
            data = elem[1].get("1.0", END)
            nlines = data.count('\n')
            if nlines == 1:
                data = data.replace("\n", "")
            if typ != 'str':
                if typ == 'ObjectId':
                    data = ObjectId(data)
                if typ == 'int':
                    data = int(data)
                if typ == 'float':
                    data = float(data)
                if typ == 'datetime':
                    data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S.%f')
                if typ ==  'Timestamp':
                    pdb.set_trace()
                if typ == 'dict' or typ == 'list':
                    #pdb.set_trace()
                    cle = "" if typ == 'dict' else "0"
                    if len(elem) == 3:  # Change type
                        #pdb.set_trace()
                        el0=cdc.clone_widget(elem[0])
                        el0.insert(tk.END,cle)
                        el1=cdc.clone_widget(elem[1])
                        data = elem[1].get("1.0", END)
                        data = data.replace("\n", "")
                        el1.insert(tk.END,data)
                        el2=cdc.clone_widget(elem[2])                    
                        el2.current(typList.index(elem[2].get().__class__.__name__))
                        elem.append([[el0, el1, el2]])
                        #elem.append([])
                    if typ == 'dict':
                        data = self.convertToDict(elem[3])
                    if typ == 'list':
                        data = self.convertToList(elem[3], True)

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

            return None
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
        #self.error = None
        for ind, elem in enumerate(listObj):
            #print("Elem[0]=" + str(len(elem)))
            #pdb.set_trace()
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
        #print(newObj)
        return newObj


    def savedata(self, updType = 1):       
        #pdb.set_trace()
        self.error = None
        self.dictObj = self.initData
        #pdb.set_trace()
        if self.typeTrx > 1:
            updType = self.typeTrx
        else:
            self.typeTrx = updType
        
        if updType == 2:     #Remove data
            print("delData")  
           
        else:
            for ind, elem in enumerate(self.arrToDel):  # Remove deleted elements
                elem[0].remove(elem[1])   
            self.dictObj = self.convertToDict(self.dictArr)
            
            #print(self.dictObj)
            if self.dictObj:
                self.clearMainFrame()
                self.initFrmEdit(self.dictObj, editMode = False)
                if self.error:
                    self.clearMainFrame()
                    self.initFrmEdit(self.dictObj, editMode = True)
        
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
        pdb.set_trace()
        x=1

    def cloneData(self):         
        data = self.dictObj
        #pdb.set_trace()
        data["_id"] = ObjectId() 
        self.clearMainFrame()
        self.initFrmEdit(data, editMode = True)
        self.typeTrx = 3
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
            else:
                w = 10
                txtCancel = "Cancel"
                txtCopy = "Copy"
                txtClone = "Clone"
                txtEdit = "Edit"
                txtSave = "Save"
                txtRemove = "Remove"
 
            if editMode:              
                butSave = tk.Button(self.butFrame, text= txtSave, font= ('Calibri 12'), command=self.savedata, width=w)
                #Hovertip(butSave,"Save")
                cdc.tooltip(butSave,"Save all data partout partout partout", self.win)
                #ToolTip(butSave, msg="Hover info")
                butCancel = tk.Button(self.butFrame, text= txtCancel, font= ('Calibri 12'), command=self.canceldata, width=w)
                #Hovertip(butCancel,"Cancel")
                cdc.tooltip(butCancel,"Cancel", self.win)
                if 'E' in self.withButton or 'W' in self.withButton:
                    if self.typeTrx != 2:  # If not deleted
                        butSave.pack()
                    butCancel.pack()
                else:
                    if self.typeTrx != 2:  # If not deleted
                        butSave.grid(row= 0, column=0, sticky="EW") 
                    butCancel.grid(row= 0, column=1, sticky="EW")             
            else:
                butEdit = tk.Button(self.butFrame, text= txtEdit, font= ('Calibri 12'), command=self.editData, width=w) 
                Hovertip(butEdit,"Edit")
                butCopy = tk.Button(self.butFrame, text= txtCopy, font= ('Calibri 12'), command=self.copyData, width=w)     
                Hovertip(butCopy,"Copy")
                butClone = tk.Button(self.butFrame, text= txtClone, font= ('Calibri 12'), command=self.cloneData, width=w)     
                Hovertip(butClone,"Clone")
                butDel = tk.Button(self.butFrame, text= txtRemove, font= ('Calibri 9'), padx=3, pady=3, command=self.delData, width=w)
                Hovertip(butDel,"Remove")
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

        topItem = tk.Frame(self.mainFrame, bg="red")
        topItem.pack(expand=1, fill=X, padx = 1, pady = 1)
        mainItem = tk.Frame(self.mainFrame)
        mainItem.pack(expand=1, fill=BOTH)
        mainItem.rowconfigure(0, weight = 1)
        #mainItem.grid_rowconfigure(1, weight = 0)
        mainItem.grid_columnconfigure(0, weight=0)
        mainItem.grid_columnconfigure(1, weight=1)
        mainItem.grid_columnconfigure(2, weight=0)

      
        self.mainItem = mainItem
        
        leftFrame = tk.Frame(mainItem) 
        leftFrame.grid(row= 0, column=0, sticky="nsew") 

        rightFrame = tk.Frame(mainItem)   #, bg="yellow"
        rightFrame.grid(row= 0, column=2, sticky="nsew")

        if self.withButton:
            if 'N' in self.withButton:
                self.butZone = topItem
                self.adjustHeight += 50
            elif 'W' in self.withButton:
                self.butZone = leftFrame
            elif 'E' in self.withButton:
                self.butZone = rightFrame        
            else :  # 'S' default
                self.butZone = self.mainFrame
                self.adjustHeight += 50
            
        self.initFrmEdit( dataObj = dataObj, editMode = editMode)
        
      
    def initFrmEdit(self, dataObj = None, editMode = False):
        self.load = False
        self.dictArr = []
        self.arrToDel = []
        self.editMode = editMode

        if self.withButton and 'N' in self.withButton:
            self.showButtons(editMode = editMode)

        #recFrame
        self.dataFrame = tk.Frame(self.mainItem)  #, bg="blue"


        self.scrollDataFrame = cdc.VscrollFrame(self.dataFrame, 300)
        self.scrollDataFrame.pack(expand= True, fill=BOTH)
        self.recFrame = self.scrollDataFrame.interior

        #self.recFrame = self.dataFrame
        
        self.addKeys(self.dictObj, self.dictArr)
        self.dataFrame.grid(row= 0, column=1, sticky="nsew")   
        self.dataFrame.grid_rowconfigure(0, weight = 1)        

        if self.withButton and not 'N' in self.withButton:
            self.showButtons(editMode = editMode)
       
        self.scrollDataFrame.canvas.config(width = self.scrollDataFrame.interior.winfo_reqwidth()-1)
        #pdb.set_trace()
        #self.scrollDataFrame.initialize(300)
        print("self.winHeight= " + str(self.winHeight))
        wh = 400 if self.winHeight <=0 else self.winHeight
        #self.scrollDataFrame.initialize(wh - self.adjustHeight)


class editModalObj(simpledialog.Dialog):
    def __init__(self, parent, obj, title=None, editMode = False):
        self.obj, self.trx = None, None
        self.obj = obj
        self.editMode = editMode        
        
        self.initHeight = 250
        super().__init__(parent, title=title)
        
    def body(self, master):
        #pdb.set_trace()
        self.editClass = editJsonObject(master, self.obj, withButton = 'EI', editMode = self.editMode)
        self.win_size = 0   
        self.minsize(width = 400, height = self.initHeight)
        #return [self.obj, self.trx]

    def buttonbox(self):
        box = tk.Frame(self)

        # Boutons OK et Annuler
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Annuler", width=10, command=self.cancel)
        w.pack(side=tk.RIGHT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(side=tk.BOTTOM, fill=tk.X)
        
        
    def validate(self):     
        self.obj, self.trx = self.editClass.getData()
        if self.trx:
            return True
        else:
            return False

    def apply(self):
        self.result = [self.obj, self.trx]        
        
        
        
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
        self.winEdit.wm_attributes("-topmost", True)        
        #self.initHeight = 250
        
        self.showWin(parent)
        
    def showWin(self, parent):
    
        self.editClass = editJsonObject(self.winEdit, self.obj, withButton = 'EI', saveCallback = self.saveData, editMode = self.editMode)

        # OK and Cancel buttons
        box = tk.Frame(self.winEdit)
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Annuler", width=10, command=self.cancel)
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
            self.winEdit.destroy()

    def cancel(self, event=None):
        self.result = None
        self.winEdit.destroy()  