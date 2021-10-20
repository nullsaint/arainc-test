from django.db import connection

# Listing user stats
def sp_listing_stats(start_date, end_date):
  with connection.cursor() as cursor:
    cursor.execute("""SELECT
      wscr.username, wscr.screened, IF(wscr.login_hour>0,wscr.login_hour,0) AS screening_hour, xchecked.crosschecked, IF(xchecked.login_hour>0,xchecked.login_hour,0) AS crosschecked_hour,
      ms.message_sent, IF(ms.login_hour>0,ms.login_hour,0) AS ms_hour, omsq.oms, IF(omsq.login_hour>0,omsq.login_hour,0) AS oms_hour,      
      (IF(wscr.login_hour>0,wscr.login_hour,0)+IF(xchecked.login_hour>0,xchecked.login_hour,0)+IF(ms.login_hour>0,ms.login_hour,0)+IF(omsq.login_hour>0,omsq.login_hour,0)) AS total_hour
    FROM 
      (SELECT
        auth_user.username AS username, auth_user.id AS va, COUNT(araincdb_listing.id) AS screened,
          SUM(IF (TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time)) )) AS login_hour
      FROM
        auth_user
      LEFT JOIN
        araincdb_listing ON auth_user.id=araincdb_listing.screened_by_id AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL        
      GROUP BY
        auth_user.id) wscr
      LEFT JOIN
      (SELECT
        auth_user.id AS va, COUNT(araincdb_listing.id) AS crosschecked,
          SUM(IF (TIME_TO_SEC(TIMEDIFF(cs_crosscheck_date, cs_crosscheck_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(cs_crosscheck_date, cs_crosscheck_start_time)) )) AS login_hour
      FROM
        auth_user
      LEFT JOIN
        araincdb_listing ON auth_user.id=araincdb_listing.cs_crosscheck_by_id AND cs_crosscheck_status='Complete' AND (cs_crosscheck_date>=%s AND cs_crosscheck_date<%s) AND cs_crosscheck_start_time IS NOT NULL
      GROUP BY
        auth_user.id) xchecked ON wscr.va = xchecked.va
      LEFT JOIN
      (SELECT
        auth_user.id AS va, COUNT(araincdb_listing.id) AS message_sent,
          SUM(IF (TIME_TO_SEC(TIMEDIFF(ms_date, ms_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(ms_date, ms_start_time)) )) AS login_hour
      FROM
        auth_user
      LEFT JOIN
        araincdb_listing ON auth_user.id=araincdb_listing.ms_by_id AND ms_status='Complete' AND (ms_date>=%s AND ms_date<%s) AND ms_start_time IS NOT NULL
      GROUP BY
        auth_user.id) ms
      ON wscr.va = ms.va
      LEFT JOIN
      (SELECT
        auth_user.id AS va, COUNT(araincdb_listing.id) AS oms,
          SUM(IF (TIME_TO_SEC(TIMEDIFF(oms_date, oms_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(oms_date, oms_start_time)) )) AS login_hour
      FROM
        auth_user
      LEFT JOIN
        araincdb_listing ON auth_user.id=araincdb_listing.oms_by_id AND oms_status='Complete' AND (oms_date>=%s AND oms_date<%s) AND oms_start_time IS NOT NULL
      GROUP BY
        auth_user.id) omsq
      ON wscr.va = omsq.va;""", [start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date])
    rows = cursor.fetchall()
  return rows


