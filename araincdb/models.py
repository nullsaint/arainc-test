from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

#Create your models here.
class MultipleFileUplaoder(models.Model):
    profile_username = models.CharField('Username', max_length=200)
    profile_description = models.CharField('Profile Description', max_length=20000, null=True, blank=True)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Multiple File Uploader'
        verbose_name_plural = 'Multiple Files Uploader'

    def __str__(self):
        return self.profile_username

class hashtag_list(models.Model):
    hashtag = models.CharField('Hashtag', max_length=200)

    class Meta:
        verbose_name = 'Hashtag List'
        verbose_name_plural = 'Hashtags List'

    def __str__(self):
        return self.hashtag

class ConnectionStatus(models.Model):
    connection_status = models.CharField('Connection Status', max_length=200)

    class Meta:
        verbose_name = 'Connection Status'
        verbose_name_plural = 'Connection Statuses'

    def __str__(self):
        return self.connection_status

class ConnectionType(models.Model):
    connection_type = models.CharField('Connection Type', max_length=200)

    class Meta:
        verbose_name = 'Connection Type'
        verbose_name_plural = 'Connection Types'

    def __str__(self):
        return self.connection_type


class ErrorType(models.Model):
    error_type = models.CharField('Error Type', max_length=200)

    class Meta:
        verbose_name = 'Error Type'
        verbose_name_plural = 'Error Types'

    def __str__(self):
        return self.error_type


class GrowthStatus(models.Model):
    growth_status = models.CharField('Growth Status', max_length=200)

    class Meta:
        verbose_name = 'Growth Status'
        verbose_name_plural = 'Growth Statuses'

    def __str__(self):
        return self.growth_status


class Country(models.Model):
    country = models.CharField('Country', max_length=200)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.country


