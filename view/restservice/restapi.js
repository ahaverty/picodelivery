/**
 * http://usejsdoc.org/
 */
var restify = require('restify');
var mysql = require('mysql');
var PropertiesReader = require('properties-reader');

var properties = new PropertiesReader('view.properties');

var connection = mysql.createConnection({
               host : properties.get('dbhost'),
               user : properties.get('dbuser'),
               password : properties.get('dbpass'),
               database: properties.get('dbname')
         });
 
var ip_addr = '0.0.0.0'
var port    =  '8081';
 
var server = restify.createServer({
    name : properties.get('hostname')
});
 
server.use(restify.queryParser());
server.use(restify.bodyParser());
server.use(restify.CORS());
server.listen(port ,ip_addr, function(){
    console.log('%s listening at %s ', server.name , server.url);
});
 
var PATH = '/api';
//server.get({path : PATH , version : '0.0.1'} , getAllPredictions);
server.get({path : PATH +'/predictions/:areaId' +'/:limit' , version : '0.0.1'} , getAreasPredictions);
server.get({path : PATH +'/actualandpredictions/:areaId' +'/:limit' , version : '0.0.1'} , getAreasActualsAndPredictions);
//server.post({path : PATH , version: '0.0.1'} , postNewUser);
//server.del({path : PATH +'/:userId' , version: '0.0.1'} , deleteUser);

function getAllPredictions(req, res, next) {
	connection.query('SELECT * FROM hourly_prediction', function (error, results){
	      if(error) {
	    	  throw error;
	      }
	      res.send(200, results);
	      return next();
	  });
}

function getAreasPredictions(req, res, next) {
	console.log("getAreasPredictions for areaid " + req.params.areaid + " for " + req.params.limit + " results.")
	connection.query('SELECT UNIX_TIMESTAMP(start_hour) as hour, predicted_value as value FROM (SELECT * FROM picodelivery.hourly_prediction WHERE area_id = ' + req.params.areaId + ' ORDER BY id DESC LIMIT ' + req.params.limit + ' ) T1 ORDER BY id', function (error, results){
	      if(error) {
	    	  throw error;
	      }
	      res.send(200, results);
	      return next();
	  });
}

function getAreasActualsAndPredictions(req, res, next) {
	console.log("getAreasActualsAndPredictions for areaid " + req.params.areaid + " for " + req.params.limit + " results.")
	connection.query('SELECT UNIX_TIMESTAMP(start_hour) as hour, count_of_jobs as actual, predicted_value as value FROM ( SELECT h.id, a.count_of_jobs, h.predicted_value, h.start_hour FROM picodelivery.hourly_prediction h JOIN picodelivery.aggregate_hourly_jobs a USING(start_hour) WHERE h.area_id = ' + req.params.areaId + ' AND a.area_id = ' + req.params.areaId + ' ORDER BY h.id DESC  LIMIT ' + req.params.limit + '  ) T1 ORDER BY id', function (error, results){
	      if(error) {
	    	  throw error;
	      }
	      res.send(200, results);
	      return next();
	  })
}
