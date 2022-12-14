from django.http import HttpResponse
from .services import lib
from rest_framework.views import APIView
import re


# Create your views here.

class ApiV1HostDiskReport(APIView):
    @lib.apiv1_create_folder_uid
    def post(self, request, uid):
        reportfile = request.FILES['shell_out']
        report_path = lib.apiv1_save_report(reportfile, uid)
        shell_out = lib.apiv1_get_content(report_path)
        status = lib.apiv1_check_report(report_path)
        lib.apiv1_send_message(status, shell_out)
        lib.apiv1_remove_old_report(report_path)
        return HttpResponse(status=200)
