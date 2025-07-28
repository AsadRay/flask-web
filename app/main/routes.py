from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g,current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from langdetect import detect, LangDetectException
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from app.translate import translate
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.search import remove_from_index
from flask import abort
from app.main.forms import PostForm,DeletePostForm
from app.main.forms import MessageForm
from app.models import Message
from app.main import bp
from flask import Response
import json
from flask import send_file
from io import BytesIO
from fpdf import FPDF
from sqlalchemy import select
from app.models import Post
import pdfkit
from app import db



@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    delete_forms = {post.id: DeletePostForm() for post in posts.items}

    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url,delete_forms=delete_forms)


@bp.route('/explore')
@login_required
def explore():
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    delete_forms = {post.id: DeletePostForm() for post in posts.items}  # Use posts.items here!

    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url,delete_forms=delete_forms)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    delete_forms = {post.id: DeletePostForm() for post in posts.items}  # Use posts.items here!
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form,delete_forms=delete_forms)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    data = request.get_json()
    source_language = data.get('source_language', '').strip()
    if not source_language:
        source_language = None  # So translate() can omit 'from=' parameter
    
    return {'text': translate(data['text'], source_language='en', dest_language='bn')}


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    delete_forms = {post.id: DeletePostForm() for post in posts}

    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url,delete_forms=delete_forms)

from elasticsearch.exceptions import NotFoundError

@bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)

    if post.author != current_user:
        abort(403)  # Forbidden

    # Try to remove from Elasticsearch index
    try:
        remove_from_index('post', post)
    except NotFoundError:
        current_app.logger.warning(f"Post ID {post.id} not found in Elasticsearch index during delete.")
    except Exception as e:
        current_app.logger.error(f"Elasticsearch delete failed: {e}")

    # Delete from the database
    db.session.delete(post)
    db.session.commit()

    flash('Your post has been permanently deleted.')
    return redirect(url_for('main.index'))

@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = db.first_or_404(sa.select(User).where(User.username == recipient))
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    # current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    query = current_user.messages_received.select().order_by(
        Message.timestamp.desc())
    messages = db.paginate(query, page=page,
                           per_page=current_app.config['POSTS_PER_PAGE'],
                           error_out=False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/notifications/unread_message_count')
@login_required
def unread_message_count():
    return {'count': current_user.unread_message_count()}


@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
        flash(_('Export started. You will receive an email when done.'))
    # For ajax call, just return JSON to avoid redirect loop
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
   request.accept_mimetypes.accept_json:

        return {'status': 'started'}
    return redirect(url_for('main.user', username=current_user.username))

@bp.route('/export_posts/progress')
@login_required
def export_posts_progress():
    task = current_user.get_task_in_progress('export_posts')
    if task:
        progress = task.get_progress()
        return {'in_progress': True, 'progress': progress}
    return {'in_progress': False, 'progress': 100}

@bp.route('/download_posts')
@login_required
def download_posts():
    # Query posts belonging to current user, ordered by timestamp desc
    stmt = select(Post).where(Post.user_id == current_user.id).order_by(Post.timestamp.desc())
    posts = db.session.execute(stmt).scalars().all()  # Use db.session here

    # Prepare HTML content for PDF with better styling (you can customize further)
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; padding: 20px; }}
            h1 {{ color: #1f4037; }}
            p {{ margin: 10px 0; font-size: 14px; }}
            strong {{ color: #0b8457; }}
        </style>
    </head>
    <body>
        <h1>Posts by {current_user.username}</h1>
    """

    for post in posts:
        html_content += f"<p><strong>{post.timestamp.strftime('%Y-%m-%d %H:%M')}</strong>: {post.body}</p>"

    html_content += "</body></html>"

    # Convert HTML to PDF using pdfkit
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')  # Adjust path if necessary
    pdf = pdfkit.from_string(html_content, False, configuration=config)

    # Send PDF as download
    return send_file(
        BytesIO(pdf),
        mimetype='application/pdf',
        download_name='posts.pdf',
        as_attachment=True
    )
