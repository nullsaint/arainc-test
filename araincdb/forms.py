from django.forms import ModelForm
from django import forms
from .models import *

class GrowthForm(ModelForm):
    class Meta:
        model = Growth
        widgets = {
            'client_name': forms.Select(attrs={'class': 'form-control'}),
            'profile_username': forms.TextInput(attrs={'class': 'form-control'}),
            'scraping_status': forms.TextInput(attrs={'class': 'form-control'}),
            'external_url': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'post_count': forms.TextInput(attrs={'class': 'form-control'}),
            'followers': forms.TextInput(attrs={'class': 'form-control'}),
            'followings': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.TextInput(attrs={'class': 'form-control jq-datepicker'}),
            'hashtag': forms.TextInput(attrs={'class': 'form-control'}),
            'input_date': forms.TextInput(attrs={'class': 'form-control jq-datepicker'}),
            'quality_status': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'assigned_account': forms.Select(attrs={'class': 'form-control'}),
            'growth_status': forms.Select(attrs={'class': 'form-control'}),
            'connection_status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        exclude = ['screened_by', 'screened_date', 'growthed_by', 'growthed_date', 'updated_by', 'updated_date']


class ScreeningForm(ModelForm):
    def __init__(self,client_name,*args,**kwargs):
        super (ScreeningForm,self ).__init__(*args,**kwargs)
        self.fields['assigned_account'].queryset = Account.objects.filter(client_name=client_name)

    class Meta:
        model = Growth
        widgets = {
            'quality_status': forms.RadioSelect(),
            'assigned_account': forms.RadioSelect(),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['quality_status', 'assigned_account', 'remarks']


class ScreeningGrowthForm(ModelForm):

    class Meta:
        model = Growth
        widgets = {
            'growth_status': forms.RadioSelect(),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['growth_status', 'remarks']

class AssignAccountForm(ModelForm):

    class Meta:
        model = Employee
        widgets = {
            'assigned_account': forms.Select(attrs={'class': 'form-control'}),
        }
        fields = ['assigned_account']

class AssignClientForm(ModelForm):

    class Meta:
        model = Employee
        widgets = {
            'assigned_client': forms.Select(attrs={'class': 'form-control'}),
        }
        fields = ['assigned_client']


class UnfollowingForm(ModelForm):

    class Meta:
        model = Growth
        widgets = {
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['remarks']


class ListingForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'assigned_account': forms.Select(attrs={'class': 'form-control'}),
            'profile_username': forms.TextInput(attrs={'class': 'form-control'}),
            'connection_type': forms.Select(attrs={'class': 'form-control'}),
            'engagement_content': forms.Select(attrs={'class': 'form-control'}),
            'connection_status': forms.Select(attrs={'class': 'form-control bg-warning'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['assigned_account', 'profile_username', 'connection_type', 'engagement_content', 'connection_status', 'remarks']

class CSForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'assigned_account': forms.Select(attrs={'class': 'form-control'}),
            'profile_username': forms.TextInput(attrs={'class': 'form-control', 'readonly':'readonly'}),
            'connection_type': forms.Select(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'engagement_content': forms.Select(attrs={'class': 'form-control', 'disabled':'disabled'}),
            'connection_status': forms.Select(attrs={'class': 'form-control bg-warning'}),
            'feedback_listing': forms.TextInput(attrs={'class': 'form-control bg-warning'}),
            'cs_va': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cs_reviewer': forms.Textarea(attrs={'class': 'form-control bg-light', 'rows': 2}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['connection_status', 'feedback_listing', 'assigned_account', 'profile_username', 'connection_type', 'engagement_content', 'cs_va', 'cs_reviewer', 'remarks']


class WarmScreeningForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'assigned_account': forms.Select(attrs={'class': 'form-control'}),
            'quality_status': forms.RadioSelect(),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['assigned_account', 'quality_status', 'remarks']

class CSCrosscheckForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'quality_status': forms.RadioSelect(),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['quality_status', 'remarks']

class CSCreateForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'cs': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quality_status': forms.RadioSelect(),
            'feedback_listing': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['cs', 'feedback_listing', 'quality_status', 'remarks']

class CSReviewForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'cs': forms.Textarea(attrs={'readonly': 'readonly', 'class': 'form-control', 'rows': 2}),
            'cs_reviewed': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quality_status': forms.RadioSelect(),
            'feedback_listing': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['cs', 'cs_reviewed', 'feedback_listing', 'quality_status', 'remarks']


class MSForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'quality_status': forms.RadioSelect(),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['quality_status', 'remarks']


class OMSForm(ModelForm):

    class Meta:
        model = Listing
        widgets = {
            'oms': forms.RadioSelect(),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['oms', 'remarks']


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))