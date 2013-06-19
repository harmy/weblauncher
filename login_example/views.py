from flask import render_template, request, redirect, url_for, flash, session, abort
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from .models import User, db_session
from .forms import LoginForm
from . import app
import requests

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.teardown_request
def remove_db_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    zonelist = None
    if current_user.is_authenticated():
        r = requests.get('http://192.168.0.100/api/7c1e2648-cf39-11e2-a5db-080027880ca6/zones')
        if r.status_code == requests.codes.ok:
            zonelist = r.json()
    return render_template('index.html', form=LoginForm(), zonelist=zonelist)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.valid_password(form.password.data):
            if login_user(user, remember=form.remember.data):
                session.permanent = not form.remember.data
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash('This username is disabled!', 'error')
        else:
            flash('Wrong username or password!', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/play/<int:zoneid>')
@login_required
def play(zoneid):
    r = requests.get('http://192.168.0.100/api/7c1e2648-cf39-11e2-a5db-080027880ca6/auth?username={0}&zoneid={1}'.format(current_user.username, zoneid))
    gateinfo = r.json() if r.status_code == requests.codes.ok else None
    if gateinfo is None:
        return redirect(url_for('playerror', message=r.json()))
    return redirect(url_for('playok', **gateinfo))

@app.route('/play/ok')
@login_required
def playok():
    return '{0}'.format(request.args['token'])

@app.route('/play/error')
@login_required
def playerror():
    err_message = request.args['message'] or ''
    return 'error:{0}'.format(err_message)