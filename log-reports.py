#!/usr/bin/env/python
"""
    log-reports.py -- report on VIVO log files

    Verison 1.0 M. Conlon 2012-05-10

    --  read log fle for 1 (default) or many days and tabulates editor,
        subjects, predicates, objects, actions

    Requested features

    --  Improve resiliency to minor variations in the time stamp in the
        name of the log file.
    --  Use global variable for location of log files
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"


import urllib2, datetime
import csv

def log_url(d):
    url="http://vivo.ufl.edu/logs/vivo-triple-log-"+d.isoformat()+"T04:00:01.log"
    return url
 
def get_log(d):
    url = log_url(d)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    reader = csv.reader(response)
    log = ["date","thing","user","as","subject","predicate","object"]
    for row in reader:
        log.append(row)
    return log[7:]

def counts(s,log,trim=100000000):
    names = ["Date","Process","User","ADD/SUB","Subject","Predicate","Object"]
    ix = names.index(s)
    print "Counts of "+s
    things = {}
    for row in log:
        try:
            thing = row[ix]
            things[thing] = things.get(thing,0) + 1
        except:
            continue
    i=0    
    for thing in sorted(things, key =things.get, reverse=True):
        i = i + 1
        if i > trim:
            break
        print thing,things[thing]

# Get a log from a particular date
d = datetime.date(2012,12,07)
log = get_log(d)

# get the logs from the previous 6 days to make a week

for i in range(1):
    d = d - datetime.timedelta(days=1)
    log = log+get_log(d)

print "I got the logs.  They have ",len(log)," entries"

counts("User",log)
counts("Process",log)
counts("ADD/SUB",log)
counts("Date",log)
counts("Subject",log,trim=25)
counts("Predicate",log,trim=25)
counts("Object",log,trim=25)

