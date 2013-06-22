#coding=utf-8
from flask import render_template, request, redirect, url_for, flash, make_response
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from .models import User, db_session
from .forms import LoginForm
from . import app
import requests

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.teardown_request
def remove_db_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    zonelist = None
    zonechunks = None
    latest_zoneid = 1
    if current_user.is_authenticated():
        r = requests.get('http://192.168.0.100/api/7c1e2648-cf39-11e2-a5db-080027880ca6/zones')
        if r.status_code == requests.codes.ok:
            zonelist = r.json()
            latest_zoneid = zonelist[0]['zoneid']
            zonechunks = chunks(zonelist, 16)
    return render_template('index.html', form=LoginForm(), zonechunks=zonechunks, latest_zoneid=latest_zoneid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.valid_password(form.password.data):
            if login_user(user, remember=False):
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash(u'该账号已被封停!', 'error')
        else:
            flash(u'错误的账号或密码!', 'error')
    return render_template('index.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/play')
@login_required
def play():
    zoneid = request.args.get('zoneid', 1)
    r = requests.get('http://192.168.0.100/api/7c1e2648-cf39-11e2-a5db-080027880ca6/authorize?username={0}&zoneid={1}'.format(current_user.username, zoneid))
    gateinfo = r.json() if r.status_code == requests.codes.ok else None
    if gateinfo is None:
        flash(u'无法登录游戏，服务器返回错误信息：{0}'.format(r.json()['message']))
        return redirect(url_for('index'))
    return redirect(url_for('playok', **gateinfo))

@app.route('/play/ok')
@login_required
def playok():
    return '{0}'.format(request.args.get('token'))