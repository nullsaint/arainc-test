from django.db.models import Count, Sum, Avg, FloatField, F, Case, When, IntegerField
from django.db import connection
from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, time
from calendar import monthrange
from django.http import HttpResponse,JsonResponse
from django.views import View
from django.views.generic.edit import FormView
from datetime import datetime
import zipfile
import io, csv
from shutil import make_archive
from wsgiref.util import FileWrapper
from . models import *
from . forms import *
from . decorators import *
from . filters import *
from . scrapper import *
from . procedures import *
import numpy as np
import re
# Create your views here.


def last_day_of_month(date_value):
    return date_value.replace(day = monthrange(date_value.year, date_value.month)[1])

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect.')

    context = {}
    return render(request, 'araincdb/login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    context = {}
    return render(request, 'araincdb/home.html', context)

@login_required(login_url='login')
def dashboard(request):
    given_date = datetime.today().date()
    start_date = given_date.replace(day=1)
    end_date = last_day_of_month(given_date)

    if 'oms' in request.POST:
        start_date = request.POST.get('start_date') #ms_date
        end_date = request.POST.get('end_date') #ms_date

        quality_statuses = Growth.objects.values(status=F('quality_status__quality_status')).annotate(number=Count('id'))
        growth_statuses = Growth.objects.values(status=F('growth_status__growth_status')).annotate(number=Count('id'))
        connection_statuses = Growth.objects.values(status=F('connection_status__connection_status')).annotate(number=Count('id'))
        
        listing_statuses = Listing.objects.values(account_code=F('assigned_account__account_code'), connection_statuses=F('connection_status__connection_status')).annotate(number=Count('id'))
        with connection.cursor() as cursor:        
            cursor.callproc('sp_oms_stats', [start_date, end_date])
            oms_statuses = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.callproc('sp_oms_percent', [start_date, end_date])
            oms_percents = cursor.fetchall()

        context = {'quality_statuses': quality_statuses, 'growth_statuses': growth_statuses, 'connection_statuses': connection_statuses,
                    'listing_statuses': listing_statuses, 'oms_statuses': oms_statuses, 'oms_percents': oms_percents}
        return render(request, 'araincdb/dashboard.html', context)

    quality_statuses = Growth.objects.values(status=F('quality_status__quality_status')).annotate(number=Count('id'))
    growth_statuses = Growth.objects.values(status=F('growth_status__growth_status')).annotate(number=Count('id'))
    connection_statuses = Growth.objects.values(client=F('client_name__client_name'), account=F('assigned_account__account_code'), status=F('connection_status__connection_status')).annotate(number=Count('id'))
    unassigned_screening = Growth.objects.filter(connection_status=11, screened_by__isnull=True).count()
    
    listing_statuses = Listing.objects.values(account_code=F('assigned_account__account_code'), connection_statuses=F('connection_status__connection_status')).annotate(number=Count('id'))
    with connection.cursor() as cursor:        
        cursor.callproc('sp_oms_stats', [start_date, end_date])
        oms_statuses = cursor.fetchall()
    with connection.cursor() as cursor:
        cursor.callproc('sp_oms_percent', [start_date, end_date])
        oms_percents = cursor.fetchall()

    context = {'quality_statuses': quality_statuses, 'growth_statuses': growth_statuses, 'connection_statuses': connection_statuses,
                'listing_statuses': listing_statuses, 'oms_statuses': oms_statuses, 'oms_percents': oms_percents, 'unassigned_screening': unassigned_screening}
    return render(request, 'araincdb/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def hashtag_score(request):
    given_date = datetime.today().date()
    start_date = given_date.replace(day=1)
    end_date = last_day_of_month(given_date)

    if request.method == 'POST':
        start_date = request.POST.get('start_date') #input_date
        end_date = request.POST.get('end_date') #input_date
        with connection.cursor() as cursor:
            cursor.callproc('sp_hashtag_score', [start_date, end_date])
            user_stats = cursor.fetchall()

        context = {'user_stats': user_stats}
        return render(request, 'araincdb/hashtag_score.html', context)
    with connection.cursor() as cursor:
        cursor.callproc('sp_hashtag_score', [start_date, end_date])
        user_stats = cursor.fetchall()

    context = {'user_stats': user_stats}
    return render(request, 'araincdb/hashtag_score.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def posturl_scrapping_stats(request):
    posturl_stats = Posturl.objects.values(client=F('client_name__client_name')).filter(is_scrapped=0).annotate(number=Count('id'))
    user_stats = Posturl.objects.values(user=F('scrapped_by__username'), client=F('client_name__client_name')).filter(is_scrapped=0, scrapped_by__isnull=False).annotate(number=Count('id'))
    context = {'posturl_stats': posturl_stats, 'user_stats': user_stats}
    return render(request, 'araincdb/stats/posturl_scrapping_stats.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def process_post_urls(request):
    heading = 'Process Post URLs'
    if request.method == 'POST':
        client = request.POST.get('client')
        locate_option = request.POST.get('locate_option')
        client_name = get_object_or_404(Client, id=client)

        if locate_option == 'locate':
            post_url_added = insert_unique_posturls(client)
            locate_posts(client)
            messages.success(request, str(post_url_added) + ' unique Post URLs were added and location segmentation were done for the URLs for ' + client_name.client_name + '.')
        else:            
            post_url_added = insert_unique_posturls(client)
            messages.success(request, str(post_url_added) + ' unique Post URLs were added for ' + client_name.client_name + '.') 
        return redirect('process_post_urls')
    clients = Client.objects.all()
    context = {'heading': heading, 'clients': clients}
    return render(request, 'araincdb/scrapper/process_post_urls.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def process_growthdedupe(request):
    heading = 'Process Growth Dedupe'
    if request.method == 'POST':
        client = request.POST.get('client')
        client_name = get_object_or_404(Client, id=client)
        deleted_usernames = dedupe_usernames(client)
        
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['profile_username', 'full_name', 'location', 'caption', 'hashtag'])
        
        growths = Growthunique.objects.all().values_list('profile_username', 'full_name', 'location', 'caption', 'hashtag').filter(client_name__id=client)
        for growth in growths:
            writer.writerow(growth)

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM araincdb_growthunique WHERE client_name_id=%s;", [client])
            unique_usernames = cursor.rowcount
        response['Content-Disposition'] = 'attachment; filename="Growthdedupe.csv"'
        return response        

        messages.success(request, str(unique_usernames) + ' Unique usernames were retained for ' + client_name.client_name + '.') 
        return redirect('process_growthdedupe')
    clients = Client.objects.all()
    context = {'heading': heading, 'clients': clients}
    return render(request, 'araincdb/scrapper/process_growthdedupe.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def process_listingdedupe(request):
    heading = 'Process Listing Dedupe'
    if request.method == 'POST':
        client = request.POST.get('client')
        client_name = get_object_or_404(Client, id=client)
        deleted_usernames = dedupe_listing_usernames(client)
        
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        # Write header row
        writer.writerow(['profile_username', 'full_name', 'location', 'caption', 'hashtag'])
        # Get data from database
        growths = Listingunique.objects.all().values_list('profile_username', 'full_name', 'location', 'caption', 'hashtag').filter(client_name__id=client)
        # Write data rows
        for growth in growths:
            writer.writerow(growth)
        # Delete data that were written in CSV
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM araincdb_listingunique WHERE client_name_id=%s;", [client])
            unique_usernames = cursor.rowcount
        response['Content-Disposition'] = 'attachment; filename="Listingdedupe.csv"'
        return response        

        messages.success(request, str(unique_usernames) + ' Unique usernames were retained for ' + client_name.client_name + '.') 
        return redirect('process_listingdedupe')
    clients = Client.objects.all()
    context = {'heading': heading, 'clients': clients}
    return render(request, 'araincdb/scrapper/process_growthdedupe.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def scrape_username(request):
    heading = 'Scrape Usernames'

    if request.method == 'POST':
        client = request.POST.get('client')
        user = request.user.id

        post_count = get_username(client, user)

        client_name = get_object_or_404(Client, id=client)

        messages.success(request, str(post_count) + ' usernames were scrapped for ' + client_name.client_name + '.')
        return redirect('scrape_username')
    clients = Client.objects.all()
    context = {'heading': heading, 'clients': clients}
    return render(request, 'araincdb/scrapper/scrape_username.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def push_usernames_to_tempgrowth(request):
    heading = 'PUSH USERNAMES TO TEMPGROWTH'
    if request.method == 'POST':
        client = request.POST.get('client')
        user = request.user.id

        usernames = push_usernames(client)

        client_name = get_object_or_404(Client, id=client)

        messages.success(request, str(usernames) + ' Usernames were inserted in Tempgrowth for ' + client_name.client_name + '.')
        return redirect('push_usernames_to_tempgrowth')
    clients = Client.objects.all()
    context = {'heading': heading, 'clients': clients}
    return render(request, 'araincdb/scrapper/push_usernames_to_tempgrowth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def scrape_posts(request):
    inserted_usernames = ''
    if request.method == 'POST':
        user = request.user.id
        client = request.POST.get('client')
        scrape_option = request.POST.get('scrape_option')

        if scrape_option == '1':
            inserted_usernames = insert_unique_usernames(client)
            scrapped_usernames = get_profile_data(client, user)
            growth_segmentation(client, user)
        elif scrape_option == '2':
            inserted_usernames = insert_unique_usernames(client)
            scrape_done_growth_segmentation(client)
        elif scrape_option == '3':
            inserted_usernames = insert_unique_usernames(client)
            dont_scrape_growth_segmentation(client, user)
        elif scrape_option == '4':
            inserted_usernames = insert_unique_usernames(client)
            dont_scrape_segment_language(client,request)
        else:
            inserted_usernames = insert_unique_usernames(client)
            print('done')
            

        client_name = get_object_or_404(Client, id=client)

        messages.success(request, str(inserted_usernames) + ' unique usernames were added for ' + client_name.client_name + '.')
        return redirect('scrape_posts')
    clients = Client.objects.all()
    context = {'clients': clients}    
    return render(request, 'araincdb/scrapper/scrape_posts.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def scrape_listing_data(request):
    if request.method == 'POST':
        user = request.user.id
        client = request.POST.get('client')
        scrape_option = request.POST.get('scrape_option')

        if scrape_option == '1': # Scrape and Segment
            follower_added = insert_unique_listing(client, 'follower')
            like_added = insert_unique_listing(client, 'like')
            get_listing_profile_data(client)
            listing_segmentation(client)            
        elif scrape_option == '2': # Don't Scrape but Segment
            follower_added = insert_unique_listing(client, 'follower')
            like_added = insert_unique_listing(client, 'like')
            scrape_done_listing_segmentation(client)
        else: # Don't Scrape and don't Segment. This will be auto match
            follower_added = insert_unique_listing(client, 'follower')
            like_added = insert_unique_listing(client, 'like')
            dont_scrape_listing_segmentation(client)            

        print(follower_added, like_added)

        messages.success(request, str(follower_added.get('follower')) + ' Follower and ' + str(like_added.get('like')) + ' Like usernames were added in Listing and Segmentation were done for the usernames.')
        return redirect('scrape_listing_data')

    clients = Client.objects.all()
    context = {'clients': clients}
    return render(request, 'araincdb/scrapper/scrape_listing_data.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def growths(request):
    growths = Growth.objects.all()[:20]

    if request.method == 'POST':
        profile_username = request.POST.get('profile_username')
        # growths = Growth.objects.filter(profile_username__icontains=profile_username)
        growths = Growth.objects.filter(profile_username=profile_username)
        context = {'growths': growths}
        return render(request, 'araincdb/growth/growths.html', context)

    context = {'growths': growths}
    return render(request, 'araincdb/growth/growths.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def read_growth(request, pk):
    growth = get_object_or_404(Growth, id=pk)
    heading = 'Growth Details'

    context = {'growth': growth, 'heading': heading}
    return render(request, 'araincdb/growth/growth_details.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def update_growth(request, pk):
    growth = get_object_or_404(Growth, id=pk)
    form = GrowthForm(instance=growth)
    heading = 'Update Growth'

    if request.method == 'POST':
        form = GrowthForm(request.POST, instance=growth)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.updated_by = request.user
            fs.updated_date = timezone.now()
            fs.save()

            growth = form.cleaned_data.get('profile_username')
            messages.success(request, 'Growth  was updated for ' + growth + '.')
            return redirect('growths')

    context = {'form': form, 'heading': heading}
    return render(request, 'araincdb/growth/growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def delete_growth(request, pk):
    growth = get_object_or_404(Growth, id=pk)
    item = growth.profile_username
    heading = 'Delete Growth'

    if request.method == 'POST':
        growth.delete()
        messages.success(request, 'Deleted Growth was ' + item + '.')
        return redirect('growths')

    context = {'growth': growth, 'heading': heading}
    return render(request, 'araincdb/growth/growth_delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def tempgrowth_import(request):
    heading = 'Upload Temp Growth'
    info = '''This importer will import the following fields: client_id, profile_username, profile_description, full_name, post_count, followers, followings,
                scraping_status, external_url, location, caption, publication_date, hashtag from a csv file.'''
    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['growth_file'].file, encoding='latin-1')
        growth = csv.DictReader(paramFile)
        list_of_dict = list(growth)
        objs = [
            Tempgrowth(
                client_name = Client.objects.get(id=row['client_id']),
                profile_username=row['profile_username'],
                profile_description=row['profile_description'],
                full_name=row['full_name'],
                post_count=row['post_count'],
                followers=row['followers'],
                followings=row['followings'],
                scraping_status=row['scraping_status'],
                external_url=row['external_url'],
                location=row['location'],
                caption=row['caption'],
                publication_date=row['publication_date'],
                hashtag=row['hashtag']
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        print(record_count)
        try:
            msg = Tempgrowth.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('tempgrowth_import')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e       
            print(error_message)
            messages.error(request, error_message, e)    
            return redirect('tempgrowth_import')
    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/growth/import_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def push_to_listing(request):
    assigned_account = ''
    connection_status = ''
    accounts = Account.objects.all()
    connection_statuses = ConnectionStatus.objects.all()
    with connection.cursor() as cursor:
        cursor.execute("""SELECT araincdb_growth.id, araincdb_growth.publication_date, araincdb_growth.profile_username, araincdb_account.account_code, araincdb_connectionstatus.connection_status 
                            FROM araincdb_growth LEFT JOIN araincdb_account ON araincdb_growth.assigned_account_id=araincdb_account.id LEFT JOIN araincdb_connectionstatus ON araincdb_growth.connection_status_id=araincdb_connectionstatus.id
                            WHERE connection_status_id=%s AND assigned_account_id=%s AND profile_username NOT IN ( SELECT profile_username FROM araincdb_listing)""", [connection_status, assigned_account])
        growths = cursor.fetchall()

    if 'search' in request.POST:
        assigned_account = int(request.POST.get('account')) #Assigned Account
        connection_status = int(request.POST.get('connection_status')) #Connection Status

        with connection.cursor() as cursor:
            cursor.execute("""SELECT araincdb_growth.id, araincdb_growth.publication_date, araincdb_growth.profile_username, araincdb_account.account_code, araincdb_connectionstatus.connection_status 
                            FROM araincdb_growth LEFT JOIN araincdb_account ON araincdb_growth.assigned_account_id=araincdb_account.id LEFT JOIN araincdb_connectionstatus ON araincdb_growth.connection_status_id=araincdb_connectionstatus.id
                            WHERE connection_status_id=%s AND assigned_account_id=%s AND profile_username NOT IN ( SELECT profile_username FROM araincdb_listing)""", [connection_status, assigned_account])
            growths = cursor.fetchall()
        context = {'growths': growths, 'accounts': accounts, 'connection_statuses': connection_statuses}
        return render(request, 'araincdb/growth/push_to_listing.html', context)

    if 'push_to_listing' in request.POST:
        assigned_account = request.POST.get('account') #Assigned Account
        connection_status = request.POST.get('connection_status') #Connection Status
        growth_number = request.POST.get('growth_number') #Number of Growth to push in Listing

        # Push Growth to Listing        
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO araincdb_listing (profile_username, client_name_id, assigned_account_id, connection_status_id, connection_type_id)
                            SELECT profile_username, 1, assigned_account_id, 10, 4 FROM araincdb_growth
                            WHERE connection_status_id=%s AND assigned_account_id=%s AND profile_username
                            NOT IN ( SELECT profile_username FROM araincdb_listing) ORDER BY id LIMIT %s""", [connection_status, assigned_account, int(growth_number)])
            growth_number = cursor.rowcount
        
        messages.success(request, str(growth_number) + ' Growth Successfully Done usernames were pushed to Listing.')
        return redirect('push_to_listing')

    context = {'growths': growths, 'accounts': accounts, 'connection_statuses': connection_statuses}
    return render(request, 'araincdb/growth/push_to_listing.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'screening'])
def growth_stats(request):
    given_date = datetime.today().date()
    start_date = given_date.replace(day=1)
    end_date = last_day_of_month(given_date)

    if request.method == 'POST':
        start_date = request.POST.get('start_date') #input_date
        end_date = request.POST.get('end_date') #input_date
        with connection.cursor() as cursor:
            cursor.callproc('sp_growth_stats', [start_date, end_date])
            user_stats = cursor.fetchall()

        context = {'user_stats': user_stats}
        return render(request, 'araincdb/growth_stats.html', context)
    with connection.cursor() as cursor:
        cursor.callproc('sp_growth_stats', [start_date, end_date])
        user_stats = cursor.fetchall()

    context = {'user_stats': user_stats}
    return render(request, 'araincdb/growth_stats.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'screening'])
def growth_user_stats(request):
    heading = 'Growth User Stats'
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    start_date = datetime.combine(today, time())
    end_date = datetime.combine(tomorrow, time())

    if request.method == 'POST':
        start_date = request.POST.get('start_date') #input_date
        end_date = request.POST.get('end_date') #input_date
        user_stats = sp_growth_user_stats(start_date, end_date)
        context = {'heading': heading, 'user_stats': user_stats}
        return render(request, 'araincdb/stats/growth_user_stats.html', context)

    user_stats = sp_growth_user_stats(start_date, end_date)
    context = {'heading': heading, 'user_stats': user_stats}
    return render(request, 'araincdb/stats/growth_user_stats.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'screening'])
def growtharchive_user_stats(request):
    heading = 'Growth Archive User Stats'
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    start_date = datetime.combine(today, time())
    end_date = datetime.combine(tomorrow, time())

    if request.method == 'POST':
        start_date = request.POST.get('start_date') #input_date
        end_date = request.POST.get('end_date') #input_date
        user_stats = sp_growtharchive_user_stats(start_date, end_date)
        context = {'heading': heading, 'user_stats': user_stats}
        return render(request, 'araincdb/stats/growth_user_stats.html', context)

    user_stats = sp_growtharchive_user_stats(start_date, end_date)
    context = {'heading': heading, 'user_stats': user_stats}
    return render(request, 'araincdb/stats/growth_user_stats.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def templisting_import(request):
    heading = 'Upload Temp Listing'
    info = 'This importer will import the following fields: client_id, profile_username, full_name, profile_description, photo_url_query, connection_type, scraping_status from a CSV file.'
    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['growth_file'].file, encoding='latin-1')
        growth = csv.DictReader(paramFile)
        list_of_dict = list(growth)
        objs = [
            Templisting(
                client_name = Client.objects.get(id=row['client_id']),
                profile_username = row['profile_username'],
                full_name = row['full_name'],
                profile_description = row['profile_description'],
                photo_url_query = row['photo_url_query'].rstrip("/"),
                connection_type = row['connection_type'],
                scraping_status = row['scraping_status'],
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        print(record_count)
        try:
            msg = Templisting.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('templisting_import')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e       
            print(error_message)
            messages.error(request, error_message, e)    
            return redirect('templisting_import')
    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/growth/import_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def phase2_reviews(request):
    given_date = datetime.today().date()
    start_date = given_date.replace(day=1)
    end_date = last_day_of_month(given_date)
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    start_date_today = datetime.combine(today, time())
    end_date_today = datetime.combine(tomorrow, time())

    client_id = request.user.employee.assigned_client.id

    form = AssignClientForm(instance=request.user)
    screenings = Growth.objects.values_list('id', 'profile_username').filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user)

    client_stats_today = Growth.objects.values(account=F('assigned_account__account_code')).filter(Q(client_name=request.user.employee.assigned_client), quality_status__lt=3,
                                                                                                screened_date__gte=start_date_today, screened_date__lt=end_date_today).annotate(number=Count('id'))

    client_stats_month = Growth.objects.values(account=F('assigned_account__account_code')).filter(Q(client_name=request.user.employee.assigned_client), quality_status__lt=3,
                                                                                                screened_date__gte=start_date, screened_date__lt=end_date).annotate(number=Count('id'))
                                                                                                
    if request.method == 'POST':
        Growth.objects.filter(screening_review_status='Assigned', screened_by=request.user).update(screened_by_id=None, screening_review_status=None, screening_start_time=None)        
        return redirect('phase2_reviews')

    context = {'form': form, 'screenings': screenings, 'client_stats_today': client_stats_today, 'client_stats_month': client_stats_month}
    return render(request, 'araincdb/growth/phase2_reviews.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def phase2_review(request):
    # Stop Reveiw
    if 'stop_review' in request.POST:
        Growth.objects.filter(screening_review_status='Assigned', screened_by=request.user).update(screened_by_id=None, screening_review_status=None, screening_start_time=None)        
        return redirect('phase2_reviews')
    # Complete Review
    screening = Growth.objects.values_list('id').filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).count()
    if (screening > 0):
        screening = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).first()
        profile_username = screening.profile_username
         
        form = ScreeningForm(request.user.employee.assigned_client, instance=screening)        
        heading = 'Phase 2 Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/phase2_review.html', context)
    elif (Growth.objects.values_list('id').filter(connection_status=24, client_name=request.user.employee.assigned_client, screening_review_status__isnull=True).count() > 0):
        screening = Growth.objects.filter(connection_status=24, client_name=request.user.employee.assigned_client, screening_review_status__isnull=True).first()
        screening.screening_review_status='Assigned'
        screening.screened_by=request.user
        screening.screening_start_time=timezone.now()
        screening.save()

        screening = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).first()
        profile_username = screening.profile_username
        
        form = ScreeningForm(request.user.employee.assigned_client, instance=screening)
        heading = 'Phase 2 Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/phase2_review.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def phase2_review_complete(request, pk):
    screening = get_object_or_404(Growth, id=pk)
    # if request.method == 'POST':
    if 'complete_review' in request.POST:
        # form = ScreeningForm(request.POST, instance=screening)
        form = ScreeningForm(request.user.employee.assigned_client, request.POST, instance=screening)
        if form.is_valid():
            quality_status = form.cleaned_data.get('quality_status')
            if (quality_status.id == 1):
                connection_status = 4
            elif (quality_status.id == 2):
                connection_status = 4
            else:
                connection_status = 23
                
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.screening_review_status='Complete'
            fs.connection_status = connection_status
            fs.screened_by = request.user
            fs.screened_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'Screening  was done for ' + screening + '.')
            return redirect('phase2_review')
    form = ScreeningForm(request.user.employee.assigned_client, instance=screening)
    heading = 'Phase 2 Review'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/growth/phase2_review.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def screenings(request):
    given_date = datetime.today().date()
    start_date = given_date.replace(day=1)
    end_date = last_day_of_month(given_date)
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    start_date_today = datetime.combine(today, time())
    end_date_today = datetime.combine(tomorrow, time())

    client_id = request.user.employee.assigned_client.id

    form = AssignClientForm(instance=request.user)
    screenings = Growth.objects.values_list('id', 'profile_username').filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user)

    client_stats_today = Growth.objects.values(account=F('assigned_account__account_code')).filter(Q(client_name=request.user.employee.assigned_client), quality_status__lt=3,
                                                                                                screened_date__gte=start_date_today, screened_date__lt=end_date_today).annotate(number=Count('id'))

    client_stats_month = Growth.objects.values(account=F('assigned_account__account_code')).filter(Q(client_name=request.user.employee.assigned_client), quality_status__lt=3,
                                                                                                screened_date__gte=start_date, screened_date__lt=end_date).annotate(number=Count('id'))
                                                                                                
    if request.method == 'POST':
        Growth.objects.filter(screening_review_status='Assigned', screened_by=request.user).update(screened_by_id=None, screening_review_status=None, screening_start_time=None)        
        return redirect('screenings')

    context = {'form': form, 'screenings': screenings, 'client_stats_today': client_stats_today, 'client_stats_month': client_stats_month}
    return render(request, 'araincdb/growth/screenings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def assign_client(request, redirect_url):
    employee = get_object_or_404(Employee, user=request.user)
    if request.method == 'POST':
        form = AssignClientForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
        return redirect (redirect_url)

    context = {}
    return render(request, 'araincdb/growth/screenings_growths.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def screening_review(request):
    # Stop Reveiw
    if 'stop_review' in request.POST:
        Growth.objects.filter(screening_review_status='Assigned', screened_by=request.user).update(screened_by_id=None, screening_review_status=None, screening_start_time=None)        
        return redirect('screenings')
    # Complete Review
    screening = Growth.objects.values_list('id').filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).count()
    if (screening > 0):
        screening = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).first()
        profile_username = screening.profile_username
        # photos = get_profile_feed(profile_username)
        # photos = ''
        # form = ScreeningForm(instance=screening)        
        form = ScreeningForm(request.user.employee.assigned_client, instance=screening)        
        heading = 'Cold Screening Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/screening.html', context)
    elif (Growth.objects.values_list('id').filter(connection_status__lte=3, client_name=request.user.employee.assigned_client, screening_review_status__isnull=True).count() > 0):
        screening = Growth.objects.filter(connection_status__lte=3, client_name=request.user.employee.assigned_client, screening_review_status__isnull=True).order_by('connection_status').first()
        screening.screening_review_status='Assigned'
        screening.screened_by=request.user
        screening.screening_start_time=timezone.now()
        screening.save()

        screening = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).first()
        profile_username = screening.profile_username
        # photos = get_profile_feed(profile_username)
        # photos = ''
        # form = ScreeningForm(instance=screening)
        form = ScreeningForm(request.user.employee.assigned_client, instance=screening)
        heading = 'Cold Screening Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/screening.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def screening_review_complete(request, pk):
    screening = get_object_or_404(Growth, id=pk)
    # if request.method == 'POST':
    if 'complete_review' in request.POST:
        # form = ScreeningForm(request.POST, instance=screening)
        form = ScreeningForm(request.user.employee.assigned_client, request.POST, instance=screening)
        if form.is_valid():
            quality_status = form.cleaned_data.get('quality_status')
            if (quality_status.id == 1):
                connection_status = 4
            elif (quality_status.id == 2):
                connection_status = 4
            else:
                connection_status = 9
                
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.screening_review_status='Complete'
            fs.connection_status = connection_status
            fs.screened_by = request.user
            fs.screened_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            # delete_profile_feed(screening) # delete media feed for the profile
            messages.success(request, 'Screening  was done for ' + screening + '.')
            return redirect('screening_review')
    # form = ScreeningForm(instance=screening)
    form = ScreeningForm(request.user.employee.assigned_client, instance=screening)
    heading = 'Screening Review'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/growth/screening.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def growth_reveiws(request):
    given_date = datetime.today().date()
    start_date = given_date.replace(day=1)
    end_date = last_day_of_month(given_date)
    client_id = request.user.employee.assigned_client.id

    form = AssignAccountForm(instance=request.user)
    assigned_growths = Growth.objects.values_list('id', 'profile_username').filter(Q(client_name=request.user.employee.assigned_client),
                                                                                growth_review_status='Assigned', growthed_by=request.user)
    
    client_stats = Growth.objects.values(account=F('assigned_account__account_code')).filter(Q(client_name=request.user.employee.assigned_client), quality_status__lt=3,
                                                                                                screened_date__gte=start_date, screened_date__lt=end_date).annotate(number=Count('id'))
                                                                                                
    with connection.cursor() as cursor:
        cursor.execute("""SELECT araincdb_account.account_code, rtg.ready_to_growth, gd.growth_done, rj.rejected FROM araincdb_account
                        LEFT JOIN (SELECT araincdb_growth.assigned_account_id, COUNT(araincdb_growth.id) AS ready_to_growth FROM araincdb_account 
                                    LEFT JOIN araincdb_growth ON araincdb_account.id=araincdb_growth.assigned_account_id AND araincdb_growth.connection_status_id=4 
                                    GROUP BY araincdb_account.id) rtg
                        ON araincdb_account.id=rtg.assigned_account_id
                        LEFT JOIN (SELECT araincdb_growth.assigned_account_id, COUNT(araincdb_growth.id) AS growth_done FROM araincdb_account
                                    LEFT JOIN araincdb_growth ON araincdb_account.id=araincdb_growth.assigned_account_id AND araincdb_growth.connection_status_id=6 AND
                                    DATE(growthed_date) BETWEEN %s AND %s GROUP BY araincdb_account.id) gd
                        ON araincdb_account.id=gd.assigned_account_id
                        LEFT JOIN (SELECT araincdb_growth.assigned_account_id, COUNT(araincdb_growth.id) AS rejected FROM araincdb_account
                                    LEFT JOIN araincdb_growth ON araincdb_account.id=araincdb_growth.assigned_account_id AND araincdb_growth.connection_status_id=7 AND
                                    DATE(growthed_date) BETWEEN %s AND %s GROUP BY araincdb_account.id) rj
                        ON araincdb_account.id=rj.assigned_account_id
                        WHERE araincdb_account.client_name_id=%s;""", [start_date, end_date, start_date, end_date, client_id])
        client_growth_stats_month = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""SELECT araincdb_account.account_code, rtg.ready_to_growth, gd.growth_done, rj.rejected FROM araincdb_account
                        LEFT JOIN (SELECT araincdb_growth.assigned_account_id, COUNT(araincdb_growth.id) AS ready_to_growth FROM araincdb_account 
                                    LEFT JOIN araincdb_growth ON araincdb_account.id=araincdb_growth.assigned_account_id AND araincdb_growth.connection_status_id=4 
                                    GROUP BY araincdb_account.id) rtg
                        ON araincdb_account.id=rtg.assigned_account_id
                        LEFT JOIN (SELECT araincdb_growth.assigned_account_id, COUNT(araincdb_growth.id) AS growth_done FROM araincdb_account
                                    LEFT JOIN araincdb_growth ON araincdb_account.id=araincdb_growth.assigned_account_id AND araincdb_growth.connection_status_id=6 AND
                                    DATE(growthed_date) = %s GROUP BY araincdb_account.id) gd
                        ON araincdb_account.id=gd.assigned_account_id
                        LEFT JOIN (SELECT araincdb_growth.assigned_account_id, COUNT(araincdb_growth.id) AS rejected FROM araincdb_account
                                    LEFT JOIN araincdb_growth ON araincdb_account.id=araincdb_growth.assigned_account_id AND araincdb_growth.connection_status_id=7 AND
                                    DATE(growthed_date) = %s GROUP BY araincdb_account.id) rj
                        ON araincdb_account.id=rj.assigned_account_id
                        WHERE araincdb_account.client_name_id=%s;""", [given_date, given_date, client_id])
        client_growth_stats_today = cursor.fetchall()
    

    context = {'form': form, 'assigned_growths': assigned_growths, 'client_stats': client_stats, 'client_growth_stats_month': client_growth_stats_month, 'client_growth_stats_today': client_growth_stats_today}
    return render(request, 'araincdb/growth/screenings_growths.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening', 'dm_team'])
def assign_account(request, redirect_url):
    employee = get_object_or_404(Employee, user=request.user)
    if request.method == 'POST':
        form = AssignAccountForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
        return redirect (redirect_url)

    context = {}
    return render(request, 'araincdb/growth/screenings_growths.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def growth_review(request):
    # Stop Reveiw
    if 'stop_review' in request.POST:
        Growth.objects.filter(growth_review_status='Assigned', growthed_by=request.user).update(growthed_by=None, growth_review_status=None, growth_start_time=None)        
        return redirect('growth_reveiws')
    growth = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), growth_review_status='Assigned', growthed_by=request.user).count()
    # print (growth)
    if (growth > 0):
        growth = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), growth_review_status='Assigned', growthed_by=request.user).order_by('-assigned_account').first()
        form = ScreeningGrowthForm(instance=growth)
        heading = 'Growth Review'
        context = {'growth': growth, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/screening_growth.html', context)
    elif (Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), Q(assigned_account = request.user.employee.assigned_account) | Q(assigned_account__isnull=True), Q(connection_status=4), growth_review_status__isnull=True).count() > 0):
        growth = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client),
                                        Q(assigned_account = request.user.employee.assigned_account) | Q(assigned_account__isnull=True),
                                        Q(connection_status=4), growth_review_status__isnull=True).order_by('-assigned_account').first()
        # print(growth)
        growth.growth_review_status='Assigned'
        growth.growthed_by=request.user
        growth.growth_start_time=timezone.now()
        growth.save()

        growth = Growth.objects.filter(Q(client_name=request.user.employee.assigned_client), growth_review_status='Assigned', growthed_by=request.user).order_by('-assigned_account').first()
        form = ScreeningGrowthForm(instance=growth)
        heading = 'Growth Review'
        context = {'growth': growth, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/screening_growth.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def growth_review_complete(request, pk):
    growth = get_object_or_404(Growth, id=pk)
    if request.method == 'POST':
        form = ScreeningGrowthForm(request.POST, instance=growth)
        if form.is_valid():
            growth_status = form.cleaned_data.get('growth_status')
            # print(growth_status.id)
            if(growth_status.id == 1):
                connection_status = 6
            else:
                connection_status = 7
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.assigned_account = request.user.employee.assigned_account
            fs.growth_review_status='Complete'
            fs.connection_status = connection_status
            fs.growthed_by = request.user
            fs.growthed_date = timezone.now()
            fs.save()

            growth = fs.profile_username
            # print(growth)
            messages.success(request, 'Growth  was done for ' + growth + '.')
            return redirect('growth_review')
    form = ScreeningGrowthForm(instance=growth)
    heading = 'Growth Review'
    context = {'growth': growth, 'form': form, 'heading': heading}
    return render(request, 'araincdb/growth/screening_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def cold_unfollowings(request):
    form = AssignAccountForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/growth/cold_unfollowings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def cold_unfollowing(request):
    with connection.cursor() as cursor:
        cursor.execute('''SELECT id FROM araincdb_growth WHERE unfollowing_status IS NULL AND (connection_status_id=6) AND assigned_account_id=%s
         AND profile_username NOT IN ( SELECT profile_username FROM araincdb_listing)
         order by growthed_date DESC LIMIT 1''', [request.user.employee.assigned_account.id])
        row = cursor.fetchone()
        row_count = cursor.rowcount

    cs = Growth.objects.filter(unfollowing_status='Assigned', unfollowing_by=request.user).count()
    print (cs)
    if (cs > 0):
        cs = Growth.objects.filter(unfollowing_status='Assigned', unfollowing_by=request.user).first()
        form = UnfollowingForm(instance=cs)
        heading = 'Cold Unfollowing'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/cold_unfollowing.html', context)
    elif (row_count > 0):
        cs = get_object_or_404(Growth, id=int(row[0]))
        cs.unfollowing_status='Assigned'
        cs.unfollowing_by=request.user
        cs.unfollowing_start_time=timezone.now()
        cs.save()

        cs = Growth.objects.filter(unfollowing_status='Assigned', unfollowing_by=request.user).first()
        form = UnfollowingForm(instance=cs)
        heading = 'Cold Unfollowing'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/cold_unfollowing.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def cold_unfollowing_complete(request, pk):
    screening = get_object_or_404(Growth, id=pk)
    if request.method == 'POST':
        form = UnfollowingForm(request.POST, instance=screening)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.unfollowing_status='Complete'
            fs.unfollowing_by = request.user
            fs.unfollowing_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'Unfollowing was done for ' + screening + '.')
            return redirect('cold_unfollowing')
    form = MSForm(instance=screening)
    heading = 'Cold Unfollowing'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/growth/cold_unfollowing.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def warm_unfollowings(request):
    form = AssignAccountForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/growth/warm_unfollowings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def warm_unfollowing(request):
    with connection.cursor() as cursor:
        cursor.execute('''SELECT id FROM araincdb_growth WHERE unfollowing_status IS NULL AND (connection_status_id=6) AND assigned_account_id=%s
         AND profile_username IN ( SELECT profile_username FROM araincdb_listing WHERE connection_type_id=3)
         order by growthed_date ASC, connection_status_id ASC LIMIT 1''', [request.user.employee.assigned_account.id])
        row = cursor.fetchone()
        row_count = cursor.rowcount
    print("Returned is "+ str(row))

    cs = Growth.objects.filter(unfollowing_status='Assigned', unfollowing_by=request.user).count()
    print (cs)
    if (cs > 0):
        cs = Growth.objects.filter(unfollowing_status='Assigned', unfollowing_by=request.user).first()
        form = UnfollowingForm(instance=cs)
        heading = 'Warm Unfollowing'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/warm_unfollowing.html', context)
    elif (row_count > 0):
        cs = get_object_or_404(Growth, id=int(row[0]))
        cs.unfollowing_status='Assigned'
        cs.unfollowing_by=request.user
        cs.unfollowing_start_time=timezone.now()
        cs.save()

        cs = Growth.objects.filter(unfollowing_status='Assigned', unfollowing_by=request.user).first()
        form = UnfollowingForm(instance=cs)
        heading = 'Warm Unfollowing'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/growth/warm_unfollowing.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def warm_unfollowing_complete(request, pk):
    screening = get_object_or_404(Growth, id=pk)
    if request.method == 'POST':
        form = UnfollowingForm(request.POST, instance=screening)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.unfollowing_status='Complete'
            fs.unfollowing_by = request.user
            fs.unfollowing_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'Unfollowing was done for ' + screening + '.')
            return redirect('warm_unfollowing')
    form = MSForm(instance=screening)
    heading = 'Warm Unfollowing'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/growth/warm_unfollowing.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'screening'])
def user_stats(request):
    given_date = datetime.today().date()
    start_date = given_date.replace(day=1)
    end_date = last_day_of_month(given_date)

    if request.method == 'POST':
        start_date = request.POST.get('start_date') #input_date
        end_date = request.POST.get('end_date') #input_date
        with connection.cursor() as cursor:
            cursor.callproc('sp_user_stats', [start_date, end_date])
            user_stats = cursor.fetchall()

        context = {'user_stats': user_stats}
        return render(request, 'araincdb/user_stats.html', context)
    with connection.cursor() as cursor:
        cursor.callproc('sp_user_stats', [start_date, end_date])
        user_stats = cursor.fetchall()

    context = {'user_stats': user_stats}
    return render(request, 'araincdb/user_stats.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def listing_user_stats(request):
    heading = 'Listing User Stats'
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    start_date = datetime.combine(today, time())
    end_date = datetime.combine(tomorrow, time())

    if request.method == 'POST':
        start_date = request.POST.get('start_date') #input_date
        end_date = request.POST.get('end_date') #input_date
        user_stats = sp_listing_stats(start_date, end_date)

        context = {'heading': heading, 'user_stats': user_stats}
        return render(request, 'araincdb/stats/listing_user_stats.html', context)
    
    user_stats = sp_listing_stats(start_date, end_date)
    context = {'heading': heading, 'user_stats': user_stats}
    return render(request, 'araincdb/stats/listing_user_stats.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def listings(request):
    listings = Listing.objects.all()[:20]

    if request.method == 'POST':
        profile_username = request.POST.get('profile_username')
        # listings = Listing.objects.filter(profile_username__icontains=profile_username)
        listings = Listing.objects.filter(profile_username=profile_username)
        context = {'listings': listings}
        return render(request, 'araincdb/listing/listings.html', context)

    context = {'listings': listings}
    return render(request, 'araincdb/listing/listings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def read_listing(request, pk):
    listing = get_object_or_404(Listing, id=pk)
    heading = 'Listing Details'

    context = {'listing': listing, 'heading': heading}
    return render(request, 'araincdb/listing/listing_details.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def update_listing(request, pk):
    listing = get_object_or_404(Listing, id=pk)
    form = ListingForm(instance=listing)
    heading = 'Update Listing'

    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.updated_by = request.user
            fs.updated_date = timezone.now()
            fs.save()

            listing = form.cleaned_data.get('profile_username')
            messages.success(request, 'Listing  was updated for ' + listing + '.')
            return redirect('listings')

    context = {'listing': listing, 'form': form, 'heading': heading}
    return render(request, 'araincdb/listing/listing.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, id=pk)
    item = listing.profile_username
    heading = 'Delete Listing'

    if request.method == 'POST':
        listing.delete()
        messages.warning(request, 'Deleted Listing was ' + item + '.')
        return redirect('listings')

    context = {'listing': listing, 'heading': heading}
    return render(request, 'araincdb/listing/listing_delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def warm_screenings(request):
    form = AssignClientForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/listing/warm_screenings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def warm_screening(request):
    screening = Listing.objects.filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).count()
    print (screening)
    if (screening > 0):
        screening = Listing.objects.filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).first()
        # insta_data = get_insta_profile(screening.profile_username)
        form = WarmScreeningForm(instance=screening)     
        heading = 'Warm Screening Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/screening.html', context)
    elif (Listing.objects.filter(Q(connection_status=1) | Q(connection_status=2) | Q(connection_status=3), Q(client_name=request.user.employee.assigned_client), screening_review_status__isnull=True).count() > 0):
        screening = Listing.objects.filter(Q(connection_status=1) | Q(connection_status=2) | Q(connection_status=3), Q(client_name=request.user.employee.assigned_client), screening_review_status__isnull=True).order_by('connection_status').first()
        print(screening)
        screening.screening_review_status='Assigned'
        screening.screened_by=request.user
        screening.screening_start_time=timezone.now()
        screening.save()

        screening = Listing.objects.filter(Q(client_name=request.user.employee.assigned_client), screening_review_status='Assigned', screened_by=request.user).first()
        # insta_data = get_insta_profile(screening.profile_username)
        form = WarmScreeningForm(instance=screening)
        heading = 'Warm Screening Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/screening.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def warm_screening_complete(request, pk):
    screening = get_object_or_404(Listing, id=pk)
    if request.method == 'POST':
        form = WarmScreeningForm(request.POST, instance=screening)
        if form.is_valid():
            quality_status = form.cleaned_data.get('quality_status')
            if (quality_status.id == 1):
                connection_status = 10
            elif (quality_status.id == 2):
                connection_status = 10
            else:
                connection_status = 12
                
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.screening_review_status='Complete'
            fs.connection_status = connection_status
            fs.screened_by = request.user
            fs.screened_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'Screening  was done for ' + screening + '.')
            return redirect('warm_screening')
    form = WarmScreeningForm(instance=screening)
    heading = 'Warm Screening Review'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/listing/screening.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def cs_crosscheck(request):
    form = AssignAccountForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/listing/cs_crosschecks.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def cs_crosscheck_review(request):
    screening = Listing.objects.filter(cs_crosscheck_status='Assigned', cs_crosscheck_by=request.user).count()
    print (screening)
    if (screening > 0):
        screening = Listing.objects.filter(cs_crosscheck_status='Assigned', cs_crosscheck_by=request.user).first()
        form = CSCrosscheckForm(instance=screening)     
        heading = 'CS Cross-check Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/cs_crosscheck.html', context)
    elif (Listing.objects.filter(Q(connection_status=10), Q(assigned_account=request.user.employee.assigned_account), cs_crosscheck_status__isnull=True).count() > 0):
        screening = Listing.objects.filter(Q(connection_status=10), Q(assigned_account=request.user.employee.assigned_account), cs_crosscheck_status__isnull=True).first()
        print(screening)
        screening.cs_crosscheck_status='Assigned'
        screening.cs_crosscheck_by=request.user
        screening.cs_crosscheck_start_time=timezone.now()
        screening.save()

        screening = Listing.objects.filter(cs_crosscheck_status='Assigned', cs_crosscheck_by=request.user).first()
        form = CSCrosscheckForm(instance=screening)
        heading = 'CS Cross-check Review'
        context = {'screening': screening, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/cs_crosscheck.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def cs_crosscheck_complete(request, pk):
    screening = get_object_or_404(Listing, id=pk)
    if request.method == 'POST':
        form = CSCrosscheckForm(request.POST, instance=screening)
        if form.is_valid():
            quality_status = form.cleaned_data.get('quality_status')
            if (quality_status.id == 1):
                connection_status = 13
            elif (quality_status.id == 2):
                connection_status = 13
            else:
                connection_status = 14
                
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.cs_crosscheck_status='Complete'
            fs.connection_status = connection_status
            fs.cs_crosscheck_by = request.user
            fs.cs_crosscheck_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'CS Cross-check was done for ' + screening + '.')
            return redirect('cs_crosscheck_review')
    form = CSCrosscheckForm(instance=screening)
    heading = 'CS Cross-check Review'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/listing/cs_crosscheck.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'screening', 'dm_team'])
def cs_creates(request):
    form = AssignAccountForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/listing/cs_creates.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'dm_team'])
def cs_create(request):
    cs = Listing.objects.filter(cs_create_status='Assigned', cs_va=request.user).count()
    print (cs)
    if (cs > 0):
        cs = Listing.objects.filter(cs_create_status='Assigned', cs_va=request.user).first()
        # insta_data = get_insta_profile(cs.profile_username)
        form = CSCreateForm(instance=cs)
        heading = 'CS Create'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/cs_create.html', context)
    elif (Listing.objects.filter(Q(connection_status=13), Q(assigned_account=request.user.employee.assigned_account), cs_create_status__isnull=True).count() > 0):
        cs = Listing.objects.filter(Q(connection_status=13), Q(assigned_account=request.user.employee.assigned_account), cs_create_status__isnull=True).first()
        print(cs)
        cs.cs_create_status='Assigned'
        cs.cs_va=request.user
        cs.cs_start_time = timezone.now()
        cs.save()

        cs = Listing.objects.filter(cs_create_status='Assigned', cs_va=request.user).first()
        # insta_data = get_insta_profile(cs.profile_username)
        form = CSCreateForm(instance=cs)
        heading = 'CS Create'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/cs_create.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'dm_team'])
