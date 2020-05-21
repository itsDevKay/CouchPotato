import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from random import choice
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models, errors
from app.routes import Entities, Category, Video


'''
==================================
CATEGORY IDS
==================================
'''
GENRES = {
    'TV': 1, # [ ]            -
    'COMEDY' : 2, # [ ]       -
    'DRAMA' : 3, # [ ]        --
    'HORROR' : 4, # [ √ ]
    'HISTORY' : 5, # [ ]
    'MUSICAL' : 6, # [ ]      ?
    'CRIME' : 7, # [ ]        -
    'FANTASY' : 8, # [ √ ]
    'BIOGRAPHY' : 9, # [ ]    -
    'ADVENTURE' : 10, # [ √ ]
    'ACTION' : 11, # [ √ ]
    'DOCUMENTARY' : 12, # [ ] --
    'FAMILY' : 13, # [ ]      -
    'WESTERN' : 14, # [ ]
    'THRILLER' : 15, # [ ]    -
    'SPORT' : 16, # [ ]
    'MYSTERY' : 17, # [ ]     -
    'ANIMATION' : 18, # [ ]   -
    'ROMANCE' : 19, # [ ]     -
    'SCI-FI' : 20, # [ √ ]
    'XMAS' : 21, # [ ]
    'WAR' : 22, # [ ]
    'COSTUME' : 23, # [ ]
    'KUNGFU' : 24, # [ ]
    'SITCOM' : 25, # [ ]
    'PSYCHOLOGICAL' : 26, # [ ]
    'MYTHOLOGICAL' : 27 # [ ]
}
'''
==================================
CUSTOM JINJA2 FUNCTIONS
==================================

all these functions below are called inside the main templates
or inside the entity templates.
'''
def get_episodes(item):
    results = item.videos.all()
    if results[0].isMovie == 1:
        return 0
    return len(results)

'''
Be careful on how many you decide to allow through `limit(x)`,
the higher the number the longer it takes to load.
If you want to utilize a bigger number or an infinite scrolling, I would refer
to this blog [ https://pythonise.com/articles/infinite-lazy-loading ]
'''
def getFilmsByGenre(CATEGORY, entity_type):
    if entity_type == 'all':
        results = db.session.query(Entities).filter(Entities.category_id == GENRES[CATEGORY]).limit(20)
    elif entity_type == 'tv':
        results = db.session.query(Entities).filter(Entities.category_id == GENRES[CATEGORY]). \
                    filter(Entities.isMovie == 0).limit(20)
    elif entity_type == 'movie':
        results = db.session.query(Entities).filter(Entities.category_id == GENRES[CATEGORY]). \
                    filter(Entities.isMovie == 1).limit(20)
    if results.count() >= 20:
        r_range = 20
        print('found count:', r_range)
        return [results, r_range]

	'''
	Not all of the categories will have 20 entitites, if thats the case you should
	load the range up to the amount it has, whether that is 5 or 19
	'''
    r_range = results.count()
    return [results, r_range]


def getQualityOfEntity(item_id):
    results = db.session.query(Video).filter(Video.quality == item_id).first()
    return results


'''
So this method takes a bit of time to return based on how many seasons and episodes there are for an
entity.

This method actually gathers all the videos it has (some entities have over 200 episodes),
and takes note of the seasons and compares them to get the highest season.

This is used to separate the seasons into sections in the jinja2 templates.
'''
def getTotalSeasons(videos):
    highestSeason = 0
    for video in videos:
        if video.season > highestSeason:
            highestSeason = video.season
    return highestSeason


'''
This generally does the same as above except takes the season as an argument
and gets all the episodes in that season. It's generally quicker than the above
method, since it doesn't have to search as much as `getTotalSeasons`
'''
def getSeasonEpisodes(season, entity_id):
    query = db.session.query(Video).filter(Video.video_id == entity_id). \
            filter(Video.season == season)
    return query


'''
I wanted to add a Related Movies section so I created this function
to get entities based on the category of whatever they were watching.
'''
def getRelatedEntities(entity_category_id):
    results = db.session.query(Entities).filter(Entities.category_id == entity_category_id)
    amount_of_entities = [num for num in range(0, results.count())]
    try:
        return_results = [results[choice(amount_of_entities)] for item in range(0,20)]
    except IndexError:
        return_results = [results[choice(amount_of_entities)] for item in range(0, results.count())]

    return return_results


'''
This was a little confusing for me to get working and even still it's not 100% accurate
when it comes to episodes.

In order to get closest to the first season and first episode, I had to start not from 0,
but from a number I was sure no episode or season was. I chose 1000. I had to do the same thing
as `getTotalSeasons` except in reverse in order to generate that information.

Once again this method takes some time to complete because of the amount of searching it does.

This method is ran with:
`get_episodes`
`getTotalSeasons`
`getRelatedEntities`

So when it comes to loading tv shows, they generally load slower than loading a normal movie,
due to having to run more searches through the database.
'''
def getFirstVideo(entity_id):
    first_episode = 1000
    lowest_season = 1000
    query = db.session.query(Video).filter(Video.video_id == entity_id)
    for video in query:
        if video.season < lowest_season:
            lowest_season = video.season
    #print(lowest_season)
    query = db.session.query(Video).filter(Video.video_id == entity_id). \
            filter(Video.season == lowest_season)
    for video in query:
        if video.episode < first_episode:
            first_episode = video.episode
    #print(first_episode)
    query = db.session.query(Video).filter(Video.video_id == entity_id). \
            filter(Video.season == lowest_season).filter(Video.episode == first_episode).first()
    #print(query.episode, query.season)
    return query


'''
==================================
CONNECTION OF METHOD TO JINJA2
==================================
'''
app.jinja_env.auto_reload = True
app.jinja_env.globals.update(get_episodes=get_episodes)
app.jinja_env.globals.update(getFirstVideo=getFirstVideo)
app.jinja_env.globals.update(getFilmsByGenre=getFilmsByGenre)
app.jinja_env.globals.update(getTotalSeasons=getTotalSeasons)
app.jinja_env.globals.update(getSeasonEpisodes=getSeasonEpisodes)
app.jinja_env.globals.update(getRelatedEntities=getRelatedEntities)

'''
==================================
LOGGING
==================================
'''
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/couchpotato.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('CurbsiteTogo startup')
