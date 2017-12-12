"""" classe per parsare feed"""

import feedparser
import bs4
import re
from time import mktime
from datetime import datetime
import urllib.request




class myFeedParser:

    def __init__(self, url, topic):
        self.url = url
        self.topic = topic



    def parseFeed(self):

         d = feedparser.parse(self.url)
         if not d.entries:
             print("INVALID URL feed: {}".format(self.url))
             return None
         else:
             return d


    def getImage(self, link):

        try:
            opened_url = urllib.request.urlopen("{}".format(link))
        except:
            return 'NOT VALID URL'

        page = bs4.BeautifulSoup(opened_url, "html.parser")




        #il sole 24 ore

        div_img = page.find("div", {'class': 'opening'})
        if div_img is not None:
            img = page.find_all("img", {'class': 'img-responsive'})
            soup = bs4.BeautifulSoup(str(div_img), "html.parser")
            img = soup.find('img')
            if img is not None:
                src = img['src']
                if src != '':
                    return src
                else:
                    return 'NO IMAGE'



        #la stampa
        else:

            div_img = page.find("div", {'class': 'ls-articoloImmagine'})
            # print(type(div_img))
            if div_img is not None:
                soup = bs4.BeautifulSoup(str(div_img), "html.parser")
                img = soup.find('meta')
                if img is not None:
                    src = img['content']
                    return src
            else: #new version la stampa
                div_img = page.find("meta", {'property': 'og:image'})
                if div_img is not None:
                    soup = bs4.BeautifulSoup(str(div_img), "html.parser")
                    src = div_img['content']
                    if src is not None and src != '':
                        return src
                    else:
                        return 'NO IMAGE'

        return 'NO IMAGE'









    #esegue il fetch di un singolo feed e memorizza gli items nel db
    def fetchFeed(self):

        feed = self.parseFeed()
        news_list = []
        for newsitem in feed['items']:

            link = newsitem['link']
            if link is None or link == '':
                continue
            title = newsitem['title']
            if title is None or title == '':
                continue
            descr = newsitem['description']
            if descr is None or link == '':
                continue
            dt = newsitem['published_parsed']
            #print(pubDate)
            pubDate = datetime.fromtimestamp(mktime(dt))
            if pubDate is None:
                continue

            # getting img src from description
            soup = bs4.BeautifulSoup(descr, "html.parser")
            img = soup.find('img')
            if img is not None:
                src = img["src"]
            else:
                if 'thumbimage' in newsitem:
                    t = newsitem['thumbimage']
                    try:
                        src = t['url']
                    except TypeError:
                        src = 'NO IMAGE'


                else:
                    src = self.getImage(link)
                # #parsing site to get the img
                # if 'thumbimage' in newsitem:
                #     t = newsitem['thumbimage']
                #     src = t["url"]
                #
                # else:
                #
                #     src = 'NO IMAGE'


            # pulizia description

            clean_descr = self.clean_txt(descr)
            if clean_descr == '':
                clean_descr = 'NO DESCRIPTION'

            #pagina non esistente nel sito
            if src == 'NOT VALID URL':
                continue

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




