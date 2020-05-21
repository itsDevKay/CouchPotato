'''
This is my Harvester. This script, code, magic word machine or whatever you want to call it,
was designed to scrape the data from an online movie streaming website and add it directly to
a SQLite3 database.

The Harvester was specifically designed to take data from [ `https://123movie.movie` ] over time,
this website has changed so, as the movie website changes you should update the `base_url` and the
`url` at the bottom before the for loop to keep relevant.

However being that majority of all these movie websites are basically copy and pasted wordpress sites
or similar, they more or less follow the same CSS class and id names. If updating this code to work with
other sites that may differ. It shouldn't take much to change in order to work properly for others.
The only changes that would need to be made are the css using the bot variable that runs off of BeautifulSoup.

This is actually v3 of my original Harvester. This harvester was designed to integrate tv shows on top of just
movies. BECAUSE OF THIS. The database grew extremely huge. Back when I only harvested movies, my database consisted of
one table and around 7000 items. This new harvester grew to handle 3 tables (Category, Entities, Video) containing
over 20,000 entities, over 200,000 videos, and 21 categories using a relational database.


===================================== [ IMPORTANT NOTES ] =====================================
BECAUSE this grew so big on an SQLite3 database, it became a bit slower to run efficiently on a website.
My advice is to recreate and edit this for a MySQL database instead of an SQLite3 for performance.

You can however utilize AJAX and LazyLoading with `intersectionObserver`, I found a REALLY GREAT tutorial
on `https://pythonise.com/articles/infinite-lazy-loading`, however I never had the time to integrate that
into my templates.
'''
from bs4 import BeautifulSoup as Soup
from main import Entities, Category, Video, db
from stem.util import term
import requests, sys, string, traceback


'''
REPLACE THIS SYMBOL IMMEDIATELY !!!! - ( Ψ )

I noticed once when scraping that symbol was in a movie. Those don't properly encode to
html, I don't know what video it was, I just know i saw it.
'''

#https://123movie.movie/film/boruto-naruto-next-generations-season-1/watching.html?ep=1
# filters = /filter/movie/ || /filter/series/ || /filter/all/
base_url = 'https://123movie.movie'
watching_url = '/watching.html?ep=1' # without this, you can't receive the iframe src

# needed some global functions in order to make the id's work properly
entity_id = 0
category_id = 0

'''
Boolean function to determine if
element is a tv show or movie.
We will handle the two differently

TV shows on this particular site usually have a circle
surrounded by how many  episodes it has. We can find that in the
html and determine if it's a movie or a show.

===========
[NOTE]: some movies have that same circle with a 1. There isn't really
a way to determine if it's really a show or movie unless you want to
use api's like imdb or the like. I found those to be too slow, so I left it as is.
===========
'''
def isTvSeries(element):
	if x.find_all('span', class_='mli-eps'):
		return True
	return False


'''
Getting the poster is pretty straightforward, we first have to
sanitize it a bit to get rid of unecessary characters.

The url string starts off with `//example-url.com/entity-poster.jpg`
This is so the images are easy to use for http & https.

We need to place `https:` before the image string to get the correct path.
'''
def getElementPoster(element):
	thumbnail = ''
	for img in element:
		image, trash = str(img).split(');">')
		trash, image = image.split('url(')
		thumbnail = ('https:' + image)
	#print(thumbnail)
	return thumbnail


'''
getVideoDetails(info_details, keyword='Duration', genreElements=False)

[ element ]: On our source website, the entity info is split in two sections.
mvici-right & mvici-left. we created a 2 variables right before this
method is called inside of `grabVideos`.

[ keyword ]: Keyword is what we are specifically looking for:
Duration, Quality, IMDb, and Genre

[ genreElements ]: We really only need this for genre since
our genres have to be handled differently being that there are
usually multiple ones. (If you wanted to grab actors, you would do the same
more or less.) We will only use 1 genre tag so we use the index[0].
'''
def getVideoDetails(element, keyword, genreElements):
	value = ''
	try:
		for details in element[0]:
			if keyword in str(details):
				trash, value = details.text.split(keyword + ': ')
	except Exception:
		print(element, '\n\n\n\n\n\n\n')
	if not genreElements:
		return value

	value = value.replace('\n','').replace(',','').split()
	value = value[0] # grabbing the first element
	#print(value)
	return value


