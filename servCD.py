#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import gethostname, gethostbyname 
from urllib.parse import urlparse, parse_qs
from sys import argv
from datetime import datetime

from http import cookies

import os, time, re, urllib.parse, urllib.request



#import requests as req
#from io import BytesIO

#Log file
LOG_DIR =os.getcwd() + '/log'
if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR)
LOG_FILE = 'log/' + str(int(time.time())) + '.log'

global logPass 

# MongoDB
import pymongo
from pymongo import MongoClient

if os.environ.get('MONGODB_USER'):
	port = int(os.environ['MONGODB_PORT'])
	user = urllib.parse.quote_plus(os.environ['MONGODB_USER'])
	passw = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])
	domain = urllib.parse.quote_plus(os.environ['MONGODB_SERVICE'])
	dbase = urllib.parse.quote_plus(os.environ['MONGODB_DATABASE'])
	uri = "mongodb://%s:%s@%s/%s?authMechanism=SCRAM-SHA-1" % (user, passw, domain, dbase)
else:
	port = 27017
	uri = "mongodb://localhost"

client = MongoClient(uri, port)
data = client.golf
from bson.json_util import dumps
import json


# HTTPRequestHandler class
class golfHTTPServer(BaseHTTPRequestHandler):
	
	@staticmethod
	def call_Func(strURL):
		print("strURL=" + strURL)
		pos = strURL.find("?")
		if pos == -1:
		  func = strURL[1:]
		else:
		  func = strURL[1:pos]
		return func
	
	@staticmethod
	def return_Res(self,mess):
		# Send response status code
		self.send_response(200)
		# Send headers
		self.send_header('Content-type','text/html')
		self.send_header('Access-Control-Allow-Origin', '*')
		#  Set cookie
		self.send_header('Set-Cookie','superBig=zag;max-age=31536000')
		self.end_headers()
		# Write content as utf-8 data
		self.wfile.write(bytes(mess, "utf8"))
		return

	# GET
	def do_GET(self):
		
		if 'HTTP_COOKIE' in os.environ:
			cookie_string = os.environ.get('HTTP_COOKIE')
			print(str(cookie_string))
		
		cookieProcessor = urllib.request.HTTPCookieProcessor()
		opener = urllib.request.build_opener(cookieProcessor)
		#r = opener.get('http://example.com', headers = headers, cookies = cookies)

		c = cookies.SimpleCookie()
		print(str(c.load("")))

		# Send message back to client
		query_components = parse_qs(urlparse(self.path).query)
		url = self.path
		print("GET " + url)
		message = case_Func(self.call_Func(url), query_components)
		self.return_Res(self,message)
		return
		
	# POST	
	def do_POST(self):

		# Send message back to client
		query_components = parse_qs(urlparse(self.path).query)
		url = self.path
		print("POST " + url)
		message = case_Func(self.call_Func(url), query_components)
		self.return_Res(self,message)
		
		return		

#End class

def case_Func(fName, param):
	if fName == "ose":
		return(ose())
	elif fName == "listLog":
		return(listLog())
	elif fName == "listLog2":
		return(listLog2())
	elif fName == "showLog":
		return(showLog(param))
	elif fName == "getRegions":
		return(getRegionList())
	elif fName == "searchResult":
		return(searchResult(param))
	else:
		return("DB server" + str(param))

def log_Info(mess):
	ip = gethostbyname(gethostname()) 
	t = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	strMess = t + "\t" + ip + "\t" + mess + "\n"
	with open(LOG_FILE,'a') as f:
		f.write(strMess)

# Requests
def ose():
	print(logPass)
	ostxt = str(os.environ)
	#f = open('workfile.txt', 'w')
	#f.write("testtt\n")
	#f.close()
	
	# Autre techique
	#x = json.dumps([1, 'simple', 'list'])
	#json.dump(x, f)
	
	log_Info('oseFunct')

	return(logPass)


	
def listLog():

	htmlCode = '<!DOCTYPE html><html lang="en-CA"><head><meta name="viewport" content="width=device-width" /></head><body><form action="/listLog2?" method="post"><input type="password" name="pass"></form></body></html>'
	return(htmlCode)

