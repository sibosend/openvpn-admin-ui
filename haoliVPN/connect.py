#!/data/www/current/haoliVPNEnv/bin/python
from application import db,create_app

from firstApp.models import Log
from firstApp.models import User
from datetime import datetime

import sys

app = create_app()
app.app_context().push()

if len(sys.argv) < 2:
    print "params error"

try:
    operate = sys.argv[1]
    if operate == 'connect':
        # insert log
        if len(sys.argv) < 6:
            print "params error"
            sys.exit()
        print sys.argv
        client = sys.argv[2]
        trust_ip = sys.argv[3]
        trust_port = sys.argv[4]
        remote_ip = sys.argv[5]

        log = Log(client, trust_ip, trust_port, remote_ip)
        db.session.add(log)
        user = User.query.filter_by(client=client).first()
        if user:
            user.online = 1
        db.session.commit()

    elif operate == 'disconnect':
        # update log
        if len(sys.argv) < 5:
            print "params error"
            sys.exit()
        print sys.argv
        client = sys.argv[2]
        bytes_received = sys.argv[3]
        bytes_sent = sys.argv[4]

        log = Log.query.filter_by(client=client).order_by(Log.id.desc()).first()
        if log:
            log.status = 0
            log.end_time = datetime.utcnow()
            log.received = bytes_received
            log.sent = bytes_sent
        else:
            print client + " exception connected " + ""

        user = User.query.filter_by(client=client).first()
        if user:
            user.online = 0
        db.session.commit()


except Exception, e:
    print e
