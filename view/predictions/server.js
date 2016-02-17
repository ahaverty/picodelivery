var connect = require('connect');
var serveStatic = require('serve-static');

var port = 8080

try{
	console.log('Attempting to start listening on port: ' + port)
	connect().use(serveStatic(__dirname)).listen(port);
	console.log('Connection success, listening on port: ' + port)
} catch (e) {
	console.log('Exception occured trying to connect port ' + port);
	console.log(e)
}
