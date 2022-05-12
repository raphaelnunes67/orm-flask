sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git -y
sudo apt install openssh-client -y
sudo apt install supervisor -y
sudo apt install nginx -y
sudo apt install git -y
sudo apt-get install python3.9 -y python3-venv python3.9-dev -y
sudo reboot
cd /home
git clone
cd /damper-project
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py