# GrowthArchive user stats
def sp_growth_user_stats(start_date, end_date):
  with connection.cursor() as cursor:
    cursor.execute("""SELECT
		cscr.username, cscr.accepted, cscr.rejected, cscr.screened, IF(cscr.login_hour>0,cscr.login_hour,0) AS screening_hour, growth.growth_done, IF(growth.login_hour>0,growth.login_hour,0) AS growth_hour,
		unfollowing.unfollowed, IF(unfollowing.login_hour>0,unfollowing.login_hour,0) AS unfollowing_hour,
        (IF(cscr.login_hour>0,cscr.login_hour,0)+IF(growth.login_hour>0,growth.login_hour,0)+IF(unfollowing.login_hour>0,unfollowing.login_hour,0)) AS total_hour
	FROM 
		((SELECT TSCR.username, TSCR.va, ACC.accepted, REJ.rejected, TSCR.screened, TSCR.login_hour FROM
		(SELECT
			auth_user.username AS username, auth_user.id AS va, COUNT(araincdb_growth.id) AS screened,
				SUM(IF (TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time)) )) AS login_hour
		FROM
			auth_user
		LEFT JOIN
			araincdb_growth ON auth_user.id=araincdb_growth.screened_by_id AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL
		GROUP BY
			auth_user.id) TSCR
		LEFT JOIN
        (SELECT
			auth_user.id AS va, COUNT(araincdb_growth.id) AS accepted
		FROM
			auth_user
		LEFT JOIN
			araincdb_growth ON auth_user.id=araincdb_growth.screened_by_id AND quality_status_id <3 AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL
		GROUP BY
			auth_user.id) ACC ON ACC.va = TSCR.va
		LEFT JOIN
        (SELECT
			auth_user.username AS username, auth_user.id AS va, COUNT(araincdb_growth.id) AS rejected
		FROM
			auth_user
		LEFT JOIN
			araincdb_growth ON auth_user.id=araincdb_growth.screened_by_id AND quality_status_id >2 AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL
		GROUP BY
			auth_user.id) REJ ON REJ.va = TSCR.va)) cscr
		LEFT JOIN
		(SELECT
			auth_user.id AS va, COUNT(araincdb_growth.id) AS growth_done,
				SUM(IF (TIME_TO_SEC(TIMEDIFF(growthed_date, growth_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(growthed_date, growth_start_time)) )) AS login_hour
		FROM
			auth_user
		LEFT JOIN
			araincdb_growth ON auth_user.id=araincdb_growth.growthed_by_id AND growth_review_status='Complete' AND (growthed_date>=%s AND growthed_date<%s) AND growth_start_time IS NOT NULL
		GROUP BY
			auth_user.id) growth ON cscr.va = growth.va
		LEFT JOIN
		(SELECT
			auth_user.id AS va, COUNT(araincdb_growth.id) AS unfollowed,
				SUM(IF (TIME_TO_SEC(TIMEDIFF(unfollowing_date, unfollowing_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(unfollowing_date, unfollowing_start_time)) )) AS login_hour
		FROM
			auth_user
		LEFT JOIN
			araincdb_growth ON auth_user.id=araincdb_growth.unfollowing_by_id AND unfollowing_status='Complete' AND (unfollowing_date>=%s AND unfollowing_date<%s) AND unfollowing_start_time IS NOT NULL
		GROUP BY
			auth_user.id) unfollowing
		ON cscr.va = unfollowing.va;""", [start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date])
    rows = cursor.fetchall()
  return rows




# GrowthArchive user stats
def sp_growtharchive_user_stats(start_date, end_date):
  with connection.cursor() as cursor:
    cursor.execute("""SELECT
		cscr.username, cscr.accepted, cscr.rejected, cscr.screened, IF(cscr.login_hour>0,cscr.login_hour,0) AS screening_hour, growth.growth_done, IF(growth.login_hour>0,growth.login_hour,0) AS growth_hour,
		unfollowing.unfollowed, IF(unfollowing.login_hour>0,unfollowing.login_hour,0) AS unfollowing_hour,
        (IF(cscr.login_hour>0,cscr.login_hour,0)+IF(growth.login_hour>0,growth.login_hour,0)+IF(unfollowing.login_hour>0,unfollowing.login_hour,0)) AS total_hour
	FROM 
		((SELECT TSCR.username, TSCR.va, ACC.accepted, REJ.rejected, TSCR.screened, TSCR.login_hour FROM
		(SELECT
			auth_user.username AS username, auth_user.id AS va, COUNT(araincdb_growtharchive.id) AS screened,
				SUM(IF (TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time)) )) AS login_hour
		FROM
			auth_user
		LEFT JOIN
			araincdb_growtharchive ON auth_user.id=araincdb_growtharchive.screened_by_id AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL
		GROUP BY
			auth_user.id) TSCR
		LEFT JOIN
        (SELECT
			auth_user.id AS va, COUNT(araincdb_growtharchive.id) AS accepted
		FROM
			auth_user
		LEFT JOIN
			araincdb_growtharchive ON auth_user.id=araincdb_growtharchive.screened_by_id AND quality_status_id <3 AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL
		GROUP BY
			auth_user.id) ACC ON ACC.va = TSCR.va
		LEFT JOIN
        (SELECT
			auth_user.username AS username, auth_user.id AS va, COUNT(araincdb_growtharchive.id) AS rejected
		FROM
			auth_user
		LEFT JOIN
			araincdb_growtharchive ON auth_user.id=araincdb_growtharchive.screened_by_id AND quality_status_id >2 AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL
		GROUP BY
			auth_user.id) REJ ON REJ.va = TSCR.va)) cscr
		LEFT JOIN
		(SELECT
			auth_user.id AS va, COUNT(araincdb_growtharchive.id) AS growth_done,
				SUM(IF (TIME_TO_SEC(TIMEDIFF(growthed_date, growth_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(growthed_date, growth_start_time)) )) AS login_hour
		FROM
			auth_user
		LEFT JOIN
			araincdb_growtharchive ON auth_user.id=araincdb_growtharchive.growthed_by_id AND growth_review_status='Complete' AND (growthed_date>=%s AND growthed_date<%s) AND growth_start_time IS NOT NULL
		GROUP BY
			auth_user.id) growth ON cscr.va = growth.va
		LEFT JOIN
		(SELECT
			auth_user.id AS va, COUNT(araincdb_growtharchive.id) AS unfollowed,
				SUM(IF (TIME_TO_SEC(TIMEDIFF(unfollowing_date, unfollowing_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(unfollowing_date, unfollowing_start_time)) )) AS login_hour
		FROM
			auth_user
		LEFT JOIN
			araincdb_growtharchive ON auth_user.id=araincdb_growtharchive.unfollowing_by_id AND unfollowing_status='Complete' AND (unfollowing_date>=%s AND unfollowing_date<%s) AND unfollowing_start_time IS NOT NULL
		GROUP BY
			auth_user.id) unfollowing
		ON cscr.va = unfollowing.va;""", [start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date])
    rows = cursor.fetchall()
  return rows


