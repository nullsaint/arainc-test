import os
from pathlib import Path
import shutil
from instaloader import Instaloader, Profile
import pandas as pd
from itertools import islice
from math import ceil
import glob
from instaloader import *
from django.db import connections
from instaloader.exceptions import *
from django.utils import timezone
from django.shortcuts import render,  redirect, get_object_or_404
from django.db import connection
from langdetect import *
from . models import *
from django.http import HttpResponse,JsonResponse
import io, csv
import pandas as pd
import numpy as np
import re



loader = Instaloader()
# Login or load session

cursor = connections['default'].cursor()

def dont_scrape_segment_language(client,request):
    print("language started")
    print("Segmentation Start!")
    # Get the usernames to segment for the client
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, profile_description, full_name, external_url, profile_username, remarks FROM araincdb_growth WHERE connection_status_id IS NULL AND client_name_id=%s LIMIT 3000;", [client])
        # cursor.execute("SELECT id, profile_description, full_name, external_url FROM araincdb_growth WHERE connection_status_id=3 AND client_name_id=%s;", [client])
        rows = cursor.fetchall()
        # print(rows)
    
    # Get the auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ATM' AND client_name_id=%s", [client])
        auto_match = str(list(cursor.fetchall()))
        auto_match = replace_string_in_list(auto_match)
        # print(auto_match)
    # Get the possible_auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='PAM' AND client_name_id=%s", [client])
        possible_auto_match = str(list(cursor.fetchall()))
        possible_auto_match = replace_string_in_list(possible_auto_match)
        # print(possible_auto_match)
    # Get the auto_no_match keyword list from database    
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ANM' AND client_name_id=%s", [client])
        auto_no_match = str(list(cursor.fetchall()))
        auto_no_match = replace_string_in_list(auto_no_match)
        # print(auto_no_match)
    # Get the phase_2 keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='PH2' AND client_name_id=%s", [client])
        phase_2 = str(list(cursor.fetchall()))
        phase_2 = replace_string_in_list(phase_2)
        # print(phase_2)

    automatch_id = 1
    possible_automatch_id = 2
    auto_no_match_id = 11
    screening_id = 3
    phase_2_id = 24

    for row in rows:
        y = str(row[1])
        x = y.lower()
        res = str(detect_langs(x))
        for i in possible_auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as possible_auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s, language_score = %s WHERE id =%s", [possible_automatch_id, timezone.now(), res, row[0]])
                                     

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id = %s", [automatch_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s",[automatch_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in phase_2:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as Phase 2.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id =%s", [phase_2_id, timezone.now(), row[0]])   

    for row in rows:
        y = str(row[4])
        x = y.lower()
        for i in phase_2:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as Phase 2.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id =%s", [phase_2_id, timezone.now(), row[0]])   

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s", [auto_no_match_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[3])
        x = y.lower()
        x.strip("//.")
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s", [auto_no_match_id, timezone.now(), row[0]])

    for row in rows:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE araincdb_growth SET scraping_status='done', connection_status_id = %s, scrapped_date =%s WHERE client_name_id=%s AND connection_status_id IS NULL;", [screening_id, timezone.now(), client])

    print("Segmentation complete!")
    
    with connection.cursor() as cursor:
        cursor.execute("DELETE from araincdb_tempgrowth WHERE client_name_id=%s", [client])
        deleted_usernames = cursor.rowcount
    print(str(deleted_usernames) + " usernames were deleted from Tempgrowth for " + client + ".")
    # cursor.execute("DELETE FROM araincdb_growth WHERE (scraping_status= %s)", ['notyet'])
    
    if request.method == 'POST':
        client = request.POST.get('client')
        #client_name = get_object_or_404(client, id=client)
        lang = Growth.objects.all().values_list('profile_username','profile_description','full_name','hashtag','connection_status_id','language_score').filter(client_name__id=client)
        print(lang)
        df = pd.DataFrame(lang)
        df.to_csv('data.csv',index=False)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['profile_username','profile_description','full_name','hashtag','connection_status_id','language_score'])
        for i in lang:
          writer.writerow(i)
        print(writer)
        response['Content-Disposition'] = 'attachment; filename="Growthdedupe.csv"'
        return response





# Scrape for hashtag and insert unique usernames in Grwoth model
def get_all_hashtags_posts(client, num_post, hashtag):
    hashtag  = hashtag
    posts = loader.get_hashtag_posts(hashtag)
    count = 0
    #status = 'done'
    #cursor.execute(""" DELETE FROM araincdb_tempgrowth WHERE scraping_status = ? """[status])

    for post in posts:
        profile = post.owner_profile
        client_name_id = client
        profile_username = str(profile.username)
        scraping_status = 'notyet'
        external_url = post.url
        location = ''
        caption = post.caption
        publication_date = post.date_utc
        hashtag = hashtag
        data = {
            'client_name_id': client_name_id, 'profile_username': profile_username, 'external_url': external_url, 'location': location, 'caption': caption, 'publication_date': publication_date, 'scraping_status': scraping_status, 'hashtag': hashtag
        }
        # print(data)
        
        cursor.execute("""INSERT INTO araincdb_tempgrowth (client_name_id, profile_username, scraping_status, external_url, location, caption, publication_date, hashtag) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""",
            [client_name_id, profile_username, scraping_status, external_url, location, caption, publication_date, hashtag])
            
        count += 1
        print('{}: {}'.format(count, profile_username))
        
        if count >= int(num_post):
            break
        else:
            continue

    data = {
        'client_name_id': client_name_id, 'profile_username': profile_username, 'external_url': external_url, 'location': location, 'caption': caption, 'publication_date': publication_date, 'scraping_status': scraping_status, 'hashtag': hashtag
    }
    return data


