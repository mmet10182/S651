import re
import smtplib
from email.mime.text import MIMEText
from decouple import config
from .settings import APIV1_DATA_FOLDER_HOSTS
import os
from datetime import datetime
from django.core.files.storage import FileSystemStorage


def apiv1_save_report(reportfile, uid):
    file_name = '{}_{}'.format(datetime.now().strftime('%d-%m-%Y_%H-%M-%S'), 'report.log')
    fs = FileSystemStorage(location=os.path.join(APIV1_DATA_FOLDER_HOSTS, uid))
    filename = fs.save(file_name, reportfile)
    path = os.path.join(APIV1_DATA_FOLDER_HOSTS, uid, filename).replace('\\', '/')
    return path


def apiv1_create_folder_uid(func):
    def wrapper(*args, **kwargs):
        folder_name = kwargs['uid']
        if not os.path.exists(os.path.join(APIV1_DATA_FOLDER_HOSTS, folder_name)):
            path = os.path.join(APIV1_DATA_FOLDER_HOSTS, folder_name)
            os.mkdir(path)
        return func(*args, **kwargs)

    return wrapper


def apiv1_get_content(report_path):
    with open(report_path, 'r') as f:
        content_report = f.readlines()
    return content_report


def apiv1_check_report(report_path):
    with open(report_path, 'r') as f:
        content_report = f.readlines()

    for index, i in enumerate(content_report):
        type_controller = re.search(r'Product Name|Controller Model', i, re.IGNORECASE)
        if type_controller is not None:
            lsi = re.search(r'avago|lsi|megaraid', i, re.IGNORECASE)
            asr = re.search(r'adaptec|asr', i, re.IGNORECASE)
            if lsi:
                regex = r"(\b[R|r][A|a][I|i][D|d][0-9]+[-]*\s*)(\s+\w+)(\s+\w+\n*)"
                allowed =  ['optl', 'ok']
                return apiv1_get_status(regex, allowed, content_report)
            elif asr:
                regex = r"(status\sof\slogical\sdevice)\s+:\s([a-z0-9]+)"
                allowed =  ['optl', 'ok']
                return apiv1_get_status(regex, allowed, content_report)
            elif len(content_report) == index - 1 and (lsi and asr) is None:
                report1 = {'model': 'Could not detect controller type',
                           'report': content_report,
                           }
                return report1


def apiv1_get_status(regex, allowed, content):
    status = None
    content = '\n'.join(content)
    values = re.findall(regex, content, re.IGNORECASE | re.MULTILINE)
    if not values:
        status = False
    for value in values:
        if value[1].lower().replace(' ', '') in allowed:
            status = True
        else:
            status = False
            break
    return status


def apiv1_send_message(state, content):
    content = ' '.join(content)
    regex = "\d+.\d+.\d+.\d+"
    ip_addr = re.search(regex, content)

    if state:
        subject = "Report Raid " + str(ip_addr[0])
    else:
        subject = "RAID ERROR !!!" + str(ip_addr[0])

    msg = MIMEText(content)
    msg['Subject'] = subject
    server = smtplib.SMTP(config('MAIL_SERVER'))
    for mail_to in config('MAIL_TO'):
        server.sendmail(config('MAIL_FROM'), mail_to, msg.as_string())
    server.quit()


def apiv1_remove_old_report(report_path):
    path = os.path.dirname(report_path)
    for filename in sorted(os.listdir(path))[:-5]:
        filename_relPath = os.path.join(path, filename)
        os.remove(filename_relPath)