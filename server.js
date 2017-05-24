//  OpenShift sample Node application

const http = require('http');
const fs = require('fs'); 
//const util = require('util');

var ip;
var url = require('url');    
//Object.assign=require('object-assign')

tl = require('./tools.js');
var infoBup = new Array();
var subWeb = '';
var subNod = 'nod/';

// Instantiate Web Server
	const server = http.createServer((req, res) => {
			//debugger;
		var url_parts = url.parse(req.url,true);
		var arrPath = url_parts.pathname.split("/");
		var filePath = arrPath[arrPath.length - 1];
		subWeb = arrPath[arrPath.length - 2] + '/';
console.log(url_parts.pathname);
		if (req.method == 'POST') {
			if (filePath == "listLog"){
				tl.listLog2(req, res, Mailer.pass);
			}else{
			if (filePath == "commPic"){
				sendImage(url_parts.query, req, res);
			}else{
				res.end();
			}}
		}else{  // method == 'GET'
			switch (filePath) {
			  case "getFav":
				getUserFav(req, res, url_parts.query);
				break;
			  case "getRegions":
				getRegionList(req, res);
				break;
			  case "getClubParc":
				getClubParcours(req, res, url_parts.query);
				break;
			  case "getClubList":
				getClubList(req, res, url_parts.query);  //À réutiliser
				break;
			  case "getGolfGPS":
				getGolfGPS(req, res, url_parts.query);
				break;
			  case "searchResult":{
				  debugger;
				searchResult(req, res, url_parts.query);
				break;				  
			  }

				
			  default:
				var param = url_parts.query;
				if (param.code)  // New code received to obtain Token
					getNewCode(req, res, url_parts)
				else{  //Cancel unknow request
					res.statusCode = 200;
					res.end("<h1>Received</h1>");
				}
			}		

		} //Fin GET
	});
// Start server listening request


var port = process.env.PORT || process.env.OPENSHIFT_NODEJS_PORT || 8080,
    ip   = process.env.IP   || process.env.OPENSHIFT_NODEJS_IP || '0.0.0.0',
    mongoURL = process.env.OPENSHIFT_MONGODB_DB_URL || process.env.MONGO_URL,
    mongoURLLabel = "";

if (mongoURL == null && process.env.DATABASE_SERVICE_NAME) {
  var mongoServiceName = process.env.DATABASE_SERVICE_NAME.toUpperCase(),
      mongoHost = process.env[mongoServiceName + '_SERVICE_HOST'],
      mongoPort = process.env[mongoServiceName + '_SERVICE_PORT'],
      mongoDatabase = process.env[mongoServiceName + '_DATABASE'],
      mongoPassword = process.env[mongoServiceName + '_PASSWORD']
      mongoUser = process.env[mongoServiceName + '_USER'];

  if (mongoHost && mongoPort && mongoDatabase) {
    mongoURLLabel = mongoURL = 'mongodb://';
    if (mongoUser && mongoPassword) {
      mongoURL += mongoUser + ':' + mongoPassword + '@';
    }
    // Provide UI label that excludes user id and pw
    mongoURLLabel += mongoHost + ':' + mongoPort + '/' + mongoDatabase;
    mongoURL += mongoHost + ':' +  mongoPort + '/' + mongoDatabase;

  }
}
var db = null,
    dbDetails = new Object();

var initDb = function(callback) {
  if (mongoURL == null) return;

  var mongodb = require('mongodb');
  if (mongodb == null) return;

  mongodb.connect(mongoURL, function(err, conn) {
    if (err) {
      callback(err);
      return;
    }

    db = conn;
    dbDetails.databaseName = db.databaseName;
    dbDetails.url = mongoURLLabel;
    dbDetails.type = 'MongoDB';

    console.log('Connected to MongoDB at: %s', mongoURL);
	console.log("Connection BD mongoServiceName=" + mongoServiceName);
	console.log("mongoHost=" + mongoHost);
	console.log("mongoPort=" + mongoPort);
	console.log("mongoDatabase=" + mongoDatabase);
	console.log("mongoPassword=" + mongoPassword);
	console.log("mongoUser=" + mongoUser);
	testBD();
  });
};

function testBD(){

  if (!db) {
    initDb(function(err){});
  }
  if (db) {
    var col = db.collection('counts');
    // Create a document with request IP and current time of request
    //col.insert({ip: req.ip, date: Date.now()});
    col.count(function(err, count){

	  console.log("Page compte11= " + count);
    });
  }
	
}

initDb(function(err){
  console.log('Error connecting to Mongo. Message:\n'+err);
});

// Start server listening request
	server.listen(port, ip, () => {
		console.log('Server started on port ' + port);
		tl.logFile('Server started on port ' + port);
	});
// END Web Server

function insertdata(res, data){
		debugger;
	var ids = data;
ids = ids.map(function(id) {  });
data = data.map(conver);

function conver(id){
	if (typeof id == 'number')
		return eval(id);
	else
		return id;
	};	

data = JSON.stringify(data);

console.log(data);
	var coll = dBase.collection('region'); 
	
	coll.insertOne( data, function(err, result) {
		 if(err) { 
			throw err; 
		}
		console.log("Insert data");
		res.statusCode = 200;
		res.end("Insert data");
		
  });	
}