# Insert unique username in the Growth table
def dedupe_usernames(client):
    # print("Dedupe Started")
    # Delete duplicate usernames from Growthdedupe Model    
    with connection.cursor() as cursor:
        cursor.execute('''SET SQL_SAFE_UPDATES = 0;''')

    with connection.cursor() as cursor:
        cursor.execute('''DELETE FROM araincdb_growthdedupe
                            WHERE id NOT IN (
                                SELECT id FROM (
                                SELECT MAX(id) AS id FROM araincdb_growthdedupe 
                                    WHERE client_name_id=%s
                                    GROUP BY profile_username
                                )  AS g_d
                            );''', [client])
        deleted_usernames = cursor.rowcount
    # Older version
    # with connection.cursor() as cursor:
    #     cursor.execute('''DELETE t1 FROM araincdb_growthdedupe t1
    #                 INNER JOIN
    #                     araincdb_growthdedupe t2 
    #                 WHERE
	# 					(t1.client_name_id= %s AND t2.client_name_id= %s) AND
    #                     t1.id < t2.id AND 
    #                     t1.profile_username = t2.profile_username;''', [client, client])                        
    #     deleted_usernames = cursor.rowcount      
    # print(str(deleted_usernames) + " Duplicate usernames were deleted internally.")

    # Insert unique usernames to Growthunique Model
    with connection.cursor() as cursor:
        cursor.execute("SELECT @client_name_id := %s;", [client])
        
    with connection.cursor() as cursor:
        cursor.execute("""INSERT INTO araincdb_growthunique (client_name_id, profile_username, hashtag)
                    SELECT
                        araincdb_growthdedupe.client_name_id, araincdb_growthdedupe.profile_username, araincdb_growthdedupe.hashtag
                    FROM
                        araincdb_growthdedupe
                    WHERE
                        client_name_id=%s AND
                        profile_username
                    NOT IN
                        (SELECT profile_username FROM 
                        ( SELECT profile_username FROM araincdb_growth WHERE client_name_id=%s
                        UNION
                        SELECT profile_username FROM araincdb_growtharchive WHERE client_name_id=%s)q);""", [client, client, client])
        rows = cursor.rowcount    
    # print(str(rows) + " Unique usernames were retained.")
    # Remove the usernames from Growthdedupe since this has been moved to Growthunique
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM araincdb_growthdedupe WHERE client_name_id=%s", [client])

    return rows


# Insert unique username in the Growth table
def insert_unique_usernames(client):
    print("Duplciate Checker Started")
    # Delete duplicate usernames from Tempgrowth Model
    with connection.cursor() as cursor:
        cursor.execute("DELETE t1 FROM araincdb_tempgrowth t1 INNER JOIN araincdb_tempgrowth t2 WHERE (t1.client_name_id= %s AND t2.client_name_id= %s) AND t1.id < t2.id AND t1.profile_username = t2.profile_username;", [client, client])                        
        deleted_usernames = cursor.rowcount    
        print(str(deleted_usernames) + " Duplicate usernames were deleted.")

    # Insert unique usernames to Growth Model
    with connection.cursor() as cursor:
        cursor.execute("SELECT @client_name_id := %s;", [client])
    with connection.cursor() as cursor:
        cursor.execute("""INSERT INTO araincdb_growth (client_name_id, profile_username, profile_description, full_name, post_count, followers, followings, scraping_status, external_url, location, caption, publication_date, hashtag, input_date)
                    SELECT
                        @client_name_id, profile_username, profile_description, full_name, post_count, followers, followings, scraping_status, external_url, location, caption, publication_date, hashtag, now()
                    FROM
                        araincdb_tempgrowth
                    WHERE
                        client_name_id=%s AND
                        profile_username
                    NOT IN
                        (SELECT profile_username FROM 
                        ( SELECT profile_username FROM araincdb_growth WHERE client_name_id=%s
                        UNION
                        SELECT profile_username FROM araincdb_growtharchive WHERE client_name_id=%s)q)""", [client, client, client])
        rows = cursor.rowcount    
        print(str(rows) + " Unique usernames were inserted.")
    return rows


