# OpenVPN Management System
This is an OpenVPN client management system implemented with python2.7, flask and sqlite.

## Web UI Implementation
Index Page:
![Index](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/1.png)

Client List Page:
![User List](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/2.png)

Add Client Page:
![User Add](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/3.png)

Log List Page:
![Log List](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/4.png)

## Project Installation

### Install Python 2.7
 
### Use Virtualenv
````
# virtualenv haoliVPNEnv
# source haoliVPNEnv/bin/activate
````

### Install dependent components
````
yum -y install expect
````
````
pip2.7 install uwsgi
pip2.7 install flask
pip2.7 install flask-bootstrap flask-script flask-moment pyminizip flask_wtf flask_sqlalchemy sqlalchemy-migrate flask-mail flask-login flask-ldap-login python-ldap
````

### sqlite
````
./db_create.py      //Create Database
./db_migrate.py     //Update Database
````

### uwsgi
````
Put the uwsgi-vpn-admin file into /etc/init.d directory(Linux boot script directory).
And start uwsgi with command '/etc/init.d/uwsgi-vpn-admin start'

/etc/init.d/uwsgi-vpn-admin start|stop|status|restart
````
### nginx/apache web server configuration
````
include        uwsgi_params;

uwsgi_param UWSGI_PYHOME /path/to/dir/haoliVPNEnv;
uwsgi_param UWSGI_CHDIR  /path/to/dir;

uwsgi_param UWSGI_SCRIPT run:app;
uwsgi_pass  unix:/path/to/dir/haoliVPN.sock;
````

### enable openldap
````
config.py: 
    1. LDAP_ENABLED = True
    2. LDAP = {........}, Configure URL, BIND_DN/BIND_PASSORD, MAP, etc.
    
````

## Run these scripts in the background
````
./scheduler.py start    //Generate client key, revoke, synchronization between index.txt and database.

./scheduler.py stop     //stop

````
## ovpn file
The ovpn files contain windows and MacOS platforms, and is placed in the installation/ovpn directory.

## OpenVPN Server Log configuration
````
chmod +x ./connect.sh
chmod +x ./disconnect.sh
chmod +x ./connect.py

Add the following configuration at the end of OpenVPN Server config file：
client-connect /path/to/dir/haoliVPN/connect.sh
client-disconnect /path/to/dir/haoliVPN/disconnect.sh
````

## Automatic Deploy
* Intall Fabric
* Run the following scripts under the project root directory:
    * development env: fab development deploy_to_remote
    * production env: fab production deploy_to_remote:tag=vx.x.x

    remark:

        1. Please check the host configuration of the fabfile.py file before running the fab scripts.

        2. produnction/development: specifies which environment to deploy
           tag=vx.x.x: specifies the git tag, the version to deploy

* OpenVPN Server Log configuration must be manually configured