# def sp_growth_user_stats(start_date, end_date):
#   with connection.cursor() as cursor:
#     cursor.execute("""SELECT
# 		cscr.username, cscr.screened, IF(cscr.login_hour>0,cscr.login_hour,0) AS screening_hour, growth.growth_done, IF(growth.login_hour>0,growth.login_hour,0) AS growth_hour,
# 		unfollowing.unfollowed, IF(unfollowing.login_hour>0,unfollowing.login_hour,0) AS unfollowing_hour,
#         (IF(cscr.login_hour>0,cscr.login_hour,0)+IF(growth.login_hour>0,growth.login_hour,0)+IF(unfollowing.login_hour>0,unfollowing.login_hour,0)) AS total_hour
# 	FROM 
# 		(SELECT
# 			auth_user.username AS username, auth_user.id AS va, COUNT(araincdb_growth.id) AS screened,
# 				SUM(IF (TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(screened_date, screening_start_time)) )) AS login_hour
# 		FROM
# 			auth_user
# 		LEFT JOIN
# 			araincdb_growth ON auth_user.id=araincdb_growth.screened_by_id AND screening_review_status='Complete' AND (screened_date>=%s AND screened_date<%s) AND screening_start_time IS NOT NULL
# 		GROUP BY
# 			auth_user.id) cscr
# 		LEFT JOIN
# 		(SELECT
# 			auth_user.id AS va, COUNT(araincdb_growth.id) AS growth_done,
# 				SUM(IF (TIME_TO_SEC(TIMEDIFF(growthed_date, growth_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(growthed_date, growth_start_time)) )) AS login_hour
# 		FROM
# 			auth_user
# 		LEFT JOIN
# 			araincdb_growth ON auth_user.id=araincdb_growth.growthed_by_id AND growth_review_status='Complete' AND (growthed_date>=%s AND growthed_date<%s) AND growth_start_time IS NOT NULL
# 		GROUP BY
# 			auth_user.id) growth ON cscr.va = growth.va
# 		LEFT JOIN
# 		(SELECT
# 			auth_user.id AS va, COUNT(araincdb_growth.id) AS unfollowed,
# 				SUM(IF (TIME_TO_SEC(TIMEDIFF(unfollowing_date, unfollowing_start_time))>120, 120, TIME_TO_SEC(TIMEDIFF(unfollowing_date, unfollowing_start_time)) )) AS login_hour
# 		FROM
# 			auth_user
# 		LEFT JOIN
# 			araincdb_growth ON auth_user.id=araincdb_growth.unfollowing_by_id AND unfollowing_status='Complete' AND (unfollowing_date>=%s AND unfollowing_date<%s) AND unfollowing_start_time IS NOT NULL
# 		GROUP BY
# 			auth_user.id) unfollowing
# 		ON cscr.va = unfollowing.va;""", [start_date, end_date, start_date, end_date, start_date, end_date])
#     rows = cursor.fetchall()
#   return rows

