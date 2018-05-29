# -*- coding: utf-8 -*-
from datetime import datetime

from application import db

from flask_login import UserMixin

from flask import current_app

class Permission():
    HELP = 0x01
    USER_MANAGE = 0x02
    LOG_MANAGE = 0x04
    ADMINISTER = 0x80

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    admins = db.relationship('Admin', backref='role', lazy='dynamic')

    def __init__(self, name, permissions, default):
        self.name = name
        self.permissions = permissions
        self.default = default

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_role():
        #这里需要注意的是‘|’的用法，以及python对各种进制的处理
        roles = {
            'User': (Permission.HELP, True),
            'Administrator': (Permission.HELP | Permission.USER_MANAGE, False),
            'SeniorAdmin': (Permission.ADMINISTER, False),
            'SystemAdmin': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r, permissions=roles[r][0], default=roles[r][1])
            db.session.add(role)
        db.session.commit()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, uid, name, email):
        self.uid = uid
        self.name = name
        self.email = email
        if self.email == current_app.config['FLASK_ADMIN']:
            #验证email是否为设置的管理员的email
            self.role = Role.query.filter_by(permissions=0xff).first()
        else:
            self.role = Role.query.filter_by(default=True).first()
        #self.role_id = self.role.id

    def can(self, permissions):
        # 这个方法用来传入一个权限来核实用户是否有这个权限,返回bool值
        if current_app.config['LDAP_ENABLED']:
            return self.role is not None and \
                (self.role.permissions & permissions) == permissions
        else:
            return True

    def is_administrator(self):
        # 因为常用所以单独写成一个方法以方便调用
        return self.can(Permission.ADMINISTER)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(50))
    depart = db.Column(db.String(30))
    client = db.Column(db.String(50), unique=True)
    type = db.Column(db.String(30))  # web:通过网页添加  cmd:linux命令添加
    status = db.Column(db.Integer, default=0)  # 0:添加中  1.可用  2.添加失败 3.删除中 4.已删除
    send_status = db.Column(db.Integer, default=0)
    online = db.Column(db.Integer, default=0)  # 用户当前连接状态：0:未连接  1:已连接
    addtime = db.Column(db.DateTime)
    deltime = db.Column(db.DateTime)

    def __init__(self, name, email, depart, client, type, status):
        self.name = name
        self.email = email
        self.depart = depart
        self.client = client
        self.type = type
        self.status = status
        self.send_status = 0
        self.online = 0
        self.addtime = datetime.utcnow()

        # def __repr__(self):
        #     return '<User %r>' % self.name


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client = db.Column(db.String(50))
    trust_ip = db.Column(db.String(50))
    trust_port = db.Column(db.String(50))
    remote_ip = db.Column(db.String(50))
    status = db.Column(db.Integer, default=1)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    received = db.Column(db.String(500))
    sent = db.Column(db.String(500))

    def __init__(self, client, trust_ip, trust_port, remote_ip):
        self.client = client
        self.trust_ip = trust_ip
        self.trust_port = trust_port
        self.remote_ip = remote_ip
        self.status = 1
        self.start_time = datetime.utcnow()
