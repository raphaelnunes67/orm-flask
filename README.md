# LG DAMPER - Project Quick Quide

## WHAT IS
A system to log Damper CLP activities with a web client viewer.

![#damper_arch](/docs/img/architecture.png)

## WHO DESTINATE / OBJECTIVE

## LOCAL INSTALLATION
```
$ git clone

$ cd damper-core

$ python -m venv venv

$ pip install -r requirements.txt

$ source venv/bin/activate
```
• python -m venv venv
• source venv/bin/activate
• Digite: `composer install` para instalar as bibliotecas;
• Instale `database.sql` em PHPMyAdmin;
• Agora, para que o envio de e-mail funcione localmente *__habilide a extensão open_openssl e php_sockets__** no php.ini, basta abrir o php.ini e usando `Ctrl+F` busque pelos termos openssl, descomente e depois depois repita os procedimentos para sockets, não se esqueça de reiniciar o apache depois do procedimento;

## REVPI INSTALLATION

```
$ sudo apt-get update
$ sudo apt-get upgrade -y
$ sudo apt-get install git -y
$ sudo apt install openssh-client -y
$ sudo apt install supervisor -y
$ sudo apt install nginx -y
$ sudo apt install git -y
$ sudo apt-get install python3.9 -y python3-venv python3.9-dev -y
$ sudo reboot
$ cd /home
$ git clone
$ cd /damper-core
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ export FLASK_APP=app.py

```
### Nginx and Gunicorn
```
$ sudo rm /etc/nginx/sites-enabled/default
$ sudo touch /etc/nginx/sites-available/flask_settings
$ sudo ln -s /etc/nginx/sites-available/flask_settings /etc/nginx/sites-enabled/flask_settings 
$ sudo nano /etc/nginx/sites-enabled/flask_settings

paste this: 

server{
  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}

$ sudo /etc/init.d/nginx restart
$ gunicorn -w 3 app:app

```
### Supervisor

```
$ sudo nano /etc/supervisor/conf.d/damper_core.conf

paste this: 

[program:damper_core]

directory=/home/damper-core
command=/home/damper-core/venv/bin/gunicorn -w 3 app:app
user=root
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/damper_core/damper_core.err.log
stdout_logfile=/var/log/damper_core/damper_core.out.log

$ mkdir -p /var/log/damper_core
$ touch /var/log/damper_core/damper_core.err.log
$ touch /var/log/damper_core/damper_core.out.log
$ supervisorctl reload
$ supervisorctl restart


$command=bash -c 'sleep 5 && exec ./venv/bin/python main.py'

```


requisicao >  nginx > gunicorn > app

### Wheel installation problem
• To install wheel folow this steps:
- pip install wheel;
- pip uninstall -r requirements.txt -y;
- pip install -r requirements.txt

## CONVENTIONS

## PROJECT LIBRARIES

## DATABASE

## SOURCE TREE


#### SOBRE O AUTOR/ORGANIZADOR