# DELIMITER //
# DROP PROCEDURE IF EXISTS sp_oms_stats;
# CREATE PROCEDURE sp_oms_stats (IN pStartDate DATE, IN pEndDate DATE)
# BEGIN
# SELECT
# q1.account_code, q2.oms, q2.oms_count, ROUND(q2.oms_count/q1.list_count*100,2) AS percent
# FROM
# (SELECT araincdb_listing.assigned_account_id AS account_id, araincdb_account.account_code, COUNT(araincdb_listing.id) AS list_count
# FROM araincdb.araincdb_listing
# LEFT JOIN araincdb_account
# ON araincdb_listing.assigned_account_id=araincdb_account.id
# WHERE araincdb_listing.ms_date>=pStartDate AND araincdb_listing.ms_date<pEndDate
# GROUP BY araincdb_listing.assigned_account_id
# )q1 LEFT JOIN
# (SELECT assigned_account_id, araincdb_oms.oms, COUNT(araincdb_listing.id) AS oms_count FROM araincdb_listing LEFT JOIN araincdb_oms ON araincdb_listing.oms_id=araincdb_oms.id
# WHERE araincdb_listing.ms_date>=pStartDate AND araincdb_listing.ms_date<pEndDate
# GROUP BY assigned_account_id, oms_id)q2
# ON
# q1.account_id=q2.assigned_account_id;
# END //

# DELIMITER //

# DROP PROCEDURE IF EXISTS sp_oms_percent;
# CREATE PROCEDURE sp_oms_percent (IN pStartDate DATE, IN pEndDate DATE)
# BEGIN
# SELECT araincdb_account.account_code, q3.total_sent, q3.reply_count, ROUND(q3.reply_count/q3.total_sent*100,2) AS percent
# FROM
# (SELECT q1.assigned_account_id, q1.total_sent, q2.reply_count FROM
# (SELECT assigned_account_id, COUNT(araincdb_listing.id) AS total_sent FROM araincdb_listing
# WHERE araincdb_listing.ms_date>=pStartDate AND araincdb_listing.ms_date<pEndDate GROUP BY assigned_account_id)q1
# LEFT JOIN
# (SELECT araincdb_listing.assigned_account_id, COUNT(id) as reply_count
# FROM araincdb.araincdb_listing
# WHERE oms_id=1 AND (araincdb_listing.ms_date>=pStartDate AND araincdb_listing.ms_date<pEndDate)
# GROUP BY araincdb_listing.assigned_account_id)q2
# ON q1.assigned_account_id=q2.assigned_account_id)q3
# LEFT JOIN araincdb_account ON q3.assigned_account_id=araincdb_account.id
# ORDER BY araincdb_account.account_code ASC;
# END //