'''
This method pretty much replicates the same ideals as `addEpisodeToDatabase`
but in a much cleaner way since there is no need to add episodes and seasons.

For further details read `addEpisodeToDatabase` notes starting after (end sanitation method)
'''
def addMovieToDatabase(title, video_src, duration, description, quality, rating):
	global entity_id
	season = 0
	episode = 0
	results = Video.query.filter_by(title=title)
	if Video.query.filter_by(title=title).first() is None: # results.first().title:
		# if no element exists. Create new element and run again
		video = Video(title=title, description=description, video_src=video_src, \
				isMovie=1, release_date='', views=0, duration=duration, season=int(season), \
				episode=int(episode), rating=rating, quality=quality, video_id=int(entity_id)
				)
		db.session.add(video)
		db.session.commit()
		#Video.query.filter_by(title=title).first().video_id = entity_id
		db.session.commit()
		print(term.format(term.format('[√] ', term.Color.GREEN) + 'Successfully added >> [ ' + title + ' ] << to the database.', term.Attr.BOLD))
		#addEpisodeToDatabase(title, episode, video_src, duration, description, quality, rating)
	else:
		Video.query.filter_by(title=title).first().video_id = entity_id
		return



'''
=======================================================================================================
[ WARNING ]: This method is extremely messy! I got irritated as I had to keep rerunning and rerunning
so I hardcoded the fixes in here. As new movies come out, you'll probably have to keep adding more
hard coded solutions.

A quick fix to make this simpler from the top of my head would be to create a global list[]
(ex. `trash_strings = []`) and insert all the strings that need to be replaced inside of it.
Once you've done that, you'd need to run possibly a loop to check if any of those exist inside of the
episode entity and replace it with nothing (ex. -> '')

+++++++++++++++++++++++++++++++++++
Some of the seasons as you'll see below didn't actually have it placed in the string,
because of this I just made an assumption that it was season 1. So it might and might not always
be entirely correct.
+++++++++++++++++++++++++++++++++++
=======================================================================================================

This function aims to santize the remaining issues and add the episode entity or movie entity into it's
proper place and connect it properly with the category and the entity.
'''
def addEpisodeToDatabase(title, episode, video_src, duration, description, quality, rating):
	global entity_id
	video_title = title

	# ===================== START SANITATION METHOD ===============================================
	try: video_title = title.lower().replace('season premiere', '')
	except: print(term.format('\n\nERROR STRING: ' + title + '\n\n', term.Color.RED)); sys.exit(0)

	try: trash, season = video_title.lower().split('season ', 1)
	except:
		try:
			if video_title.lower() == 'ruler: master of the mask: episode 32':
				video_title = video_title.lower().replace(': episode 32','')
		except: print(term.format('\n\nERROR STRING: [line 92] | ' + video_title + '\n\n', term.Color.RED)); print(traceback.format_exc()); sys.exit(0)

	try: season, trash = season.split(' ', 1)
	except:
		try:
			if season == '1episode4':
				season = ('1')
			season = int(season)
		except UnboundLocalError: season = ''
		except:
			print(term.format('\n\nERROR STRING: [line 89] | ' + season + '\n\n', term.Color.RED)); print(traceback.format_exc()); sys.exit(0)

	season = str(season).replace(' ','')

	try:
		season, trash = season.lower().split('epi', 1)
		season, trash = season.split(':', 1).replace('.','').replace(',','')
		season = season.replace(':','').replace('upright','')
	except: pass
	season = season.replace('-','').replace(' ','').replace('with','').replace(';','')
	season = season.replace('(2017)', '').replace('.','').replace(',','').replace('/','')
	season = season.replace(':','').replace('upright','').replace('tonight','')
	season = season.replace('\\','')
	if season == ' ' or season == '' or (season == 'bladers'): season = 0
	if season == '1v': season = 1
	# ======================== END SANITATION METHOD ===============================================


	results = Video.query.filter_by(title=title)

	# if our video doesn't exist, we need to add it to our database and assign an `entity_id`
	if Video.query.filter_by(title=title).first() is None:

		# if no element exists. Create new element and run again
		video = Video(title=title, description=description, video_src=video_src, \
				isMovie=0, release_date='', views=0, duration=duration, season=int(season), \
				episode=int(episode), rating=rating, quality=quality, video_id=int(entity_id)
				)

		'''
		Initially I had some issues with getting the `entity_id` to actually stick.
		During my testing I found that It would show up empty which was annoying.
		I found I had to add the video first and commit it.

		I'm not sure why I have to commits, as I don't actually comment my code as I type.
		But for the purpose of not breaking anything, I'm going to leave it.
		Feel free to edit and test it.
		'''
		db.session.add(video)
		db.session.commit()
		#Video.query.filter_by(title=title).first().video_id = entity_id
		db.session.commit()
		print(term.format(term.format('[√] ', term.Color.GREEN) + 'Successfully added >> [ ' + title + ' ] << to the database.', term.Attr.BOLD))
		#addEpisodeToDatabase(title, episode, video_src, duration, description, quality, rating)
	else:
		Video.query.filter_by(title=title).first().video_id = entity_id
		return


