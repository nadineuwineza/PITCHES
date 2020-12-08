from flask import render_template,request,redirect,url_for,abort, flash, abort
from . import main
from flask_fontawesome import FontAwesome
from .. import db, photos
from flask_login import login_required, current_user
from ..models import User, Pitch, Comment, Upvotes,Downvote, PhotoProfile
from .forms import AddPitch, UpdateProfile, CommentsForm, UpvoteForm,DownvoteForm
from flask.views import View, MethodView
import markdown2

@main.route('/', methods=['GET', 'post'])
def index():
   pitch = Pitch.query.filter_by().first()
   promotion = Pitch.query.filter_by(category='promotion')
   interview = Pitch.query.filter_by(category='interview')
   product = Pitch.query.filter_by(category='product')
   pickuplines =Pitch.query.filter_by(category='pickuplines')
   title = 'pitches'
   
   upvotes = Upvotes.get_all_upvotes(pitches_id=Pitch.id)

   return render_template('index.html', title=title,upvotes=upvotes, promotion=promotion, product= product, interview=interview, pickuplines=pickuplines)

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user)

@main.route('/user/<uname>/update', methods=['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username= uname).first()
    if user is None:
        abort(404)
    form = UpdateProfile()
    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile', uname=user.username))
    return render_template('profile/update.html', form=form)

@main.route('/user/<uname>/update/pic', methods=['POST'])
@login_required
def update_pic(uname):
    user= User.query.filter_by(username=uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        user_photo = PhotoProfile(pic_path = path,user = user)
        db.session.commit()
    return redirect(url_for('main.profile', uname=uname))

@main.route('/pitches/new/', methods= ['GET','POST'])
@login_required
def new_pitch():
    form = AddPitch()
    upvotes = Upvotes.query.filter_by(pitches_id=Pitch.id)
    if form.validate_on_submit():
        details= form.details.data
        pitch_id =current_user
        category = form.category.data
        print(current_user._get_current_object().id)
        new_pitches = Pitch(pitch_id=current_user._get_current_object().id, details=details, category=category)
        new_pitches.save_pitches()

        return redirect(url_for('main.index'))

    return render_template('pitching.html', form=form)

@main.route('/comment/new/<int:pitches_id>', methods=['GET','POST'])
@login_required
def add_comment(pitches_id):
    form = CommentsForm()
    pitch = Pitch.query.get(pitches_id)
    if form.validate_on_submit():
        details= form.details.data
        add_comment= Comment(details=details, user_id=current_user._get_current_object().id, pitches_id=pitches_id)
        db.session.add(add_comment)
        db.session.commit()

        return redirect(url_for('.add_comment', pitches_id=pitches_id))
    allComents= Comment.query.filter_by(pitches_id=pitches_id).all()
    return render_template('comment.html',form=form, allComents=allComents,pitch =pitch)

@main.route('/pitch/upvote/<int:pitches_id>/upvote', methods=['GET', 'POST'])
@login_required
def upvote(pitches_id):
    pitch = Pitch.query.get(pitches_id)
    user = current_user
    p_upvotes =Upvotes.query.filter_by(pitches_id=pitches_id)

    if Upvotes.query.filter(Upvotes.user_id==user.id, Upvotes.pitches_id==pitches_id).first():
        return redirect(url_for('main.index'))

    newUpvote = Upvotes(pitches_id=pitches_id, user=current_user)
    newUpvote.save_upvotes()
    return redirect(url_for('main.index'))



@main.route('/pitch/downvote/<int:pitches_id>/downvote', methods=['GET','POST'])
@login_required
def downvote(pitches_id):
    pitch= Pitch.query.get(pitches_id)
    user = current_user
    douwnVotes= Downvote.query.filter_by(pitches_id=pitches_id)

    if Downvote.query.filter(Downvote.user_id==user.id, Downvote.pitches_id==pitches_id).first():
        return redirect(url_for('main.index'))

    newDownvote = Downvote(pitches_id=pitches_id, user=current_user)
    newDownvote.save_downvotes()
    return redirect(url_for('main.index'))