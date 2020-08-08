from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from JDiary.auth import login_required
from JDiary.database import get_db
from JDiary.util import page_util

import math

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    page = request.args.get("p", '')
    show_go_back = 0

    if page == '':
        page = 1
    else:
        page = int(page)
        if page > 1:
            show_go_back =1
    
    db = get_db()
    first_post = (int(page) - 1) * 10

    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ' LIMIT ?, 10',
        (first_post,)
    ).fetchall()

    pages = db.execute(
        'SELECT COUNT(id) AS total FROM post'
    ).fetchall()

    total = int(math.ceil(pages[0]['total'] / 10.0))

    page_range = page_util.get_page(total, page)
    data={
        'posts': posts,
        'p': int(page),
        'total': total,
        'show_go_back': show_go_back,
        'page_range': page_range
    }
    return render_template('blog/index.html', data=data)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title =request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Posts require a title'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES(?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id))
    db.commit()
    return redirect(url_for('blog.index'))