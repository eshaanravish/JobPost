import datetime

from job.models import Job
from django.utils.deprecation import MiddlewareMixin

class JobActive(MiddlewareMixin):
    def process_request(self, request):
        Job.objects.filter(job_valid_upto__lte=datetime.date.today(), job_availability=True).update(job_availability=False)