# Scrape profile data and update in Growth model
def get_profile_data(client, user):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM araincdb_growth WHERE (client_name_id= %s) AND (scraping_status= %s) AND scrapped_by_id=%s;", [client, 'notyet', user])
        assigned = cursor.fetchone()
    if assigned[0] < 1:
        with connection.cursor() as cursor:
            cursor.execute("""UPDATE araincdb_growth SET scrapped_by_id=%s WHERE id IN (
                                SELECT id FROM (
                                    SELECT id FROM araincdb_growth WHERE (client_name_id= %s) AND scraping_status='notyet' AND scrapped_by_id IS NULL
                                    ORDER BY location DESC  
                                    LIMIT 0, 500
                                ) tmp
                            );""", [user, client])
                            
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, profile_username FROM araincdb_growth WHERE (client_name_id= %s) AND (scraping_status= %s) AND scrapped_by_id=%s;", [client, 'notyet', user])
        rows = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM araincdb_growth WHERE (client_name_id= %s) AND (scraping_status= %s) AND scrapped_by_id=%s;", [client, 'notyet', user])    
        username_count = cursor.fetchone()[0]

    scraping_status = 'done'
    for row in rows:
        try:
            PROFILE = row[1]  # Insert profile name here
            id = row[0]
            L = Instaloader()
            profile = Profile.from_username(L.context, PROFILE)
            if profile.is_private == False or profile.is_verified == False:
                print("Getting Profile Data:",profile.username)
                profile_username = profile.username
                post_count = profile.mediacount
                followers = profile.followers
                followings = profile.followees
                profile_description = profile.biography
                full_name = profile.full_name
                
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET scraping_status=%s, post_count=%s, followers=%s, followings=%s, profile_description=%s, full_name=%s, scrapped_date=%s WHERE id=%s",
                    [scraping_status, post_count, followers, followings, profile_description, full_name, timezone.now(), id])
                
            else:
                continue
        except ProfileNotExistsException or BadResponseException or ConnectionException:
            continue
        except LoginRequiredException:
            import time
            time.sleep(1800)
            continue
    return username_count


# Function to replace string with new string
def replace_string_in_list(strings):
    strings = str(strings)
    # print(strings)
    remove_characters = ["[","(", ",)", "'", "]", "."]
    for character in remove_characters:
        strings = strings.replace(character, "")
        li = list(strings.split(","))
        li = [x.strip(' ') for x in li]
    return li


# Segmentating profiles in Growth model
def dont_scrape_growth_segmentation(client, user):
    print("Automatch Input Start!")
    with connection.cursor() as cursor:
        cursor.execute("UPDATE araincdb_growth SET connection_status_id = 1, scrapped_date =%s WHERE connection_status_id IS NULL AND client_name_id=%s", [timezone.now(), client])
    print("Automatch Input Complete!")