def cs_create_complete(request, pk):
    screening = get_object_or_404(Listing, id=pk)
    if request.method == 'POST':
        form = CSCreateForm(request.POST, instance=screening)
        if form.is_valid():
            quality_status = form.cleaned_data.get('quality_status')
            if (quality_status.id == 1):
                connection_status = 15
            elif (quality_status.id == 2):
                connection_status = 15
            else:
                connection_status = 16
                
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.cs_create_status='Complete'
            fs.connection_status = connection_status
            fs.cs_va = request.user
            fs.cs_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'CS was created for ' + screening + '.')
            return redirect('cs_create')
    form = CSCreateForm(instance=screening)
    heading = 'CS Create'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/listing/cs_create.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'screening', 'dm_team'])
def cs_reviews(request):
    form = AssignAccountForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/listing/cs_reviews.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'dm_team'])
def cs_review(request):
    cs = Listing.objects.filter(Q(connection_status=15), Q(assigned_account=request.user.employee.assigned_account), cs_review_status='Assigned', cs_reviewer=request.user).count()
    print (cs)
    if (cs > 0):
        cs = Listing.objects.filter(Q(connection_status=15), Q(assigned_account=request.user.employee.assigned_account), cs_review_status='Assigned', cs_reviewer=request.user).first()
        # insta_data = get_insta_profile(cs.profile_username)
        form = CSReviewForm(instance=cs)
        heading = 'CS Review'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/cs_review.html', context)
    elif (Listing.objects.filter(Q(connection_status=15), Q(assigned_account=request.user.employee.assigned_account), cs_review_status__isnull=True).count() > 0):
        cs = Listing.objects.filter(Q(connection_status=15), Q(assigned_account=request.user.employee.assigned_account), cs_review_status__isnull=True).first()
        cs.cs_review_status='Assigned'
        cs.cs_reviewer=request.user
        cs.cs_review_start_time=timezone.now()
        cs.save()

        cs = Listing.objects.filter(Q(connection_status=15), Q(assigned_account=request.user.employee.assigned_account), cs_review_status='Assigned', cs_reviewer=request.user).first()
        # insta_data = get_insta_profile(cs.profile_username)
        form = CSReviewForm(instance=cs)
        heading = 'CS Review'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/cs_review.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead', 'dm_team'])
