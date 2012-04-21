#!/usr/bin/env python
#
import sys
import xapian
import string


if len(sys.argv) != 2:
    print >> sys.stderr, "Usage: %s PATH_TO_DATABASE" % sys.argv[0]
    sys.exit(1)

try:
    # Open the database for update, creating a new database if necessary.
    database = xapian.WritableDatabase(sys.argv[1], xapian.DB_CREATE_OR_OPEN)

    indexer = xapian.TermGenerator()
    stemmer = xapian.Stem("english")
    indexer.set_stemmer(stemmer)

    para = ''
    try:
        for line in sys.stdin:
            line = string.strip(line)
            if line == '':
                if para != '':
                    # We've reached the end of a paragraph, so index it.
                    doc = xapian.Document()
                    doc.set_data(para)

                    indexer.set_document(doc)
                    indexer.index_text(para)

                    # Add the document to the database.
                    database.add_document(doc)
                    para = ''
            else:
                if para != '':
                    para += ' '
                para += line
    except StopIteration:
        pass

except Exception, e:
    print >> sys.stderr, "Exception: %s" % str(e)
    sys.exit(1)
