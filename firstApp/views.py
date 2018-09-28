# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, session, g, flash, request, redirect, url_for, make_response, send_file
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
import json
from forms import AddUserForm, LoginForm

from models import User, Log, Admin, Permission
from application import db, mail, login_manager, ldap_mgr
#from settings import PER_PAGE, LDAP_ENABLED, BASE_DIR
from flask import current_app
from utils import permission_required, check_scheduler_status

import time
import os

firstApp_app = Blueprint('firstApp_app', __name__, template_folder='templates')

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)

@ldap_mgr.save_user
def save_user(username, userdata):
    admin = Admin.query.filter_by(uid=username).first()
    if admin is None:
        admin = Admin(username, userdata['name'].decode("utf-8"), userdata['email'].decode("utf-8"))
        db.session.add(admin)
    else:
        admin.name = userdata['name'].decode("utf-8")
        admin.email = userdata['email'].decode("utf-8")
    db.session.commit()
    return admin

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('firstApp_app.login'))

@firstApp_app.route('/')
@login_required
def index():
    return render_template('index.html')

@firstApp_app.route('/user_list')
@login_required
@permission_required(Permission.USER_MANAGE)
def user_list():
    # 获取所有user
    user_status = ['Creating', 'Valid', 'Crate failed', u'Deleting', u'Deleted', ]
    users = User.query.filter(User.status != 4).order_by(User.id.desc()).all()
    return render_template('user.html', users=users, user_status=user_status)

@firstApp_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # ldap认证
        login_user(form.user, remember=True)
        print "Valid"
        return redirect('/')
    else:
        print "Invalid"

    return render_template('login.html', form=form)

@firstApp_app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

@firstApp_app.route('/add_user', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USER_MANAGE)
def add_user():
    form = AddUserForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.name.data.encode('UTF-8').isalnum() and form.depart.data.encode('UTF-8').isalnum():
            strlist = form.email.data.split('@')
            hosts = strlist[1].split('.')
            if len(hosts) > 1:
                host = hosts[len(hosts) - 2]
            else:
                host = hosts[0]

            client = '-'.join([host, form.depart.data, form.name.data])
            user = User(form.name.data, form.email.data, form.depart.data, client, 'web', 0)
            db.session.add(user)
            db.session.commit()
            flash("Add user success！")
            return render_template('status.html')
        else:
            flash('Name and department must only consist of letters or numbers, please modify them!', 'danger')
            return render_template('status.html')

    else:
        return render_template('add_user.html', form=form)


@firstApp_app.route('/delete_user', methods=['POST'])
@login_required
@permission_required(Permission.USER_MANAGE)
def delete_user():
    client = request.values.get('client', 0)
    if client:
        user = User.query.filter_by(client=client).first()
        if user and user.status == 1:
            user.status = 3
            user.deltime = datetime.utcnow()
            db.session.commit()
            return json.dumps({'success': True})
        else:
            return json.dumps({'success': False, 'lastlog': 'User not exist!'})
    else:
        return json.dumps({'success': False, 'lastlog': 'User not exist!'})

@firstApp_app.route('/send_email', methods=['POST'])
@login_required
@permission_required(Permission.USER_MANAGE)
def send_email():
    client = request.values.get('client', '')
    if client:
        user = User.query.filter_by(client=client).first()
        user.send_status = 1
        db.session.commit()
        return json.dumps({'success': True})
    else:
        return json.dumps({'success': False, 'lastlog': 'User not exist!'})

@firstApp_app.route('/loglist')
@login_required
@permission_required(Permission.ADMINISTER)
def loglist():
    # 获取log list
    # page = request.values.get('page', 0)
    page = request.values.get('page', 1, type=int)
    startdate = request.values.get('startdate', '')
    enddate = request.values.get('enddate', '')
    status = request.values.get('status', '')
    title = request.values.get('title', '')
    keyword = request.values.get('keyword', '')
    data_query = Log.query.outerjoin(User, Log.client == User.client).add_entity(User)
    if startdate != '':
        utc_time = time.mktime(time.strptime(startdate, '%Y-%m-%d')) + time.timezone
        data_query = data_query.filter(Log.start_time >= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(utc_time)))
    if enddate != '':
        utc_time = time.mktime(time.strptime(enddate, '%Y-%m-%d')) + time.timezone
        data_query = data_query.filter(Log.start_time < time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(utc_time)))

    if status != '':
        status = int(status)
        data_query = data_query.filter(Log.status == status)

    if title != '' and keyword != '':
        if title == 'name':
            data_query = data_query.filter(User.name == keyword)
        elif title == 'client':
            data_query = data_query.filter(Log.client == keyword)

    pagination = data_query.order_by(Log.id.desc()).paginate(page, current_app.config['PER_PAGE'])
    loglist = pagination.items
    query_items = request.values.items()
    qs = ''
    for (key,item) in query_items:
        if key != 'page':
            qs += '&' + key + '=' + item
    return render_template('loglist.html', loglist=loglist, pagination=pagination, qs=qs)

@firstApp_app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@firstApp_app.errorhandler(403)
def page_no_permission(error):
    return render_template('403.html'), 403

@firstApp_app.context_processor
def app_permission():
    def can_admin(permission):
        return current_user.can(permission)
    return dict(can_admin=can_admin, permission=Permission)

@firstApp_app.route('/process')
@login_required
@permission_required(Permission.USER_MANAGE)
def process():
    result, number = check_scheduler_status()
    print result
    return render_template('process.html', scheduler=result, number=number)

@firstApp_app.route('/process/log')
@login_required
@permission_required(Permission.USER_MANAGE)
def process_log():
    url = current_app.config['SCHEDULER_LOG'];
    if os.path.exists(url):
        respnse = make_response(send_file(url))
        respnse.headers["Content-Disposition"] = "attament; filename=scheduler.log"
        return respnse
    else:
        flash('Log file does not exist', 'danger')
        return render_template('status.html')

@firstApp_app.route('/process/error')
@login_required
@permission_required(Permission.USER_MANAGE)
def process_error():
    url = current_app.config['SCHEDULER_ERROR'];
    if os.path.exists(url):
        respnse = make_response(send_file(url))
        respnse.headers["Content-Disposition"] = "attament; filename=scheduler.error"
        return respnse
    else:
        flash('Log file does not exist', 'danger')
        return render_template('status.html')
