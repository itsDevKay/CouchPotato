from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from hashlib import md5


class Entities(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 1
    name = db.Column(db.String(250)) # Unleashed
    thumbnail = db.Column(db.String(250)) # image url
    category_id = db.Column(db.Integer)
    eps = db.Column(db.Integer)
    isMovie = db.Column(db.Integer)
    videos = db.relationship('Video', backref='video', lazy='dynamic')
    url_title = db.Column(db.String(250))

    def __repr__(self):
        return '<User {}>'.format(self.name)



class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True) # unique image id
    name = db.Column(db.String(50))

    def __repr__(self):
        return '<Post {}>'.format(self.name)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True) # √
    title = db.Column(db.String(250)) # lower case url title √
    description = db.Column(db.String(9000)) # can skip for now
    video_src = db.Column(db.String(500))# video_src √
    video_src_main = db.Column(db.String(800))# video_src √
    isMovie = db.Column(db.Integer) # √
    upload_date = db.Column(db.DateTime, default=datetime.utcnow) # √
    release_date = db.Column(db.String(50)) # can skip for now
    views = db.Column(db.Integer) # √
    duration = db.Column(db.String(15)) # √
    season = db.Column(db.Integer) # √
    episode = db.Column(db.Integer) # √
    rating = db.Column(db.String(5))
    quality = db.Column(db.String(15))
    video_id = db.Column(db.Integer, db.ForeignKey('entities.id')) # how am i going to get this info

    def __repr__(self):
        return '<Post {}>'.format(self.title)
