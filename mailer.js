'use strict';
const fs = require('fs');
const nodemailer = require('nodemailer');
const jsonInfo = "mailInfo.json";
var transporter = null;
var subject, toMail, userM, passW;

var Mailer = {
	user: "",
	pass: ""
}

Mailer.initMailer = initM;

function initM(mailer, PARAM_DIR) {
	
//console.log(process.env.MAIL + " Pass= " + process.env.INFO);
  fs.readFile( PARAM_DIR + jsonInfo, function(err, jsonInfo) {  
    if (err) {
		console.log('Error reading mailInfo.json : ' + err.message);
    }else {
		var mailInfo = JSON.parse(jsonInfo);
		subject = mailInfo.subject;
		toMail = mailInfo.to;

		if (process.env.MAIL){
			userM = process.env.MAIL;
			passW = process.env.INFO;
		}else{
			userM = mailInfo.user;
			passW = mailInfo.pass;
		}
		mailer.user = userM;
		mailer.pass = passW;
		// Create a SMTP transporter object
		transporter = nodemailer.createTransport({
			service: 'Gmail',
			auth: {
				user: userM,
				pass: passW
			}
		}, {
			// sender info
			from: 'Golf du Quebec <cdore00@yahoo.ca>',
			headers: {
				'X-Laziness-level': 1000 // just an example header, no need to use this
			}
		});
	}
  });

}
// END define email transporter

Mailer.formatMailData = function (HOST, userMail, userPass) {
	
var formattedBody = '<html><body><div style="text-align: center;"><div style="background-color: #3A9D23;height: 34px;"><div style="margin: 3px;float:left;"><img alt="Image Golf du Québec" width="25" height="25" src="https://cdore00.github.io/golf/images/golf.png" /></div><div style="font-size: 22px;font-weight: bold;color: #ccf;padding-top: 5px;">Golfs du Qu&eacute;bec</div></div></br><a href="%1" style="font-size: 20px;font-weight: bold;">Cliquer ce lien pour confirmer l\'inscription de votre compte:<p>%2</p> </a></br></br></br><p><div id="copyright">Copyright &copy; 2005-2017</div></p></div></body></html>';

formattedBody = formattedBody.replace("%1", HOST + "confInsc?data=" + userMail);
formattedBody = formattedBody.replace("%2", userMail);

return formattedBody;
}

Mailer.formatMailPass = function (HOST, userName, userMail, userPass) {
	
var formattedBody = '<html><body><div style="text-align: center;"><div style="background-color: #3A9D23;height: 34px;"><div style="margin: 3px;float:left;"><img alt="Image Golf du Québec" width="25" height="25" src="https://cdore00.github.io/golf/images/golf.png" /></div><div style="font-size: 22px;font-weight: bold;color: #ccf;padding-top: 5px;">Golfs du Qu&eacute;bec</div></div></br><p style="width: 100%; text-align: left;">Bonjour&#8239; %1,</p><p>&#8239;</p><p style="width: 100%; text-align: left;">Votre mot de passe est :&#8239; %2 </p><p>&#8239;</p><p><div id="copyright">Copyright &copy; 2005-2017</div></p></div></body></html>';

formattedBody = formattedBody.replace("%1", userName);
formattedBody = formattedBody.replace("%2", userPass);

return formattedBody;
}

Mailer.sendMessage = function( res, userName, userMail, bodyMess, linkMess) {
	// Message object
	var message = {

		// Comma separated list of recipients
		to: userMail,
		cc: toMail,
		subject: subject + userName, //

		// HTML body
		html: bodyMess ,
		// Apple Watch specific HTML body
		watchHtml: bodyMess 
	};
	//console.log('Sending Mail...');  // + message.html
	transporter.sendMail(message, (error, info) => {
		if (error) {
			console.log('Error occurred');
			console.log(error.message);
		}else{
			//this.logFile('Message sent successfully to: ' + userMail + '! Server responded with: ' + info.response);
			console.log('Server responded with "%s"', info.response);
			if (res){
				res.write(linkMess);
				res.end();  //JSON.stringify(infoVal)
			}
		}
		transporter.close();
	});
}

module.exports = Mailer;