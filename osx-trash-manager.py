#!/usr/bin/env python
#-*- coding: utf-8 -*-

import logging
import sqlite3

from os import listdir, remove
from os.path import isdir, isfile, join, expanduser
from shutil import rmtree

HOME        = expanduser("~")
TRASH       = join(HOME, '.Trash')
DB          = join(HOME, '.Trash.sqlite3')

EXPIRE_TIME = '-30 days'

SIMPLE_FORMAT  = '%(levelname)-8s %(message)s'
VERBOSE_FORMAT = '%(levelname)-8s %(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=SIMPLE_FORMAT, level=logging.DEBUG)
# WARNING: define a logger her may cause problems when this module is intended
# to be imported from elsewhere. Calling `logging.dictConfig()` may override
# this settings if the python 2.7+ option `disable_existing_loggers` is not used
logger = logging.getLogger(__name__)

class TrashDB(object):

    def __init__(self):
        super(TrashDB, self).__init__()
        self.db = sqlite3.connect(DB)
        self.cursor = self.db.cursor()
        self.added_files_count = 0
        self.removed_files_count = 0

    def create(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS file_eliminati(id INTEGER PRIMARY KEY, name TEXT UNIQUE, data TEXT)')
        self.db.commit()

    def insert(self, trashed_file, timestamp='now'):
        query = '''INSERT INTO file_eliminati(name, data) VALUES ('%s', datetime('%s'))''' % (unicode(trashed_file), timestamp)
        self.cursor.execute(query)
        self.db.commit()
        self.added_files_count += 1

    def delete(self, trashed_file):
        id = self.exists(trashed_file)
        if id:
            self.cursor.execute('DELETE FROM file_eliminati WHERE id = ?', [ id ])
            self.db.commit()
        return id

    def exists(self, trashed_file):
        self.cursor.execute('SELECT id FROM file_eliminati WHERE name = ?', [ unicode(trashed_file) ])
        id = self.cursor.fetchone()
        if id:
            return id[0]
        return None

    def retrieve_expired_files(self):
        """Return a list of tuples containing only filenames of files
        stored in the trash for more than 30 days.
        """
        query = '''SELECT name FROM file_eliminati WHERE data <= datetime('now', '%s')''' % EXPIRE_TIME
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        logger.info("Found %d file(s) older than 30 days." % len(rows))
        return rows

    def close(self):
        self.db.close()

class TrashedFile(object):

    def __init__(self, filename):
        super(TrashedFile, self).__init__()
        self.filename = filename
        self.path = join(TRASH, filename)

    # "The goal of __repr__ is to be unambiguous"
    # "Container's __str__ uses contained objects' __repr__"
    def __repr__(self):
        return 'TrashedFile(%r)' % self.filename

    def __unicode__(self):
        """Return unicode (text) in PY2
        """
        if self.is_unicode():
            return self.filename
        return unicode(self.filename, 'utf-8')

    # "The goal of __str__ is to be readable"
    # "__str__ defaults to __repr__ if no __str__ is implemented"
    def __str__(self):
        """Return str (bytes) in PY2, text in PY3
        """
        return unicode(self).encode('utf-8')

    def is_unicode(self):
        if isinstance(self.filename, unicode): return True
        if isinstance(self.filename, str): return False
        raise TypeError

    def filetype_symbol(self):
        """Check if given path is a directory, a file or something unknown.
        Return a char using the same convention as *nix `ls`
        """
        if isdir(self.path): return 'd'
        if isfile(self.path): return '-'
        return '?'

    def delete(self):
        """Return boolean
        """
        result = False
        try:
            if isfile(self.path): remove(self.path)
            if isdir(self.path): rmtree(self.path, ignore_errors=False)
            result = True
        except TypeError as e:
            logger.error(str(e))
        return result

def main():
    # create table
    db = TrashDB()
    db.create()

    # check and store missing files
    for f in listdir(TRASH):
        tf = TrashedFile(f)
        if not db.exists(tf):
            if db.added_files_count is 0:
                logger.debug("New file(s) found:")
            logger.debug("%s %s %s" % (tf.filetype_symbol(), 'utf-8' if tf.is_unicode() else 'ascii', f))
            db.insert(tf)

    logger.info("Found %d new file(s)." % db.added_files_count)

    # check old files and delete them
    for f in db.retrieve_expired_files():
        tf = TrashedFile(f[0])
        if db.removed_files_count is 0:
            logger.debug("Old file(s) found:")
        logger.debug("%s %s %s" % (tf.filetype_symbol(), 'utf-8' if tf.is_unicode() else 'ascii', f))
        if tf.delete() and db.delete(tf):
            db.removed_files_count += 1

    logger.info("Removed %d file(s)." % db.removed_files_count)

    db.close()

if __name__ == "__main__":
    main()
