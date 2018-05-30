#!haoliVPNEnv/bin/python
# -*- coding: utf-8 -*-

from application import app,db,mail,create_app
from firstApp.models import User
from firstApp import utils
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy import or_

import thread
import time
import os
import subprocess

from daemon.runner import DaemonRunner
import logging
import logging.handlers

from flask_mail import Message

logger = None

class Scheduler(object):
    stdin_path = "/dev/null"
    stdout_path = os.path.join(app.config['BASE_DIR'], "scheduler.stdout")
    stderr_path =  os.path.join(app.config['BASE_DIR'], "scheduler.stderr")
    pidfile_path =  app.config['SCHEDULER_PID']
    pidfile_timeout = 5

    # 同步
    def synchronize(self):
        with app.app_context():
            openvpn_users = utils.get_users()  # 获取index.txt中所有用户
            if openvpn_users:
                clients = []
                for item in openvpn_users:  # 循环对比
                    client = item['client']
                    clients.append(client)
                    user = User.query.filter_by(client=client).first()
                    if user:
                        if user.status == item['status']:
                            continue
                        else:
                            user.status = item['status']
                            if item['status'] == 1:
                                user.addtime = datetime.utcnow()
                            elif item['status'] == 4:
                                user.deltime = datetime.utcnow()
                            db.session.commit()
                    else:
                        user = User(item['name'], item['email'], item['depart'], client, 'cmd', item['status'])
                        db.session.add(user)
                        db.session.commit()
                if len(clients) > 0:
                    delete_users = list(User.query.filter(User.client.notin_(clients)).all())
                else:
                    delete_users = list(User.query.all())
                for user_item in delete_users:
                    if user_item.status != 4:
                        db.session.delete(user_item)
                        utils.zip_delete(user_item.client)
                db.session.commit()
            else:
                logger.error('index.txt not exist')
                print 'index.txt not exist'

            if os.path.exists(app.config['CLIENT_VPN_HAOLI_DIR'] + '/crl.pem'):
                stdout = subprocess.check_output(app.config['CMD_REVOKE_FILE_COPY'], shell=True)
                if stdout:
                    logger.info('index.txt not exist')
                    print stdout

    def operate_user(self):
        with app.app_context():
            users = list(User.query.filter(or_(User.status.in_((0, 3)), and_(User.status == 1, User.send_status == 1))).all())
            for user in users:
                if user.status == 0:
                    status, log = utils.buildKey([user.name, user.client, user.email, user.depart])
                    lastlog = log[-1]
                    if status:
                        user.status = 1
                        user.send_status = 0
                        user.addtime = datetime.utcnow()
                        db.session.commit()
                        self.send_to_email(user)
                    else:
                        user.status = 2
                        user.addtime = datetime.utcnow()
                        db.session.commit()
                        logger.info(lastlog)
                        print lastlog

                elif user.status == 3:
                    status, log = utils.revoke(user.client)
                    lastlog = log[-1]
                    if status:
                        user.status = 4
                        user.deltime = datetime.utcnow()
                        db.session.commit()
                        utils.zip_delete(user.client)
                    else:
                        user.status = 1
                        db.session.commit()
                        logger.info(lastlog)
                        print lastlog

                elif user.status == 1 and user.send_status == 1:
                    user.send_status = 0
                    db.session.commit()
                    self.send_to_email(user)

                else:
                    continue

    def send_to_email(self, user):
        logger.info("send to emali")
        with app.app_context():
            status, output, password = utils.zip_compress(user.client)
            if status:
                if user.email:
                    msg = Message(u'OpenVPN连接', recipients = [user.email])
                    msg.body = app.config['MAIL_SUBJECT'] % password
                    with app.open_resource(output) as fp:
                        msg.attach(user.client + '.zip', "application/zip", fp.read())
                    mail.send(msg)
            else:
                logger.info(output)
                print output

# search users
    def schedule_run(self, threadName, delay):
        while True:
            global app
            app = create_app()
            self.operate_user()
            self.synchronize()
            time.sleep(delay)

    def run(self):
        global logger
        logger = logging.getLogger('Scheduler')
        logger.setLevel(logging.DEBUG)
        fh = logging.handlers.RotatingFileHandler(
            os.path.join(app.config['BASE_DIR'], "scheduler.log"), maxBytes=10000000,backupCount=5)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(u'%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        logger.info("start scheduler:")

        try:
            with app.app_context():
                thread.start_new_thread(self.schedule_run, ('haoliVPN', app.config['BACK_THREAD_SLEEP_TIME']))
        except:
            logger.error("Error: unable to start thread")
            print "Error: unable to start thread"

        while 1:
            pass


if __name__ == '__main__':
    run = DaemonRunner(Scheduler())
    run.do_action()
