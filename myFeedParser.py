"""" classe per parsare feed"""

import feedparser
import bs4
import re
from time import mktime
from datetime import datetime


import db




class myFeedParser:

    def __init__(self, url, topic):
        self.url = url
        self.topic = topic



    def parseFeed(self):

         d = feedparser.parse(self.url)
         if d.entries:
             return d
         else:
             print("INVALID URL feed: {}".format(self.url))
             return None



    #esegue il fetch di un singolo feed e memorizza gli items nel db
    def fetchFeed(self):

        feed = self.parseFeed()
        news_list = []
        for newsitem in feed['items']:

            link = newsitem['link']
            title = newsitem['title']
            descr = newsitem['description']
            dt = newsitem['published_parsed']
            #print(pubDate)
            pubDate = datetime.fromtimestamp(mktime(dt))

            # getting img src from description
            soup = bs4.BeautifulSoup(descr, "html.parser")
            img = soup.find('img')
            if img is not None:
                src = img["src"]
            else:
                # azione defoult
                src = 'NO IMAGE'
            # pulizia description

            clean_descr = self.clean_txt(descr)
            if clean_descr == '':
                clean_descr = 'NO DESCRIPTION'


            news_list.append({'link': link,
                    'title': title,
                    'descr': clean_descr,
                    'pubDate': pubDate,
                    'img': src,
                    'topic': self.topic

                    })
        return news_list


            #creo dict

            # it = item.item(link, title, desc, pubDate, self.topic, img)
            #
            #
            #
            # #operazione di memorizzazione item nel db
            # feedDBOp.storeItem(item)

            #collegamento al db e memorizzazione
            #db.db_item_store(link, title, desc, img, self.topic)





    def clean_txt(self, txt):
        """clean txt from e.g. html tags"""
        cleaned = re.sub(r'<.*?>', '', txt)  # remove html
        cleaned = cleaned.replace('&lt;', '<').replace('&gt;', '>')  # retain html code tags
        cleaned = cleaned.replace('&quot;', '"')
        cleaned = cleaned.replace('&rsquo;', "'")
        cleaned = cleaned.replace('&nbsp;', ' ')  # italized text
        return cleaned




