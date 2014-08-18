#!/usr/bin/env/python
"""
    log-reports.py -- report on VIVO log files

    Version 1.0 M. Conlon 2012-05-10
    --  read log fle for 1 (default) or many days and tabulates editor,
        subjects, predicates, objects, actions
    1.1 MC 2014-06-05
    --  Update for reading vivo.all.log.1.  Works as expected for single file
    1.2 MC 2014-08-11
    --  Now reads web files.  Command line arguments control number of days to
        read and the trim level
    1.3 MC 2014-08-13
    --  Fixed bug reading wrong date in the log.  Date is now correct for
        transactions
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.3"

from datetime import datetime
from datetime import timedelta
from urllib2 import urlopen
import argparse


def counts(s, log_data, trim=None):
    """
    Given a keyword s, and log data, generate a frequency table for s from the
    log data
    :param s: name of key
    :param log_data: log data
    :param trim: number of lines to show in frequency tables
    """
    trim_text = ""
    if trim is not None:
        trim_text = ' (trimmed at ' + str(trim) + ')'
    print "\nCounts of " + s + trim_text
    things = {}
    for row in log_data:
        try:
            thing = row[s]
            things[thing] = things.get(thing, 0) + 1
        except KeyError:
            continue
    i = 0
    for thing in sorted(things, key=things.get, reverse=True):
        i = i + 1
        if trim is not None and i > trim:
            break
        print things[thing], '\t', thing


def get_logs(start_date, end_date):
    """
    Given a start and end date, gather and return log_records, a list of the log
    records
    """
    base_uri = 'http://vivo.ufl.edu/logs/vivo-triple-log-'
    tail_uri = '.log'
    date_fmt = '%Y-%m-%d'
    log_records = []
    log_date = start_date
    while log_date <= end_date:
        date_str = log_date.strftime(date_fmt)
        uri = base_uri + date_str + tail_uri
        print "Reading", date_str, "from", uri
        try:
            response = urlopen(uri)
            log_file = response.read().split('\n')
            log_records = log_records + log_file
        except IOError:
            pass
        log_date = log_date + day
    return log_records

# Start here

parser = argparse.ArgumentParser()
parser.add_argument("days", help="number of days of logs to include",
                    type=int, default=7)
parser.add_argument("trim", help="number of lines to show in tables",
                    type=int, default=100)
args = parser.parse_args()

print datetime.now(), "Start"

day = timedelta(days=1)
to_date = datetime.now() - day
from_date = datetime.now() - args.days * day
log_recs = get_logs(from_date, to_date)
n = 0
log = []
for log_row in log_recs:
    if len(log_row) < 127:
        continue
    words = log_row.split(' ')
    if len(words) < 10:
        continue
    io = words[9][:-1]
    user = words[8][:-1]
    process = words[7][:-1]
    date = words[0]
    triple_string = ' '.join(words[10:])
    triple_string = triple_string.replace('","', "|")
    try:
        [triple_subject, triple_predicate, triple_object] = \
            triple_string.split("|")
        triple_object = triple_object.replace('""', '"')
        triple_object = triple_object.replace('>"', '>')
        triple_object = triple_object.replace('\n', '')
        if triple_subject[0] == '"':
            triple_subject = triple_subject[1:]
    except:
        continue
    if io != "ADD" and io != "SUB":
        continue
    n = n + 1
    log.append({
        "User": user,
        "Process": process,
        "ADD/SUB": io,
        "Date": date,
        "Subject": triple_subject,
        "Predicate": triple_predicate,
        "Object": triple_object
    })

print n, "log lines read"

counts("Date", log)
counts("Process", log)
counts("ADD/SUB", log)
counts("User", log)
counts("Subject", log, trim=args.trim)
counts("Predicate", log, trim=args.trim)
counts("Object", log, trim=args.trim)
print datetime.now(), "Finish"
