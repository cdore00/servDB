#https://www.youtube.com/watch?v=I2wwyOTtIe4
# coding=utf-8
import pdb
#; pdb.set_trace()
import sys, os, io, re, cgi, csv, urllib.parse
import urllib.request
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
from tkinter.messagebox import askyesno

from bson import ObjectId
import time 
import datetime
#import winsound
#winsound.Beep(500, 60)
import dropbox, base64

def milliToDate(milli, showTime = False):
    dt=datetime.datetime.fromtimestamp(milli / 1000.0)
    sdt = str(dt.year) + "-" + str(dt.month).rjust(2, '0') + "-" + str(dt.day).rjust(2, '0')
    if showTime:
        sdt = sdt + " " + str(dt.hour).rjust(2, '0') + ":" + str(dt.minute).rjust(2, '0')
    return sdt

C_WA = "àâäôóéèëêïîçùûüÿÀÂÄÔÉÈËÊÏÎŸÇÙÛÜ()"
C_NA = "aaaooeeeeiicuuuyAAAOEEEEIIYCUUU  "    
def scanName(name):
    for car in name:
        if (C_WA.find(car)) > -1:
            pos = C_WA.find(car)
            name = name.replace(car, C_NA[pos:pos+1], 1)
    return name.upper()
    
class VscrollFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        
        #Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                width = 200, height = 300,
                                yscrollcommand=vscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command = self.canvas.yview)
        
        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = tk.Frame(self.canvas)       #, bg="grey" 
        self.interior.bind('<Configure>', self.configure_interior)
        self.canvas.bind('<Configure>', self.configure_canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)

    def configure_interior(self, event):
        #Update the scrollbar to match the size of the inner frame.
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=(0,0, size[0], size[1]))
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            #Update the inner canvas's width to fit the inner frame
            self.canvas.config(width = self.interior.winfo_reqwidth())
            
    def configure_canvas(self, event):   
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            #Update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
            
        
class modalDialogWin():
    def __init__(self, win, title = "Dialogue modal", optionalObject = None, geometry = None, *args, **kwargs):
        self.win = win              #Parent window
        self.title = title          #Modal window title
        self.obj = optionalObject   #Optionnal object Ex.: data
        self.dframe = None
        self.pop = None
        self.modal = None
        
    def createDialog(self):
        self.pop = Toplevel(self.win)
        self.pop.title(self.title)
        #self.pop.geometry("300x150")
        self.pop.attributes('-toolwindow', True)  #Removing minimize/maximize buttons    
        self.pop.bind('<Destroy>', self.closemodal)
        self.dframe = Frame(self.pop)  # not ttk
        self.dframe.grid_rowconfigure(0, weight=1)
        self.dframe.grid_columnconfigure(0, weight=1)        
        
        t=self.win.geometry()
        di=t.split("x")
        w = eval(di[0])        
        self.modal = tk.Frame(self.win, background="")
        self.modal["width"] = eval(di[0])
        self.modal["height"] = eval(di[1].split("+")[0]) #eval(di[1]) - 10
        self.modal.place(x=0, y=0) 
        self.modal.bind("<Button-1>", self.clickModal)


    def createWidget(self):
        #To rewrite for user 
        button1 = Button(self.dframe, text="Ok", command=self.close)
        button1.grid(row=2, column=1)
 
        
    def showDialog(self):
        self.createDialog()
        x = self.win.winfo_x()
        y = self.win.winfo_y()
        pos = "+%d+%d" % (x + 70, y + 70)
        self.pop.geometry(pos)
        self.createWidget()
        self.dframe.pack(expand= True, fill=BOTH, padx=5, pady=3, anchor=CENTER)
        
    def close(self, event = None):
        self.closepop()
        self.modal.destroy()
    def closepop(self):
        self.pop.destroy()
    def closemodal(self, e):
        self.modal.destroy()
        
    def clickModal(self, e):
        self.win.bell()
        self.closepop()
        self.showDialog()


class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, bg, command=None, cursor=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg=bg, cursor="hand2")
        self.command = command
            
        if cornerradius > 0.5*width:
            print("Error: cornerradius is greater than width.")
            return None

        if cornerradius > 0.5*height:
            print("Error: cornerradius is greater than height.")
            return None

        rad = 2*cornerradius
        def shape():
            self.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,padding+cornerradius,padding,width-padding-cornerradius,padding,width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,width-padding-cornerradius,height-padding,padding+cornerradius,height-padding), fill=color, outline=color)
            self.create_arc((padding,padding+rad,padding+rad,padding), start=90, extent=90, fill=color, outline=color)
            self.create_arc((width-padding-rad,padding,width-padding,padding+rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width-padding,height-rad-padding,width-padding-rad,height-padding), start=270, extent=90, fill=color, outline=color)
            self.create_arc((padding,height-padding-rad,padding+rad,height-padding), start=180, extent=90, fill=color, outline=color)


        id = shape()
        (x0,y0,x1,y1)  = self.bbox("all")
        width = (x1-x0)
        height = (y1-y0)
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)


    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()
            
