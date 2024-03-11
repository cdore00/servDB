import pdb
import tkinter as tk
from tkinter import * 
from tkinter import messagebox, TclError, ttk
from bson import ObjectId
#from tkinter import (Tk, Frame, Button, Entry, Canvas, Text, LEFT, DISABLED, NORMAL, RIDGE, END)

from tkinter import simpledialog
import cdControl as cdc
import editObject as eob
  
data = {
    "_id": 1,
    "desc": "Bouffe",
    "cat": "Repas"
}

data1 = {
    "_id": "5b26d094dc0ec2000b326366",
    "Time": 1529256020626,
    "Date": "2018-06-17 17:20:20",
    "IP": "172.17.0.4",
    "Name": "Charles Dor\u00e9",
    "Address": "228 Cr\u00e9mazie Ouest #B",
    "email": "cdore00@yahoo.ca",
    "ID": "",
    "Choix": [
        "Salade de l\u00e9gumineuses au saumon fum\u00e9 et \u00e0 l'aneth frais",
        "Couscous aux saucisses merguez et oignons caram\u00e9lis\u00e9s",
        "Rabais de 2.50$ pour les commandes de 40.00$ et plus"
    ]
}

data = {
    "_id": "5ec1626963f1571d78b4f8dd",
    "cat": {
        "no": 1,
        "desc": "Repas"
    },
    "liste": ["element1","element2","element3"],
    "keyBool": True,
    "keyTup": (1,2,3),
    "keySet": {1,2,3},
    "nom": "Chop suey au poulet",
    "dec": 1234.56789
}

data3 = {
    '_id': ObjectId('5b26deb8dc0ec2001513fc16'),
    'title': 'Mets préparés - Semaine du 30 avril',
    'active': 1,
    'date': '19 avril 2018',
    'dateC': 1529259640081,
    'dateM': 1595875210280,
    'contentL': '<p><br></p>',
    'contentR': '<p>😀😀Vous <span style="background-color: rgb(255, 255, 0)'
  }             

data4 = {
  "_id": {
    "$oid": "5b26d094dc0ec2000b326366"
  },
  "Time": {
    "$numberLong": "1529256020626"
  },
  "Date": "2018-06-17 17:20:20",
  "IP": "172.17.0.4",
  "Name": "Charles Doré",
  "Address": "228 Crémazie Ouest #B",
  "email": "cdore00@yahoo.ca",
  "ID": "",
  "Choix": [
    "Salade de légumineuses au saumon fumé et à l'aneth frais",
    "Couscous aux saucisses merguez et oignons caramélisés",
    "Rabais de 2.50$ pour les commandes de 40.00$ et plus"
  ],
  "info": [
    [
      "Livraison du dimanche 15 avril:$1*2$1*3"
    ],
    [
      "Frais et rabais$3*1"
    ]
  ]
}

