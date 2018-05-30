# -*- coding: utf-8 -*-

import os

class DefaultConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY='============================'
    PERMANENT_SESSION_LIFETIMD = 60 * 60
    # flask wtf forms  settings
    WTF_CSRF_ENABLED = True
    # project settings
    PROJECT_SITE_NAME = u'OpenVPN VPN连接'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DB_DIR = '/data/www/haolivpn_db/'
    DB_FILE = 'haolivpn.db'
    DB_REPOSITORY = 'db_repository'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DB_DIR, DB_FILE)
    SQLALCHEMY_MIGRATE_REPO = os.path.join(DB_DIR, DB_REPOSITORY)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BACK_THREAD_SLEEP_TIME = 300    # 脚本线程sleep time： 300秒

    #Scheduler
    SCHEDULER_ERROR = os.path.join(DB_DIR, 'scheduler.stderr')
    SCHEDULER_LOG = os.path.join(DB_DIR, 'scheduler.log')
    SCHEDULER_PID = os.path.join(DB_DIR, 'scheduler.pid')

    # mail
    MAIL_DEBUG = False
    MAIL_USE_SSL = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'xxxxxxxxx'
    MAIL_PASSWORD = 'xxxxxxxxx'
    MAIL_DEFAULT_SENDER = (u"haoliVPN", "haoliVPN@qq.com")
    MAIL_SUBJECT = u'您申请了OpenVPN连接，附件是您的配置文件，解压密码是：%s'

    OPENVPN_DIR = '/etc/openvpn'
    EASY_RSA = '/etc/openvpn/easy-rsa'
    CLIENT_VPN_HAOLI_DIR = os.path.join(EASY_RSA, 'keys')
    CLIENT_VPN_HAOLI_CA = os.path.join(CLIENT_VPN_HAOLI_DIR, 'ca.crt')
    CLIENT_VPN_HAOLI_OVPN = os.path.join(BASE_DIR, 'installation/ovpn')

    CLIENT_VPN_HAOLI_LIST = os.path.join(CLIENT_VPN_HAOLI_DIR, "index.txt")
    CLIENT_VPN_HAOLI_IPP = os.path.join('/var/log/openvpn', "ipp.txt")

    CLIENT_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'installation/clients')

    # cmd / expect
    EXPECT_DIR = os.path.join(BASE_DIR, 'expect')
    EXPECT_BUILD_KEY = os.path.join(EXPECT_DIR, 'build-key.expect')
    EXPECT_REVOKE = os.path.join(EXPECT_DIR, 'revoke.expect')

    CMD_CHECKVPN = ['/usr/sbin/ifconfig', '/usr/bin/grep 1.1.1.1', '/usr/bin/wc -l']

    CMD_BUILD_KEY = ['cd ' + EASY_RSA, 'source ./vars', EXPECT_BUILD_KEY]
    CMD_REVOKE = ['cd ' + EASY_RSA, 'source ./vars', EXPECT_REVOKE]
    CMD_REVOKE_FILE_COPY = '/bin/cp ' + CLIENT_VPN_HAOLI_DIR + '/crl.pem' + ' ' + OPENVPN_DIR

    # Log Settings
    PER_PAGE = 20

    # bootstrap settings
    BOOTSTRAP_SERVE_LOCAL = True

    #admin
    FLASK_ADMIN = 'admin@qq.com'

    # LDAP验证是否可用
    LDAP_ENABLED = False

    # LDAP settings
    LDAP = {
        'URI': 'ldap://192.168.0.124:389',

        # This BIND_DN/BIND_PASSORD default to '', this is shown here for demonstrative purposes
        # The values '' perform an anonymous bind so we may use search/bind method
        'BIND_DN': 'uid=%(username)s,ou=haoli,dc=local,dc=openldap,dc=com',
        'BIND_AUTH': '',

        # Adding the USER_SEARCH field tells the flask-ldap-login that we areusing
        # the search/bind method
        #'USER_SEARCH': {'base': 'dc=openldap,dc=redmine,dc=com', 'filter': 'uid=%(username)s'},

        # Map ldap keys into application specific keys
        'KEY_MAP': {
            'uid': 'uid',
            'name': 'cn',
            'email': 'mail',
        },
        # LDAP connection options
        'OPTIONS': {
            'OPT_PROTOCOL_VERSION': 3,
        }
    }

