import smtplib
import socket
import os
import subprocess

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# PATH_TO_BE_MONITOR is the path to be monitored, e.g. "/"
#  If the current percentage of free space under {PATH_TO_BE_MONITOR} is lower than {MIN_FREE_PERCENT},
#  then a disk sweep will be performed and the contacts in the {TO_EMAILS} will get warned
PATH_TO_BE_MONITOR = "/path/to/be/monitored"

# PATHS_CAN_BE_CLEAN contains the paths could be swept
#  These paths are typically paths to logs and tmp images you want to clean after some days
PATHS_CAN_BE_CLEAN = ["/path/can/be/deleted/1", "/path/can/be/deleted/2"]

# EXPIRY_DAYS is the expiry time of files to be swept.
#  The files under {PATH_TO_BE_MONITOR} with modified-date more than {EXPIRY_DAYS} days ago will be deleted 
EXPIRY_DAYS = 30

# TO_EMAILS is the list of person you want to notify upon disk-full
TO_EMAILS = ["xxx1@qq.com", "xxx2@gmail.com"]

# TOOL_NAME is the name of this script, which will be shown as the 'From' bar in the warn email
TOOL_NAME = "system-monitor"

# MIN_FREE_PERCENT is the minimum percentage of free spaces required on the specified disk.
#  see the description of PATH_TO_BE_MONITOR
MIN_FREE_PERCENT = 10

# PATH_LOGS is the path to the logs
#  will be created if not exists
PATH_LOGS = "/data/disc-sweeper"

# EMAIL_ACCOUNT is your account to be used by this script for sending the email
EMAIL_ACCOUNT = "xxxxxx@163.com"

# EMAIL_PASSWD is the password of your email account
#  if you use Gmail, plz enable 'https://myaccount.google.com/lesssecureapps'
#  if you use 163 to send your email, plz set the 'authorization code' first, and use it as your password
EMAIL_PASSWD = "your-password"

def sendTo163(fromaddr, toaddrs, subject, body):
    account = EMAIL_ACCOUNT
    password = EMAIL_PASSWD

    # fill the msg body
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ', '.join(toaddrs)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()

    # login your smtp server using your account
    server = smtplib.SMTP_SSL('smtp.163.com', 587, timeout=15)
    server.login(account, password)

    # send the email and logout
    server.sendmail(account, toaddrs, text)
    server.quit()

def notify_disc_full(freePercent):
    toaddr = TO_EMAILS
    fromaddr = TOOL_NAME

    hostname = socket.gethostname()
    hostip = socket.gethostbyname(hostname)

    subject = "Warn: Disk of {mon_path} on {host} [{ip}] is nearly full! Only {free}% free now".format(
        mon_path=PATH_TO_BE_MONITOR,
        host = hostname,
        ip = hostip,
        free = freePercent
    )

    df_res = subprocess.check_output(['df', '-h', PATH_TO_BE_MONITOR])
    du_res = subprocess.check_output(['du', '-h', '-d', '1', PATH_TO_BE_MONITOR])

    # customize your email body here
    body = """
The free disk space on {mon_path} is lower than {min_free_percent}% !

A disc auto-clean process will be performed on following paths:
{clean_path}

======================================
df -h {mon_path}
{df}

du -hd 1 {mon_path}
{du}
======================================

//NOTE:
DO NOT REPLY!
This is an email sent by a script automatically

System adminstrators:

  xxxx1@your-company.com;
  xxxx2@your-company.com;
""".format(
        df = df_res,
        du = du_res,
        clean_path = '\n'.join(PATHS_CAN_BE_CLEAN),
        mon_path=PATH_TO_BE_MONITOR,
        min_free_percent = MIN_FREE_PERCENT
    )

    sendTo163(fromaddr, toaddr, subject, body)


def cleanDisc(path, mtime):
    subprocess.call(["mkdir", "-p", PATH_LOGS])
    f = open(PATH_LOGS + "sweep-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +".log", "w")
    findCmd = ["find"] + path + ["-mindepth", "1", "-mtime", "+"+str(mtime), "-delete", "-print"] 
    subprocess.call(findCmd, stdout=f, stderr=f)
    f.close()

def getFreeDiscPercentage(path):
    s = os.statvfs(path)
    total_disc = s.f_frsize * s.f_blocks
    avail_disc = s.f_frsize * s.f_bavail
    return round((float(avail_disc)/total_disc)*100, 2)

## program entrance
freeSpacePercent = getFreeDiscPercentage(PATH_TO_BE_MONITOR)

if freeSpacePercent < MIN_FREE_PERCENT:
    print "disc is nearly full! At least", MIN_FREE_PERCENT, "% free spaces is need."
    notify_disc_full(freeSpacePercent)
    cleanDisc(PATHS_CAN_BE_CLEAN, EXPIRY_DAYS)