'''
Takes the category as an argument. Checks to see if the category
already exists inside the database. If it does. Then it will return
the categories Id.
If it doesn't exist, it will create the category and rerun this function.
'''
def checkForCategoryId(category):
	global category_id
	results = Category.query.filter(Category.name.like('%'+category+'%')).first()
	try:
		if results.name:
			category_id = results.id
			return
	except AttributeError:
		# if no element exists. Create new element and run again
		print(term.format('\t[-] No Category named [ ' + category + ' ] | Adding to Database Now', term.Color.YELLOW))
		genre = Category(name=category)
		db.session.add(genre)
		db.session.commit()
		print(term.format('\t\t[-] Successfully added [ ' + category + ' ] to Database', term.Attr.BOLD))
		checkForCategoryId(category)


'''
Takes the entity as an argument. Checks to see if the entity
already exists inside the database. If it does. Then it will return
the entity's ID.
If it doesn't exist it will create the entity with the
proper elements and rerun this function.
'''
def checkForEntities(entity, thumbnail, category_id):
	global entity_id
	results = Entities.query.filter_by(name=entity)
	try:
		if results.first().name:
			entity_id = results.first().id
			return
	except AttributeError:
		# if no element exists. Create new element and run again
		print(term.format('\t[-] No Entity named [ ' + entity + ' ] | Adding to Database Now', term.Color.YELLOW))
		series = Entities(name=entity, thumbnail=thumbnail, category_id=category_id)
		db.session.add(series)
		db.session.commit()
		print(term.format('\t\t[-] Successfully added [ ' + entity + ' ] to Database', term.Attr.BOLD))
		checkForEntities(series.name, series.thumbnail, series.category_id)


'''
This method consist of mostly sanitation methods
to get rid of unecessary strings. It'll make it easier to
call it from the database if all of these are the exact same.

will return elements id location in the database
'''
def addEntityToDatabase(name, thumbnail, category, isMovie=False):
	global entity_id
	global category_id
	try: # try/except clause is to prevent failure if none or some of these existed
		if not isMovie:
			try: name = name.replace('Season Premiere', '')
			except: pass

			try: title, season = name.split(' - Season ', 1)
			except:
				try: title, trash = name.split(' Epi', 1)
				except:
					try:
						title, trash = name.split(' epi', 1)
					except: title = name
				#print(term.format('\n\nERROR STRING: [line 185] | ' + name + ' | ' + str(isMovie) + '\n\n', term.Color.RED))
			#title, crap = title.split(' - ')


			# read checkForCategoryId method for details
			# read checkForEntities method for details
			checkForCategoryId(category)
			checkForEntities(title, thumbnail, category_id)
		else:
			checkForCategoryId(category)
			checkForEntities(name, thumbnail, category_id)
	except ValueError as e:
		#print(name)
		print(term.format('\n\nERROR STRING: [line 189] | ' + name + ' | ' + str(isMovie) + '\n\n', term.Color.RED)); print(traceback.format_exc());
		#sys.exit(0)

	return entity_id


