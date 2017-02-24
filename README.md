# openstack-utils
Just some helper programs for my work in OpenStack

## download-log-files.py
This is a program to download the log files from an OpenStack gate job run.
Just provide it a URL to the top-level log directory (the one containing
console.html) and it will download all the log files.

## find-log-messages.py
This is a program to scan log files and print messages which are at a certain
log level or higher.

## fix-telnet.py
A program to execute telnet when given a URL in the form of
telnet://HOST_IP_ADDRESS:PORT. These URLs are provided by the Zuul status page
http://status.openstack.org/zuul/