def cs_review_complete(request, pk):
    screening = get_object_or_404(Listing, id=pk)
    if request.method == 'POST':
        form = CSReviewForm(request.POST, instance=screening)
        if form.is_valid():
            quality_status = form.cleaned_data.get('quality_status')
            if (quality_status.id == 1):
                connection_status = 17
            elif (quality_status.id == 2):
                connection_status = 17
            else:
                connection_status = 18
                
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.cs_review_status='Complete'
            fs.connection_status = connection_status
            fs.cs_reviewer = request.user
            fs.cs_review_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'CS was reviewed for ' + screening + '.')
            return redirect('cs_review')
    form = CSReviewForm(instance=screening)
    heading = 'CS Review'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/listing/cs_review.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead', 'screening'])
def message_sendings(request):
    form = AssignAccountForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/listing/message_sendings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def message_sending(request):
    cs = Listing.objects.filter(Q(connection_status=17), Q(assigned_account=request.user.employee.assigned_account), ms_status='Assigned', ms_by=request.user).count()
    print (cs)
    if (cs > 0):
        cs = Listing.objects.filter(Q(connection_status=17), Q(assigned_account=request.user.employee.assigned_account), ms_status='Assigned', ms_by=request.user).first()
        form = MSForm(instance=cs)
        heading = 'Message Sending'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/message_sending.html', context)
    elif (Listing.objects.filter(Q(connection_status=17), Q(assigned_account=request.user.employee.assigned_account), ms_status__isnull=True).count() > 0):
        cs = Listing.objects.filter(Q(connection_status=17), Q(assigned_account=request.user.employee.assigned_account), ms_status__isnull=True).first()
        cs.ms_status='Assigned'
        cs.ms_by=request.user
        cs.ms_start_time=timezone.now()
        cs.save()

        cs = Listing.objects.filter(Q(connection_status=17), Q(assigned_account=request.user.employee.assigned_account),ms_status='Assigned', ms_by=request.user).first()
        form = MSForm(instance=cs)
        heading = 'Message Sending'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/message_sending.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def message_sending_complete(request, pk):
    screening = get_object_or_404(Listing, id=pk)
    if request.method == 'POST':
        form = MSForm(request.POST, instance=screening)
        if form.is_valid():
            quality_status = form.cleaned_data.get('quality_status')
            if (quality_status.id == 1):
                connection_status = 19
            elif (quality_status.id == 2):
                connection_status = 19
            else:
                connection_status = 20
                
            connection_status = ConnectionStatus.objects.get(id=connection_status)

            fs = form.save(commit=False)
            fs.ms_status='Complete'
            fs.connection_status = connection_status
            fs.ms_by = request.user
            fs.ms_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'MS was done for ' + screening + '.')
            return redirect('message_sending')
    form = MSForm(instance=screening)
    heading = 'Message Sending'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/listing/message_sending.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def omses(request):
    form = AssignAccountForm(instance=request.user)

    context = {'form': form}
    return render(request, 'araincdb/listing/omses.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def oms(request):
    cs = Listing.objects.filter(Q(connection_status=19), Q(assigned_account=request.user.employee.assigned_account), oms_status='Assigned', oms_by=request.user).count()
    print (cs)
    if (cs > 0):
        cs = Listing.objects.filter(Q(connection_status=19), Q(assigned_account=request.user.employee.assigned_account), oms_status='Assigned', oms_by=request.user).first()
        form = OMSForm(instance=cs)
        heading = 'Openning Message Status'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/oms.html', context)
    elif (Listing.objects.filter(Q(connection_status=19), Q(assigned_account=request.user.employee.assigned_account), oms_status__isnull=True).count() > 0):
        cs = Listing.objects.filter(Q(connection_status=19), Q(assigned_account=request.user.employee.assigned_account), oms_status__isnull=True).order_by('ms_date').first()
        cs.oms_status='Assigned'
        cs.oms_by=request.user
        cs.oms_start_time=timezone.now()
        cs.save()

        cs = Listing.objects.filter(Q(connection_status=19), Q(assigned_account=request.user.employee.assigned_account), oms_status='Assigned', oms_by=request.user).first()
        form = OMSForm(instance=cs)
        heading = 'Openning Message Status'
        context = {'cs': cs, 'form': form, 'heading': heading}
        return render(request, 'araincdb/listing/oms.html', context)
    else:
        return redirect('home')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'device_only', 'igteamlead'])