'''
Once we have the entity to harvest from, we gather all the necessary
elements to place inside our database.
[ TITLE, EPISODE, SEASON, DURATION ]

These entities are sometimes mixed in with a whole bunch of special
characters. They will later need to be sanitized with another function.
'''
def grabVideos(show_url, isMovie):
	global entity_id
	global category_id
	page = requests.get(show_url).content
	bot = Soup(page, 'html.parser')

	# read getVideoDetails method for details
	info_details = bot.find_all('div', class_='mvici-right')
	categories = bot.find_all('div', class_='mvici-left')
	duration = getVideoDetails(info_details, keyword='Duration', genreElements=False)
	quality  = getVideoDetails(info_details, keyword='Quality', genreElements=False)
	rating   = getVideoDetails(info_details, keyword='IMDb', genreElements=False)
	category = getVideoDetails(categories, keyword='Genre', genreElements=True)

	# read getElementPoster method for details
	poster_img = bot.find_all('div', class_='thumb mvic-thumb')
	thumbnail = getElementPoster(poster_img)

	'''
	the description lies inside it's own `div`, so it's easier to retrieve.
	There are some characters that need to be sanitized before it's ready as
	you'll see below.
	'''
	description = ''
	for x in bot.find_all('div', class_='desc'):
		desc = x.text
		description = desc.replace('"', "'")
	description = description.replace('\n            ','')
	description = description.replace('        ','')


	'''
	Here we are grabbing the server location for the very main server.
	This site has other server locations, but I decided to focus only
	on the first loaded one, which I assumed is the main server.
	'''
	server = bot.find('div', {'id': 'server-9'})
	for x in (server.find_all('div', class_='les-content')):
		'''
		If we are scraping a tv show then we will collect server
		locations for every episode available.
		'''
		if not isMovie:
			for ep in (x.find_all('a', class_='btn-eps')):
				title     = (ep['title'])
				episode   = (ep['episode-data'])
				video_src = ('https:' + ep['player-data'])

				'''
				[ `addEntityToDatabase` ] must be ran first before [ `addEpisodeToDatabase` ]
				or else the episode will belong to itself and you would have X amount of different entities
				vs 1 entity with X amount of episodes
				'''
				# read addEntityToDatabase method for details
				# read addEpisodeToDatabase method for details
				addEntityToDatabase(title, thumbnail, category, isMovie=False)
				addEpisodeToDatabase(title, int(episode), video_src, duration, description, quality, rating)

		# rules for dealing with movies
		else:
			for video in (x.find_all('a', class_='btn-eps')):
				title     = video['title']
				video_src = ('https:' + video['player-data'])

				# read addEntityToDatabase method for details
				# read addMovieToDatabase method for details
				addEntityToDatabase(title, thumbnail, category, isMovie=True)
				addMovieToDatabase(title, video_src, duration, description, quality, rating)



'''
Depending on how many pages you wish to harvest from will depend on what number to end with

for the first 500 pages you would use
`range(1, 501)`

The great thing about it, is that if you already have scraped the 500 pages before,
it would skip what it has already done and only page attention to what it has
'''
#https://123movie.movie/film/boruto-naruto-next-generations-season-1/watching.html?ep=1
# filters = /filter/movie/ || /filter/series/ || /filter/all/
url = 'https://123movie.movie/movie/filter/all/all/all/all/all/latest/?page='
for page_num in range(1, 3):
	page = requests.get( url+str(page_num) ).content
	bot = Soup(page, 'html.parser')

	print(term.format('\n\n[-] Starting Data harvest page [ ', term.Color.GREEN) + term.format(str(page_num), term.Attr.BOLD)+ term.format(' ]\n\n', term.Color.GREEN))

	# finding the links on the main page and getting the url to the movie/show
	for x in bot.find_all('a', class_='ml-mask jt'):
		isTvShow = isTvSeries(x) # checks if entity is a TV Show or Movie
		video_url = (base_url + x['href'] + watching_url)

		if isTvShow:
			grabVideos(video_url, isMovie=False)

		elif not isTvShow:
			grabVideos(video_url, isMovie=True)
