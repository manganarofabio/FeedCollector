from pony import orm
from pony.orm import db_session
import datetime
from urls import rss

def define_database_and_entities(**db_params):
    #db = orm.Database(**db_params)
    db = orm.Database()


    class Url(db.Entity):
         link = orm.PrimaryKey(str)
         topic = orm.Required(str)



    class Item(db.Entity):
        link = orm.PrimaryKey(str)
        title = orm.Required(str)
        descr = orm.Optional(str)
        pubDate = orm.Required(datetime.datetime)
        img = orm.Optional(str)
        topic = orm.Required(str)

    db.bind(**db_params)
    db.generate_mapping(create_tables=True)
    return db

@db_session
def urls_populate_db(db, rss):

    for cat in rss.keys():
        for url in rss[cat]:
            url = db.Url(link=url, topic=cat)
            db.commit()