# Segmentating profiles in Growth model for scraping done profiles
def scrape_done_growth_segmentation(client):

    print("Segmentation Start!")
    # Get the usernames to segment for the client
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, profile_description, full_name, external_url, profile_username, remarks FROM araincdb_growth WHERE connection_status_id IS NULL AND client_name_id=%s LIMIT 3000;", [client])
        # cursor.execute("SELECT id, profile_description, full_name, external_url FROM araincdb_growth WHERE connection_status_id=3 AND client_name_id=%s;", [client])
        rows = cursor.fetchall()
        # print(rows)
    
    # Get the auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ATM' AND client_name_id=%s", [client])
        auto_match = str(list(cursor.fetchall()))
        auto_match = replace_string_in_list(auto_match)
        # print(auto_match)
    # Get the possible_auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='PAM' AND client_name_id=%s", [client])
        possible_auto_match = str(list(cursor.fetchall()))
        possible_auto_match = replace_string_in_list(possible_auto_match)
        # print(possible_auto_match)
    # Get the auto_no_match keyword list from database    
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ANM' AND client_name_id=%s", [client])
        auto_no_match = str(list(cursor.fetchall()))
        auto_no_match = replace_string_in_list(auto_no_match)
        # print(auto_no_match)
    # Get the phase_2 keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='PH2' AND client_name_id=%s", [client])
        phase_2 = str(list(cursor.fetchall()))
        phase_2 = replace_string_in_list(phase_2)
        # print(phase_2)

    automatch_id = 1
    possible_automatch_id = 2
    auto_no_match_id = 11
    screening_id = 3
    phase_2_id = 24

    for row in rows:
        y = str(row[1])
        x = y.lower()
        res = str(detect_langs(x))
        for i in possible_auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as possible_auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s, remarks = %s WHERE id =%s", [possible_automatch_id, timezone.now(), res, row[0]])
                                     

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id = %s", [automatch_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s",[automatch_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in phase_2:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as Phase 2.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id =%s", [phase_2_id, timezone.now(), row[0]])   

    for row in rows:
        y = str(row[4])
        x = y.lower()
        for i in phase_2:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as Phase 2.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id =%s", [phase_2_id, timezone.now(), row[0]])   

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s", [auto_no_match_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[3])
        x = y.lower()
        x.strip("//.")
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s", [auto_no_match_id, timezone.now(), row[0]])

    for row in rows:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE araincdb_growth SET scraping_status='done', connection_status_id = %s, scrapped_date =%s WHERE client_name_id=%s AND connection_status_id IS NULL;", [screening_id, timezone.now(), client])

    print("Segmentation complete!")
    for i in rows:
        with connection.cursor() as cursor:
            res = cursor.execute("SELECT * FROM araincdb_growth WHERE profile_username=?",[i[4],])
            print(res)
    with connection.cursor() as cursor:
        cursor.execute("DELETE from araincdb_tempgrowth WHERE client_name_id=%s", [client])
        deleted_usernames = cursor.rowcount
    print(str(deleted_usernames) + " usernames were deleted from Tempgrowth for " + client + ".")
    # cursor.execute("DELETE FROM araincdb_growth WHERE (scraping_status= %s)", ['notyet'])


# Segmentating profiles in Growth model
def growth_segmentation(client, user):
    print("Segmentation Start!")
    
    # Get the usernames to segment for the client
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, profile_description, full_name, external_url FROM araincdb_growth WHERE connection_status_id IS NULL AND client_name_id=%s AND scrapped_by_id=%s;", [client, user])
        rows = cursor.fetchall()
        # print(rows)
    
    # Get the auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ATM' AND client_name_id=%s", [client])
        auto_match = str(list(cursor.fetchall()))
        auto_match = replace_string_in_list(auto_match)
        # print(auto_match)
    # Get the possible_auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='PAM' AND client_name_id=%s", [client])
        possible_auto_match = str(list(cursor.fetchall()))
        possible_auto_match = replace_string_in_list(possible_auto_match)
        # print(possible_auto_match)
    # Get the auto_no_match keyword list from database    
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ANM' AND client_name_id=%s", [client])
        auto_no_match = str(list(cursor.fetchall()))
        auto_no_match = replace_string_in_list(auto_no_match)
        # print(auto_no_match)

    automatch_id = 1
    possible_automatch_id = 2
    auto_no_match_id = 11
    screening_id = 3

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in possible_auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as possible_auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id =%s", [possible_automatch_id, timezone.now(), row[0]])                

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth SET connection_status_id = %s, scrapped_date =%s WHERE id = %s", [automatch_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s",[automatch_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s", [auto_no_match_id, timezone.now(), row[0]])

    for row in rows:
        y = str(row[3])
        x = y.lower()
        x.strip("//.")
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_growth set connection_status_id = %s, scrapped_date =%s where id = %s", [auto_no_match_id, timezone.now(), row[0]])

    for row in rows:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE araincdb_growth SET scraping_status='done', connection_status_id = %s, scrapped_date =%s WHERE client_name_id=%s AND connection_status_id IS NULL AND scrapped_by_id=%s;", [screening_id, timezone.now(), client, user])

    print("Segmentation complete!")
    
    with connection.cursor() as cursor:
        cursor.execute("DELETE from araincdb_tempgrowth WHERE client_name_id=%s", [client])
        deleted_usernames = cursor.rowcount
    print(str(deleted_usernames) + " usernames were deleted from Tempgrowth for " + client + ".")
    # cursor.execute("DELETE FROM araincdb_growth WHERE (scraping_status= %s)", ['notyet'])


# Check username uniniqueness in the Listing table from Listingdedupe table
# and insert unique usernames to Listingunique Model
def dedupe_listing_usernames(client):
    # print("Dedupe Started")
    # Delete duplicate usernames from Listingdedupe Model    
    with connection.cursor() as cursor:
        cursor.execute('''SET SQL_SAFE_UPDATES = 0;''')

    with connection.cursor() as cursor:
        cursor.execute('''DELETE FROM araincdb_listingdedupe
                            WHERE id NOT IN (
                                SELECT id FROM (
                                SELECT MAX(id) AS id FROM araincdb_listingdedupe 
                                    WHERE client_name_id=%s
                                    GROUP BY profile_username
                                )  AS l_d
                            );''', [client])
        deleted_usernames = cursor.rowcount

    # Insert unique usernames to Listingunique Model
    with connection.cursor() as cursor:
        cursor.execute("SELECT @client_name_id := %s;", [client])
        
    with connection.cursor() as cursor:
        cursor.execute("""INSERT INTO araincdb_listingunique (client_name_id, profile_username, full_name, hashtag)
                    SELECT
                        client_name_id, profile_username, full_name, hashtag
                    FROM
                        araincdb_listingdedupe
                    WHERE
                        client_name_id=%s AND
                        profile_username
                    NOT IN
                        (SELECT profile_username FROM araincdb_listing WHERE client_name_id=%s);""", [client, client])
        rows = cursor.rowcount    
    # print(str(rows) + " Unique usernames were retained.")
    # Remove the usernames from Listingdedupe since this has been moved to Listingunique
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM araincdb_listingdedupe WHERE client_name_id=%s", [client])

    return rows


# Insert unique usernames in Listing model
def insert_unique_listing(client, connection_type):

    # Delete duplicate usernames from Tempgrowth Model  
    with connection.cursor() as cursor:
        cursor.execute('''DELETE t1 FROM araincdb_templisting t1
                    INNER JOIN
                        araincdb_templisting t2 
                    WHERE
						(t1.client_name_id= %s AND t2.client_name_id= %s) AND
                        t1.id < t2.id AND 
                        t1.profile_username = t2.profile_username;''', [client, client])                      
        deleted_usernames = cursor.rowcount    
    print(str(deleted_usernames) + " Duplicate usernames were deleted.")

    follower_added = 0
    like_added = 0
    if (connection_type == 'follower'):
        connection_type == 'follower'  
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO araincdb_listing (profile_username, full_name, profile_description, photo_url_query, scraping_status, connection_type_id, client_name_id, assigned_account_id, input_date)
                            SELECT q1.profile_username, q1.full_name, q1.profile_description, q1.photo_url_query, q1.scraping_status, 3 AS connection_type_id, q1.client_name_id, araincdb_account.id, %s
                            FROM
                                (SELECT profile_username, full_name, profile_description, photo_url_query, scraping_status, client_name_id, SUBSTRING(photo_url_query, 27) AS assigned_account FROM araincdb_templisting WHERE lower(connection_type)='follower')q1
                            LEFT JOIN araincdb_account on q1.assigned_account=araincdb_account.username
                            WHERE q1.client_name_id=%s AND q1.profile_username NOT IN (SELECT profile_username FROM araincdb_listing WHERE client_name_id=%s)""",[timezone.now(), client, client])        
            follower_added = cursor.rowcount    
            print(str(follower_added) + " Unique Follower usernames were inserted.")    
    else:
        connection_type == 'like'  
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO araincdb_listing (profile_username, full_name, profile_description, photo_url_query, scraping_status, connection_type_id, client_name_id, input_date)
                            SELECT profile_username, full_name, profile_description, photo_url_query, scraping_status, 2 AS connection_type_id, client_name_id, %s
                            FROM araincdb_templisting
                            WHERE lower(connection_type)='like' AND client_name_id=%s AND profile_username NOT IN (SELECT profile_username FROM araincdb_listing WHERE client_name_id=%s)""",[timezone.now(), client, client])      
            like_added = cursor.rowcount    
        print(str(like_added) + " Unique Like usernames were inserted.")
    d = dict()
    d['follower'] = follower_added
    d['like']   = like_added
    print(d)
    return d


# Scrape profile data and update in Listing model
def get_listing_profile_data(client):
    cursor.execute("SELECT profile_username FROM araincdb_listing WHERE (client_name_id= %s) AND (scraping_status= %s)", [client, 'notyet'])
    rows = cursor.fetchall()
    scraping_status = 'done'
    for row in rows:
        try:
            PROFILE = row[0]  # Insert profile name here
            L = Instaloader()
            profile = Profile.from_username(L.context, PROFILE)
            if profile.is_private == False or profile.is_verified == False:
                print("Getting Profile Data for:",profile.username)
                profile_username = profile.username
                profile_description = profile.biography
                full_name = profile.full_name
                external_url = profile.external_url
                
                cursor.execute("UPDATE araincdb_listing SET scraping_status=%s, profile_description=%s, full_name=%s, external_url=%s WHERE profile_username=%s",
                [scraping_status, profile_description, full_name, external_url, profile_username])
                
            else:
                continue
        except ProfileNotExistsException or BadResponseException or ConnectionException:
            continue
        except LoginRequiredException:
            import time
            time.sleep(1800)
            continue


# Segmentating profiles in Listing model
def dont_scrape_listing_segmentation(client, user):
    print("Automatch Input Start!")
    with connection.cursor() as cursor:
        cursor.execute("UPDATE araincdb_listing SET connection_status_id = 1 WHERE connection_status_id IS NULL AND client_name_id=%s", [client])
    print("Automatch Input Complete!")


# Segmentating profiles in Listing model for scraping done profiles
def scrape_done_listing_segmentation(client):
    print("Segmentation Start!")
    # Get the usernames to segment for the client
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, profile_description, full_name, external_url, profile_username FROM araincdb_listing WHERE connection_status_id IS NULL AND client_name_id=%s LIMIT 3000;", [client])
        rows = cursor.fetchall()
        # print(rows)
    
    # Get the auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ATM' AND client_name_id=%s", [client])
        auto_match = str(list(cursor.fetchall()))
        auto_match = replace_string_in_list(auto_match)
        # print(auto_match)
    # Get the possible_auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='PAM' AND client_name_id=%s", [client])
        possible_auto_match = str(list(cursor.fetchall()))
        possible_auto_match = replace_string_in_list(possible_auto_match)
        # print(possible_auto_match)
    # Get the auto_no_match keyword list from database    
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='ANM' AND client_name_id=%s", [client])
        auto_no_match = str(list(cursor.fetchall()))
        auto_no_match = replace_string_in_list(auto_no_match)
        # print(auto_no_match)
    # Get the phase_2 keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_growthkeyword WHERE match_type='PH2' AND client_name_id=%s", [client])
        phase_2 = str(list(cursor.fetchall()))
        phase_2 = replace_string_in_list(phase_2)
        # print(phase_2)

    automatch_id = 1
    possible_automatch_id = 2
    auto_no_match_id = 11
    screening_id = 3
    phase_2_id = 24

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in possible_auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as possible_auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE id =%s", [possible_automatch_id, row[0]])                 

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE id = %s", [automatch_id, row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE id = %s",[automatch_id, row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in phase_2:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as Phase 2.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE id =%s", [phase_2_id, row[0]])   

    for row in rows:
        y = str(row[4])
        x = y.lower()
        for i in phase_2:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as Phase 2.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE id =%s", [phase_2_id, row[0]])   

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing set connection_status_id = %s WHERE id = %s", [auto_no_match_id, row[0]])

    for row in rows:
        y = str(row[3])
        x = y.lower()
        x.strip("//.")
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing set connection_status_id = %s WHERE id = %s", [auto_no_match_id, row[0]])

    for row in rows:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE araincdb_listing SET scraping_status='done', connection_status_id = %s WHERE client_name_id=%s AND connection_status_id IS NULL;", [screening_id, client])

    print("Segmentation complete!")
    
    with connection.cursor() as cursor:
        cursor.execute("DELETE from araincdb_templisting WHERE client_name_id=%s", [client])
        deleted_usernames = cursor.rowcount
    print(str(deleted_usernames) + " usernames were deleted from Templisting for " + client + ".")

    
# Segmentating profiles in Listing model
def listing_segmentation(client):
    print("Listing segmentation Start!")
    
    # Get the usernames to segment for the client
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, profile_description, full_name, external_url from araincdb_listing WHERE connection_status_id IS NULL AND client_name_id=%s", [client])
        rows = cursor.fetchall()
    
    # Get the auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_listingkeyword WHERE match_type='ATM' AND client_name_id=%s", [client])
        auto_match = str(list(cursor.fetchall()))
        auto_match = replace_string_in_list(auto_match)
    
    # Get the possible_auto_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_listingkeyword WHERE match_type='PAM' AND client_name_id=%s", [client])
        possible_auto_match = str(list(cursor.fetchall()))
        possible_auto_match = replace_string_in_list(possible_auto_match)
    
    # Get the auto_no_match keyword list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT keyword from araincdb_listingkeyword WHERE match_type='ANM' AND client_name_id=%s", [client])
        auto_no_match = str(list(cursor.fetchall()))
        auto_no_match = replace_string_in_list(auto_no_match)

    automatch_id = 1
    possible_automatch_id = 2
    auto_no_match_id = 11
    screening_id = 3

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in possible_auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as possible_auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE id =%s", [possible_automatch_id, row[0]])

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE id = %s", [automatch_id, row[0]])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        for i in auto_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_match.')
                with connection.cursor() as cursor:
                    cursor.execute("update araincdb_listing set connection_status_id = %s WHERE id = %s",[automatch_id, row[0]])

    for row in rows:
        y = str(row[1])
        x = y.lower()
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("update araincdb_listing set connection_status_id = %s WHERE id = %s", [auto_no_match_id, row[0]])

    for row in rows:
        y = str(row[3])
        x = y.lower()
        x.strip("//.")
        for i in auto_no_match:
            if x.find(i) >= 0:
                # print('Found ' + i + ' for ' + str(row[0]) + ' : Adding as auto_no_match.')
                with connection.cursor() as cursor:
                    cursor.execute("update araincdb_listing set connection_status_id = %s WHERE id = %s", [auto_no_match_id, row[0]])


    for row in rows:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE araincdb_listing SET connection_status_id = %s WHERE client_name_id=%s AND connection_status_id IS NULL", [screening_id, client])

    print("Listing segmentation complete!")

    with connection.cursor() as cursor:
        cursor.execute("DELETE from araincdb_templisting WHERE client_name_id=%s", [client])
        deleted_usernames = cursor.rowcount
    print(str(deleted_usernames) + " usernames were deleted from Templisting for " + client + ".")
    # cursor.execute("DELETE FROM araincdb_listing WHERE (scraping_status= %s)", ['notyet'])


# Insert unique username in the Growth table
def insert_unique_posturls(client):
    print("Duplciate Checker Started")
    # Delete duplicate Post URL from TempPosturl Model
    with connection.cursor() as cursor:
        cursor.execute("""DELETE araincdb_tempposturl
                    FROM araincdb_tempposturl
                        INNER JOIN (
                        SELECT max(id) as lastId, post_url FROM araincdb_tempposturl GROUP BY post_url HAVING count(*) > 1
                        ) duplic ON duplic.post_url = araincdb_tempposturl.post_url
                    WHERE araincdb_tempposturl.id < duplic.lastId;""")
        deleted_post_urls = cursor.rowcount
    print(str(deleted_post_urls) + " Duplicate Post URLs were deleted.")

    # Insert unique usernames to Posturl Model
    with connection.cursor() as cursor:
        cursor.execute("""INSERT INTO araincdb_posturl (client_name_id, post_url, description, caption, publication_date, hashtag, input_date, is_located)
                        SELECT
                            client_name_id, post_url, description, caption, publication_date, hashtag, %s, 0
                        FROM
                            araincdb_tempposturl
                        WHERE
                            client_name_id=%s AND post_url
                        NOT IN
                            ( SELECT post_url FROM araincdb_posturl);""",[timezone.now(), client])
        rows = cursor.rowcount
    print(str(rows) + " Unique Post URLs were inserted.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE from araincdb_tempposturl WHERE client_name_id=%s", [client])
        deleted_usernames = cursor.rowcount
    print(str(deleted_usernames) + " usernames were deleted from Tempposturl for " + client + ".")

    return rows

    
# Find location from description and caption in Posturl model
def locate_posts(client):
    print("Locating post Start!")
    
    # Get the description and caption to locate the post
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, description, caption from araincdb_posturl WHERE client_name_id=%s AND is_located=0;",[client])
        rows = cursor.fetchall()
    
    # Get the US location list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT LOWER(location) from araincdb_location WHERE country_id=1;")
        us_location = str(list(cursor.fetchall()))
        us_locations = replace_string_in_list(us_location)
    # Get the Reject location list from database
    with connection.cursor() as cursor:
        cursor.execute("SELECT LOWER(location) from araincdb_location WHERE country_id=2;")
        reject_location = str(list(cursor.fetchall()))
        reject_locations = replace_string_in_list(reject_location)

    us_located = 'USA'
    reject_located = 'Reject'
    not_located = 'Unidentified'

    # for row in rows:
    #     y = str(row[1])
    #     x = y.lower()
    #     if any(location in x for location in us_locations):
    #         with connection.cursor() as cursor:
    #             cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[us_located, row[0]])
    #     elif any(location in x for location in reject_locations):
    #         with connection.cursor() as cursor:
    #             cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[reject_located, row[0]])
    #     else:            
    #         with connection.cursor() as cursor:
    #             cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where location IS NULL",[not_located])

    for row in rows:
        y = str(row[2])
        x = y.lower()
        if any(location in x for location in us_locations):
            with connection.cursor() as cursor:
                cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[us_located, row[0]])
        elif any(location in x for location in reject_locations):
            with connection.cursor() as cursor:
                cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[reject_located, row[0]])
        else:            
            with connection.cursor() as cursor:
                cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where location IS NULL",[not_located])

