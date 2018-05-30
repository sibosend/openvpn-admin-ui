#!haoliVPNEnv/bin/python
from migrate.versioning import api
from application import db,create_app
import os
import subprocess
import sys
from firstApp.models import Role

app=create_app()
app.app_context().push()

db.create_all()
Role.insert_role()
if not os.path.exists(app.config['SQLALCHEMY_MIGRATE_REPO']):
    api.create(app.config['SQLALCHEMY_MIGRATE_REPO'], 'database repository')
    api.version_control(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_MIGRATE_REPO'])
else:
    api.version_control(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_MIGRATE_REPO'], api.version(app.config['SQLALCHEMY_MIGRATE_REPO']))


# print DATABASE_URL
#
# try:
#     output = subprocess.check_output('chown nobody:nobody ' + DATABASE_URL, stderr=subprocess.STDOUT)
#     returncode = 0
# except subprocess.CalledProcessError as e:
#     stderr = "command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output)
#     returncode = -1
# except Exception, e:
#     stderr = str(e)
#     returncode = -1
#
# if returncode == 0:
#     print 'success'
# else:
#     print stderr
