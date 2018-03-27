#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from sys import argv

import urllib.parse
import urllib.request
import re
from http import cookies

import os
#import requests as req
#from io import BytesIO

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
	def callFunc(strURL):
		print("strURL=" + strURL)
		pos = strURL.find("?")
		if pos == -1:
		  func = strURL[1:]
		else:
		  func = strURL[1:pos]
		return func
	
	@staticmethod
	def returnRes(self,mess):
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
		
		ose = (str(os.environ))
		#print(ose)
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
		message = caseFunc(self.callFunc(url), query_components)
		self.returnRes(self,message)
		return
	def do_POST(self):

		# Send message back to client
		query_components = parse_qs(urlparse(self.path).query)
		url = self.path
		print("POST " + url)
		message = caseFunc(self.callFunc(url), query_components)
		self.returnRes(self,message)
		
		return		

#End class

def caseFunc(fName, param):
	if fName == "getRegions":
		return(getRegionList())
	elif fName == "searchResult":
		return(searchResult(param))
	else:
		return("DB server" + str(param))

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
	
def run(server_class=HTTPServer, handler_class=golfHTTPServer, port=8080, domain = ''):
	# Server settings
	server_address = (domain, port)
	httpd = HTTPServer(server_address, handler_class)
	print('running server...(' + domain + ":" + str(port) + ')')
	httpd.serve_forever()
	return
	
if __name__ == "__main__":
	print(argv[0])
	if len(argv) > 2:
		run(port=int(argv[1]), domain=argv[2])
	elif len(argv) > 1:
		run(port=int(argv[1]))
	else:
		run()


    
