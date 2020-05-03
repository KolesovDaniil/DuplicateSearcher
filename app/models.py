from app.database import db


class Video(db.Model):

    __tablename__ = 'video'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    video_name = db.Column(db.String, nullable=False)
    video_url = db.Column(db.String, nullable=False)

    hashed_video = db.relashionshap('VideoHash', backref='hash', dynamic='lazy')
    compared_video1 = db.relashionshap('Log', backref='comp_video1', dynamic='lazy')
    compared_video2 = db.relashionshap('Log', backref='comp_video2', dynamic='lazy')


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


