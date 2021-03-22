import bleach  # secure against script injection by stripping html tags
from flask import (render_template, url_for, flash,
                   redirect, request, abort, current_app, Blueprint)
from flask_login import current_user, login_required
from sqlalchemy import exc

from flaskblog import db
from flaskblog.decorators import permission_required, moderator_required
from flaskblog.models import Post, Tag, Comment, Permission
from flaskblog.posts.forms import PostForm, CommentForm

posts = Blueprint('posts', __name__)


@permission_required(Permission.WRITE_ARTICLES)
@posts.route("/post/new", methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        cleaned_content = bleach.clean(form.content.data, tags = bleach.sanitizer.ALLOWED_TAGS + ['p'])
        create_post = Post(title = form.title.data, content = cleaned_content,
                           author = current_user._get_current_object())

        if form.tags.data[0]:
            for i in form.tags.data:
                tags = Tag(name = i)  # adds tag to TAG db Table
                create_post.tag.append(tags)  # adds tag to post_tag table with post id.

        db.session.add(create_post)
        db.session.commit()

        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title = 'New Post',
                           form = form, legend = 'New Post')


# for viewing a selected post and comments
@posts.route("/post/<int:post_id>", methods = ['GET', 'POST'])
def post(post_id):
    # get_or_404() method gets the post with the post_id and if it doesn't exist it returns a 404 error (
    # page doesn't exist)
    view_post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(body = form.body.data, post = view_post,
                          author = current_user._get_current_object())  # current_user._get_current_object()
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added', 'success')
        return redirect(url_for('.post', post_id = view_post.id, page = -1))

    page = request.args.get('page', 1, type = int)
    if page == -1:
        page = (view_post.comments.count() - 1) // current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1

    pagination = view_post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page = current_app.config[
        'FLASKY_COMMENTS_PER_PAGE'], error_out = False)
    comments = pagination.items

    return render_template('post.html', title = view_post.title, post = view_post, form = form, comments = comments,
                           pagination = pagination)


@posts.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
    post_update = Post.query.get_or_404(post_id)

    if post_update.author != current_user and not current_user.can(Permission.ADMINISTRATOR):
        abort(403)  # abort function is for showing the passed error page (error 403 - forbidden page)
    form = PostForm()
    if form.validate_on_submit():
        post_update.title = form.title.data
        post_update.content = bleach.clean(form.content.data, tags = bleach.sanitizer.ALLOWED_TAGS + ['p'])
        for i in form.tags.data:
            exists = db.session.query(db.exists().where(Tag.name == i)).scalar()
            if not exists:
                tags = Tag(name = i)  # adds tag to TAG db Table
                post_update.tag.append(tags)  # adds tag to post_tag table with post id.
        try:
            db.session.commit()
            flash('Your post has been updated!', 'success')
        except exc.IntegrityError:
            db.session.rollback()
            flash('Your post has been couldn\'t be updated!', 'warning')

        return redirect(url_for('posts.post', post_id = post_update.id))
    elif request.method == 'GET':
        form.title.data = post_update.title
        form.content.data = post_update.content
        tags = [x.name for i, x in enumerate(post_update.tag.all())]  # loop through all the tags and display them
        form.tags.data = tags

    return render_template('create_post.html', title = 'Update Post',
                           form = form, legend = 'Update Post')


@posts.route("/post/<int:post_id>/delete", methods = ['POST'])
@login_required
def delete_post(post_id):
    post_delete = Post.query.get_or_404(post_id)
    if post_delete.author != current_user:
        abort(403)  # abort function is for showing the passed error page (error 403 - forbidden page)
    db.session.delete(post_delete)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route('/moderate')
@login_required
@moderator_required
def moderate():
    form = CommentForm()
    page = request.args.get('page', 1, type = int)
    pagination = Comment.query.order_by(Comment.timestamp.asc()).paginate(page, per_page = current_app.config[
        'FLASKY_COMMENTS_PER_PAGE'], error_out = False)
    comments = pagination.items
    print(comments)
    return render_template('moderate_comments.html', comments = comments,
                           pagination = pagination, page = page, form = form)


@posts.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    # db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page = request.args.get('page', 1, type = int)))


@posts.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    # db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page = request.args.get('page', 1, type = int)))
