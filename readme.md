# PassMeta Server — *your passwords SAFE*
#### © 2024 Vladislav Mironov


### About the project
PassMeta Server is a part of PassMeta System, which provides reliable
<br>
distributed password storage and password management tools.

**Desktop** application is [here](https://github.com/defhid/PassMeta-DesktopApp).

### Technologies
*Python 3.11, FastAPI, asyncpg + passql, PostgreSQL.*


### Deployment on Linux

+ **Install python 3.8, postgresql, unzip:**
  - `sudo apt update`
  - `sudo apt install python3`
  - `sudo apt install python3-pip`
  - `sudo apt install python3-venv`
  - `sudo apt install postgresql`
  - `sudo apt install postgresql-client`
  - `sudo apt install unzip`


+ **Download and unzip the project, change current directory:**
  - `wget https://github.com/vlad120/PassMeta-Server/archive/refs/heads/master.zip`
  - `unzip master.zip`
  - `rm master.zip`
  - `mv PassMeta-Server-master /home/passmeta`
  - `cd /home/passmeta`


+ **Create database:**
  - `sudo -u postgres psql`
  - `CREATE DATABASE passmeta;`


+ **Generate bash scripts:**
  - `python3 Utils/makescripts.py`


+ **Install python environment and dependencies:**
  - `sudo bash Scripts/dependency-installer.sh`


+ **Generate configuration files:**
  - `env/bin/python Utils/makeappsettings.py`
    - input username for local PostgreSQL server
    - input password for that user
  - `env/bin/python Utils/makeconfig.py`
    - input server host, like `x.x.x.x` or `my-server-host.com`
    - input server country code, like `RU`


+ **Generate SSL Certificates**
  - `sudo bash Scripts/certmaker.sh`


### Launch as service

+ **Setup:**
  - `sudo bash Scripts/service-maker.sh`


+ **Enable-disable:**
  - `sudo bash Scripts/service-enabler.sh`
  - `sudo bash Scripts/service-disabler.sh`


+ **Start-stop:**
  - `sudo bash Scripts/service-starter.sh`
  - `sudo bash Scripts/service-stopper.sh`


### Launch as a process
+ **Start:** `sudo bash Scripts/process-starter.sh`
+ **Stop:** `sudo bash Scripts/process-killer.sh`


### Update
+ `sudo bash Scripts/updater.sh`
