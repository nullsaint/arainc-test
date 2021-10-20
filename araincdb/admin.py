from django.shortcuts import render,  redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.db import IntegrityError
from .resources import *
from import_export import resources
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportActionModelAdmin


class AccountResource(resources.ModelResource):

    class Meta:
        model = Account


class ClientAdmin(ImportExportModelAdmin):
    list_display = ['id', 'client_name', 'client_code']


class AccountAdmin(ImportExportModelAdmin):
    list_display = ['id', 'account_name', 'username', 'account_code', 'client_name']


class ConnectionStatusAdmin(ImportExportModelAdmin):
    list_display = ['id', 'connection_status']

class ConnectionTypeAdmin(ImportExportModelAdmin):
    list_display = ['id', 'connection_type']

class ErrorTypeAdmin(ImportExportModelAdmin):
    list_display = ['id', 'error_type']

class GrowthStatusAdmin(ImportExportModelAdmin):
    list_display = ['id', 'growth_status']

class CountryAdmin(ImportExportModelAdmin):
    list_display = ['id', 'country']


class LocationAdmin(ImportExportModelAdmin):
    list_display = ['id', 'location']
    list_filter = ['country']


class MessageSendingStatusAdmin(ImportExportModelAdmin):
    list_display = ['id', 'mss']

class OMSAdmin(ImportExportModelAdmin):
    list_display = ['id', 'oms']

class QcFeedbackAdmin(ImportExportModelAdmin):
    list_display = ['id', 'qc_feedback']

class QualityStatusAdmin(ImportExportModelAdmin):
    list_display = ['id', 'quality_status']

class WarmScriptAdmin(ImportExportModelAdmin):
    list_display = ['id', 'url', 'message']

