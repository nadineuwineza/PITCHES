from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin,db.Model):
    _tablename_ = 'users'
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255),unique = True,index = True)
    bio = db.Column(db.String(255))
    pass_word= db.Column(db.String(255))
    profile_pic_path = db.Column(db.String())
    photos = db.relationship('PhotoProfile',backref = 'user',lazy = "dynamic")
    pitch = db.relationship('Pitch', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref = 'user', lazy = 'dynamic')
    upvotes = db.relationship('Upvotes', backref = 'user', lazy = 'dynamic')
    downvotes = db.relationship('Downvote', backref = 'user', lazy = 'dynamic')

    @property
    def password(self):
        raise AttributeError('You cannot read the password attribute')

    @password.setter
    def password(self, password):
        self.pass_word = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.pass_word,password)


    def _repr_(self):
        return f'User {self.username}'

class PhotoProfile(db.Model):
    _tablename_ = 'profile_photos'

    id = db.Column(db.Integer,primary_key = True)
    pic_path = db.Column(db.String())
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))

class Pitch(db.Model):
    _tablename_='pitches'

    id = db.Column(db.Integer, primary_key=True)
    pitch_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    details= db.Column(db.String(), index=True)
    category = db.Column(db.String(255), nullable=False)
    comments = db.relationship('Comment',backref='pitch',lazy='dynamic')
    upvotes = db.relationship('Upvotes', backref = 'pitch', lazy = 'dynamic')
    downvotes = db.relationship('Downvote', backref = 'pitch', lazy = 'dynamic')

    def save_pitches(self):
        db.session.add(self)
        db.session.commit()
        
    @classmethod
    def getPitches(cls, id):
        pitches = Pitch.query.order_by(pitchId=id).desc().all()
        return pitches

    def _repr_(self):
        return f'Pitch {self.details}'

class Comment(db.Model):
    _tablename_='comments'
    id =db.Column(db.Integer, primary_key=True)
    pitches_id = db.Column(db.Integer, db.ForeignKey('pitch.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)
    details = db.Column(db.Text)

    def _repr_(self):
        return f'Comment: id:{self.id} comment: {self.details}'

class Upvotes(db.Model):
    _tablename_='upvotes'
    id = db.Column(db.Integer, primary_key=True)
    upvote = db.Column(db.Integer, default=0)
    pitches_id = db.Column(db.Integer,db.ForeignKey('pitch.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def save_upvotes(self):
        db.session.add(self)
        db.session.commit()


    def add_upvotes(cls,id):
        upvote_pitch = Upvotes(user = current_user, pitches_id=id)
        upvote_pitch.save_upvotes()

    
    @classmethod
    def get_upvotes(cls,id):
        upvote = Upvotes.query.filter_by(pitches_id=id).all()
        return upvote

    @classmethod
    def get_all_upvotes(cls,pitches_id):
        upvotes = Upvotes.query.order_by('id').all()
        return upvotes

    def _repr_(self):
        return f'{self.user_id}:{self.pitches_id}'

class Downvote(db.Model):
    _tablename_= 'downvotes'

    id = db.Column(db.Integer, primary_key=True)
    downvote =db.Column(db.Integer, default= 0)
    pitches_id = db.Column(db.Integer,db.ForeignKey('pitch.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def save_downvotes(self):
        db.session.add(self)
        db.session.commit()

    def add_downvotes(cls,id):
        downvote_pitch = Downvote(user = current_user, pitches_id=id)
        downvote_pitch.save_downvotes()

    
    @classmethod
    def get_downvotes(cls,id):
        downvote = Downvote.query.filter_by(pitches_id=id).all()
        return downvote

    @classmethod
    def get_all_downvotes(cls,pitches_id):
        downvote = Downvote.query.order_by('id').all()
        return downvote

    def _repr_(self):
        return f'{self.user_id}:{self.pitches_id}'