class Location(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Country', null=True, blank=True)
    location = models.CharField('Location', max_length=200)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.location


class MessageSendingStatus(models.Model):
    mss = models.CharField('Message Status', max_length=200)

    class Meta:
        verbose_name = 'Message Sending Status'
        verbose_name_plural = 'Message Sending Statuses'

    def __str__(self):
        return self.mss

class OMS(models.Model):
    oms = models.CharField('Message Status', max_length=200)

    class Meta:
        verbose_name = 'OMS'
        verbose_name_plural = 'OMSES'

    def __str__(self):
        return self.oms


class QualityStatus(models.Model):
    quality_status = models.CharField('Quality Status', max_length=200)

    class Meta:
        verbose_name = 'Quality Status'
        verbose_name_plural = 'Quality Statuses'

    def __str__(self):
        return self.quality_status


class QcFeedback(models.Model):
    qc_feedback = models.CharField('QC Feedback', max_length=200)

    class Meta:
        verbose_name = 'QC Feedback'
        verbose_name_plural = 'QC Feedbacks'

    def __str__(self):
        return self.qc_feedback

class WarmScript(models.Model):
    url = models.CharField('URL', max_length=200)
    message = models.CharField('Message', max_length=1000)

    class Meta:
        verbose_name = 'Warm Script'
        verbose_name_plural = 'Warm Scripts'

    def __str__(self):
        return self.message


class Client(models.Model):
    client_name = models.CharField('Client Name', max_length=200)
    client_code = models.CharField('Client Code', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.client_name


class Account(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name', null=True, blank=True)
    account_name = models.CharField('Account Name', max_length=200)
    username = models.CharField('Account Username', unique=True, max_length=200, null=True, blank=True)
    account_code = models.CharField('Account Code', max_length=200)

    class Meta:
        verbose_name = 'Assigned Account'
        verbose_name_plural = 'Assigned Accounts'

    def __str__(self):
        return self.account_code


class GrowthArchive(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    scraping_status = models.CharField('Scraping Status', max_length=200)
    external_url = models.CharField('External URL', max_length=1000, null=True, blank=True)
    profile_description = models.CharField('Profile Description', max_length=1000, null=True, blank=True)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)
    post_count = models.IntegerField('Post Count', null=True, blank=True)
    followers = models.IntegerField('Followers', null=True, blank=True)
    followings = models.IntegerField('Followings', null=True, blank=True)
    publication_date = models.DateField('Publication Date', null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    input_date = models.DateTimeField('Input Date', default=timezone.now, null=True, blank=True)
    quality_status = models.ForeignKey(QualityStatus, on_delete=models.CASCADE, null=True, blank=False, verbose_name='Quality Status')
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    assigned_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+', verbose_name='Assigned Account', null=True, blank=True)
    growth_review_status = models.CharField('Growth Review Status', max_length=200, null=True, blank=True)
    screening_review_status = models.CharField('Screening Review Status', max_length=200, null=True, blank=True)
    unfollowing_status = models.CharField('Unfollowing Status', max_length=200, null=True, blank=True)
    growth_status = models.ForeignKey(GrowthStatus, on_delete=models.CASCADE, verbose_name='Growth Status', null=True, blank=False)
    connection_status = models.ForeignKey(ConnectionStatus, on_delete=models.CASCADE, verbose_name='Connection Status', null=True, blank=True)
    remarks = models.CharField('Remarks', max_length=1000, null=True, blank=True)
    screened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Screening VA'
    )
    screening_start_time = models.DateTimeField('Screening Start Time', auto_now_add=False, null=True, blank=True)
    screened_date = models.DateTimeField('Screening End Date', auto_now_add=False, null=True, blank=True)
    growthed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Growth VA'
    )
    growth_start_time = models.DateTimeField('Growth Start Time', auto_now_add=False, null=True, blank=True)
    growthed_date = models.DateTimeField('Growth End Time', auto_now_add=False, null=True, blank=True)
    unfollowing_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Unfolloiwng VA'
    )
    unfollowing_start_time = models.DateTimeField('Unfollowing Start Time', auto_now_add=False, null=True, blank=True)
    unfollowing_date = models.DateTimeField('Unfollowing End Time', auto_now_add=False, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Updated By'
    )
    updated_date = models.DateTimeField('Growth Date', auto_now_add=False, null=True, blank=True)

    class Meta:
        verbose_name = 'Growth Archive'
        verbose_name_plural = 'Growth Archive'

    def __str__(self):
        return self.profile_username


class Growthdedupe(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = 'Growthdedupe'
        verbose_name_plural = 'Growthdedupe'

    def __str__(self):
        return self.profile_username


class Growthunique(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = 'Growthunique'
        verbose_name_plural = 'Growthunique'

    def __str__(self):
        return self.profile_username


class Growth(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    scraping_status = models.CharField('Scraping Status', max_length=200)
    external_url = models.CharField('External URL', max_length=1000, null=True, blank=True)
    profile_description = models.CharField('Profile Description', max_length=1000, null=True, blank=True)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)
    post_count = models.IntegerField('Post Count', null=True, blank=True)
    followers = models.IntegerField('Followers', null=True, blank=True)
    followings = models.IntegerField('Followings', null=True, blank=True)
    publication_date = models.DateField('Publication Date', null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    input_date = models.DateTimeField('Input Date', default=timezone.now, null=True, blank=True)
    quality_status = models.ForeignKey(QualityStatus, on_delete=models.CASCADE, null=True, blank=False, verbose_name='Quality Status')
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    assigned_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+', verbose_name='Assigned Account', null=True, blank=True)
    growth_review_status = models.CharField('Growth Review Status', max_length=200, null=True, blank=True)
    screening_review_status = models.CharField('Screening Review Status', max_length=200, null=True, blank=True)
    unfollowing_status = models.CharField('Unfollowing Status', max_length=200, null=True, blank=True)
    growth_status = models.ForeignKey(GrowthStatus, on_delete=models.CASCADE, verbose_name='Growth Status', null=True, blank=True)
    connection_status = models.ForeignKey(ConnectionStatus, on_delete=models.CASCADE, verbose_name='Connection Status', null=True, blank=True)
    remarks = models.CharField('Remarks', max_length=1000, null=True, blank=True)
    scrapped_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Scrapped By'
    )
    scrapped_date = models.DateTimeField('Scrapped Date', auto_now_add=False, null=True, blank=True)
    screened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Screening VA'
    )
    screening_start_time = models.DateTimeField('Screening Start Time', auto_now_add=False, null=True, blank=True)
    screened_date = models.DateTimeField('Screening End Date', auto_now_add=False, null=True, blank=True)
    growthed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Growth VA'
    )
    growth_start_time = models.DateTimeField('Growth Start Time', auto_now_add=False, null=True, blank=True)
    growthed_date = models.DateTimeField('Growth End Time', auto_now_add=False, null=True, blank=True)
    unfollowing_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Unfolloiwng VA'
    )
    unfollowing_start_time = models.DateTimeField('Unfollowing Start Time', auto_now_add=False, null=True, blank=True)
    unfollowing_date = models.DateTimeField('Unfollowing End Time', auto_now_add=False, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Updated By'
    )
    updated_date = models.DateTimeField('Growth Date', auto_now_add=False, null=True, blank=True)
    language_score = models.CharField('Language Score', max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = 'Growth'
        verbose_name_plural = 'Growths'

    def __str__(self):
        return self.profile_username


class Tempgrowth(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, default=1, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    profile_description = models.CharField('Profile Description', max_length=1000, null=True, blank=True)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    post_count = models.IntegerField('Post Count', null=True, blank=True)
    followers = models.IntegerField('Followers', null=True, blank=True)
    followings = models.IntegerField('Followings', null=True, blank=True)
    scraping_status = models.CharField('Scraping Status', max_length=200)
    external_url = models.CharField('External URL', max_length=1000, null=True, blank=True)
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)
    publication_date = models.DateField('Publication Date', null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Temp Growth'
        verbose_name_plural = 'Temp Growths'

    def __str__(self):
        return self.profile_username


class Templisting(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, default=1, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    profile_description = models.CharField('Profile Description', max_length=1000, null=True, blank=True)
    photo_url_query = models.CharField('Photo URL/ Query', max_length=1000)
    connection_type = models.CharField('Connection Type', max_length=200, null=True, blank=True)
    scraping_status = models.CharField('Scraping Status', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Temp Listing'
        verbose_name_plural = 'Temp Listings'

    def __str__(self):
        return self.profile_username


class Listingdedupe(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = 'Listingdedupe'
        verbose_name_plural = 'Listingdedupe'

    def __str__(self):
        return self.profile_username


class Listingunique(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = 'Listingunique'
        verbose_name_plural = 'Listingunique'

    def __str__(self):
        return self.profile_username


class Listing(models.Model):
    profile_username = models.CharField('Username', max_length=200)
    scraping_status = models.CharField('Scraping Status', max_length=200, null=True, blank=True)
    connection_type = models.ForeignKey(ConnectionType, on_delete=models.CASCADE, verbose_name='Connection Type', null=True, blank=True)
    assigned_account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Assigned Account', null=True)
    photo_url_query = models.CharField('Photo URL/ Query', max_length=1000, null=True, blank=True)
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client Name')
    external_url = models.CharField('External URL', max_length=1000, null=True, blank=True)
    profile_description = models.CharField('Profile Description', max_length=1000, null=True, blank=True)
    full_name = models.CharField('Full Name', max_length=200, null=True, blank=True)
    input_date = models.DateTimeField('Input Date', default=timezone.now, null=True, blank=True)
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    caption = models.CharField('Caption', max_length=1000, null=True, blank=True)
    quality_status = models.ForeignKey(QualityStatus, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Quality Status')
    connection_status = models.ForeignKey(ConnectionStatus, on_delete=models.CASCADE, verbose_name='Connection Status', null=True, blank=True)
    cs = models.CharField('CS', max_length=1000, null=True, blank=True)
    cs_reviewed = models.CharField('CS Reviewed', max_length=1000, null=True)
    operation_date = models.DateField('Operation Date', null=True, blank=True)
    mss = models.ForeignKey(MessageSendingStatus, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Message Sending Status')
    engagement_content = models.CharField('Engagement Content', max_length=200, null=True, blank=True)
    oms = models.ForeignKey(OMS, on_delete=models.CASCADE, null=True, blank=True, verbose_name='OMS')
    feedback_listing = models.CharField('Feedback Listing', max_length=200, null=True, blank=True)
    warm_script = models.ForeignKey(WarmScript, on_delete=models.CASCADE, related_name='+', verbose_name='Warm Script', null=True, blank=True)
    remarks = models.CharField('Remarks', max_length=1000, null=True, blank=True)
    screening_review_status = models.CharField('Screening Review Status', max_length=200, null=True, blank=True)
    cs_create_status = models.CharField('CS Create Status', max_length=200, null=True, blank=True)
    cs_crosscheck_status = models.CharField('CS Crosscheck Status', max_length=200, null=True, blank=True)
    cs_review_status = models.CharField('CS Review Status', max_length=200, null=True, blank=True)
    ms_status = models.CharField('MS Status', max_length=200, null=True, blank=True)
    oms_status = models.CharField('OMS Status', max_length=200, null=True, blank=True)
    screened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Screened By'
    )
    screening_start_time = models.DateTimeField('Screening Start Time', auto_now_add=False, null=True, blank=True)
    screened_date = models.DateTimeField('Screening End Time', auto_now_add=False, null=True, blank=True)
    cs_va = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='CS VA'
    )
    cs_start_time = models.DateTimeField('CS Start Time', auto_now_add=False, null=True, blank=True)
    cs_date = models.DateTimeField('CS End Time', auto_now_add=False, null=True, blank=True)
    cs_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='CS Reviewer'
    )
    cs_review_start_time = models.DateTimeField('CS Review Start Time', auto_now_add=False, null=True, blank=True)
    cs_review_date = models.DateTimeField('CS Review End Time', auto_now_add=False, null=True, blank=True)
    cs_crosscheck_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='CS Crosscheck By'
    )
    cs_crosscheck_start_time = models.DateTimeField('CS Crosscheck Start Time', auto_now_add=False, null=True, blank=True)
    cs_crosscheck_date = models.DateTimeField('CS Crosscheck End Time', auto_now_add=False, null=True, blank=True)
    ms_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Message Sending VA'
    )
    ms_start_time = models.DateTimeField('Message Sending Start Time', auto_now_add=False, null=True, blank=True)
    ms_date = models.DateTimeField('Message Sending End Time', auto_now_add=False, null=True, blank=True)
    oms_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='OMS VA'
    )
    oms_start_time = models.DateTimeField('OMS Start Time', auto_now_add=False, null=True, blank=True)
    oms_date = models.DateTimeField('OMS End Time', auto_now_add=False, null=True, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Added By'
    )
    added_date = models.DateTimeField('Added Date', auto_now_add=False, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Updated By'
    )
    updated_date = models.DateTimeField('Update Date', auto_now_add=False, null=True, blank=True)

    class Meta:
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'

    def __str__(self):
        return self.profile_username


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assigned_client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client', null=True, blank=True)
    assigned_account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Assigned Account')
    department = models.CharField(max_length=200)
    employee_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return self.employee_id


class Growthkeyword(models.Model):
    AUTOMATCH = 'ATM'
    POSSIBLE_AUTO_MATCH = 'PAM'
    AUTO_NO_MATCH = 'ANM'
    PHASE_2 = 'PH2'

    MATCH_TYPE_CHOICES = [
        (AUTOMATCH, 'Automatch'),
        (POSSIBLE_AUTO_MATCH, 'Possible Auto Match'),
        (AUTO_NO_MATCH, 'Auto No Match'),
        (PHASE_2, 'Phase 2'),
    ]
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, default=1, verbose_name='Client Name')
    keyword = models.CharField('Keyword', max_length=200)
    match_type = models.CharField(
        max_length=3,
        choices=MATCH_TYPE_CHOICES,
        default=AUTOMATCH,
    )

    class Meta:
        verbose_name = 'Growth Keyword'
        verbose_name_plural = 'Growth Keywords'

    def __str__(self):
        return self.keyword


class Listingkeyword(models.Model):
    AUTOMATCH = 'ATM'
    POSSIBLE_AUTO_MATCH = 'PAM'
    AUTO_NO_MATCH = 'ANM'

    MATCH_TYPE_CHOICES = [
        (AUTOMATCH, 'Automatch'),
        (POSSIBLE_AUTO_MATCH, 'Possible Auto Match'),
        (AUTO_NO_MATCH, 'Auto No Match'),
    ]
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, default=1, verbose_name='Client Name')
    keyword = models.CharField('Keyword', max_length=200)
    match_type = models.CharField(
        max_length=3,
        choices=MATCH_TYPE_CHOICES,
        default=AUTOMATCH,
    )

    class Meta:
        verbose_name = 'Listing Keyword'
        verbose_name_plural = 'Listing Keywords'

    def __str__(self):
        return self.keyword