# DELIMITER //
# CREATE PROCEDURE sp_user_stats (IN pStartDate DATE, IN pEndDate DATE)
# BEGIN
#         SELECT
#         auth_user.username, c.screened_by_id, c.completed, a.assigned, gip.growth_in_progress, gdw.growth_done_well,
#         af.already_following, cag.confusing_at_growth, cis.confusing_in_screening, r.rejected, b.bad
#         FROM
#         auth_user
#         RIGHT JOIN
#         (SELECT screened_by_id, SUM(CASE
#          WHEN quality_status_id <>1 THEN 1
#          ELSE 0
#            END) AS completed
#           FROM araincdb_growth
#           WHERE input_date >=pStartDate AND input_date<pEndDate
#           GROUP BY screened_by_id) c ON auth_user.id=c.screened_by_id
#         LEFT JOIN
#         (SELECT screened_by_id, SUM(CASE
#          WHEN connection_status_id = 11 AND quality_status_id =1 THEN 1
#          ELSE 0
#            END) AS assigned
#           FROM araincdb_growth
#           GROUP BY screened_by_id) a ON auth_user.id=a.screened_by_id
#         LEFT JOIN
#         (SELECT screened_by_id, SUM(CASE
#          WHEN connection_status_id = 13 THEN 1
#          ELSE 0
#            END) AS growth_in_progress
#           FROM araincdb_growth
#           GROUP BY screened_by_id) gip ON auth_user.id=gip.screened_by_id
#         LEFT JOIN
#         (SELECT growthed_by_id,  SUM(CASE
#          WHEN growth_status_id = 3 THEN 1
#          ELSE 0
#            END) AS growth_done_well
#           FROM araincdb_growth
#           GROUP BY growthed_by_id) gdw ON auth_user.id=gdw.growthed_by_id
#         LEFT JOIN
#         (SELECT growthed_by_id, SUM(CASE
#          WHEN growth_status_id = 1 THEN 1
#          ELSE 0
#            END) AS already_following
#           FROM araincdb_growth
#           GROUP BY growthed_by_id) af ON auth_user.id=af.growthed_by_id
#         LEFT JOIN
#         (SELECT growthed_by_id, SUM(CASE
#          WHEN growth_status_id = 2 THEN 1
#          ELSE 0
#            END) AS confusing_at_growth
#           FROM araincdb_growth
#           GROUP BY growthed_by_id) cag ON auth_user.id=cag.growthed_by_id
#         LEFT JOIN
#         (SELECT screened_by_id, SUM(CASE
#          WHEN quality_status_id = 4 THEN 1
#          ELSE 0
#            END) AS confusing_in_screening
#           FROM araincdb_growth
#           GROUP BY screened_by_id) cis ON auth_user.id=cis.screened_by_id
#         LEFT JOIN
#         (SELECT growthed_by_id, SUM(CASE
#          WHEN quality_status_id = 5 THEN 1
#          ELSE 0
#            END) AS rejected
#           FROM araincdb_growth
#           GROUP BY growthed_by_id) r ON auth_user.id=r.growthed_by_id
#         LEFT JOIN
#         (SELECT screened_by_id, SUM(CASE
#          WHEN quality_status_id = 2 THEN 1
#          ELSE 0
#            END) AS bad
#           FROM araincdb_growth
#           GROUP BY screened_by_id) b ON auth_user.id=b.screened_by_id
#         WHERE c.completed>0
#         ORDER BY auth_user.username;
# END //

# DELIMITER //

# DROP PROCEDURE IF EXISTS sp_listing_status;
# CREATE PROCEDURE sp_listing_status (IN pAccountId VARCHAR(50), IN pConnectionStatusId VARCHAR(50))
# BEGIN
# SELECT
# araincdb_account.account_code, araincdb_connectionstatus.connection_status, COUNT(araincdb_listing.id) AS list_count
# FROM araincdb_listing
# LEFT JOIN araincdb_account ON assigned_account_id=araincdb_account.id
# LEFT JOIN araincdb_connectionstatus ON connection_status_id=araincdb_connectionstatus.id
# WHERE
# araincdb_listing.assigned_account_id LIKE '%pAccountId%' AND araincdb_listing.connection_status_id LIKE '%pConnectionStatusId%'
# GROUP BY
# assigned_account_id, connection_status_id;
# END //

# DELIMITER //

# DROP PROCEDURE IF EXISTS sp_hashtag_score;
# CREATE PROCEDURE sp_hashtag_score (IN pStartDate DATE, IN pEndDate DATE)
# BEGIN
# 	SELECT
# 		g.hashtag, g.record_count AS growth_done, f.follower AS followed, ROUND((f.follower/g.record_count)*100,2) AS hashtag_score
# 	FROM
# 		(SELECT hashtag, COUNT(id) record_count FROM araincdb_growth WHERE araincdb_growth.growthed_date >= pStartDate AND araincdb_growth.growthed_date < pEndDate GROUP BY hashtag)g
# 	LEFT JOIN
# 		(SELECT
# 			araincdb_growth.hashtag, COUNT(araincdb_growth.id) AS follower
# 		FROM
# 			araincdb_growth LEFT JOIN araincdb_listing ON araincdb_growth.profile_username=araincdb_listing.profile_username
# 		WHERE
# 			(araincdb_growth.growthed_date >= pStartDate AND araincdb_growth.growthed_date < pEndDate) AND
# 			araincdb_listing.connection_type_id=2
# 		GROUP BY
# 			araincdb_growth.hashtag)f
# 	ON
# 		g.hashtag=f.hashtag WHERE f.follower>0
# 	ORDER BY
# 		f.follower DESC;
# END //


