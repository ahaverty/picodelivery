/*
*	The custom queries defined in the Backand.com service
*	Query name, parameters, and the actual sql query are listed
*	for each below.
*	@author: alanhaverty@student.dit.ie
*/


------------------------
--Custom Query: acceptJob
--Parameters: jobDetailId
CALL acceptJobAsDriver({{jobDetailId}}, "{{sys::username}}");

------------------------
--Custom Query: captureDriverLocation
--Parameters: lat,lng
INSERT INTO driver_location (driver_id, coordinates)
VALUES (
    (
        SELECT d.id FROM driver d
        INNER JOIN user u on d.user_id = u.id
        WHERE u.email = '{{sys::username}}'
        LIMIT 1
    ),
    GeomFromText('POINT({{lng}} {{lat}})')
)
ON DUPLICATE KEY UPDATE coordinates=VALUES(coordinates);

------------------------
--Custom Query: createJobRequest
--Parameters: street,map_point,fname,lname,mnumber,tip, paymentDue,prepaid,pickuptime,packagesize
set autocommit = 0;

INSERT INTO address
(street, map_point)
VALUES
('{{street}}', GEOMFROMTEXT('{{map_point}}'));

INSERT INTO customer
(address_id, first_name, last_name, mobile_number)
VALUES
(last_insert_id(),
'{{fname}}',
'{{lname}}',
'{{mnumber}}');

INSERT INTO job_detail
(restaurant_id,
customer_id,
tip_text,
prepaid,
payment_due,
pickup_time_requested,
package_size)
VALUES
(
(SELECT r.id from restaurant r
join user u on u.id = r.user_id
where u.email = '{{sys::username}}'),
last_insert_id(),
'{{tip}}',
{{prepaid}},
{{paymentDue}},
DATE_ADD(NOW(), INTERVAL '{{pickuptime}}' MINUTE),
{{packagesize}});

SELECT id from job
where job_detail_id = last_insert_id();

commit;

------------------------
--Custom Query: createNewArea
--Parameters: areaName, areaPolygon
INSERT INTO area
(name, area)
VALUES
("{{areaName}}",GeomFromText("{{areaPolygon}}"));

------------------------
--Custom Query: createRestaurantWithAddress
--Parameters: restaurantName, streetAddress, mapPoint
INSERT INTO address
(street,  map_point)
VALUES
("{{streetAddress}}", GeomFromText("{{mapPoint}}") );

INSERT INTO restaurant
(name, address_id)
VALUES
("{{restaurantName}}", (SELECT id FROM address WHERE map_point = GeomFromText("{{mapPoint}}") LIMIT 1));

SELECT id from restaurant
order by id desc
limit 1;

------------------------
--Custom Query: getActiveJobForDriver
SELECT
jd.id as job_detail_id,
j.id as job_id,
r.id as restaurant_id,
r.mobile_number as restaurant_mobile_number,
c.mobile_number as customer_mobile_number,
c.first_name as customer_first_name,
jd.tip_text as tip_text,
jd.prepaid as prepaid,
jd.estimated_worth as estimated_worth,
jd.pickup_time_requested as pickup_time_requested,
j.status_id as status_id,
s.description as status_description,
j.create_time as create_time,
j.start_time as start_time,
j.end_time as end_time,
j.payload_collected_time as payload_collected_time,
r.name as restaurant_name,
ra.street as restaurant_street,
ca.street as customer_street,
ASTEXT(ra.map_point) as restaurant_map_point,
ASTEXT(ca.map_point) as customer_map_point,
ST_Y(ra.map_point) as restaurant_lat,
ST_X(ra.map_point) as restaurant_lng,
ST_Y(ca.map_point) as customer_lat,
ST_X(ca.map_point) as customer_lng
FROM job j
JOIN job_detail jd on jd.id = j.job_detail_id
JOIN restaurant r on r.id = jd.restaurant_id
JOIN address ra on ra.id = r.address_id
JOIN status s on s.id = j.status_id
JOIN customer c on c.id = jd.customer_id
JOIN address ca on ca.id = c.address_id
WHERE j.driver_id IN
    (SELECT id FROM driver
    WHERE user_id IN
        (SELECT id FROM user
        WHERE email = '{{sys::username}}')
    )