### Slower version ###
    # for row in rows:
    #     y = str(row[1])
    #     x = y.lower()
    #     for i in us_locations:
    #         if x.find(i) >= 0:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[us_located, row[0]])
    # for row in rows:
    #     y = str(row[2])
    #     x = y.lower()
    #     for i in us_locations:
    #         if x.find(i) >= 0:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[us_located, row[0]])

    # for row in rows:
    #     y = str(row[1])
    #     x = y.lower()
    #     for i in us_locations:
    #         if x.find(i) >= 0:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[reject_located, row[0]])
    # for row in rows:
    #     y = str(row[2])
    #     x = y.lower()
    #     for i in us_locations:
    #         if x.find(i) >= 0:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where id = %s",[reject_located, row[0]])
    # for row in rows:
    #     with connection.cursor() as cursor:
    #         cursor.execute("UPDATE araincdb_posturl set location = %s, is_located = 1 where location IS NULL",[not_located])

    print("Locating post complete!")
    

# Scrape username and update in Posturl model
def get_username(client, user):
    L = Instaloader()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM araincdb_posturl WHERE client_name_id=%s AND is_scrapped=0 AND scrapped_by_id=%s;", [client, user])
        assigned = cursor.fetchone()
    if assigned[0] < 1:
        with connection.cursor() as cursor:
            cursor.execute("""UPDATE araincdb_posturl SET scrapped_by_id=%s WHERE id IN (
                                SELECT id FROM (
                                    SELECT id FROM araincdb_posturl WHERE client_name_id=%s AND is_scrapped=0 AND scrapped_by_id IS NULL
                                    ORDER BY id ASC  
                                    LIMIT 0, 500
                                ) tmp
                            );""", [user, client])

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, post_url FROM araincdb_posturl WHERE client_name_id=%s AND is_scrapped=0 AND scrapped_by_id=%s;", [client, user])
        rows = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM araincdb_posturl WHERE client_name_id=%s AND is_scrapped=0 AND scrapped_by_id=%s;", [client, user])
        post_count = cursor.fetchone()

    for row in rows:
        id = row[0]
        post_url = row[1]

        try:
            posts = instaloader.Post.from_shortcode(L.context, post_url)
            profile_username = str(posts.owner_username)
            # print(profile_username)
            with connection.cursor() as cursor:
                cursor.execute("UPDATE araincdb_posturl SET profile_username = %s, scrapped_date = %s, is_scrapped = 1 where id=%s", [profile_username, timezone.now(), id])
        except BadResponseException or QueryReturnedBadRequestException:            
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM araincdb_posturl WHERE id=%s", [id])
            print('deleted id: ' + str(id))
            continue
    return post_count[0]


