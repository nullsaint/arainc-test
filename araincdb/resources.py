from import_export import resources
from .models import *

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