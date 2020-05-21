'''
This was made to utilize requests sent from the site to my admin Email

Its simple, but not automated. It can definitely be upgraded in that way, but I
never got around to it.
'''

from app import Category, Entities, Video, db
import string

movieName = str(input("Enter Movie Name: "))
thumbnailImg = str(input("Enter Thumbnail Link: "))
categoryID = int(input("Enter Category ID: "))
episodeCount = int(input("Enter Episode Count: "))
isMovieOrNo = str(input("Is this a movie? [y=1/n=0]: "))
itemDescription = str(input("Enter Description of entity: "))
videoSource = str(input("Enter Video Source: "))
viewCount = 0
duration = str(input("Enter Duration: "))
season = int(input("Enter Season Number: "))
episode = int(input("Enter Episode Number "))
imdbRating = str(input("IMDb Rating: "))
quality = str(input("Movie Quality: "))

invalid_chars = [s for s in string.punctuation]

url_list = []
fixed_string = ''
for letter in movieName:
	if letter not in invalid_chars:
		fixed_string += letter.lower()


print(fixed_string)
print(fixed_string.split())

valid_url_string = '-'.join(fixed_string.split())
print(valid_url_string)


entity = Entities(name=movieName, thumbnail=thumbnailImg, category_id=categoryID, eps=int(episodeCount), isMovie=int(isMovieOrNo), url_title=valid_url_string)

db.session.add(entity)
db.session.commit()

e = Entities.query.filter(Entities.name == movieName).first()
entity_id = e.id
e.url_title = e.url_title + '-' + str(entity_id)
db.session.commit()


video = Video(title=movieName, description=itemDescription, video_src=videoSource, isMovie=int(isMovieOrNo), views=viewCount, duration=duration, season=season, episode=episode, rating=imdbRating, quality=quality, video_id=entity_id)

db.session.add(video)

db.session.commit()