class messageObj():
    def __init__(self, parent, objToBind = None, *args, **kwargs):
        self.parent = parent
        self.objToBind = objToBind  #Object to click to clear message
        self.messLabel = None
        self.messframe = tk.Frame(self.parent, height=0)
        self.messframe.pack(fill=X)

    def showMess(self, message, color = '#f00'):
        #pdb.set_trace()
        self.clearMess()
        self.messLabel = tk.Label(self.messframe, font=('Calibri 12'), fg= color)
        self.messLabel.config(text= message)
        #print(str(self.messframe.winfo_width()))
        w = self.messframe.winfo_width() - 50
        self.messLabel.config(wraplength=w)
        self.messLabel.pack(expand= True, fill=X)
        if not self.objToBind is None:
            self.objToBind.bind("<Button-1>", self.clearMess)
        
    def clearMess(self, event = None):
        if not self.objToBind is None:
            self.objToBind.update_idletasks()
            self.objToBind.unbind("<Button-1>")
        if not self.messLabel is None:
            self.messLabel.destroy()
            self.messframe.config(height=1)
            self.messframe.update_idletasks()
        
        
class imageObj():
    def __init__(self, parentObj, parentContainer, imgURL = "", dim = (2,1),*args, **kwargs):
        self.objToBind = parentObj
        self.imgCont = parentContainer
        self.imgURL = imgURL
        self.localImage = ""
        self.labImg = Label(self.imgCont)
        self.width = dim[0]
        self.height = dim[1]
                
        if self.imgURL == "":
            self.showNoImage()
        else:
            self.objToBind.bind("<Enter>",self.showImg)
 
    def showNoImage(self, modify = False):
        self.labImg.config(text="Image\nϴ")
        self.labImg.config(font='Calibri 20')
        self.labImg.config(width= self.width)
        self.labImg.config(height= self.height)
        self.labImg.grid(row=0, column=0) 
        if modify:
            self.labImg = Label(self.imgCont, cursor="hand2")
            self.labImg.bind("<Button-1>", self.changeImage)

    def showImg(self, event = None, localPath = ""):
        self.objToBind.unbind("<Enter>")
        self.objToBind.config(cursor="watch")
        ht = 140
        if localPath :
            self.labImg.destroy()
            self.labImg = Label(self.imgCont)
            self.recImage=Image.open(localPath)
            self.labImg.bind("<Button-1>", self.modifImage)            
        else:
            cover = self.imgURL
            raw_data = urllib.request.urlopen(cover).read()
            self.recImage = Image.open(io.BytesIO(raw_data))
            self.labImg.bind("<Button-1>", self.showImage)
        image = ImageTk.PhotoImage(self.recImage)
        lg = int(image.width() * (ht/image.height()))
        img=self.recImage.resize(( lg, ht))
        image = ImageTk.PhotoImage(img)
        self.labImg.config(image=image)
        self.labImg.config(cursor="hand2")
        self.labImg.photo = image
        self.labImg.grid(row=0, column=0)  
        
        self.objToBind.config(cursor="")

    def showImage(self, event):
        winImg = showRecImg(self.objToBind, "Image", self.recImage)
        winImg.showDialog()
        
    def editImgage(self):
        self.labImg.config(cursor="hand2")
        self.editMode = True
        if self.imgURL :
            self.labImg.bind("<Button-1>", self.modifImage)
        else:
            self.labImg.bind("<Button-1>", self.changeImage)           

    def changeImage(self, event = None):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.localImage = file_path
            self.showImg(False, file_path)    
    
    def modifImage(self, event):
        winImg = modifRecImg(self.objToBind, "Modifier image", self)
        winImg.showDialog()    

    def deleteImage(self):
        self.labImg.config(image="")
        self.labImg.photo = ""
        self.imgURL = ""
        self.localImage = ""        
        self.showNoImage(True)
        self.labImg.bind("<Button-1>", self.changeImage)

    def saveImage(self):
        dl_url = ""
        if self.localImage:
            def readFile(fName):
                f = open(fName, "r")
                return f.read()
    
            upload_filename = ""
            pos = self.localImage.rfind('/')
            upload_filename=self.localImage[pos+1:]
            upload_file = os.path.normpath(os.path.join("", upload_filename))
 
            dbx = dropbox.Dropbox(readFile("" + "info"))
     
            file_to = "/" + upload_filename
     
            while True:
                try:
                    with open(upload_file, 'rb') as f:
                        dbx.files_upload(f.read(), file_to)
                    break
                except Exception as ex:
                    if 'WriteConflictError' in str(ex):
                        x = str(ObjectId())
                        p = file_to.rfind(".")
                        file_to = file_to[0:p] + x[-2:] + file_to[p:]
                    else:
                        break
                        return except_handler("addFile Dropbox", ex)
            
            link = dbx.sharing_create_shared_link(file_to)
            dl_url = link.url.replace("dl=0", "raw=1")
            
        return dl_url    


        
