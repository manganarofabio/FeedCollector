#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""FeedCollector

Usage:

    feedCollector -a <rss-url> -c <category>
    feedCollector -d <rss-url>
    feedCollector -t <category>
    feedCollector (-h | --help)
    feedCollector --topics
Options:
                                Start FeedCollector with while loop.
    -a URL  -c CATEGORY         Add new url <rss-url> to database under <category>
    -d URL                      Delete <rss-url> from the database file.
    -t CATEGORY                 Show the stored urls for the specific <category>.
    -h --help                   Show this screen.
    --topics                    Show all the stored topics
"""

from __future__ import print_function
import time
from myFeedParser import myFeedParser
from urls import rss
import db
import argparse
from pony import orm
import os


try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen



def _connected():
    """check internet connect"""
    host = 'http://google.com'

    try:
        urlopen(host)
        return True
    except:
        return False

def main():


    parser = argparse.ArgumentParser(description="esegue feedCollector")
    parser.add_argument('-a', action="store", dest="a", help="add url A in category -c" )
    parser.add_argument('-c', action="store", dest="c", help="category")
    parser.add_argument('-d', action="store", dest="d", help="delete url B")
    parser.add_argument('--topics', action="store_true", default=False, help="show all topics")
    parser.add_argument('-t', action="store", dest="t", help="show urls topic T")

    args = parser.parse_args()
    print(args)

    a = args.a
    c = args.c
    d = args.d
    t = args.t
    topics = args.topics

    #DB init

    flag_populated = os.path.isfile('feed.db')  # true if existing

    if not flag_populated:
        mdb = db.define_database_and_entities(provider='sqlite', filename='feed.db', create_db=True)
        db.urls_populate_db(mdb, rss)
        print('db created and populated')
    else:
        mdb = db.define_database_and_entities(provider='sqlite', filename='feed.db', create_db=True)
        print('db connected')

    if a is not None:

        if c is not None:
            mfp = myFeedParser(a, c)
            url = mfp.parseFeed()

            if url is not None:
                with orm.db_session:
                    if not mdb.Url.exists(link=a):
                        url = mdb.Url(link=a, topic=c)
                        mdb.commit()
                    else:
                        print('url already existing')

            else:
                print('url not valid')

        else:
            print('insert topic')

    elif d is not None:

        with orm.db_session:
            if mdb.Url.exists(link=d):

                link = mdb.Url[d]
                print(link)
                link.delete()
                mdb.commit()
                print('link {} deleted'.format(d))
            else:
                print('link not existing')

    elif t is not None:
        if t in rss.keys():
            with orm.db_session:

                links = mdb.Url.select(lambda top:  top.topic == t)
                for l in links:
                    print(l)
        else:
            print('topic {} not existing'.format(t))

    elif topics is True:
        print(rss.keys())

    else:
        #5 minutes
        timeout = 60*5
        while True:

            print("loop")
            with orm.db_session:
                links = orm.select(u.link for u in mdb.Url)
                #print(type(links))
                for l in links:
                    print(l)

            #print(flag_populated)

            #populating items
            with orm.db_session:
                for top in rss.keys():
                    print(top)
                    urls_topic_x = mdb.Url.select(lambda t: t.topic == top)

                    for l1 in urls_topic_x:
                        # fixig url
                        l2 = str(l1)
                        l2 = l2[5:-2]

                        fp = myFeedParser(url=l2, topic=top)
                        correct = fp.parseFeed()
                        if correct is not None:
                            print('feed {} ok'.format(fp.url))
                            listItemParsed = fp.fetchFeed()
                            for it in listItemParsed:

                                if mdb.Item.exists(link=it['link']):
                                    #print("item already existing")
                                    continue
                                else:
                                    item = mdb.Item(link=it['link'], title=it['title'], descr=it['descr'], pubDate=it['pubDate'],
                                                    img=it['img'], topic=it['topic'])
                                    mdb.commit()

                        else:
                            print('feed not valid')

            print("timeout")
            time.sleep(timeout)



# start
if __name__ == '__main__':

    if not _connected():
        print('No Internet Connection!')
        exit()

    main()