# Push usernames from Posturls to Tempgrowth
def push_usernames(client):
    with connection.cursor() as cursor:
        cursor.execute("""INSERT INTO araincdb_tempgrowth (profile_username, scraping_status, location, caption, publication_date, hashtag, client_name_id)
                        SELECT
                            profile_username, 'notyet', location, caption, publication_date, hashtag, client_name_id
                        FROM
                            araincdb_posturl
                        WHERE
                            client_name_id=%s AND is_pushed_tempgrowth=0 AND is_scrapped=1;""", [client])
        rows = cursor.rowcount
    
    if rows > 1:
        with connection.cursor() as cursor:
            cursor.execute("""UPDATE araincdb_posturl SET is_pushed_tempgrowth=1
                            WHERE
                                client_name_id=%s AND is_pushed_tempgrowth=0 AND is_scrapped=1;""", [client])
            moved_rows = cursor.rowcount

            # print(str(rows) + " Usernames were inserted." + str(moved_rows) + "usernames were updated as moved to Tempgrowth.")
    return rows

# Get Post URLs for export
def get_posturls(start_time, end_time):    
    print("Getting Post URLs from database!")
    # Getting Post URLs from database
    with connection.cursor() as cursor:
        cursor.execute("""SELECT CONCAT('https://www.instagram.com/p/',post_url,'/') AS post_url, location, caption, description, input_date
                        FROM araincdb.araincdb_posturl
                        WHERE input_date>= %s AND input_date<= %s;""", [start_time, end_time])
        row_count = cursor.rowcount
        rows = cursor.fetchall()
    print(str(row_count) + " Unique Post URLs were returned.")
    return rows


