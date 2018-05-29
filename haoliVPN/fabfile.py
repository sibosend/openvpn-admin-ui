# -*- coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import local, run, put, settings, abort, env, cd, prefix
from contextlib import contextmanager

import os
import config
#from settings import DB_DIR, DB_FILE

RELEASE_PATH = './../'
ZIP_NAME = 'openvpn-admin-ui'
EXCLUDE_LIST = ['.idea/\*', '.git/\*', 'haoliVPNEnv/\*', 'haolivpn.db', 'fabfile.py']
TO_DIR = '/data/www/'
SERVER_ENV = 'production'         #发布环境(development/production)
UWSGI_ENV = "default"              #服务器uwsgi运行环境(development/production/default)
DB_DIR = config.DefaultConfig.DB_DIR
DB_FILE = config.DefaultConfig.DB_FILE

env.use_ssh_config = True

def pre_local_test():
    with settings(warn_only=True):
        result = local('git --version')
        if result.failed:
            abort("Please install git.")
        result = local('zip -v')
        if result.failed:
            abort("Please install zip.")


def pre_remote_test():
    with settings(warn_only=True):
        result = run('python --version')
        if result.failed:
            abort("Please install python.")
        result = run('pip --version')
        if result.failed:
            abort("Please install pip.")
        result = run("unzip -v")
        if result.failed:
            abort("Please install unzip.")
        result = run("virtualenv --version")
        if result.failed:
            abort("Please install virtualenv")

def git_pull_from_tag(tag):
    local("git checkout tags/" + tag)

def zip_files(file_name):
    #local("rm " + file_name)
    if os.path.exists(file_name):
        local("rm " + file_name)
    exclude_file = ' '.join(EXCLUDE_LIST)
    local("zip -r0 --quiet " + file_name + " ./ --exclude " + exclude_file)

def upload(local_file, to_dir):
    put(local_file, to_dir)



def unzip_file(file_path, to_path):
    run("rm -r " + to_path, warn_only=True)
    run("unzip -q "+ file_path + " -d " + to_path)


def git_reset_to_master():
    local("git checkout master")

def virtualenv(name):
    run("virtualenv " + name)

@contextmanager
def act_virtualenv(name):
    with prefix("source ./"+name+"/bin/activate"):
        yield

def install(name):
    with act_virtualenv(name):
        run("pip install uwsgi")
        run("pip install flask==0.12.4")
        run("pip install flask-bootstrap")
        run("pip install flask-script")
        run("pip install flask-moment")
        run("pip install pyminizip==0.2.1")
        run("pip install flask_wtf")
        run("pip install flask_sqlalchemy")
        run("pip install sqlalchemy-migrate")
        run("pip install flask-mail")
        run("pip install flask-login")
        run("pip install flask-ldap-login")
        run("pip install python-ldap")
        run("pip install python-daemon")

def prepare_deploy(name):
    virtualenv(name)
    install(name)

def local_prepare(tag, zip_file_name):
    pre_local_test()
    if SERVER_ENV == 'production':
        git_pull_from_tag(tag)
    zip_files(zip_file_name)
    if SERVER_ENV == 'production':
        git_reset_to_master()

def run_db_create():
    run("mkdir " + DB_DIR, warn_only=True)
    run("chmod 777 " + DB_DIR)
    run("chmod +x ./db_create.py")
    run("DEPLOY_TARGET=" + UWSGI_ENV + " ./db_create.py")

def run_db_migrate():
    run("chmod +x ./db_migrate.py")
    run("DEPLOY_TARGET=" + UWSGI_ENV + " ./db_migrate.py")

def deploy_to_remote(tag="development", name="haoliVPNEnv"):
    zip_file_name = ZIP_NAME + "_" + tag;
    zip_file = zip_file_name + '.zip';
    local_prepare(tag, RELEASE_PATH + zip_file)
    pre_remote_test()
    upload(RELEASE_PATH + zip_file, TO_DIR)
    unzip_file(TO_DIR + zip_file, TO_DIR + zip_file_name)
    with cd(TO_DIR + zip_file_name):
        prepare_deploy(name)
        result = run("find " + DB_DIR + ' -name ' + DB_FILE, warn_only=True)
        print(result)
        if result.failed:
            run_db_create()
        else:
            run_db_migrate()
        run("chmod -R +x ./*")
        run("chmod 766 " + DB_DIR + DB_FILE)
        run("chmod 777 " + TO_DIR + zip_file_name)
        run("sudo /etc/init.d/uwsgi-vpn-admin stop")
        run("sudo rm /etc/init.d/uwsgi-vpn-admin", warn_only=True)
        run("sudo ./scheduler.py stop", warn_only=True)
        run("sed -i -e s/__UWSGI_TARGET__/" + UWSGI_ENV + "/g haoliVPN.ini")
        run("rm -rf " + TO_DIR + "current", warn_only=True)
        run("ln -s " + TO_DIR + zip_file_name + " " + TO_DIR + "current")
        run("sudo cp -f ./uwsgi-vpn-admin /etc/init.d/")
        run("sudo chmod +x /etc/init.d/uwsgi-vpn-admin")
        run('set -m; '+ "sudo " + "DEPLOY_TARGET=" + UWSGI_ENV +  ' ./scheduler.py start')
        run("sudo /etc/init.d/uwsgi-vpn-admin start")

#production Env
def production():
    global SERVER_ENV, UWSGI_ENV, DB_DIR, DB_FILE
    env.hosts = ['haoli-normal-06-vpn-dns']
    env.user = 'haoli'
    SERVER_ENV = 'production'
    UWSGI_ENV = 'production'
    DB_DIR = config.ProductionConfig.DB_DIR
    DB_FILE = config.ProductionConfig.DB_FILE

#development Env
def development():
    global SERVER_ENV, UWSGI_ENV, DB_DIR, DB_FILE
    env.hosts = ['192.168.0.121']
    env.user = 'admin'
    SERVER_ENV = 'development'
    UWSGI_ENV = 'development'
    DB_DIR = config.DevelopmentConfig.DB_DIR
    DB_FILE = config.DevelopmentConfig.DB_FILE

def devserver():
    global SERVER_ENV, UWSGI_ENV, DB_DIR, DB_FILE
    env.hosts = ['local-vm-win10-centos6']
    env.user = 'caritasem'
    SERVER_ENV = 'development'
    UWSGI_ENV = 'development'
    DB_DIR = config.DevelopmentConfig.DB_DIR
    DB_FILE = config.DevelopmentConfig.DB_FILE

def run_test():
    with cd(TO_DIR + "current"):
        #run('sudo ./scheduler.py stop')
        run('set -m; sudo ./scheduler.py start')