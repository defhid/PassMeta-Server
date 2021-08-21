# PassMeta Server — *your passwords SAFE*
#### © 2021 Vladislav Mironov


### About the project
PassMeta Server is a part of PassMeta System, which provides reliable distributed
<br>
password storage and password management tools.
<br>


### Technologies
*Python 3.8, FastAPI, SqlAlchemy, PostgreSQL.*


### Deployment

+ **Install python 3.8, postgresql, unzip:**
  - `sudo apt update`
  - `sudo apt install python3`
  - `sudo apt install python3-pip`
  - `sudo apt install python3-venv`
  - `sudo apt install postgresql`
  - `sudo apt install postgresql-client`
  - `sudo apt install unzip`


+ **Download and unzip the project, change current directory:**
  - `wget https://github.com/vlad120/PM-Server/archive/refs/heads/master.zip`
  - `unzip proj.zip`
  - `rm proj.zip`
  - `mv PM-Server-master passmeta`
  - `cd passmeta`


+ **Install python environment and dependencies:**
  - `python3 -m venv env`
  - `env/bin/pip install -r requirements.txt`
  - `env/bin/pip install uvicorn[standard]`
  - `env/bin/pip install gunicorn`


+ **Create database:**
  - `sudo -u postgres psql`
  - `CREATE DATABASE passmeta;`


+ **Generate configuration files and SSL Certificates:**
  - `env/bin/python App/settings.py`
    - input username for local PostgreSQL server
    - input password for that user
  - `env/bin/python Gun/makeconfig.py`
    - input server host, like `x.x.x.x` or `my-server-host.com`
    - input server country code, like `RU`
  - `sudo bash Gun/ssl/certmaker.sh`


### Launch as service

+ **Setup:**
  - `sudo cp Gun/service/passmeta-server-app.service /etc/systemd/system/`
  - `sudo chmod 664 /etc/systemd/system/passmeta-server-app.service`
  - `sudo systemctl daemon-reload`


+ **Enable-disable:**
  - `sudo systemctl enable passmeta-server-app`
  - `sudo systemctl disable passmeta-server-app`


+ **Start-stop:**
  - `sudo systemctl start passmeta-server-app`
  - `sudo systemctl stop passmeta-server-app`


### Launch as process
+ Ensure auto-launch disabled:
  - `sudo systemctl stop passmeta-server-app`
  - `sudo systemctl disable passmeta-server-app`
  

+ **Start:** `sudo env/bin/python -m gunicorn --config Gun/config/manual.py`
+ **Stop:** `sudo env/bin/python Gun/kill.py`


### Tests
+ Not implemented yet...