def get_profile_feed(profile_username):
    PROFILE = profile_username        # profile to download from
    profile = Profile.from_username(loader.context, PROFILE)  
    # Getting root directory to check if the profile already exists  
    root_dir = os.getcwd()
    img_dir = os.path.join(root_dir, profile_username)
    # if the profile directory does not exist, download
    if not os.path.exists(img_dir):
        for post in islice(profile.get_posts(), ceil(6)): # ceil takes a number as an argument to download
            loader.download_post(post, PROFILE)
    # Now, as feed is downloaded, we are going to make a copy of Photos in 'static/img' to serve for the users.
    photos = []
    files = []
    # Getting static image directory
    dest_dir = os.path.join(root_dir, 'static/img')
    os.chdir(dest_dir)
    # Create a directory for the profile if not exists
    Path(profile_username).mkdir(parents=True, exist_ok=True)
    # Going back to root directory
    os.chdir(root_dir)
    dest = os.path.join(root_dir, 'static/img/'+profile_username)
    # Listing photos to make a copy
    for r, d, f in os.walk(img_dir):
            for file in f:
                if file.endswith(".jpg"):
                    files.append(file)
                    photos.append('img/'+ profile_username + '/' + file)
    # print(files)
    # Moving to profile directory to copy the photos
    os.chdir(img_dir)
    # Copying the files to the destination
    for file in files:
        shutil.copy(file, dest)
    # Going back to root directory
    os.chdir(root_dir)

    # print(photos)

    return photos