data5 = {"_id": "5ec1626963f1571d78b4f8dd", "cat": {"_id": 1, "desc": "Repas"}, "nom": "Chop suey au poulet", "ingr": ["180 ml (3/4 tasse) de bouillon de poulet ", "60 ml (1/4 tasse) de sauce soya ", "15 ml (1 c. \u00e0 soupe) de f\u00e9cule de ma\u00efs", "225 g (1/2 lb) de champignons blancs, tranch\u00e9s", "1 poivron rouge, \u00e9p\u00e9pin\u00e9 et coup\u00e9 en lani\u00e8res", "2 branches de c\u00e9leri, tranch\u00e9es en diagonale", "6 oignons verts, \u00e9minc\u00e9s (le blanc et le vert s\u00e9par\u00e9s)", "30 ml (2 c. \u00e0 soupe) d\u2019huile v\u00e9g\u00e9tale", "300 g (4 tasses) de f\u00e8ves germ\u00e9es", "1 gousse d'ail, hach\u00e9e finement", "340 g (2 tasses) de poulet cuit, coup\u00e9 en d\u00e9s", "65 g (1/2 tasse) de noix de cajou, grill\u00e9es et concass\u00e9es (facultatif)"], "prep": ["Dans un bol, m\u00e9langer le bouillon de poulet, la sauce soya et la f\u00e9cule.", "Dans le wok ou une grande po\u00eale, \u00e0 feu vif, dorer les champignons, le poivron, le c\u00e9leri et le blanc des oignons dans l'huile. Ajouter les f\u00e8ves germ\u00e9es, l'ail et poursuivre la cuisson environ 2 minutes. Ajouter le poulet et le m\u00e9lange de bouillon de poulet. Porter \u00e0 \u00e9bullition en remuant et laisser mijoter environ 2 minutes ou jusqu'\u00e0 ce que les f\u00e8ves soient tendres. Rectifier l'assaisonnement. Parsemer du vert des oignons et de noix de cajou. "], "nomU": "CHOP SUEY AU POULET", "nomP": "XPSPLT", "temp": "20 min.", "port": "4", "cuis": "10 min.", "dateC": 1591390898613, "dateM": 1592018628893, "userID": "5ec5a673bc1a97243823bc25", "imgURL": "https://www.dropbox.com/s/s5jiohluoagj7ti/chop.jpg?raw=1", "state": 1, "ingrP": [" TS PLN PLT ", " TS SS S ", "SP FKL M ", " XMPNNS PLNKS TRNXS ", "PFRN RJ APPN KP LNRS ", "PRNXS SLR TRNXS TKNL ", "ANNS FRTS AMNSS PLNK FRT SPRS ", "SP TL FKTL ", "TSS FFS KRMS ", "KS TL HX FNMNT ", "TSS PLT KT KP TS ", " TS NKS KJ KRLS KNKSS FKLTTF "], "ingrU": ["180 ML  3/4 TASSE  DE BOUILLON DE POULET ", "60 ML  1/4 TASSE  DE SAUCE SOYA ", "15 ML  1 C. A SOUPE  DE FECULE DE MAIS", "225 G  1/2 LB  DE CHAMPIGNONS BLANCS, TRANCHES", "1 POIVRON ROUGE, EPEPINE ET COUPE EN LANIERES", "2 BRANCHES DE CELERI, TRANCHEES EN DIAGONALE", "6 OIGNONS VERTS, EMINCES  LE BLANC ET LE VERT SEPARES ", "30 ML  2 C. A SOUPE  D\u2019HUILE VEGETALE", "300 G  4 TASSES  DE FEVES GERMEES", "1 GOUSSE D'AIL, HACHEE FINEMENT", "340 G  2 TASSES  DE POULET CUIT, COUPE EN DES", "65 G  1/2 TASSE  DE NOIX DE CAJOU, GRILLEES ET CONCASSEES  FACULTATIF "]}       
 
data6 = {'_id': ObjectId('5b26d094dc0ec2000b326366'), 'Time': 1529256020626, 'Date': '2018-06-17 17:20:20', 'IP': '172.17.0.4', 'Name': 'Charles Doré', 'Address': '228 Crémazie Ouest #B', 'email': 'cdore00@yahoo.ca', 'ID': '', 'Choix': ["Salade de légumineuses au saumon fumé et à l'aneth frais", 'Couscous aux saucisses merguez et oignons caramélisés', 'Rabais de 2.50$ pour les commandes de 40.00$ et plus'], 'info': [['Livraison du dimanche 15 avril:$1*2$1*3'], ['Frais et rabais$3*1']]} 

def saveData(newObj, updType):
    print("zone1.saveData=" + str(newObj) + "  TRX= " + str(updType))

        
def showData( win, obj):
    #pdb.set_trace()
    editMode = False
    if not obj:
        editMode = True
    custom_dialog = eob.editModalObj(win, obj, title="Edit JSON Object", editMode = editMode)
    #custom_dialog.geometry("800x500")
    res = custom_dialog.result #Retourner les valeurs par le bouton Ok, sinon None
    return res
      

root = tk.Tk()
root.title("Édit json")
root.geometry("250x200")
#root.withdraw()

res = None

#objMess = cdc.messageObj(root, height=25)  # simpledialog.Dialog Class
#editClass = eob.editJsonObject(root, data, withButton = 'EI', saveCallback = saveData)   #  , messObj = objMess
editClass = eob.editOntopObj(root, data, editMode = True)   #, callBack = saveData, messObj = objMess
print(str(editClass.result))
#res = showData(root, data)    #  simpledialog.Dialog Class
if res:
    print(str(res[0]) + "  TRX= " + str(res[1]))
root.destroy()

#editClass = eob.editJsonObject(root, data, withButton = 'EI', saveCallback = saveData)   #, messObj = objMess

"""
butFrame = tk.Frame(root, height=1)  #, bg="red"
butFrame.pack(expand=1, padx = 5, anchor=N)  
butSave = tk.Button(butFrame, text='Save', command=editClass.savedata, width=10)
butSave.grid(row= 0, column=0, sticky="EW", padx=5, pady=10)    
butSave = tk.Button(butFrame, text='Cancel', command=editClass.canceldata, width=10)
butSave.grid(row= 0, column=1, sticky="EW", padx=5, pady=10)
"""

root.mainloop()