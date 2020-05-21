from flask import request, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from app import app, db
from app.models import Entities, Video, Category
from werkzeug.urls import url_parse
from datetime import datetime
import random
import requests as RE

import urllib.parse


'''
This was recreated so I could properly call the categories
based on what was given from the jinja2 templates
'''
GENRES = {
    'TV': 1,
    'COMEDY' : 2,
    'DRAMA' : 3,
    'HORROR' : 4,
    'HISTORY' : 5,
    'MUSICAL' : 6,
    'CRIME' : 7,
    'FANTASY' : 8,
    'BIOGRAPHY' : 9,
    'ADVENTURE' : 10,
    'ACTION' : 11,
    'DOCUMENTARY' : 12,
    'FAMILY' : 13,
    'WESTERN' : 14,
    'THRILLER' : 15,
    'SPORT' : 16,
    'MYSTERY' : 17,
    'ANIMATION' : 18,
    'ROMANCE' : 19,
    'SCI-FI' : 20,
    'XMAS' : 21,
    'WAR' : 22,
    'COSTUME' : 23,
    'KUNGFU' : 24,
    'SITCOM' : 25,
    'PSYCHOLOGICAL' : 26,
    'MYTHOLOGICAL' : 27
}
category_names_list = [x.name for x in Category.query.all()]


def send_simple_message(movie, email):
	return RE.post(
	   "https://api.mailgun.net/v3/sandbox7b4e11811d03b8d1b719b2abb8dd.mailgun.org/messages",
		auth=("api", "YOUR-API-KEY"),
		data={"from": "CouchPotato Movie Request <postmaster@sandbox11811d404603b8d1b719b2abb8dd.mailgun.org>",
			"to": "YOUR_NAME <YOUR_NAME@EMAIL.com>",
			"subject": "NEW MOVIE REQUEST",
			"text": "MOVIE REQUESTED: %s \nRETURN EMAIL: %s" % (movie, email)})
def send_bug_report(bug, email):
	return RE.post(
	   "https://api.mailgun.net/v3/sandbox7b4e1181103b8d1b719b2abb8dd.mailgun.org/messages",
		auth=("api", "YOUR-API-KEY"),
		data={"from": "CouchPotato Movie Request <postmaster@sandbox11811d404603b8d1b719b2abb8dd.mailgun.org>",
			"to": "YOUR_NAME <YOUR_NAME@EMAIL.com>",
			"subject": "NEW BUG SUBMISSION",
			"text": "BUG REPORT SUBMISSION: %s\n\nRETURN EMAIL: %s" % (bug, email)})


#entities = Entities.query.all()
#videos = Video.query.all()

@app.route('/')
@app.route('/all')
@app.route('/index')
def index():
    return render_template('index.html', all_categories=category_names_list)

@app.route('/tv')
def tvShowsOnly():
    return render_template('tv.html', all_categories=category_names_list)

@app.route('/movies')
def moviesOnly():
    return render_template('moviesOnly.html', all_categories=category_names_list)


'''
METHOD to generate a random entity based on the selector
from the first page. This method takes a little bit of time to load,
mostly due to SQLite3 rather than using MySQL
'''
@app.route('/get-random-item/<category>')
def getRandomCategory(category):
    if category != 'All Categories':
        categoryID = GENRES[category.upper()]
        random_entity_id = random.randrange(0, Entities.query.filter(Entities.category_id == categoryID).count())
        chosen_entity = Entities.query.filter(Entities.category_id == categoryID)[random_entity_id]
    else:
        random_entity_id = random.randrange(0, Entities.query.filter(Entities).count())
        chosen_entity = Entities.query.filter(Entities)[random_entity_id]
    resp = {
        'url_title': chosen_entity.url_title,
        'thumbnail': chosen_entity.thumbnail,
        'entity_name': chosen_entity.name,
        'entity_desc': chosen_entity.videos[0].description,
        'entity_rating': chosen_entity.videos[0].rating,
        'entity_duration': chosen_entity.videos[0].duration
    }
    return jsonify(resp)


@app.route('/entity/<entity>', methods=['GET','POST'])
def watch_entity(entity, bug_reported=None):
	bug = bug_reported
	query_string = request.query_string
	q = urllib.parse.unquote_plus(query_string.decode()).replace('bug_reported=','')
	if q == 'True' and request.method=='POST':
		bug = 'Your reported issue has been sent to our administrator. We will look into this immediately. Thanks!'
		report_body = request.form['exampleFormControlTextarea1']
		report_email = request.form['exampleFormControlInput1']
		#print(report_email)
		send_bug_report(report_body, report_email)

	results = db.session.query(Entities).filter(Entities.url_title == entity).first()
	tvShow = False
	if results.isMovie == 0: # a tv show
		tvShow = True
	return render_template('entity.html', results=results, tvShow=tvShow, bug_reported=bug)


@app.route('/alphabet/<letter>')
def alphabet(letter):
    results = Entities.query.filter(Entities.name.startswith(letter))[:42]
    for x in results:
        print('Result: ' + str(x))
    if len(results) == 0:
        return render_template('search.html', category_results=results, none_left=True, isAlpha=True, all_categories=category_names_list)
    return render_template('search.html', category_results=results, none_left=False, isAlpha=True, letter=letter, all_categories=category_names_list)


