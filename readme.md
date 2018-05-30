# OpenVPN管理系统
这是用python flask sqlite实现的一个OpenVPN客户端管理系统

## Web Installation

### 启用virtualenv
````
# virtualenv haoliVPNEnv
# source haoliVPNEnv/bin/activate
````

### 安装依赖的组件
````
yum -y install expect
````
````
pip2.7 install uwsgi
pip2.7 install flask
pip2.7 install flask-bootstrap flask-script flask-moment pyminizip flask_wtf flask_sqlalchemy sqlalchemy-migrate flask-mail flask-login flask-ldap-login python-ldap
````

### sqlite数据库
````
./db_create.py 创建数据库
./db_migrate.py 更新数据库
````

### uwsgi
````
将工程中的uwsgi-vpn-admin放到/etc/init.d目录，/etc/init.d/uwsgi-vpn-admin start启动uwsgi

/etc/init.d/uwsgi-vpn-admin start|stop|status|restart
````
### nginx/apache web服务器配置
````
include        uwsgi_params;

uwsgi_param UWSGI_PYHOME /path/to/dir/haoliVPNEnv;
uwsgi_param UWSGI_CHDIR  /path/to/dir;

uwsgi_param UWSGI_SCRIPT run:app;
uwsgi_pass  unix:/path/to/dir/haoliVPN.sock;
````

### 启用openldap
````v
config.py文件中LDAP_ENABLED设为True
````

## 后台运行脚本：
````
./scheduler.py start/stop

./scheduler.py: 后台生成client key，revoke, index.txt与数据库同步等
````
## ovpn文件
ovpn文件区分windows和MacOS平台，放在installation文件夹下的ovpn目录

## server端Log配置
````
./connect.sh ./disconnect.sh ./connect.py 可执行权限
openvpn服务端配置文件增加下面配置：
client-connect /path/to/dir/haoliVPN/connect.sh
client-disconnect /path/to/dir/haoliVPN/disconnect.sh
````

## 自动发布流程
* 安装python fabric工具
* 工程根目录下执行:
    * development环境: fab development deploy_to_remote
    * production环境: fab production deploy_to_remote:tag=vx.x.x

    备注：

        1. 执行fab命令前请检查文件的host配置

        2. produnction/development，指定文件部署环境host, tag,指定git标签和当前版本

* server端Log配置,请手动配置

## UI效果
![首页](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/1.png)
![user list](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/2.png)
![user add](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/3.png)
![log list](https://github.com/sibosend/openvpn-admin-ui/raw/master/screenshots/4.png)
