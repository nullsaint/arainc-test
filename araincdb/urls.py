from django.urls import path
from . import views

urlpatterns = [
    path('combine_csv/', views.combine_csv, name="combine_csv"),
    path('vlookup/',views.vlookup, name="vlookup"),
    path('optimize_language/', views.optimize_language, name="optimize_language"),
    path('language_segment_template', views.language_segment_template, name="language_segment_template"),
    path('growth_segment', views.growth_segment, name="growth_segment"),
    path('universal_combine', views.universal_combine, name="universal_combine"),

    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('', views.home, name="home"),
    path('dashboard/', views.home, name="dashboard"),
    path('hashtag_score/', views.hashtag_score, name="hashtag_score"),   
    path('scrape_posts/', views.scrape_posts, name='scrape_posts'), 
    path('scrape_username/', views.scrape_username, name='scrape_username'),
    path('push_usernames_to_tempgrowth/', views.push_usernames_to_tempgrowth, name='push_usernames_to_tempgrowth'),    
    path('scrape_listing_data/', views.scrape_listing_data, name='scrape_listing_data'),
    path('process_post_urls/', views.process_post_urls, name='process_post_urls'),
    path('posturl_scrapping_stats/', views.posturl_scrapping_stats, name="posturl_scrapping_stats"),

    path('growths/', views.growths, name="growths"),
    path('read_growth/<str:pk>/', views.read_growth, name="read_growth"),
    path('update_growth/<str:pk>/', views.update_growth, name="update_growth"),
    path('delete_growth/<str:pk>/', views.delete_growth, name="delete_growth"),
    path('upload_growth/', views.upload_growth, name='upload_growth'),
    path('growth_export/', views.growth_export, name='growth_export'),
    path('growtharchive_export/', views.growtharchive_export, name='growtharchive_export'),
    path('growthdedupe_import/', views.growthdedupe_import, name='growthdedupe_import'),
    path('process_growthdedupe/', views.process_growthdedupe, name='process_growthdedupe'),
        
    path('listingdedupe_import/', views.listingdedupe_import, name='listingdedupe_import'),
    path('process_listingdedupe/', views.process_listingdedupe, name='process_listingdedupe'),
    
    path('tempgrowth_import/', views.tempgrowth_import, name='tempgrowth_import'),
    path('push_to_listing/', views.push_to_listing, name="push_to_listing"),
    path('growth_stats/', views.growth_stats, name="growth_stats"),
    path('growth_user_stats/', views.growth_user_stats, name="growth_user_stats"),
    path('growtharchive_user_stats/', views.growtharchive_user_stats, name="growtharchive_user_stats"),

    path('templisting_import/', views.templisting_import, name='templisting_import'),
    path('location_import/', views.location_import, name='location_import'),
    path('temp_posturl_import/', views.temp_posturl_import, name='temp_posturl_import'),
    path('posturl_import/', views.posturl_import, name='posturl_import'),
    path('posturl_export/', views.posturl_export, name='posturl_export'),

    path('phase2_reviews/', views.phase2_reviews, name="phase2_reviews"),
    path ('phase2_review/', views.phase2_review, name="phase2_review"),
    path ('phase2_review_complete/<str:pk>/', views.phase2_review_complete, name="phase2_review_complete"),

    path('screenings/', views.screenings, name="screenings"),
    path('assign_client/<str:redirect_url>/', views.assign_client, name='assign_client'),
    path ('screening_review/', views.screening_review, name="screening_review"),
    path ('screening_review_complete/<str:pk>/', views.screening_review_complete, name="screening_review_complete"),

    path('growth_reveiws/', views.growth_reveiws, name="growth_reveiws"),
    path('assign_account/<str:redirect_url>/', views.assign_account, name='assign_account'),
    path ('growth_reveiw/', views.growth_review, name="growth_review"),
    path ('growth_review_complete/<str:pk>/', views.growth_review_complete, name="growth_review_complete"),
    
    path('cold_unfollowings/', views.cold_unfollowings, name="cold_unfollowings"),
    path('cold_unfollowing/', views.cold_unfollowing, name="cold_unfollowing"),
    path('cold_unfollowing_complete/<str:pk>/', views.cold_unfollowing_complete, name="cold_unfollowing_complete"),

    path('warm_unfollowings/', views.warm_unfollowings, name="warm_unfollowings"),
    path('warm_unfollowing/', views.warm_unfollowing, name="warm_unfollowing"),
    path('warm_unfollowing_complete/<str:pk>/', views.warm_unfollowing_complete, name="warm_unfollowing_complete"),

    path('user_stats/', views.user_stats, name="user_stats"),
    
    path('listings/', views.listings, name="listings"),
    path('read_listing/<str:pk>/', views.read_listing, name="read_listing"),
    path('update_listing/<str:pk>/', views.update_listing, name="update_listing"),
    path('delete_listing/<str:pk>/', views.delete_listing, name="delete_listing"),

    path('listing_user_stats/', views.listing_user_stats, name="listing_user_stats"),
    
    path('warm_screenings/', views.warm_screenings, name="warm_screenings"),
    path('warm_screening/', views.warm_screening, name="warm_screening"),
    path ('warm_screening_complete/<str:pk>/', views.warm_screening_complete, name="warm_screening_complete"),
    
    path('cs_crosscheck/', views.cs_crosscheck, name="cs_crosscheck"),
    path('cs_crosscheck_review/', views.cs_crosscheck_review, name="cs_crosscheck_review"),
    path('cs_crosscheck_complete/<str:pk>/', views.cs_crosscheck_complete, name="cs_crosscheck_complete"),
    
    path('cs_creates/', views.cs_creates, name="cs_creates"),
    path('cs_create/', views.cs_create, name="cs_create"),
    path('cs_create_complete/<str:pk>/', views.cs_create_complete, name="cs_create_complete"),
    
    path('cs_reviews/', views.cs_reviews, name="cs_reviews"),
    path('cs_review/', views.cs_review, name="cs_review"),
    path('cs_review_complete/<str:pk>/', views.cs_review_complete, name="cs_review_complete"),

    path('message_sendings/', views.message_sendings, name="message_sendings"),
    path('message_sending/', views.message_sending, name="message_sending"),
    path('message_sending_complete/<str:pk>/', views.message_sending_complete, name="message_sending_complete"),
    
    path('omses/', views.omses, name="omses"),
    path('oms/', views.oms, name="oms"),
    path('oms_complete/<str:pk>/', views.oms_complete, name="oms_complete"),
]