# # Set mysql environment for load data local infile
# SET GLOBAL local_infile=1;
# quit
# mysql --local-infile=1 -u root -p;
# use araincdb;


# LOAD DATA LOCAL INFILE '/mnt/c/Users/smrashel/Downloads/Growth-2020-12-31.csv' 
# INTO TABLE araincdb_growth
# FIELDS TERMINATED BY ','
# LINES TERMINATED BY '\r\n'
# IGNORE 1 LINES
# (client_name_id,profile_username,scraping_status,external_url,profile_description,full_name,caption,post_count,followers,followings,publication_date,
# hashtag,@input_date,quality_status_id,location,assigned_account_id,growth_status_id,connection_status_id,remarks,screened_by_id,@screened_date,growthed_by_id,@growthed_date,updated_by_id,@updated_date)
# SET id = NULL, input_date = STR_TO_DATE(@input_date,'%d-%b-%y %H:%i:%s'), quality_status_id = nullif(quality_status_id,''),location = nullif(location,''),assigned_account_id = nullif(assigned_account_id,''),growth_status_id = nullif(growth_status_id,''),
# remarks = nullif(remarks,''),screened_by_id = nullif(screened_by_id,''),screened_date = STR_TO_DATE(@screened_date,'%d-%b-%y %H:%i:%s'),growthed_by_id = nullif(growthed_by_id,''),growthed_date = STR_TO_DATE(@growthed_date,'%d-%b-%y %H:%i:%s'),updated_by_id = nullif(updated_by_id,''),updated_date = STR_TO_DATE(@updated_date,'%d-%b-%y %H:%i:%s');


# # Works below import
# LOAD DATA LOCAL INFILE '/mnt/c/Users/smrashel/Downloads/Growth-2020-12-30.csv' 
# INTO TABLE araincdb_growth
# FIELDS TERMINATED BY ','
# LINES TERMINATED BY '\r\n'
# IGNORE 1 LINES
# (client_name_id,profile_username,scraping_status)
# SET id = NULL;

# # Working below import
# LOAD DATA LOCAL INFILE '/mnt/c/Users/smrashel/Downloads/Growth-2020-12-30.csv' 
# INTO TABLE araincdb_growth
# FIELDS TERMINATED BY ','
# LINES TERMINATED BY '\r\n'
# IGNORE 1 LINES
# (client_name_id,profile_username,scraping_status,external_url,location,caption,publication_date,hashtag,input_date)
# SET id = NULL;

# # Listing upload worked
# LOAD DATA LOCAL INFILE '/mnt/c/Users/smrashel/Downloads/Listing_Old_Load_Data_all.csv'
# LOAD DATA LOCAL INFILE '/mnt/c/Users/smrashel/Downloads/Listing_Skipped.csv'
# INTO TABLE araincdb_listing
# FIELDS TERMINATED BY ','
# LINES TERMINATED BY '\r\n'
# IGNORE 1 LINES
# (profile_username,scraping_status, connection_type_id, assigned_account_id, connection_status_id, photo_url_query, client_name_id, external_url, profile_description, full_name, @input_date,quality_status_id)
# SET id = NULL, input_date = STR_TO_DATE(@input_date,'%Y-%m-%d');

# SET SQL_SAFE_UPDATES = 0;
# update araincdb_growth set hashtag='old_database_growth' where hashtag='2020-12-31';
# update araincdb_growth set hashtag='old_database_growth' where hashtag IS NULL;
# update araincdb_growth set hashtag='old_database_growth' where length(hashtag)>20;

# mysqldump -u root -p -R araincdb > /mnt/c/Users/smrashel/Downloads/araincdb_2021.1.17.sql


# CS Create Logic

# create queue = Listing Assigned Account = User Assigned Account, Connection Status= Ready to CS
# submit = 

# # CS Review Logic

# Listing Assigned Account = User Assigned Account, Connection Status= Ready to CS

# MS Review Logic

# OMS Review Logic

# UPDATE araincdb_growth SET connection_status_id=11 where connection_status_id=3;
# UPDATE araincdb_growth SET connection_status_id=3 where connection_status_id=1;
# UPDATE araincdb_growth SET connection_status_id=1 where connection_status_id=2;
# UPDATE araincdb_growth SET connection_status_id=2 where connection_status_id=3;
# UPDATE araincdb_growth SET connection_status_id=3 where connection_status_id=4;