
/*
This file is an extract from the Backand.com service,
It's purpose is to query google's direction API
And calculate a worth of the job, based on the trip time
returned from Google.
Created by alanhaverty@student.dit.ie
*/



/* globals
  $http - Service for AJAX calls 
  CONSTS - CONSTS.apiUrl for Backands API URL
  Config - Global Configuration
  socket - Send realtime database communication
  files - file handler, performs upload and delete of files
  request - the current http request
*/

function getCustomerLocation(customerId) {
    var response = $http({
        method: "GET",
        url: CONSTS.apiUrl + "/1/query/data/getLocation",
        params: {
            parameters: {
                table:"customer",
                id:customerId
            }
        },
        headers: {"Authorization": userProfile.token}
    });
    return response[0];
}

function getRestaurantLocation(restaurantId) {
    var response = $http({
        method: "GET",
        url: CONSTS.apiUrl + "/1/query/data/getLocation",
        params: {
            parameters: {
                table:"restaurant",
                id:restaurantId
            }
        },
        headers: {"Authorization": userProfile.token}
    });
    return response[0];
}

function getDuration(origin, destination) {
    
    var response = $http({
        method: "GET",
        url: "https://maps.googleapis.com/maps/api/distancematrix/json",
        params: {
            units:"imperial",
            origins:origin,
            destinations:destination,
            key:Config.googleServerKey
        }
    });
    return response.rows[0].elements[0].duration.value;
}

function round(x, n) {
    return Math.round(x * Math.pow(10, n)) / Math.pow(10, n)
}

function calculateWorth(duration) {
    return round((Config.hourthWorth/3600) * duration, 2);
}


function commitWorth(worth) {
    var response = $http({
      method: "PUT",
      url: CONSTS.apiUrl + "/1/objects/job_detail/" + dbRow.id,
      data: {
        estimated_worth: worth
      },
      headers: {"Authorization": userProfile.token}
    });
}

'use strict';
function backandCallback(userInput, dbRow, parameters, userProfile) {
    var customerLocation = getCustomerLocation(dbRow.customer_id);
    var restaurantLocation = getRestaurantLocation(dbRow.restaurant_id);
    
    var origin = restaurantLocation.lat + "," + restaurantLocation.lng;
    var destination = customerLocation.lat + "," + customerLocation.lng;
    
    var duration = getDuration(origin, destination);
    
    var jobWorth = calculateWorth(duration);
    
    //console.log("jobWorth: " + jobWorth);
    commitWorth(jobWorth);
}
