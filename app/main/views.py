from flask import render_template,request,redirect,url_for,abort
from . import main
from .forms import PitchForm,UpdateProfile
from ..models import User, Role, Pitch,Like,Dislike
from flask_login import login_required, current_user
from .. import db,photos
from sqlalchemy import func
from sqlalchemy.orm import session


# Views
@main.route('/',methods = ['GET', 'POST'])
def index():

    '''
    View root page function that returns the index page and its data
    '''

    # Getting popular movie
    pickup_lines = Pitch.query.filter_by(category="pickup")
    interview = Pitch.query.filter_by(category = "interview")
    promotion = Pitch.query.filter_by(category = "promotion")

    # likes = Like.get_all_likes(pitch_id=Pitch.id)
    # dislikes = Dislike.get_all_dislikes(pitch_id=Pitch.id)

    title = 'Home - Welcome to The best pitch posting Website Online'
    return render_template('index.html', title = title, pickup_lines = pickup_lines, interview = interview, promotion = promotion)

@main.route('/user/<uname>')
@login_required
def profile(uname):
    user = User.query.filter_by(username = uname).first()
    get_pitches = Pitch.query.filter_by(user_id = User.id).all()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user, pitches_content = get_pitches)


@main.route('/user/<uname>/update',methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname=user.username))

    return render_template('profile/update.html',form =form)

@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/pitch/new',methods = ['GET','POST'])
@login_required
def new_pitch():
    '''
    View pitch function that returns the pitch page and data
    '''
    pitch_form = PitchForm()
    my_likes = Like.query.filter_by(pitch_id=Pitch.id)

    if pitch_form.validate_on_submit():
        content = pitch_form.content.data
        category = pitch_form.category.data
        pitch_title = pitch_form.pitch_title.data

        new_pitch = Pitch(pitch_title=pitch_title, content=content, category = category, user = current_user)
        new_pitch.save_pitch()

        return redirect(url_for('main.index'))


    title = 'New Pitch'
    return render_template('pitch.html', title = title, pitch_form = pitch_form, likes = my_likes)

@main.route('/pitch/<int:pitch_id>/comment',methods = ['GET', 'POST'])
@login_required
def comment(pitch_id):
    '''
    View comments page function that returns the comment page and its data
    '''
    # comment_form = CommentForm()

    comment_form = CommentForm()
    my_pitch = Pitch.query.get(pitch_id)
    if my_pitch is None:
        abort(404)

    if comment_form.validate_on_submit():
        comment_content = comment_form.comment_content.data

        new_comment = Comment(comment_content=comment_content, pitch_id = pitch_id, user = current_user)
        new_comment.save_comment()

        return redirect(url_for('.comment', pitch_id=pitch_id))

    all_comments = Comment.query.filter_by(pitch_id=pitch_id).all()
    title = 'Comments'

    return render_template('comment.html', title = title, pitch=my_pitch ,comment_form = comment_form, comment = all_comments )


@main.route('/pitch/<int:pitch_id>/like',methods = ['GET','POST'])
@login_required
def like(pitch_id):
    '''
    View like function that returns likes
    '''
    my_pitch = Pitch.query.get(pitch_id)
    user = current_user

    pitch_likes = Like.query.filter_by(pitch_id=pitch_id)


    if Like.query.filter(Like.user_id==user.id,Like.pitch_id==pitch_id).first():
        return  redirect(url_for('.index'))

    new_like = Like(pitch_id=pitch_id, user = current_user)
    new_like.save_likes()
    return redirect(url_for('.index'))

@main.route('/pitch/<int:pitch_id>/dislike',methods = ['GET','POST'])
@login_required
def dislike(pitch_id):
    '''
    View dislike function that returns dislikes
    '''
    my_pitch = Pitch.query.get(pitch_id)
    user = current_user

    pitch_dislikes = Dislike.query.filter_by(pitch_id=pitch_id)

    if Dislike.query.filter(Dislike.user_id==user.id,Dislike.pitch_id==pitch_id).first():
        return redirect(url_for('.index'))

    new_dislike = Dislike(pitch_id=pitch_id, user = current_user)
    new_dislike.save_dislikes()
    return redirect(url_for('.index'))

    