class showRecImg(modalDialogWin):
    def createWidget(self):
        #self.pop.resizable(0, 0)
        lab0 = Label(self.dframe, text="Actuel = ", bg="white", pady=5)
        lab0.grid(row=0, column=0, columnspan=2, sticky=EW)
        
        ht = 500
        image = ImageTk.PhotoImage(self.obj)
        actH = image.height()
        lg = int(image.width() * (ht/image.height()))
        img=self.obj.resize(( lg, ht))
        image = ImageTk.PhotoImage(img)
        labImg = Label(self.dframe, image=image)
        labImg.photo = image
        labImg.grid(row=0, column=0)  
        labImg.bind("<Button-1>", self.close)
        self.pop.resizable(0, 0)   

class modifRecImg(modalDialogWin):
    def createWidget(self):

        datURL = self.obj.localImage if self.obj.localImage else self.obj.imgURL
        print(datURL)
        if datURL == '' or datURL == 'undefined' :
            txt = "Ajouter..."
        else:
            txt = "Remplacer..."
        button1 = Button(self.dframe, text= txt, command=self.changeImage, width=30)
        button1.grid(row=1, column=0, columnspan=2)
        button2 = Button(self.dframe, text="Supprimer...", command=self.deleteImage, width=30)
        button2.grid(row=2, column=0, columnspan=2)
        
        lab1 = Label(self.dframe, text=" ")
        lab1.grid(row=3, column=0, columnspan=2, pady=5)

        buttonC = Button(self.dframe, text="Fermer", command=self.close, width=10) 
        buttonC.grid(row=4, column=0)
        buttonC.grid_rowconfigure(4, weight=1)
        buttonC.grid_columnconfigure(4, weight=1)        

    def changeImage(self):
        self.close()
        self.obj.changeImage()
 
    def deleteImage(self):
        answer = askyesno(title='Suppression de l\'image',
            message='Supprimer l\'image de la recette ? ')
        if answer:
            self.close()
            self.obj.deleteImage()
            
            
class menuEdit():
    def __init__(self, parentWin, inputToBind, *args, **kwargs):
        self.win = parentWin
        self.inputToBind = inputToBind  #Object to right click to pop menuEdit
        self.menu = Menu(self.win,tearoff=0) # Create a menu
        self.menu.add_command(label='Couper',command=self.cut) # Create labels and commands
        self.menu.add_command(label='Copier',command=self.copy) 
        self.menu.add_command(label='Coller',command=self.paste)
        self.menu.add_command(label='Sélectionner tout',command=self.selectAll)
        
        self.inputToBind.bind('<Button-3>',self.popup) # Bind to right click

    def popup(self, event):
        try:
            self.menu.tk_popup(event.x_root,event.y_root) # Pop the menu up in the given coordinates
        finally:
            self.menu.grab_release() # Release it once an option is selected

    def cut(self):
        self.inputToBind.event_generate("<<Cut>>")
        
    def paste(self):
        self.inputToBind.event_generate("<<Paste>>")

    def copy(self):
        self.inputToBind.event_generate("<<Copy>>")

    def selectAll(self):
        if isinstance(self.inputToBind, tk.Entry):
            self.inputToBind.select_range(0, 'end')
        else:
            #lines = len(self.inputToBind.get("1.0", "end").split('\n'))
            self.inputToBind.tag_add('sel', '{}.0'.format(1), '{}.end'.format(1))
            #print(str(lines))


class editEntry(tk.Entry):
    def __init__(self, parent=None, width=None, textvariable=None, state=None, validate="key", maxlen=None):
        tk.Entry.__init__(self, parent, textvariable=textvariable, width=width, state=state, validate=validate)
        self.win = parent.win
        menuEdit(parent.win, self)
        if maxlen:
            self.config(validatecommand=(parent.register(self.validate), '%P', maxlen))
        
    def validate(self, P, maxlen):
        #pdb.set_trace()
        if len(P) <= int(maxlen):
            return True
        else:
            self.win.bell()
            return False
            
            
class resizeFrame(tk.Frame):
    def __init__(self, parent=None, borderwidth = None, relief=None, bg = None, pack = True):
        tk.Frame.__init__(self, parent, borderwidth = borderwidth, relief=relief, bg=bg)
        self.win = parent
        if pack:
            self.pack(expand=YES, fill=BOTH)            