'''
This function is only ever called inside of the `search.html` template and called by AJAX
'''
@app.route('/load-more-alphabet/<letter>?index=<int:lastIndex>')
def loadMoreAlphabet(letter, lastIndex):
    results = Entities.query.filter(Entities.name.startswith(letter))[lastIndex:(lastIndex+42)]
    resp = []
    for x in results:
        resp.append({
            'entity_name': x.name,
            'entity_thumbnail': x.thumbnail,
            'entity_url': x.url_title,
            'last_index': (lastIndex+42)
        })
    if len(results) == 0:
        return jsonify('None Left')
    return jsonify(resp)


@app.route('/category/<entity_type>/<category>', methods=['GET'])
def categories(entity_type, category):
    category_item = Category.query.filter(Category.name.like('%'+category+'%')).first()
    if entity_type == 'all':
        results = Entities.query.filter(Entities.category_id == category_item.id)[:42]
    elif entity_type == 'tv':
        results = Entities.query.filter(Entities.category_id == category_item.id). \
                filter(Entities.isMovie == 0)[:42]
    elif entity_type == 'movie':
        results = Entities.query.filter(Entities.category_id == category_item.id). \
                filter(Entities.isMovie == 1)[:42]
    for x in results:
        print('Result: ' + str(x))
    if len(results) == 0:
        return render_template('search.html', category_results=results, entity_type=entity_type, none_left=True, genre=category, all_categories=category_names_list)
    return render_template('search.html', category_results=results, entity_type=entity_type, none_left=False, genre=category_item.name, all_categories=category_names_list)


'''
This function is only ever called inside of the `search.html` template and called by AJAX
'''
@app.route('/load-more-category/<entity_type>/<category>?index=<int:lastIndex>')
def loadMoreCategory(entity_type, category, lastIndex):
    if category:
        category_item = Category.query.filter(Category.name.like('%'+category+'%')).first()
        if entity_type == 'all':
            results = Entities.query.filter(Entities.category_id == category_item.id)[lastIndex:(lastIndex+42)]
        elif entity_type == 'tv':
            results = Entities.query.filter(Entities.category_id == category_item.id). \
                    filter(Entities.isMovie == 0)[lastIndex:(lastIndex+42)]
        elif entity_type == 'movie':
            results = Entities.query.filter(Entities.category_id == category_item.id). \
                    filter(Entities.isMovie == 1)[lastIndex:(lastIndex+42)]
        resp = []
        for x in results:
            print(x, x.isMovie)
            resp.append({
                'entity_name': x.name,
                'entity_thumbnail': x.thumbnail,
                'entity_url': x.url_title,
                'last_index': (lastIndex+42),
                'entity_type': entity_type
            })
        if len(results) == 0:
            return jsonify('None Left')
        return jsonify(resp)


@app.route('/search', methods=['GET','POST'])
def searchQuery():
	query = request.form.get('q')
	try:
		query_string = request.query_string
		q = urllib.parse.unquote_plus(query_string.decode()).replace('q=','')
		#print(query_string)
		print('Q: (' + str(q)+')')
		print('Query: (' + str(query_string.decode().replace('query=',''))+')')
		check_search = query_string.decode().replace('query=','')

		'''
		DO NOT LET USERS GENERATE A NO QUERY SEARCH, THERE ARE OVER
		20,000 ENTITIES TO LOAD. THE LOAD TIME WILL BE BEYOND EXTENSIVE AND
		COULD POSSIBLY CRASH OR FREEZE THE SERVER TEMPORARLIY, SLOWING DOWN,
		NOT ONLY FOR THE USER WHO WAS DUMB ENOUGH TO GIVE A NO QUERY SEARCH,
		BUT ALSO FOR ANY OTHER USERS ON THE SITE.
		'''
		if q == '' or q == ' ' or q == None:
			return render_template('search.html', error="Search cannot be blank. Please enter a valid search query.")
		else:
			results = db.session.query(Entities).filter(Entities.name.like('%'+q+'%')).all()
			#print(request.query_string)
			return render_template('search.html', search_results=results, isAlpha=False, query_string=q, all_categories=category_names_list)
	except TypeError as e:
		print(str(e))
		return render_template('base.html')


'''
This function is only ever called inside of the `search.html` template and called by AJAX
'''
@app.route('/search-entities', methods=['POST'])
def search():
	searchQuery = request.form['search']
	results = db.session.query(Entities).filter(Entities.name.like('%'+searchQuery+'%')).limit(20).all()
	resp = []
	for x in results:
		resp.append({
			'name': x.name,
			'id': x.id
		})
	return jsonify(resp)


@app.route('/request', methods=['GET','POST'])
def requestEntity():
	didSubmit = False
	if request.method=='POST':
		report_body = request.form['exampleFormControlTextarea1']
		report_email = request.form['exampleFormControlInput1']
		#print(report_email)
		send_simple_message(report_body, report_email)
		didSubmit = True
	return render_template('request-about.html', request_page=True, didSubmit=didSubmit)


@app.route('/about-us')
def aboutUs():
    return render_template('request-about.html', request_page=False)


'''
This is only necessary if you wish to add push notifications
from OneSignal. I used it to let people know when new movies were
added to the site.
'''
@app.route('/OneSignalSDKWorker.js')
@app.route('/OneSignalSDKUpdaterWorker.js')
def OneSignalSDK():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])
