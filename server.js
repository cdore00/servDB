//  OpenShift sample Node application

const http = require('http');
const fs = require('fs'); 
//const util = require('util');

var ip;
var url = require('url');    
//Object.assign=require('object-assign')

tl = require('./tools.js');

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
			  case "searchResult":
				searchResult(req, res, url_parts.query);
				break;				
			  case "load":
				loadF(req, res, url_parts.query);
				break;					
				
			  default:
				var param = url_parts.query;
				if (param.code)  // New code received to obtain Token
					getNewCode(req, res, url_parts)
				else{  //Cancel unknow request
					res.statusCode = 200;
					res.end("<h1>Received DB</h1>");
				}
			}		

		} //End GET
	});
// End  Instantiate Web Server


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
	console.log("mongoAdmin=" + process.env[mongoServiceName + '_ADMIN_PASSWORD']);
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


//Request functions

//
function getUserFav(req, res, param){
//var strClub = "";
var arrC = new Array;

var coll = dBase.collection('userFavoris');
  // Find some documents
  coll.find({}, ["CLUB_ID"]).toArray(function(err, docs) {
    assert.equal(err, null);
	    console.log(docs);

for (var i = 0; i < docs.length; i++) {
  //strClub += "," + docs[i].CLUB_ID;
  arrC[arrC.length] = docs[i].CLUB_ID;
}
getClubNameList(res, arrC)

  });	
  	
  
}

function getClubNameList(res, clubList){
//var query = 
var a=clubList[0], b=clubList[1], c=clubList[2], d=clubList[3], e=clubList[4], f=clubList[5], g=clubList[6], h=clubList[7], i=clubList[8], j=clubList[9];
	var coll = dBase.collection('club'); 
coll.find({"_id":{$in:[ a,b,c,d,e,f,g,h,i,j ]}},["_id","nom"]).toArray(function(err, docs) {
//{"CLUB_ID":{$in:[429,424]}} 
    assert.equal(err, null);
returnRes(res, docs);
  });  
}

function returnRes(res, docs){
	
	if (res.data){
		var clubInfo = res.data;
		clubInfo[0].parc = docs;
		docs = clubInfo;
	}
		
	res.setHeader('Access-Control-Allow-Origin', '*');
	// Request methods you wish to allow
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
	// Request headers you wish to allow
	res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');
	// Set to true if you need the website to include cookies in the requests sent
	// to the API (e.g. in case you use sessions)
	//	res.setHeader('Access-Control-Allow-Credentials', true);
    res.end(JSON.stringify(docs));
}

function getRegionList(req, res){
	var coll = dBase.collection('regions'); 
coll.find({}).toArray(function(err, docs) {
    assert.equal(err, null);
	returnRes(res, docs);
  });  
}

function getClubParcours(req, res, param){
var clubID = parseInt(param.data);

	var coll = dBase.collection('club'); 
coll.find({"_id": clubID }).toArray(function(err, docs) {
    assert.equal(err, null);
	returnRes(res, docs);
  });  

}

// À réutiliser
function getClubList(req, res, param){
var query = (decodeURI(param.data));
var ids = query.split(',');
ids = ids.map(function(id) { return parseInt(id); });
var coll = dBase.collection('club');
coll.find({_id: {$in: ids }}, ["_id","nom", "adresse", "municipal", "telephone", "telephone2", "telephone3", "courses.TROUS"]).toArray(function(err, docs) {
    assert.equal(err, null);
    console.log("Found the following list clubs");
   // console.log(docs)
returnRes(res, docs);
  });
}

function getGolfGPS(req, res, param){
var courseID = parseInt(param.data);
	var coll = dBase.collection('golfGPS'); 
coll.find({"Parcours_id": courseID }).toArray(function(err, docs) {
    assert.equal(err, null);
    console.log("Found the following GPS");
    console.log(docs)
	res.data = docs;
	getBlocGPS(res, courseID);
  });
}

function getBlocGPS(res, courseID){
	var coll = dBase.collection('blocs'); 
coll.find({"PARCOURS_ID": courseID }).toArray(function(err, docs) {
    assert.equal(err, null);
    console.log("Found the following blocs");
    console.log(docs)
	returnRes(res, docs);
  });
}


