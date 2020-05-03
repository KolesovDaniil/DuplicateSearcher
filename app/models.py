from app.database import db


class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    fps = db.Column(db.Integer, nullable=False)

    hashed_video = db.relationship('VideoHash', backref='video', lazy='dynamic')

    video1 = db.relationship('Log', foreign_keys='Log.video1_id', backref='comp_video1',
                             lazy='dynamic')
    video2 = db.relationship('Log', foreign_keys='Log.video2_id', backref='comp_video2',
                             lazy='dynamic')


class VideoHash(db.Model):
    __tablename__ = 'video_hash'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    hash = db.Column(db.String, nullable=False)
    time_code = db.Column(db.String, nullable=False)


class Log(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    video1_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    time_code1 = db.Column(db.String, nullable=False)
    video2_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    time_code2 = db.Column(db.String, nullable=False)
