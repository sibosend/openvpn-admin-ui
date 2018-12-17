import os
import subprocess

import re
import pyminizip
from flask import current_app
import random, string

from functools import wraps
from flask import abort
from flask_login import current_user
from models import Permission


def runPipe(cmds):
    try:
        p1 = subprocess.Popen(cmds[0].split(' '), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        prev = p1
        for cmd in cmds[1:]:
            p = subprocess.Popen(cmd.split(' '), stdin=prev.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            prev.stdout.close()
            prev = p
        stdout, stderr = p.communicate()
        p.wait()
        returncode = p.returncode
    except Exception, e:
        stderr = str(e)
        returncode = -1
    if returncode == 0:
        return (True, stdout.strip().split('\n'))
    else:
        return (False, stderr)


# return current vpn status
# 0: unknown; 1: running; 2: not running
def checkVPN():
    cmd_vpn_s, cmd_vpn_pscnt = runPipe(current_app.config['CMD_CHECKVPN'])
    vpn_running = 0
    if cmd_vpn_s:
        if int(cmd_vpn_pscnt[0]) > 0:
            vpn_running = 1
        else:
            vpn_running = 2
    return vpn_running


def connectVPN(username, code):
    if checkVPN() == 1:
        return (False, ["Already Connected"])
    try:
        output = subprocess.check_output([current_app.config['EXPECT_VPN_CONNECT'], username, code], stderr=subprocess.STDOUT)
        returncode = 0
    except subprocess.CalledProcessError as e:
        stderr = "command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output)
        returncode = -1
    except    Exception, e:
        stderr = str(e)
        returncode = -1

    if returncode == 0:
        return (True, output.strip().split('\n'))
    else:
        return (False, stderr.strip().split('\n'))


def buildKey(params):
    try:
        cmds = ' && '.join(current_app.config['CMD_BUILD_KEY']) + ' ' + ' '.join(params)
        p1 = subprocess.Popen(cmds, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p1.communicate()
        print(stdout)
        print(stderr)
        p1.wait()
        returncode = p1.returncode
    except Exception, e:
        stderr = str(e)
        returncode = -1
    if returncode == 0:
        return (True, stdout.strip().split('\n'))
    else:
        return (False, stderr.strip().split('\n'))


def revoke(client):
    try:
        cmds = ' && '.join(current_app.config['CMD_REVOKE']) + ' ' + client
        # cmds = ['cd ' + EASY_RSA, 'source ./vars', BASE_DIR + '/expect/revoke.expect ' + client]
        p1 = subprocess.Popen(cmds, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # prev = p1
        # p = subprocess.Popen(['/usr/share/easy-rsa/2.0/build-key', client], stdin = prev.stdout, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        # prev.stdout.close()
        stdout, stderr = p1.communicate()
        p1.wait()
        if p1.returncode == 0:
            stdout = subprocess.check_output(current_app.config['CMD_REVOKE_FILE_COPY'], shell=True)
            print(stdout)
            if stdout:
                returncode = 1
            else:
                returncode = 0
        else:
            returncode = p1.returncode
    except Exception, e:
        stderr = str(e)
        returncode = -1
    if returncode == 0:
        return (True, stdout.strip().split('\n'))
    else:
        return (False, stderr.strip().split('\n'))


def zip_compress(client):
    is_dir_exist = os.path.exists(current_app.config['CLIENT_DOWNLOAD_DIR'])
    if not is_dir_exist:
        os.makedirs(current_app.config['CLIENT_DOWNLOAD_DIR'])
    compression_level = 5
    file_dest = os.path.join(current_app.config['CLIENT_DOWNLOAD_DIR'], client + '.zip')
    file_password = random_str()
    if os.path.exists(file_dest):
        os.remove(file_dest)
    if os.path.exists(current_app.config['CLIENT_VPN_HAOLI_OVPN']) and os.path.exists(os.path.join(current_app.config['CLIENT_VPN_HAOLI_DIR'], client + ".key")) \
            and os.path.exists(os.path.join(current_app.config['CLIENT_VPN_HAOLI_DIR'], client + ".crt")) \
            and os.path.exists(os.path.join(current_app.config['CLIENT_VPN_HAOLI_DIR'], 'ca.crt')):
        try:
            cmd = 'cd ' + current_app.config['CLIENT_VPN_HAOLI_OVPN'] + ' && ' + ' zip -q -r -P ' + file_password + ' ' + file_dest + ' ./'
            output = subprocess.check_output(cmd, shell=True)
            if output:
                returncode = 1
            else:
                returncode = 0
            if returncode == 0:
                cmd = 'cd ' + current_app.config['CLIENT_VPN_HAOLI_DIR'] + ' && ' + \
                      ' zip -q -g -P ' + file_password + ' ' + file_dest + ' ' \
                      + ' '.join([client + ".key", client + ".crt", 'ca.crt'])
                output = subprocess.check_output(cmd, shell=True)
                if output:
                    returncode = 1
                else:
                    returncode = 0
        except Exception, e:
            output = str(e)
            returncode = -1
        if returncode == 0:
            return (True, file_dest, file_password)
        else:
            return (False, output, 500)

    return ((False, 'user file not exist', 404))


# def zip_compress(client):
#     is_dir_exist = os.path.exists(CLIENT_DOWNLOAD_DIR)
#     if not is_dir_exist:
#         os.makedirs(CLIENT_DOWNLOAD_DIR)
#     compression_level = 5
#     file_dest = os.path.join(CLIENT_DOWNLOAD_DIR, client + '.zip')
#     file_password = random_str()
#     if os.path.exists(file_dest):
#         os.remove(file_dest)
#     if os.path.exists(CLIENT_VPN_HAOLI_OVPN) and os.path.exists(os.path.join(CLIENT_VPN_HAOLI_DIR, client + ".key")) \
#             and os.path.exists(os.path.join(CLIENT_VPN_HAOLI_DIR, client + ".crt")) and os.path.exists(
#         CLIENT_VPN_HAOLI_CA):
#         pyminizip.compress_multiple(
#             [CLIENT_VPN_HAOLI_OVPN,
#              os.path.join(CLIENT_VPN_HAOLI_DIR, client + ".key"),
#              os.path.join(CLIENT_VPN_HAOLI_DIR, client + ".crt"),
#              CLIENT_VPN_HAOLI_CA],
#             file_dest,
#             file_password,
#             compression_level)
#
#     return (file_dest, file_password)


def zip_delete(client):
    file_dest = os.path.join(current_app.config['CLIENT_DOWNLOAD_DIR'], client + '.zip')
    if os.path.exists(file_dest):
        os.remove(file_dest)


def random_str(randomlength=8):
    strlist = list(string.ascii_letters + string.digits)
    random.shuffle(strlist)
    return ''.join(strlist[:randomlength])


def get_users():
    # ip txt
    # ip_dicts = {}
    # if os.path.exists(CLIENT_VPN_HAOLI_IPP):
    #     ipfile = open(CLIENT_VPN_HAOLI_IPP)
    #     ipline = ipfile.readline()
    #     while ipline:
    #         ipinfo = ipline.strip().split(",")
    #         if len(ipinfo) == 2:
    #             ip_dicts[ipinfo[0]] = ipinfo[1]
    #         ipline = ipfile.readline()
    #     ipfile.close()

    # index txt
    client_list = []
    if os.path.exists(current_app.config['CLIENT_VPN_HAOLI_LIST']):
        index_file = open(current_app.config['CLIENT_VPN_HAOLI_LIST'])
        line = index_file.readline()
        while line:
            list = line.strip().split("\t")
            if len(list) != 6:
                line = index_file.readline()
                continue

            if list[0] == 'V':
                status = 1
            else:
                status = 4
            number = int(list[3], 16)
            item = list[5]
            groups = item.strip().split("/")
            client = None
            email = None
            depart = None
            name = None
            for group in groups:
                infos = group.strip().split("=")
                if len(infos) < 2:
                    continue
                if infos[0] == 'CN':
                    client = infos[1]
                elif infos[0] == 'emailAddress':
                    email = infos[1]
                elif infos[0] == 'OU':
                    depart = infos[1]
                elif infos[0] == 'name':
                    name = infos[1]

            if client:
                client_list.append(
                    {'No': number, 'depart': depart, 'name': name, 'client': client, 'email': email, 'status': status})

            line = index_file.readline()

        index_file.close()
        return client_list
    else:
        return False

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_scheduler_status():
    if not(os.path.exists(current_app.config['SCHEDULER_PID'])):
        return (False,0)

    process = "haoliVPNEnv/bin/python"
    script = "scheduler.py"
    try:
        cmd = "ps -ef | grep " + process + " | grep " + script + " | grep -v nobody | wc -l"
	    # print cmd
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        # print output
        returncode = 0
    except subprocess.CalledProcessError as e:
        stderr = "command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output)
        print stderr
        returncode = -1
    except Exception, e:
        stderr = str(e)
        returncode = -1

    if returncode == 0:
        result = int(output)
        if result == 0:
            return (False, 0)

    else:
        return (False, 0)

    return (True, result)