def listLog2():

	fileList = os.listdir(LOG_DIR)
	cont = '<h2>Log files</h2>'
	for line in fileList:
		f = os.stat(LOG_DIR + '/' + line)
		t = time.ctime(f.st_ctime)
		s = f.st_size
		cont = cont + '<a target="_blank" href="./showLog?nam=' + line + '">' + line + "\t" + t + "\t" + str(int(s/1024) + 1) + " ko" '</a></br>'
	#print(fileList)
	return(str(cont))
	
def showLog(param):
	print(str(param))
	if param.get("nam"):
		fileName = param["nam"][0]
	lines = [line.rstrip('\n') for line in open(LOG_DIR + "/" + fileName)]
	f = os.stat(LOG_DIR + '/' + fileName)
	cont = '<h2>' + fileName + "  " + time.ctime(f.st_ctime) + '</h2>'
	for line in lines:
		cont = cont + line + '</br>'
	return(str(cont))

def getRegionList():
	col = data.regions
	docs = col.find({})
	res = dumps(docs)
	return res
	
def searchResult(param):
	print(str(param))
	if param.get("qn"):
		qNom = param["qn"][0]
		qVille = param["qv"][0]
	if param.get("qr"):
		qReg = int(param["qr"][0])
	if param.get("qd"):
		dist = float(param["qd"][0])
		lng = float(param["qlt"][0])
		lat = float(param["qln"][0])
	qT = []
	col = data.club
	
	if 'qNom' in locals():
		#regx = re.compile("alb", re.IGNORECASE)
		regxN = re.compile(qNom, re.IGNORECASE)
		regxV = re.compile(qVille, re.IGNORECASE)
		q1 = {"$or": [ {"nom": {"$regex": regxN } } , {"municipal": {"$regex": regxV} } ]}
		qT.append(q1)
		#docs = col.find(q1)
	
	if 'qReg' in locals():
		q2 = {'region': qReg}
		qT.append(q2)

	if 'dist' in locals():
		q3 = {"location": { "$near" : {"$geometry": { "type": "Point",  "coordinates": [ lng , lat ] }, "$maxDistance": dist }}};
		qT.append(q3)
		
	query = { "$and": qT }
	docs = col.find(query).sort("nom")
	res = dumps(docs)
	return res
	
	
# Start server
def run(server_class=HTTPServer, handler_class=golfHTTPServer, port=8080, domain = ''):
	# Server settings
	print(str(port))
	server_address = (domain, port)
	httpd = HTTPServer(server_address, handler_class)
	print('running server...(' + domain + ":" + str(port) + ')')
	httpd.serve_forever()
	return

def build_arg_dict(arg):
	argd = dict()
	def add_dict(item):
		i = 0
		for x in arg:
			if x == item:
			  argd[x] = arg[i+1]
			else:
			  i+= 1

	if "port" in arg:
		add_dict("port")
	if "domain" in arg:
		add_dict("domain")
	if "pass" in arg:
		add_dict("pass")
		
	#print("DIC=" + str(argd) + str(len(arg)) + str(len(argd)))
	if (len(arg) / 2) != len(argd):
		return False
	else:
		return argd

if __name__ == "__main__":
	print(argv[0])
	if len(argv) > 2:
		arg = [x for x in argv]
		del arg[0]
		argt = {x for x in arg}
		#argd = dict(argt)
		#print(str(arg))
		param = build_arg_dict(arg)
		print(str(param))
		if param:
			if "pass" in param:
				global logPass 
				logPass = param["pass"]
			if "domain" in param and "port" in param:
				run(domain=(param["domain"]), port=int(param["port"]))
			elif "domain" in param:
				run(domain=(param["domain"]))
			elif "port" in param:
				run(port=int(param["port"]))				
		else:
			print("[domain VALUE] [port VALUE] [pass VALUE]")
		#run(port=int(argv[1]), domain=argv[2])
	elif len(argv) > 1:

		x=1
		#run(port=int(argv[1]))
	else:
		run()


    
