#initial settings

export PROJECT_PATH=$(pwd)/../
echo export PROJECT_PATH=$PROJECT_PATH >> .bashrc
apt-get install openssh-client -y
apt-get install supervisor -y
service apache2 stop
apt-get install nginx -y
#apt-get install macchanger -y

cd $PROJECT_PATH
pip3 install -r requirements.txt

FLASK_APP=wsgi.py

#Nginx and Gunicorn

echo "setting nginx and gunicorn..."

rm /etc/nginx/sites-enabled/default
#sudo ln -s /etc/nginx/sites-available/flask_settings.conf /etc/nginx/sites-enabled/flask_settings.conf
cp conf/flask_settings.conf /etc/nginx/sites-enabled
/etc/init.d/nginx restart

#Supervisor

echo "setting supervisor..."

cp conf/orm-flask.conf /etc/supervisor/conf.d/
mkdir -p /var/log/orm-flask
touch /var/log/orm-flask/api.err.log
touch /var/log/orm-flask/api.out.log

#sudo service supervisor stop

supervisorctl reload
supervisorctl restart all
supervisorctl status

#sudo service supervisor start

echo "installation done!"