class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    TESTING = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DB_DIR = '/data/www/haolivpn_db/'
    DB_FILE = 'haolivpn.db'
    DB_REPOSITORY = 'db_repository'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DB_DIR, DB_FILE)
    SQLALCHEMY_MIGRATE_REPO = os.path.join(DB_DIR, DB_REPOSITORY)

    OPENVPN_DIR = '/etc/openvpn'
    EASY_RSA = '/usr/share/easy-rsa/2.0'
    CLIENT_VPN_HAOLI_DIR = os.path.join(EASY_RSA, 'keys')
    CLIENT_VPN_HAOLI_CA = os.path.join(CLIENT_VPN_HAOLI_DIR, 'ca.crt')

    CLIENT_VPN_HAOLI_LIST = os.path.join(CLIENT_VPN_HAOLI_DIR, "index.txt")
    CLIENT_VPN_HAOLI_IPP = os.path.join(OPENVPN_DIR, "ipp.txt")

    EXPECT_DIR = os.path.join(BASE_DIR, 'expect')
    EXPECT_BUILD_KEY = os.path.join(EXPECT_DIR, 'build-key.expect')
    EXPECT_REVOKE = os.path.join(EXPECT_DIR, 'revoke.expect')

    CMD_CHECKVPN = ['/usr/sbin/ifconfig', '/usr/bin/grep 1.1.1.1', '/usr/bin/wc -l']

    CMD_BUILD_KEY = ['cd ' + EASY_RSA, 'source ./vars', EXPECT_BUILD_KEY]
    CMD_REVOKE = ['cd ' + EASY_RSA, 'source ./vars', EXPECT_REVOKE]
    CMD_REVOKE_FILE_COPY = '/bin/cp ' + CLIENT_VPN_HAOLI_DIR + '/crl.pem' + ' ' + OPENVPN_DIR

    FLASK_ADMIN = 'admin@qq.com'
    LDAP_ENABLED = False

class ProductionConfig(DefaultConfig):
    DEBUG = False
    TESTING = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DB_DIR = '/data/www/haolivpn_db/'
    DB_FILE = 'haolivpn.db'
    DB_REPOSITORY = 'db_repository'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DB_DIR, DB_FILE)
    SQLALCHEMY_MIGRATE_REPO = os.path.join(DB_DIR, DB_REPOSITORY)

    OPENVPN_DIR = '/etc/openvpn'
    EASY_RSA = '/etc/openvpn/easy-rsa'
    CLIENT_VPN_HAOLI_DIR = os.path.join(EASY_RSA, 'keys')
    CLIENT_VPN_HAOLI_CA = os.path.join(CLIENT_VPN_HAOLI_DIR, 'ca.crt')

    CLIENT_VPN_HAOLI_LIST = os.path.join(CLIENT_VPN_HAOLI_DIR, "index.txt")
    CLIENT_VPN_HAOLI_IPP = os.path.join('/var/log/openvpn', "ipp.txt")

    EXPECT_DIR = os.path.join(BASE_DIR, 'expect')
    EXPECT_BUILD_KEY = os.path.join(EXPECT_DIR, 'build-key.expect')
    EXPECT_REVOKE = os.path.join(EXPECT_DIR, 'revoke.expect')

    CMD_CHECKVPN = ['/usr/sbin/ifconfig', '/usr/bin/grep 1.1.1.1', '/usr/bin/wc -l']

    CMD_BUILD_KEY = ['cd ' + EASY_RSA, 'source ./vars', EXPECT_BUILD_KEY]
    CMD_REVOKE = ['cd ' + EASY_RSA, 'source ./vars', EXPECT_REVOKE]
    CMD_REVOKE_FILE_COPY = '/bin/cp ' + CLIENT_VPN_HAOLI_DIR + '/crl.pem' + ' ' + OPENVPN_DIR

    FLASK_ADMIN = 'admin@qq.com'
    LDAP_ENABLED = False

# if __name__=='__main__':
#     if len(sys.argv) <= 1:
#         settings = config['DefaultConfig']
#     else:
#         settings = config[sys.atgv[1] + 'Config']
