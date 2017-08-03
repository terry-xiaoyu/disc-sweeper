## disc-sweeper
This is a small python script used to clean expired files on your server, if it there's no enough disk space.

It uses following linux command to clean your server.
```shell
find /path/to/be/cleaned -mindepth 1 -mtime +{days_of_expiry} -depth -print > /path/to/log/sweep-date.log
```
It will also email you before the clean.

Please set the constants at the beginning of the script.

NOTE:
Your email account should allow login from 'less-secured' apps

### config the crontab
The following config runs a crontab task at 10:00 and 18:00 every day
```shell
cat /etc/crontab
0  10,18 * * * root python /data/disc-sweeper/discMonitor.py
```