AND j.status_id < 4
AND j.status_id > 1;

------------------------
--Custom Query: getActualsAndPredictions
--Parameters: areaId,fromDate,toDate
SELECT CONVERT_TZ(hp.start_hour,@@session.time_zone,'UTC') as hour,
hp.predicted_value as prediction,
ag.count_of_jobs as actual
FROM hourly_prediction hp
LEFT JOIN aggregate_hourly_jobs ag
on ag.start_hour = hp.start_hour AND hp.area_id = ag.area_id
WHERE hp.start_hour between '{{fromDate}}' AND '{{toDate}}'
AND hp.area_id = {{areaId}}
;

------------------------
--Custom Query: getAddresses
--Parameters: id
SELECT * FROM address
WHERE id in ({{id}});

------------------------
--Custom Query: getAllAreaNameAndPolygon
SELECT name as areaName, ASTEXT(area) as area
FROM area
WHERE ASTEXT(area) is not null;

------------------------
--Custom Query: getAllAreaPolygonAndCoverage
SET @PERIOD_TIME = 20;
SET @sum_all_drivers = 0;

SELECT *, (t.amount_of_drivers_needed / @sum_all_drivers) as coverage
FROM (
SELECT
	@rate:=ROUND(hp.predicted_value / (60/@PERIOD_TIME))
    as rate_of_jobs,
	
    @pending:=(
		SELECT count(*) as count
		FROM job jr
		INNER JOIN job_detail jdr on jdr.id = jr.job_detail_id
		INNER JOIN restaurant rr on rr.id = jdr.restaurant_id
		INNER JOIN address ar on ar.id = rr.address_id
		WHERE jr.status_id = 1
		AND ar.area_id = hp.area_id
    )
	as jobs_pending,
    
    @recent_drivers:=(
		SELECT count(*) as count
		FROM driver_location dl
		WHERE ST_CONTAINS(a.area, dl.coordinates) 
		AND dl.captured > DATE_SUB(now(), INTERVAL @PERIOD_TIME MINUTE)
	) as drivers_in_area,
    
    @drivers_will_be:=(
		SELECT count(*) as count
        FROM job jc
		INNER JOIN job_detail jdc on jdc.id = jc.job_detail_id
		INNER JOIN customer cc on cc.id = jdc.customer_id
		INNER JOIN address ac on ac.id = cc.address_id
		WHERE  jc.status_id between 2 and 3
		AND jc.payload_collected_time > DATE_SUB(now(), INTERVAL @PERIOD_TIME MINUTE)
        AND ac.area_id = hp.area_id
    ) as drivers_soon_to_be_in_area,
    
    (@drivers_needed:= ROUND(@rate + @pending - (4/5 * (@recent_drivers)) - (4/5 * (@drivers_will_be)))) as amount_of_drivers_needed,
    
    (@sum_all_drivers := @sum_all_drivers + @drivers_needed) as tmp_running_sum_drivers_total,
    
	hp.area_id as area_id,
	
	ST_Y(centroid(a.area)) as centroid_lat,

	ST_X(centroid(a.area)) as centroid_lng,
	
    ASTEXT(a.area) as area
    
FROM hourly_prediction hp
INNER JOIN area a on a.id = hp.area_id
WHERE start_hour = IF(MINUTE(NOW()) between 0 and 3,
@CURRENT_FLOORED_HOUR := DATE_SUB(DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00"'),INTERVAL 1 HOUR),
@CURRENT_FLOORED_HOUR := DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00"'))
GROUP BY area_id) as t;

------------------------
--Custom Query: getAllRestaurantAndPoint
SELECT r.id as id, r.name as restaurantName, ASTEXT(a.map_point) as mapPoint,
ST_Y(a.map_point) as lat, ST_X(a.map_point) as lng, a.street
FROM restaurant r
JOIN address a ON r.address_id = a.id;

------------------------
--Custom Query: getAreasThatHavePredictions
SELECT area_id FROM hourly_prediction
GROUP BY area_id;

------------------------
--Custom Query: getAvailableJobsForDriver
SELECT jd.id as id,
r.name as name,
a.street as street,
jd.estimated_worth as estimated_worth,
ASTEXT(a.map_point) as map_point_as_text
FROM job j
INNER JOIN job_detail jd on j.job_detail_id = jd.id
INNER JOIN restaurant r on r.id = jd.restaurant_id
INNER JOIN address a on a.id = r.address_id
WHERE j.create_time > DATE_SUB(now(), INTERVAL 10 MINUTE)
AND j.status_id = 1
ORDER BY ST_DISTANCE(a.map_point, POINT({{currentLng}}, {{currentLat}}))
LIMIT {{limit}}
;

------------------------
--Custom Query: getCustomers
--Parameters: id
SELECT * FROM customer
WHERE id in ({{id}});

------------------------
--Custom Query: getDrivers
--Parameters: id
SELECT * FROM driver
WHERE id in ({{id}});

------------------------
--Custom Query: getDriversHistory
--Parameters: limitStart,limitEnd
SELECT *
FROM job j
INNER JOIN job_detail jd on jd.id = j.job_detail_id
INNER JOIN restaurant r on r.id = jd.restaurant_id
INNER JOIN driver d on j.driver_id = d.id
INNER JOIN user u on u.id = d.user_id
WHERE u.email = '{{sys::username}}'
AND status_id > 3
ORDER BY j.id desc
LIMIT {{limitStart}},{{limitEnd}}

------------------------
--Custom Query: getDriversStats
SELECT sum(TIMESTAMPDIFF(SECOND, j.start_time, j.end_time)) as total_job_time,
sum(jd.estimated_worth) as total_earnings
FROM driver d
JOIN job j on j.driver_id = d.id
JOIN job_detail jd on jd.id = j.job_detail_id
JOIN user u on u.id = d.user_id
WHERE u.email = '{{sys::username}}'
AND j.status_id > 3

------------------------
--Custom Query: getJobDetails
--Parameters: id
SELECT * FROM job_detail
WHERE id in ({{id}});

------------------------
--Custom Query: getJobDetailsForDriver
--Parameters: jobId
SELECT
jd.id as job_detail_id,
r.id as restaurant_id,
jd.prepaid as prepaid,
jd.estimated_worth as estimated_worth,
jd.pickup_time_requested as pickup_time_requested,
r.name as restaurant_name,
ra.street as restaurant_street,
ca.street as customer_street,
ASTEXT(ra.map_point) as restaurant_map_point,
ASTEXT(ca.map_point) as customer_map_point
FROM job_detail jd
JOIN restaurant r on r.id = jd.restaurant_id
JOIN address ra on ra.id = r.address_id
JOIN customer c on c.id = jd.customer_id
JOIN address ca on ca.id = c.address_id
JOIN job j on j.job_detail_id = jd.id
WHERE jd.id = {{jobId}}
AND j.status_id = 1;

------------------------
--Custom Query: getLocation
--Parameters: table, id
SELECT ST_X(a.map_point) as lng, ST_Y(a.map_point) as lat
FROM {{table}} t
JOIN address a on a.id = t.address_id
WHERE t.id = {{id}};

------------------------
--Custom Query: isDriverOnJob
SELECT count(*) as count
FROM job j
WHERE j.driver_id IN
    (SELECT id FROM driver
    WHERE user_id IN
        (SELECT id FROM user
        WHERE email = '{{sys::username}}')
    )
AND j.status_id < 4
AND j.status_id > 1;