class GrowthResource(resources.ModelResource):

    class Meta:
        model   =   Growth
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(GrowthResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass

class GrowthAdmin(ImportExportActionModelAdmin):
    resource_class = GrowthResource
    list_display = ['id', 'profile_username', 'client_name', 'connection_status']
    list_filter = ['assigned_account', 'connection_status', 'quality_status', 'growth_status', 'location', 'growthed_date', 'client_name']

    # Override of ImportExportMixin.get_export_queryset
    # Filter export to exclude Growths where is_active is false
    # def get_export_queryset(self, request):
    #         return Growth.objects.filter(is_active=True)

    actions = ['growth_assign', 'export_admin_action', 'manual_screening']


    def growth_assign(self, request, queryset):
        accounts = Account.objects.all()

        if 'apply' in request.POST:
            account = request.POST['account']

            queryset.update(assigned_account=account, growth_review_status=None)
            self.message_user(request,
                              "{} Growths assigned".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())
        
        context={'accounts': accounts, 'growths': queryset}

        return render(request, 'araincdb/admin/growth_assign.html', context)
    
        growth_assign.short_description = "Assign Growth"


    def manual_screening(self, request, queryset):
        connection_statuses = ConnectionStatus.objects.all()

        if 'apply' in request.POST:
            connection_status = request.POST['connection_status']

            queryset.update(connection_status=connection_status)
            self.message_user(request,
                              "{} Manual Screeing done for ".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())
        
        context={'connection_statuses': connection_statuses, 'growths': queryset}

        return render(request, 'araincdb/admin/manual_screening.html', context)
    
        manual_screening.short_description = "Maual Screening"


class TempgrowthResource(resources.ModelResource):

    class Meta:
        model   =   Tempgrowth
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(TempgrowthResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass


class TempgrowthAdmin(ImportExportModelAdmin):
    resource_class = TempgrowthResource
    list_display = ['id', 'client_name', 'profile_username', 'scraping_status', 'external_url', 'publication_date', 'hashtag', 'location', 'caption']


class TemplistingResource(resources.ModelResource):

    class Meta:
        model   =   Templisting
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(TemplistingResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass


class TemplistingAdmin(ImportExportModelAdmin):
    resource_class = TemplistingResource
    list_display = ['id', 'client_name', 'profile_username', 'photo_url_query', 'connection_type']


class ListingResource(resources.ModelResource):

    class Meta:
        model   =   Listing
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(ListingResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass


class ListingAdmin(ImportExportActionModelAdmin):
    resource_class = ListingResource
    list_display = ['id', 'profile_username', 'assigned_account', 'connection_status', 'connection_type', 'mss', 'ms_date', 'oms']
    list_filter = ['connection_status', 'oms', 'assigned_account', 'mss', 'ms_date', 'connection_type']

    actions = ['assign_operaton_date', 'export_admin_action']


    def assign_operaton_date(self, request, queryset):
        if 'apply' in request.POST:
            operation_date = request.POST['operation_date']

            queryset.update(operation_date=operation_date)
            self.message_user(request,
                              "Operation Date was assigned to {} records".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())
        
        context={'lists': queryset}

        return render(request, 'araincdb/admin/assign_operaton_date.html', context)
    
    assign_operaton_date.short_description = "Assign Operation Date"


class EmployeeResource(resources.ModelResource):

    class Meta:
        model   =   Employee
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(ListingResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass


class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = ['id', 'employee_id', 'department']


class GrowthkeywordResource(resources.ModelResource):

    class Meta:
        model   =   Growthkeyword
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(GrowthkeywordResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass


class GrowthkeywordAdmin(ImportExportModelAdmin):
    resource_class = GrowthkeywordResource
    list_display = ['id', 'client_name', 'keyword', 'match_type']
    list_filter = ['client_name', 'match_type']


class ListingkeywordResource(resources.ModelResource):

    class Meta:
        model   =   Listingkeyword
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(ListingkeywordResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass


class ListingkeywordAdmin(ImportExportModelAdmin):
    resource_class = ListingkeywordResource
    list_display = ['id', 'client_name', 'keyword', 'match_type']
    list_filter = ['client_name', 'match_type']


class PosturlResource(resources.ModelResource):

    class Meta:
        model   =   Posturl
        skip_unchanged = True
        report_skipped = True

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        try:
            super(PosturlResource, self).save_instance(instance, using_transactions, dry_run)
        except IntegrityError:
            pass


class PosturlAdmin(ImportExportModelAdmin):
    resource_class = PosturlResource
    list_display = ['id', 'post_url', 'description', 'caption', 'location']
    list_filter = ['input_date','location']


class TempPosturlAdmin(ImportExportModelAdmin):
    list_display = ['id', 'post_url', 'description', 'caption']


class MultipleFileUplaoderAdmin(ImportExportActionModelAdmin):
    list_display = ['profile_username']

class HashtagListAdmin(ImportExportActionModelAdmin):
    list_display = ['hashtag']
    


# Register your models here.
admin.site.register(hashtag_list, HashtagListAdmin)
admin.site.register(MultipleFileUplaoder, MultipleFileUplaoderAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(ConnectionStatus, ConnectionStatusAdmin)
admin.site.register(ConnectionType, ConnectionTypeAdmin)
admin.site.register(ErrorType, ErrorTypeAdmin)
admin.site.register(GrowthStatus, GrowthStatusAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(MessageSendingStatus, MessageSendingStatusAdmin)
admin.site.register(OMS, OMSAdmin)
admin.site.register(QcFeedback, QcFeedbackAdmin)
admin.site.register(QualityStatus, QualityStatusAdmin)
admin.site.register(WarmScript, WarmScriptAdmin)
admin.site.register(Growth, GrowthAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Tempgrowth, TempgrowthAdmin)
admin.site.register(Templisting, TemplistingAdmin)
admin.site.register(Growthkeyword, GrowthkeywordAdmin)
admin.site.register(Listingkeyword, ListingkeywordAdmin)
admin.site.register(Posturl, PosturlAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(TempPosturl, TempPosturlAdmin)


# Changing Admin header
admin.site.site_header = "Ara Inc"
admin.site.site_title = "Ara Inc"