function searchResult(req, res, param){
var request = (decodeURI(param.data));
var req = request.split("$");
var coll = dBase.collection('club');
	
debugger;
switch (req[0]) {
  case "1":
	listByName(req[1]);
	break;
  case "2":
	listByRegion(req[1]);
	break;
  case "3":
	listByDistance(parseFloat(req[1]), parseFloat(req[2]), parseInt(req[3]));
	break;
  default:
	res.statusCode = 200;
	res.end("No action");
}

function listByName(query){
console.log(query);
coll.find({ $or:[ {nom: {'$regex': new RegExp(query, "ig")} }, {municipal: {'$regex': new RegExp(query, "ig")} } ]}).toArray(function(err, docs) {
    assert.equal(err, null);
    console.log("Found the following search clubs");
   // console.log(docs)
returnRes(res, docs);
  });
}
	
function listByRegion(query){
var ids = query.split(',');
debugger;
ids = ids.map(function(id) { return parseInt(id); });

coll.find({region: {$in: ids }}).toArray(function(err, docs) {
    assert.equal(err, null);
    console.log("Found the following search clubs");
   // console.log(docs)
returnRes(res, docs);
  });
}

function listByDistance(lng, lat, dist){

coll.find({ location: { $near : {$geometry: { type: "Point",  coordinates: [ lng , lat ] }, $minDistance: 0, $maxDistance: dist } } }).toArray(function(err, docs) {
    assert.equal(err, null);
    console.log("Found the following near clubs");
   // console.log(docs)
returnRes(res, docs);
  });
}

}


function loadF(req, res, param){
var fileName = (decodeURI(param.data));
var collName = fileName.substring(0, fileName.indexOf("."));
console.log(collName);


switch (collName) {
  case "users":
	var  insertdata = insertUsers;
	break;
  case "userFavoris":
	var  insertdata = insertuserFavoris;
	break;
  case "regions":
	var  insertdata = insertRegions;
	break;
  case "golfGPS":
	var  insertdata = insertGolfGPS;
	break;
}


	fs.readFile(fileName, "utf8", (err, data) => {
		if(err){
			tl.logFile(err.message);
			throw err;
		}else{
			res.statusCode = 200;
			res.setHeader('Content-type', 'text/html');
			//console.log(data);
			var arrObj = JSON.parse(data);
			var coll = dBase.collection(collName); 
			console.log(coll.namespace);
			for (var p = 0; p < arrObj.length; p++) {
				if (p == arrObj.length - 1)
					insertdata(coll, arrObj[p], res);
				else
					insertdata(coll, arrObj[p]);
				//console.log("Insert data " + p);
				res.write("Insert data _id:" + arrObj[p]._id + "</br>");
			}
			}
	});	
}

function  insertuserFavoris(coll, data, res){

	coll.insertOne( {"_id": eval(data._id),"USER_ID":data.Nom,"Nom2":data.Nom2}, function(err, result) {
		 if(err) { 
			console.log("Insert erreur:" + err.message);
			throw err; 
		}
		 if (res){
			 console.log("Insert data terminate in " + coll.namespace);
			 res.end();
		 }
  });	  
}

function insertUsers(coll, data, res){

	coll.insertOne( {"_id": eval(data._id),"USER_ID": eval(data.USER_ID),"CLUB_ID": eval(data.CLUB_ID)}, function(err, result) {
		 if(err) { 
			console.log("Insert erreur:" + err.message);
			throw err; 
		}
		 if (res){
			 console.log("Insert data terminate in " + coll.namespace);
			 res.end();
		 }
  });	  
}

function insertRegions(coll, data, res){

	coll.insertOne( {"_id": eval(data._id),"Nom":data.Nom,"Nom2":data.Nom2}, function(err, result) {
		 if(err) { 
			console.log("Insert erreur:" + err.message);
			throw err; 
		}
		 if (res){
			 console.log("Insert data terminate in " + coll.namespace);
			 res.end();
		 }
  });	  
}

function insertGolfGPS(coll, data, res){

	coll.insertOne( {"_id": eval(data._id),"Parcours_id": eval(data.Parcours_id),"trou": eval(data.trou),"latitude": eval(data.latitude), "longitude": eval(data.longitude)}, function(err, result) {
		 if(err) { 
			console.log("Insert erreur:" + err.message);
			throw err; 
		}
		 if (res){
			 console.log("Insert data terminate in " + coll.namespace);
			 res.end();
		 }
  });	  
}








