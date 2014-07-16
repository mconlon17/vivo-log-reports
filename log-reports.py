#!/usr/bin/env/python
"""
    log-reports.py -- report on VIVO log files

    Verison 1.0 M. Conlon 2012-05-10
    --  read log fle for 1 (default) or many days and tabulates editor,
        subjects, predicates, objects, actions
    1.1 MC 2014-06-05
    --  Update for reading vivo.all.log.1.  Works as expected for single file

    To Do
    --  Handle multi-file
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.1"

from datetime import datetime
from datetime import timedelta
from urllib2 import urlopen

def counts(s,log,trim=None):
    trim_text = ""
    if trim is not None:
        trim_text = ' (trimmed at '+str(trim)+')'
    print "\nCounts of "+s+trim_text
    things = {}
    for row in log:
        try:
            thing = row[s]
            things[thing] = things.get(thing,0) + 1
        except:
            continue
    i=0    
    for thing in sorted(things, key =things.get, reverse=True):
        i = i + 1
        if trim is not None and i > trim:
            break
        print things[thing],'\t',thing

def get_logs(from_date, to_date):
    """
    Given a from and to date, gather and return the logs
    """
    base_uri = 'http://vivo.ufl.edu/logs/vivo-triple-log-'
    tail_uri = '.log'
    date_fmt = '%Y-%m-%d'
    log_recs = []
    date = from_date
    while date <= to_date:
        date_str = date.strftime(date_fmt)
        uri = base_uri + date_str + tail_uri
        print "Reading", date_str, "from", uri
        try:
            response = urlopen(uri)
            log_file = response.read().split('\n')
            log_recs = log_recs + log_file
        except:
            pass
        date = date + day
    return log_recs

# Start here

print datetime.now(),"Start"

day = timedelta(days=1)
to_date = datetime.now() - day
from_date = datetime.now() - 30*day
log_recs = get_logs(from_date, to_date)
n = 0
log = []
for row in log_recs:
    if len(row) < 127:
        continue
    words = row.split(' ')
    if len(words) < 10:
        continue
    io = words[9][:-1]
    user = words[8][:-1]
    process = words[7][:-1]
    date = words[5]
    triple_string = ' '.join(words[10:])
    triple_string = triple_string.replace('","',"|")
    try:
        [subject,predicate,object] = triple_string.split("|")
        object = object.replace('""', '"')
        object = object.replace('>"', '>')
        object = object.replace('\n', '')
        if subject[0] == '"':
            subject = subject[1:]
    except:
        continue
    if io != "ADD" and io != "SUB":
        continue
    n = n + 1
    log.append({
        "User" : user,
        "Process" : process,
        "ADD/SUB" : io,
        "Date" : date,
        "Subject" : subject,
        "Predicate": predicate,
        "Object": object
        })

print n,"log lines read"

counts("Date",log)
counts("Process",log)
counts("ADD/SUB",log)
counts("User",log)
counts("Subject",log,trim=50)
counts("Predicate",log,trim=50)
counts("Object",log,trim=50)
print datetime.now(),"Finish"