def oms_complete(request, pk):
    screening = get_object_or_404(Listing, id=pk)
    if request.method == 'POST':
        form = OMSForm(request.POST, instance=screening)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.oms_status='Complete'
            fs.oms_by = request.user
            fs.oms_date = timezone.now()
            fs.save()

            screening = fs.profile_username
            messages.success(request, 'OMS was done for ' + screening + '.')
            return redirect('oms')
    form = MSForm(instance=screening)
    heading = 'Openning Message Status'
    context = {'screening': screening, 'form': form, 'heading': heading}
    return render(request, 'araincdb/listing/oms.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def location_import(request):
    heading = 'Upload Location'
    info = 'This importer will import the following fields: country_id, location from a csv file.'

    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['growth_file'].file)
        growth = csv.DictReader(paramFile)
        list_of_dict = list(growth)
        objs = [
            Location(
                country = Country.objects.get(id=row['country_id']),
                location=row['location']
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        print(record_count)
        try:
            msg = Location.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('location_import')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e       
            print(error_message)
            messages.error(request, error_message, e)    
            return redirect('location_import')
    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/growth/import_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def temp_posturl_import(request):
    heading = 'Upload Temp Post URL'
    info = 'This importer will import the following fields: client_id, post_url, description, caption, publication_date, hashtag from a csv file.'

    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['growth_file'].file, encoding='latin-1')
        growth = csv.DictReader(paramFile)
        list_of_dict = list(growth)
        objs = [
            TempPosturl(
                client_name = Client.objects.get(id=row['client_id']),
                post_url=row['post_url'],
                description=row['description'],
                caption=row['caption'],
                publication_date=row['publication_date'],
                hashtag=row['hashtag']
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        print(record_count)
        try:
            msg = TempPosturl.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('temp_posturl_import')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e       
            print(error_message)
            messages.error(request, error_message, e)    
            return redirect('temp_posturl_import')
    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/growth/import_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def posturl_import(request):
    heading = 'Upload Post URL'
    info = 'This importer will import the following fields: client_id, post_url, description, caption from a csv file.'

    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['growth_file'].file, encoding='latin-1')
        growth = csv.DictReader(paramFile)
        list_of_dict = list(growth)
        objs = [
            Posturl(
                client_name = Client.objects.get(id=row['client_id']),
                post_url=row['post_url'],
                description=row['description'],
                caption=row['caption']
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        print(record_count)
        try:
            msg = Posturl.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('posturl_import')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e       
            print(error_message)
            messages.error(request, error_message, e)    
            return redirect('posturl_import')
    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/growth/import_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def posturl_export(request):
    heading = 'Export Post URLs'

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['post_url', 'location', 'caption', 'description', 'input_date'])
        
        post_urls = get_posturls(start_time, end_time)
        for post_url in post_urls:
            writer.writerow(post_url)

        response['Content-Disposition'] = 'attachment; filename="Post_URL.csv"'
        return response

    context = {'heading': heading}
    return render(request, 'araincdb/scrapper/export_post_urls.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def growth_export(request):
    heading = 'Export Growth'
    clients = Client.objects.all()
    accounts = Account.objects.all()
    connection_statuses = ConnectionStatus.objects.all()

    if request.method == 'POST':
        client = request.POST.get('client')
        client = get_object_or_404(Client, id=client)
        # account = request.POST.get('account')
        # account = get_object_or_404(Account, id=account)
        connection_status = request.POST.get('connection_status')
        connection_status = get_object_or_404(ConnectionStatus, id=connection_status)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['id', 'profile_username','full_name', 'profile_description', 'post_count', 'followers', 'followings', 'hashtag', 'location', 'external_url', 'quality_status', 'assigned_account', 'connection_status', 'screened_by', 'remarks'])
        
        # growths = Growth.objects.all().values_list('id', 'profile_username', 'quality_status', 'assigned_account', 'connection_status', 'screening_review_status', 'screened_by').filter(
        #     client_name__client_name=client, assigned_account__account_code__icontains=account, connection_status__connection_status=connection_status, input_date__gte=start_time, input_date__lte=end_time)
        growths = Growth.objects.all().values_list('id', 'profile_username','full_name', 'profile_description', 'post_count', 'followers', 'followings', 'hashtag', 'location', 'external_url', 'quality_status', 'assigned_account', 'connection_status', 'screened_by', 'remarks').filter(
            client_name__client_name=client, connection_status__connection_status=connection_status, input_date__gte=start_time, input_date__lte=end_time)
        for growth in growths:
            writer.writerow(growth)

        response['Content-Disposition'] = 'attachment; filename="Growth.csv"'
        return response
        # print(growths)
    context = {'heading': heading, 'clients': clients, 'accounts': accounts, 'connection_statuses': connection_statuses}
    return render(request, 'araincdb/scrapper/growth_export.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def growtharchive_export(request):
    heading = 'Export Growth Archive'
    clients = Client.objects.all()
    accounts = Account.objects.all()
    connection_statuses = ConnectionStatus.objects.all()

    if request.method == 'POST':
        client = request.POST.get('client')
        client = get_object_or_404(Client, id=client)
        # account = request.POST.get('account')
        # account = get_object_or_404(Account, id=account)
        connection_status = request.POST.get('connection_status')
        connection_status = get_object_or_404(ConnectionStatus, id=connection_status)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['id', 'profile_username','full_name', 'profile_description', 'post_count', 'followers', 'followings', 'hashtag', 'location', 'external_url', 'quality_status', 'assigned_account', 'connection_status', 'screened_by', 'remarks'])
        
        # growths = GrowthArchive.objects.all().values_list('id', 'profile_username', 'quality_status', 'assigned_account', 'connection_status', 'screening_review_status', 'screened_by').filter(
        #     client_name__client_name=client, assigned_account__account_code__icontains=account, connection_status__connection_status=connection_status, input_date__gte=start_time, input_date__lte=end_time)
        growths = GrowthArchive.objects.all().values_list('id', 'profile_username','full_name', 'profile_description', 'post_count', 'followers', 'followings', 'hashtag', 'location', 'external_url', 'quality_status', 'assigned_account', 'connection_status', 'screened_by', 'remarks').filter(
            client_name__client_name=client, connection_status__connection_status=connection_status, input_date__gte=start_time, input_date__lte=end_time)
        for growth in growths:
            writer.writerow(growth)

        response['Content-Disposition'] = 'attachment; filename="Growth Archive.csv"'
        return response
        # print(growths)
    context = {'heading': heading, 'clients': clients, 'accounts': accounts, 'connection_statuses': connection_statuses}
    return render(request, 'araincdb/scrapper/growth_export.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def upload_growth(request):
    heading = 'Upload Old Growth'
    info = '''This importer will import the following fields: client_name, profile_username, scraping_status, external_url,
     profile_description, full_name, caption, post_count, followers, followings, publication_date, hashtag, input_date, quality_status,
     location, assigned_account, growth_review_status, screening_review_status, unfollowing_status, growth_status, connection_status, remarks,
     scrapped_by, scrapped_date, screened_by, screening_start_time, screened_date, growthed_by, growth_start_time, growthed_date, unfollowing_by,
     unfollowing_start_time, unfollowing_date, updated_by, updated_date from a csv file.'''

    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['growth_file'].file, encoding='latin-1')
        growth = csv.DictReader(paramFile)
        list_of_dict = list(growth)
        objs = [
            Growth(
                client_name=Client.objects.get(id=row['client_name']),
                profile_username=row['profile_username'],
                scraping_status=row['scraping_status'],
                external_url=row['external_url'],
                profile_description=row['profile_description'],
                full_name=row['full_name'],
                caption=row['caption'],
                post_count=row['post_count'],
                followers=row['followers'],
                followings=row['followings'],
                publication_date=row['publication_date'],
                hashtag=row['hashtag'],
                input_date=row['input_date'],
                quality_status=QualityStatus.objects.get(id=row['quality_status']),
                location=row['location'],
                assigned_account=Account.objects.get(id=row['assigned_account']),
                growth_review_status=row['growth_review_status'],
                screening_review_status=row['screening_review_status'],
                unfollowing_status=row['unfollowing_status'],
                growth_status=GrowthStatus.objects.get(id=row['growth_status']),
                connection_status=ConnectionStatus.objects.get(id=row['connection_status']),
                remarks=row['remarks'],
                scrapped_by=User.objects.get(id=row['scrapped_by']),
                scrapped_date=row['scrapped_date'],
                screened_by=User.objects.get(id=row['screened_by']),
                screening_start_time=row['screening_start_time'],
                screened_date=row['screened_date'],
                growthed_by=User.objects.get(id=row['growthed_by']),
                growth_start_time=row['growth_start_time'],
                growthed_date=row['growthed_date'],
                unfollowing_by=User.objects.get(id=row['unfollowing_by']),
                unfollowing_start_time=row['unfollowing_start_time'],
                unfollowing_date=row['unfollowing_date'],
                updated_by=User.objects.get(id=row['updated_by']),
                updated_date=row['updated_date']
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        try:
            msg = Growth.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('upload_growth')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e
            messages.error(request, error_message, e)    
            return redirect('upload_growth')

    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/growth/import_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def growthdedupe_import(request):
    heading = 'Upload Usernames to Dedupe for Growth'
    info = 'This importer will import the following fields: client_id, profile_username, full_name, location, caption, hashtag from a csv file.'

    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['growth_file'].file, encoding='latin-1')
        growth = csv.DictReader(paramFile)
        list_of_dict = list(growth)
        objs = [
            Growthdedupe(
                client_name=Client.objects.get(id=row['client_id']),
                profile_username=row['profile_username'],
                full_name=row['full_name'],
                location=row['location'],
                caption=row['caption'],
                hashtag=row['hashtag'],
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        try:
            msg = Growthdedupe.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('growthdedupe_import')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e
            messages.error(request, error_message, e)    
            return redirect('growthdedupe_import')
    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/growth/import_growth.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def listingdedupe_import(request):
    heading = 'Upload Usernames to Dedupe for Listing'
    info = 'This importer will import the following fields: client_id, profile_username, full_name, location, caption, hashtag from a csv file.'

    if request.method == 'POST':
        paramFile = io.TextIOWrapper(request.FILES['listing_file'].file, encoding='latin-1')
        listing = csv.DictReader(paramFile)
        list_of_dict = list(listing)
        objs = [
            Listingdedupe(
                client_name=Client.objects.get(id=row['client_id']),
                profile_username=row['profile_username'],
                full_name=row['full_name'],
                location=row['location'],
                caption=row['caption'],
                hashtag=row['hashtag'],
         )
         for row in list_of_dict
        ]
        record_count = len(list_of_dict)
        try:
            msg = Listingdedupe.objects.bulk_create(objs)
            messages.success(request, str(record_count) + ' records were uploaded.')
            return redirect('listingdedupe_import')
        except Exception as e:
            error_message = 'Error While Importing Data: ',e
            messages.error(request, error_message, e)    
            return redirect('listingdedupe_import')
    context = {'heading': heading, 'info': info}
    return render(request, 'araincdb/listing/import_listing.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def export_growth(request):
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['client_name', 'profile_username', 'profile_description', 'full_name', 'is_private'])

    for growth in Growth.objects.all().values_list('client_name', 'profile_username', 'profile_description', 'full_name', 'is_private'):
        writer.writerow(growth)
    
    response['Content-Disposition'] = 'attachment; filename="growth.csv"'
    return response


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'igteamlead'])
def export_listing(request):

    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['assigned_account', 'profile_username', 'connection_type', 'engagement_content', 'connection_status'])

    for listing in Listing.objects.all().values_list('assigned_account', 'profile_username', 'connection_type', 'engagement_content', 'connection_status'):
        writer.writerow(listing)
    
    response['Content-Disposition'] = 'attachment; filename="listing.csv"'
    return response
@login_required(login_url='login')
def combine_csv(request):
    #response = HttpResponse(content_type='text/csv')

    if request.method == "POST":
        files = request.FILES.getlist('file_field')
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
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=combined_unique.csv'
        df3.to_csv(response,index=False)
        return response

            
    #response['Content-Disposition'] = 'attachment; filename="df2.csv"'
    #return response
    context = {}
    return render(request, 'araincdb/scrapper/combine_csv.html', context)

@login_required(login_url='login')
def vlookup(request):
    print('Vlookup Starts...')
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    username = ''
    if request.method == "POST":
        files = request.FILES.getlist('file_field')
       
        #print(files)
        for file in files:

            if file.name == "1.csv":
                df1 = pd.read_csv(file,encoding='ISO-8859-1')
                print('found')
            elif file.name == '2.csv':
                df2 = pd.read_csv(file,encoding='ISO-8859-1')
            else:
                print("not FOund")


        inner_join = pd.merge(df1,df2,on='username',how='right')
        df = inner_join.drop(['full_name', 'location', 'caption', 'hashtag'],axis=1)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Ready For Language.csv'
        df.to_csv(response,index=False)
        return response


    context = {}
    return render(request, 'araincdb/scrapper/vlookup.html', context)

@login_required(login_url='login')
def optimize_language(request):
    desc = []
    def count_ratio(stra):
        en_ratio = 0
        or_ratio = 0
        for i in stra:
            if ord(i) >= 65 and ord(i) <= 122:
                en_ratio += 1
            else:
                or_ratio += 1
        #en_ratio = (en_ratio * 100) / 100
        #or_ratio = (or_ratio * 100) / 100
        return en_ratio,or_ratio


    print("optmize")
    hashtag_lists = hashtag_list.objects.all()
    df = pd.DataFrame()
    df2 = pd.DataFrame()
    if request.method == 'POST':
        files = request.FILES.getlist('file_field')
        for file in files:
            df2 = pd.read_csv(file,encoding='ISO-8859-1')
    
        for i in df2['description']:
            for j in hashtag_lists:
                #print(j.hashtag)
                i = i.replace(j.hashtag, '')
            desc.append(i)

        df2['optimized description'] = desc
        df = df2.replace(np.nan, 'a', regex=True)

        rows = df['optimized description']
        count = 0
        language = []
        word_count = []
        for row in rows:
            temp_df = []
            for i in row:
                #if ord(i) >= 65 and ord(i) <= 122 or ord(i) == 32:
                temp_df.append(i)
                str = ""
                for j in temp_df:
                    str += j
            try:
                x,y = count_ratio(str)
                count+=1
                print(count)
                data=[]
                res = detect_langs(str)
                language.append(detect_langs(str))
                word_count.append([x,y])
            except LangDetectException:
                language.append('Unindentified')
                word_count.append([0,0])
                ##
                continue
        df['language'] = language
        df['word_count'] = word_count
        #df.to_csv('ignore.csv', index = False)
        #df = pd.read_csv('ignore.csv',encoding='ISO-8859-1')

        print(df)
        lists = []
        for row in df['description']:
                temp_df = []
                for i in row:
                    if ord(i) >= 65 and ord(i) <= 122 or ord(i) == 32:
                        temp_df.append(i)
                        stra = ""
                        for j in temp_df:
                            stra += j
                lists.append(stra)

        df['description'] = lists

        lists2 = []

        for row in df['fullName']:
                temp_df = []
                for i in row:
                    if ord(i) >= 65 and ord(i) <= 122 or ord(i) == 32:
                        temp_df.append(i)
                        stra = ""
                        for j in temp_df:
                            stra += j
                lists2.append(stra)

        df['fullName'] = lists2

        data = []
        for i in df['description']:
            data.append(i[:998])

        df['description'] = data
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Result.csv'
        df.to_csv(response,index=False)
        return response


    context = {}
    return render(request,'araincdb/scrapper/optimize_language.html', context)

@login_required(login_url='login')
def language_segment_template(request):
    df = pd.DataFrame()
    df2 = pd.DataFrame()
    language_analysis = []

    
    if request.method == "POST":
        files = request.FILES.getlist('file_field')
        for file in files:
            df = pd.read_csv(file,encoding='ISO-8859-1')
        for i in df['language']:
            if i == 'Unindentified':
                language_analysis.append('Unidentified')
            else:
                x = str(i[1:-1])
                #print(x)
                if x.find('en')>=0:
                    language_analysis.append('Accepted')
                elif x.find('es') >=0:
                    language_analysis.append('Bad Language')
                elif x.find('fr') >=0:
                    language_analysis.append('Bad Language')
                elif x.find('ca') >=0:
                    language_analysis.append('Bad Language')
                else:
                    language_analysis.append('Bad Language')

        df['language_analysis'] = language_analysis
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename=Output.csv'
        # df.to_csv(response,index=False)
        # return response

        client_id = []
        profile_username = []
        profile_description = []
        full_name = []
        post_count = []
        followers = []
        followings = []
        scraping_status = []
        external_url = []
        location = []
        caption = []
        publication_date = []
        hashtag = []

        idy = []
        client_namey = []
        profile_usernamey = []
        publication_datey = []
        hashtagy = []
        connection_statusy = []


        for index, row in df.iterrows():
            y = str(row['language_analysis'])
            #print(y)
            if y == 'Accepted':
                client_id.append('1')
                profile_username.append(row['username'])
                profile_description.append(row['description'])
                full_name.append(row['fullName'])
                post_count.append('0')
                followers.append('0')
                followings.append('0')
                scraping_status.append('done')
                publication_date.append(datetime.today().strftime('%Y-%m-%d'))
                hashtag.append(row['query'])
            else:
                client_namey.append('1')
                profile_usernamey.append(row['username'])
                publication_datey.append(datetime.today().strftime('%Y-%m-%d'))
                connection_statusy.append('34')

        
        data = {
                    'client_id':client_id,
                    'profile_username':profile_username,
                    'profile_description':profile_description,
                    'full_name': full_name,
                    'post_count': post_count,
                    'followers': followers,
                    'followings': followings,
                    'scraping_status': scraping_status,
                    'external_url': external_url,
                    'location': location,
                    'caption': caption,
                    'publication_date': publication_date,
                    'hashtag': hashtag
                }
        datay = {
                'id':idy,
                'client_name': client_namey,
                'profile_username': profile_usernamey,
                'publication_date': publication_datey,
                'hashtag': hashtagy,
                'connection_status': connection_statusy

            }

        dirspot = os.getcwd()
        print(dirspot)
        dfx = pd.DataFrame.from_dict(data,orient='index')
        dfx = dfx.transpose()
        dfy = pd.DataFrame.from_dict(datay,orient='index')
        dfy = dfy.transpose()
        # dfx = pd.DataFrame.from_dict(data, columns=[ 'client_id','profile_username','profile_description', 'full_name','post_count','followers',
        #         'followings','scraping_status','external_url','location','caption','publication_date','hashtag'])
        # dfy = pd.DataFrame.from_dict(datay,columns=['id','profile_username','publication_date','hashtag','connection_status'])
        path= 'E:/arainc-test/csv/'
        with zipfile.ZipFile(path+'my_csvs.zip', 'w') as csv_zip:
            csv_zip.writestr("Accepted.csv", dfx.to_csv(index=False))
            csv_zip.writestr("Bad Language.csv", dfy.to_csv(index=False))
        file_name = 'CSV'
        files_path = "E:/arainc-test/csv/"
        path_to_zip = make_archive(files_path, "zip", files_path)
        response = HttpResponse(FileWrapper(open(path_to_zip,'rb')), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{filename}.zip"'.format(
            filename = file_name.replace(" ", "_")
            )
        return response




        # response = HttpResponse(content_type='application/x-zip-compressed')
        # response['Content-Disposition'] = 'attachment; filename=my_csvs.zip'
        # #dfy.to_csv(response,index=False)
        # return response

    context = {}
    return render(request,'araincdb/scrapper/language_segment_template.html', context)

@login_required(login_url='login')
def growth_segment(request):
    print("Growth Segment On The Fly")
    df = pd.DataFrame()
    client = 1

    if request.method == "POST":
        files = request.FILES.getlist('file_field')
        for file in files:
            df = pd.read_csv(file,encoding='ISO-8859-1')
    
        df = df.replace(np.nan, 'a', regex=True)


        lists = []
        for row in df['profile_description']:
                temp_df = []
                for i in row:
                    if ord(i) >= 65 and ord(i) <= 122 or ord(i) == 32:
                        temp_df.append(i)
                        stra = ""
                        for j in temp_df:
                            stra += j
                lists.append(stra)

        df['profile_description'] = lists

        lists2 = []

        for row in df['full_name']:
                temp_df = []
                for i in row:
                    if ord(i) >= 65 and ord(i) <= 122 or ord(i) == 32:
                        temp_df.append(i)
                        stra = ""
                        for j in temp_df:
                            stra += j
                lists2.append(stra)

        df['full_name'] = lists2

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
        df['segment'] = ''
        print(df)
        for index, row in df.iterrows():
            y = str(row['profile_description'])
            x = y.lower()
            for i in possible_auto_match:
                # if x.find(i) >= 0:
                #     #print('Found ' + i + ' for ' + str(y) + ' : Adding as possible_auto_match.')
                #     row['segment']= '2'
                # else:
                #     continue
                reg_ex = re.compile(fr"{i}", re.IGNORECASE)
                if reg_ex.findall(x):
                    row['segment'] = '2'
                else:
                    continue

        
        for index, row in df.iterrows():
            y = str(row['profile_description'])
            x = y.lower()
            for i in auto_match:
                # if x.find(i) >= 0:
                #     #print('Found ' + i + ' for ' + str(y) + ' : Adding as possible_auto_match.')
                #     row['segment']='1'
                # else:
                #     continue
                reg_ex = re.compile(fr"{i}", re.IGNORECASE)
                if reg_ex.findall(x):
                    row['segment'] = '1'
                else:
                    continue
        
        for index, row in df.iterrows():
            y = str(row['full_name'])
            x = y.lower()
            for i in auto_match:
                # if x.find(i) >= 0:
                #     #print('Found ' + i + ' for ' + str(y) + ' : Adding as possible_auto_match.')
                #     row['segment']='1'
                # else:
                #     continue
                reg_ex = re.compile(fr"{i}", re.IGNORECASE)
                if reg_ex.findall(x):
                    row['segment'] = '1'
                else:
                    continue
                    
        for index, row in df.iterrows():
            y = str(row['full_name'])
            x = y.lower()
            for i in phase_2:
                # if x.find(i) >= 0:
                #     #print('Found ' + i + ' for ' + str(y) + ' : Adding as possible_auto_match.')
                #     row['segment']='24'
                # else:
                #     continue
                reg_ex = re.compile(fr"{i}", re.IGNORECASE)
                if reg_ex.findall(x):
                    row['segment'] = '24'
                else:
                    continue
        
        for index, row in df.iterrows():
            y = str(row['profile_username'])
            x = y.lower()
            for i in phase_2:
                # if x.find(i) >= 0:
                #     #print('Found ' + i + ' for ' + str(y) + ' : Adding as possible_auto_match.')
                #     row['segment']='24'
                # else:
                #     continue
                reg_ex = re.compile(fr"{i}", re.IGNORECASE)
                if reg_ex.findall(x):
                    row['segment'] = '24'
                else:
                    continue
        
        for index, row in df.iterrows():
            y = str(row['profile_description'])
            x = y.lower()
            for i in auto_no_match:
                # if x.find(i) >= 0:
                #     #print('Found ' + i + ' for ' + str(y) + ' : Adding as possible_auto_match.')
                #     row['segment']='11'
                # else:
                #     continue   
                reg_ex = re.compile(fr"{i}", re.IGNORECASE)
                if reg_ex.findall(x):
                    row['segment'] = '11'
                else:
                    continue
        
        for index, row in df.iterrows():
            y = str(row['full_name'])
            x = y.lower()
            for i in auto_no_match:
                # if x.find(i) >= 0:
                #     #print('Found ' + i + ' for ' + str(y) + ' : Adding as possible_auto_match.')
                #     row['segment']='11'
                # else:
                #     continue
                reg_ex = re.compile(fr"{i}", re.IGNORECASE)
                if reg_ex.findall(x):
                    row['segment'] = '11'
                else:
                    continue

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Segmented.csv'
        df.to_csv(response,index=False)
        return response

        
    context = {}
    return render(request,'araincdb/scrapper/growth_segment.html', context)

@login_required(login_url='login')
def universal_combine(request):
    #response = HttpResponse(content_type='text/csv')

    if request.method == "POST":
        files = request.FILES.getlist('file_field')
        source = request.POST.get('source')
        print(source)
        if source == '1':
            data = source_phantombuster(files, source)
            print(data)
            print(type(data))
            
        elif source == '2':
            data = source_profilebud(files, source)
            #print(data)
            data['client_id'] = '1'
            data['full_name'] = ''
            data['location'] = ''
            data['caption'] = ''
            column_name = ["client_id", "profile_username","full_name","location","caption","hashtag"]
            data = data.reindex(columns=column_name)
        elif source == '3':
            data = source_influencer(files, source)
        else:
            print('done')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=combined_unique.csv'
        data.to_csv(response,index=False)
        return response

    context = {}
    return render(request, 'araincdb/scrapper/universal_combine.html', context)
