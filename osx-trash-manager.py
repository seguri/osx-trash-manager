#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from os import chdir, listdir, remove
from os.path import expanduser, isdir, isfile
from shutil import rmtree
import pytz
import sqlite3
import unicodedata


tzinfo = pytz.timezone('CET')
def iso8601():
	now = datetime.now(tzinfo)
	now = now.replace(microsecond=0)
	return now.isoformat()

# go to Trash
chdir(expanduser('~/.Trash'))

# connect
db = sqlite3.connect(expanduser('~/.Trash.db'))
c = db.cursor()
# create if necessary
c.execute('create table if not exists deleted_files(id integer primary key, filename text unique, delete_date text)')
# insert all new files
new_files = 0
for f in listdir('.'):
	# http://stackoverflow.com/a/26733055/1521064
	nor = unicodedata.normalize('NFC', f)
	# check if it's a new deleted file
	c.execute('select id from deleted_files where filename = ?', (nor,))
	ids = c.fetchone()
	if ids is None:
		c.execute('insert into deleted_files(filename, delete_date) values(?, datetime())', (nor,))
		new_files += 1
db.commit()
print iso8601(), 'new files:', new_files
# retrieve files older than 30 days
c.execute("select * from deleted_files where delete_date <= datetime('now', '-30 days')")
rows = c.fetchall()
deleted_files = 0
deleted_dirs = 0
for r in rows:
	nor = r[1]
	if isfile(nor):
		remove(nor)
		deleted_files += 1
	elif isdir(nor):
		rmtree(nor)
		deleted_dirs += 1
	else:
		print 'warning: neither dir nor file:', nor
	# in any case, delete old entry
	c.execute('delete from deleted_files where id = ?', (r[0],))
db.commit()
print iso8601(), 'deleted directories:', deleted_dirs
print iso8601(), 'deleted files:', deleted_files