class Posturl(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, default=1, verbose_name='Client Name')
    profile_username = models.CharField('Username', max_length=200, null=True, blank=True)
    post_url = models.CharField('Post URL', unique=True, max_length=200)
    description = models.TextField('Description', null=True, blank=True)
    caption = models.TextField('Caption', null=True, blank=True)
    publication_date = models.DateField('Publication Date', null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)
    location = models.CharField('Location', max_length=200, null=True, blank=True)
    input_date = models.DateTimeField('Input Date', default=timezone.now, null=True, blank=True)
    is_located = models.BooleanField('Is Located', default=False)
    is_scrapped = models.BooleanField('Is Scrapped', default=False)
    is_pushed_tempgrowth = models.BooleanField('Is Scrapped', default=False)
    scrapped_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name='Scrapped By'
    )
    scrapped_date = models.DateTimeField('Scrapped Date', auto_now_add=False, null=True, blank=True)

    class Meta:
        verbose_name = 'Post URL'
        verbose_name_plural = 'Post URLs'

    def __str__(self):
        return self.post_url


class TempPosturl(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE, default=1, verbose_name='Client Name')
    post_url = models.CharField('Post URL', max_length=200)
    description = models.TextField('Description', null=True, blank=True)
    caption = models.TextField('Caption', null=True, blank=True)
    publication_date = models.DateField('Publication Date', null=True, blank=True)
    hashtag = models.CharField('Hashtag', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Temp Post URL'
        verbose_name_plural = 'Temp Post URLs'

    def __str__(self):
        return self.post_url