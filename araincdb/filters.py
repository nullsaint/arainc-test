import django_filters
from .models import *

class GrowthFilter(django_filters.FilterSet):
    class Meta:
        model = Growth
        fields = ['client_name', 'publication_date', 'quality_status',
        'location', 'growth_status', 'connection_status']


class ListingFilter(django_filters.FilterSet):
    class Meta:
        model = Listing
        fields = ['assigned_account', 'connection_type', 'connection_status',
        'operation_date', 'feedback_listing']