def delete_profile_feed(profile_username):
    root_dir = os.getcwd()
    img_dir = os.path.join(root_dir, profile_username) # Downloaded directory
    dest = os.path.join(root_dir, 'static/img/'+profile_username) # directory in static
    try:
        shutil.rmtree(img_dir)
        shutil.rmtree(dest)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))


def get_insta_profile(profile_username):
    PROFILE = profile_username # Insert profile name here

    profile = Profile.from_username(loader.context, PROFILE)
    a = profile.mediacount
    b = profile.followees
    c = profile.followers
    d = profile.biography
    x = profile.username
    y = profile.is_private
    z = profile.profile_pic_url
    m = profile.full_name

    data = {
        "UserName": x,
        "PostCount": a,
        "Followers": c,
        "Following": b,
        "FullName" : m,
        "Biography": d,
        "ProfilePicUrl": z,
        "Is_private": y
    }
    return data


def get_followee():
    L = Instaloader()
    # Login or load session
    username = "smrashel_kanta"
    password = "lone_rider15"
    L.login(username, password)  
    # Obtain profile metadata
    profile = Profile.from_username(L.context, "smrashel_kanta")
    # file = open("prada_followers.txt","a+")
    for followee in profile.get_followees():
        username = followee.username
        full_name = followee.full_name
        profile_pic_url = followee.profile_pic_url
        profile_url = "https://www.instagram.com/" + username + "/" 
        userid = followee.userid    
        
        followee_profile = Profile.from_username(L.context, followee.username)
        followee_profile = dir(followee)
        data = {
            'userid': userid, 'username': username, 'full_name': full_name, 'profile_pic_url': profile_pic_url, 'profile_url': profile_url
        }
        print(data)

def source_phantombuster(files, source):
    print("Phanmbuster function called")
    print(files, source)
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    for file in files:
            print(file)
            df = pd.read_csv(file,encoding='ISO-8859-1')
            username = df['username']
            fullName = df['fullName']
            description = df['description']
            query = df['query']
            data = {
                "username": username,
                "fullName": fullName,
                "description": description,
                "query": query
            }
            #Growth.objects.bulk_create(data)
            dfx = pd.DataFrame(data)

            df2 = pd.concat([df2,dfx]).drop_duplicates(subset=['username'], keep='first')
            #df2 = pd.concat([df2,dfx])
        
    df3 = df2.replace(np.nan, 'a', regex=True)
    return df3

def source_profilebud(files, source):
    print("ProfileBud function called")
    #print(files, source)
    count = 0
    df = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    for file in files:
        file_name = str(file.name)
        result = ''.join([i for i in file_name if not i.isdigit()])
        modified_string = re.sub(r"\([^()]*\)", "", result)
        file_name = modified_string[:-4]
        print(file_name,df.count)
        df = pd.read_csv(file,encoding='ISO-8859-1')
        username = df['Username']
        data = {
            "profile_username": username
        }
        dfx = pd.DataFrame(data)
        dfx['hashtag'] = file_name

        df2 = pd.concat([df2,dfx]).drop_duplicates(subset=['profile_username'], keep='first')
    
    return df2
        

def source_influencer(files, source):
    print("Influencer function called")
    print(files, source)
    for file in files:
        df = pd.read_csv(file,encoding='ISO-8859-1')
        print(df)
